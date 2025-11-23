# Deprecated Scripts Archive

**Deprecated**: 2025-11-20  
**Version**: v7.7.0 이전

---

## 📁 폴더 구조

### `sga_parsers/` (18개)
SG&A 파싱 관련 deprecated 스크립트

**파서 버전들**:
- `parse_sga_hybrid.py` - 하이브리드 파서
- `parse_sga_optimized.py` - 최적화 버전
- `parse_sga_v2_validated.py` - v2 검증 버전
- `parse_sga_unified.py` - 통합 파서
- `parse_sga_standard_accounts.py` - 표준 계정 파서
- `llm_based_sga_parser.py` - LLM 기반 파서

**배치 처리**:
- `batch_parse_extended.py`
- `batch_reparse_2024.py`
- `reparse_all_2024.py`
- `validate_all_2024.py`

**유틸리티**:
- `collect_sga_patterns.py`
- `clean_sga_data.py`
- `enrich_sga_with_economics.py`
- `summarize_sga_results.py`
- `create_clean_sga_files.py`
- `classify_variable_fixed_costs.py`
- `calculate_contribution_margin.py`
- `check_danggi_jeongi.py`
- `debug_gs_retail_parsing.py`
- `find_gs_2024_report.py`

### `excel_tests/` (22개)
Excel 생성 및 테스트 관련 deprecated 스크립트

**생성 도구**:
- `generate_example_financial_projection.py`
- `generate_example_market_sizing.py`
- `generate_example_unit_economics.py`
- `create_golden_workbook.py`
- `create_market_analysis_excel.py`

**값 채우기**:
- `populate_all_excel_values.py`
- `populate_market_sizing_values.py`

**테스트**:
- `test_all_excel_generators.py`
- `test_excel_generation.py`
- `test_market_sizing_v7_2.py`
- `test_financial_projection_batch4.py`
- `test_financial_projection_batch5.py`
- `test_financial_projection_complete.py`
- `test_unit_economics_batch1.py`
- `test_unit_economics_batch2.py`
- `test_unit_economics_complete.py`

**QA**:
- `golden_test_all.py`
- `final_qa_all_excel.py`
- `qa_all_example_files.py`
- `regenerate_all_examples.py`

**체크**:
- `find_all_hardcoded_ranges.py`
- `check_named_ranges.py`
- `check_all_dashboards.py`
- `check_assumptions_values.py`
- `check_duplicate_items.py`
- `apply_full_named_range.py`

### `validation/` (14개)
검증 및 진단 관련 deprecated 스크립트

**진단**:
- `diagnose_excel_formulas.py`
- `diagnose_market_sizing.py`
- `diagnose_market_sizing_detailed.py`

**검증**:
- `validate_generated_excel.py`
- `validate_formula_references.py`
- `validate_benchmarks.py`
- `validate_sga_quality.py`
- `test_kpi_validation.py`

**테스트**:
- `test_robust_crawler_batch.py`
- `test_dart_crawler.py`
- `test_google_search.py`
- `test_web_search_debug.py`
- `test_source_collector.py`
- `test_source_consolidation.py`

**비교**:
- `compare_with_golden.py`

### `build_tools/` (6개)
빌드 및 추출 관련 deprecated 도구

- `extract_tools_from_umis.py` - Tool Registry 추출
- `extract_agent_sections.py` - Agent 섹션 추출
- `build_evolution_patterns_rag.py` - 진화 패턴 RAG
- `build_margin_benchmarks_rag.py` - 마진 벤치마크 RAG
- `build_kpi_library.py` - KPI 라이브러리
- `collect_kosis_statistics.py` - KOSIS 통계 수집

---

## 🔄 대체 도구

### SGA 파싱
현재 사용 중인 최신 파서가 있다면 해당 경로 명시 필요

### Excel 생성
Deliverable 시스템으로 통합:
- `umis_rag/deliverables/`

### 검증
테스트 시스템으로 통합:
- `scripts/test_all_improvements.py`
- `scripts/test_schema_contract.py`

### RAG 빌드
현재 사용 중:
- `scripts/01_convert_yaml.py`
- `scripts/02_build_index.py`
- `scripts/build_canonical_index.py`
- `scripts/build_projected_index.py`
- `scripts/build_system_knowledge.py`

---

## 📊 통계

```yaml
총 파일: 60개

분류:
  sga_parsers: 18개
  excel_tests: 22개
  validation: 14개
  build_tools: 6개

총 코드: ~15,000줄 (추정)
```

---

## ⚠️ 주의사항

**이 파일들은 동작하지 않을 수 있습니다**:
- 의존성 변경
- API 변경
- 데이터 구조 변경
- 더 나은 대체 도구 존재

**복구가 필요한 경우**:
1. 새로운 시스템에서 동일 기능 확인
2. 없다면 코드 리뷰 후 재작성 고려
3. 단순 복사는 권장하지 않음

---

**Archive 날짜**: 2025-11-20  
**Version**: v7.7.0


