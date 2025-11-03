# schema_registry.yaml 작성 가이드

**목적:** Schema Registry가 무엇을 담아야 하는지 명확히 하기

---

## 🎯 schema_registry.yaml이란?

### 역할

```yaml
schema_registry.yaml = "RAG 시스템의 헌법"

모든 Layer가:
  1. 어떤 필드를 사용하는가
  2. 각 필드의 타입은 무엇인가
  3. 필드가 어떻게 매핑되는가
  4. 어떻게 검증하는가

→ 단일 진실의 원천!
```

**비유:**
```yaml
schema_registry.yaml = 건축 도면
  • 모든 방(Layer)의 구조
  • 전기/수도(필드) 배치
  • 방 간 연결(매핑)
  • 안전 기준(검증)

Layer 구현 = 시공
  • 도면 따라 짓기
  • 임의 변경 불가
  • 검사 통과 필수
```

---

## 📋 무엇을 담는가?

### 1. Core Fields (모든 Layer 공유)

```yaml
목적:
  모든 Collection에 반드시 있어야 하는 필드

포함 기준:
  ✅ 모든 Layer에서 사용
  ✅ Layer 간 연결에 필요
  ✅ 추적/검증에 필수

예시:
  source_id:
    type: string
    required: true
    description: "사례/패턴 고유 ID"
    used_by: [canonical, projected, graph]
    why: "Layer 간 동일 데이터 추적"
  
  version:
    type: string
    required: true
    description: "데이터 버전"
    used_by: [all]
    why: "버전 호환성 확인"
  
  created_at:
    type: datetime
    required: true
    used_by: [all]
    why: "생성 시점 추적"

포함하지 않을 것:
  ❌ Layer 전용 필드 (다음 섹션)
  ❌ 옵션 필드 (일부만 사용)
```

---

### 2. Layer-Specific Fields (Layer별 전용)

```yaml
목적:
  각 Layer만 사용하는 고유 필드

포함 기준:
  ✅ 특정 Layer만 사용
  ✅ 다른 Layer와 공유 안 함
  ✅ Layer 동작에 필수

Layer 1 Canonical:
  sections:
    type: object
    description: "Agent별 섹션 인덱스"
    why: "Canonical만 섹션 분할 정보 보유"
  
  total_tokens:
    type: int
    why: "Canonical만 전체 토큰 관리"

Layer 1 Projected:
  agent_view:
    type: enum
    values: [observer, explorer, ...]
    required: true
    why: "Projected만 Agent 구분"
  
  canonical_id:
    type: string
    required: true
    why: "Projected만 원본 참조"
  
  explorer_pattern_id:
    type: string
    why: "Explorer Agent 전용"

Layer 3 Graph:
  node_type:
    type: enum
    values: [pattern, case, agent_output]
    why: "Graph만 노드 타입 구분"
  
  pattern_id:
    type: string
    why: "Graph에서 패턴 노드 식별"

Layer 4 Memory:
  query_text:
    type: string
    why: "Memory만 쿼리 저장"
  
  repetition_count:
    type: int
    why: "Memory만 반복 추적"
```

---

### 3. Field Mappings (Layer 간 매핑)

```yaml
목적:
  같은 개념이 Layer마다 다른 이름일 때 매핑

포함 기준:
  ✅ Layer 간 필드명 불일치
  ✅ 하지만 같은 정보
  ✅ 자동 변환 필요

예시 (중요!):
  explorer_pattern_id ↔ pattern_id
  
  문제:
    Layer 1 Projected: explorer_pattern_id
    Layer 3 Graph: pattern_id
    
    → 이름 다름!
  
  매핑:
    explorer_pattern_id:
      layer_1_projected: "explorer_pattern_id"
      layer_3_graph: "pattern_id"
      
      mapping_rule: |
        Projected의 explorer_pattern_id는
        Graph의 pattern_id로 자동 변환
  
  사용:
    # Projected → Graph 전송 시
    graph_pattern_id = map_field(
      "explorer_pattern_id",
      projected.metadata["explorer_pattern_id"],
      from_layer="projected",
      to_layer="graph"
    )
    # → "pattern_id"로 변환됨

포함해야 할 매핑:
  • explorer_pattern_id → pattern_id (Projected → Graph)
  • source_id → source_id (동일, 확인용)
  • ... (필요한 것만)
```

---

### 4. Validation Rules (검증 규칙)

```yaml
목적:
  필드 값의 타당성 검증

포함 기준:
  ✅ 필수 필드 존재 확인
  ✅ 타입 정확성
  ✅ Layer 간 참조 무결성

타입별:
  required_fields:
    - "모든 청크는 source_id 필수"
    - "agent_view는 Projected만 필수"
  
  type_validation:
    - "source_id는 string"
    - "quality_grade는 A/B/C/D만"
    - "created_at은 ISO 8601"
  
  cross_layer:
    - "Projected의 canonical_id는 Canonical에 존재"
    - "Graph의 pattern_id는 Projected의 explorer_pattern_id"
  
  range:
    - "confidence는 0-1"
    - "repetition_count >= 0"
```

---

### 5. Version Compatibility (버전 호환성)

```yaml
목적:
  Schema 변경 시 기존 데이터 호환성

포함 기준:
  ✅ 버전별 변경사항
  ✅ Breaking Changes
  ✅ Migration Path

예시:
  v1.0:
    layers: [canonical, projected, graph, memory]
    fields:
      - source_id
      - domain
      - quality_grade
  
  v1.1:
    layers: [canonical, projected, graph, memory, system]
    
    added_fields:
      - tool_type (system용)
    
    breaking_changes: []
    
    migration:
      - "기존 Collection 영향 없음"
      - "system_knowledge 신규만"
  
  v2.0:
    added_fields:
      - confidence.similarity (graph용)
    
    breaking_changes:
      - "confidence 구조 변경 (숫자 → 객체)"
    
    migration:
      - "Graph relationship 재생성 필요"
      - "Canonical/Projected 영향 없음"
```

---

## 🔍 어떤 기준으로?

### 포함 기준

#### 1. 공통성 (Core Fields)

```yaml
질문:
  이 필드가 모든 Layer에 있는가?

✅ Yes → Core Fields에 추가
  • source_id (모든 곳)
  • version (모든 곳)
  • created_at (모든 곳)

❌ No → Layer-Specific으로
  • sections (Canonical만)
  • agent_view (Projected만)
```

#### 2. 필수성 (Required)

```yaml
질문:
  이 필드 없으면 시스템 작동 불가능?

✅ Yes → required: true
  • source_id (식별 필수)
  • agent_view (Projected 구분 필수)

❌ No → required: false
  • quality_grade (선택)
  • validation_status (선택)
```

#### 3. 매핑 필요성

```yaml
질문:
  Layer마다 이름이 다른가?
  하지만 같은 정보인가?

✅ Yes → Mappings에 추가
  • explorer_pattern_id ↔ pattern_id

❌ No → Mappings 불필요
  • source_id (모든 곳에서 같은 이름)
```

#### 4. 검증 필요성

```yaml
질문:
  이 필드의 값을 검증해야 하는가?

✅ Yes → Validation Rules 추가
  • canonical_id 존재 여부
  • enum 값 범위
  • 참조 무결성

❌ No → 검증 불필요
  • 자유 텍스트 (description 등)
```

---

## 📝 작성 프로세스

### Step 1: Core Fields 추출

```yaml
방법:
  1. 모든 Layer 나열
     • Canonical
     • Projected
     • Graph
     • Memory
  
  2. 각 Layer의 필드 리스트
  
  3. 교집합 찾기
     모든 Layer에 있는 필드
     → Core Fields!

결과:
  source_id: ✅ (모든 곳)
  domain: ✅ (모든 곳)
  version: ✅ (모든 곳)
  agent_view: ❌ (Projected만)
  sections: ❌ (Canonical만)
```

---

### Step 2: Layer-Specific 정의

```yaml
방법:
  1. 각 Layer별로
     Core가 아닌 필드 추출
  
  2. 그 필드가 왜 필요한지 설명
  
  3. 다른 Layer와 충돌 없는지 확인

Canonical:
  sections: {observer: {...}, ...}
  → 왜? 섹션 분할 정보
  → 충돌? Projected는 이미 분할됨, 불필요

Projected:
  agent_view: "explorer"
  → 왜? Agent 구분
  → 충돌? Canonical은 통합, 불필요
  
  canonical_id: "canonical_baemin"
  → 왜? 원본 참조
  → 충돌? Canonical은 자기 자신, 불필요
```

---

### Step 3: Mappings 발견

```yaml
방법:
  1. Layer 간 데이터 흐름 추적
     Projected → Graph 전송?
     
  2. 필드명 비교
     Projected: explorer_pattern_id
     Graph: pattern_id
     
     → 이름 다름!
  
  3. 매핑 규칙 작성
     explorer_pattern_id → pattern_id

주의:
  매핑이 필요한 경우만!
  
  source_id → source_id (같은 이름)
  → 매핑 불필요 (명시만)
```

---

### Step 4: Validation 정의

```yaml
방법:
  1. 각 필드의 제약사항
     source_id: 문자열, 비어있으면 안 됨
     quality_grade: A/B/C/D만
  
  2. Layer 간 참조 규칙
     Projected.canonical_id는 Canonical에 존재?
     Graph.pattern_id는 Projected.explorer_pattern_id?
  
  3. 비즈니스 규칙
     confidence는 0-1
     repetition_count >= 0
```

---

## 🎯 schema_registry.yaml 구조

### 최종 구조

```yaml
# ========================================
# UMIS RAG Schema Registry v1.0
# ========================================

_meta:
  version: "1.0"
  umis_version: "6.3.0-alpha"
  purpose: "모든 RAG Layer 통합 스키마"
  last_updated: "2025-11-02"

# ========================================
# PART 1: Core Fields (모든 Layer)
# ========================================

core_fields:
  source_id:
    type: string
    required: true
    description: "사례/패턴 고유 ID"
    used_by: [canonical, projected, graph]
    examples: ["baemin_case", "platform_pattern"]
    validation:
      - "비어있으면 안 됨"
      - "중복 불가"
  
  domain:
    type: enum
    values: [case_study, pattern, framework, tool]
    required: true
    used_by: [canonical, projected, graph, system]
  
  ... (계속)

# ========================================
# PART 2: Layer-Specific Fields
# ========================================

layer_1_canonical:
  sections:
    type: object
    required: true
    properties:
      observer: {type: object, properties: {start: int, end: int}}
      explorer: {type: object, properties: {start: int, end: int}}
      ...
  
  ... (계속)

layer_1_projected:
  agent_view:
    type: enum
    values: [observer, explorer, quantifier, validator, guardian]
    required: true
  
  ... (계속)

layer_3_graph:
  node_type:
    type: enum
    values: [pattern, case, agent_output]
    required: true
  
  ... (계속)

# ========================================
# PART 3: Field Mappings
# ========================================

field_mappings:
  explorer_pattern_id_to_pattern_id:
    source_layer: "projected"
    source_field: "explorer_pattern_id"
    target_layer: "graph"
    target_field: "pattern_id"
    
    mapping_function: "direct_copy"
    
    example:
      input: {explorer_pattern_id: "platform_business_model"}
      output: {pattern_id: "platform_business_model"}

# ========================================
# PART 4: Validation Rules
# ========================================

validation_rules:
  required_core_fields:
    - rule: "모든 청크는 source_id 필수"
      layers: [canonical, projected, graph]
      check: "field_exists('source_id')"
  
  type_validation:
    - rule: "quality_grade는 A/B/C/D만"
      field: "quality_grade"
      check: "value in ['A', 'B', 'C', 'D']"
  
  cross_layer_integrity:
    - rule: "Projected.canonical_id는 Canonical에 존재"
      check: "exists_in_collection('canonical', canonical_id)"
  
  ... (계속)

# ========================================
# PART 5: Version Compatibility
# ========================================

version_compatibility:
  "1.0":
    supported_layers: [canonical, projected, graph, memory]
    core_fields: [source_id, domain, version, ...]
  
  "1.1":
    supported_layers: [canonical, projected, graph, memory, system]
    added_fields: [tool_type]
    breaking_changes: []
```

---

## 🔍 작성 기준 상세

### 기준 1: 필드 추가 여부

```yaml
질문 체크리스트:
  
  1. 이 필드가 모든 Layer에 있는가?
     → Yes: Core Fields
     → No: 다음 질문
  
  2. 이 필드가 특정 Layer에만 있는가?
     → Yes: Layer-Specific
     → No: 제외 (불필요)
  
  3. 이 필드가 Layer 작동에 필수인가?
     → Yes: required: true
     → No: required: false
  
  4. 이 필드가 다른 Layer와 관련 있는가?
     → Yes: Mappings 추가
     → No: Mappings 불필요
  
  5. 이 필드의 값을 검증해야 하는가?
     → Yes: Validation Rules 추가
     → No: 검증 불필요
```

---

### 기준 2: 타입 정의

```yaml
타입 선택:
  
  string:
    언제: 자유 텍스트
    예시: source_id, description
  
  enum:
    언제: 정해진 값만
    예시: domain, quality_grade, agent_view
    필수: values 리스트
  
  int:
    언제: 정수
    예시: repetition_count, total_tokens
  
  float:
    언제: 실수
    예시: confidence, alignment_score
    범위: 0-1 (보통)
  
  datetime:
    언제: 시간
    예시: created_at, updated_at
    형식: ISO 8601
  
  object:
    언제: 구조화된 데이터
    예시: sections, confidence
    필수: properties 정의
  
  array:
    언제: 리스트
    예시: csf, reasoning
    필수: items 타입
  
  vector:
    언제: 임베딩
    예시: query_embedding
    필수: dimension
```

---

### 기준 3: 매핑 규칙

```yaml
매핑이 필요한 경우:
  
  1. 같은 정보, 다른 이름
     Projected: explorer_pattern_id
     Graph: pattern_id
     → 매핑 필요!
  
  2. 같은 이름, 같은 정보
     Projected: source_id
     Graph: source_id
     → 매핑 불필요 (명시만)
  
  3. 변환 로직
     단순 복사: "direct_copy"
     계산: "calculate"
     조건부: "conditional"

매핑 함수:
  direct_copy:
    A → B (그대로)
  
  prefix_remove:
    explorer_pattern_id → pattern_id
    (explorer_ 제거)
  
  conditional:
    if condition: A → B
    else: A → C
```

---

### 기준 4: 검증 수준

```yaml
검증 강도:
  
  Level 1: 존재 확인
    - "필드 있는가?"
    - 빠름
  
  Level 2: 타입 확인
    - "string인가?"
    - 빠름
  
  Level 3: 값 확인
    - "A/B/C/D만인가?"
    - 빠름
  
  Level 4: 참조 확인
    - "canonical_id가 실제 존재?"
    - 느림 (DB 쿼리)
  
  Level 5: 비즈니스 로직
    - "confidence 3개 차원 모두?"
    - 느림 (복잡한 로직)

포함 기준:
  Level 1-3: 항상 포함
  Level 4-5: 중요한 것만
```

---

## 💡 실용적 작성 팁

### Tip 1: 최소주의

```yaml
원칙:
  필요한 것만!

나쁨:
  모든 가능한 필드를 미리 정의
  → 복잡, 관리 어려움

좋음:
  현재 사용하는 필드만
  → 단순, 명확
  
  나중에 추가:
    version 1.1로 확장
    → 점진적
```

---

### Tip 2: 예시 필수

```yaml
모든 필드에 예시:
  
  source_id:
    type: string
    examples:
      - "baemin_case"
      - "platform_pattern"
      - "subscription_model"
  
왜:
  AI가 이해하기 쉬움
  사람도 이해하기 쉬움
  오해 방지
```

---

### Tip 3: Why 설명

```yaml
모든 필드에 이유:
  
  canonical_id:
    type: string
    required: true
    why: "Projected가 원본 Canonical 참조 위해"
  
왜:
  나중에 "왜 이 필드?"
  → 설명 있으면 명확
  → 삭제 여부 판단 가능
```

---

## 🎯 최종 체크리스트

### schema_registry.yaml 작성 전 확인

```yaml
✅ 모든 Layer 이해했는가?
   • Canonical
   • Projected
   • Graph
   • Memory
   • (System)

✅ 각 Layer의 필드 조사했는가?
   • META_INDEX_DESIGN.md 확인
   • umis_rag_architecture_v2.0.yaml 확인

✅ Core Fields 식별했는가?
   • 모든 Layer 공통
   • 최소 5-7개

✅ Layer 간 매핑 파악했는가?
   • explorer_pattern_id → pattern_id
   • 기타

✅ 검증 규칙 정의했는가?
   • 필수 필드
   • 타입
   • 참조 무결성
```

---

## 🚀 작성 시작

**준비 완료되었으면:**

```yaml
다음 단계:
  1. schema_registry.yaml 생성
  2. PART 1: Core Fields부터
  3. 예시 포함
  4. 점진적 확장
```

**시작하시겠어요?** 🚀

