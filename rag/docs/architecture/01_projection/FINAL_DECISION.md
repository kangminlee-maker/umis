# Projection 전략 최종 결정

**날짜:** 2025-11-02  
**결론:** Dual-Index + Hybrid Projection + Learning Loop

---

## 🎯 최종 아키텍처

### Dual-Index 구조

```yaml
1. Canonical Index (업데이트용):
   • 정규화 청크 (5,000개)
   • Write: 여기만!
   • 1곳 수정 = 일관성 보장

2. Projected Index (검색용):
   • Agent별 청크 (30,000개)
   • Read: 여기서!
   • 검색 품질 우수
```

### Hybrid Projection 자동화

```yaml
Canonical → Projected 변환:

  90% 규칙 기반:
    projection_rules.yaml
    • 키워드 매칭
    • 섹션 분배
    • 빠름 (< 1초)
  
  10% LLM 판단:
    • 새 필드
    • 애매한 케이스
    • 느림 (2초)
```

### Learning Loop (점진적 개선!)

```yaml
1. LLM 판단 로그:
   llm_projection_log.jsonl
   
   예시:
   {
     "field": "churn_rate",
     "llm_decision": {
       "explorer": true,
       "quantifier": true,
       "guardian": true
     },
     "confidence": 0.95,
     "timestamp": "..."
   }

2. 분석 (주간):
   • 반복 패턴 발견
   • "churn_rate" → 항상 같은 Agent
   
3. 규칙화:
   projection_rules.yaml 자동 업데이트
   
   + churn_rate:
   +   agents: [explorer, quantifier, guardian]
   +   learned_from_llm: true

4. 효과:
   • 다음부터는 규칙으로!
   • LLM 호출 ↓
   • 비용 ↓, 속도 ↑
   
   → 자동 학습! 🎯
```

---

## 📊 성능 비교 (5,000개 사례)

| 항목 | Pre | Lazy | Dual-Index |
|------|-----|------|------------|
| **검색 품질** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **검색 속도** | 160ms | 140ms | 160ms |
| **업데이트** | 복잡 (6곳) | 단순 (1곳) | 단순 (1곳) |
| **일관성** | 위험 🚨 | 완벽 ✅ | 완벽 ✅ |
| **저장 공간** | 407 MB | 90 MB | 497 MB |
| **비용** | $70/월 | Free | $70/월 |

**종합:**
```yaml
Dual-Index = Pre 품질 + Lazy 일관성

추가 비용:
  저장: +90 MB (22%)
  → 무시 가능!

추가 이득:
  품질: Pre 수준
  일관성: 완벽
  학습: 자동 개선
  
  → 최선! ✨
```

---

## 🔧 구현 우선순위

### Phase 1 (즉시): Dual-Index 기본

```yaml
구현:
  1. Canonical Index 생성
  2. Projected Index 생성 (기존 유지)
  3. 업데이트 플로우:
     YAML → Canonical → Projected (단순 복사)

소요: 2일
효과: 일관성 보장
```

### Phase 2 (1주): Hybrid Projection

```yaml
구현:
  1. projection_rules.yaml 작성
  2. 규칙 기반 투영 (90%)
  3. LLM 판단 (10%)

소요: 3일
효과: 자동화
```

### Phase 3 (2주): Learning Loop

```yaml
구현:
  1. LLM 로그 저장
  2. 패턴 분석
  3. 자동 규칙 생성

소요: 5일
효과: 자동 학습
```

---

## 💡 사용자 경험

### 업데이트 시

```
Cursor (Cmd+I):

"코웨이에 해지율 3-5% 추가해줘"

AI:
  [Canonical 수정]
  + churn_rate: "3-5%"
  
  [Hybrid Projector 자동 실행]
  • 규칙: churn_rate → quantifier ✅
  • LLM: explorer, guardian 필요? → Yes
  
  [Projected 자동 재생성]
  • explorer_coway: + 해지율
  • quantifier_coway: + 해지율
  • guardian_coway: + 해지율
  
  [LLM 로그 저장]
  • churn_rate 분배 패턴 기록
  
  ✅ 완료! (2초)

사용자:
  대화만! 복잡도 0!
```

### 학습 효과

```yaml
1개월 후:
  • LLM 판단 축적: 100개
  • 패턴 발견: 20개
  • 규칙 추가: 20개
  
  효과:
    • LLM 호출: 10% → 5%
    • 속도: ↑
    • 비용: ↓
    
    → 자동 개선! 🎯
```

---

## 🎯 최종 결정

**Dual-Index + Hybrid Projection + Learning Loop 채택!**

```yaml
이유:
  ✅ 품질: Pre 수준 (노이즈 없음)
  ✅ 일관성: Lazy 수준 (1곳 수정)
  ✅ 자동화: Hybrid (규칙 + LLM)
  ✅ 학습: 점진적 개선
  ✅ 비용: 무시 가능 ($70/월)

구현:
  즉시: Dual-Index
  1주: Hybrid Projection
  2주: Learning Loop
```

**다음:** 2번 (Schema-Registry) 검토

---

**관련 문서:**
- ARCHITECTURE_REVIEW_01_PROJECTION.md
- SCALE_COST_ANALYSIS.md
- PERFORMANCE_UPDATE_ANALYSIS.md
- SEARCH_QUALITY_COMPARISON.md
- DUAL_INDEX_AUTOMATION.md
- 이 파일 (FINAL_DECISION.md)

