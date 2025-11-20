# Domain Reasoner vs Estimator Tier 2 분석

**작성일**: 2025-11-10  
**목적**: 중복 여부 판단 및 처리 방향 결정

---

## 🔍 개념 비교

### Estimator Tier 2: Judgment Path

**위치**: `umis_rag/agents/estimator/tier2.py`  
**목적**: 값 추정 (데이터 없을 때)  
**방식**: 11개 Source 수집 + 종합 판단

#### 11개 Source

**Physical (3개)**:
1. SpacetimeConstraint (시공간 제약)
2. ConservationLaw (보존 법칙)
3. MathematicalDefinition (수학 정의)

**Soft (3개)**:
4. LegalNorm (법률 규범)
5. StatisticalPattern (통계 패턴)
6. BehavioralInsight (행동 통찰)

**Value (5개)**:
7. DefiniteData (확정 데이터)
8. LLMEstimation (LLM 추정)
9. WebSearch (웹 검색)
10. RAGBenchmark (RAG 벤치마크)
11. StatisticalValue (통계 값)

---

### Domain Reasoner: 10-Signal Stack

**위치**: `umis_rag/methodologies/domain_reasoner.py`  
**목적**: 정밀 분석 (신뢰도 높은 결과)  
**방식**: 10개 신호 우선순위 + 충돌 해결

#### 10개 신호 (우선순위 순)

1. **s3_laws_ethics_physics** (weight 1.0) → Hard Constraint
2. **s8_time_space_bounds** (weight 1.0) → Hard Constraint
3. **s6_math_relations** (weight 1.0) → 차원 분석
4. **s10_industry_kpi_library** (weight 0.95) → 정의 검증
5. **s2_rag_consensus** (weight 0.9) → RAG 합의
6. **s9_case_analogies** (weight 0.85) → 사례 전이
7. **s7_rules_of_thumb** (weight 0.7) → 경험 공식
8. **s5_stat_patterns** (weight 0.75) → 통계 패턴
9. **s4_behavioral_econ** (weight 0.6) → 행동경제학
10. **s1_llm_guess** (weight 0.15) → LLM 추측

---

## 📊 대응 관계

| Estimator Tier 2 (11 Sources) | Domain Reasoner (10 Signals) | 일치도 |
|-------------------------------|------------------------------|--------|
| SpacetimeConstraint | s8_time_space_bounds | 100% ✅ |
| ConservationLaw | s6_math_relations (일부) | 80% ✅ |
| MathematicalDefinition | s6_math_relations | 90% ✅ |
| LegalNorm | s3_laws_ethics_physics (law 부분) | 90% ✅ |
| StatisticalPattern | s5_stat_patterns | 100% ✅ |
| BehavioralInsight | s4_behavioral_econ | 100% ✅ |
| RAGBenchmark | s2_rag_consensus | 100% ✅ |
| LLMEstimation | s1_llm_guess | 100% ✅ |
| DefiniteData | (없음) | - |
| WebSearch | (없음) | - |
| StatisticalValue | s2_rag_consensus (일부) | 50% |
| (없음) | s10_industry_kpi_library | - |
| (없음) | s9_case_analogies | - |

**중복도**: **약 70-80%** 🔴

---

## 🎯 차이점

### 1. **목적**
- **Tier 2**: 빠른 값 추정 (3-8초)
- **Domain Reasoner**: 정밀 분석 (시간 제약 없음)

### 2. **출력**
- **Tier 2**: EstimationResult (value, confidence, reasoning)
- **Domain Reasoner**: 
  - point_estimate
  - range_estimate
  - should_vs_will
  - evidence_table
  - verification_log
  - signal_breakdown

### 3. **우선순위**
- **Tier 2**: 가중치 없음 (종합 판단)
- **Domain Reasoner**: 신호별 우선순위 (s3 → s8 → s6 → ...)

### 4. **KPI 정의 검증**
- **Tier 2**: 없음
- **Domain Reasoner**: s10 (KPI Library)

### 5. **Should vs Will**
- **Tier 2**: 없음
- **Domain Reasoner**: 행동경제학 보정

---

## 🔄 사용 현황

### Quantifier에서 사용

**메서드**: `calculate_sam_with_hybrid()`  
**흐름**:
```
Phase 1: Guestimation (빠른 추정)
  ↓
Guardian 평가
  ↓
Phase 2: Domain Reasoner (조건부, 정밀 분석)
```

**호출 위치**:
- ✅ `umis_rag/agents/quantifier.py` (구현됨)
- ❌ 실제 production에서 호출 없음
- ✅ `scripts/test_quantifier_hybrid.py` (테스트)
- ✅ `scripts/test_e2e_full_workflow.py` (테스트)

**결론**: **구현되어 있지만 실사용 안 됨** ⚠️

---

## 💡 판단

### Domain Reasoner 상태

| 항목 | 상태 |
|------|------|
| **구현** | ✅ 완료 (domain_reasoner.py, 1,907줄) |
| **Tool Registry** | ✅ 등록 (tool:universal:domain_reasoner_10_signals) |
| **Quantifier 통합** | ✅ 코드 존재 (calculate_sam_with_hybrid) |
| **실제 사용** | ❌ Production 호출 없음 |
| **테스트** | ✅ 존재 (11월 5일 수정) |
| **Tier 2 중복** | 🔴 70-80% 중복 |

---

## 🎯 추천: 2가지 옵션

### Option 1: Archive (추천) ⭐

**이유**:
1. **중복**: Estimator Tier 2와 70-80% 겹침
2. **미사용**: Production에서 호출 안 됨
3. **복잡도**: 1,907줄 (유지보수 부담)
4. **Tier 2가 충분**: 11개 Source로 커버 가능

**조치**:
```bash
# Archive 이동
mv umis_rag/methodologies/domain_reasoner.py \
   archive/v7.2.0_and_earlier/methodologies/

mv data/raw/umis_domain_reasoner_methodology.yaml \
   archive/v7.2.0_and_earlier/data/

# Quantifier 메서드 제거
# - calculate_sam_with_hybrid()
# - _execute_domain_reasoner()
```

**장점**:
- 코드 단순화 (1,907줄 제거)
- 중복 제거 (MECE 달성)
- Estimator Tier 2로 통합

**단점**:
- Should vs Will 기능 상실
- KPI Library (s10) 상실

---

### Option 2: 유지 + 역할 분리

**이유**:
1. **고급 기능**: Should vs Will, KPI Library 유용
2. **정밀 분석**: Tier 2보다 더 정밀한 분석 필요 시
3. **최근 작업**: 11월 5일 테스트 파일 수정

**조치**:
```python
# Quantifier만 사용하도록 명확화
class QuantifierRAG:
    def analyze_market_detailed(self, market_definition):
        """
        정밀 시장 분석 (Domain Reasoner 사용)
        
        vs calculate_sam(): 빠른 계산
        vs analyze_market_detailed(): 정밀 분석
        """
        # Phase 1: Estimator (빠른 추정)
        # Phase 2: Domain Reasoner (정밀 분석)
```

**장점**:
- Should vs Will 유지
- KPI Library 유지
- 정밀 분석 옵션 보존

**단점**:
- 복잡도 유지
- 중복 존재 (70-80%)
- 사용 빈도 낮음

---

## 📋 최종 권장사항

### **Option 1: Archive** ⭐

**근거**:
1. **Estimator Tier 2가 충분함** (11개 Source, confidence 0.80+)
2. **중복 70-80%** (MECE 위배)
3. **실사용 없음** (테스트만 존재)
4. **유지보수 부담** (1,907줄 + 1,033줄 YAML)

**대체 방안**:
- Should vs Will → Estimator Tier 2에 추가 가능
- KPI Library → Validator로 이동 가능
- 정밀 분석 → Estimator Tier 2 + Tier 3 조합

---

## 🚀 다음 단계 (Option 1 선택 시)

### 1. Archive 이동
```bash
mkdir -p archive/v7.2.0_and_earlier/methodologies
mkdir -p archive/v7.2.0_and_earlier/data

mv umis_rag/methodologies/domain_reasoner.py \
   archive/v7.2.0_and_earlier/methodologies/

mv data/raw/umis_domain_reasoner_methodology.yaml \
   archive/v7.2.0_and_earlier/data/
```

### 2. Quantifier 정리
```python
# quantifier.py에서 제거
- calculate_sam_with_hybrid()
- _execute_domain_reasoner()
- _execute_guestimation()
```

### 3. Tool Registry 정리
```yaml
# config/tool_registry.yaml에서 제거
- tool:universal:domain_reasoner_10_signals
```

### 4. 테스트 파일 Archive
```bash
mv scripts/test_quantifier_hybrid.py \
   archive/v7.2.0_and_earlier/scripts/

mv scripts/test_e2e_full_workflow.py \
   archive/v7.2.0_and_earlier/scripts/

mv scripts/test_signal*.py \
   archive/v7.2.0_and_earlier/scripts/
```

---

**END**

