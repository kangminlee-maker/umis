# Knowledge Graph 구현 계획 (Week 3)

**날짜:** 2025-11-02  
**버전:** v3.0  
**기간:** 7일

---

## 🎯 목표

### Knowledge Graph + Multi-Dimensional Confidence

```yaml
현재:
  • Vector RAG만 (Projected Index)

목표:
  • Neo4j Knowledge Graph
  • 패턴 관계 (45개)
  • Multi-Dimensional Confidence
  • Evidence & Provenance

강화 (v3.0):
  • ID: GND-xxx (노드), GED-xxx (간선)
  • evidence_ids (근거 추적)
  • provenance (reviewer, timestamp)
  • overall: 0-1 숫자
```

---

## 📋 Day 1-2: Neo4j 설정

### 목표

```yaml
Neo4j 설치 및 설정:
  • Docker Neo4j
  • Python 드라이버
  • 스키마 정의
```

### 작업

#### 1. Neo4j Docker

```bash
# docker-compose.yml
version: '3'
services:
  neo4j:
    image: neo4j:5.13
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/***REMOVED***
    volumes:
      - ./data/neo4j:/data
```

#### 2. Python 연결

```python
# umis_rag/graph/connection.py

from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "***REMOVED***")
        )
    
    def close(self):
        self.driver.close()
```

#### 3. 노드/간선 스키마

```cypher
-- Pattern 노드
CREATE CONSTRAINT pattern_id IF NOT EXISTS
FOR (p:Pattern) REQUIRE p.pattern_id IS UNIQUE;

-- Case 노드  
CREATE CONSTRAINT case_id IF NOT EXISTS
FOR (c:Case) REQUIRE c.source_id IS UNIQUE;

-- 인덱스
CREATE INDEX pattern_domain IF NOT EXISTS
FOR (p:Pattern) ON (p.domain);
```

### 산출물

```yaml
Day 1-2:
  ✅ docker-compose.yml
  ✅ Neo4j 실행
  ✅ umis_rag/graph/connection.py
  ✅ 스키마 생성
```

---

## 📋 Day 3-4: 패턴 관계 정의

### 목표

```yaml
45개 패턴 관계:
  • platform + subscription
  • platform + freemium
  • subscription + d2c
  • ...

Multi-Dimensional Confidence:
  • similarity (Vector)
  • coverage (분포)
  • validation (체크리스트)
  • overall (0-1)
```

### 작업

#### pattern_relationships.yaml

```yaml
# pattern_relationships.yaml (신규)

relationships:
  - id: "REL-001"
    source: "platform_business_model"
    target: "subscription_model"
    type: "COMBINES_WITH"
    
    synergy: "충성도 증가 + 안정 수익"
    
    # v3.0: Evidence & Provenance
    evidence_ids:
      - "CAN-amazon-001"  # Amazon Prime
      - "PRJ-spotify-exp-002"  # Spotify Premium
    
    provenance:
      source: "humn_review"
      reviewer_id: "stewart"
      timestamp: "2025-11-02T10:00:00Z"
    
    # Multi-Dimensional
    confidence:
      similarity:
        method: "vector_embedding"
        value: 0.92
      
      coverage:
        method: "distribution"
        value: 0.10
      
      validation:
        method: "checklist"
        value: true
      
      overall: 0.83
      
      reasoning:
        - "Best case similarity 0.92 (Amazon Prime)"
        - "10% of cases show pattern"
        - "Validator verified"
  
  - id: "REL-002"
    source: "platform_business_model"
    target: "freemium_model"
    type: "COMBINES_WITH"
    
    synergy: "무료 유입 + 플랫폼 락인"
    
    evidence_ids:
      - "CAN-linkedin-001"
    
    provenance:
      source: "auto_rule"
      reviewer_id: None
      timestamp: "2025-11-02T11:00:00Z"
    
    confidence:
      similarity: {method: "embedding", value: 0.85}
      coverage: {method: "distribution", value: 0.08}
      validation: {method: "checklist", value: true}
      overall: 0.77
      reasoning:
        - "LinkedIn case 0.85"
        - "8% pattern coverage"
  
  # ... (45개 관계)
```

#### Confidence 계산

```python
# umis_rag/graph/confidence_calculator.py

def calculate_overall_confidence(similarity, coverage, validation):
    """
    Multi-Dimensional → overall (0-1)
    """
    
    # 고품질 하나 (질적)
    if similarity['value'] >= 0.90 and validation['value']:
        return 0.85
    
    # 강한 패턴 (양적)
    if coverage['value'] >= 0.10:
        return 0.80
    
    # 중간
    if similarity['value'] >= 0.70 or coverage['value'] >= 0.05:
        return 0.65
    
    # 약함
    return 0.40
```

### 산출물

```yaml
Day 3-4:
  ✅ pattern_relationships.yaml (45개)
  ✅ umis_rag/graph/confidence_calculator.py
  ✅ Evidence IDs 연결
  ✅ Provenance 기록
```

---

## 📋 Day 5-7: Graph+Vector Hybrid

### 목표

```yaml
통합 검색:
  1. Vector 검색 (Projected)
  2. Graph 확장 (조합)
  3. 결과 통합
```

### 작업

#### Graph Builder

```python
# scripts/build_knowledge_graph.py

from neo4j import GraphDatabase
import yaml

class KnowledgeGraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(...)
        self.relationships = load_yaml('pattern_relationships.yaml')
    
    def build(self):
        """Graph 구축"""
        
        with self.driver.session() as session:
            # 노드 생성
            for pattern in patterns:
                session.run("""
                    CREATE (p:Pattern {
                        graph_node_id: $node_id,
                        pattern_id: $pattern_id,
                        domain: $domain,
                        source_id: $source_id,
                        version: $version
                    })
                """, 
                    node_id=generate_id("GND", pattern['id']),
                    pattern_id=pattern['id'],
                    ...
                )
            
            # 간선 생성 (v3.0)
            for rel in self.relationships['relationships']:
                session.run("""
                    MATCH (s:Pattern {pattern_id: $source})
                    MATCH (t:Pattern {pattern_id: $target})
                    CREATE (s)-[r:COMBINES_WITH {
                        graph_edge_id: $edge_id,
                        evidence_ids: $evidence_ids,
                        provenance: $provenance,
                        confidence: $confidence
                    }]->(t)
                """,
                    edge_id=generate_id("GED", f"{rel['id']}"),
                    source=rel['source'],
                    target=rel['target'],
                    evidence_ids=rel['evidence_ids'],
                    provenance=rel['provenance'],
                    confidence=rel['confidence']
                )
```

#### Hybrid Search

```python
# umis_rag/graph/hybrid_search.py

def hybrid_search(query, explorer):
    """
    Vector + Graph Hybrid 검색
    """
    
    # Step 1: Vector 검색
    vector_results = explorer.search_patterns(query, k=3)
    
    # Step 2: Graph 확장
    graph_results = []
    
    for doc, score in vector_results:
        pattern_id = doc.metadata.get('explorer_pattern_id')
        
        # Graph에서 조합 찾기
        combinations = find_combinations(pattern_id)
        graph_results.extend(combinations)
    
    # Step 3: 통합
    return {
        'patterns': vector_results,
        'combinations': graph_results
    }
```

### 산출물

```yaml
Day 5-7:
  ✅ scripts/build_knowledge_graph.py
  ✅ umis_rag/graph/hybrid_search.py
  ✅ Neo4j DB (45개 관계)
  ✅ Explorer 통합
```

---

## 🎯 완료 기준

```yaml
필수:
  ✅ Neo4j 실행
  ✅ Pattern 노드 (54개)
  ✅ 관계 (45개)
  ✅ Multi-Dimensional Confidence
  ✅ Evidence & Provenance
  ✅ Hybrid 검색 작동

테스트:
  "플랫폼 + 구독" 조합 검색
  → platform + subscription 발견
  → confidence: 0.83
  → evidence: Amazon Prime, Spotify
```

---

## 🚀 시작

**Cursor (Cmd+I):**

```
"Week 3 Knowledge Graph를 구현해줘.

1. Neo4j Docker 설정
2. pattern_relationships.yaml (45개)
3. build_knowledge_graph.py
4. Hybrid 검색

schema_registry.yaml 준수
(GND-xxx, GED-xxx, evidence, provenance)"
```

→ Cursor가 자동 구현! ✨

---

**시작하시겠어요?** 🚀

