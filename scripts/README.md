# UMIS Scripts

**목적**: 모든 실행 가능한 스크립트 (빌드, 쿼리, 테스트)  
**버전**: v7.7.0  
**Last Update**: 2025-11-20

---

## 📁 스크립트 분류

### 🔨 빌드 스크립트 (Core)

```bash
01_convert_yaml.py             # YAML → JSONL 변환
02_build_index.py              # RAG 인덱스 통합 빌드 (Canonical + Projected)
build_canonical_index.py       # Canonical Index 빌드
build_projected_index.py       # Projected Index 빌드 (Agent별)
build_knowledge_graph.py       # Neo4j Knowledge Graph 빌드
build_system_knowledge.py      # System RAG (umis.yaml → RAG)
build_agent_rag_collections.py # Agent RAG Collections 빌드
build_data_sources_registry.py # Data Sources Registry 빌드
```

### 🔍 쿼리 스크립트

```bash
query_rag.py                   # RAG 검색 CLI (Explorer, Quantifier 등)
query_system_rag.py            # System RAG 검색 (umis.yaml 도구 로드)
```

### 🧪 테스트 스크립트

```bash
# Core Tests
03_test_search.py              # 검색 기능 테스트
test_schema_contract.py        # 스키마 계약 테스트 (pytest)
test_all_improvements.py       # 전체 기능 통합 테스트
test_system_rag_determinism.py # System RAG 결정성 테스트

# Agent Tests
test_agent_rag.py              # Agent RAG 통합 테스트
test_explorer_patterns.py      # Explorer 패턴 매칭 테스트
test_guardian_memory.py        # Guardian Memory 테스트
test_hybrid_explorer.py        # Hybrid Search 테스트

# Feature Tests
test_native_mode.py            # Native/External 모드 테스트 (v7.7.0)
test_web_search.py             # Web Search 테스트

# Infrastructure Tests
test_neo4j_connection.py       # Neo4j 연결 및 CRUD 테스트
test_api_key_parsing.py        # API Key 파싱 테스트
```

### 🔧 유틸리티 스크립트

```bash
# Migration & Sync
migrate_umis_to_rag.py         # umis.yaml → RAG 마이그레이션
sync_umis_to_rag.py            # umis.yaml 변경사항 동기화
rollback_rag.py                # RAG 롤백

# Verification
verify_benchmarks.py           # 벤치마크 검증
verify_market_sizing_formulas.py # 시장 규모 수식 검증
verify_tool_coverage.py        # 도구 커버리지 검증
validate_all_yaml.py           # YAML 검증

# Analysis
analyze_pattern_coverage.py   # 패턴 커버리지 분석
estimate_korean_practical_education_market.py # 실용 교육 시장 추정

# Benchmarking
benchmark_openai_models.py     # OpenAI 모델 벤치마크
interactive_model_benchmark.py # 대화형 모델 벤치마크
```

### 🚀 배포 스크립트

```bash
deploy_to_main.sh              # main 브랜치 배포
quick_sync.sh                  # 빠른 동기화
```

### 📚 문서

```bash
README.md                      # 본 파일
README_SYNC.md                 # 동기화 가이드
collect_real_data_guide.md     # 실제 데이터 수집 가이드
```

### 🔧 기타

```bash
download_prebuilt_db.py        # 사전 빌드된 DB 다운로드
```

---

## 🚀 사용 방법

### 초기 설치

```bash
# 전체 RAG 빌드 (권장)
python scripts/02_build_index.py --agent explorer

# 또는 단계별
python scripts/01_convert_yaml.py
python scripts/build_canonical_index.py
python scripts/build_projected_index.py

# System RAG 빌드 (umis.yaml → RAG)
python scripts/build_system_knowledge.py
```

### RAG 검색

```bash
# 패턴 검색 (Explorer)
python scripts/query_rag.py "구독 모델"

# System RAG 검색 (도구 로드)
python scripts/query_system_rag.py tool:explorer:complete
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

# Native 모드 테스트 (v7.7.0)
UMIS_MODE=native python scripts/test_native_mode.py
```

### umis.yaml 동기화

```bash
# umis.yaml 변경 후 RAG 동기화
python scripts/sync_umis_to_rag.py

# 또는 빠른 동기화 스크립트
./scripts/quick_sync.sh
```

---

## 📊 통계

```yaml
총 스크립트: 39개 (Python: 37개, Shell: 2개, Markdown: 3개)

분류:
  빌드: 8개
  쿼리: 2개
  테스트: 12개
  유틸리티: 13개
  배포: 2개
  문서: 3개

총 코드: ~8,500줄
```

---

## 🗄️ Archive

**Deprecated 스크립트**는 `archive/` 폴더로 이동되었습니다:

- `archive/guestimation_v3/scripts/` - Guestimation v3 테스트 (11개)
- `archive/deprecated_scripts/sga_parsers/` - SGA 파서 (18개)
- `archive/deprecated_scripts/excel_tests/` - Excel 테스트 (22개)
- `archive/deprecated_scripts/validation/` - 검증 도구 (14개)
- `archive/deprecated_scripts/build_tools/` - 빌드 도구 (6개)

**Archive 날짜**: 2025-11-20  
**총 Archive**: 71개 파일

자세한 내용은 각 archive 폴더의 README.md 참조

---

## 🔗 관련 문서

- **[../umis_rag/](../umis_rag/)** - RAG 코드 패키지
- **[../docs/](../docs/)** - 활성 프로토콜 문서
- **[../umis.yaml](../umis.yaml)** - UMIS 메인 가이드
- **[../INSTALL.md](../INSTALL.md)** - 설치 가이드
- **[../CHANGELOG.md](../CHANGELOG.md)** - 변경 이력

---

**업데이트**: 2025-11-20  
**버전**: v7.7.0  
**통합**: 활성 스크립트만 유지, deprecated는 archive/로 이동
