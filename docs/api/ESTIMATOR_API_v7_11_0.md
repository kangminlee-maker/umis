# Estimator API 문서 (v7.11.0 Fusion Architecture)

**버전**: v7.11.0  
**최종 업데이트**: 2025-11-26  
**아키텍처**: 4-Stage Fusion Architecture (재귀 없음, Budget 기반)

---

## 📋 목차

1. [개요](#개요)
2. [EstimatorRAG](#estimatorrag)
3. [Stage 컴포넌트](#stage-컴포넌트)
4. [EstimationResult](#estimationresult)
5. [Budget](#budget)
6. [Context](#context)
7. [사용 예시](#사용-예시)
8. [마이그레이션 가이드](#마이그레이션-가이드)

---

## 개요

Estimator는 **4-Stage Fusion Architecture**로 값을 추정하는 시스템입니다.

### v7.11.0 주요 변경사항

#### 🎯 Phase → Stage 전환
- **Phase 0-4** (5단계) → **Stage 1-4** (4단계)
- **재귀 제거**: Phase 4 재귀 로직 완전 제거
- **Budget 기반 탐색**: Phase3Config/Phase4Config → Budget

#### 🔄 용어 변경
| Legacy (v7.10.2) | v7.11.0 | 설명 |
|------------------|---------|------|
| `phase` (0-4) | `source` (Literal, Prior, Fermi, Fusion 등) | 추정 소스 |
| `confidence` (0.0-1.0) | `certainty` (high/medium/low) | LLM 내부 확신도 |
| Phase3Config/Phase4Config | `Budget` | 자원 제한 (max_llm_calls, max_depth) |

### Stage 순서

| Stage | 이름 | 설명 | 속도 | 정확도 |
|-------|------|------|------|--------|
| **1** | Evidence Collection | Literal + Direct RAG + Validator + Guardrails | ⚡ <1s | ⭐⭐⭐⭐⭐ 90-100% |
| **2** | Generative Prior | LLM 직접 값 요청 | 🕐 ~3s | ⭐⭐⭐ 70-80% |
| **3** | Structural Explanation (Fermi) | 구조적 분해 (재귀 없음, max_depth=2) | 🕐 ~5s | ⭐⭐⭐ 60-70% |
| **4** | Fusion & Validation | 모든 Stage 결과 가중 합성 | ⚡ <1s | ⭐⭐⭐⭐ 80-90% |

**Early Return**:
- Stage 1에서 확정값 발견 시 즉시 반환 (Literal, Direct RAG 등)
- 각 Stage는 독립적으로 실행 (병렬 가능)

---

## EstimatorRAG

### 클래스 정의

```python
class EstimatorRAG:
    """
    Fermi 추정 Agent (v7.11.0 Fusion Architecture)
    
    Stage 순서:
    1. Evidence Collection (Literal + Direct RAG + Validator + Guardrails)
    2. Generative Prior (LLM 직접 값 요청)
    3. Structural Explanation (Fermi, 재귀 없음)
    4. Fusion & Validation (가중 합성)
    
    v7.11.0 주요 변경사항:
    - 재귀 제거 (Phase 4 재귀 → Fermi max_depth=2)
    - Budget 기반 탐색 (max_llm_calls, max_runtime)
    - Certainty (high/medium/low) 도입
    - source (Literal, Prior, Fermi, Fusion) 사용
    """
```

### estimate()

**시그니처**:
```python
def estimate(
    self,
    question: str,
    project_data: Optional[Dict] = None,
    context: Optional[Context] = None,
    budget: Optional[Budget] = None  # v7.11.0: Budget 추가
) -> EstimationResult:
```

**파라미터**:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `question` | `str` | ✅ | - | 추정할 질문 (예: "B2B SaaS ARPU는?") |
| `project_data` | `Dict` | ❌ | `None` | 프로젝트 확정 데이터 (Stage 1 Literal) |
| `context` | `Context` | ❌ | `None` | 맥락 정보 (domain, region, time_period 등) |
| `budget` | `Budget` | ❌ | `None` | 자원 제한 (max_llm_calls=10, max_depth=2) |

**반환값**: `EstimationResult`

**반환값 구조**:
```python
EstimationResult(
    question="질문",
    value=1000.0,                    # 추정값 (또는 None)
    unit="원",
    source="Generative Prior",       # v7.11.0: source (Literal, Prior, Fermi, Fusion, Failure)
    certainty="high",                # v7.11.0: certainty (high/medium/low)
    decomposition={...},             # Fermi 분해 (있는 경우)
    evidence={...},                  # Stage 1 증거
    cost={'llm_calls': 3, 'time': 2.5},  # 비용
    error=None,                      # 실패 시 에러 메시지
    # ... 기타 필드 ...
)
```

**v7.11.0 변경사항**:
| Field | v7.10.2 | v7.11.0 |
|-------|---------|---------|
| `phase` | 0-4 (또는 -1) | (Deprecated) |
| `source` | (없음) | "Literal", "Direct RAG", "Validator Search", "Generative Prior", "Fermi", "Fusion", "Failure" |
| `confidence` | 0.0-1.0 | (Deprecated) |
| `certainty` | (없음) | "high", "medium", "low" |
| `phase_path` | [0, 1, 2, 3] | (Deprecated) |
| `decomposition` | `fermi_model` | `decomposition` (간소화) |

**성능 특성**:
- **Stage 1 (Evidence)**: <1초 (Early Return 시 <0.1초)
- **Stage 2 (Prior)**: <3초 (LLM 1회 호출)
- **Stage 3 (Fermi)**: <5초 (재귀 없음, max_depth=2)
- **Stage 4 (Fusion)**: <1초 (가중 합성)

**사용 예시**:

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import create_standard_budget

estimator = EstimatorRAG()

# 예시 1: Stage 1 Literal (프로젝트 데이터)
result = estimator.estimate(
    question="churn_rate",
    project_data={'churn_rate': 0.05}
)
print(f"Source: {result.source}, Value: {result.value}")
# 출력: Source: Literal, Value: 0.05

# 예시 2: Stage 2 Prior (LLM 직접 값 요청)
result = estimator.estimate(
    question="B2B SaaS의 평균 ARPU는?",
    context=Context(domain='B2B_SaaS', region='한국')
)
if result.is_successful():
    print(f"Source: {result.source}, Value: {result.value} {result.unit}")
    print(f"Certainty: {result.certainty}")
else:
    print(f"실패: {result.error}")

# 예시 3: Budget 설정 (Fast Mode)
from umis_rag.agents.estimator.common import create_fast_budget

result = estimator.estimate(
    question="AI 챗봇 ARPU는?",
    context=Context(domain='AI_Chatbot'),
    budget=create_fast_budget()  # max_llm_calls=3
)
print(f"LLM Calls: {result.cost['llm_calls']}")  # <= 3
```

---

## Stage 컴포넌트

### Stage 1: Evidence Collection

**컴포넌트**:
1. **Literal**: 프로젝트 데이터 확인 (즉시 반환)
2. **Direct RAG**: 학습된 규칙 검색
3. **Validator Search**: 확정 데이터 검색
4. **Guardrail Engine**: 논리적/경험적 제약 수집

**Early Return**:
- Literal에서 확정값 발견 시 즉시 반환
- Direct RAG에서 높은 신뢰도 결과 시 즉시 반환

**사용 예시**:
```python
# 자동으로 Stage 1 실행됨
result = estimator.estimate(
    question="employees",
    project_data={'employees': 150}
)
# Source: Literal (즉시 반환)
```

### Stage 2: Generative Prior

**특징**:
- LLM에 직접 값 요청
- Certainty (high/medium/low) 반환
- Budget 기반 탐색 (max_llm_calls 제한)

**사용 예시**:
```python
result = estimator.estimate(
    question="2025년 AI 챗봇 ARPU는?",
    context=Context(domain='AI_Chatbot')
)
# Source: Generative Prior
# Certainty: high/medium/low
```

### Stage 3: Structural Explanation (Fermi)

**특징**:
- 구조적 분해 (2-4개 변수)
- **재귀 없음** (max_depth=2 강제)
- 변수 추정 시 `PriorEstimator` 사용

**사용 예시**:
```python
result = estimator.estimate(
    question="서울 음식점 수는?",
    context=Context(region='서울')
)
# Source: Fermi
# Decomposition: {'formula': 'A * B', 'variables': [...]}
```

### Stage 4: Fusion & Validation

**특징**:
- 모든 Stage 결과 가중 합성
- 증거 기반 신뢰도 조정

**사용 예시**:
```python
# 자동으로 Fusion 실행 (여러 Stage 결과 있을 때)
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(domain='B2B_SaaS')
)
# Source: Fusion (Prior + Fermi + Evidence 합성)
```

---

## EstimationResult

### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `question` | `str` | 질문 |
| `value` | `float` | 추정값 |
| `unit` | `str` | 단위 |
| `source` | `str` | 추정 소스 (Literal, Prior, Fermi, Fusion, Failure) |
| `certainty` | `str` | LLM 내부 확신도 (high/medium/low) |
| `decomposition` | `dict` | Fermi 분해 정보 |
| `evidence` | `dict` | Stage 1 증거 |
| `cost` | `dict` | 비용 (llm_calls, time) |
| `error` | `str` | 에러 메시지 |

### 메서드

```python
def is_successful() -> bool:
    """성공 여부 (source != "Failure")"""
    return self.source != "Failure"
```

---

## Budget

### Budget 클래스

```python
@dataclass
class Budget:
    """자원 제한"""
    max_llm_calls: int = 10        # LLM 최대 호출 횟수
    max_variables: int = 4         # Fermi 최대 변수 수
    max_runtime_seconds: int = 60  # 최대 실행 시간
    max_depth: int = 2             # Fermi 최대 깊이 (v7.11.0: 2 강제)
```

### Helper Functions

```python
from umis_rag.agents.estimator.common import (
    create_standard_budget,  # max_llm_calls=10
    create_fast_budget       # max_llm_calls=3
)

# Standard Budget
budget = create_standard_budget()

# Fast Budget
budget = create_fast_budget()

# Custom Budget
budget = Budget(
    max_llm_calls=5,
    max_variables=3,
    max_runtime_seconds=30,
    max_depth=2  # 고정
)
```

---

## Context

### Context 클래스

```python
@dataclass
class Context:
    """맥락 정보"""
    domain: str = ""          # 도메인 (예: "B2B_SaaS")
    region: str = ""          # 지역 (예: "서울", "한국")
    time_period: str = ""     # 시간 (예: "2025Q1")
    industry: str = ""        # 산업 (예: "Healthcare")
    business_model: str = ""  # 비즈니스 모델 (예: "Subscription")
```

---

## 사용 예시

### 기본 사용

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("B2B SaaS ARPU는?")

if result.is_successful():
    print(f"추정값: {result.value}")
    print(f"소스: {result.source}")
    print(f"확신도: {result.certainty}")
```

### Context 활용

```python
from umis_rag.agents.estimator.models import Context

result = estimator.estimate(
    question="2025년 AI 챗봇 서비스 ARPU는?",
    context=Context(
        domain="AI_Chatbot",
        region="한국",
        time_period="2025"
    )
)
```

### Budget 설정

```python
from umis_rag.agents.estimator.common import create_fast_budget

# Fast Mode (max_llm_calls=3)
result = estimator.estimate(
    question="서울 음식점 수는?",
    budget=create_fast_budget()
)

print(f"LLM 호출: {result.cost['llm_calls']}")  # <= 3
print(f"실행 시간: {result.cost['time']:.2f}초")
```

---

## 마이그레이션 가이드

### v7.10.2 → v7.11.0

#### 1. Import 변경

```python
# Before (v7.10.2)
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition

# After (v7.11.0)
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator import PriorEstimator  # Stage 2
from umis_rag.agents.estimator import FermiEstimator  # Stage 3
```

#### 2. 결과 확인 변경

```python
# Before (v7.10.2)
if result.phase >= 0:
    print(f"Phase {result.phase}: {result.value}")
    print(f"Confidence: {result.confidence:.0%}")

# After (v7.11.0)
if result.is_successful():
    print(f"Source: {result.source}, Value: {result.value}")
    print(f"Certainty: {result.certainty}")
```

#### 3. Config → Budget 변경

```python
# Before (v7.10.2)
from umis_rag.agents.estimator.models import Phase3Config
config = Phase3Config(max_llm_calls=10)
phase3 = Phase3Guestimation(config=config)

# After (v7.11.0)
from umis_rag.agents.estimator.common import create_standard_budget
budget = create_standard_budget()  # max_llm_calls=10
estimator = EstimatorRAG()
result = estimator.estimate(question, budget=budget)
```

#### 4. 하위 호환성 (Deprecated API)

```python
# v7.11.0에서도 작동 (compat.py를 통해)
from umis_rag.agents.estimator import Phase3Guestimation  # DeprecationWarning

phase3 = Phase3Guestimation()  # 내부적으로 PriorEstimator 사용
result = phase3.estimate(question, context)

# 경고 메시지:
# "Phase3Guestimation은 v7.11.0에서 Deprecated되었습니다.
#  PriorEstimator (Stage 2)를 사용하세요."
```

---

## 자주 묻는 질문 (FAQ)

### Q1: Phase 3, 4는 어디로 갔나요?
**A:** Stage 2 (Generative Prior)와 Stage 3 (Fermi)로 재설계되었습니다.
- Phase 3 Guestimation → Stage 2 Generative Prior
- Phase 4 Fermi Decomposition → Stage 3 Structural Explanation (재귀 제거)

### Q2: 재귀가 제거되었는데, 복잡한 문제는 어떻게 풀나요?
**A:** Stage 3 Fermi는 max_depth=2로 제한하고, 변수 추정 시 Stage 2 Prior를 사용합니다. 재귀 없이도 대부분의 문제를 해결할 수 있습니다.

### Q3: confidence가 certainty로 바뀐 이유는?
**A:** confidence는 외부 증거 기반 신뢰도를 의미했지만, certainty는 LLM의 내부 확신도를 나타냅니다. 더 정확한 의미 전달을 위해 변경했습니다.

### Q4: 하위 호환성은 어떻게 되나요?
**A:** `compat.py`를 통해 `Phase3Guestimation`, `Phase4FermiDecomposition`을 계속 사용할 수 있습니다 (DeprecationWarning 발생). 하지만 프로덕션에서는 새로운 API 사용을 권장합니다.

### Q5: Budget을 설정하지 않으면 어떻게 되나요?
**A:** 기본 Standard Budget (max_llm_calls=10, max_depth=2)이 사용됩니다.

---

**문서 버전**: v7.11.0  
**작성일**: 2025-11-26  
**관련 문서**: [User Guide](../guides/ESTIMATOR_USER_GUIDE_v7_11_0.md), [Migration Plan](../../dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md)

