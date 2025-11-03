# Dual-Index 구현 계획 (Week 2)

**날짜:** 2025-11-02  
**버전:** v3.0 (전문가 피드백 반영)  
**기간:** 7일

---

## 🎯 목표

### Dual-Index + TTL 구현

```yaml
현재 (v6.3.0-alpha):
  • explorer_knowledge_base (54 chunks)
  • Pre-Projection (Agent별 분리)

목표 (Week 2):
  • canonical_index (54 chunks)
  • projected_index (TTL + 온디맨드)
  • Hybrid Projection (90% rule + 10% LLM)

강화 (v3.0):
  • ID: CAN-xxx, PRJ-xxx
  • Lineage 추적
  • anchor_path + content_hash
  • TTL 24시간
  • Overlay 메타 (선반영)
```

---

## 📋 Day 1-2: Canonical Index

### 목표

```yaml
기존:
  data/chunks/explorer_business_models.jsonl (31개)
  data/chunks/explorer_disruption_patterns.jsonl (23개)
  → 분리되어 있음

변환:
  → canonical_index Collection
  → 정규화된 단일 청크
  → ID: CAN-xxx
  → sections: anchor_path + hash
```

### 작업

#### 1. Canonical 청크 생성 로직

```python
# scripts/canonical_builder.py (신규)

import hashlib
import yaml
from umis_rag.core.schema import SchemaRegistry

class CanonicalBuilder:
    def __init__(self):
        self.schema = SchemaRegistry()
    
    def build_canonical_chunk(self, source_data):
        """
        사례 → Canonical 청크
        """
        
        # ID 생성
        canonical_id = generate_id("CAN", source_data['id'])
        
        # Sections with anchor+hash
        sections = []
        for agent in ['observer', 'explorer', 'quantifier', 'validator', 'guardian']:
            section_data = extract_agent_section(source_data, agent)
            
            if section_data:
                sections.append({
                    'agent_view': agent,
                    'anchor_path': f"{source_data['pattern_id']}.{agent}_section",
                    'content_hash': hashlib.sha256(section_data.encode()).hexdigest(),
                    'span_hint': {
                        'paragraphs': '...',
                        'tokens': len(section_data.split())
                    }
                })
        
        # Lineage
        lineage = {
            'from': source_data['id'],  # YAML 원본
            'via': [],  # 최초 생성
            'evidence_ids': [],
            'created_by': {
                'agent': 'system',
                'overlay_layer': 'core',
                'tenant_id': None
            }
        }
        
        # Canonical Chunk
        return {
            'id': canonical_id,
            'canonical_chunk_id': canonical_id,
            'source_id': source_data['id'],
            'domain': source_data['domain'],
            'version': '6.3.0-alpha',
            'content_type': 'normalized_full',
            'sections': sections,
            'total_tokens': calculate_tokens(source_data['content']),
            'lineage': lineage,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'content': source_data['content']  # 전체 내용
        }
```

#### 2. Chroma Collection 생성

```python
# canonical_index Collection 생성
client = chromadb.PersistentClient(path="data/chroma")

canonical_collection = client.create_collection(
    name="canonical_index",
    metadata={
        "hnsw:space": "cosine",
        "version": "1.0",
        "architecture": "v3.0"
    }
)
```

#### 3. 기존 54개 사례 변환

```bash
# 실행
python scripts/build_canonical_index.py

# 결과
data/chroma/canonical_index/
  • 54 documents
  • ID: CAN-xxx
  • sections: anchor+hash
  • Lineage 포함
```

### 산출물

```yaml
Day 1-2:
  ✅ scripts/canonical_builder.py
  ✅ data/chroma/canonical_index/ (54 docs)
  ✅ ID: CAN-xxx
  ✅ sections: anchor_path + hash
  ✅ Lineage 추적
```

---

## 📋 Day 3-4: Hybrid Projection

### 목표

```yaml
Canonical → Projected 자동 변환
  • 90% projection_rules.yaml
  • 10% LLM 판단
  • LLM 로그 저장
```

### 작업

#### 1. projection_rules.yaml 작성

```yaml
# projection_rules.yaml (신규)

rules:
  churn_rate:
    agents: [explorer, quantifier, guardian]
    reason: "구독 모델 평가/계산/검증에 필요"
    learned: false
  
  market_size:
    agents: [quantifier]
    reason: "시장 규모 계산"
    learned: false
  
  competitive_structure:
    agents: [observer, explorer]
    reason: "구조 관찰 + 기회 발굴"
    learned: false
  
  # ... (패턴 발견 시 자동 추가)

coverage: "예상 90%"
```

#### 2. HybridProjector 구현

```python
# umis_rag/projection/hybrid_projector.py (신규)

class HybridProjector:
    def __init__(self):
        self.rules = load_yaml('projection_rules.yaml')
        self.llm = ChatOpenAI()
        self.log = []
    
    def project(self, canonical_chunk):
        """
        Canonical → Projected (6개)
        """
        projected_chunks = []
        
        for agent in ['observer', 'explorer', 'quantifier', 'validator', 'guardian']:
            
            # Step 1: Rule-based (90%)
            section_data = self.apply_rules(canonical_chunk, agent)
            
            # Step 2: LLM (10%, 규칙 없을 때)
            if section_data is None:
                section_data = self.llm_decide(canonical_chunk, agent)
                
                # Log
                self.log.append({
                    'field': canonical_chunk['source_id'],
                    'agent': agent,
                    'method': 'llm',
                    'decision': section_data is not None,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 3: Projected 청크 생성
            if section_data:
                projected = self.create_projected(
                    canonical_chunk,
                    agent,
                    section_data
                )
                projected_chunks.append(projected)
        
        # Save log
        self.save_log()
        
        return projected_chunks
    
    def create_projected(self, canonical, agent, section_data):
        """
        Projected 청크 생성 (schema 준수!)
        """
        projected_id = generate_id("PRJ", f"{canonical['source_id']}-{agent}")
        
        return {
            'projected_chunk_id': projected_id,
            'source_id': canonical['source_id'],
            'agent_view': agent,
            'canonical_chunk_id': canonical['canonical_chunk_id'],
            'projection_method': 'rule',  # or 'llm'
            'domain': canonical['domain'],
            'version': canonical['version'],
            
            # v3.0: TTL
            'materialization': {
                'strategy': 'on_demand',
                'cache_ttl_hours': 24,
                'persist_profile': None,
                'last_materialized_at': datetime.now().isoformat(),
                'access_count': 0
            },
            
            # Lineage
            'lineage': {
                'from': canonical['canonical_chunk_id'],
                'via': [
                    {
                        'step': 1,
                        'action': 'projection',
                        'rule_id': 'RULE-...',
                        'chunk_id': projected_id
                    }
                ],
                'evidence_ids': [canonical['canonical_chunk_id']],
                'created_by': {
                    'agent': 'system',
                    'overlay_layer': 'core',
                    'tenant_id': None
                }
            },
            
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'content': section_data  # Agent별 섹션만
        }
```

### 산출물

```yaml
Day 3-4:
  ✅ projection_rules.yaml (초기 규칙)
  ✅ umis_rag/projection/hybrid_projector.py
  ✅ llm_projection_log.jsonl (로그)
  ✅ 테스트 통과
```

---

## 📋 Day 5: Projected Index

### 목표

```yaml
Canonical → Hybrid Projection → Projected Index
  • 54개 → 324개 (54 × 6 agents)
  • TTL + 온디맨드
  • ID: PRJ-xxx
  • Lineage 추적
```

### 작업

#### projected_index Collection 생성

```python
projected_collection = client.create_collection(
    name="projected_index",
    metadata={
        "hnsw:space": "cosine",
        "version": "1.0",
        "architecture": "v3.0",
        "materialization": "on_demand"
    }
)

# 투영 실행
for canonical in canonical_collection.get()['documents']:
    projected_chunks = hybrid_projector.project(canonical)
    
    # 온디맨드: 지금은 생성만, 실제 저장은 첫 접근 시
    # 하지만 초기 구축은 전체 생성
    projected_collection.add(
        documents=[p['content'] for p in projected_chunks],
        metadatas=projected_chunks,
        ids=[p['projected_chunk_id'] for p in projected_chunks]
    )
```

### 산출물

```yaml
Day 5:
  ✅ data/chroma/projected_index/ (324 docs)
  ✅ ID: PRJ-xxx
  ✅ TTL 메타데이터
  ✅ Lineage 포함
```

---

## 📋 Day 6-7: 통합 및 테스트

### Contract Tests

```python
# tests/test_schema_contract.py (신규)

def test_canonical_schema():
    """Canonical이 schema 준수?"""
    chunk = get_canonical_chunk()
    
    # ID 네임스페이스
    assert chunk['canonical_chunk_id'].startswith('CAN-')
    
    # Lineage 존재
    assert 'lineage' in chunk
    assert 'from' in chunk['lineage']
    
    # sections: anchor+hash
    for section in chunk['sections']:
        assert 'anchor_path' in section
        assert 'content_hash' in section

def test_projected_schema():
    """Projected가 schema 준수?"""
    chunk = get_projected_chunk()
    
    # ID
    assert chunk['projected_chunk_id'].startswith('PRJ-')
    
    # Canonical 참조
    assert chunk['canonical_chunk_id'].startswith('CAN-')
    
    # TTL
    assert 'materialization' in chunk
    assert chunk['materialization']['strategy'] in ['on_demand', 'persistent']
    
    # Lineage
    assert chunk['lineage']['from'] == chunk['canonical_chunk_id']

def test_canonical_to_projected():
    """Canonical → Projected 정보 손실 없음?"""
    canonical = get_canonical_chunk()
    projected = get_projected_chunks(canonical['canonical_chunk_id'])
    
    # 모든 Agent 생성?
    assert len(projected) == 6
    
    # Lineage 연결?
    for p in projected:
        assert p['lineage']['from'] == canonical['canonical_chunk_id']
    
    # 정보 보존?
    # ... (상세 검증)
```

### Explorer 통합

```python
# umis_rag/agents/explorer.py 업데이트

class Explorer:
    def __init__(self):
        # Projected Index 사용 (검색용!)
        self.vectorstore = Chroma(
            collection_name="projected_index",
            ...
        )
    
    def search_patterns(self, triggers):
        """패턴 검색"""
        results = self.vectorstore.search(
            query=triggers,
            filter={
                'agent_view': 'explorer',
                'materialization.strategy': 'on_demand'  # TTL 기반
            },
            k=5
        )
        
        # 접근 카운트 업데이트 (프로파일링)
        for result in results:
            update_access_count(result.metadata['projected_chunk_id'])
        
        return results
```

### 산출물

```yaml
Day 6-7:
  ✅ tests/test_schema_contract.py (통과!)
  ✅ Explorer 통합
  ✅ 검색 작동 확인
  ✅ Lineage 추적 테스트
```

---

## 🔧 구현 파일

### 신규 파일 (7개)

```yaml
1. scripts/build_canonical_index.py
   → Canonical Index 구축

2. scripts/build_projected_index.py
   → Projected Index 구축 (TTL)

3. umis_rag/projection/hybrid_projector.py
   → Hybrid Projection 로직

4. umis_rag/core/schema.py
   → SchemaRegistry 로더

5. projection_rules.yaml
   → 규칙 기반 (90%)

6. llm_projection_log.jsonl
   → LLM 판단 로그

7. tests/test_schema_contract.py
   → Contract Tests
```

### 수정 파일 (3개)

```yaml
1. umis_rag/agents/explorer.py
   → Projected Index 사용

2. scripts/01_convert_yaml.py
   → Canonical 변환 추가

3. scripts/02_build_index.py
   → 두 Index 모두 구축
```

---

## 📊 예상 결과

### 데이터 구조

```yaml
Before:
  data/chroma/
    └── explorer_knowledge_base/ (54 docs)

After:
  data/chroma/
    ├── canonical_index/ (54 docs)
    │   └── ID: CAN-xxx
    │
    └── projected_index/ (324 docs, TTL)
        └── ID: PRJ-xxx
```

### 검색 흐름

```yaml
사용자:
  "@Steve, 구독 서비스 기회"

Explorer:
  1. Projected Index 검색
     filter: {agent_view: 'explorer'}
  
  2. TTL 확인:
     last_materialized < 24h?
     → 캐시 사용
     
     last_materialized > 24h?
     → Canonical에서 재투영
     → Projected 업데이트
  
  3. 결과 반환
  
  4. access_count++
     (프로파일링)
```

---

## 🎯 완료 기준

```yaml
필수:
  ✅ Canonical Index (54 docs)
     • ID: CAN-xxx
     • anchor_path + hash
     • Lineage
  
  ✅ Projected Index (324 docs)
     • ID: PRJ-xxx
     • TTL 메타데이터
     • Lineage
  
  ✅ Hybrid Projection
     • projection_rules.yaml
     • LLM fallback
     • 로그
  
  ✅ Contract Tests 통과
  
  ✅ Explorer 작동

선택 (향후):
  📋 Learning Loop
     • llm_projection_log 분석
     • 자동 규칙 생성
     → Week 5-6
```

---

## 🚀 시작

**Cursor에게 요청:**

```
"Dual-Index를 구현해줘.

1. Canonical Index 구축
   - ID: CAN-xxx
   - sections: anchor_path + content_hash
   - Lineage 추적

2. Projected Index 구축
   - ID: PRJ-xxx
   - TTL + 온디맨드
   - Hybrid Projection (rule 90% + LLM 10%)

schema_registry.yaml 100% 준수!"
```

**Cursor가 자동으로:**
- 파일 생성
- 로직 구현
- 테스트
- 통합

**대화만으로 구현!** ✨

---

**시작하시겠어요?** 🚀

