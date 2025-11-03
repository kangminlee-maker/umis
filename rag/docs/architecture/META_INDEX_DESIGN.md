# UMIS RAG 메타 인덱스 설계

**날짜:** 2025-11-02  
**목적:** 전체 RAG 시스템의 통합 메타데이터 구조 확정

---

## 🎯 왜 메타 인덱스가 먼저인가?

### 문제

```yaml
현재 계획:
  Day 3-5: Knowledge Graph 먼저
  Day 6-7: Guardian Memory
  Day 10-12: Modular RAG

문제:
  • Knowledge Graph 메타데이터 설계
  • Memory 메타데이터 설계
  • Modular RAG 메타데이터 설계
  
  → 각각 다르게 설계하면?
  → Layer 간 불일치! 🚨
  → 나중에 통합 불가능!
```

### 해결

```yaml
올바른 순서:
  
  Step 0: 메타 인덱스 설계 (먼저!)
    • 모든 Layer가 공유할 필드
    • Layer별 전용 필드
    • 매핑 규칙
  
  Step 1: Schema Registry 구축
    • schema_registry.yaml
    • Contract Tests
  
  Step 2-4: Layer 순차 구현
    • 모두 Schema Registry 준수
    • 호환성 보장
```

---

## 📊 전체 RAG 시스템 구조

### 5개 Collection

```yaml
1. canonical_index (Canonical Index)
   목적: 업데이트용, 정규화 청크
   
2. projected_index (Projected Index)
   목적: 검색용, Agent별 투영 청크
   
3. knowledge_graph (Knowledge Graph - Neo4j)
   목적: 패턴 관계, 조합 발견
   
4. query_memory (QueryMemory)
   목적: 순환 감지
   
5. goal_memory (GoalMemory)
   목적: 목표 정렬

+ system_knowledge (System RAG, 향후)
   목적: umis.yaml 도구 검색
```

---

## 🔑 통합 메타데이터 스키마

### Core Fields (모든 Collection 공유)

```yaml
core_metadata:
  # === Identity ===
  source_id:
    type: string
    required: true
    description: "사례/패턴 고유 ID"
    example: "baemin_case"
    used_by: [canonical, projected, graph]
  
  domain:
    type: enum
    values: [case_study, pattern, framework, tool]
    required: true
    used_by: [canonical, projected, graph, system]
  
  version:
    type: string
    required: true
    description: "데이터 버전"
    example: "6.3.0-alpha"
    used_by: [all]
  
  # === Quality ===
  quality_grade:
    type: enum
    values: [A, B, C, D]
    required: false
    description: "Guardian 평가 등급"
    used_by: [canonical, projected]
  
  validation_status:
    type: enum
    values: [verified, pending, failed]
    required: false
    used_by: [canonical, projected]
  
  # === Timestamps ===
  created_at:
    type: datetime
    required: true
    used_by: [all]
  
  updated_at:
    type: datetime
    required: true
    used_by: [all]
```

---

### Layer 1: Canonical Index

```yaml
canonical_metadata:
  # Core
  - source_id
  - domain
  - version
  - quality_grade
  - validation_status
  - created_at
  - updated_at
  
  # Canonical 전용
  content_type:
    type: enum
    values: [normalized_full]
    description: "정규화된 완전 청크"
  
  sections:
    type: object
    description: "Agent별 섹션 인덱스"
    structure:
      observer: {start: int, end: int}
      explorer: {start: int, end: int}
      quantifier: {start: int, end: int}
      validator: {start: int, end: int}
      guardian: {start: int, end: int}
  
  total_tokens:
    type: int
    description: "총 토큰 수"
  
  projection_history:
    type: array
    description: "투영 이력"
    items:
      - timestamp: datetime
        projected_count: int
        method: "rule / llm"

예시:
  source_id: "baemin_case"
  domain: "case_study"
  version: "6.3.0-alpha"
  content_type: "normalized_full"
  sections:
    observer: {start: 0, end: 150}
    explorer: {start: 152, end: 450}
    quantifier: {start: 452, end: 600}
  total_tokens: 1500
```

---

### Layer 1: Projected Index

```yaml
projected_metadata:
  # Core
  - source_id
  - domain
  - version
  - quality_grade
  - validation_status
  - created_at
  - updated_at
  
  # Projected 전용
  agent_view:
    type: enum
    values: [observer, explorer, quantifier, validator, guardian]
    required: true
    description: "어느 Agent용인가"
  
  canonical_id:
    type: string
    required: true
    description: "원본 Canonical 청크 ID"
  
  projection_method:
    type: enum
    values: [rule, llm]
    description: "투영 방법"
  
  # Agent별 전용 (동적)
  {agent}_*:
    description: "각 Agent 전용 메타데이터"
    examples:
      explorer_pattern_id: string
      explorer_csf: array
      explorer_difficulty: enum
      
      quantifier_metrics: array
      quantifier_formula: string
      
      observer_patterns: array
      observer_dynamics: string

예시:
  source_id: "baemin_case"
  domain: "case_study"
  agent_view: "explorer"
  canonical_id: "canonical_baemin"
  projection_method: "rule"
  explorer_pattern_id: "platform_business_model"
  explorer_csf: ["양측확보", "밀도전략"]
```

---

### Layer 3: Knowledge Graph (Neo4j)

```yaml
graph_node_metadata:
  # Core
  - source_id
  - domain
  - version
  
  # Graph 전용
  node_type:
    type: enum
    values: [pattern, case, agent_output]
    required: true
  
  pattern_id:
    type: string
    description: "패턴 ID (Layer 1의 explorer_pattern_id 매핑)"
  
  # Vector 통합
  vector_chunk_id:
    type: string
    description: "Layer 1 청크 참조"

graph_relationship_metadata:
  # Relationship 속성
  relationship_type:
    type: enum
    values: [COMBINES_WITH, COUNTERS, PREREQUISITE]
  
  # Confidence (Multi-Dimensional!)
  confidence:
    similarity:
      method: "vector_embedding"
      value: float (0-1)
    
    coverage:
      method: "distribution"
      value: float (0-1)
    
    validation:
      method: "checklist"
      value: enum (yes/no)
    
    overall:
      value: enum (high/medium/low)
      reasoning: array[string]

예시:
  (platform:Pattern)-[:COMBINES_WITH {
    confidence: {
      similarity: 0.92,
      coverage: 0.10,
      validation: yes,
      overall: high,
      reasoning: ["Best case 0.92", "10% pattern"]
    }
  }]->(subscription:Pattern)
```

---

### Layer 4: Memory Collections

```yaml
query_memory_metadata:
  # Core
  - version
  - created_at
  
  # Memory 전용
  query_text:
    type: string
    required: true
  
  query_embedding:
    type: vector
    dimension: 3072
  
  query_topic:
    type: string
    description: "주제 추출"
  
  repetition_count:
    type: int
    description: "반복 횟수"

goal_memory_metadata:
  # Core
  - version
  - created_at
  
  # Memory 전용
  goal_text:
    type: string
    required: true
  
  goal_embedding:
    type: vector
    dimension: 3072
  
  alignment_score:
    type: float
    description: "현재 쿼리와 목표 정렬도"
```

---

## 🔗 Schema Registry 구조

### schema_registry.yaml

```yaml
# ========================================
# UMIS RAG Schema Registry v1.0
# ========================================

_meta:
  version: "1.0"
  umis_version: "6.3.0-alpha"
  purpose: "모든 RAG Layer 통합 스키마"

# === Core Fields (모든 Layer) ===

core_fields:
  source_id:
    type: string
    required: true
    description: "사례/패턴 고유 ID"
    used_by: [canonical, projected, graph]
    
    examples:
      - "baemin_case"
      - "platform_pattern"
      - "subscription_model"
  
  domain:
    type: enum
    values:
      - case_study
      - pattern
      - framework
      - tool
    required: true
    used_by: [canonical, projected, graph, system]
  
  version:
    type: string
    required: true
    pattern: "\\d+\\.\\d+\\.\\d+(-alpha|beta|rc)?"
    used_by: [all]
  
  quality_grade:
    type: enum
    values: [A, B, C, D]
    required: false
    used_by: [canonical, projected]
  
  created_at:
    type: datetime
    format: "ISO 8601"
    required: true
    used_by: [all]
  
  updated_at:
    type: datetime
    format: "ISO 8601"
    required: true
    used_by: [all]

# === Layer 1: Canonical ===

canonical_fields:
  content_type:
    type: string
    values: [normalized_full]
    required: true
  
  sections:
    type: object
    required: true
    properties:
      observer: {start: int, end: int}
      explorer: {start: int, end: int}
      quantifier: {start: int, end: int}
      validator: {start: int, end: int}
      guardian: {start: int, end: int}
  
  total_tokens:
    type: int
    required: true

# === Layer 1: Projected ===

projected_fields:
  agent_view:
    type: enum
    values: [observer, explorer, quantifier, validator, guardian]
    required: true
  
  canonical_id:
    type: string
    required: true
    description: "원본 Canonical 청크 참조"
  
  projection_method:
    type: enum
    values: [rule, llm]
    required: true
  
  # Agent별 동적 필드
  agent_specific_pattern:
    pattern: "{agent}_*"
    examples:
      - "explorer_pattern_id"
      - "explorer_csf"
      - "quantifier_metrics"
      - "observer_dynamics"

# === Layer 3: Knowledge Graph ===

graph_node_fields:
  node_type:
    type: enum
    values: [pattern, case, agent_output]
    required: true
  
  pattern_id:
    type: string
    description: "패턴 ID"
    mapping:
      from: "projected.explorer_pattern_id"
      to: "graph.pattern_id"
  
  vector_chunk_id:
    type: string
    description: "Layer 1 청크 참조"

graph_relationship_fields:
  relationship_type:
    type: enum
    values: [COMBINES_WITH, COUNTERS, PREREQUISITE]
  
  confidence:
    type: object
    required: true
    properties:
      similarity: float
      coverage: float
      validation: enum [yes, no]
      overall: enum [high, medium, low]
      reasoning: array[string]

# === Layer 4: Memory ===

memory_fields:
  query_text:
    type: string
    required: true
  
  query_embedding:
    type: vector
    dimension: 3072
    required: true
  
  query_topic:
    type: string
  
  repetition_count:
    type: int

# === Field Mappings (Layer 간) ===

field_mappings:
  explorer_pattern_id:
    layer_1_canonical: "sections.explorer"
    layer_1_projected: "explorer_pattern_id"
    layer_3_graph: "pattern_id"
    
    mapping_rule: |
      Layer 1 Projected의 explorer_pattern_id는
      Layer 3 Graph의 pattern_id로 매핑됨
  
  source_id:
    layer_1_canonical: "source_id"
    layer_1_projected: "source_id"
    layer_3_graph: "source_id"
    
    mapping_rule: |
      모든 Layer에서 동일한 이름 사용

# === Validation Rules ===

validation_rules:
  required_core:
    - "모든 청크는 source_id 필수"
    - "모든 청크는 version 필수"
    - "모든 청크는 created_at 필수"
  
  cross_layer:
    - "Projected의 canonical_id는 Canonical에 존재해야 함"
    - "Graph의 vector_chunk_id는 Projected에 존재해야 함"
    - "Graph의 pattern_id는 Projected의 explorer_pattern_id와 매핑"
  
  type_safety:
    - "enum 필드는 정의된 값만"
    - "datetime은 ISO 8601 형식"
    - "float는 0-1 범위 (confidence)"

# === Version Compatibility ===

version_compatibility:
  "1.0":
    layers: [canonical, projected, graph, memory]
    breaking_changes: []
  
  "1.1":
    layers: [canonical, projected, graph, memory, system]
    breaking_changes:
      - "system_rag 추가"
    
    migration:
      - "기존 Collection 영향 없음"
      - "system_knowledge 신규 추가만"

# ========================================
# END
# ========================================
```

---

## 🔧 구현 계획

### Phase 0: Schema Registry (1주) 🔴 최우선!

```yaml
Week 1:
  
  Day 1-2: schema_registry.yaml 작성
    • Core Fields 정의
    • Layer별 Fields 정의
    • Mapping Rules 정의
    • Validation Rules 정의
  
  Day 3-4: Validation 로직
    • schema_validator.py 구현
    • validate_field() 함수
    • check_compatibility() 함수
  
  Day 5: Contract Tests
    • tests/test_schema_contract.py
    • Layer 1 ↔ Layer 3 호환성
    • Canonical ↔ Projected 무손실
  
  Day 6-7: 통합 및 문서화
    • scripts/01_convert_yaml.py 통합
    • 자동 검증 추가
    • 문서화

산출물:
  ✅ schema_registry.yaml
  ✅ schema_validator.py
  ✅ tests/test_schema_contract.py
  ✅ 문서

가치:
  모든 Layer 호환성 보장
  필드 일관성
  안전한 확장
```

---

### Phase 1: Dual-Index (1주)

```yaml
Week 2:
  
  전제:
    Schema Registry 완료 ✅
    → 모든 필드 schema_registry.yaml 준수
  
  Day 1-2: Canonical Index
    • canonical_index Collection
    • Metadata: schema_registry 준수
  
  Day 3-4: Hybrid Projection
    • projection_rules.yaml
    • Metadata: schema_registry 준수
  
  Day 5: Projected Index
    • projected_index Collection
    • Metadata: schema_registry 준수
  
  Day 6-7: 테스트
    • Contract Test 통과?
    • 호환성 확인

산출물:
  ✅ canonical_index/ (data/chroma/)
  ✅ projected_index/ (data/chroma/)
  ✅ projection_rules.yaml
  ✅ Contract Test 통과

검증:
  schema_registry 100% 준수
```

---

### Phase 2: Knowledge Graph (1주)

```yaml
Week 3:
  
  전제:
    Schema Registry 완료 ✅
    Dual-Index 완료 ✅
    
  Day 1-2: Neo4j 설정
    • Docker Neo4j
    • 노드 스키마: schema_registry 준수
    • 관계 스키마: confidence 포함
  
  Day 3-4: 패턴 관계 정의
    • pattern_relationships.yaml
    • 45개 관계
    • Multi-Dimensional Confidence
  
  Day 5-7: Graph+Vector Hybrid
    • Graph 검색 API
    • Vector 통합 (Projected Index 참조)
    • Explorer 통합

산출물:
  ✅ Neo4j DB
  ✅ pattern_relationships.yaml
  ✅ graph_search.py

검증:
  schema_registry field_mappings 준수
  pattern_id 매핑 정확
```

---

### Phase 3: Memory (1주)

```yaml
Week 4:
  
  전제:
    Schema Registry 완료 ✅
  
  Day 1-3: QueryMemory
    • query_memory Collection
    • Metadata: schema_registry 준수
    • 순환 감지 로직
  
  Day 4-6: GoalMemory
    • goal_memory Collection
    • Metadata: schema_registry 준수
    • 정렬도 측정
  
  Day 7: Guardian 통합
    • Memory-RAG + LLM Hybrid
    • 자동 경고

산출물:
  ✅ query_memory Collection
  ✅ goal_memory Collection
  ✅ guardian/memory.py

검증:
  schema_registry 준수
```

---

## 🎯 수정된 구현 순서

```yaml
올바른 순서:

Week 0 (준비):
  ✅ v6.3.0-alpha (현재)

Week 1 (기반):
  🔴 Schema Registry ⭐ 최우선!

Week 2 (Layer 1):
  🔴 Dual-Index

Week 3 (Layer 3):
  🔴 Knowledge Graph

Week 4 (Layer 4):
  🔴 Memory

Week 5-6 (Layer 2):
  🟡 Guardian Meta-RAG

총: 6주
```

**vs 원래 계획:**

```yaml
원래:
  Day 3-5: Knowledge Graph 먼저
  
문제:
  Schema 없이 시작
  → 나중에 불일치

수정:
  Week 1: Schema Registry 먼저!
  → 모든 Layer 호환 보장
```

---

## 🎯 최종 권장사항

**즉시 시작: Schema Registry!**

```yaml
우선순위: 🔴 P0 (모든 것의 기반)

이유:
  1. 모든 Layer가 공유
  2. 나중에 수정 어려움
  3. 호환성의 핵심

다음:
  schema_registry.yaml 작성 시작?
```

**당신의 지적이 완벽했습니다!** ✨


