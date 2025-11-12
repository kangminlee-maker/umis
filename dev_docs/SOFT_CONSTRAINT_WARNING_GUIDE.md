# Soft Constraint 경고 시스템 (v7.8.0)

**날짜**: 2025-11-12  
**목적**: Soft Constraint 위반 시 사용자 확인 요청  
**원칙**: 자동 Knock-out 없음 → 경고 + 사용자 판단

---

## 🎯 핵심 원칙

### **Hard vs Soft Constraints 차이**

| 구분 | Hard (Physical) | Soft (Legal, Statistical, Behavioral) |
|------|----------------|--------------------------------------|
| **위반 시** | ❌ 즉시 Knock-out | ⚠️ 경고 + 사용자 확인 |
| **이유** | 물리 법칙 (절대 위반 불가) | 예외 가능 (특수 상황, 혁신 등) |
| **예시** | Rate > 1.0 (불가능) | 시급 < 최저임금 (지하경제?) |
| **처리** | 자동 제거 | 사용자 판단 위임 |

### **왜 Soft는 자동 Knock-out 안 하나?**

1. **예외 상황 존재**
   - 지하경제 (최저임금 미달)
   - 혁신 모델 (전환율 30% 초과)
   - 특수 산업 (자연 범위 벗어남)

2. **사용자가 더 잘 판단**
   - 도메인 전문성
   - 맥락 이해
   - 데이터 품질 평가

3. **Soft의 의미**
   - "대부분 지켜지지만"
   - "예외도 있을 수 있음"
   - "사용자 판단 필요"

---

## 📊 경고 출력 예시

### **예시 1: 법률 위반 (최저임금)**

```
⚠️⚠️⚠️ Soft Constraint 경고 1개 ⚠️⚠️⚠️

[경고 1]
⚠️ 법률 제약 위반 가능성
  추정값: 5,000원
  임계값: 6,902원 (최저 9,860원 × 0.7)
  차이: -28%

📋 근거: 최저임금의 70% 미만은 명백한 위반 (사회 유지 불가)

⚠️ 이 추정값을 사용하시겠습니까?
   - 예외 상황 (지하경제, 특수 케이스)일 수 있음
   - 또는 추정 오류일 수 있음

심각도: high
```

### **예시 2: 통계 패턴 이탈 (Churn Rate)**

```
⚠️⚠️⚠️ Soft Constraint 경고 1개 ⚠️⚠️⚠️

[경고 1]
⚠️ 통계 패턴 이상치 감지
  추정값: 0.600 (60%)
  자연 범위: [0.0, 0.5] (p5-p95)

📋 근거: Churn rate 50% 초과는 비즈니스 지속 불가능

⚠️ 이 추정값을 사용하시겠습니까?
   - 특수한 상황일 수 있음
   - 또는 추정 오류일 수 있음

심각도: medium
```

### **예시 3: 행동 패턴 이상 (전환율)**

```
⚠️⚠️⚠️ Soft Constraint 경고 1개 ⚠️⚠️⚠️

[경고 1]
⚠️ 행동 패턴 이상치 감지
  추정값: 0.350 (35%)
  인간본능 범위: [0.005, 0.30]

📋 근거: 전환율 30% 초과는 비현실적 (인간 행동 한계)

⚠️ 이 추정값을 사용하시겠습니까?
   - 혁신적 비즈니스 모델일 수 있음
   - 또는 추정 오류일 수 있음

심각도: medium
```

---

## 🔧 구현 구조

### **1. Soft Source validate() 메서드**

```python
def validate(self, question: str, estimated_value: float) -> Optional[Dict[str, Any]]:
    """
    Soft Constraint 검증
    
    Returns:
        None: 통과 ✅
        Dict: 경고 정보 (사용자 확인 필요)
    """
    
    # 위반 감지
    if violation_detected:
        return {
            'warning': True,
            'severity': 'high' | 'medium' | 'low',
            'message': '상세 경고 메시지',
            'threshold': 임계값,
            'user_confirmation_needed': True
        }
    
    return None  # 통과
```

### **2. JudgmentSynthesizer 통합**

```python
class JudgmentSynthesizer:
    def __init__(self):
        # Soft Sources 초기화
        self.legal = LegalNormSource()
        self.statistical = StatisticalPatternSource()
        self.behavioral = BehavioralInsightSource()
    
    def synthesize(self, ..., question: str):
        # ...
        
        # Soft Constraint 검증
        soft_warnings = self._validate_soft_constraints(value, question)
        
        if soft_warnings:
            result['soft_warnings'] = soft_warnings
            # 경고 출력 (사용자에게 보임)
```

### **3. Phase 3 Guestimation 처리**

```python
# Phase 3에서 경고 처리
judgment = self.synthesizer.synthesize(
    value_estimates,
    context,
    question=question  # 전달
)

soft_warnings = judgment.get('soft_warnings', [])

if soft_warnings:
    # 로그에 경고 출력
    logger.warning(f"\n⚠️⚠️⚠️ Soft Constraint 경고 {len(soft_warnings)}개\n")
    
    for warning in soft_warnings:
        logger.warning(warning['message'])

# EstimationResult에 포함
result = EstimationResult(
    ...,
    soft_warnings=soft_warnings  # 사용자가 확인 가능
)
```

### **4. 사용자 경험**

```python
# Estimator 사용
estimator = EstimatorRAG()
result = estimator.estimate("소상공인 시급은?")

# 결과 확인
if result.soft_warnings:
    print(f"\n⚠️ 경고 {len(result.soft_warnings)}개\n")
    
    for warning in result.soft_warnings:
        print(warning['message'])
        
        # 사용자 확인
        user_input = input("\n계속하시겠습니까? (y/N): ")
        
        if user_input.lower() != 'y':
            print("추정 중단")
            return None

# 경고 없거나 사용자 승인 → 계속
print(f"최종 값: {result.value}")
```

---

## 📋 Soft Constraint 목록

### **1. LegalNormSource (법률/규범)**

| 제약 | 법적 값 | 임계값 | 위반 조건 |
|------|---------|--------|----------|
| 최저임금 | 9,860원 | 6,902원 (70%) | < 6,902원 |
| 시급 | 9,860원 | 6,902원 (70%) | < 6,902원 |
| 주당근로시간 | 52시간 | 67.6시간 (130%) | > 67.6시간 |
| 근로시간 | 52시간 | 67.6시간 (130%) | > 67.6시간 |

**Severity**: high (법률 위반)

### **2. StatisticalPatternSource (통계 패턴)**

| 패턴 | 자연 범위 | 위반 조건 | Severity |
|------|----------|----------|----------|
| 흡연율 | 5-60% | < 5% or > 60% | high if ×1.5, medium |
| 이탈률 | 0-50% | > 50% | high if > 75%, medium |
| Churn | 0-50% | > 50% | high if > 75%, medium |

**Severity 계산**:
- high: 자연 범위의 150% 초과
- medium: 자연 범위 벗어남

### **3. BehavioralInsightSource (행동경제학)**

| 패턴 | 인간본능 범위 | 위반 조건 |
|------|--------------|----------|
| 전환율 | 0.5-30% | < 0.5% or > 30% |
| Conversion | 0.5-30% | < 0.5% or > 30% |
| 가격민감도 | 0.3-2.5 | < 0.3 or > 2.5 |

**Severity**: medium (행동경제학)

---

## 🎯 사용 사례

### **Case 1: 경고 없음 (정상)**

```python
질문: "SaaS Churn Rate는?"
추정값: 0.05 (5%)

검증:
- Legal: N/A (해당 없음)
- Statistical: 0.05 ∈ [0.0, 0.5] → ✅ 통과
- Behavioral: N/A

결과: soft_warnings = [] (경고 없음)
→ 바로 사용 가능
```

### **Case 2: 경고 1개 (사용자 확인)**

```python
질문: "소상공인 시급은?"
추정값: 5,000원

검증:
- Legal: 5,000 < 6,902 → ⚠️ 경고
- Statistical: N/A
- Behavioral: N/A

결과: soft_warnings = [
    {
        'severity': 'high',
        'message': '법률 제약 위반 가능성...',
        'user_confirmation_needed': True
    }
]

→ 사용자에게 경고 표시
→ 사용자 확인 후 진행 또는 중단
```

### **Case 3: 경고 2개 (복합)**

```python
질문: "특수 산업 전환율은?"
추정값: 0.35 (35%)

검증:
- Legal: N/A
- Statistical: N/A
- Behavioral: 0.35 > 0.30 → ⚠️ 경고

결과: soft_warnings = [
    {
        'severity': 'medium',
        'message': '행동 패턴 이상치...',
        'user_confirmation_needed': True
    }
]

→ 혁신적 모델일 수 있음
→ 사용자 판단 필요
```

---

## 💡 사용자 응답 처리

### **Native 모드 (Cursor)**

Cursor Composer에서 경고 표시:

```
⚠️⚠️⚠️ Soft Constraint 경고 1개 ⚠️⚠️⚠️

⚠️ 법률 제약 위반 가능성
  추정값: 5,000원
  임계값: 6,902원
  ...

❓ 계속하시겠습니까?
```

사용자 응답:
- "네" / "계속" → 경고 무시하고 진행
- "아니오" / "중단" → 추정 재검토
- "다시" → Phase 4 (Fermi) 시도

### **External 모드 (API)**

```python
result = estimator.estimate("소상공인 시급")

if result.soft_warnings:
    for warning in result.soft_warnings:
        print(warning['message'])
        
        user_input = input("\n계속? (y/N): ")
        
        if user_input.lower() != 'y':
            # 재추정 또는 중단
            return None

# 사용자 승인 → 진행
use_result(result)
```

---

## 📝 경고 메시지 설계 원칙

### **1. 명확한 정보 제공**
- 추정값과 임계값 비교
- 차이% 표시
- 근거 명확히

### **2. 양방향 해석 제공**
```
⚠️ 이 추정값을 사용하시겠습니까?
   - 예외 상황일 수 있음 (긍정적 해석)
   - 또는 추정 오류일 수 있음 (부정적 해석)
```

### **3. Severity 구분**

| Severity | 의미 | 예시 |
|----------|------|------|
| **high** | 매우 심각 (법률, 자연 범위 150% 초과) | 시급 < 최저 70%, Churn > 75% |
| **medium** | 주의 필요 (자연 범위 벗어남) | Churn 60%, 전환율 35% |
| **low** | 참고 (미사용) | - |

---

## 🚀 향후 개선

### **Phase 1: 자동 학습** (v7.9.0)

사용자가 경고 무시하고 진행한 케이스 학습:

```python
# 사용자: "네, 지하경제라 맞습니다"
result = estimator.estimate("소상공인 시급", user_confirmed=True)

# 학습
estimator.learn_exception(
    constraint="최저임금",
    exception_case="지하경제",
    context=context
)

# 다음부터 같은 맥락이면 경고 안 함
```

### **Phase 2: 맥락 기반 경고** (v8.0.0)

맥락에 따라 경고 제외:

```python
context = Context(
    domain="Underground_Economy",  # 지하경제
    special_case=True
)

# 최저임금 경고 스킵
# 사용자가 이미 알고 있는 특수 케이스
```

---

## 📚 관련 코드

- `umis_rag/agents/estimator/sources/soft.py` - validate() 메서드
- `umis_rag/agents/estimator/judgment.py` - _validate_soft_constraints()
- `umis_rag/agents/estimator/phase3_guestimation.py` - 경고 처리
- `umis_rag/agents/estimator/models.py` - EstimationResult.soft_warnings

---

**작성자**: UMIS Team  
**버전**: v7.8.0  
**핵심**: Soft = 경고 (사용자 판단), Hard = Knock-out (자동 제거)

