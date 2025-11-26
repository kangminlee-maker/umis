# Archive: tests v7.10.2

**보관 일자**: 2025-11-26
**이유**: v7.11.0 Fusion Architecture - Phase 0-4 → Stage 1-4로 대체

---

## 📁 구조

```
archive/tests_v7.10.2/
├── test_estimator_phase0_4.py
├── test_phase_0_4_comprehensive.py
├── test_phase2_threshold.py
├── integration/
│   └── test_hybrid_integration.py
├── unit/
│   └── test_hybrid_architecture.py
├── COMPREHENSIVE_TEST_REPORT.md
├── ESTIMATOR_PHASE0_4_TEST_REPORT.md
├── PHASE3_PHASE4_FIX_REPORT.md
├── PHASE4_FINAL_TEST_REPORT.md
├── TEST_RESULTS_v7_8_1.md
└── README.md (이 파일)
```

---

## 🎯 Phase 0-4 Architecture

### 구조
```
Phase 0: Literal Evidence (프로젝트 데이터)
Phase 1: Direct RAG (학습 규칙)
Phase 2: Validator Search (확정 데이터, 85%)
Phase 3: Guestimation (LLM 직접 추정)
Phase 4: Fermi Decomposition (재귀, max_depth=4)
```

---

## 🔄 v7.11.0 변경사항

### Architecture 변경
| 항목 | v7.10.2 | v7.11.0 |
|------|---------|---------|
| 구조 | Phase 0-4 (5단계) | Stage 1-4 (4단계) |
| Phase 0 | Literal Evidence | Evidence Collection (통합) |
| Phase 1 | Direct RAG | ↑ Stage 1 |
| Phase 2 | Validator Search | ↑ Stage 1 |
| Phase 3 | Guestimation | Generative Prior (Stage 2) |
| Phase 4 | Fermi (재귀) | Structural Explanation (Stage 3, 재귀 없음) |
| - | - | Fusion & Validation (Stage 4, 신규) |

### 용어 개선
- `phase` → `source` (추정 소스)
- `confidence` → `certainty` (LLM 확신도)
- `PhaseConfig` → `Budget` (자원 제어)

---

## 📚 보관된 테스트

### Phase 0-4 테스트
- `test_estimator_phase0_4.py` - Phase 0-4 통합 테스트
- `test_phase_0_4_comprehensive.py` - 종합 테스트
- `test_phase2_threshold.py` - Phase 2 threshold 테스트

### Hybrid Architecture 테스트
- `integration/test_hybrid_integration.py` - Hybrid 통합 (v7.10.0)
- `unit/test_hybrid_architecture.py` - Hybrid 단위 테스트

### 보고서
- `COMPREHENSIVE_TEST_REPORT.md` - 종합 테스트 보고서
- `ESTIMATOR_PHASE0_4_TEST_REPORT.md` - Phase 0-4 테스트 보고서
- `PHASE3_PHASE4_FIX_REPORT.md` - Phase 3-4 버그 수정
- `PHASE4_FINAL_TEST_REPORT.md` - Phase 4 최종 테스트
- `TEST_RESULTS_v7_8_1.md` - v7.8.1 테스트 결과

---

## ⚠️ 주의사항

### 이 테스트들은 Archive입니다
- v7.11.0에서 더 이상 유효하지 않습니다
- 히스토리 참고용으로만 사용하세요
- 새 테스트는 `tests/` 폴더 참조

### v7.11.0 새 테스트
Stage 기반 테스트:
- `tests/unit/test_prior_estimator.py` (Stage 2)
- `tests/unit/test_fermi_estimator.py` (Stage 3)
- `tests/integration/test_stage_flow_v7_11_0.py`
- `tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py`

---

## 📞 문의

**v7.11.0 관련**:
- 문서: `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md`

**Archive 복원**:
- Git history에서 복원 가능

---

**보관**: 2025-11-26
**Phase 0-4 → Stage 1-4** 🎉
