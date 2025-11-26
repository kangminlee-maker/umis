# Estimator 사용자 가이드 (v7.11.0 Fusion Architecture)

**대상**: 비개발자 포함 모든 사용자  
**버전**: v7.11.0  
**최종 업데이트**: 2025-11-26  
**아키텍처**: 4-Stage Fusion Architecture

---

## 📋 목차

1. [Quick Start](#quick-start)
2. [핵심 개념](#핵심-개념)
3. [Stage별 가이드](#stage별-가이드)
4. [Budget 관리](#budget-관리)
5. [성능 최적화](#성능-최적화)
6. [트러블슈팅](#트러블슈팅)
7. [FAQ](#faq)

---

## Quick Start

### 1단계: 설치 (이미 완료됨)

```bash
# UMIS 설치 확인
python setup/setup.py --check
```

### 2단계: 간단한 추정

```python
from umis_rag.agents.estimator import EstimatorRAG

# Estimator 생성
estimator = EstimatorRAG()

# 질문하기
result = estimator.estimate("B2B SaaS의 평균 ARPU는?")

# 결과 확인
if result.is_successful():
    print(f"추정값: {result.value}")
    print(f"확신도: {result.certainty}")
    print(f"소스: {result.source}")
else:
    print(f"실패: {result.error}")
```

**출력 예시**:
```
추정값: 50000.0
확신도: high
소스: Generative Prior
```

---

## 핵심 개념

### 4-Stage Fusion Architecture (v7.11.0)

Estimator는 4단계로 값을 추정합니다:

| Stage | 이름 | 설명 | 속도 | 정확도 |
|-------|------|------|------|--------|
| **1** | Evidence Collection | 증거 수집 (Literal + RAG + Validator + Guardrails) | ⚡ <1s | ⭐⭐⭐⭐⭐ 90-100% |
| **2** | Generative Prior | LLM 직접 값 요청 | 🕐 ~3s | ⭐⭐⭐ 70-80% |
| **3** | Structural Explanation | 구조적 분해 (재귀 없음) | 🕐 ~5s | ⭐⭐⭐ 60-70% |
| **4** | Fusion & Validation | 모든 결과 가중 합성 | ⚡ <1s | ⭐⭐⭐⭐ 80-90% |

### v7.11.0 주요 변경사항

#### 🎯 Phase → Stage 전환
- **Phase 0-4** (5단계) → **Stage 1-4** (4단계)
- **재귀 제거**: 복잡했던 재귀 로직 제거, max_depth=2로 제한
- **Early Return**: Stage 1에서 확정값 발견 시 즉시 반환

#### 🔄 용어 변경
| 이전 (v7.10.2) | 새로운 (v7.11.0) | 의미 |
|----------------|------------------|------|
| `phase` (0-4) | `source` (Literal, Prior 등) | 추정 소스 |
| `confidence` (0.0-1.0) | `certainty` (high/medium/low) | LLM 내부 확신도 |
| Phase3Config | `Budget` | 자원 제한 |

#### 💡 왜 변경했나요?
- **Phase → Source**: "어떤 단계"가 아니라 "어떤 소스"에서 왔는지가 중요
- **Confidence → Certainty**: 외부 증거 기반 신뢰도 → LLM 내부 확신도
- **재귀 제거**: 속도 개선 (10-30초 → 3-5초), 예측 가능성 향상

---

### EstimationResult (결과 객체)

모든 추정은 `EstimationResult` 객체를 반환합니다.

**주요 필드**:
```python
result.value           # 추정값 (예: 50000.0)
result.unit            # 단위 (예: "원")
result.source          # 추정 소스 (예: "Generative Prior")
result.certainty       # 확신도 (예: "high")
result.cost            # 비용 {'llm_calls': 3, 'time': 2.5}
result.is_successful() # 성공 여부 (True/False)
```

**Source 종류**:
- `"Literal"`: 프로젝트 데이터에서 확정값 발견
- `"Direct RAG"`: 학습된 규칙에서 발견
- `"Validator Search"`: 확정 데이터에서 발견
- `"Generative Prior"`: LLM이 직접 추정
- `"Fermi"`: 구조적 분해로 추정
- `"Fusion"`: 여러 소스 결과 합성
- `"Failure"`: 모든 시도 실패

**Certainty 종류**:
- `"high"`: LLM이 매우 확신함 (예: 알려진 사실)
- `"medium"`: LLM이 보통 확신함 (예: 일반적인 추정)
- `"low"`: LLM이 확신 낮음 (예: 추측)

---

## Stage별 가이드

### Stage 1: Evidence Collection (증거 수집)

**구성 요소**:
1. **Literal**: 프로젝트 데이터 확인
2. **Direct RAG**: 학습된 규칙 검색
3. **Validator Search**: 확정 데이터 검색
4. **Guardrail Engine**: 논리적/경험적 제약 수집

**언제 사용**:
- 프로젝트에서 이미 알고 있는 값
- 이전에 학습한 규칙
- 확정된 데이터

**사용법**:
```python
# Literal: 프로젝트 데이터
result = estimator.estimate(
    question="churn_rate",  # 또는 "이탈률은?"
    project_data={'churn_rate': 0.05}
)
# Source: Literal, Value: 0.05 (즉시 반환)
```

**Early Return**:
- Literal에서 확정값 발견 → 즉시 반환 (0.01초)
- Direct RAG에서 높은 신뢰도 결과 → 즉시 반환 (0.5초)

**팁**:
- 질문에 project_data의 키 또는 키워드가 포함되어야 함
- 정확한 키를 사용하면 더 빠름 (예: "churn_rate")

---

### Stage 2: Generative Prior (생성적 사전)

**언제 사용**:
- Stage 1에서 확정값을 찾지 못함
- LLM이 직접 값을 추정할 수 있음
- 빠른 추정이 필요함 (3초)

**특징**:
- LLM에 직접 값 요청
- Certainty (high/medium/low) 반환
- Budget 기반 탐색 (max_llm_calls 제한)

**사용법**:
```python
result = estimator.estimate(
    question="2025년 AI 챗봇 서비스 평균 ARPU는?",
    context=Context(domain='AI_Chatbot')
)
# Source: Generative Prior
# Certainty: high/medium/low
```

**Context 활용**:
```python
from umis_rag.agents.estimator.models import Context

result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(
        domain="B2B_SaaS",
        region="한국",
        time_period="2025"
    )
)
```

**팁**:
- Context를 자세히 제공할수록 정확도 향상
- Certainty가 "high"이면 신뢰 가능

---

### Stage 3: Structural Explanation (구조적 설명)

**언제 사용**:
- Stage 2에서 Certainty가 낮음
- 구조적 분해가 필요함
- 복잡한 문제 (예: "서울 음식점 수는?")

**특징**:
- 2-4개 변수로 분해
- **재귀 없음** (max_depth=2 고정)
- 변수 추정 시 Stage 2 (Prior) 사용

**사용법**:
```python
result = estimator.estimate(
    question="서울 음식점 수는?",
    context=Context(region='서울')
)
# Source: Fermi
# Decomposition: {'formula': 'A * B', 'variables': [...]}
```

**분해 예시**:
```
질문: "서울 음식점 수는?"

분해:
- 서울 음식점 수 = 서울 인구 × 1인당 음식점 수
- 변수 A: 서울 인구 (1000만 명)
- 변수 B: 1인당 음식점 수 (0.01)
- 결과: 10만 개
```

**팁**:
- 복잡한 문제일수록 Fermi가 유용
- Decomposition을 확인하여 로직 이해 가능

---

### Stage 4: Fusion & Validation (융합 및 검증)

**언제 사용**:
- 여러 Stage에서 결과가 나옴
- 결과들을 종합하고 싶음

**특징**:
- 모든 Stage 결과 가중 합성
- 증거 기반 신뢰도 조정
- 최종 값 반환

**사용법**:
```python
# 자동으로 Fusion 실행됨
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(domain='B2B_SaaS')
)
# Source: Fusion (Prior + Fermi + Evidence 합성)
```

**가중치**:
- Literal/Direct RAG: 1.0 (100% 신뢰)
- Validator Search: 0.9 (90% 신뢰)
- Generative Prior (high): 0.8
- Generative Prior (medium): 0.6
- Generative Prior (low): 0.4
- Fermi: 0.5-0.7

---

## Budget 관리

### Budget이란?

Budget은 자원 제한을 설정합니다:

```python
from umis_rag.agents.estimator.common import Budget

budget = Budget(
    max_llm_calls=10,        # LLM 최대 호출 횟수
    max_variables=4,         # Fermi 최대 변수 수
    max_runtime_seconds=60,  # 최대 실행 시간
    max_depth=2              # Fermi 최대 깊이 (고정)
)
```

### Budget 종류

#### Standard Budget (기본)
```python
from umis_rag.agents.estimator.common import create_standard_budget

budget = create_standard_budget()
# max_llm_calls=10, max_variables=4, max_runtime=60s
```

#### Fast Budget (빠른 모드)
```python
from umis_rag.agents.estimator.common import create_fast_budget

budget = create_fast_budget()
# max_llm_calls=3, max_variables=2, max_runtime=30s
```

### 사용 예시

```python
# Standard Mode (기본)
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    budget=create_standard_budget()
)

# Fast Mode (빠른 추정)
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    budget=create_fast_budget()
)

print(f"LLM 호출: {result.cost['llm_calls']}")
print(f"실행 시간: {result.cost['time']:.2f}초")
```

---

## 성능 최적화

### 1. Context를 자세히 제공

```python
# ❌ 나쁜 예
result = estimator.estimate("ARPU는?")

# ✅ 좋은 예
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(
        domain="B2B_SaaS",
        region="한국",
        time_period="2025"
    )
)
```

### 2. 프로젝트 데이터 활용

```python
# ❌ 나쁜 예
result = estimator.estimate("이탈률은?")

# ✅ 좋은 예
result = estimator.estimate(
    question="churn_rate",
    project_data={'churn_rate': 0.05}
)
# Stage 1 Literal에서 즉시 반환 (0.01초)
```

### 3. Fast Budget 사용

```python
# 빠른 추정 필요 시
result = estimator.estimate(
    question="AI 챗봇 ARPU는?",
    budget=create_fast_budget()
)
# max_llm_calls=3, 실행 시간 < 5초
```

### 4. 결과 캐싱

```python
# 같은 질문 반복 시 캐싱
cache = {}

def estimate_with_cache(question, **kwargs):
    if question in cache:
        return cache[question]
    
    result = estimator.estimate(question, **kwargs)
    cache[question] = result
    return result
```

---

## 트러블슈팅

### 문제 1: 추정 실패 (source == "Failure")

**원인**:
- 모든 Stage에서 실패
- Context 부족
- Budget 소진

**해결**:
```python
# Context 추가
result = estimator.estimate(
    question="ARPU는?",
    context=Context(
        domain="B2B_SaaS",
        region="한국"
    )
)

# Budget 증가
budget = Budget(max_llm_calls=20)
result = estimator.estimate(question, budget=budget)
```

### 문제 2: 실행 시간이 너무 김

**원인**:
- Stage 3 (Fermi) 사용
- Budget이 너무 큼

**해결**:
```python
# Fast Budget 사용
result = estimator.estimate(
    question="...",
    budget=create_fast_budget()
)

# 또는 프로젝트 데이터 제공 (Stage 1 Early Return)
result = estimator.estimate(
    question="churn_rate",
    project_data={'churn_rate': 0.05}
)
```

### 문제 3: Certainty가 "low"

**원인**:
- LLM이 확신하지 못함
- Context 부족

**해결**:
```python
# Context 자세히 제공
result = estimator.estimate(
    question="2025년 AI 챗봇 ARPU는?",
    context=Context(
        domain="AI_Chatbot",
        region="한국",
        time_period="2025Q1",
        business_model="Subscription"
    )
)
```

---

## FAQ

### Q1: Phase는 어디로 갔나요?

**A:** v7.11.0에서 **Phase → Stage**로 전환했습니다.
- Phase 0-2 → Stage 1 (Evidence Collection)
- Phase 3 → Stage 2 (Generative Prior)
- Phase 4 → Stage 3 (Structural Explanation, 재귀 제거)
- (신규) → Stage 4 (Fusion & Validation)

### Q2: confidence는 어디로 갔나요?

**A:** `confidence` → `certainty`로 변경했습니다.
- **Before**: `confidence` (0.0-1.0, 외부 증거 기반 신뢰도)
- **After**: `certainty` (high/medium/low, LLM 내부 확신도)

더 직관적이고 정확한 의미 전달을 위해 변경했습니다.

### Q3: 재귀가 제거되었는데, 복잡한 문제는 어떻게 풀나요?

**A:** Stage 3 (Fermi)는 max_depth=2로 제한하고, 변수 추정 시 Stage 2 (Prior)를 사용합니다. 재귀 없이도 대부분의 문제를 해결할 수 있으며, 속도가 크게 향상되었습니다 (10-30초 → 3-5초).

### Q4: 이전 코드와 호환되나요?

**A:** 네, `compat.py`를 통해 하위 호환성을 제공합니다.

```python
# v7.10.2 코드 (여전히 작동)
from umis_rag.agents.estimator import Phase3Guestimation
phase3 = Phase3Guestimation()
result = phase3.estimate(question, context)

# 경고 메시지 발생:
# "Phase3Guestimation은 Deprecated되었습니다. PriorEstimator를 사용하세요."
```

하지만 프로덕션에서는 새로운 API 사용을 권장합니다.

### Q5: Budget을 설정하지 않으면 어떻게 되나요?

**A:** 기본 Standard Budget (max_llm_calls=10, max_depth=2)이 사용됩니다.

### Q6: Early Return은 무엇인가요?

**A:** Stage 1 (Evidence Collection)에서 확정값을 발견하면 즉시 반환하는 기능입니다.

```python
result = estimator.estimate(
    question="employees",
    project_data={'employees': 150}
)
# Stage 1 Literal에서 즉시 반환 (0.01초)
# Source: Literal
```

### Q7: Fusion은 언제 사용되나요?

**A:** 여러 Stage에서 결과가 나올 때 자동으로 사용됩니다.

```python
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(domain='B2B_SaaS')
)
# Stage 1: Validator Search → 50000 (0.9 가중치)
# Stage 2: Prior → 55000 (0.8 가중치)
# Stage 4: Fusion → 52000 (가중 평균)
```

### Q8: 어떤 Stage가 사용되었는지 확인할 수 있나요?

**A:** `result.source`를 확인하세요.

```python
result = estimator.estimate("B2B SaaS ARPU는?")
print(f"Source: {result.source}")
# 출력: Source: Generative Prior (또는 Literal, Fermi, Fusion 등)
```

---

## 다음 단계

### 고급 사용법
- [API 문서](../api/ESTIMATOR_API_v7_11_0.md)
- [마이그레이션 가이드](../../dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md)

### 학습 자료
- [Stage별 상세 설명](../../dev_docs/improvements/PHASE_0_4_REDESIGN_ANALYSIS_v7_10_0.md)
- [Budget 최적화](../../dev_docs/improvements/CONFIG_REFACTORING_DESIGN_v7_11_0.md)

---

**문서 버전**: v7.11.0  
**작성일**: 2025-11-26  
**관련 문서**: [API 문서](../api/ESTIMATOR_API_v7_11_0.md), [Migration Plan](../../dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md)

