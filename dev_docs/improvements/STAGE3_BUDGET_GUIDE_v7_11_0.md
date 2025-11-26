# Stage 3 (Fermi) Budget 설정 및 작동 기준 (v7.11.0)

**날짜:** 2025-11-26  
**버전:** v7.11.0 Fusion Architecture

---

## 📋 개요

Stage 3 (Fermi Estimator)는 **재귀 없이** 구조적 설명을 제공하는 단계입니다.
Budget 기반 탐색으로 리소스를 명시적으로 제한하며, 예산 초과 시 즉시 중단됩니다.

---

## 🎯 Budget 구조

### Budget 클래스

```python
@dataclass
class Budget:
    # 외부 설정 가능
    max_llm_calls: int = 10          # 최대 LLM 호출 횟수
    max_variables: int = 8            # 최대 변수 추정 개수
    max_runtime_seconds: float = 60.0  # 최대 실행 시간 (초)
    max_depth: int = 2                # 최대 분해 깊이 (재귀 금지)
    
    # 내부 상태 (읽기 전용)
    _consumed_llm_calls: int = 0      # 소비된 LLM 호출
    _consumed_variables: int = 0      # 소비된 변수 개수
    _start_time: Optional[float] = None  # 시작 시간
```

---

## 📊 Budget 프리셋

### 1. Fast Budget (빠른 추정)

```python
create_fast_budget()

Budget(
    max_llm_calls=3,           # LLM 호출 3회
    max_variables=3,           # 변수 3개
    max_runtime_seconds=10.0,  # 10초 제한
    max_depth=1                # 깊이 1 (거의 분해 안 함)
)
```

**용도:** 빠른 응답이 필요할 때 (3초 이내)  
**Stage 3 동작:** 
- 분해식 1회 생성 (LLM 1회)
- 변수 2개까지 추정 가능 (LLM 2회)
- **총 LLM 호출: 3회 이하**

---

### 2. Standard Budget (표준, 기본값)

```python
create_standard_budget()

Budget(
    max_llm_calls=10,          # LLM 호출 10회
    max_variables=8,           # 변수 8개
    max_runtime_seconds=60.0,  # 60초 제한
    max_depth=2                # 깊이 2 (v7.11.0 최대)
)
```

**용도:** 일반적인 추정 작업  
**Stage 3 동작:**
- 분해식 1회 생성 (LLM 1회)
- 변수 8개까지 추정 가능 (LLM 8회)
- **총 LLM 호출: 9회 이하**

---

### 3. Thorough Budget (정밀 추정)

```python
create_thorough_budget()

Budget(
    max_llm_calls=20,          # LLM 호출 20회
    max_variables=15,          # 변수 15개
    max_runtime_seconds=120.0, # 120초 제한
    max_depth=3                # 깊이 3 (특수 케이스)
)
```

**용도:** 복잡한 Fermi 분해가 필요할 때  
**Stage 3 동작:**
- 분해식 1회 생성 (LLM 1회)
- 변수 15개까지 추정 가능 (LLM 15회)
- **총 LLM 호출: 16회 이하**

---

## 🔧 Stage 3 작동 기준

### 1. 실행 조건 (Stage 3 시작)

```python
# estimator.py Line 249
if use_fermi and budget.can_call_llm(1) and not budget.is_exhausted():
    # Stage 3 실행
```

**조건:**
- ✅ `use_fermi=True` (Fermi 사용 설정)
- ✅ `budget.can_call_llm(1)` (LLM 호출 1회 이상 가능)
- ✅ `not budget.is_exhausted()` (예산 소진 아님)

**예시:**
```python
# Standard Budget (max_llm_calls=10)
# Stage 2에서 LLM 1회 사용 → 잔여 9회
if use_fermi and (9 >= 1) and not exhausted:  # True
    # Stage 3 실행!
```

---

### 2. 스킵 조건 (Stage 3 건너뜀)

```python
# estimator.py Line 268-271
else:
    if not use_fermi:
        logger.info("Fermi 사용 안 함 (use_fermi=False)")
    else:
        logger.warning("Fermi 스킵 (예산 부족 또는 소진)")
```

**스킵 이유:**
1. **`use_fermi=False`** - 사용자가 Fermi 사용 안 함 설정
2. **`budget.can_call_llm(1) = False`** - LLM 호출 예산 부족
3. **`budget.is_exhausted() = True`** - 예산 완전 소진

**예시:**
```python
# Fast Budget (max_llm_calls=3)
# Stage 2에서 LLM 3회 사용 → 잔여 0회
if use_fermi and (0 >= 1) and not exhausted:  # False
    # Stage 3 스킵!
```

---

### 3. 깊이 제한 (depth check)

```python
# fermi_estimator.py Line 149-151
if depth >= budget.max_depth:
    logger.warning(f"깊이 제한 초과 (depth={depth} >= max={budget.max_depth})")
    return None
```

**제한:**
- **v7.11.0: max_depth = 2 (재귀 금지)**
- depth=0: 최초 분해 (허용)
- depth=1: 2차 분해 (허용, 하지만 v7.11.0에서는 사용 안 함)
- depth=2: 3차 분해 (차단!)

---

### 4. 예산 소진 체크

```python
# fermi_estimator.py Line 156-162
if budget.is_exhausted():
    logger.warning("예산 소진")
    return None

if not budget.can_call_llm(1):
    logger.warning("LLM 호출 예산 부족")
    return None
```

**예산 소진 조건 (`is_exhausted()`):**
```python
def is_exhausted(self) -> bool:
    # 다음 중 하나라도 초과하면 True
    if not self.has_time():  # 시간 초과
        return True
    if self._consumed_llm_calls >= self.max_llm_calls:  # LLM 호출 초과
        return True
    if self._consumed_variables >= self.max_variables:  # 변수 개수 초과
        return True
    return False
```

---

## 🎬 Stage 3 실행 프로세스

### Step 1: 분해식 생성 (LLM 1회)

```python
# fermi_estimator.py Line 165-172
try:
    formula, variables = self._decompose(question, evidence, context)
    budget.consume_llm_call(1)  # LLM 호출 1회 소비
    
    logger.info(f"분해식: {formula}")
    logger.info(f"변수: {list(variables.keys())}")
except Exception as e:
    return None
```

**예시:**
```
질문: "E-commerce 구독 서비스 월 해지율은?"
분해식: 월_해지율 = (월_평균_이탈_고객수 ÷ 전체_유료_구독자수) × 100
변수: ['월_평균_이탈_고객수', '전체_유료_구독자수']
```

---

### Step 2: 변수 추정 (PriorEstimator, 재귀 금지!)

```python
# fermi_estimator.py Line 183-210
for var_name, var_description in variables.items():
    # 예산 체크
    if budget.is_exhausted():
        logger.warning(f"예산 소진 (변수 {var_name} 추정 중단)")
        break
    
    if not budget.can_call_llm(1) or not budget.can_estimate_variable(1):
        logger.warning(f"변수 {var_name} 추정 불가 (예산 부족)")
        break
    
    # PriorEstimator로 직접 추정 (재귀 금지!)
    var_result = self.prior_estimator.estimate(
        question=f"{var_name}은/는?",
        evidence=evidence,
        budget=budget,  # 동일 Budget 공유
        context=context
    )
    
    if var_result:
        variable_results[var_name] = var_result
        budget.consume_variable(1)  # 변수 1개 소비
        logger.info(f"✅ {var_name} = {var_result.value} (certainty={var_result.certainty})")
```

**예시 (Fast Budget, 변수 2개):**
```
Budget: max_llm_calls=3, max_variables=3
소비: LLM 1회 (분해식) → 잔여 2회

변수 1: 월_평균_이탈_고객수
  - PriorEstimator 호출 (LLM 1회) → 500
  - 소비: LLM 1회, 변수 1개 → 잔여 LLM 1회, 변수 2개

변수 2: 전체_유료_구독자수
  - 예산 체크: LLM 1회 가능? ✅ 변수 1개 가능? ✅
  - PriorEstimator 호출 (LLM 1회) → ?
  - ❌ LLM 호출 예산 부족 (3/3)
  - 중단!
```

---

### Step 3: 공식 계산

```python
# fermi_estimator.py Line 212-238
if not variable_results:
    return None

# 모든 변수가 추정되었는지 확인
if len(variable_results) < len(variables):
    logger.warning(f"일부 변수 미추정 ({len(variable_results)}/{len(variables)})")
    # 공식 계산 시도하지만 실패할 가능성 높음

# 공식 계산
try:
    final_value = self._evaluate_formula(formula, variable_results)
    return create_fermi_result(
        value=final_value,
        decomposition={'formula': formula, 'variables': variable_results},
        reasoning=f"Fermi 분해: {formula}"
    )
except Exception as e:
    logger.error(f"공식 계산 실패: {e}")
    return None
```

---

## ❌ Stage 3 실패 케이스

### Case 1: 예산 소진 (Budget Exhausted)

**로그:**
```
[Stage 3] Structural Explanation (Fermi)
[FermiEstimator] 추정 시작 (depth=0): E-commerce 구독 서비스 월 해지율은?
  분해식: 월_해지율 = (월_평균_이탈_고객수 ÷ 전체_유료_구독자수) × 100
  변수: ['월_평균_이탈_고객수', '전체_유료_구독자수']
  변수 추정: 월_평균_이탈_고객수 = ...
    ✅ 월_평균_이탈_고객수 = 500 (certainty=medium)
  ⚠️ 예산 소진 (변수 전체_유료_구독자수 추정 중단)
  ❌ 공식 계산 오류: name '전체_유료_구독자수' is not defined
  ❌ Fermi 실패 또는 스킵
```

**원인:** Fast Budget (max_llm_calls=3)에서 LLM 호출 3회 모두 소진
- 분해식 생성: 1회
- 변수 1 추정: 1회
- 변수 2 추정: 예산 부족 (3/3)

**결과:** Stage 3 실패 → Stage 4 Fusion에서 Prior만 사용

---

### Case 2: 깊이 제한 초과

**로그:**
```
[FermiEstimator] 추정 시작 (depth=2)
  ⚠️ 깊이 제한 초과 (depth=2 >= max=2)
  return None
```

**원인:** v7.11.0에서 max_depth=2로 재귀 금지

**결과:** Stage 3 실패 → Stage 4 Fusion에서 Prior만 사용

---

### Case 3: 공식 계산 실패

**로그:**
```
[FermiEstimator] 추정 시작 (depth=0)
  분해식: LTV = ARPU / Churn
  변수: ['ARPU', 'Churn']
  ✅ ARPU = 100
  ✅ Churn = 0.05
  ❌ 공식 계산 오류: division by zero
  ❌ Fermi 실패
```

**원인:** 변수는 추정했지만 공식 계산 중 오류

**결과:** Stage 3 실패 → Stage 4 Fusion에서 Prior만 사용

---

## 🎯 Budget 소비 패턴

### Fast Budget (max_llm_calls=3)

| 단계 | 작업 | LLM 호출 | 변수 | 잔여 LLM | 상태 |
|------|------|---------|------|---------|------|
| Stage 2 | Prior 추정 | 1 | 0 | 2 | ✅ |
| Stage 3 | 분해식 생성 | 1 | 0 | 1 | ✅ |
| Stage 3 | 변수 1 추정 | 1 | 1 | 0 | ✅ |
| Stage 3 | 변수 2 추정 | - | - | 0 | ❌ 예산 부족 |

**결과:** Stage 3 실패 (변수 미추정)

---

### Standard Budget (max_llm_calls=10)

| 단계 | 작업 | LLM 호출 | 변수 | 잔여 LLM | 상태 |
|------|------|---------|------|---------|------|
| Stage 2 | Prior 추정 | 1 | 0 | 9 | ✅ |
| Stage 3 | 분해식 생성 | 1 | 0 | 8 | ✅ |
| Stage 3 | 변수 1 추정 | 1 | 1 | 7 | ✅ |
| Stage 3 | 변수 2 추정 | 1 | 2 | 6 | ✅ |
| Stage 3 | 변수 3 추정 | 1 | 3 | 5 | ✅ |
| Stage 3 | 공식 계산 | 0 | 0 | 5 | ✅ |

**결과:** Stage 3 성공 (Fermi 분해 완료)

---

## 📊 실제 E2E 테스트 결과

### Scenario 1: B2B SaaS ARPU (Fast Budget)

```
Budget: max_llm_calls=3, max_variables=3
Stage 2: LLM 1회 → 결과: $5,000
Stage 3: 스킵 (Prior만으로 충분)
Stage 4: Fusion(Prior) → 최종: $5,000

비용: LLM 1회, 3.9초, $0
```

**Stage 3 스킵 이유:** Prior가 직접 답변 가능, Fermi 불필요

---

### Scenario 2: E-commerce Churn (Fast Budget)

```
Budget: max_llm_calls=3, max_variables=3
Stage 2: LLM 1회 → 결과: 5%
Stage 3: 시도 → 실패 (Budget 소진)
  - 분해식 생성: LLM 1회
  - 변수 1 추정: LLM 1회 (500)
  - 변수 2 추정: ❌ LLM 호출 예산 부족 (3/3)
  - 공식 계산 실패
Stage 4: Fusion(Prior) → 최종: 5%

비용: LLM 3회, 5.4초, $0
```

**Stage 3 실패 이유:** Fast Budget (max_llm_calls=3)으로 변수 2개 추정 불가

---

## 🎯 결론 및 권장사항

### Budget 선택 가이드

| 상황 | 권장 Budget | max_llm_calls | Stage 3 동작 |
|------|-------------|--------------|--------------|
| **빠른 응답** | Fast | 3 | 스킵 또는 단순 분해 |
| **일반 추정** | Standard | 10 | 2-3개 변수 분해 가능 |
| **복잡한 Fermi** | Thorough | 20 | 4-5개 변수 분해 가능 |

### Stage 3 성공 조건

✅ **Stage 3가 성공하려면:**
1. `use_fermi=True` 설정
2. Budget에 충분한 LLM 호출 잔여 (최소 변수 개수 + 1)
3. Budget에 충분한 변수 개수 한도
4. 시간 제한 내 완료

✅ **최소 Budget:**
- 변수 2개 분해: `max_llm_calls >= 3` (분해 1 + 변수 2)
- 변수 3개 분해: `max_llm_calls >= 4` (분해 1 + 변수 3)

---

**Stage 3 (Fermi) Budget 설정 완전 가이드!** 📊
