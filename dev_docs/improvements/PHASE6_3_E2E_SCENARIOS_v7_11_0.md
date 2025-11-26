# Phase 6.3: E2E 시나리오 테스트 설계 (v7.11.0)

**날짜:** 2025-11-26  
**버전:** v7.11.0  
**상태:** ✅ 완료

---

## 📋 개요

v7.11.0 Fusion Architecture의 실제 사용 시나리오를 검증하는 End-to-End 테스트 설계 및 구현

---

## 🎯 목표

1. **실제 사용자 시나리오 커버** - 10개 대표 시나리오
2. **4-Stage Fusion Architecture 검증** - Stage 1→2→3→4 흐름
3. **Budget 기반 탐색 검증** - Fast vs Standard Budget
4. **Early Return 검증** - Literal, Validator 우선
5. **하위 호환성 검증** - Legacy API 지원
6. **성능 벤치마크** - 속도, LLM 호출, 성공률

---

## 📊 10개 E2E 시나리오

### Scenario 1: B2B SaaS ARPU 추정 (Stage 2 Prior)

**목표:** Stage 2 Generative Prior 검증

**입력:**
```python
question = "B2B SaaS 평균 ARPU는?"
context = Context(domain="B2B_SaaS", business_model="subscription", region="글로벌")
budget = create_standard_budget()
```

**검증:**
- `source = "Generative Prior"` (또는 Fusion)
- `certainty in ["high", "medium", "low"]`
- `value in [50, 500]` (USD/month)
- `reasoning` 존재 (>50자)

---

### Scenario 2: E-commerce Churn Rate 추정 (Stage 2 Prior)

**목표:** Stage 2 Generative Prior 검증 (비율)

**입력:**
```python
question = "E-commerce 구독 서비스 월 해지율은?"
context = Context(domain="E-commerce", business_model="subscription", region="한국")
budget = create_standard_budget()
```

**검증:**
- `source in ["Generative Prior", "Fusion"]`
- `certainty in ["high", "medium", "low"]`
- `value in [0.01, 0.15]` (1-15% monthly churn)

---

### Scenario 3: 음악 스트리밍 시장 규모 추정 (Stage 3 Fermi)

**목표:** Stage 3 Fermi 구조적 분해 검증

**입력:**
```python
question = "2025년 글로벌 음악 스트리밍 시장 규모는?"
context = Context(domain="Music_Streaming", time_period="2025", region="글로벌")
budget = create_standard_budget()
```

**검증:**
- `source in ["Fermi", "Fusion", "Generative Prior"]`
- `certainty in ["high", "medium", "low"]`
- `value in [1e9, 100e9]` (1B-100B USD)

---

### Scenario 4: AI 챗봇 LTV 추정 (Stage 4 Fusion)

**목표:** Stage 4 Fusion 가중 합성 검증

**입력:**
```python
question = "AI 챗봇 SaaS 고객 LTV는?"
context = Context(domain="AI_Chatbot", business_model="subscription", region="글로벌")
budget = create_standard_budget()
```

**검증:**
- `source in ["Generative Prior", "Fermi", "Fusion"]`
- `certainty in ["high", "medium", "low"]`
- `value in [50, 10000]` (50-10000 USD)

---

### Scenario 5: 구독 모델 CAC 추정 (Stage 2 Prior)

**목표:** Stage 2 Generative Prior 검증 (CAC)

**입력:**
```python
question = "구독 모델 평균 CAC는?"
context = Context(domain="Subscription", business_model="subscription", region="한국")
budget = create_standard_budget()
```

**검증:**
- `source in ["Generative Prior", "Fusion"]`
- `certainty in ["high", "medium", "low"]`
- `value in [5, 1000]` (5-1000 USD)

---

### Scenario 6: Fast Budget 빠른 추정 (Budget Control)

**목표:** Fast Budget (max_llm_calls=3) 검증

**입력:**
```python
question = "모바일 앱 평균 ARPU는?"
context = Context(domain="Mobile_App")
budget = create_fast_budget()  # max_llm_calls=3
```

**검증:**
- `cost['llm_calls'] ≤ 3`
- `elapsed < 10초`
- `source in ["Generative Prior", "Fusion"]`

---

### Scenario 7: Standard Budget 정밀 추정 (Budget Control)

**목표:** Standard Budget (max_llm_calls=10) 검증

**입력:**
```python
question = "B2B SaaS 평균 월 매출 성장률은?"
context = Context(domain="B2B_SaaS", business_model="subscription")
budget = create_standard_budget()  # max_llm_calls=10
```

**검증:**
- `cost['llm_calls'] ≤ 10`
- `source in ["Generative Prior", "Fermi", "Fusion"]`
- 더 정밀한 추정

---

### Scenario 8: Literal Evidence 즉시 반환 (Stage 1 Early Return)

**목표:** Stage 1 Literal Evidence Early Return 검증

**입력:**
```python
question = "테스트용 ARPU는?"
context = Context(domain="Test")
budget = create_standard_budget()
project_data = {"arpu": 100.0, "arpu_confidence": "확정"}
```

**검증:**
- `source = "Literal"`
- `certainty = "high"`
- `cost['llm_calls'] = 0`
- `elapsed < 1초`
- `value = 100.0`

---

### Scenario 9: Validator 확정 데이터 우선 (Stage 1 Validator)

**목표:** Stage 1 Validator 확정 데이터 우선 검색 검증

**입력:**
```python
question = "Netflix 2024년 연간 ARPU는?"
context = Context(domain="Streaming", company="Netflix", time_period="2024")
budget = create_standard_budget()
```

**검증:**
- `source in ["Validator", "Generative Prior", "Fermi", "Fusion"]`
- Validator 검색 시도 확인
- `certainty in ["high", "medium", "low"]`

---

### Scenario 10: Legacy API 하위 호환성 (Backward Compatibility)

**목표:** Phase3Guestimation, Phase4FermiDecomposition 하위 호환성 검증

**입력:**
```python
from umis_rag.agents.estimator import Phase3Guestimation, Phase4FermiDecomposition

phase3 = Phase3Guestimation()  # → PriorEstimator
phase4 = Phase4FermiDecomposition()  # → FermiEstimator
```

**검증:**
- `DeprecationWarning` 발생
- `PriorEstimator`, `FermiEstimator`로 자동 매핑
- 정상 작동

---

## 🚀 성능 벤치마크

### 10개 질문 연속 처리

**목표:** 실제 운영 환경 성능 검증

**테스트:**
- 10개 질문 연속 처리 (Fast Budget)
- B2B SaaS, E-commerce, Mobile App, AI Chatbot, Subscription, SaaS, Cloud, Gaming, Fintech, Edtech

**검증:**
- 전체 시간 < 120초
- 평균 시간 < 15초
- 성공률 ≥ 80%

**목표 성능:**
| 지표 | 목표 | 실제 |
|------|------|------|
| 전체 시간 | <120초 | TBD |
| 평균 시간 | <15초 | TBD |
| 성공률 | ≥80% | TBD |

---

## 📁 테스트 파일

### 위치
```
tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py
```

### 구조
```python
class TestEstimatorE2EScenarios:
    """10개 E2E 시나리오 테스트"""
    
    def test_scenario_1_b2b_saas_arpu(self, estimator)
    def test_scenario_2_ecommerce_churn(self, estimator)
    def test_scenario_3_music_streaming_market(self, estimator)
    def test_scenario_4_ai_chatbot_ltv(self, estimator)
    def test_scenario_5_subscription_cac(self, estimator)
    def test_scenario_6_fast_budget_estimation(self, estimator)
    def test_scenario_7_standard_budget_estimation(self, estimator)
    def test_scenario_8_literal_evidence_early_return(self, estimator)
    def test_scenario_9_validator_priority(self, estimator)
    def test_scenario_10_legacy_api_compatibility(self)

class TestEstimatorE2EPerformance:
    """성능 벤치마크"""
    
    def test_performance_benchmark_10_questions(self, estimator)
```

---

## 🧪 실행 방법

### 전체 E2E 테스트
```bash
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v
```

### 특정 시나리오
```bash
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py::TestEstimatorE2EScenarios::test_scenario_1_b2b_saas_arpu -v
```

### 성능 벤치마크
```bash
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py::TestEstimatorE2EPerformance::test_performance_benchmark_10_questions -v
```

### 결과 상세 출력
```bash
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v -s
```

---

## ✅ 검증 항목

### Stage 기반 Source
- [ ] Stage 1 (Literal) → `source = "Literal"`
- [ ] Stage 1 (Validator) → `source = "Validator"`
- [ ] Stage 2 (Prior) → `source = "Generative Prior"`
- [ ] Stage 3 (Fermi) → `source = "Fermi"`
- [ ] Stage 4 (Fusion) → `source = "Fusion"`

### Certainty
- [ ] `certainty in ["high", "medium", "low"]`
- [ ] Literal → `certainty = "high"`

### Budget Control
- [ ] Fast Budget → `max_llm_calls ≤ 3`
- [ ] Standard Budget → `max_llm_calls ≤ 10`

### Early Return
- [ ] Literal Evidence → 0 LLM calls, <1초
- [ ] Validator Priority → 우선 검색 시도

### Backward Compatibility
- [ ] Phase3Guestimation → PriorEstimator
- [ ] Phase4FermiDecomposition → FermiEstimator
- [ ] DeprecationWarning 발생

### Performance
- [ ] 10개 질문 < 120초
- [ ] 평균 < 15초
- [ ] 성공률 ≥ 80%

---

## 📊 예상 결과

### Scenario Coverage

| Scenario | Stage | LLM Calls | Time | Success |
|----------|-------|-----------|------|---------|
| 1. B2B SaaS ARPU | 2 | 1-3 | 3-5s | ✅ |
| 2. E-commerce Churn | 2 | 1-3 | 3-5s | ✅ |
| 3. Music Streaming | 2-3 | 3-7 | 5-10s | ✅ |
| 4. AI Chatbot LTV | 2-4 | 3-10 | 5-15s | ✅ |
| 5. Subscription CAC | 2 | 1-3 | 3-5s | ✅ |
| 6. Fast Budget | 2 | 1-3 | 3-5s | ✅ |
| 7. Standard Budget | 2-3 | 3-10 | 5-15s | ✅ |
| 8. Literal Evidence | 1 | 0 | <1s | ✅ |
| 9. Validator Priority | 1-2 | 0-3 | 1-5s | ✅ |
| 10. Legacy API | - | - | - | ✅ |

---

## 🎯 성공 기준

### 필수 (Must Pass)
- [x] 10개 시나리오 모두 구현
- [ ] 8개 이상 시나리오 Pass (80%)
- [ ] Stage 기반 Source 검증
- [ ] Certainty 검증
- [ ] Budget Control 검증
- [ ] Early Return 검증
- [ ] Backward Compatibility 검증

### 권장 (Should Pass)
- [ ] 성능 벤치마크 Pass
- [ ] 10개 질문 < 120초
- [ ] 평균 < 15초
- [ ] 성공률 ≥ 80%

---

## 📝 다음 단계

1. **E2E 테스트 실행** - `pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v`
2. **결과 분석** - Pass/Fail 확인
3. **실패 시나리오 디버깅** - 로그 확인, 수정
4. **성능 최적화** - 병목 지점 개선
5. **문서 업데이트** - 실제 결과 반영

---

**Phase 6.3 E2E 시나리오 테스트 설계 완료!** ✅

