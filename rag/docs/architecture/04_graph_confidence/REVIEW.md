# Graph Provenance & Confidence 검토

**제안:** Knowledge Graph 간선에 신뢰도 추가

---

## 🔍 문제 상황

### 현재 (간선 신뢰도 없음)

```cypher
// Neo4j Graph

(platform:Pattern)-[:COMBINES_WITH {
  synergy: "충성도 + 안정수익",
  example: "Amazon Prime",
  success_rate: 0.8
}]->(subscription:Pattern)
```

**문제:**
```yaml
신뢰도 불명:
  • "이 조합이 정말 좋은가?"
  • "누가 검증했나?"
  • "근거는?"
  
  example: "Amazon Prime"
    → 1개 사례만?
    → 충분한가?
  
  success_rate: 0.8
    → 어떻게 계산?
    → 믿을 수 있나?

Guardian 평가 시:
  "platform + subscription 조합 추천"
  
  Guardian:
    "이 조합 신뢰할 만한가?"
    → 판단 근거 없음! 🚨
```

---

## 💡 제안 1: Provenance (근거 추적)

```cypher
(platform)-[:COMBINES_WITH {
  synergy: "충성도 + 안정수익",
  
  // Provenance (근거)
  evidence: [
    {
      case: "Amazon Prime",
      metrics: {
        retention: "+40%",
        revenue: "+25%"
      },
      source: "SRC_042",
      verified_by: "validator",
      date: "2024-10"
    },
    {
      case: "Spotify Premium",
      metrics: {
        conversion: "42%",
        churn: "-15%"
      },
      source: "SRC_089",
      verified_by: "validator",
      date: "2024-11"
    }
  ],
  
  // Confidence (신뢰도)
  confidence: 0.85,
  confidence_basis: "2개 검증 사례, Validator 확인"
}]->(subscription)
```

**장점:**
```yaml
✅ 추적 가능:
   • 근거 명확
   • 출처 확인
   • 검증자 표시

✅ Guardian 평가:
   • evidence 개수 확인
   • verified_by 확인
   • confidence 참고
   
   → 평가 근거 명확!

✅ 품질:
   • 약한 관계 필터링
   • confidence < 0.7 제외
```

**단점:**
```yaml
❌ 복잡:
   • 간선 메타데이터 복잡
   • 관리 부담

❌ 업데이트:
   • 새 사례 추가 시
   • evidence 배열 업데이트
   • 수동 작업?
```

---

## 💡 제안 2: Binary (Yes/No 구조)

```cypher
(platform)-[:COMBINES_WITH {
  synergy: "충성도 + 안정수익",
  
  // Binary Flags
  verified: true,  // Guardian 검증 완료
  has_evidence: true,  // 사례 있음
  
  // 간단한 Provenance
  evidence_count: 2,
  primary_example: "Amazon Prime",
  verified_date: "2024-11-02"
}]->(subscription)
```

**장점:**
```yaml
✅ 단순:
   • Boolean 플래그
   • 판단 쉬움
   
✅ 명확:
   • verified: true → 믿을 수 있음
   • verified: false → 의심
   
✅ 빠름:
   • 플래그 확인만
   • 복잡한 계산 없음
```

**단점:**
```yaml
❌ 정보 손실:
   • 얼마나 확실한지?
   • 어떤 근거?
   
   → 세밀한 판단 어려움
```

---

## 🎯 당신의 선호: Yes/No

```yaml
제안:
  "숫자보다 yes/no 선호"

이유 추측:
  • 단순함
  • 명확함 (애매함 없음)
  • 결정 쉬움 (믿는다/안 믿는다)

vs 숫자:
  confidence: 0.73
  → 믿는가? 애매함!
  
  verified: true
  → 믿는다! 명확!
```

---

## 🔍 대안: Tiered Confidence (계층적)

```cypher
(platform)-[:COMBINES_WITH {
  synergy: "충성도 + 안정수익",
  
  // 계층적 신뢰도
  confidence_tier: "high",  // high / medium / low
  
  // 각 Tier 기준
  // high: 3개 이상 검증 사례, Validator 확인
  // medium: 1-2개 사례
  // low: 이론적 추론만
  
  evidence_count: 2,
  verified: true,
  
  // Guardian 사용
  guardian_approved: true
}]->(subscription)
```

**장점:**
```yaml
✅ 명확:
   • high/medium/low (3단계)
   • 애매함 적음
   
✅ 실용적:
   • confidence_tier: high → 즉시 승인
   • confidence_tier: low → 추가 검증
   
✅ 단순:
   • 숫자보다 간단
   • Yes/No보다 세밀

판단 쉬움:
  high → 믿음
  medium → 신중
  low → 의심
```

---

## 💡 자동 Tier 계산

```yaml
규칙 기반 (schema_registry.yaml):

confidence_tier_rules:
  high:
    - evidence_count >= 3
    - all_verified == true
    - no_counter_evidence == true
  
  medium:
    - evidence_count >= 1
    - verified == true
  
  low:
    - evidence_count == 0
    - OR theoretical_only == true

자동 계산:
  evidence = [Amazon Prime, Spotify Premium]
  verified = true
  
  → Tier 계산:
    evidence_count: 2 (>= 1)
    verified: true
    
    → medium ✅

Guardian 사용:
  if tier == "high":
      approve()
  elif tier == "medium":
      additional_check()
  else:
      reject()
```

---

## 🎯 최종 추천

### Tiered Confidence (high/medium/low)

```yaml
방식:
  • 3-tier: high / medium / low
  • 규칙 자동 계산
  • schema_registry.yaml 정의

장점:
  ✅ 명확 (Yes/No보다 세밀)
  ✅ 단순 (숫자보다 간단)
  ✅ 자동 (규칙 기반)
  ✅ 실용적 (판단 쉬움)

vs Yes/No:
  더 세밀하지만 여전히 명확!

vs 숫자:
  덜 정밀하지만 훨씬 실용적!

→ 최적 균형! ✨
```

**당신의 의견은?**

A. Yes/No (가장 단순)  
B. Tiered (high/medium/low) ⭐ 제 추천  
C. 숫자 (0-1)  
D. 다른 방식?

**선택해주시면 최종 정리하겠습니다!** 🚀
