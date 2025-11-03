# 전문가 피드백 채택 결정

**날짜:** 2025-11-02  
**결정:** 6개 P0 보완안 모두 채택!

---

## ✅ 채택 결정

### P0-1: ID & Lineage ✅ 채택

**이유:** 감사성(A) 핵심

```yaml
추가:
  ID 네임스페이스:
    • CAN-xxxxxxxx (Canonical)
    • PRJ-xxxxxxxx (Projected)
    • GND-xxxxxxxx (Graph Node)
    • GED-xxxxxxxx (Graph Edge)
    • MEM-xxxxxxxx (Memory)
  
  Lineage 블록:
    from: "CAN-1234"
    via: ["RULE-5678", "PRJ-9012"]
    evidence_ids: ["CAN-1234", "PRJ-9012"]
    created_by: {agent, overlay_layer, tenant_id}

가치:
  • 교차 레이어 추적
  • 충돌 방지
  • 디버깅 용이
```

---

### P0-2: anchor_path + hash ✅ 채택

**이유:** 재현성(A) 핵심

```yaml
변경:
  Before:
    sections: {start: 0, end: 150}
  
  After:
    sections:
      - anchor_path: "subscription.trigger_observations"
        content_hash: "sha256:ab12..."
        span_hint: {paragraphs: "12-18"}

가치:
  • 토크나이저 변경 안전
  • YAML 수정 안전
  • 참조 불변성
```

---

### P0-3: TTL + 온디맨드 ✅ 채택

**이유:** 비용 통제 + 원래 Lazy 제안 복원

```yaml
변경:
  Dual-Index 설계 수정
  
  Canonical: 항상 물리화
  Projected: TTL + 온디맨드
  
  materialization:
    strategy: "on_demand"
    cache_ttl_hours: 24
    persist_profiles: ["explorer_high_traffic"]

가치:
  • 저장 비용 급감
  • 재인덱싱 비용 급감
  • 동기화 간단
  • 당신의 원래 통찰!
```

---

### P0-4: Graph 근거 ✅ 채택

**이유:** 설명가능성

```yaml
추가:
  graph.relationship:
    evidence_ids: ["CAN-...", "PRJ-..."]
    provenance:
      source: enum[humn_review, auto_rule, llm_infer]
      reviewer_id: "stewart|rachel"
      timestamp: ISO8601
    confidence:
      overall: 0.83 (0-1 숫자)

가치:
  • 근거 추적
  • 감사 가능
  • 설명 가능
```

---

### P0-5: RAE Index (초소형) ✅ 채택!

**이유:** 결과 일관성 > 비용 절감

**당신의 판단:**
```yaml
"비용절감 아니지만
 결과 일관성을 위해
 가치 > 복잡도"
```

**완전 동의합니다!**

```yaml
초소형 RAE:
  fields:
    - deliverable_id
    - grade
    - rationale
    - evidence_ids
    - created_at
  
  복잡도: 낮음 (5개 필드, Vector 재사용)
  
  가치:
    • 평가 일관성 ⭐ 핵심!
    • 유사 케이스 재사용
    • Stage-3 근거 재사용

비용:
  연간 $1-2 (미미하지만)
  → 일관성이 더 중요!

채택 이유:
  비용 X
  일관성 O
  → 가치 충분! ✅
```

---

### P0-6: Overlay 메타 선반영 ✅ 채택

**이유:** 미래 안전, 비용 거의 없음

```yaml
추가 (스키마만):
  overlay:
    layer: enum[core, team, personal]
    tenant_id: string
    merge_strategy: enum[append, replace, patch]
    acl: {visibility: enum[private, org, public]}

복잡도: 매우 낮음
구현: 향후
스키마만: 지금

가치:
  나중 마이그레이션 방지
```

---

## 🎯 개선안 번호 재조정

### Before (8개)

```yaml
1-4, 7-8 채택
5 제외
6 설계만
```

### After (14개!)

```yaml
기존:
  1. Dual-Index (수정: TTL 추가)
  2. Schema-Registry
  3. Routing YAML
  4. Multi-Dimensional Confidence (수정: overall 숫자)
  5. RAE Index (제외 → 채택!) ⭐
  6. Overlay Layer
  7. Fail-Safe
  8. System RAG

신규 (P0-1,2,3,4,6):
  9. ID & Lineage 표준화 ⭐
  10. anchor_path + hash ⭐
  11. TTL + 온디맨드 (1번 수정)
  12. Graph 근거 표준화 (4번 수정)
  13. RAE Index 초소형 (5번 복원)
  14. Overlay 메타 선반영 (6번 수정)
```

**정리하면:**

```yaml
새 개선안:
  9. ID & Lineage (신규)
  10. anchor + hash (신규)

수정 개선안:
  1. Dual-Index → TTL 추가
  4. Confidence → overall 숫자
  5. RAE → 초소형 채택
  6. Overlay → 메타 선반영

총: 14개 (8개 + 6개)
```

---

## 📋 다음 작업

```yaml
즉시:
  1. schema_registry.yaml 작성
     • P0-1,2,4,6 모두 반영
     • ID 네임스페이스
     • anchor + hash
     • Graph 근거
     • Overlay 메타
  
  2. Architecture 문서 업데이트
     • 14개 개선안으로 확장
     • P0-5 복원
     • 수정 사항 반영
  
  3. ROADMAP 업데이트
     • TTL 구현 추가
     • RAE Index 구현 추가
```

**시작하시겠어요?** 🚀

