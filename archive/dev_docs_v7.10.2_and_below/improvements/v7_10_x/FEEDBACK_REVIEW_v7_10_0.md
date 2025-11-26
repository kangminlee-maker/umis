# v7.10.0 피드백 검토 및 개선 방안

**작성일**: 2025-11-23
**중요도**: ⭐⭐⭐⭐⭐

---

## 📝 피드백 핵심 요약

### ✅ 전체 방향성: **찬성**

```
v7.10.0 제안이 이상적 구조를 잘 구현:
- Phase 0-2: 검증 + 가드레일 ✅
- Phase 3-4: 병렬 추정 ✅
- Synthesis: 전체 종합 ✅

→ 정보 손실 제거, 교차 검증 가능
```

### 🔧 개선 필요 (5가지)

1. **Phase 3 정체성**: Range 엔진 vs Point 추정 혼재
2. **Hard/Soft 분리**: 더 명시적으로
3. **Synthesis 위상**: Phase 5 승격 or Stage 유지?
4. **LLM 판정 고도화**: 2단계 체인
5. **검증 체계**: A/B 테스트, Phase별 책임

---

## ✅ 동의 부분

### 1. 정보 손실 제거 ✅

**피드백**: "유사 데이터를 guardrail로 변환하는 게 핵심"

**동의**: 완전 동의!

```python
# v7.9.0: 버림 ❌
if confidence < 0.95:
    return None

# v7.10.0: 가드레일 ✅
if confidence >= 0.70:
    guardrails.append(analyze(result))
```

### 2. 역할 분리 잘됨 ✅

```
Phase 0-2: 검증 + 재활용
Phase 3: Guardrail Range
Phase 4: Fermi
Synthesis: 종합 판단

→ 정확한 이해!
```

### 3. Top-down vs Bottom-up ✅

```
Phase 3 (Top-Down): 일반 법칙 → [20만, 40만]
Phase 4 (Bottom-Up): Fermi → 30만

교차 검증: 30만 ∈ [20만, 40만]? YES!
→ 신뢰도 +15% ✅
```

---

## 🔧 개선 방안

### 개선 1: Phase 3 순수 Range 엔진 ⭐⭐⭐⭐⭐

**문제**: 현재 Phase 3이 range + point 동시 제공

**개선**:
```python
# Before
{
    "value": 30만,  # Point (애매)
    "value_range": [20만, 40만]
}

# After (순수 Range 엔진)
{
    "value": None,  # 부수적
    "value_range": [20만, 40만],  # 핵심!
    "confidence": 0.95  # Hard → 높음
}
```

**결정**: ✅ **채택**

---

### 개선 2: Hard/Soft 명시적 분리 ⭐⭐⭐⭐⭐

**문제**: 현재 hard/soft 구분 없음

**개선**:
```python
# Before
class GuardrailType(Enum):
    UPPER_BOUND = "upper_bound"  # 모호

# After
class GuardrailType(Enum):
    # Hard (논리적, conf ≥ 0.90)
    HARD_UPPER = "hard_upper"
    HARD_LOWER = "hard_lower"
    
    # Soft (경험적, conf 0.60-0.85)
    SOFT_UPPER = "soft_upper"
    SOFT_LOWER = "soft_lower"
```

**사용**:
```python
# Phase 3: Hard만
hard_guards = [g for g in guardrails if g.is_hard]
phase3_range = calculate_range(hard_guards)

# Synthesis: Soft는 조정용
soft_guards = [g for g in guardrails if not g.is_hard]
confidence *= adjust_by_soft(soft_guards)
```

**결정**: ✅ **채택**

---

### 개선 3: Synthesis 위상 명확화 ⭐⭐⭐⭐

**옵션 A**: Phase 5로 승격
**옵션 B**: Stage 개념 유지 (API 호환)

**피드백 권장**: **옵션 B**

**결정**: ✅ **옵션 B 채택**
```python
# 외부 API: phase=4 유지
final.phase = 4

# 내부 로그: Stage 명시
logger.info("⚖️ Stage 3: Synthesis")
final.reasoning = f"[Stage 3 Synthesis] ..."
```

---

### 개선 4: LLM 판정 2단계 체인 ⭐⭐⭐⭐

**문제**: 현재 단일 LLM 호출 (불안정)

**개선**:
```python
class GuardrailAnalyzer:
    def analyze(self, target, similar):
        # 1단계: 관계 판단
        relationship = llm_1("X > Y? X < Y? 무관?")
        
        # 2단계: Hard/Soft 판정
        if relationship != "무관":
            hardness = llm_2("Hard (논리적)? Soft (경험적)?")
            
            return Guardrail(
                type=HARD_UPPER if hardness == "Hard" else SOFT_UPPER,
                confidence=0.95 if hardness == "Hard" else 0.75
            )
```

**결정**: ✅ **채택**

---

### 개선 5: 검증 체계 구축 ⭐⭐⭐⭐

**추가 (Week 5)**:
```python
# 1. A/B 테스트
compare(v7_9_0, v7_10_0, test_cases)

# 2. Phase별 책임
measure_coverage(phase3_range, ground_truth)

# 3. 실패 분석
analyze_failure(result, ground_truth)
```

**결정**: ✅ **채택**

---

## 📅 실행 계획 업데이트

### Week 1: Core + 개선

**기존**:
- GuardrailType
- GuardrailCollector

**추가**:
- ⭐ HARD/SOFT 명시적 분리
- ⭐ Phase 3 → Range 엔진 재설계

### Week 2: Parallel (유지)

- Phase 1-2 병렬
- Phase 3-4 병렬

### Week 3: Synthesis + 개선

**추가**:
- ⭐ Hard → Phase 3, Soft → Synthesis
- ⭐ Stage 로그 명확화

### Week 4: Advanced + 개선

**추가**:
- ⭐ GuardrailAnalyzer (2단계 체인)

### Week 5: Testing + 개선

**추가**:
- ⭐ A/B 테스트
- ⭐ Phase별 책임 측정
- ⭐ 실패 케이스 분석

---

## 🎯 최종 아키텍처 (개선판)

```
Stage 1: Tiered Collection
  → Definite + Hard/Soft Guardrails

Stage 2: Parallel Estimation
  → Phase 3: Hard Guardrail Range (순수 Range)
  → Phase 4: Fermi Point

Stage 3: Synthesis
  → Cross-Validation
  → Hard: Range 강제
  → Soft: Confidence 조정
  → Weighted Fusion

검증: A/B, Phase별, 실패 분석
```

---

## ✅ 결론

### 피드백 핵심 수용

1. ✅ Phase 3 순수 Range 엔진
2. ✅ Hard/Soft 명시적 분리
3. ✅ Synthesis 위상 (Stage 유지)
4. ✅ LLM 2단계 체인
5. ✅ 검증 체계 구축

### 기대 효과

- 역할 명확 (Range vs Point)
- Guardrail 안정성 ↑
- LLM 판정 신뢰도 ↑
- 검증 가능성 ↑

---

**다음: Week 1 구현 시작**

---

**END**
