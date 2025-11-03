# Confidence 숫자의 출처

**질문:** 0.8, 0.7 같은 숫자를 누가 어떻게 정하는가?

---

## 🔍 4가지 방법

### Method 1: 수동 설정 (사람)

```yaml
# config/pattern_relationships.yaml

platform + subscription:
  synergy: "충성도 + 안정수익"
  example: "Amazon Prime"
  confidence: 0.8  # ← 사람이 직접 입력!
```

**문제:**
```yaml
누가 정하나?
  • 관리자?
  • 전문가?
  • UMIS 사용자?

기준은?
  • 느낌?
  • 경험?
  • 직관?

일관성:
  • A: 0.8 (보수적)
  • B: 0.9 (낙관적)
  → 사람마다 다름! ❌

유지보수:
  • 새 사례 추가 시
  • confidence 재조정?
  • 누가 판단?

판단:
  주관적, 불일치 위험
  → 나쁨! ❌
```

---

### Method 2: 규칙 기반 (자동 계산)

```yaml
# confidence_rules.yaml

tier_calculation:
  high: 0.9
    rules:
      - evidence_count >= 3
      - all_verified == true
      - validator_approved == true
  
  medium: 0.7
    rules:
      - evidence_count >= 1
      - verified == true
  
  low: 0.4
    rules:
      - evidence_count == 0
      - theoretical_only == true

# 자동 계산
evidence = ["Amazon Prime", "Spotify Premium"]
verified = true

→ evidence_count: 2 (>= 1)
→ verified: true
→ Tier: medium
→ Confidence: 0.7 ✅
```

**장점:**
```yaml
✅ 객관적:
   • 규칙 기반
   • 일관성 보장

✅ 자동:
   • 계산 자동
   • 사람 판단 불필요

✅ 투명:
   • 규칙 공개
   • 이유 명확

✅ 유지보수:
   • 새 사례 → 자동 재계산
   • confidence 자동 업데이트
```

**단점:**
```yaml
⚠️ 경직성:
   • 규칙으로만
   • 예외 처리 어려움

⚠️ 초기 설정:
   • 적절한 규칙 찾기
   • 조정 필요
```

---

### Method 3: 통계 기반 (실제 성공률)

```yaml
platform + subscription:
  
  실제 사용 추적:
    • 추천: 100회
    • 성공: 85회
    • 실패: 15회
  
  계산:
    confidence = 85 / 100 = 0.85
```

**장점:**
```yaml
✅ 실제 데이터:
   • 가장 정확
   • 검증됨

✅ 자동 개선:
   • 사용할수록 정확해짐
```

**단점:**
```yaml
❌ 초기값:
   • 사용 전에는?
   • Cold start 문제

❌ 데이터:
   • 성공/실패 추적 필요
   • 인프라 필요
   
❌ 시간:
   • 충분한 데이터까지 오래 걸림
```

---

### Method 4: LLM 판단

```yaml
prompt = f"""
다음 패턴 조합의 신뢰도를 평가하세요:

조합: platform + subscription
시너지: 충성도 + 안정수익
사례:
  - Amazon Prime (retention +40%, revenue +25%)
  - Spotify Premium (conversion 42%)

0-1 사이 점수와 이유를 제시하세요.
"""

result = llm.invoke(prompt)
# → 0.85, "2개 검증 사례, 대기업 성공..."
```

**장점:**
```yaml
✅ 지능적:
   • 맥락 이해
   • 근거 제시

✅ 유연:
   • 복잡한 판단
   • 예외 처리
```

**단점:**
```yaml
❌ 비용:
   • 관계마다 LLM 호출
   • 45개 × $0.001 = $0.045

❌ 불안정:
   • 매번 다를 수 있음
   • 재현성 낮음

❌ 느림:
   • 초기 구축 시 시간
```

---

## 🎯 제 추천: Hybrid (규칙 + Tier)

### 구조

```yaml
# config/pattern_relationships.yaml

platform + subscription:
  synergy: "충성도 + 안정수익"
  
  # Evidence (근거)
  evidence:
    - "Amazon Prime"
    - "Spotify Premium"
  
  verified: true
  
  # 자동 계산됨!
  confidence_tier: medium  # ← 규칙 기반 자동!
  
  # 상세 (선택)
  confidence_detail:
    evidence_count: 2
    verified: true
    validator_approved: true
    
    calculation: "2 verified cases → medium tier"
```

### 자동 계산

```python
def calculate_tier(relationship):
    evidence_count = len(relationship['evidence'])
    verified = relationship.get('verified', False)
    
    # 규칙 적용 (간단!)
    if evidence_count >= 3 and verified:
        return "high"
    elif evidence_count >= 1 and verified:
        return "medium"
    else:
        return "low"

# 사용
tier = calculate_tier(platform_subscription)
# → "medium"
```

**Guardian 사용:**
```python
def evaluate_pattern_combination(combination):
    tier = combination['confidence_tier']
    
    if tier == "high":
        return {'approve': True, 'reason': '검증된 조합'}
    elif tier == "medium":
        return {'approve': True, 'caution': '추가 검증 권장'}
    else:
        return {'approve': False, 'reason': '근거 부족'}
```

---

## 🎯 4번 최종 추천

**Tiered Confidence (규칙 기반 자동)**

```yaml
방식:
  • high / medium / low
  • 규칙 기반 자동 계산
  • confidence_rules.yaml

장점:
  ✅ 객관적 (규칙)
  ✅ 자동 (계산)
  ✅ 명확 (3단계)
  ✅ 단순 (Yes/No보다 약간 세밀)

vs Yes/No:
  더 세밀하면서도 여전히 명확!

계산 근거:
  명시적 (confidence_rules.yaml)
```

**당신의 의견은?**

선호하시는 방식을 말씀해주세요! 🚀
