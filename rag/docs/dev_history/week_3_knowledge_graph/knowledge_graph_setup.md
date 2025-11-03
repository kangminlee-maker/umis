# UMIS Knowledge Graph 설정 가이드

**버전:** v6.3.0-alpha  
**날짜:** 2025-11-03  
**Week 3 Day 1-2 완료**

---

## 🎯 개요

UMIS Knowledge Graph는 Neo4j를 사용하여 비즈니스 패턴 간의 관계를 저장하고 검색합니다.

```yaml
기능:
  • 패턴 조합 발견 (platform + subscription)
  • Multi-Dimensional Confidence
  • Evidence & Provenance 추적
  • Vector + Graph Hybrid 검색

기술 스택:
  • Neo4j 5.13 (Docker)
  • Python neo4j driver
  • schema_registry.yaml 준수
```

---

## 📦 설치

### 1. 필수 패키지 설치

```bash
# 프로젝트 루트에서
cd /Users/kangmin/Documents/AI_dev/umis-main

# 가상환경 활성화
source venv/bin/activate

# Neo4j 드라이버 설치
pip install neo4j>=5.13.0

# 또는 전체 의존성 설치
pip install -r requirements.txt
```

### 2. Neo4j Docker 실행

```bash
# docker-compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f neo4j

# 상태 확인
docker ps | grep umis-neo4j
```

### 3. 환경 변수 설정

`.env` 파일에 Neo4j 설정 추가 (이미 env.template에 있음):

```bash
# Neo4j 설정 (Knowledge Graph)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=***REMOVED***
```

---

## 🧪 테스트

### 기본 테스트 실행

```bash
# 연결 + 스키마 + CRUD 테스트
python scripts/test_neo4j_connection.py
```

**예상 출력:**

```
╔==========================================================╗
║            UMIS Neo4j Test Suite                         ║
╚==========================================================╝

==========================================================
Neo4j Connection Test
==========================================================
✅ Connection test PASSED

Current Graph Stats:
  total_nodes: 0
  total_relationships: 0
  pattern_nodes: 0
  case_nodes: 0

==========================================================
Neo4j Schema Initialization Test
==========================================================
✅ Constraint created
✅ Constraint created
✅ Constraint created
✅ Constraint created
✅ Index created
✅ Index created
✅ Schema initialization PASSED
✅ Schema verification PASSED

==========================================================
Neo4j Basic Operations Test
==========================================================

1. Creating test node...
   Created 1 node(s)

2. Reading test node...
   Found 1 node(s)
   Node: {...}

3. Deleting test node...
   Deleted node

✅ Basic operations test PASSED

==========================================================
Test Summary
==========================================================
Connection.................................. ✅ PASSED
Schema Initialization....................... ✅ PASSED
Basic Operations............................ ✅ PASSED

==========================================================
Total: 3/3 tests passed
==========================================================
```

### Neo4j Browser 접속

웹 브라우저에서 확인:

```
URL: http://localhost:7474

Username: neo4j
Password: ***REMOVED***
```

**테스트 쿼리:**

```cypher
-- 모든 제약 조건 확인
SHOW CONSTRAINTS;

-- 모든 인덱스 확인
SHOW INDEXES;

-- 노드 수 확인
MATCH (n) RETURN count(n) as total_nodes;

-- Pattern 노드 수
MATCH (p:Pattern) RETURN count(p) as patterns;
```

---

## 📁 파일 구조

```yaml
Week 3 Day 1-2 완료 파일:
  docker-compose.yml:
    • Neo4j 5.13 컨테이너 정의
    • 포트: 7474 (HTTP), 7687 (Bolt)
    • 볼륨: ./data/neo4j
  
  umis_rag/graph/:
    • __init__.py
    • connection.py (Neo4jConnection)
    • schema_initializer.py (GraphSchemaInitializer)
  
  scripts/:
    • test_neo4j_connection.py
  
  data/neo4j/:
    • .gitkeep (Docker 볼륨)
  
  env.template:
    • NEO4J_* 환경 변수
  
  requirements.txt:
    • neo4j>=5.13.0
```

---

## 🎯 schema_registry.yaml 준수

### ID 네임스페이스

```yaml
Graph Node:
  • GND-xxxxxxxx (Pattern, Case 노드)
  • pattern: "GND-[a-z0-9]{8}"

Graph Edge:
  • GED-xxxxxxxx (관계)
  • pattern: "GED-[a-z0-9]{8}"
```

### 필수 필드

**Pattern 노드:**
```cypher
CREATE (p:Pattern {
  graph_node_id: 'GND-xxxxx',    -- 필수, UNIQUE
  pattern_id: 'platform_model',   -- 필수, UNIQUE
  domain: 'business_model',       -- 필수
  version: '1.0.0',               -- 필수
  source_id: 'CAN-amazon-001',    -- lineage
  created_at: datetime(),
  updated_at: datetime()
})
```

**관계 (COMBINES_WITH):**
```cypher
CREATE (a)-[r:COMBINES_WITH {
  graph_edge_id: 'GED-xxxxx',     -- 필수, UNIQUE
  evidence_ids: ['CAN-001', ...], -- v3.0: 근거 추적
  provenance: {                   -- v3.0: 출처
    source: 'humn_review',
    reviewer_id: 'stewart',
    timestamp: '2025-11-03T...'
  },
  confidence: {                   -- Multi-Dimensional
    similarity: {...},
    coverage: {...},
    validation: {...},
    overall: 0.83
  }
}]->(b)
```

---

## 🚀 다음 단계

### Day 3-4: 패턴 관계 정의

```yaml
작업:
  1. pattern_relationships.yaml (45개 관계)
  2. confidence_calculator.py
  3. 45개 관계 데이터 정의

준비:
  ✅ Neo4j 실행 중
  ✅ 스키마 생성 완료
  ✅ Python 연결 테스트 완료
```

**시작 명령:**

```
"Day 3-4 패턴 관계를 정의해줘.
pattern_relationships.yaml 45개 작성"
```

---

## 🛠️ 트러블슈팅

### Neo4j 연결 실패

```bash
# Docker 상태 확인
docker ps

# 컨테이너 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs neo4j
```

### 포트 충돌

```bash
# 7474, 7687 포트 사용 확인
lsof -i :7474
lsof -i :7687

# 다른 Neo4j 종료
pkill neo4j
```

### 권한 문제

```bash
# data/neo4j 권한 확인
ls -la data/neo4j

# 권한 수정
chmod -R 755 data/neo4j
```

---

## 📚 참고

- **Architecture:** `rag/docs/architecture/COMPLETE_ARCHITECTURE_V3.md`
- **Schema:** `schema_registry.yaml` (PART 5: Knowledge Graph)
- **Plan:** `rag/docs/architecture/03_routing_yaml/IMPLEMENTATION_PLAN.md`

---

**작성:** UMIS Team  
**상태:** Day 1-2 완료 ✅  
**다음:** Day 3-4 패턴 관계 정의


