# Schema-Registry & Contract-Test 검토

**문제:** 4-Layer가 공통 필드 공유 → 불일치 위험

---

## 🔍 문제 상황

### Case 1: 메타데이터 필드 불일치

```yaml
시나리오:
  Layer 1 (Modular RAG):
    metadata:
      source_id: "baemin_case"
      explorer_pattern_id: "platform_business_model"
  
  Layer 3 (Knowledge Graph):
    필요한 필드:
      source_id: "baemin_case"  ← 같음
      pattern_id: "platform_business_model"  ← 다름!
  
  문제:
    • Layer 1: explorer_pattern_id
    • Layer 3: pattern_id
    
    → 필드명 불일치!
    → Graph 쿼리 실패! 🚨
```

### Case 2: 필드 추가 시 파급 효과

```yaml
시나리오:
  "confidence_score 필드 추가"
  
  영향:
    • Layer 1: Canonical/Projected 둘 다?
    • Layer 2: Meta-RAG에서 사용?
    • Layer 3: Graph에 저장?
    • Layer 4: Memory에 기록?
  
  문제:
    • 어디에 추가해야 하나?
    • 누락하면?
    • 일관성 보장?
    
    → 판단 어려움! 🚨
```

### Case 3: 스키마 변경

```yaml
시나리오:
  "explorer_csf → explorer_success_factors"
  (필드명 변경)
  
  영향:
    • Canonical: 변경
    • Projected: 변경
    • projection_rules.yaml: 변경
    • Layer 3 Graph: 변경
    • Layer 4 Memory: 변경
    • 기존 데이터: 마이그레이션?
  
  문제:
    • 5곳 동기화
    • 기존 5,000개 청크?
    • 버전 호환성?
    
    → 대공사! 🚨
```

---

## 💡 해결책

### Option 1: Schema Registry (중앙 집중)

```yaml
# schema_registry.yaml

version: "1.0"

core_fields:
  source_id:
    type: string
    required: true
    description: "사례 고유 ID"
    used_by: [layer1, layer2, layer3, layer4]
  
  domain:
    type: enum
    values: [case_study, pattern, framework]
    required: true
    used_by: [layer1, layer3]
  
  quality_grade:
    type: enum
    values: [A, B, C, D]
    required: false
    used_by: [layer1, layer2, layer4]

layer_specific_fields:
  layer1_modular:
    explorer_pattern_id:
      type: string
      required: true
      description: "Explorer 패턴 ID"
      alias: ["pattern_id"]  # ← Layer 3에서 이 이름 사용
  
  layer3_graph:
    pattern_id:
      type: string
      source: "layer1.explorer_pattern_id"  # ← 매핑!
      
  layer4_memory:
    query_topic:
      type: string
      required: true

schema_version_compatibility:
  "1.0": [layer1, layer2, layer3, layer4]
  "1.1": [layer1, layer2, layer3, layer4]  # 하위 호환
```

**사용:**
```python
from umis_rag.schema import SchemaRegistry

registry = SchemaRegistry()

# 필드 검증
registry.validate_field("source_id", "baemin_case")  # ✅

# 필드 매핑
layer3_field = registry.map_field(
    from_layer="layer1",
    field="explorer_pattern_id",
    to_layer="layer3"
)
# → "pattern_id" 반환

# 호환성 확인
registry.is_compatible(
    schema_version="1.0",
    layer="layer3"
)  # → True
```

**장점:**
```yaml
✅ 중앙 집중: 모든 필드 한 곳에
✅ 매핑: Layer 간 필드 자동 변환
✅ 검증: 타입 체크
✅ 호환성: 버전 관리
✅ 문서화: 자동 (YAML이 문서)
```

**단점:**
```yaml
⚠️ 초기 설정: schema_registry.yaml 작성
⚠️ 오버헤드: 검증 로직
```

---

### Option 2: Contract Tests (행동 검증)

```python
# tests/test_schema_contract.py

def test_layer1_to_layer3_compatibility():
    """
    Layer 1 메타데이터가 Layer 3에서 사용 가능한가?
    """
    
    # Layer 1 청크 생성
    chunk = create_explorer_chunk("baemin_case")
    
    # Layer 3에서 필요한 필드 확인
    assert 'source_id' in chunk.metadata
    assert 'explorer_pattern_id' in chunk.metadata
    
    # Graph 쿼리 가능한가?
    graph_node = map_to_graph(chunk.metadata)
    assert graph_node.pattern_id == chunk.metadata['explorer_pattern_id']

def test_canonical_to_projected_projection():
    """
    Canonical → Projected 투영이 정보 손실 없는가?
    """
    
    canonical = create_canonical("baemin_case")
    projected = project_to_agents(canonical)
    
    # 모든 Agent 생성되었나?
    assert len(projected) == 6
    
    # 핵심 정보 보존?
    assert "해지율" in projected['quantifier'].content
    assert "플랫폼" in projected['explorer'].content

def test_schema_version_compatibility():
    """
    스키마 v1.0 → v1.1 호환되는가?
    """
    
    # v1.0 청크
    chunk_v1 = load_chunk(schema_version="1.0")
    
    # v1.1 시스템에서 사용 가능?
    result = process_with_v1_1(chunk_v1)
    assert result is not None
```

**장점:**
```yaml
✅ 실용적: 실제 작동 검증
✅ 자동: CI/CD 통합
✅ 안전: 변경 시 자동 체크
✅ 문서화: 테스트 = 명세
```

**단점:**
```yaml
⚠️ 사후 검증: 문제 발생 후 발견
⚠️ 커버리지: 모든 케이스 어려움
```

---

### Option 3: Pydantic Models (타입 강제)

```python
# umis_rag/schema/models.py

from pydantic import BaseModel, Field
from typing import Literal

class CoreMetadata(BaseModel):
    """모든 Layer 공통"""
    source_id: str = Field(..., description="사례 ID")
    domain: Literal["case_study", "pattern"] = Field(...)
    quality_grade: Literal["A", "B", "C", "D"] | None = None

class ExplorerMetadata(BaseModel):
    """Explorer 전용"""
    explorer_pattern_id: str = Field(..., alias="pattern_id")
    explorer_csf: list[str] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True  # pattern_id → explorer_pattern_id

class Layer1Metadata(CoreMetadata, ExplorerMetadata):
    """Layer 1 전체"""
    pass

# 사용
metadata = Layer1Metadata(
    source_id="baemin_case",
    pattern_id="platform"  # ← alias 작동!
)

metadata.explorer_pattern_id  # → "platform" ✅
```

**장점:**
```yaml
✅ 타입 안전: 컴파일 타임 체크
✅ 자동 완성: IDE 지원
✅ 변환: alias로 필드 매핑
✅ 검증: 자동 (Pydantic)
```

**단점:**
```yaml
⚠️ Python 전용: YAML에서 사용 어려움
⚠️ 엄격함: 유연성 ↓
```

---

## 🎯 최종 추천: 3-Layer 방어

### 조합: Registry + Contract + Pydantic

```yaml
Layer 1: Schema Registry (설계)
  • schema_registry.yaml
  • 모든 필드 정의
  • Layer 간 매핑
  • 버전 호환성

Layer 2: Pydantic Models (구현)
  • Python 타입 강제
  • 자동 검증
  • alias 매핑

Layer 3: Contract Tests (검증)
  • 실제 작동 확인
  • CI/CD 통합
  • 회귀 방지
```

**실제 사용:**

```python
# 1. Schema Registry (설계 단계)
# schema_registry.yaml 작성

# 2. Pydantic (개발 단계)
from umis_rag.schema import Layer1Metadata

metadata = Layer1Metadata(
    source_id="baemin",
    pattern_id="platform"  # Pydantic이 검증!
)

# 3. Contract Test (배포 단계)
# tests/test_schema_contract.py
# → CI/CD에서 자동 실행
```

**효과:**
```yaml
설계: schema_registry.yaml
  → 중앙 집중, 문서화

개발: Pydantic
  → 타입 안전, IDE 지원

검증: Contract Tests
  → 실제 작동 보장

→ 3중 방어! 🛡️
```

---

## 💡 구현 우선순위

### Phase 1 (즉시): Pydantic Models

```yaml
이유:
  • 가장 쉬움
  • 즉시 효과
  • metadata_schema.py 이미 있음!

구현:
  umis_rag/core/metadata_schema.py 활성화
  → 이미 작성되어 있음! ✅

소요: 1일
```

### Phase 2 (1주): Schema Registry

```yaml
이유:
  • 중앙 집중 필요
  • Layer 간 매핑

구현:
  schema_registry.yaml 작성

소요: 2일
```

### Phase 3 (2주): Contract Tests

```yaml
이유:
  • 안정성 보장
  • CI/CD

구현:
  tests/test_schema_contract.py

소요: 3일
```

---

## 🎯 2번 최종 결정

**3-Layer 방어 채택!**

```yaml
우선순위:
  🔴 P0: Pydantic (즉시)
  🔴 P0: Schema Registry (1주)
  🟡 P1: Contract Tests (2주)

효과:
  ✅ 필드 일관성
  ✅ 타입 안전성
  ✅ 버전 관리
  ✅ Layer 간 호환

구현:
  • metadata_schema.py 활성화
  • schema_registry.yaml 작성
  • Contract Tests 추가
```

**다음:** 3번 (Routing YAML) 검토할까요? 🚀

