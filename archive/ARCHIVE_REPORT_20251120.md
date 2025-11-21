# Scripts Archive Report

**날짜**: 2025-11-20  
**작업**: Deprecated 스크립트 정리  
**버전**: v7.7.0

---

## 📊 요약

### 이동된 파일

| 카테고리 | 파일 수 | 목적지 |
|---------|--------|--------|
| Guestimation v3 테스트 | 11개 | `archive/guestimation_v3/scripts/` |
| SGA 파서 | 18개 | `archive/deprecated_scripts/sga_parsers/` |
| Excel 테스트 | 22개 | `archive/deprecated_scripts/excel_tests/` |
| 검증 도구 | 14개 | `archive/deprecated_scripts/validation/` |
| 빌드 도구 | 6개 | `archive/deprecated_scripts/build_tools/` |
| **총계** | **71개** | **5개 폴더** |

### 남은 파일

| 카테고리 | 파일 수 |
|---------|--------|
| 빌드 스크립트 | 8개 |
| 쿼리 스크립트 | 2개 |
| 테스트 스크립트 | 12개 |
| 유틸리티 | 13개 |
| 배포 | 2개 |
| 문서 | 3개 |
| **총계** | **39개** |

---

## 📁 Archive 구조

```
archive/
├── guestimation_v3/
│   ├── scripts/                        (11개)
│   │   ├── test_tier1_guestimation.py
│   │   ├── test_tier2_guestimation.py
│   │   ├── test_tier3_basic.py
│   │   ├── test_tier3_business_metrics.py
│   │   ├── test_fermi_model_search.py
│   │   ├── test_learning_e2e.py
│   │   ├── test_learning_writer.py
│   │   ├── test_phase2_enhanced.py
│   │   ├── test_phase3_models.py
│   │   ├── test_single_source_policy.py
│   │   └── test_quantifier_v3.py
│   └── README.md
│
└── deprecated_scripts/
    ├── sga_parsers/                    (18개)
    │   ├── parse_sga_hybrid.py
    │   ├── parse_sga_optimized.py
    │   ├── parse_sga_v2_validated.py
    │   ├── parse_sga_unified.py
    │   ├── parse_sga_standard_accounts.py
    │   ├── llm_based_sga_parser.py
    │   ├── batch_parse_extended.py
    │   ├── batch_reparse_2024.py
    │   ├── reparse_all_2024.py
    │   ├── validate_all_2024.py
    │   └── ... (8개 더)
    │
    ├── excel_tests/                    (22개)
    │   ├── generate_example_*.py (3개)
    │   ├── test_*_batch*.py (6개)
    │   ├── test_*_complete.py (3개)
    │   ├── *_test_all.py (3개)
    │   └── ... (7개 더)
    │
    ├── validation/                     (14개)
    │   ├── diagnose_*.py (3개)
    │   ├── validate_*.py (4개)
    │   ├── test_*_crawler*.py (2개)
    │   └── ... (5개 더)
    │
    ├── build_tools/                    (6개)
    │   ├── extract_tools_from_umis.py
    │   ├── extract_agent_sections.py
    │   ├── build_evolution_patterns_rag.py
    │   ├── build_margin_benchmarks_rag.py
    │   ├── build_kpi_library.py
    │   └── collect_kosis_statistics.py
    │
    └── README.md
```

---

## 🔄 변경 이유

### 1. Guestimation v3 → Estimator v7.7.0

**Deprecated**:
- Tier 1-3 시스템
- Built-in Rules
- Fermi Model Search
- Learning Writer (v1)

**새로운 시스템**:
- 5-Phase Architecture (Phase 0-4)
- Canonical Store
- EstimatorRAG 통합 인터페이스
- 자동 학습 시스템

### 2. SGA 파서 통합

여러 버전의 파서가 존재했으나, 현재는:
- 최신 파서로 통합
- 또는 더 이상 사용하지 않음

### 3. Excel 생성 시스템 진화

**Deprecated**:
- 개별 생성 스크립트들
- 배치 테스트들
- QA 도구들

**새로운 시스템**:
- Deliverable 시스템 (`umis_rag/deliverables/`)
- 통합된 생성 및 검증

### 4. 검증 도구 통합

**Deprecated**:
- 개별 검증 스크립트들
- 진단 도구들

**새로운 시스템**:
- `test_all_improvements.py` - 통합 테스트
- `test_schema_contract.py` - 스키마 검증

---

## 📝 Documentation

각 archive 폴더에 README.md 추가:

1. **`archive/guestimation_v3/README.md`**
   - 이동된 파일 목록
   - 아키텍처 변경 설명
   - 새로운 시스템 참조

2. **`archive/deprecated_scripts/README.md`**
   - 카테고리별 파일 목록
   - 대체 도구 안내
   - 복구 가이드

3. **`scripts/README.md` (업데이트)**
   - 현재 사용 중인 스크립트만 반영
   - Archive 섹션 추가
   - v7.7.0 기준으로 업데이트

---

## ✅ 완료 항목

- [x] Guestimation v3 테스트 11개 이동
- [x] SGA 파서 18개 이동
- [x] Excel 테스트 22개 이동
- [x] 검증 도구 14개 이동
- [x] 빌드 도구 6개 이동
- [x] Archive README 작성 (2개)
- [x] scripts/README.md 업데이트
- [x] 최종 보고서 작성 (본 문서)

---

## 🎯 결과

### Before (정리 전)
- scripts/ 폴더: **110개 파일** (Python)
- 혼재된 active/deprecated 스크립트
- 불명확한 사용 여부

### After (정리 후)
- scripts/ 폴더: **39개 파일** (Python)
- 모두 active 스크립트
- 명확한 분류 및 문서화
- archive/ 폴더: **71개 파일** (deprecated)

### 개선 효과
- **64% 감소** (110개 → 39개)
- 명확한 스크립트 목적
- 빠른 파일 검색
- 혼란 감소

---

## 📚 관련 문서

- `archive/guestimation_v3/README.md` - Guestimation v3 상세
- `archive/deprecated_scripts/README.md` - Deprecated 스크립트 상세
- `scripts/README.md` - 현재 스크립트 가이드
- `dev_docs/estimator/` - Estimator 개발 문서

---

**작업 완료**: 2025-11-20  
**작업자**: AI Assistant  
**버전**: v7.7.0

