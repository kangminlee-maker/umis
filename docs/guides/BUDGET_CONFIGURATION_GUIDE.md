# Budget 모드 설정 가이드 (v7.11.0)

**날짜:** 2025-11-26  
**버전:** v7.11.0 Fusion Architecture

---

## 📋 Budget 설정 방법 (3가지)

Budget 설정은 **코드에서 직접** 수행합니다. 환경변수나 설정 파일이 아닙니다!

---

## 🎯 방법 1: 프리셋 함수 사용 (권장!)

### 가장 간단한 방법

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_fast_budget, create_standard_budget, create_thorough_budget

estimator = EstimatorRAG()

# Fast Budget (빠른 추정, 3초 이내)
budget = create_fast_budget()
result = estimator.estimate("B2B SaaS ARPU는?", budget=budget)

# Standard Budget (일반 추정, 기본값)
budget = create_standard_budget()
result = estimator.estimate("E-commerce Churn Rate는?", budget=budget)

# Thorough Budget (정밀 추정, 최대 2분)
budget = create_thorough_budget()
result = estimator.estimate("음악 스트리밍 시장 규모는?", budget=budget)
```

### 프리셋 스펙

| 프리셋 | max_llm_calls | max_variables | max_runtime | max_depth | 속도 | 용도 |
|--------|--------------|--------------|-------------|-----------|------|------|
| **Fast** | 3 | 3 | 10초 | 1 | ~3초 | 빠른 응답 |
| **Standard** | 10 | 8 | 60초 | 2 | ~10초 | 일반 추정 |
| **Thorough** | 20 | 15 | 120초 | 3 | ~30초 | 정밀 분해 |

---

## 🎯 방법 2: 헬퍼 메서드 사용

### EstimatorRAG의 편의 메서드

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Fast Budget 자동 사용 (Fermi 비활성화)
result = estimator.estimate_fast("B2B SaaS ARPU는?")

# Thorough Budget 자동 사용 (Fermi 활성화)
result = estimator.estimate_thorough("음악 스트리밍 시장 규모는?")
```

**내부 구현:**
```python
def estimate_fast(self, question: str, context=None):
    budget = create_fast_budget()
    return self.estimate(question, context=context, budget=budget, use_fermi=False)

def estimate_thorough(self, question: str, context=None):
    budget = create_thorough_budget()
    return self.estimate(question, context=context, budget=budget, use_fermi=True)
```

---

## 🎯 방법 3: 커스텀 Budget 생성

### 직접 Budget 객체 생성

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import Budget

estimator = EstimatorRAG()

# 커스텀 Budget 생성
budget = Budget(
    max_llm_calls=5,           # LLM 호출 5회
    max_variables=4,           # 변수 4개
    max_runtime_seconds=30.0,  # 30초 제한
    max_depth=2                # 깊이 2
)

result = estimator.estimate("AI 챗봇 LTV는?", budget=budget)
```

**파라미터:**
- `max_llm_calls`: 최대 LLM 호출 횟수 (1-100, 기본 10)
- `max_variables`: 최대 변수 추정 개수 (1-50, 기본 8)
- `max_runtime_seconds`: 최대 실행 시간 초 (1-600, 기본 60)
- `max_depth`: 최대 분해 깊이 (1-3, 기본 2, **v7.11.0: 2 권장**)

---

## 🎯 방법 4: Budget 없이 사용 (기본값)

### Budget을 지정하지 않으면 Standard Budget 자동 적용

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Budget 지정 안 함 → Standard Budget 자동
result = estimator.estimate("B2B SaaS ARPU는?")

# 내부적으로:
# budget = create_standard_budget()  # 자동 생성
```

---

## 📊 Budget 설정 결정 가이드

### 언제 어떤 Budget을 사용할까?

#### Fast Budget (빠른 응답 우선)

**사용 시나리오:**
- ✅ 빠른 응답이 필요한 대화형 UI
- ✅ 실시간 추정 요구
- ✅ Prior로 충분한 단순 질문
- ✅ Fermi 분해 불필요

**Stage 3 동작:**
- 거의 스킵 (LLM 3회로 부족)
- 또는 매우 단순한 분해 (변수 1-2개)

**예시:**
```python
# "B2B SaaS ARPU는?" - Prior로 충분
budget = create_fast_budget()
result = estimator.estimate("B2B SaaS ARPU는?", budget=budget)
# 결과: Stage 2 Prior만 사용, 3초 완료
```

---

#### Standard Budget (일반 추정, 권장!)

**사용 시나리오:**
- ✅ 일반적인 추정 작업
- ✅ Fermi 분해가 필요한 경우
- ✅ 2-3개 변수 분해
- ✅ 균형잡힌 속도/품질

**Stage 3 동작:**
- 2-3개 변수 분해 가능
- LLM 호출 3-5회 (분해 1 + 변수 2-4)

**예시:**
```python
# "음악 스트리밍 시장 규모는?" - Fermi 분해 유용
budget = create_standard_budget()
result = estimator.estimate("음악 스트리밍 시장 규모는?", budget=budget)
# 결과: Stage 3 Fermi 분해 (변수 2-3개), 10초 완료
```

---

#### Thorough Budget (정밀 추정)

**사용 시나리오:**
- ✅ 복잡한 Fermi 분해 필요
- ✅ 4-5개 변수 분해
- ✅ 품질 최우선
- ✅ 시간 여유 있음

**Stage 3 동작:**
- 4-5개 변수 복잡한 분해
- LLM 호출 5-10회

**예시:**
```python
# "AI 챗봇 서비스 기업 가치는?" - 복잡한 분해
budget = create_thorough_budget()
result = estimator.estimate("AI 챗봇 서비스 기업 가치는?", budget=budget)
# 결과: Stage 3 Fermi 분해 (변수 4-5개), 30초 완료
```

---

## 📝 실제 사용 예시

### 예시 1: 대화형 Cursor Composer

**상황:** 사용자가 Cursor Composer에서 빠른 응답 원함

```python
# Native (Cursor) LLM 모드
# .env: LLM_MODE=cursor

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_fast_budget

estimator = EstimatorRAG()
budget = create_fast_budget()  # 빠른 응답!

result = estimator.estimate(
    question="@Fermi, B2B SaaS ARPU는?",
    budget=budget
)

# 결과: 3초 이내, Stage 2 Prior만 사용, 외부 API 호출 없음
```

---

### 예시 2: 배치 처리 스크립트

**상황:** 10개 질문을 자동으로 처리, 품질 우선

```python
# External LLM 모드
# .env: LLM_MODE=gpt-4o-mini

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_standard_budget

estimator = EstimatorRAG()
questions = ["질문1", "질문2", ..., "질문10"]

for q in questions:
    budget = create_standard_budget()  # 매번 새로운 Budget!
    result = estimator.estimate(q, budget=budget)
    # 각 질문마다 독립적인 예산
```

---

### 예시 3: 복잡한 Fermi 분해

**상황:** 시장 규모 추정, Fermi 분해 필수

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_thorough_budget
from umis_rag.agents.estimator.models import Context

estimator = EstimatorRAG()
budget = create_thorough_budget()  # 정밀 추정!

result = estimator.estimate(
    question="2025년 글로벌 음악 스트리밍 시장 규모는?",
    context=Context(
        domain="Music_Streaming",
        time_period="2025",
        region="글로벌"
    ),
    budget=budget,
    use_fermi=True  # Fermi 명시적 활성화
)

# 결과: Stage 3 Fermi 분해 (변수 4-5개), 30초 완료
```

---

## ❌ 잘못된 설정 예시

### ❌ 환경변수로 설정 (불가능!)

```bash
# .env
BUDGET_MODE=fast  # ← 이런 설정 없음!
MAX_LLM_CALLS=3   # ← 이런 설정 없음!
```

**이유:** Budget은 요청별로 다를 수 있으므로 코드에서 명시적으로 지정

---

### ❌ Config 파일로 설정 (불가능!)

```yaml
# config/budget_config.yaml (존재하지 않음!)
default_budget: fast
```

**이유:** Budget은 런타임에 동적으로 생성되어야 함

---

## 📊 Stage 3와 Budget 관계

### Budget이 Stage 3에 미치는 영향

| Budget | max_llm_calls | Stage 3 동작 | 변수 추정 가능 | 실제 Stage 3 LLM |
|--------|--------------|--------------|---------------|-----------------|
| **Fast** | 3 | 거의 스킵 | 0-2개 | 1-2회 |
| **Standard** | 10 | 2-3개 변수 분해 | 2-4개 | 3-5회 |
| **Thorough** | 20 | 4-5개 변수 분해 | 4-10개 | 5-10회 |

**Stage 3 LLM 호출 계산:**
```
Stage 3 LLM 호출 = 1 (분해식) + N (변수 개수)

예시:
- 변수 2개 분해 → 1 + 2 = 3회 LLM 호출
- 변수 4개 분해 → 1 + 4 = 5회 LLM 호출
```

**Stage 2가 먼저 LLM을 소비:**
```
전체 Budget: max_llm_calls=10
Stage 2 (Prior): 1회 소비 → 잔여 9회
Stage 3 (Fermi): 최대 9회 사용 가능
  - 분해식: 1회
  - 변수: 8개까지 가능
```

---

## 🚀 실전 가이드

### 1. 빠른 추정이 필요하면

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_fast_budget

estimator = EstimatorRAG()
result = estimator.estimate("질문", budget=create_fast_budget())
```

또는

```python
result = estimator.estimate_fast("질문")  # 더 간단!
```

---

### 2. 일반적인 추정이면 (기본값, 권장!)

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("질문")  # Budget 생략 → Standard 자동
```

또는

```python
from umis_rag.agents.estimator.common import create_standard_budget
result = estimator.estimate("질문", budget=create_standard_budget())  # 명시적
```

---

### 3. 복잡한 Fermi 분해가 필요하면

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_thorough_budget

estimator = EstimatorRAG()
result = estimator.estimate("질문", budget=create_thorough_budget())
```

또는

```python
result = estimator.estimate_thorough("질문")  # 더 간단!
```

---

### 4. 커스텀 Budget이 필요하면

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import Budget

estimator = EstimatorRAG()

# 특수 케이스: LLM 5회, 변수 4개, 30초 제한
budget = Budget(
    max_llm_calls=5,
    max_variables=4,
    max_runtime_seconds=30.0,
    max_depth=2
)

result = estimator.estimate("질문", budget=budget)
```

---

## 📊 Budget 선택 플로우차트

```
질문 받음
    ↓
빠른 응답 필요? (3초 이내)
    ├─ Yes → create_fast_budget()
    │         또는 estimator.estimate_fast()
    │
    └─ No → Fermi 분해 필요?
            ├─ No → create_fast_budget() + use_fermi=False
            │
            └─ Yes → 변수 몇 개?
                    ├─ 2-3개 → create_standard_budget() (권장!)
                    │           또는 estimator.estimate()
                    │
                    └─ 4개 이상 → create_thorough_budget()
                                  또는 estimator.estimate_thorough()
```

---

## 🔧 코드 위치

### Budget 관련 코드

| 파일 | 내용 | 위치 |
|------|------|------|
| `common/budget.py` | Budget 클래스 및 프리셋 함수 | `umis_rag/agents/estimator/common/` |
| `estimator.py` | estimate(), estimate_fast(), estimate_thorough() | `umis_rag/agents/estimator/` |
| `__init__.py` | Export (create_*_budget) | `umis_rag/agents/estimator/` |

### Import 방법

```python
# 방법 1: 개별 Import (권장)
from umis_rag.agents.estimator.common import (
    create_fast_budget,
    create_standard_budget,
    create_thorough_budget,
    Budget
)

# 방법 2: 전체 Import
from umis_rag.agents.estimator import (
    EstimatorRAG,
    create_fast_budget,
    create_standard_budget,
    create_thorough_budget,
    Budget
)
```

---

## 📝 실제 E2E 테스트 예시

### E2E 테스트에서의 사용

```python
# tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.common import create_fast_budget, create_standard_budget

@pytest.fixture
def estimator():
    return EstimatorRAG()

def test_scenario_6_fast_budget_estimation(estimator):
    """Fast Budget 테스트"""
    budget = create_fast_budget()  # ← 여기서 설정!
    
    result = estimator.estimate(
        question="모바일 앱 평균 ARPU는?",
        budget=budget  # ← Budget 전달
    )
    
    assert result.cost['llm_calls'] <= 3  # Fast Budget 검증

def test_scenario_7_standard_budget_estimation(estimator):
    """Standard Budget 테스트"""
    budget = create_standard_budget()  # ← 여기서 설정!
    
    result = estimator.estimate(
        question="B2B SaaS 평균 월 매출 성장률은?",
        budget=budget  # ← Budget 전달
    )
    
    assert result.cost['llm_calls'] <= 10  # Standard Budget 검증
```

---

## 🎯 요약

### Budget 설정 위치

| 방법 | 코드 | 설정 위치 |
|------|------|----------|
| **프리셋** | `create_fast_budget()` | Python 코드 |
| **헬퍼 메서드** | `estimator.estimate_fast()` | Python 코드 |
| **커스텀** | `Budget(max_llm_calls=5, ...)` | Python 코드 |
| **기본값** | `estimator.estimate(...)` | 자동 (Standard) |

### ❌ Budget을 설정할 수 없는 곳

- ❌ 환경변수 (`.env`)
- ❌ Config 파일 (`config/*.yaml`)
- ❌ 전역 설정

**이유:** Budget은 요청별로 다르므로 코드에서 명시적으로 지정해야 함

---

## 💡 Best Practices

### 1. 대부분의 경우 Standard Budget 사용 (기본값)

```python
estimator = EstimatorRAG()
result = estimator.estimate("질문")  # Budget 생략 → Standard
```

### 2. 빠른 응답이 필요하면 estimate_fast()

```python
result = estimator.estimate_fast("질문")  # 가장 간단!
```

### 3. 복잡한 Fermi가 필요하면 estimate_thorough()

```python
result = estimator.estimate_thorough("질문")  # Fermi 최대 활용
```

### 4. 특수한 경우에만 커스텀 Budget

```python
budget = Budget(max_llm_calls=7, max_variables=5)
result = estimator.estimate("질문", budget=budget)
```

---

**Budget 설정은 Python 코드에서!** 🎯
