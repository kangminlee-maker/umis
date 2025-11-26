# Phase 3-4 테스트 카탈로그 (v7.11.0)

**날짜:** 2025-11-26  
**Task:** Phase 1.2 - 테스트 카탈로그 작성  
**목적:** Phase 3-4 관련 테스트 분류 및 전환 전략 수립

---

## 📊 전체 요약

### 테스트 현황
- **전체 테스트 파일:** 30개
- **Phase 3-4 관련:** 22개
- **v7.11.0 신규:** 3개 (이미 Stage 기반)
- **무관:** 5개

---

## 🎯 Phase 3-4 관련 테스트 분류

### Category A: 자동 전환 가능 (8개)
> Import만 수정하면 동작하는 테스트

| # | 파일 | 내용 | 전환 후 |
|---|------|------|---------|
| A1 | `unit/test_phase3_guestimation.py` | Phase 3 Unit Test | `unit/test_prior_estimator.py` |
| A2 | `unit/test_phase4_fermi.py` | Phase 4 Unit Test | `unit/test_fermi_estimator.py` |
| A3 | `test_phase2_threshold.py` | Phase 2 Threshold 테스트 | `test_validator_threshold.py` |
| A4 | `test_model_config_live.py` | Phase 3-4 모델 Config 라이브 테스트 | `test_model_config_live.py` (Stage 기반 수정) |
| A5 | `test_model_configs.py` | Phase Config 테스트 | `test_model_configs.py` (Stage 기반 수정) |
| A6 | `test_model_configs_simulation.py` | Phase Config 시뮬레이션 | `test_model_configs_simulation.py` (Stage 기반 수정) |
| A7 | `unit/test_guardrail_collector.py` | Guardrail Collector (Phase 2 관련) | 유지 (Stage 1 연관) |
| A8 | `unit/test_guardrail_analyzer.py` | Guardrail Analyzer | 유지 (Stage 1 연관) |

**전환 작업:**
- Import 수정: `Phase3Guestimation` → `PriorEstimator`
- Assertion 수정: `result.phase == 3` → `result.source == 'Generative Prior'`
- 예상 시간: 파일당 15-30분 (총 2-4시간)

---

### Category B: 수동 재작성 필요 (6개)
> 로직 변경이 필요한 테스트

| # | 파일 | 내용 | 이유 | 전환 후 |
|---|------|------|------|---------|
| B1 | `integration/test_phase_flow.py` | Phase 0→1→2→3→4 Flow | Phase 개념 → Stage 개념 | `integration/test_stage_flow_v7_11_0.py` |
| B2 | `integration/test_hybrid_integration.py` | Hybrid Architecture Integration | Phase 3-4 병렬 → Stage 2-3 독립 | `integration/test_fusion_integration.py` |
| B3 | `unit/test_hybrid_architecture.py` | Hybrid Architecture Unit | 동일 | `unit/test_fusion_architecture.py` |
| B4 | `test_phase_0_4_comprehensive.py` | Phase 0-4 Comprehensive | Phase Fallback → Stage 독립성 | `test_stage_comprehensive_v7_11_0.py` |
| B5 | `test_estimator_phase0_4.py` | Estimator Phase 0-4 | 동일 | `test_estimator_stages_v7_11_0.py` |
| B6 | `ab_testing/test_ab_framework.py` | Phase 3-4 AB 테스트 | Metric 재정의 (certainty, budget) | `ab_testing/test_ab_framework.py` (Stage 기반 재작성) |

**전환 작업:**
- Flow 재설계: Early Return, Stage 독립성, Budget 테스트
- Metric 재정의: `confidence` → `certainty`, `phase` → `source`
- 예상 시간: 파일당 1-2시간 (총 6-12시간)

---

### Category C: Archive 이동 (8개)
> 레거시 전용 테스트 (재귀, Step 1-4 등)

| # | 파일 | 내용 | Archive 이유 |
|---|------|------|------------|
| C1 | `test_phase4_model_config.py` | Phase 4 Model Config | Phase 4 재귀 전용 로직 |
| C2 | `test_phase4_creative.py` | Phase 4 Creative 테스트 | Phase 4 특정 프롬프트 |
| C3 | `test_phase4_quick.py` | Phase 4 Quick 테스트 | Phase 4 재귀 로직 |
| C4 | `test_phase4_quick_final.py` | Phase 4 Quick Final | 동일 |
| C5 | `test_phase4_parsing_fix.py` | Phase 4 JSON Parsing Fix | Phase 4 특정 버그 수정 테스트 |
| C6 | `test_estimator_comprehensive.py` | Estimator Comprehensive (Phase 포함) | Phase 0-4 전체 로직 |
| C7 | `test_v7_11_0_recursive_explosion_check.py` | 재귀 폭발 체크 (Phase 4 문제) | 재귀 제거 완료 후 불필요 |
| C8 | `performance/test_performance.py` | Phase 3-4 성능 테스트 | 레거시 성능 메트릭 |

**처리:**
- `archive/tests_phase3_4_legacy_v7.10.2/` 이동
- README 작성 (Archive 이유)
- 예상 시간: 1시간

---

### Category D: v7.11.0 신규 (3개, 이미 Stage 기반)
> 전환 불필요

| # | 파일 | 내용 | 상태 |
|---|------|------|-----|
| D1 | `test_v7_11_0_fermi_10problems.py` | 10개 Fermi 문제 (Stage 기반) | ✅ 유지 |
| D2 | `test_v7_11_0_fusion_architecture.py` | Fusion Architecture 테스트 | ✅ 유지 |
| D3 | `test_phase0_guardrail_v7_11_0.py` | Phase 0 & Guardrail (Stage 1) | ✅ 유지 |

**처리:** 변경 없음

---

### Category E: 무관 (5개)
> Phase 3-4와 무관한 테스트

| # | 파일 | 내용 |
|---|------|------|
| E1 | `test_evidence_collector.py` | Evidence Collector (Stage 1) |
| E2 | `test_integration_timeline.py` | Timeline Integration |
| E3 | `test_observer_timeline.py` | Observer Timeline |
| E4 | `test_strategy_playbook.py` | Strategy Playbook |
| E5 | `edge_cases/test_edge_cases.py` | Edge Cases |

**처리:** 변경 없음

---

## 📋 상세 전환 전략

### A1: `unit/test_phase3_guestimation.py` → `unit/test_prior_estimator.py`

**현재 코드 (예상):**
```python
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation

class TestPhase3Guestimation:
    def test_estimate(self):
        phase3 = Phase3Guestimation()
        result = phase3.estimate("B2B SaaS Churn Rate는?")
        
        assert result is not None
        assert result.phase == 3
        assert result.confidence >= 0.60
```

**전환 후:**
```python
from umis_rag.agents.estimator import PriorEstimator

class TestPriorEstimator:
    def test_estimate(self):
        prior = PriorEstimator()
        result = prior.estimate("B2B SaaS Churn Rate는?")
        
        assert result is not None
        assert result.source == "Generative Prior"
        assert result.certainty in ['high', 'medium', 'low']
```

**변경 사항:**
- Import: `Phase3Guestimation` → `PriorEstimator`
- Class: `TestPhase3Guestimation` → `TestPriorEstimator`
- Assertion: `result.phase == 3` → `result.source == "Generative Prior"`
- Assertion: `result.confidence` → `result.certainty`

---

### A2: `unit/test_phase4_fermi.py` → `unit/test_fermi_estimator.py`

**전환 후:**
```python
from umis_rag.agents.estimator import FermiEstimator, PriorEstimator
from umis_rag.agents.estimator.common import Budget, create_standard_budget

class TestFermiEstimator:
    def test_decompose(self):
        prior = PriorEstimator()
        fermi = FermiEstimator(llm_mode='external', prior_estimator=prior)
        budget = create_standard_budget()
        
        result = fermi.estimate(
            question="서울 음식점 수는?",
            budget=budget,
            depth=0
        )
        
        assert result is not None
        assert result.source == "Fermi"
        assert result.decomposition is not None  # Fermi 분해 확인
```

**핵심 변경:**
- `Phase4FermiDecomposition` → `FermiEstimator`
- `prior_estimator` 주입 (의존성 역전)
- `budget` 파라미터 추가 (재귀 대신)
- `depth` 파라미터 (max_depth=2)

---

### B1: `integration/test_phase_flow.py` → `integration/test_stage_flow_v7_11_0.py`

**새로운 Flow 테스트:**
```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_fast_budget

class TestStageFlow:
    def test_stage1_early_return(self):
        """Stage 1 Early Return (Literal 확정 값)"""
        estimator = EstimatorRAG(project_id="test_project")
        result = estimator.estimate("Churn Rate는?")  # Literal에 저장된 값
        
        assert result.source in ['Literal', 'Direct RAG', 'Validator Search']
        assert result.cost['llm_calls'] == 0  # Stage 1만 사용
    
    def test_stage2_generative_prior(self):
        """Stage 2 Generative Prior"""
        estimator = EstimatorRAG()
        result = estimator.estimate("B2B SaaS LTV는?", use_fermi=False)
        
        assert result.source in ['Generative Prior', 'Fusion']
        assert result.certainty in ['high', 'medium', 'low']
    
    def test_stage3_fermi(self):
        """Stage 3 Fermi (재귀 없음)"""
        estimator = EstimatorRAG()
        result = estimator.estimate("서울 음식점 수는?")
        
        # Fermi 또는 Fusion
        assert result.source in ['Fermi', 'Fusion']
        if result.decomposition:
            assert len(result.decomposition['variables']) <= 4
    
    def test_stage4_fusion(self):
        """Stage 4 Fusion (Prior + Fermi)"""
        estimator = EstimatorRAG()
        budget = create_standard_budget()
        result = estimator.estimate("B2B SaaS Churn Rate는?", budget=budget)
        
        # Fusion 확률 높음
        if result.source == 'Fusion':
            assert result.fusion_weights is not None
            assert 'prior' in result.fusion_weights or 'fermi' in result.fusion_weights
```

**핵심 변경:**
- Phase 0→1→2→3→4 Fallback → Stage 1-4 독립 실행
- Early Return 테스트
- Budget 테스트
- Fusion 테스트

---

### C1-C8: Archive 이동

**디렉터리 생성:**
```bash
mkdir -p archive/tests_phase3_4_legacy_v7.10.2/
```

**이동 대상:**
```bash
mv tests/test_phase4_model_config.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_phase4_creative.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_phase4_quick.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_phase4_quick_final.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_phase4_parsing_fix.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_estimator_comprehensive.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/test_v7_11_0_recursive_explosion_check.py archive/tests_phase3_4_legacy_v7.10.2/
mv tests/performance/test_performance.py archive/tests_phase3_4_legacy_v7.10.2/
```

**README 작성:**
```markdown
# Phase 3-4 레거시 테스트 Archive

**이동일:** 2025-11-26  
**v7.11.0 마이그레이션**

## Archive 이유

이 테스트들은 v7.10.2 Phase 3-4 아키텍처 전용입니다:
- 재귀 로직 테스트
- Phase 4 Step 1-4 세부 테스트
- 레거시 성능 메트릭

v7.11.0 Fusion Architecture에서는:
- 재귀 완전 제거
- Stage 1-4 독립 실행
- Budget 기반 탐색

## 복원 방법

필요 시 역사적 참고용으로 사용:
```bash
cp archive/tests_phase3_4_legacy_v7.10.2/*.py tests/
```
```

---

## 📊 전환 통계

| Category | 파일 수 | 예상 시간 | 처리 방식 |
|----------|---------|----------|---------|
| A: 자동 전환 | 8개 | 2-4시간 | Import + Assertion 수정 |
| B: 수동 재작성 | 6개 | 6-12시간 | Flow + Metric 재설계 |
| C: Archive | 8개 | 1시간 | 이동 + README |
| D: v7.11.0 신규 | 3개 | 0시간 | 유지 |
| E: 무관 | 5개 | 0시간 | 유지 |
| **총계** | **30개** | **9-17시간** | |

---

## ✅ Coverage 목표

### 현재 Coverage (예상)
- **Phase 0-4 전체:** ~85%
- **Phase 3-4 집중:** ~90%

### 전환 후 Coverage (목표)
- **Stage 1-4 전체:** 80% 이상
- **Stage 2-3 집중:** 85% 이상

### Coverage 유지 전략
1. **Category A (8개):** 100% 전환 → Coverage 유지
2. **Category B (6개):** 100% 재작성 → Coverage 향상
3. **Category C (8개):** Archive → 신규 테스트로 대체 (D1-D3)
4. **Category D (3개):** 이미 80%+ Coverage

---

## 🎯 우선순위

### High Priority (즉시 실행)
1. **A1-A2:** Unit Tests (Prior, Fermi)
2. **B1:** Stage Flow 테스트
3. **C1-C8:** Archive 이동

### Medium Priority (Phase 3)
4. **B2-B6:** Integration, AB Testing
5. **A3-A8:** 나머지 자동 전환

### Low Priority (Phase 4)
6. Coverage 보고서 작성
7. 신규 테스트 추가 (필요 시)

---

## 📋 체크리스트

### Phase 1.2 완료 조건
- [x] 전체 30개 테스트 파일 분류
- [x] Category A-E 정의
- [x] 전환 전략 수립
- [x] 예상 시간 산정 (9-17시간)
- [x] Coverage 목표 설정 (80%)
- [x] 우선순위 지정

---

## 🔗 다음 단계

**Phase 1.3: 문서 인벤토리 (156개 문서 스캔 및 분류)**

---

**작성자:** AI Assistant  
**작성일:** 2025-11-26  
**Task:** Phase 1.2 완료 ✅

**끝.**

