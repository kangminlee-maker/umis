# benchmarks / tests / scripts 폴더 정리 계획 v7.11.0

**작성일**: 2025-11-26
**목적**: v7.11.0 마이그레이션 완료 후 benchmarks, tests, scripts 폴더 정리

---

## 📊 현재 상태

### benchmarks/
- **총 49개 Phase 4 테스트 파일**
- **12개 JSON 결과 파일** (archive/)
- **8개 JSON 결과 파일** (phase4/results/)
- **Phase 4 중심 구조** (v7.11.0에서 Stage 3로 대체)

### tests/
- **25개 테스트 파일**
- **23개 JSON 결과 파일** (results/)
- **4개 MD 보고서**
- **Phase 0-4 테스트** (v7.11.0에서 Stage 1-4로 대체)

### scripts/
- **31개 Python 스크립트**
- **3개 MD 문서**
- **2개 Shell 스크립트**
- 빌드, 쿼리, 테스트, 벤치마크, 검증 등 다양한 용도

---

## 🎯 정리 원칙

### 1. v7.11.0 중심
- Stage 1-4 테스트만 보관
- Phase 0-4 관련 → Archive

### 2. 중복 제거
- 같은 목적의 파일 통합
- 오래된 JSON 결과 삭제

### 3. 명확한 분류
- benchmarks/: 성능 벤치마크만
- tests/: 기능 테스트만
- scripts/: 현재 사용 중인 스크립트만

---

## 📁 benchmarks/ 정리

### Archive 이동 (Phase 4 관련)

#### benchmarks/estimator/phase4/ 전체 → Archive
```
benchmarks/estimator/phase4/
├── tests/ (49개) → archive/benchmarks_v7.10.2/phase4/tests/
├── results/ (8개 JSON) → archive/benchmarks_v7.10.2/phase4/results/
├── analysis/ (2개 MD) → archive/benchmarks_v7.10.2/phase4/analysis/
├── scenarios.py → archive/benchmarks_v7.10.2/phase4/
├── common.py → archive/benchmarks_v7.10.2/phase4/
└── README.md → archive/benchmarks_v7.10.2/phase4/
```

**이유**: Phase 4 → v7.11.0 Stage 3 Fermi로 대체

#### benchmarks/estimator/ MD 파일 → Archive
```
MODEL_CONFIG_DESIGN.md → archive/benchmarks_v7.10.2/
MODEL_CONFIG_TEST_RESULTS.md → archive/benchmarks_v7.10.2/
PHASE4_IMPROVEMENT_PLAN.md → archive/benchmarks_v7.10.2/
PHASE4_IMPROVEMENTS_SUMMARY.md → archive/benchmarks_v7.10.2/
PHASE4_INTEGRATION_COMPLETE.md → archive/benchmarks_v7.10.2/
PHASE4_INTEGRATION_FINAL.md → archive/benchmarks_v7.10.2/
```

#### benchmarks/ Root MD → Archive
```
PHASE1_COMPLETION_REPORT.md → archive/benchmarks_v7.10.2/
MIGRATION_PLAN.md → archive/benchmarks_v7.10.2/
```

### 삭제 대상

#### benchmarks/archive/ (12개 JSON)
```
❌ benchmark_o1_mini_*.json (2개)
❌ benchmark_responses_api_*.json (1개)
❌ benchmark_phase4_comprehensive_*.json (1개)
❌ benchmark_untested_models_*.json (1개)
❌ gpt5_pro_problem1_retest_*.json (1개)
❌ gpt51_complete_*.json (3개)
❌ phase4_*.json (3개)
```

**이유**: Phase 4 벤치마크 결과, 보고서에 통합됨

### 보관 대상

```
benchmarks/
├── __init__.py
├── common/
│   ├── __init__.py
│   └── common.py
├── estimator/
│   ├── __init__.py
│   └── README.md (v7.11.0로 업데이트 필요)
└── README.md (v7.11.0로 업데이트 필요)
```

**v7.11.0 벤치마크는 새로 작성 필요**

---

## 📁 tests/ 정리

### Archive 이동 (Phase 0-4 관련)

#### Root 레벨 Phase 테스트 → Archive
```
test_estimator_phase0_4.py → archive/tests_v7.10.2/
test_phase_0_4_comprehensive.py → archive/tests_v7.10.2/
test_phase2_threshold.py → archive/tests_v7.10.2/
```

#### MD 보고서 → Archive
```
COMPREHENSIVE_TEST_REPORT.md → archive/tests_v7.10.2/
ESTIMATOR_PHASE0_4_TEST_REPORT.md → archive/tests_v7.10.2/
PHASE3_PHASE4_FIX_REPORT.md → archive/tests_v7.10.2/
PHASE4_FINAL_TEST_REPORT.md → archive/tests_v7.10.2/
TEST_RESULTS_v7_8_1.md → archive/tests_v7.10.2/
```

#### integration/test_hybrid_integration.py → Archive
```
test_hybrid_integration.py → archive/tests_v7.10.2/integration/
```

**이유**: Hybrid Architecture (v7.10.0) 테스트

#### unit/test_hybrid_architecture.py → Archive
```
test_hybrid_architecture.py → archive/tests_v7.10.2/unit/
```

### 삭제 대상

#### tests/results/ JSON (23개)
```
❌ estimator_comprehensive_*.json (9개)
❌ estimator_phase0_4_test_*.json (2개)
❌ phase4_creative_test_*.json (7개)
❌ phase4_final_test_*.json (1개)
❌ test_model_config_live_*.json (2개)
❌ test_phase4_model_config_*.json (1개)
```

**이유**: Phase 0-4 테스트 결과, 보고서에 통합됨

**보관**: TEST_RESULTS_V7_11_0_RECURSIVE_EXPLOSION.md (v7.11.0)

### 이름 변경 (명확성)

```
test_v7_11_0_fermi_10problems.py
  → test_stage3_fermi_10problems_v7_11_0.py

test_v7_11_0_fusion_architecture.py
  → test_fusion_architecture_v7_11_0.py

test_v7_11_0_recursive_explosion_check.py
  → test_recursive_explosion_check_v7_11_0.py
```

### 보관 대상 (v7.11.0)

```
tests/
├── ab_testing/
│   ├── __init__.py
│   └── test_stage_ab_framework_v7_11_0.py ✅
├── e2e/
│   ├── check_e2e_results.py
│   └── test_estimator_e2e_scenarios_v7_11_0.py ✅
├── edge_cases/
│   └── test_edge_cases.py
├── integration/
│   └── test_stage_flow_v7_11_0.py ✅
├── unit/
│   ├── test_fermi_estimator.py ✅
│   ├── test_prior_estimator.py ✅
│   ├── test_guardrail_analyzer.py ✅
│   └── test_guardrail_collector.py ✅
├── results/
│   └── TEST_RESULTS_V7_11_0_RECURSIVE_EXPLOSION.md ✅
├── test_evidence_collector.py ✅
├── test_phase0_guardrail_v7_11_0.py ✅
├── test_stage3_fermi_10problems_v7_11_0.py ✅ (이름 변경)
├── test_fusion_architecture_v7_11_0.py ✅ (이름 변경)
├── test_recursive_explosion_check_v7_11_0.py ✅ (이름 변경)
├── test_model_config_live.py
├── test_model_configs.py
├── test_model_configs_simulation.py
├── test_integration_timeline.py
├── test_observer_timeline.py
└── test_strategy_playbook.py
```

---

## 📁 scripts/ 정리 (세심한 분석)

### 분류 기준

#### A. Core 스크립트 (보관, 11개)
```
✅ 01_convert_yaml.py              # YAML → JSONL 변환
✅ 02_build_index.py               # RAG 인덱스 빌드
✅ 03_test_search.py               # 검색 테스트
✅ build_canonical_index.py        # Canonical 빌드
✅ build_projected_index.py        # Projected 빌드
✅ build_knowledge_graph.py        # Neo4j 빌드
✅ build_system_knowledge.py       # System RAG 빌드
✅ build_agent_rag_collections.py  # Agent RAG 빌드
✅ build_data_sources_registry.py  # Data Sources 빌드
✅ query_rag.py                    # RAG 쿼리
✅ query_system_rag.py             # System RAG 쿼리
```

#### B. 검증 스크립트 (보관, 4개)
```
✅ validate_all_yaml.py            # YAML 검증
✅ verify_benchmarks.py            # 벤치마크 검증
✅ verify_market_sizing_formulas.py # 공식 검증
✅ verify_tool_coverage.py         # 도구 커버리지 검증
```

#### C. 유틸리티 스크립트 (보관, 3개)
```
✅ analyze_pattern_coverage.py    # 패턴 커버리지 분석
✅ download_prebuilt_db.py         # Pre-built DB 다운로드
✅ clean_architecture.py           # 아키텍처 정리
```

#### D. 마이그레이션 스크립트 (Archive, 3개)
```
migrate_umis_to_rag.py → archive/scripts_v7.10.2/
sync_umis_to_rag.py → archive/scripts_v7.10.2/
rollback_rag.py → archive/scripts_v7.10.2/
```

**이유**: RAG v3.0 마이그레이션 완료, 더 이상 사용 안 함

#### E. 벤치마크 스크립트 (Archive, 7개)
```
benchmark_comprehensive_2025.py → archive/scripts_v7.10.2/
benchmark_final_2025.py → archive/scripts_v7.10.2/
benchmark_llm_models_2025.py → archive/scripts_v7.10.2/
benchmark_openai_models.py → archive/scripts_v7.10.2/
interactive_model_benchmark.py → archive/scripts_v7.10.2/
retest_failed_models.py → archive/scripts_v7.10.2/
retry_and_merge.py → archive/scripts_v7.10.2/
run_full_benchmark_with_responses.py → archive/scripts_v7.10.2/
```

**이유**: Phase 4 벤치마크, v7.11.0에서 새로 작성 필요

#### F. 예제 스크립트 (Archive, 2개)
```
estimate_korean_practical_education_market.py → archive/scripts_v7.10.2/
generate_fermi_report.py → archive/scripts_v7.10.2/
```

**이유**: Phase 4 Fermi 예제, Stage 3로 재작성 필요

#### G. Shell 스크립트 (보관, 2개)
```
✅ deploy_to_main.sh               # Main 브랜치 배포
✅ quick_sync.sh                   # 빠른 동기화
```

#### H. 문서 (정리 필요, 3개)
```
README.md → 보관 (v7.11.0로 업데이트 필요)
README_SYNC.md → archive/scripts_v7.10.2/ (RAG 동기화 가이드)
collect_real_data_guide.md → docs/ (데이터 수집 가이드)
MAX_OUTPUT_TOKENS_OPTIMIZATION.md → archive/scripts_v7.10.2/ (Phase 4 최적화)
```

### 최종 scripts/ 구조 (20개 보관)

```
scripts/
├── README.md (v7.11.0 업데이트)
│
├── 빌드 스크립트 (11개)
│   ├── 01_convert_yaml.py
│   ├── 02_build_index.py
│   ├── 03_test_search.py
│   ├── build_canonical_index.py
│   ├── build_projected_index.py
│   ├── build_knowledge_graph.py
│   ├── build_system_knowledge.py
│   ├── build_agent_rag_collections.py
│   ├── build_data_sources_registry.py
│   ├── query_rag.py
│   └── query_system_rag.py
│
├── 검증 스크립트 (4개)
│   ├── validate_all_yaml.py
│   ├── verify_benchmarks.py
│   ├── verify_market_sizing_formulas.py
│   └── verify_tool_coverage.py
│
├── 유틸리티 (3개)
│   ├── analyze_pattern_coverage.py
│   ├── download_prebuilt_db.py
│   └── clean_architecture.py
│
└── Shell (2개)
    ├── deploy_to_main.sh
    └── quick_sync.sh
```

---

## 🗂️ Archive 폴더 구조

```
archive/
├── benchmarks_v7.10.2/
│   ├── README.md
│   ├── PHASE1_COMPLETION_REPORT.md
│   ├── MIGRATION_PLAN.md
│   ├── MODEL_CONFIG_DESIGN.md
│   ├── MODEL_CONFIG_TEST_RESULTS.md
│   ├── PHASE4_*.md (4개)
│   └── phase4/
│       ├── tests/ (49개 .py)
│       ├── results/ (8개 .json)
│       ├── analysis/ (2개 .md)
│       ├── scenarios.py
│       ├── common.py
│       └── README.md
│
├── tests_v7.10.2/
│   ├── README.md
│   ├── test_estimator_phase0_4.py
│   ├── test_phase_0_4_comprehensive.py
│   ├── test_phase2_threshold.py
│   ├── COMPREHENSIVE_TEST_REPORT.md
│   ├── ESTIMATOR_PHASE0_4_TEST_REPORT.md
│   ├── PHASE3_PHASE4_FIX_REPORT.md
│   ├── PHASE4_FINAL_TEST_REPORT.md
│   ├── TEST_RESULTS_v7_8_1.md
│   ├── integration/
│   │   └── test_hybrid_integration.py
│   └── unit/
│       └── test_hybrid_architecture.py
│
└── scripts_v7.10.2/
    ├── README.md
    ├── README_SYNC.md
    ├── MAX_OUTPUT_TOKENS_OPTIMIZATION.md
    ├── migrate_umis_to_rag.py
    ├── sync_umis_to_rag.py
    ├── rollback_rag.py
    ├── benchmark_*.py (5개)
    ├── interactive_model_benchmark.py
    ├── retest_failed_models.py
    ├── retry_and_merge.py
    ├── run_full_benchmark_with_responses.py
    ├── estimate_korean_practical_education_market.py
    └── generate_fermi_report.py
```

---

## 📊 정리 요약

| 폴더 | Before | After | Archive | 삭제 |
|------|--------|-------|---------|------|
| **benchmarks/** | 70+ 파일 | 7개 | 63개 | 12개 JSON |
| **tests/** | 48개 | 25개 | 11개 | 23개 JSON |
| **scripts/** | 36개 | 23개 | 13개 | 0개 |

### 정리 효과

- **benchmarks/**: Phase 4 완전 제거, v7.11.0 새 벤치마크 준비
- **tests/**: v7.11.0 Stage 테스트만 보관, Phase 테스트 제거
- **scripts/**: 현재 사용 중인 20개만 보관, 레거시 13개 Archive

---

## ✅ 실행 순서

1. Archive 폴더 생성
2. benchmarks/ 정리 (phase4/ 전체 Archive)
3. tests/ 정리 (Phase 테스트 Archive)
4. scripts/ 정리 (레거시 Archive)
5. JSON 결과 파일 삭제
6. 문서 이동/업데이트
7. Archive README 작성
8. Git commit & push

---

**예상 소요 시간**: 20분
**위험도**: 낮음 (Archive로 이동, 복구 가능)
