# "추정 금지" 정책 명확화

**작성일**: 2025-11-07  
**목적**: Single Source of Truth 원칙의 정확한 의미  
**핵심**: "데이터/값 추정 금지"

---

## 🎯 정책의 정확한 의미

### "추정 금지" = **데이터/값 추정 금지**

```yaml
금지되는 것:
  ✅ 값/데이터를 직접 추정하는 행위
  ✅ 근사값을 자체적으로 생성하는 행위
  ✅ "대충 이 정도일 것 같아" 판단

허용되는 것:
  ✅ 확정 데이터 사용
  ✅ 계산 (공식 적용)
  ✅ 검증 (기준과 비교)
  ✅ Estimator 호출 (위임)
```

---

## 📋 Agent별 상세 정책

### Quantifier (Bill)

#### ✅ 허용 (계산)

```python
# 1. 확정 데이터로 계산
def calculate_sam(data):
    users = data['users']  # 100만 (확정 데이터)
    arpu = data['arpu']    # 5만원 (확정 데이터)
    
    sam = users * arpu * 12  # 계산
    return sam  # ✅ OK (계산)

# 2. 공식 적용
def calculate_growth_rate(data):
    current = data['current_value']  # 100억 (확정)
    previous = data['previous_value']  # 80억 (확정)
    
    growth = (current - previous) / previous  # 공식
    return growth  # ✅ OK (계산)

# 3. 벤치마크 검색
def search_benchmark(market):
    results = self.benchmark_store.search(market)
    return results  # ✅ OK (검색)
```

#### ❌ 금지 (추정)

```python
# 1. 값을 임의로 정하기
def calculate_sam(data):
    users = data.get('users', 100_0000)  # ❌ 금지!
    # "없으면 100만으로 가정" → 추정!
    
    arpu = 50_000  # ❌ 금지!
    # "대충 5만원" → 추정!
    
    sam = users * arpu * 12
    return sam

# 2. 근사값 생성
def estimate_churn_rate():
    # "보통 5-7% 정도니까 6%로 하자"
    return 0.06  # ❌ 금지! (추정)

# 3. 간접 추정
def calculate_with_assumption():
    # "업계 평균이 이 정도니까..."
    industry_avg = 1_000_000  # ❌ 금지!
    # Estimator에게 물어봐야 함!
```

#### ✅ 올바른 방법 (위임)

```python
def calculate_sam(data):
    # 1. 확정 데이터 사용
    users = data.get('users')
    
    # 2. 없으면 Estimator 호출 (위임!)
    if users is None:
        estimator = get_estimator_rag()
        result = estimator.estimate(
            "우리 서비스 사용자 수는?",
            domain=data.get('domain')
        )
        users = result.value  # ✅ OK (Estimator가 추정)
    
    # 3. ARPU도 동일
    arpu = data.get('arpu')
    if arpu is None:
        result = estimator.estimate("ARPU는?", domain=...)
        arpu = result.value  # ✅ OK
    
    # 4. 계산
    sam = users * arpu * 12  # ✅ OK (계산)
    return sam
```

---

### Validator (Rachel)

#### ✅ 허용 (검증)

```python
# 1. 정의 검증
def verify_definition(term):
    cases = self.definition_store.search(term)
    return cases  # ✅ OK (검색)

# 2. 소스 신뢰도 평가
def evaluate_source(source_name):
    source = self.source_store.search(source_name)
    reliability = source.metadata['reliability']
    return reliability  # ✅ OK (평가)

# 3. 값 검증 (기준과 비교)
def validate_number(claimed_value, data_point):
    # 외부 기준 데이터와 비교
    reference = self._get_reference_value(data_point)
    
    if reference:
        diff = abs(claimed_value - reference) / reference
        return {'valid': diff < 0.3}  # ✅ OK (비교)
    
    return {'valid': 'unknown'}
```

#### ❌ 금지 (추정)

```python
# 1. 값 추정
def validate_mau(claimed_mau):
    # "보통 이 정도 서비스면 50만은 될 것 같은데..."
    expected = 500_000  # ❌ 금지! (추정)
    
    diff = abs(claimed_mau - expected)
    return {'valid': diff < 100_000}

# 2. 근사값 생성
def estimate_reasonable_range(data_point):
    # "업계 평균이 100만~200만 사이니까..."
    return (1_000_000, 2_000_000)  # ❌ 금지! (추정)

# 3. 암묵적 추정
def check_if_reasonable(value):
    # "경험상 이 정도면 합리적"
    if value < 1_000_000:  # ❌ 기준을 어떻게 정했나? 추정!
        return False
```

#### ✅ 올바른 방법 (위임)

```python
def validate_with_estimation(claimed_value, question):
    """
    추정을 활용한 검증
    
    올바른 방법: Estimator에게 위임
    """
    # 1. Estimator에게 교차 검증 요청
    estimator = get_estimator_rag()
    est_result = estimator.estimate(question)
    
    if not est_result:
        return {'validation': 'unable'}
    
    # 2. 비교 (검증만 수행)
    diff_pct = abs(claimed_value - est_result.value) / est_result.value
    
    # 3. 검증 결과
    return {
        'claimed': claimed_value,
        'estimated': est_result.value,  # Estimator가 추정
        'estimator_confidence': est_result.confidence,
        'difference': diff_pct,
        'validation': 'pass' if diff_pct < 0.3 else 'fail',
        
        # 근거 포함
        'estimation_reasoning': est_result.reasoning_detail
    }
    # ✅ OK (Estimator가 추정, Validator는 비교만)
```

---

### Observer, Explorer (기타 Agent)

#### ❌ 금지

```python
# Observer
def analyze_market_structure():
    # "이 시장은 대충 5,000억 규모일 것 같아"
    market_size = 500_000_000_000  # ❌ 금지!

# Explorer
def generate_hypothesis():
    # "TAM은 1조 정도로 보면..."
    tam = 1_000_000_000_000  # ❌ 금지!
```

#### ✅ 올바른 방법

```python
# Observer
def analyze_market_structure():
    # "시장 규모 추정 필요" → Estimator 호출
    estimator = get_estimator_rag()
    size = estimator.estimate("이 시장 규모는?")
    
    return {
        'structure': '...',
        'estimated_size': size.value,  # ✅ OK
        'size_source': 'Estimator',
        'size_confidence': size.confidence
    }

# Explorer
def generate_hypothesis():
    # "TAM 필요" → Estimator 호출
    estimator = get_estimator_rag()
    tam = estimator.estimate("TAM은?")
    
    return {
        'hypothesis': '...',
        'tam_estimate': tam.value,  # ✅ OK
        'tam_reasoning': tam.reasoning_detail
    }
```

---

## 🚫 구체적 금지 패턴

### Pattern 1: 기본값 (Default Value)

```python
# ❌ 금지
value = data.get('churn_rate', 0.06)  # 기본값 6%
# "없으면 6%로 가정" → 추정!

# ✅ 올바름
value = data.get('churn_rate')
if value is None:
    estimator = get_estimator_rag()
    result = estimator.estimate("Churn Rate는?")
    value = result.value
```

### Pattern 2: 업계 평균 (Industry Average)

```python
# ❌ 금지
def get_arpu():
    # "SaaS 업계 평균 5만원"
    return 50_000  # 이 값을 어떻게 알았나? 추정!

# ✅ 올바름
def get_arpu():
    estimator = get_estimator_rag()
    result = estimator.estimate(
        "B2B SaaS ARPU는?",
        domain="B2B_SaaS"
    )
    return result.value  # Estimator가 증거 기반 추정
```

### Pattern 3: 경험적 판단 (Rule of Thumb)

```python
# ❌ 금지
def estimate_conversion():
    # "보통 3% 정도"
    return 0.03  # 경험? 추정!

# ✅ 올바름
def get_conversion():
    estimator = get_estimator_rag()
    result = estimator.estimate("전환율은?")
    # Estimator가 statistical_pattern, rag_benchmark 등으로 판단
    return result.value
```

### Pattern 4: 범위 추정 (Range Guessing)

```python
# ❌ 금지
def get_reasonable_range():
    # "100만~200만 사이일 것"
    return (1_000_000, 2_000_000)  # 추정!

# ✅ 올바름
def get_reasonable_range():
    estimator = get_estimator_rag()
    result = estimator.estimate("사용자 수는?")
    return result.value_range  # Estimator가 증거 기반 판단
```

---

## ✅ 허용되는 것

### 1. 확정 데이터 사용

```python
# ✅ OK
users = 100_000  # 공식 발표, HR 시스템 등
price = 50_000   # 실제 가격

sam = users * price * 12  # 계산
```

### 2. 공식/알고리즘 적용

```python
# ✅ OK
def calculate_cagr(start, end, years):
    cagr = (end / start) ** (1 / years) - 1
    return cagr  # 공식 적용 (추정 아님)
```

### 3. 논리적 추론 (단, 값 아닌 것)

```python
# ✅ OK (정성적 판단)
def analyze_market_maturity(growth_rate):
    if growth_rate > 0.50:
        return "초기 시장"
    elif growth_rate > 0.20:
        return "성장 시장"
    else:
        return "성숙 시장"
    # 정성적 분류 (값 추정 아님)

# ❌ 금지 (정량적 추정)
def estimate_market_size(maturity):
    if maturity == "초기":
        return 100_000_000_000  # ❌ 값 추정!
```

### 4. 검색 및 참조

```python
# ✅ OK
def get_benchmark(market):
    results = self.benchmark_store.search(market)
    
    if results:
        return results[0].metadata['value']  # 찾은 값 (추정 아님)
    
    # 없으면?
    estimator = get_estimator_rag()
    result = estimator.estimate(f"{market} 규모는?")
    return result.value  # ✅ OK (Estimator가 추정)
```

---

## 🔍 경계 케이스 (Gray Area)

### Case 1: 비율 계산

```python
# 상황: 전체는 알고 부분은 모를 때

# ❌ 잘못된 방법
def calculate_segment_size(total_market, segment_ratio=0.30):
    # segment_ratio를 어떻게 정했나? 추정!
    return total_market * segment_ratio

# ✅ 올바른 방법
def calculate_segment_size(total_market, segment_name):
    # 비율을 Estimator에게 물어봄
    estimator = get_estimator_rag()
    ratio_result = estimator.estimate(
        f"{segment_name}의 시장 점유율은?",
        context={'total_market': total_market}
    )
    
    segment_size = total_market * ratio_result.value
    
    return {
        'segment_size': segment_size,
        'ratio_used': ratio_result.value,
        'ratio_confidence': ratio_result.confidence,
        'ratio_reasoning': ratio_result.reasoning_detail
    }
```

### Case 2: 조정 계수 (Adjustment Factor)

```python
# 상황: 벤치마크를 우리 상황에 맞게 조정

# ❌ 잘못된 방법
def adjust_benchmark(benchmark_value):
    adjustment = 0.8  # "우리는 작으니까 80%만"
    # 0.8을 어떻게 정했나? 추정!
    return benchmark_value * adjustment

# ✅ 올바른 방법 A (논리적 근거)
def adjust_benchmark(benchmark_value, our_users, benchmark_users):
    # 사용자 수 비율로 조정 (논리적)
    adjustment = our_users / benchmark_users
    return benchmark_value * adjustment
    # ✅ OK (논리적 계산, 추정 아님)

# ✅ 올바른 방법 B (Estimator 호출)
def adjust_benchmark(benchmark_value, context):
    # "우리 상황의 조정 계수는?"
    estimator = get_estimator_rag()
    result = estimator.estimate(
        "벤치마크 조정 계수는?",
        context=context
    )
    return benchmark_value * result.value
    # ✅ OK (Estimator가 추정)
```

### Case 3: 보수적 할인 (Conservative Discount)

```python
# 상황: 보수적 추정 필요

# ❌ 잘못된 방법
def conservative_estimate(optimistic_value):
    discount = 0.7  # "보수적으로 30% 할인"
    # 30%는 어디서? 추정!
    return optimistic_value * discount

# ✅ 올바른 방법 A (Estimator 전략 사용)
def conservative_estimate(question):
    estimator = get_estimator_rag()
    
    # Context에 intent 명시
    from umis_rag.agents.estimator.models import Context, Intent
    context = Context(intent=Intent.MAKE_DECISION)
    
    result = estimator.estimate(question, context)
    # Estimator가 알아서 conservative 전략 선택
    return result.value
    # ✅ OK (Estimator의 판단)

# ✅ 올바른 방법 B (명시적 할인율 요청)
def conservative_estimate(value):
    estimator = get_estimator_rag()
    discount_result = estimator.estimate(
        "보수적 추정을 위한 할인율은?",
        context={'value_type': 'market_size'}
    )
    return value * (1 - discount_result.value)
    # ✅ OK (할인율도 Estimator가 추정)
```

---

## 🎯 핵심 원칙

### Single Source of Truth

```yaml
원칙:
  "모든 값/데이터 추정은 Estimator만 수행"

의미:
  - Quantifier: 계산 ✅, 추정 ❌
  - Validator: 검증 ✅, 추정 ❌
  - Observer: 관찰 ✅, 추정 ❌
  - Explorer: 가설 ✅, 추정 ❌ (가설 내 값은 Estimator)
  - Guardian: 평가 ✅, 추정 ❌
  - Estimator: 추정 ✅ (유일한 권한)

이유:
  1. 데이터 일관성
     - 같은 질문 → 같은 답
     - "Churn Rate"를 여러 Agent가 다르게 추정 → 혼란!
  
  2. 학습 효율
     - 모든 추정이 한 곳에 축적
     - Tier 2 → Tier 1 학습
     - 재사용 극대화
  
  3. 추적 가능성
     - 값의 출처 명확
     - "6%는 어디서 왔나?" → Estimator
     - 근거 완전 제공

예외:
  없음! (모든 Agent에 적용)
```

---

## 📊 적용 체크리스트

### Quantifier 검증

```yaml
✅ 체크:
  - 하드코딩된 값 없는가? (없어야 함)
  - 기본값 사용 없는가? (없어야 함)
  - "보통", "평균", "대략" 없는가? (없어야 함)
  - Estimator 호출하는가? (있어야 함)

❌ 발견 시:
  - Estimator 호출로 대체
  - 근거 기록
```

### Validator 검증

```yaml
✅ 체크:
  - 값 생성 없는가? (없어야 함)
  - 범위 추정 없는가? (없어야 함)
  - Estimator 호출하는가? (교차 검증 시)

❌ 발견 시:
  - Estimator 호출로 대체
```

### 모든 Agent 공통

```yaml
금지 키워드:
  ❌ "대충", "보통", "평균적으로"
  ❌ "~정도", "~쯤", "~즈음"
  ❌ "가정", "assume", "guess"
  ❌ 하드코딩된 숫자 (상수 제외)

필수 패턴:
  ✅ estimator.estimate()
  ✅ result.value
  ✅ result.reasoning_detail (근거 확인)
```

---

## 💡 요약

### "추정 금지" 정확한 의미

```yaml
금지:
  ❌ 값/데이터를 직접 추정하는 것
  ❌ 근사값을 자체 생성하는 것
  ❌ "대충 이 정도" 판단
  ❌ 기본값, 하드코딩, 가정

허용:
  ✅ 확정 데이터 사용
  ✅ 공식/알고리즘 적용 (계산)
  ✅ 검증 (비교, 평가)
  ✅ 검색 (RAG)
  ✅ Estimator 호출 (위임)

핵심:
  "추정 = 데이터/값 생성 행위"
  → Estimator만 가능
  → 다른 Agent는 위임
```

### 왜 이 원칙이 중요한가?

```yaml
1. 데이터 일관성:
   - 같은 질문 → 같은 답 (보장)
   - 여러 Agent가 추정 → 불일치 (위험)

2. 근거 추적:
   - "6%는 어디서?" → Estimator 한 곳
   - 여러 Agent → 출처 불명

3. 학습 효율:
   - 한 곳에 축적 → 빠른 진화
   - 분산 → 비효율

4. 품질 관리:
   - Estimator: 검증된 프로세스 (11 Source, 판단 전략)
   - 각 Agent 자체 추정 → 품질 불균일
```

---

**정리**:

네, **"추정 금지" = "데이터/값 추정 금지"**가 맞습니다!

- ✅ **계산** (공식 적용) → 허용
- ✅ **검증** (비교, 평가) → 허용
- ✅ **검색** (RAG) → 허용
- ❌ **추정** (값 생성) → **Estimator만** 가능

**핵심**: 값을 만들어내는 행위는 Estimator만!

문서 저장하시겠습니까? 🎯
