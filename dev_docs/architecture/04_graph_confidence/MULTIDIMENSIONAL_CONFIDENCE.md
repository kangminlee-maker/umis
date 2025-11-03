# 다차원 Confidence 평가

**통찰:** 질적/양적을 함께 봐야 함!

---

## 🎯 당신의 정확한 지적

### 반례 1: 고품질 1개

```yaml
시나리오:
  platform + subscription
  
  사례: 1개
    • Amazon Prime (유사도 0.99)
    • 검증됨, 5년, 글로벌

제 방식 (Count 기반):
  evidence_count: 1
  → Tier: low ❌
  
  문제: 품질 무시!

당신의 방식 (질적):
  similarity: 0.99
  → confidence: high ✅
  
  맞음: 1개여도 충분히 확실!
```

### 반례 2: 패턴 존재

```yaml
시나리오:
  low_end + channel 조합
  
  사례: 5,000개
    • 최고 유사도: 0.66
    • 0.5+ 사례: 5,000개 (모든 사례!)

제 방식 (유사도만):
  best_similarity: 0.66
  → confidence: medium? ⚠️
  
  문제: 패턴 무시!

당신의 방식 (양적):
  coverage: 5,000 / 5,000 = 100%
  threshold_0.5: 100%
  
  → confidence: high ✅
  
  맞음: 강한 패턴!
```

**결론:**
```yaml
질적 (유사도): 개별 사례 강도
  0.99 하나 → 확실!

양적 (분포): 전체 패턴
  0.5+ 100% → 패턴 확실!

→ 둘 다 봐야 함! ✨
```

---

## 💡 다차원 Confidence

### 3가지 차원

```yaml
1. Similarity (질적, 연속)
   최고 유사도:
     0.95+: 거의 동일
     0.80-0.95: 매우 유사
     0.60-0.80: 유사
     < 0.60: 약함

2. Coverage (양적, 분포)
   패턴 강도:
     threshold_0.7+ > 10%: 강한 패턴
     threshold_0.5+ > 50%: 명확한 패턴
     threshold_0.5+ < 10%: 약한 패턴

3. Validation (검증, 이진)
   검증 여부:
     validator_approved: true/false
     source_reliability: high/medium/low
```

### 종합 평가

```cypher
(platform)-[:COMBINES_WITH {
  synergy: "충성도 + 안정수익",
  
  // 다차원 Confidence
  confidence: {
    // 질적 (유사도)
    similarity: {
      best: 0.99,
      avg_top5: 0.92,
      judgment: "excellent"
    },
    
    // 양적 (분포)
    coverage: {
      total_cases: 50000,
      threshold_0.7: 150,  // 0.3%
      threshold_0.5: 5000,  // 10%
      judgment: "moderate_pattern"
    },
    
    // 검증
    validation: {
      validator_approved: true,
      source_reliability: "high",
      time_tested: "5 years",
      judgment: "verified"
    }
  },
  
  // 종합 판단
  overall_confidence: "high",
  reasoning: [
    "Best case 0.99 (Amazon Prime)",
    "10% cases show pattern",
    "Validator verified"
  ]
}]->(subscription)
```

---

## 🎯 판단 로직

### Guardian 평가 (다차원)

```python
def evaluate_confidence(relationship):
    sim = relationship['confidence']['similarity']
    cov = relationship['confidence']['coverage']
    val = relationship['confidence']['validation']
    
    # Case 1: 고품질 하나 (유사도)
    if sim['best'] >= 0.95 and val['validator_approved']:
        return {
            'confidence': 'high',
            'reason': f"Excellent case (similarity {sim['best']})"
        }
    
    # Case 2: 강한 패턴 (양적)
    if cov['threshold_0.5'] / cov['total_cases'] > 0.1:
        return {
            'confidence': 'high',
            'reason': f"Strong pattern (10% cases match)"
        }
    
    # Case 3: 중간 (둘 다 중간)
    if sim['best'] >= 0.7 and cov['threshold_0.5'] > 100:
        return {
            'confidence': 'medium',
            'reason': "Moderate similarity + coverage"
        }
    
    # Case 4: 약함
    return {
        'confidence': 'low',
        'reason': "Insufficient evidence"
    }
```

**예시:**

```yaml
Case A (고품질 1개):
  similarity.best: 0.99 (Amazon Prime)
  validator_approved: true
  
  → confidence: high ✅
  → 이유: "Excellent proven case"

Case B (패턴 존재):
  similarity.best: 0.66
  coverage.threshold_0.5: 5000 / 50000 = 10%
  
  → confidence: high ✅
  → 이유: "Strong pattern (10%)"

Case C (둘 다 약함):
  similarity.best: 0.55
  coverage.threshold_0.5: 10 / 50000 = 0.02%
  
  → confidence: low ❌
  → 이유: "Weak evidence"
```

---

## 💡 최종 추천

**Multi-Dimensional Confidence**

```yaml
구조:
  confidence: {
    similarity: {...}
    coverage: {...}
    validation: {...}
  }
  
  overall: high/medium/low

판단:
  • 질적 OR 양적 충족 → high
  • 둘 다 중간 → medium
  • 둘 다 약함 → low

장점:
  ✅ 예외 없음 (다각도)
  ✅ 명확 (근거 투명)
  ✅ 자동 (규칙 기반)
  ✅ 실용적 (판단 쉬움)
```

**당신이 정확했습니다!**

한 방향만 보면 예외 생김  
→ 다차원 평가 필수! ✨

---

**5번 검토하시겠어요?** 🚀
