# Projection 전문가 피드백

**날짜:** 2025-11-02  
**출처:** 동료 전문가

---

## 📊 피드백

### P0-3: TTL + 온디맨드

```yaml
원래 설계 (v2.0):
  Projected Index: 항상 물리화
  → 30,000개 청크

문제:
  • 저장 팽창
  • 재인덱싱 비용
  • 동기화 복잡

피드백:
  "Projected = Materialized View(+TTL)"
  
  기본: 지연 투영
  고빈도만: 영속화
  TTL: 24시간

효과:
  저장/재인덱싱 비용 급감
```

---

## 🎯 당신의 원래 제안

```yaml
당신 (처음):
  "Lazy Projection 병행?"

저 (v2.0):
  "Dual-Index로 항상 물리화"

전문가:
  "TTL + 온디맨드"

결론:
  당신이 처음부터 맞았음!
```

---

## ✅ v3.0 반영

```yaml
Projected Index:
  materialization:
    strategy: "on_demand"
    cache_ttl_hours: 24
    persist_profiles: ["explorer_high_traffic"]

효과:
  비용 급감
  품질 유지
```

---

**전문가 평가:**
"저장 중복/동기화 비용 급감. 규칙+캐시로 충분히 빠름."
