# Estimator Agent (v7.11.0 Fusion Architecture)

**4-Stage Fusion Architecture** - 재귀 없는 빠르고 정확한 값 추정

---

## 📋 개요

Estimator는 **4-Stage Fusion Architecture**로 모든 값 추정 문제를 해결합니다.

### v7.11.0 주요 변경사항

#### 재귀 제거 ✅
- **Before (v7.10.2)**: Phase 4 재귀 (max_depth=4, 10-30초)
- **After (v7.11.0)**: Stage 3 Fermi (max_depth=2, 3-5초)
- **속도 향상**: 3-10배

#### 아키텍처 변경 ✅
- **Phase 0-4 (5단계)** → **Stage 1-4 (4단계)**
- Phase 3 Guestimation → Stage 2 Generative Prior
- Phase 4 Fermi → Stage 3 Structural Explanation (재귀 없음)

#### 용어 개선 ✅
| 이전 | v7.11.0 | 의미 |
|------|---------|------|
| `phase` | `source` | 추정 소스 |
| `confidence` | `certainty` | LLM 내부 확신도 |
| Phase3Config | `Budget` | 자원 제한 |

---

## 🎯 4-Stage Fusion Architecture

```
Stage 1: Evidence Collection
├─ Literal (프로젝트 데이터, <0.01초)
├─ Direct RAG (학습 규칙, <0.5초)
├─ Validator Search (확정 데이터, <1초, 85% 처리!)
└─ Guardrail Engine (제약 수집)
→ Early Return (확정값 발견 시 즉시 반환)

Stage 2: Generative Prior
└─ LLM 직접 값 요청 (~3초)
   + Certainty (high/medium/low)

Stage 3: Structural Explanation (Fermi)
└─ 구조적 분해 (~5초)
   - 재귀 없음 (max_depth=2)
   - 변수 추정 시 Stage 2 사용

Stage 4: Fusion & Validation
└─ 모든 Stage 결과 가중 합성 (<1초)
```

---

## 🚀 사용법

### 기본 사용

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("B2B SaaS ARPU는?")

if result.is_successful():
    print(f"값: {result.value}")
    print(f"소스: {result.source}")  # Literal, Prior, Fermi, Fusion
    print(f"확신도: {result.certainty}")  # high, medium, low
```

### Budget 설정

```python
from umis_rag.agents.estimator.common import create_standard_budget, create_fast_budget

# Standard Budget (기본)
budget = create_standard_budget()  # max_llm_calls=10
result = estimator.estimate(question, budget=budget)

# Fast Budget (빠른 추정)
budget = create_fast_budget()  # max_llm_calls=3
result = estimator.estimate(question, budget=budget)
```

### Context 활용

```python
from umis_rag.agents.estimator.models import Context

result = estimator.estimate(
    question="2025년 AI 챗봇 ARPU는?",
    context=Context(
        domain="AI_Chatbot",
        region="한국",
        time_period="2025"
    )
)
```

---

## 📊 Stage별 컴포넌트

### Stage 1: Evidence Collection

**역할**: 확정 데이터 수집 (85% 처리)

**컴포넌트**:
- `Literal`: 프로젝트 데이터 확인
- `Direct RAG`: 학습된 규칙 검색
- `Validator Search`: 확정 데이터 검색
- `Guardrail Engine`: 논리적/경험적 제약 수집

**사용**:
```python
from umis_rag.agents.estimator import EvidenceCollector

collector = EvidenceCollector()
evidence = collector.collect(question, context, project_data)
```

### Stage 2: Generative Prior

**역할**: LLM 직접 값 요청

**특징**:
- 단일 LLM 호출
- Certainty (high/medium/low) 반환
- 재귀 금지

**사용**:
```python
from umis_rag.agents.estimator import PriorEstimator
from umis_rag.agents.estimator.common import Evidence, create_standard_budget

prior = PriorEstimator()
result = prior.estimate(
    question=question,
    evidence=Evidence(),
    budget=create_standard_budget(),
    context=context
)
```

### Stage 3: Structural Explanation (Fermi)

**역할**: 구조적 분해

**특징**:
- 재귀 없음 (max_depth=2)
- 변수 추정 시 PriorEstimator 사용
- 2-4개 변수로 분해

**사용**:
```python
from umis_rag.agents.estimator import FermiEstimator, PriorEstimator

prior = PriorEstimator()
fermi = FermiEstimator(prior_estimator=prior)
result = fermi.estimate(
    question=question,
    evidence=evidence,
    budget=budget,
    context=context,
    depth=0
)
```

### Stage 4: Fusion & Validation

**역할**: 모든 Stage 결과 가중 합성

**특징**:
- 증거 기반 가중치
- LLM 미사용 (계산만)

**사용**:
```python
from umis_rag.agents.estimator import FusionLayer

fusion = FusionLayer()
result = fusion.fuse(results_from_stages)
```

---

## 🔄 마이그레이션 가이드

### Phase 3 → Stage 2

```python
# Before (v7.10.2)
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
phase3 = Phase3Guestimation()
result = phase3.estimate(question, context)

# After (v7.11.0)
from umis_rag.agents.estimator import PriorEstimator
from umis_rag.agents.estimator.common import Evidence, create_standard_budget

prior = PriorEstimator()
result = prior.estimate(
    question=question,
    evidence=Evidence(),
    budget=create_standard_budget(),
    context=context
)
```

### Phase 4 → Stage 3

```python
# Before (v7.10.2)
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
phase4 = Phase4FermiDecomposition()
result = phase4.estimate(question, context, available_data={}, depth=0)

# After (v7.11.0)
from umis_rag.agents.estimator import FermiEstimator, PriorEstimator
from umis_rag.agents.estimator.common import Evidence, create_standard_budget

prior = PriorEstimator()
fermi = FermiEstimator(prior_estimator=prior)
result = fermi.estimate(
    question=question,
    evidence=Evidence(),
    budget=create_standard_budget(),
    context=context,
    depth=0
)
```

### 하위 호환성

```python
# v7.11.0에서도 작동 (DeprecationWarning 발생)
from umis_rag.agents.estimator import Phase3Guestimation, Phase4FermiDecomposition

phase3 = Phase3Guestimation()  # → 내부적으로 PriorEstimator 사용
phase4 = Phase4FermiDecomposition()  # → 내부적으로 FermiEstimator 사용
```

---

## 📚 문서

- **[API 문서](../../docs/api/ESTIMATOR_API_v7_11_0.md)** - 전체 API 레퍼런스
- **[User Guide](../../docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md)** - 사용자 가이드
- **[Migration Plan](../../dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md)** - 마이그레이션 계획
- **[Migration Complete](../../dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md)** - 완료 보고서

---

## 🧪 테스트

```bash
# Unit Tests
pytest tests/unit/test_prior_estimator.py
pytest tests/unit/test_fermi_estimator.py

# Integration Tests
pytest tests/integration/test_stage_flow_v7_11_0.py

# AB Testing
pytest tests/ab_testing/test_stage_ab_framework_v7_11_0.py
```

---

## 📈 성능

### 속도 비교

| Stage | v7.10.2 (Phase) | v7.11.0 (Stage) | 개선 |
|-------|-----------------|-----------------|------|
| Evidence | <1초 | <1초 | - |
| Prior | ~3초 | ~3초 | - |
| Fermi | 10-30초 (재귀) | 3-5초 (재귀 없음) | **3-10배** |
| Fusion | - | <1초 | 신규 |

### LLM 호출 횟수

| Stage | v7.10.2 | v7.11.0 | 개선 |
|-------|---------|---------|------|
| Prior | 1-3회 | 1회 | - |
| Fermi | 5-20회 (재귀) | 3-5회 | **50% 감소** |

---

## ✨ v7.11.0 주요 개선사항

1. ✅ **재귀 제거**: 속도 3-10배 향상
2. ✅ **Budget 기반 탐색**: 자원 명시적 제어
3. ✅ **Early Return**: Stage 1에서 85% 처리
4. ✅ **Certainty**: LLM 내부 확신도 (high/medium/low)
5. ✅ **하위 호환성**: Graceful Deprecation (compat.py)
6. ✅ **예측 가능성**: max_depth=2 고정

---

**Estimator v7.11.0 - Fusion Architecture**
