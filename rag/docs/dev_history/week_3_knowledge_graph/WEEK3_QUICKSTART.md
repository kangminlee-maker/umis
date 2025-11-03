# Week 3 Knowledge Graph - Quick Start

**상태:** Day 1-2 완료 ✅  
**다음:** Day 3-4 시작 준비

---

## ✅ Day 1-2 완료 내용

```yaml
완성된 파일:
  ✅ docker-compose.yml (Neo4j 5.13)
  ✅ umis_rag/graph/connection.py
  ✅ umis_rag/graph/schema_initializer.py
  ✅ scripts/test_neo4j_connection.py
  ✅ requirements.txt (neo4j 추가)
  ✅ env.template (Neo4j 설정)
  ✅ docs/knowledge_graph_setup.md

기능:
  ✅ Neo4j 연결 관리
  ✅ 스키마 초기화 (Constraints, Indexes)
  ✅ 테스트 스크립트
  ✅ schema_registry.yaml 준수 (GND-xxx, GED-xxx)
```

---

## 🚀 지금 바로 시작하기

### Step 1: Neo4j 패키지 설치

```bash
# 프로젝트 루트로 이동
cd /Users/kangmin/Documents/AI_dev/umis-main

# 가상환경 활성화
source venv/bin/activate

# neo4j 설치
pip install neo4j>=5.13.0
```

### Step 2: Docker로 Neo4j 실행

```bash
# Neo4j 컨테이너 시작
docker-compose up -d

# 실행 확인 (약 10초 소요)
docker-compose logs -f neo4j

# "Started." 메시지 나오면 Ctrl+C
```

### Step 3: 연결 테스트

```bash
# 테스트 실행
python scripts/test_neo4j_connection.py
```

**예상 결과:**

```
✅ Connection test PASSED
✅ Schema initialization PASSED  
✅ Basic operations test PASSED

Total: 3/3 tests passed
```

### Step 4: Neo4j Browser 확인 (선택)

브라우저에서 열기:

```
http://localhost:7474

로그인:
  Username: neo4j
  Password: ***REMOVED***
```

테스트 쿼리:

```cypher
SHOW CONSTRAINTS;
SHOW INDEXES;
```

---

## 📊 현재 상태

### 완료된 작업

```yaml
Day 1-2: ✅ 완료
  • Neo4j Docker 설정
  • Python 연결 관리
  • 스키마 정의
  • 테스트 스크립트
```

### 다음 작업

```yaml
Day 3-4: 📋 대기 중
  • pattern_relationships.yaml (45개 관계 정의)
  • confidence_calculator.py (Multi-Dimensional)
  • Evidence & Provenance 추가

Day 5-7: 📋 대기 중
  • build_knowledge_graph.py
  • hybrid_search.py
  • Explorer 통합
```

---

## 🎯 Day 3-4 시작 방법

준비가 되면 다음과 같이 시작하세요:

```
"Day 3-4 패턴 관계 정의를 시작하자.
pattern_relationships.yaml 45개 작성해줘."
```

---

## 🛠️ 문제 해결

### Neo4j가 시작되지 않는 경우

```bash
# 기존 컨테이너 제거
docker-compose down

# 데이터 초기화 (선택)
rm -rf data/neo4j/*

# 다시 시작
docker-compose up -d
```

### 테스트가 실패하는 경우

```bash
# Neo4j 상태 확인
docker ps | grep neo4j

# 로그 확인
docker-compose logs neo4j

# 재시작
docker-compose restart neo4j

# 10초 대기 후 재테스트
sleep 10
python scripts/test_neo4j_connection.py
```

### 포트가 이미 사용 중인 경우

```bash
# 포트 사용 확인
lsof -i :7474
lsof -i :7687

# 해당 프로세스 종료 후 재시작
docker-compose restart neo4j
```

---

## 📚 참고 문서

- **설정 가이드:** `docs/knowledge_graph_setup.md`
- **Architecture:** `rag/docs/architecture/COMPLETE_ARCHITECTURE_V3.md`
- **Schema:** `schema_registry.yaml` (PART 5)
- **구현 계획:** `rag/docs/architecture/03_routing_yaml/IMPLEMENTATION_PLAN.md`

---

**작성:** 2025-11-03  
**상태:** Day 1-2 완료 ✅  
**다음:** Day 3-4 대기 중


