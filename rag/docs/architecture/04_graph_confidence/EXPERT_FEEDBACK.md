# Graph Confidence 전문가 피드백

**날짜:** 2025-11-02  
**출처:** 동료 전문가

---

## 📊 피드백: P0-4

### 문제

```yaml
v2.0:
  confidence: {
    similarity: 0.92,
    coverage: 0.10,
    validation: yes,
    overall: "high"  # 문자열
  }

부족:
  • 근거 없음 ("왜 0.92?")
  • reviewer 없음
  • timestamp 없음
  • overall 숫자 아님
```

---

### 제안

```yaml
추가:
  evidence_ids: ["CAN-amazon", "PRJ-spotify"]
  
  provenance:
    source: enum[humn_review, auto_rule, llm_infer]
    reviewer_id: "stewart|rachel"
    timestamp: ISO8601
  
  confidence.overall: 0.83 (0-1 숫자)
```

---

## ✅ v3.0 반영

```yaml
graph.relationship:
  confidence:
    similarity: 0.92
    coverage: 0.10
    validation: yes
    overall: 0.83  # 숫자!
  
  evidence_ids: ["CAN-...", "PRJ-..."]
  
  provenance:
    reviewer_id: "stewart"
    timestamp: "2025-11-02T..."

효과:
  • 근거 역추적 100%
  • 설명가능성
  • 감사 가능
```

---

**전문가 평가:**
"그래프 써도 A(재현성/설명성) 무너지지 않음"

