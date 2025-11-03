# ID & Lineage 표준화 최종 결정

**날짜:** 2025-11-02  
**결론:** ID 네임스페이스 + Lineage 블록 채택 (P0)  
**출처:** 전문가 피드백

---

## 🎯 문제

```yaml
현재:
  source_id만 존재
  
문제:
  • 레이어별 ID 구분 없음
  • "baemin" → 어느 레이어?
  • 계보 추적 불가능
  • 충돌 위험
```

---

## 💡 해결책

### ID 네임스페이스

```yaml
구조:
  CAN-xxxxxxxx: Canonical Index
  PRJ-xxxxxxxx: Projected Index
  GND-xxxxxxxx: Graph Node
  GED-xxxxxxxx: Graph Edge
  MEM-xxxxxxxx: Memory

예시:
  CAN-baemin-001: Canonical 청크
  PRJ-baemin-exp-001: Projected (Explorer view)
  GND-platform-001: Graph 노드 (패턴)
  GED-plat-sub-001: Graph 간선 (조합)
  MEM-query-001: Query Memory
```

### Lineage 블록

```yaml
구조:
  lineage:
    from: "CAN-1234"
    via:
      - projection_rule_id: "RULE-5678"
        projected_chunk_id: "PRJ-9012"
      - graph_node_id: "GND-3456"
    evidence_ids: ["CAN-1234", "PRJ-9012"]
    created_by:
      agent: "Stewart"
      overlay_layer: "team"
      tenant_id: "team_alpha"

추적:
  PRJ-9012는?
  → lineage 확인
  → from: CAN-1234 (원본)
  → via: RULE-5678 (방법)
  → created_by: Stewart/team
  
  → 완전 추적! ✅
```

---

## 🎯 가치

```yaml
감사성(A):
  • 교차 레이어 추적 100%
  • "왜 이렇게 됐는지" 완전 설명
  • 외부 감사 가능

충돌 방지:
  • ID 구분 명확
  • 네임스페이스 분리
  • 중복 불가능

디버깅:
  • 문제 발생 → lineage 추적
  • 원인 빠르게 파악
  • 수정 지점 명확
```

---

## 🔧 구현

### schema_registry.yaml

```yaml
core_fields:
  identity:
    canonical_chunk_id:
      type: string
      pattern: "CAN-[a-z0-9]{8}"
      required: true
    
    projected_chunk_id:
      type: string
      pattern: "PRJ-[a-z0-9]{8}"
    
    graph_node_id:
      type: string
      pattern: "GND-[a-z0-9]{8}"
    
    graph_edge_id:
      type: string
      pattern: "GED-[a-z0-9]{8}"
    
    memory_id:
      type: string
      pattern: "MEM-[a-z0-9]{8}"
  
  lineage:
    from:
      type: string
      description: "원본 Canonical ID"
    
    via:
      type: array
      description: "변환 경로"
    
    evidence_ids:
      type: array
      description: "근거 청크 ID"
    
    created_by:
      type: object
      properties:
        agent: string
        overlay_layer: enum
        tenant_id: string
```

---

## 📋 우선순위

```
P0: 즉시 (Week 1)
구현: schema_registry.yaml
가치: 감사성(A) 핵심
```

---

**전문가 피드백:**
"교차 레이어 추적성 강화로 감사성 확보"

