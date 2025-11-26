# Phase → Stage 마이그레이션 퀵스타트 (v7.11.0)

**🎯 목표:** Phase 5 → Stage 4 Fusion Architecture 100% 전환  
**📅 예상 소요:** 6-10일  
**📊 난이도:** ★★★★★

---

## 📌 3분 요약

### 현재 상황
- ✅ **v7.11.0 Stage 4 아키텍처 완성**
  - `estimator.py`, `evidence_collector.py`, `prior_estimator.py`, `fermi_estimator.py`, `fusion_layer.py`
  - Stage 1-4 기반 완전 재설계
- ❌ **레거시 Phase 3-4 아직 존재**
  - `phase3_guestimation.py` (466줄)
  - `phase3_range_engine.py` (131줄)
  - `phase4_fermi.py` (3,460줄! 대형 파일)
  - 38개 테스트, 156개 문서, Config 파일들이 Phase 3-4 참조

### 전환 전략
**점진적 제거 (Graceful Deprecation):**
1. Archive 이동 → Import 리다이렉트
2. 테스트 전환 → 문서 업데이트
3. 최종 검증 → 프로덕션 배포 후 완전 제거

---

## 🚀 Phase별 작업 개요

| Phase | 작업 | 소요 | 주요 산출물 |
|-------|-----|-----|----------|
| **Phase 1** | 사전 분석 및 준비 | 1일 | 의존성 분석, 테스트 카탈로그, 문서 인벤토리 |
| **Phase 2** | 코드 리팩터링 | 2일 | Archive 이동, compat.py, Models 정리 |
| **Phase 3** | 테스트 마이그레이션 | 1일 | Unit/Integration/Benchmark 전환 |
| **Phase 4** | 문서 업데이트 | 1일 | API 문서, 아키텍처, README |
| **Phase 5** | Config & 통합 | 0.5일 | model_configs.yaml, tool_registry.yaml |
| **Phase 6** | 최종 검증 | 0.5일 | 전체 테스트, E2E 시나리오 |

---

## 📋 체크리스트 (24개 Task)

### ✅ Phase 0: 준비
- [x] Fusion Architecture v7.11.0 구현 완료
- [x] 작업 리스트 설계 완료

### 🔍 Phase 1: 사전 분석 (4 tasks)
- [ ] 1.1: 의존성 트리 분석 (`rg "from.*phase[34]" --type py -l`)
- [ ] 1.2: 테스트 카탈로그 작성 (38개 파일 분류)
- [ ] 1.3: 문서 인벤토리 (156개 파일 스캔)
- [ ] 1.4: Config 변경점 설계

### 🔧 Phase 2: 코드 리팩터링 (5 tasks)
- [ ] 2.1: Phase 3-4 파일 Archive 이동
- [ ] 2.2: Import 리다이렉트 (`compat.py` 생성)
- [ ] 2.3: Source Collector & Utilities 마이그레이션
- [ ] 2.4: Models.py 정리 (`Phase3Config` → Alias)
- [ ] 2.5: 순환 의존성 해결

### 🧪 Phase 3: 테스트 마이그레이션 (4 tasks)
- [ ] 3.1: Unit Tests 전환 (`test_prior_estimator.py`)
- [ ] 3.2: Integration Tests (`test_stage_flow_v7_11_0.py`)
- [ ] 3.3: Benchmark Tests 정리 (10개+ 파일)
- [ ] 3.4: AB Testing Framework 업데이트

### 📄 Phase 4: 문서 업데이트 (4 tasks)
- [ ] 4.1: API 문서 (`ESTIMATOR_API_v7_11_0.md`)
- [ ] 4.2: 아키텍처 (`UMIS_ARCHITECTURE_BLUEPRINT.md`)
- [ ] 4.3: 마이그레이션 가이드 (`v7_11_0_MIGRATION_COMPLETE.md`)
- [ ] 4.4: README 업데이트

### ⚙️ Phase 5: Config & 통합 (3 tasks)
- [ ] 5.1: `model_configs.yaml` 리팩터링 (Stage 기반)
- [ ] 5.2: `fermi_model_search.yaml` Archive 이동
- [ ] 5.3: `tool_registry.yaml` 업데이트

### ✅ Phase 6: 최종 검증 (4 tasks)
- [ ] 6.1: 전체 테스트 실행 (100% Pass)
- [ ] 6.2: Import 검증
- [ ] 6.3: E2E 시나리오 10개
- [ ] 6.4: 레거시 최종 제거 (배포 후 1-2주)

---

## 🎯 시작 방법

### 1. Git Branch 생성
```bash
git checkout -b feature/phase-to-stage-migration-v7.11.0
```

### 2. Phase 1.1 시작 (의존성 분석)
```bash
# Import 스캔
rg "from.*phase[34]|import.*Phase[34]" --type py -l > phase_imports.txt

# 파일 수 확인
wc -l phase_imports.txt
```

### 3. TODO 관리
```bash
# 상세 작업 리스트 확인
cat dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md
```

---

## 🚨 핵심 리스크 3가지

### 1. 순환 참조
- **문제:** `phase4_fermi.py` → `phase3_guestimation.py`
- **대응:** Task 2.5에서 철저히 검증, Archive 이동 시 자동 해결

### 2. 테스트 대량 손실
- **문제:** 38개 테스트 파일 영향
- **대응:** 커버리지 80% 유지 목표, Archive에 백업

### 3. Breaking Change
- **문제:** 프로덕션 환경 영향
- **대응:** Deprecation Warning + 호환성 레이어 (`compat.py`)

---

## 📊 성공 기준

### Must Have (필수)
- ✅ 모든 테스트 통과 (100% Pass Rate)
- ✅ 0 Import Errors
- ✅ API 문서 업데이트
- ✅ `umis.yaml` 일관성

### Nice to Have (권장)
- 🎯 Coverage 80% 이상
- 🎯 Deprecation Warning 최소화
- 🎯 마이그레이션 가이드 제공

---

## 📚 참고 문서

1. **작업 리스트 (Full):**  
   `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md`

2. **v7.11.0 Fusion Architecture 설계:**  
   `dev_docs/improvements/PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md`

3. **현재 umis.yaml (Stage 기반):**  
   `umis.yaml` (Lines 4880+)

4. **기존 Phase 3-4 구현:**
   - `umis_rag/agents/estimator/phase3_guestimation.py`
   - `umis_rag/agents/estimator/phase4_fermi.py`

5. **신규 Stage 1-4 구현:**
   - `umis_rag/agents/estimator/estimator.py`
   - `umis_rag/agents/estimator/evidence_collector.py`
   - `umis_rag/agents/estimator/prior_estimator.py`
   - `umis_rag/agents/estimator/fermi_estimator.py`
   - `umis_rag/agents/estimator/fusion_layer.py`

---

## 🔄 업데이트 이력

| 날짜 | 버전 | 내용 |
|-----|------|------|
| 2025-11-26 | v1.0 | 초기 작성 |

---

**작성자:** AI Assistant  
**문의:** [To be assigned]

**끝.**

