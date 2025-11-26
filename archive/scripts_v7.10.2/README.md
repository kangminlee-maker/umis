# Archive: scripts v7.10.2

**보관 일자**: 2025-11-26
**이유**: v7.11.0 마이그레이션 완료 후 사용하지 않는 스크립트 정리

---

## 📁 구조

```
archive/scripts_v7.10.2/
├── 마이그레이션 스크립트 (3개)
│   ├── migrate_umis_to_rag.py
│   ├── sync_umis_to_rag.py
│   └── rollback_rag.py
├── 벤치마크 스크립트 (8개)
│   ├── benchmark_comprehensive_2025.py
│   ├── benchmark_final_2025.py
│   ├── benchmark_llm_models_2025.py
│   ├── benchmark_openai_models.py
│   ├── interactive_model_benchmark.py
│   ├── retest_failed_models.py
│   ├── retry_and_merge.py
│   └── run_full_benchmark_with_responses.py
├── 예제 스크립트 (2개)
│   ├── estimate_korean_practical_education_market.py
│   └── generate_fermi_report.py
├── 문서 (2개)
│   ├── README_SYNC.md
│   └── MAX_OUTPUT_TOKENS_OPTIMIZATION.md
└── README.md (이 파일)
```

---

## 🎯 보관 이유

### 마이그레이션 스크립트 (3개)
**이유**: RAG v3.0 마이그레이션 완료, 더 이상 사용 안 함

- `migrate_umis_to_rag.py` - umis.yaml → RAG 마이그레이션
- `sync_umis_to_rag.py` - umis.yaml ↔ RAG 동기화
- `rollback_rag.py` - RAG 롤백

**완료 일자**: 2024-11 (v7.0.0)

### 벤치마크 스크립트 (8개)
**이유**: Phase 4 벤치마크, v7.11.0 Stage 3로 재작성 필요

- `benchmark_comprehensive_2025.py` - 종합 벤치마크
- `benchmark_final_2025.py` - 최종 벤치마크
- `benchmark_llm_models_2025.py` - LLM 모델 벤치마크
- `benchmark_openai_models.py` - OpenAI 모델 벤치마크
- `interactive_model_benchmark.py` - 대화형 벤치마크
- `retest_failed_models.py` - 실패 모델 재테스트
- `retry_and_merge.py` - 재시도 및 병합
- `run_full_benchmark_with_responses.py` - Responses API 벤치마크

**대체**: 새 벤치마크 필요 (Stage 3 기반)

### 예제 스크립트 (2개)
**이유**: Phase 4 Fermi 예제, Stage 3로 재작성 필요

- `estimate_korean_practical_education_market.py` - 한국 실용교육 시장 추정
- `generate_fermi_report.py` - Fermi 리포트 생성

**대체**: v7.11.0 예제 필요

### 문서 (2개)
**이유**: 레거시 문서

- `README_SYNC.md` - RAG 동기화 가이드 (v7.0.0)
- `MAX_OUTPUT_TOKENS_OPTIMIZATION.md` - Phase 4 최적화 (v7.10.0)

---

## ✅ 현재 사용 중인 스크립트 (20개)

```
scripts/
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
├── 검증 스크립트 (4개)
│   ├── validate_all_yaml.py
│   ├── verify_benchmarks.py
│   ├── verify_market_sizing_formulas.py
│   └── verify_tool_coverage.py
├── 유틸리티 (3개)
│   ├── analyze_pattern_coverage.py
│   ├── download_prebuilt_db.py
│   └── clean_architecture.py
└── Shell (2개)
    ├── deploy_to_main.sh
    └── quick_sync.sh
```

---

## ⚠️ 주의사항

### 이 스크립트들은 Archive입니다
- v7.11.0에서 더 이상 사용하지 않습니다
- 히스토리 참고용으로만 보관
- 새 벤치마크/예제 필요

### v7.11.0 새 스크립트
Stage 3 기반으로 재작성 필요:
- Stage 3 Fermi 벤치마크
- Budget 기반 예제
- Non-recursive 검증

---

## 📞 문의

**현재 스크립트**:
- 문서: `scripts/README.md`

**Archive 복원**:
- Git history에서 복원 가능

---

**보관**: 2025-11-26
**레거시 스크립트 정리 완료** 🎉
