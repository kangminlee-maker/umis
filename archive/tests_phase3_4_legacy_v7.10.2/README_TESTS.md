# Archive: Phase 3-4 Legacy Tests (v7.10.2)

**날짜:** 2025-11-26  
**버전:** v7.11.0 Migration  
**위치:** `archive/tests_phase3_4_legacy_v7.10.2/`

---

## 📋 Archive 내용

### Unit Tests (2개)
- `test_phase3_guestimation.py` → `tests/unit/test_prior_estimator.py`
- `test_phase4_fermi.py` → `tests/unit/test_fermi_estimator.py`

### Integration Tests (1개)
- `test_phase_flow.py` → `tests/integration/test_stage_flow_v7_11_0.py`

### Benchmark/Regression Tests (6개)
- `test_phase4_model_config.py` (Phase 4 Model Config)
- `test_phase4_creative.py` (Phase 4 Creative 테스트)
- `test_phase4_quick.py` (Phase 4 Quick 테스트)
- `test_phase4_quick_final.py` (Phase 4 Quick Final)
- `test_phase4_parsing_fix.py` (Phase 4 JSON Parsing Fix)
- `test_estimator_comprehensive.py` (Estimator Comprehensive)

### Performance Tests (1개)
- `test_performance.py` (Phase 3-4 성능 테스트)

---

## 🎯 Archive 이유

### v7.11.0 Fusion Architecture 도입
- **재귀 제거**: Phase 4 재귀 로직 완전 제거 → 테스트 불필요
- **Stage 기반 설계**: Phase 0-4 → Stage 1-4 (Evidence → Prior → Fermi → Fusion)
- **Budget 기반 탐색**: Phase3Config/Phase4Config → Budget (max_llm_calls, max_depth=2)
- **Certainty 도입**: confidence → certainty (high/medium/low)

### 특정 테스트별 이유

#### `test_phase4_model_config.py`
- Phase 4 재귀 전용 Config 테스트
- Step 1-4 (Create/Execute/Recursive/Synthesize) 검증
- v7.11.0: 재귀 제거, Step 개념 폐기

#### `test_phase4_creative.py`
- Phase 4 Creative 모드 테스트
- 재귀 기반 창의적 모형 생성
- v7.11.0: PriorEstimator로 대체

#### `test_phase4_quick*.py`
- Phase 4 재귀 로직 Quick 테스트
- Backtracking, 순환 의존성 검증
- v7.11.0: max_depth=2, 재귀 금지

#### `test_phase4_parsing_fix.py`
- Phase 4 JSON Parsing 버그 수정 테스트
- v7.10.2 특정 버그 검증
- v7.11.0: FermiEstimator 새 구현으로 불필요

#### `test_estimator_comprehensive.py`
- Phase 0-4 전체 Comprehensive 테스트
- Phase Fallback 로직 (0→1→2→3→4)
- v7.11.0: Stage 독립성 (Early Return), `test_stage_comprehensive_v7_11_0.py`로 대체

#### `test_performance.py`
- Phase 3-4 성능 테스트 (재귀 포함)
- v7.11.0: 재귀 제거로 성능 메트릭 변경

---

## 🔄 대체 테스트

### Unit Tests
| Legacy | v7.11.0 Replacement |
|--------|---------------------|
| `test_phase3_guestimation.py` | `tests/unit/test_prior_estimator.py` |
| `test_phase4_fermi.py` | `tests/unit/test_fermi_estimator.py` |

### Integration Tests
| Legacy | v7.11.0 Replacement |
|--------|---------------------|
| `test_phase_flow.py` | `tests/integration/test_stage_flow_v7_11_0.py` |

### Comprehensive Tests
| Legacy | v7.11.0 Replacement |
|--------|---------------------|
| `test_estimator_comprehensive.py` | `tests/test_stage_comprehensive_v7_11_0.py` (예정) |

### Performance Tests
| Legacy | v7.11.0 Replacement |
|--------|---------------------|
| `test_performance.py` | `tests/performance/test_stage_performance_v7_11_0.py` (예정) |

---

## 📌 복원 방법

### 롤백 필요 시
```bash
# 1. Archive에서 복원
cp archive/tests_phase3_4_legacy_v7.10.2/test_*.py tests/

# 2. 레거시 코드 복원
cp archive/phase3_4_legacy_v7.10.2/*.py umis_rag/agents/estimator/

# 3. 레거시 브랜치로 체크아웃
git checkout v7.10.2
```

### 참조용 (읽기 전용)
- Archive 파일은 참조용으로 유지
- 롤백 가능성 대비 (프로덕션 배포 후 1-2주)
- Phase 1.4 (Phase 6.4)에서 최종 제거 검토

---

## ✅ 검증

### Archive 완료 체크
- [x] Unit Tests (2개)
- [x] Integration Tests (1개)
- [x] Benchmark Tests (6개)
- [x] Performance Tests (1개)
- [x] README 작성

### 대체 파일 생성 체크
- [x] `tests/unit/test_prior_estimator.py`
- [x] `tests/unit/test_fermi_estimator.py`
- [x] `tests/integration/test_stage_flow_v7_11_0.py`
- [ ] `tests/test_stage_comprehensive_v7_11_0.py` (TODO: Phase 3.3)
- [ ] `tests/performance/test_stage_performance_v7_11_0.py` (TODO: Phase 3.3)

---

## 📚 관련 문서
- `/dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md`
- `/dev_docs/improvements/TEST_CATALOG_v7_11_0.md`
- `/MIGRATION_QUICKSTART_v7_11_0.md`

