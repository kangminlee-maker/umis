# Phase → Stage 마이그레이션 작업 리스트 설계 완료

**날짜:** 2025-11-26  
**버전:** v7.11.0  
**상태:** ✅ 설계 완료, 실행 대기

---

## 📋 작업 개요

### 목표
**Phase 5 기반 레거시 아키텍처를 Stage 4 Fusion Architecture로 100% 전환**

### 범위
- **코드:** 4개 레거시 파일 (총 5,257줄) Archive 이동
- **테스트:** 38개 테스트 파일 전환 또는 Archive
- **문서:** 156개 문서 업데이트 (우선순위별)
- **Config:** 3개 주요 파일 리팩터링

### 예상 소요
- **최소:** 6일 (집중 작업)
- **현실:** 7-10일 (디버깅 포함)

---

## 📊 산출물 목록

### 1. 메인 작업 리스트
**파일:** `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md`

**내용:**
- 141줄, 6-Phase 상세 작업 계획
- 24개 Major Tasks, 100+ Sub-tasks
- Task별 체크리스트, 예상 시간, 산출물 정의
- 리스크 관리 (High/Medium/Low)
- 성공 기준 (Mandatory/Recommended/Stretch)

**구조:**
```
Phase 1: 사전 분석 및 준비 (1일)
  Task 1.1: 의존성 트리 완전 분석
  Task 1.2: 테스트 카탈로그 작성
  Task 1.3: 문서 인벤토리
  Task 1.4: Config 파일 변경점 설계

Phase 2: 코드 리팩터링 (2일)
  Task 2.1: Phase 3-4 파일 Archive 이동
  Task 2.2: Import 리다이렉트 레이어 구현
  Task 2.3: Source Collector & Utilities 마이그레이션
  Task 2.4: Models.py 정리
  Task 2.5: 순환 의존성 해결

Phase 3: 테스트 마이그레이션 (1일)
  Task 3.1-3.4: Unit/Integration/Benchmark/AB Testing

Phase 4: 문서 업데이트 (1일)
  Task 4.1-4.4: API/Architecture/History/README

Phase 5: Config & 시스템 통합 (0.5일)
  Task 5.1-5.3: model_configs.yaml, fermi_model_search.yaml, tool_registry.yaml

Phase 6: 최종 검증 및 Clean-up (0.5일)
  Task 6.1-6.4: 전체 테스트, Import 검증, E2E, 최종 제거
```

---

### 2. 퀵스타트 가이드
**파일:** `MIGRATION_QUICKSTART_v7_11_0.md`

**내용:**
- 132줄, 3분 요약 + 실행 가이드
- Phase별 작업 개요 테이블
- 24-Task 체크리스트
- 시작 방법 (Git branch, 첫 작업)
- 핵심 리스크 3가지
- 성공 기준

**특징:**
- 빠른 실행을 위한 간략 버전
- 체크리스트 중심
- 명령어 포함

---

### 3. 전략 요약
**파일:** `dev_docs/improvements/MIGRATION_STRATEGY_SUMMARY_v7_11_0.md`

**내용:**
- 100줄, 전략 중심 설명
- 현황 분석 (완료/제거 대상/영향 범위)
- 점진적 제거 전략 설명
- 3대 리스크 & 대응책 상세
- 주요 파일 매핑
- 타임라인 (Week 1-4+)

**특징:**
- 리스크 중심 접근
- 호환성 레이어 전략 상세
- Breaking Change 최소화 방안

---

## 🎯 핵심 설계 결정

### 1. 점진적 제거 (Graceful Deprecation)
**이유:**
- 프로덕션 환경 안정성 보장
- 롤백 가능성 유지
- 사용자 혼란 최소화

**구현:**
```python
# compat.py (호환성 레이어)
from .prior_estimator import PriorEstimator as Phase3Guestimation
import warnings
warnings.warn("Phase3Guestimation은 Deprecated입니다.", DeprecationWarning)
```

---

### 2. Archive 우선, 삭제 나중
**이유:**
- 3,460줄 `phase4_fermi.py` 즉시 삭제 리스크 높음
- 롤백 시나리오 대비
- 역사적 가치 (참고용)

**구조:**
```
archive/phase3_4_legacy_v7.10.2/
  phase3_guestimation.py
  phase3_range_engine.py
  phase4_fermi.py
  estimator_v7.10.2.py
  README.md (이동 사유)
```

---

### 3. 테스트 Coverage 80% 유지
**이유:**
- 품질 보증
- 프로덕션 신뢰성

**전략:**
- 자동 전환 가능 테스트 (20개): Import만 수정
- 수동 재작성 (10개): Stage 독립성, Budget 테스트
- Archive (8개): 레거시 전용 테스트

---

### 4. Config 하위 호환성
**이유:**
- 환경변수 `LLM_MODEL_PHASE3`, `LLM_MODEL_PHASE4` 계속 동작
- 기존 배포 환경 영향 최소화

**구현:**
```yaml
# model_configs.yaml
stages:
  stage_2_generative_prior:
    default_model: gpt-4o-mini
    legacy_alias: phase_3  # LLM_MODEL_PHASE3 → Stage 2
```

---

## 🚨 리스크 관리 전략

### High Risk: 순환 의존성
```
phase4_fermi.py → phase3_guestimation.py
```
**대응:** Archive 이동 시 자동 해결 (둘 다 제거)

---

### High Risk: 테스트 대량 손실
**대응:**
- 테스트 카탈로그 작성 (Task 1.2)
- 전환 가능성 사전 평가
- Coverage 80% 목표

---

### High Risk: Breaking Change
**대응:**
1. `compat.py` (호환성 레이어)
2. `EstimationResult.phase` → Property (하위 호환)
3. Config Alias (환경변수 호환)
4. Deprecation Warning (안내)

---

## 📊 TODO 관리

### 총 27개 TODO 생성
- ✅ 2개 완료 (Phase 0, Guardrail Engine)
- 🔄 1개 진행 중 (Phase → Stage 마이그레이션)
- ⏳ 24개 대기 (Phase 1.1 ~ 6.4)

### TODO 구조
```
phase_to_stage_migration (in_progress)
├── phase1_dependency_analysis (pending)
├── phase1_test_catalog (pending)
├── phase1_docs_inventory (pending)
├── phase1_config_design (pending)
├── phase2_archive_move (pending)
├── phase2_import_redirect (pending)
├── phase2_utilities_migration (pending)
├── phase2_models_cleanup (pending)
├── phase2_circular_deps (pending)
├── phase3_unit_tests (pending)
├── phase3_integration_tests (pending)
├── phase3_benchmark_tests (pending)
├── phase3_ab_testing (pending)
├── phase4_user_docs (pending)
├── phase4_system_docs (pending)
├── phase4_dev_history (pending)
├── phase4_readme (pending)
├── phase5_model_configs (pending)
├── phase5_fermi_config (pending)
├── phase5_tool_registry (pending)
├── phase6_all_tests (pending)
├── phase6_import_verification (pending)
├── phase6_e2e_scenarios (pending)
└── phase6_legacy_removal (pending)
```

---

## 🎯 다음 단계

### Immediate (지금 바로)
1. **사용자 승인 대기**
   - 작업 리스트 검토
   - 우선순위 조정 (필요 시)
   - 일정 확정

2. **실행 준비**
   ```bash
   git checkout -b feature/phase-to-stage-migration-v7.11.0
   ```

### Phase 1 시작 (승인 후)
1. **Task 1.1:** 의존성 트리 분석
   ```bash
   rg "from.*phase[34]|import.*Phase[34]" --type py -l > phase_imports.txt
   wc -l phase_imports.txt
   ```

2. **Task 1.2:** 테스트 카탈로그
   ```bash
   rg "phase.*[34]" tests/ --type py -l | wc -l
   ```

3. **Task 1.3:** 문서 인벤토리
   ```bash
   rg "Phase [34]|phase_[34]" dev_docs/ --type md -l | wc -l
   ```

---

## 📈 예상 결과

### 코드 품질
- ✅ 순환 의존성 0건
- ✅ Import 에러 0건
- ✅ Test Coverage 80%+
- ✅ Linting 통과

### 아키텍처
- ✅ 100% Stage 기반 (Phase 완전 제거)
- ✅ 재귀 0건 (Budget 기반 탐색)
- ✅ 모듈 독립성 강화
- ✅ 호환성 레이어 (2주 후 제거 가능)

### 문서
- ✅ API 문서 v7.11.0
- ✅ Architecture 업데이트
- ✅ 마이그레이션 가이드
- ✅ README 갱신

---

## 📚 참고 문서

1. **Full Plan (141줄):**  
   `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md`

2. **Quickstart (132줄):**  
   `MIGRATION_QUICKSTART_v7_11_0.md`

3. **Strategy Summary (100줄):**  
   `dev_docs/improvements/MIGRATION_STRATEGY_SUMMARY_v7_11_0.md`

4. **v7.11.0 Design (1,119줄):**  
   `dev_docs/improvements/PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md`

5. **umis.yaml:**  
   Lines 4880+ (Estimator, Stage 기반)

---

## ✅ 체크리스트 (설계 단계)

- [x] 현황 분석 완료
- [x] 레거시 파일 식별 (4개, 5,257줄)
- [x] 영향 범위 파악 (38 tests, 156 docs, 3 configs)
- [x] 리스크 식별 (순환 의존성, 테스트, Breaking Change)
- [x] 전략 수립 (점진적 제거, Archive 우선)
- [x] 6-Phase 24-Task 작업 계획
- [x] TODO 관리 시스템 (27개 TODO)
- [x] 3개 문서 작성 (Plan, Quickstart, Strategy)
- [x] 성공 기준 정의
- [x] 타임라인 수립 (6-10일)

---

## 🎉 결론

**Phase → Stage 마이그레이션 작업 리스트 설계 완료!**

### 핵심 성과
1. ✅ **141줄 상세 작업 계획** (Phase 1-6, 24 Major Tasks)
2. ✅ **132줄 퀵스타트 가이드** (체크리스트 중심)
3. ✅ **100줄 전략 요약** (리스크 중심)
4. ✅ **27개 TODO 관리** (Cursor 통합)
5. ✅ **리스크 관리 전략** (High/Medium/Low)
6. ✅ **호환성 레이어 설계** (compat.py, Property Alias, Config Alias)

### 다음 단계
- **사용자 검토 및 승인 대기**
- **승인 후 즉시 Phase 1 시작 가능**

---

**작성자:** AI Assistant  
**작성일:** 2025-11-26  
**버전:** v1.0

**끝.**

