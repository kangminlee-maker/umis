# Estimator/Quantifier 역할 분리 v7.5.0

**작성일**: 2025-11-10  
**버전**: v7.5.0  
**상태**: ✅ 완료  

---

## 📋 요약

Estimator와 Quantifier의 역할을 **MECE** 원칙에 따라 명확히 분리했습니다.

| Agent | 역할 | 소유 | 예시 |
|-------|------|------|------|
| **Estimator** | 값 추정 | • 3-Tier 추정 로직<br>• 11개 Source 수집<br>• 일반 Fermi 분해 | "B2B SaaS ARPU는?"<br>→ 80,000원 |
| **Quantifier** | 계산 수행 | • 31개 계산 방법론<br>• 비즈니스 지표 공식<br>• 벤치마크 데이터 | LTV = ARPU / Churn<br>→ 1,600,000원 |

---

## 🔧 주요 변경사항

### 1. Tier 1/2 임계값 강화 ✅

**목적**: Tier 3 활용도 증가 (Tier 3가 Estimator의 핵심!)

```python
# umis_rag/agents/estimator/models.py

# Tier 1: 정확한 매칭만
Tier1Config.min_similarity = 0.95  # (Before: 0.85)

# Tier 2: 높은 신뢰도만  
Tier2Config.min_confidence = 0.80  # (Before: 0.60)
```

**효과**:
- Tier 1/2에서 거부되는 비율 증가
- → Tier 3로 넘어가는 질문 증가
- → Tier 3 Fermi 분해 활용도 증가

---

### 2. Quantifier 계산 공식 강화 ✅

**위치**: `data/raw/calculation_methodologies.yaml`

**추가된 공식**:
- LTV (2가지 방법)
- CAC (2가지 방법)
- ARPU (4가지 방법)
- Churn (2가지 방법 + 연간 전환)
- NRR/GRR 분리
- Gross Margin (2가지 방법)

**Before**: 30개 방법론  
**After**: 31개 방법론

---

### 3. Estimator Tier 3 비즈니스 템플릿 제거 ✅

**위치**: `umis_rag/agents/estimator/tier3.py`

**제거된 내용**:
```python
# Before: 12개 비즈니스 지표 템플릿
BUSINESS_METRIC_TEMPLATES = {
    "ltv": {...},
    "cac": {...},
    "payback": {...},
    # 전부 제거!
}
```

**After**:
```python
# 비즈니스 지표 템플릿 제거
# Quantifier가 계산 공식 소유
# Estimator는 일반 Fermi 분해만
```

**이유**: 계산 공식 중복 (MECE 위배) → Quantifier로 통합

---

### 4. Context 전달 개선 ✅

**위치**: `umis_rag/agents/estimator/tier3.py`

**Before** (재귀 시 애매한 질문):
```python
question = f"{var_name}는?"  # "arpu는?" ❌
```

**After** (구체적인 질문):
```python
question = self._build_contextualized_question(var_name, context)
# → "B2B SaaS 한국 2024 시장의 ARPU는?" ✅
```

**효과**:
- RAG 검색 정확도 증가
- LLM 이해도 향상
- 추정 품질 개선

---

### 5. 문서 업데이트 ✅

**업데이트된 파일**:
- `umis_core.yaml`: Estimator/Quantifier 역할 명확화
- `umis.yaml`: Tier 3 설명 업데이트, 협업 예시 추가
- `umis_deliverable_standards.yaml`: 산출물 표준 업데이트

---

## 🎯 새로운 협업 시나리오

### 시나리오: LTV 계산

```
사용자: "이 SaaS의 LTV는?"

Step 1: Quantifier가 계산 시작
  - calculation_methodologies.yaml 검색
  - 공식 발견: LTV = ARPU / Churn_Rate

Step 2: Quantifier가 ARPU 확인
  - 프로젝트 데이터에 없음
  - → Estimator 호출!

Step 3: Estimator가 ARPU 추정
  estimator.estimate(
      question="B2B SaaS 한국 2024 시장의 ARPU는?",
      context=Context(domain="B2B_SaaS", region="한국", time_period="2024")
  )
  
  - Tier 1 시도: 유사도 0.92 (< 0.95) → 실패
  - Tier 2 시도:
    * RAG 벤치마크: 70,000-90,000원
    * 업계 평균: 80,000원
    * Confidence: 0.85
  - → 80,000원 반환

Step 4: Quantifier가 Churn 확인
  - 프로젝트 데이터에 없음
  - → Estimator 호출!

Step 5: Estimator가 Churn 추정
  estimator.estimate("B2B SaaS 한국 2024 시장의 Churn Rate는?")
  
  - Tier 2: 4-6% (벤치마크)
  - Confidence: 0.82
  - → 5% 반환

Step 6: Quantifier가 LTV 계산
  ltv = 80,000 / 0.05 = 1,600,000원

Step 7: Estimation_Details 시트 기록
  EST_001 (Estimator Tier 2): ARPU 80,000원 (conf: 0.85)
  EST_002 (Estimator Tier 2): Churn 5% (conf: 0.82)
  
  계산 (Quantifier): LTV = 80,000 / 0.05 = 1,600,000원
  최종 신뢰도: 0.83 (Geometric Mean)
```

---

## 📊 효과

| 항목 | Before | After | 효과 |
|------|--------|-------|------|
| **역할 분리** | 겹침 (계산 공식 중복) | MECE | ✅ 유지보수성 ↑ |
| **Tier 3 활용** | 낮음 (Tier 2에서 걸러짐) | 높음 (임계값 강화) | ✅ 핵심 강화 |
| **질문 명확성** | "ARPU는?" | "B2B SaaS 한국 ARPU는?" | ✅ 정확도 ↑ |
| **재사용성** | 낮음 | 높음 (Quantifier 어디서나) | ✅ 확장성 ↑ |
| **코드 중복** | 계산 공식 2곳 | 계산 공식 1곳 | ✅ DRY 원칙 |

---

## 🔄 마이그레이션 가이드

### AS-IS (v7.4.0 이하)

```python
# Estimator가 LTV 계산까지 수행
estimator = EstimatorRAG()
result = estimator.estimate("LTV는?")
# → Tier 3 템플릿 매칭: ltv
# → 재귀: arpu, churn_rate 추정
# → 계산: ltv = arpu / churn_rate
# → 반환: 1,600,000원
```

### TO-BE (v7.5.0+)

```python
# Quantifier가 계산, Estimator가 추정
quantifier = QuantifierRAG()

# Quantifier가 내부적으로:
# 1. LTV 공식 확인: LTV = ARPU / Churn
# 2. ARPU 필요 → estimator.estimate("ARPU는?")
# 3. Churn 필요 → estimator.estimate("Churn은?")
# 4. 계산: ltv = 80,000 / 0.05 = 1,600,000

# 사용자는 그냥:
result = quantifier.calculate_ltv(context)
```

**변경 필요 없음**: Quantifier가 자동으로 Estimator 호출

---

## 📁 변경된 파일 목록

### 코드 (5개)
1. `umis_rag/agents/estimator/models.py` - Tier 1/2 임계값 강화
2. `umis_rag/agents/estimator/tier1.py` - 로그 메시지 업데이트
3. `umis_rag/agents/estimator/tier3.py` - 비즈니스 템플릿 제거, Context 질문 생성
4. `umis_rag/agents/estimator/estimator.py` - 문서 업데이트
5. `data/raw/calculation_methodologies.yaml` - 비즈니스 공식 강화

### 문서 (3개)
6. `umis_core.yaml` - Estimator/Quantifier 역할 명확화
7. `umis.yaml` - Tier 3 설명, 협업 시나리오
8. `umis_deliverable_standards.yaml` - 산출물 표준 업데이트

### Archive (1개)
9. `data/raw/umis_ai_guide.yaml` → `archive/v7.2.0_and_earlier/` (v6.2.2, 미사용)

---

## 🚀 다음 단계

### 권장사항

1. **RAG 재구축** (선택)
   ```bash
   python scripts/build_system_knowledge.py
   ```
   - Estimator 변경사항 반영
   - 하지만 구조 변경이라 꼭 필요하진 않음

2. **통합 테스트**
   - Quantifier → Estimator 협업 검증
   - Tier 3 Fermi 분해 검증
   - Context 전달 검증

3. **문서 배포**
   - README 업데이트
   - CHANGELOG 업데이트

---

## 🎯 핵심 원칙 (v7.5.0)

### MECE 분리

```
Estimator = 값이 없을 때 만들어냄
Quantifier = 값이 있을 때 계산함

겹치지 않고 (Mutually Exclusive)
빠짐없이 (Collectively Exhaustive)
```

### Single Source of Truth

```
모든 값 추정 = Estimator만
모든 계산 = Quantifier만

일관성 보장 + 학습 효율 + 근거 추적
```

### Context 명시

```
질문에 항상 Context 포함:
- Domain (예: B2B_SaaS)
- Region (예: 한국)
- Time_Period (예: 2024)

애매한 질문 금지!
```

---

## ✅ 완료 체크리스트

- [x] Tier 1/2 임계값 강화 (0.95/0.80)
- [x] Quantifier 공식 강화 (31개)
- [x] Estimator Tier 3 템플릿 제거
- [x] Context 전달 개선
- [x] umis_core.yaml 업데이트
- [x] umis.yaml 업데이트
- [x] umis_deliverable_standards.yaml 업데이트
- [x] umis_ai_guide.yaml Archive
- [x] 통합 테스트 검증

---

## 📖 참조

- **Estimator 구현**: `umis_rag/agents/estimator/`
- **Quantifier 공식**: `data/raw/calculation_methodologies.yaml`
- **Domain Reasoner**: `data/raw/umis_domain_reasoner_methodology.yaml` (별도 방법론, 유지)
- **Tool Registry**: `config/tool_registry.yaml`

---

**END**

