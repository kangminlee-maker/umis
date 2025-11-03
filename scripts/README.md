# UMIS Scripts

**목적**: 모든 실행 가능한 스크립트 (빌드, 쿼리, 테스트)  
**버전**: v7.0.0

---

## 📁 스크립트 분류

### 빌드 스크립트

```
01_convert_yaml.py             # YAML → JSONL 변환
02_build_index.py              # RAG 인덱스 통합 빌드
build_canonical_index.py       # Canonical Index 빌드
build_projected_index.py       # Projected Index 빌드
build_knowledge_graph.py       # Knowledge Graph 빌드
```

### 쿼리 스크립트

```
query_rag.py                   # RAG 검색 CLI
```

### 테스트 스크립트

```
03_test_search.py              # 검색 기능 테스트
test_neo4j_connection.py       # Neo4j 연결 및 CRUD 테스트
test_hybrid_explorer.py        # Hybrid Search 테스트
test_schema_contract.py        # 스키마 계약 테스트 (pytest)
test_guardian_memory.py        # Guardian Memory 테스트
test_all_improvements.py       # 전체 기능 통합 테스트
```

---

## 🚀 사용 방법

### 초기 설치

```bash
# 전체 RAG 빌드
python scripts/02_build_index.py --agent explorer

# 또는 단계별
python scripts/01_convert_yaml.py
python scripts/build_canonical_index.py
python scripts/build_projected_index.py
```

### RAG 검색

```bash
# 패턴 검색
python scripts/query_rag.py "구독 모델"

# 사례 검색
python scripts/query_rag.py case "음악 산업" --pattern subscription_model
```

### 테스트 실행

```bash
# 검색 테스트
python scripts/03_test_search.py

# Neo4j 테스트 (Docker 필요)
python scripts/test_neo4j_connection.py

# 스키마 테스트 (pytest)
pytest scripts/test_schema_contract.py

# 전체 테스트
python scripts/test_all_improvements.py
```

---

## 🎯 스크립트 상세

### 02_build_index.py (통합 빌드)

**기능**: Canonical + Projected Index 자동 빌드

```bash
# Explorer만
python scripts/02_build_index.py --agent explorer

# 모든 Agent (향후)
python scripts/02_build_index.py --agent all
```

**소요 시간**: 1-2분  
**비용**: ~$0.006 (OpenAI API)

### query_rag.py (검색 CLI)

**기능**: 터미널에서 RAG 검색

```bash
# 기본 검색
python scripts/query_rag.py "구독 모델"

# 옵션
python scripts/query_rag.py "플랫폼" --top-k 10
```

### build_knowledge_graph.py (Graph 빌드)

**기능**: Neo4j Knowledge Graph 구축

```bash
python scripts/build_knowledge_graph.py
```

**요구사항**: Docker + Neo4j 실행 중

---

## 📊 통계

```yaml
총 스크립트: 12개

분류:
  빌드: 5개
  쿼리: 1개
  테스트: 6개

총 코드: ~1,330줄
```

---

## 🔗 관련 문서

- **[../umis_rag/](../umis_rag/)** - RAG 코드 패키지
- **[../CURRENT_STATUS.md](../CURRENT_STATUS.md)** - 현재 작동 상태
- **[../INSTALL.md](../INSTALL.md)** - 설치 가이드

---

**업데이트**: 2025-11-03  
**통합**: tests/ → scripts/ (모든 실행 스크립트 한곳에)
