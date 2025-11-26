# 문서 정리 계획 v7.11.0

**작성일**: 2025-11-26
**목적**: v7.11.0 마이그레이션 완료 후 누적된 문서/로그 정리

---

## 📊 현재 상태

### dev_docs/improvements
- **총 48개 문서**
- Phase 0-4 관련: 20개
- v7.8.x: 5개
- v7.9.0: 6개
- v7.10.0: 8개
- v7.11.0: 18개

### Root 폴더
- **Log 파일**: 25개
- **MD 파일**: 6개 (README 제외)
- **JSON 파일**: 2개

---

## 🎯 정리 기준

### 1. Archive 이동 대상

#### A. Phase 5 Architecture 관련 (v7.7.0 이전)
- Phase 0-4 (5단계) 구조 관련 모든 문서
- v7.7.0 이전 버전 문서

#### B. v7.8.x 미만 문서
- v7.7.0 이하 모든 문서
- 단, 히스토리 가치가 있는 문서는 보관

#### C. v7.8.x ~ v7.9.x 문서
- Phase 0-4 관련 문서 (Stage 1-4로 대체됨)
- Native/External 모드 레거시 (Model Config로 통합됨)

#### D. v7.10.0 문서
- Hybrid Architecture 관련 (v7.11.0 Fusion으로 대체)
- Phase 0-4 Redesign 관련

### 2. 보관 대상 (dev_docs/improvements)

#### A. v7.11.0 핵심 문서 (18개)
- V7_11_0_MIGRATION_COMPLETE.md ⭐ 최종 보고서
- PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md
- BUDGET_CONFIGURATION_GUIDE_v7_11_0.md
- STAGE3_BUDGET_GUIDE_v7_11_0.md
- E2E_NATIVE_MODE_SUPPORT_v7_11_0.md
- E2E_NATIVE_MODE_VERIFICATION_v7_11_0.md
- PHASE6_1_TEST_RESULTS_v7_11_0.md
- PHASE6_3_E2E_SCENARIOS_v7_11_0.md
- CONFIG_REFACTORING_DESIGN_v7_11_0.md
- DEPENDENCY_ANALYSIS_v7_11_0.md
- DOCS_INVENTORY_v7_11_0.md
- MIGRATION_DESIGN_COMPLETE_v7_11_0.md
- MIGRATION_STRATEGY_SUMMARY_v7_11_0.md
- EVIDENCE_COLLECTOR_IMPLEMENTATION_v7_11_0.md
- IMPLEMENTATION_COMPLETE_v7_11_0.md
- PHASE0_GUARDRAIL_IMPLEMENTATION_v7_11_0.md
- PHASE3_COMPLETE_v7_11_0.md
- SOURCE_COLLECTOR_ANALYSIS_v7_11_0.md
- TEST_CATALOG_v7_11_0.md
- PHASE3_4_IMPLEMENTATION_CHECKLIST_v7_11_0.md
- PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md

#### B. 히스토리 가치가 있는 문서
- PRODUCTION_QUALITY_ROADMAP_COMPLETE_v7_9_0.md (완료 보고서)

### 3. Root 폴더 정리

#### A. 삭제 대상 (Log 파일, 25개)
```
gpt51_with_conceptual_test.log
test_model_config_live_output.log
benchmark_run_20251121_111609.log
extended_test_output.log
gpt51_medium_effort_test_fixed.log
test_v7_11_0_recursive_explosion_check.log
test_v7_11_0_fermi_10problems_run2.log
estimator_phase0_4_test.log
phase4_test_output.log
gpt51_test.log
fermi_test_output.log
gpt51_medium_effort_test.log
benchmark_run.log
gpt51_strict_prompt_test.log
recursive_explosion_test.log
gpt51_optimized_test.log
test_v7_11_0_fermi_10problems.log
v7_11_0_test_output.log
```

이유: 테스트 실행 로그, 재현 불필요

#### B. 보관 (Root → 적절한 폴더)
```
CHANGELOG.md → 그대로 유지 (중요!)
README.md → 그대로 유지 (중요!)
MIGRATION_QUICKSTART_v7_11_0.md → docs/
V7_11_0_FINAL_SUMMARY.md → dev_docs/improvements/
PULL_REQUEST_v7_11_0.md → dev_docs/deployment/
CHECKLIST_v7_11_0_COMPLETE.md → dev_docs/deployment/
TEST_RESULTS_V7_11_0_RECURSIVE_EXPLOSION.md → tests/results/
```

#### C. 삭제 대상 (JSON 파일)
```
test_v7_11_0_recursive_explosion_20251126_082542.json
phase4_final_test_20251125_223558.json
```

이유: 테스트 결과, 보고서에 통합됨

---

## 📁 Archive 폴더 구조

```
archive/
  └─ dev_docs_v7.10.2_and_below/
      ├─ improvements/
      │   ├─ v7_8_x/
      │   │   ├─ NATIVE_EXTERNAL_LEGACY_REMOVAL_v7_8_1.md
      │   │   ├─ PHASE_0_4_TEST_RESULTS_v7_8_1.md
      │   │   ├─ PHASE_3_4_IMPROVEMENTS_v7_8_1.md
      │   │   ├─ SOURCE_TYPE_FIX_v7_8_1.md
      │   │   └─ V7_8_1_LEGACY_REMOVAL_COMPLETE_SUMMARY.md
      │   ├─ v7_9_x/
      │   │   ├─ PHASE_0_COMPLETE_v7_9_0.md
      │   │   ├─ PHASE_1_COMPLETE_v7_9_0.md
      │   │   ├─ PHASE_2_COMPLETE_v7_9_0.md
      │   │   ├─ PHASE_2_PROGRESS_v7_9_0.md
      │   │   ├─ PHASE_3_PLAN_v7_9_0.md
      │   │   └─ PRODUCTION_QUALITY_ROADMAP_v7_9_0.md
      │   └─ v7_10_x/
      │       ├─ BENCHMARK_PATTERNS_FOR_PHASE_0_4.md
      │       ├─ FEEDBACK_REVIEW_v7_10_0.md
      │       ├─ HYBRID_ARCHITECTURE_EXPLAINED.md
      │       ├─ HYBRID_ARCHITECTURE_SUMMARY_v7_10_0.md
      │       ├─ PHASE_0_4_FINAL_SYNTHESIS_v7_10_0.md
      │       ├─ PHASE_0_4_REDESIGN_ANALYSIS_v7_10_0.md
      │       ├─ WEEK1_COMPLETE_v7_10_0.md
      │       ├─ WEEK1_SUMMARY_v7_10_0.md
      │       ├─ WEEK2_FINAL_STATUS_v7_10_0.md
      │       ├─ WEEK2_PROGRESS_v7_10_0.md
      │       ├─ YAML_REVIEW_v7_10_0.md
      │       └─ estimator_work_domain_v7_10_0.yaml
      └─ README.md (Archive 설명)
```

---

## 🚀 실행 계획

### Phase 1: Archive 폴더 생성
```bash
mkdir -p archive/dev_docs_v7.10.2_and_below/improvements/{v7_8_x,v7_9_x,v7_10_x}
```

### Phase 2: dev_docs 문서 이동

#### v7.8.x (5개)
```bash
mv dev_docs/improvements/NATIVE_EXTERNAL_LEGACY_REMOVAL_v7_8_1.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
mv dev_docs/improvements/NATIVE_EXTERNAL_LEGACY_REMOVAL_COMPLETE_v7_8_1.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
mv dev_docs/improvements/PHASE_0_4_TEST_RESULTS_v7_8_1.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
mv dev_docs/improvements/PHASE_3_4_IMPROVEMENTS_v7_8_1.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
mv dev_docs/improvements/SOURCE_TYPE_FIX_v7_8_1.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
mv dev_docs/improvements/V7_8_1_LEGACY_REMOVAL_COMPLETE_SUMMARY.md archive/dev_docs_v7.10.2_and_below/improvements/v7_8_x/
```

#### v7.9.x (6개)
```bash
mv dev_docs/improvements/PHASE_0_COMPLETE_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PHASE_1_COMPLETE_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PHASE_2_COMPLETE_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PHASE_2_PROGRESS_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PHASE_3_PLAN_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PRODUCTION_QUALITY_ROADMAP_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
mv dev_docs/improvements/PRODUCTION_QUALITY_ROADMAP_COMPLETE_v7_9_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_9_x/
```

#### v7.10.x (12개)
```bash
mv dev_docs/improvements/BENCHMARK_PATTERNS_FOR_PHASE_0_4.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/FEEDBACK_REVIEW_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/HYBRID_ARCHITECTURE_EXPLAINED.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/HYBRID_ARCHITECTURE_SUMMARY_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/PHASE_0_4_FINAL_SYNTHESIS_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/PHASE_0_4_REDESIGN_ANALYSIS_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/WEEK1_COMPLETE_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/WEEK1_SUMMARY_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/WEEK2_FINAL_STATUS_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/WEEK2_PROGRESS_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/YAML_REVIEW_v7_10_0.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/estimator_work_domain_v7_10_0.yaml archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/PHASE0_TASK1_COMPLETED.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
mv dev_docs/improvements/PHASE0_TASK2_COMPLETED.md archive/dev_docs_v7.10.2_and_below/improvements/v7_10_x/
```

### Phase 3: Root 폴더 정리

#### 3.1. 문서 이동
```bash
# docs/로 이동
mv MIGRATION_QUICKSTART_v7_11_0.md docs/

# dev_docs/improvements/로 이동
mv V7_11_0_FINAL_SUMMARY.md dev_docs/improvements/

# dev_docs/deployment/ 폴더 생성 후 이동
mkdir -p dev_docs/deployment
mv PULL_REQUEST_v7_11_0.md dev_docs/deployment/
mv CHECKLIST_v7_11_0_COMPLETE.md dev_docs/deployment/

# tests/results/ 폴더 생성 후 이동
mkdir -p tests/results
mv TEST_RESULTS_V7_11_0_RECURSIVE_EXPLOSION.md tests/results/
```

#### 3.2. Log 파일 삭제 (25개)
```bash
rm gpt51_*.log
rm test_*.log
rm benchmark_*.log
rm estimator_*.log
rm phase4_*.log
rm fermi_*.log
rm recursive_*.log
rm extended_*.log
rm v7_11_0_*.log
```

#### 3.3. JSON 파일 삭제 (2개)
```bash
rm test_v7_11_0_recursive_explosion_20251126_082542.json
rm phase4_final_test_20251125_223558.json
```

### Phase 4: Archive README 생성
```bash
cat > archive/dev_docs_v7.10.2_and_below/README.md << 'EOF'
# Archive: dev_docs v7.10.2 and Below

이 폴더는 v7.11.0 Fusion Architecture 마이그레이션 이전 버전의 개발 문서를 보관합니다.

## 구조

- `v7_8_x/`: v7.8.x 버전 관련 문서 (Native/External 모드 개선)
- `v7_9_x/`: v7.9.0 버전 관련 문서 (Phase 0-2 완료)
- `v7_10_x/`: v7.10.x 버전 관련 문서 (Hybrid Architecture)

## 히스토리

- **v7.8.x**: Native/External 모드 통합, Model Config 시스템
- **v7.9.0**: Phase 0-2 완료, Production Quality Roadmap
- **v7.10.x**: Hybrid Architecture, Phase 0-4 Redesign

## v7.11.0 변경사항

v7.11.0에서 다음과 같이 대체되었습니다:
- Phase 0-4 (5단계) → Stage 1-4 (4단계)
- Phase 4 재귀 → Stage 3 Fermi (재귀 없음)
- PhaseConfig → Budget
- confidence → certainty

## 참고

현재 버전 문서: `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md`
EOF
```

---

## 📊 정리 후 상태

### dev_docs/improvements
- **v7.11.0 문서만 보관**: 21개
- **정리 비율**: 48개 → 21개 (56% 감소)

### Root 폴더
- **CHANGELOG.md**: 유지
- **README.md**: 유지
- **Log 파일**: 0개 (25개 삭제)
- **기타 MD**: 0개 (적절한 폴더로 이동)

### archive/
- **v7.8.x**: 6개
- **v7.9.x**: 7개
- **v7.10.x**: 14개
- **총 27개 문서 Archive**

---

## ✅ 체크리스트

- [ ] Phase 1: Archive 폴더 생성
- [ ] Phase 2: dev_docs 문서 이동 (23개)
- [ ] Phase 3.1: Root 문서 이동 (5개)
- [ ] Phase 3.2: Root log 파일 삭제 (25개)
- [ ] Phase 3.3: Root JSON 파일 삭제 (2개)
- [ ] Phase 4: Archive README 생성
- [ ] Git commit & push

---

**예상 소요 시간**: 10분
**위험도**: 낮음 (Archive로 이동, 복구 가능)
