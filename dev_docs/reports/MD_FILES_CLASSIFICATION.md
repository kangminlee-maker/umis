# MD 문서 분류 계획

**작성일**: 2025-11-07  
**목적**: 루트 디렉토리 md 문서 정리

---

## 📂 분류 기준

```yaml
루트 (유지):
  - README.md (프로젝트 소개)
  - CHANGELOG.md (변경 이력)
  - CURRENT_STATUS.md (현재 상태)
  - UMIS_ARCHITECTURE_BLUEPRINT.md (아키텍처 개요)

docs/ (가이드, 스펙):
  - 사용자 가이드
  - 스펙 문서
  - Release Notes

dev_docs/ (설계 과정, 보고서):
  - 세션 요약
  - 개발 보고서
  - 설계 문서
  - 분석 문서

archive/ (deprecated):
  - v1.0/v2.1 관련
  - 과거 버전 문서
```

---

## 📋 분류 목록 (30개)

### 루트 유지 (4개)

```
✅ README.md
✅ CHANGELOG.md
✅ CURRENT_STATUS.md
✅ UMIS_ARCHITECTURE_BLUEPRINT.md
```

### → docs/ (3개)

```
RELEASE_NOTES_v7.0.0.md
RELEASE_NOTES_v7.2.0.md
RELEASE_NOTES_v7.3.0.md
  → docs/release_notes/
```

### → dev_docs/guestimation_v3/ (11개)

```
GUESTIMATION_V3_DESIGN_SPEC.md (2,944줄) - 초기 설계
GUESTIMATION_V3_MVP_STATUS.md - MVP 상태
GUESTIMATION_V3_SESSION_COMPLETE.md - 세션 완료

SESSION_SUMMARY_20251107_GUESTIMATION_V3_DESIGN.md (639줄) - 세션 요약

PHASE_5_IMPLEMENTATION_GUIDE.md (650줄) - 구현 가이드
PHASE_5_QUICK_CHECKLIST.md (150줄) - 체크리스트
PHASE_5_STEP1_COMPLETE.md (500줄) - Step 1 완료
PHASE_5_COMPLETE.md (900줄) - Phase 5 완료
PHASE_5_AND_INTEGRITY_FINAL_SUMMARY.md (1,400줄) - 최종 요약

CONFIDENCE_CALCULATION_GUIDE.md (593줄) - Confidence 계산
RULE_VS_LLM_TRADEOFF_ANALYSIS.md (500줄) - 규칙 vs LLM
```

### → dev_docs/analysis/ (3개)

```
GUESTIMATION_ARCHITECTURE.md - Guestimation 아키텍처
GUESTIMATION_FLOWCHART.md - 플로우차트
SEARCH_CONSENSUS_DEFINITION.md - 검색 합의 정의
```

### → dev_docs/fermi/ (3개)

```
FERMI_IMPLEMENTATION_STATUS.md - Fermi 구현 상태
FERMI_MODEL_SEARCH_SUMMARY.md - Fermi 요약
SESSION_SUMMARY_20251106_FERMI_COMPLETE.md - Fermi 세션
```

### → dev_docs/reports/ (4개)

```
FINAL_ORGANIZATION_REPORT_20251105.md - 조직화 보고
INTEGRITY_TEST_COMPLETE.md (900줄) - 무결성 테스트
DEPRECATED_FILES_LIST.md (200줄) - Deprecated 목록
SETTINGS_ARCHITECTURE_FINAL.md - Settings 아키텍처
```

### → dev_docs/summary/ (1개)

```
V7.2.1_FINAL_SUMMARY.md - v7.2.1 요약
```

### → docs/guides/ (1개)

```
GITHUB_RELEASE_GUIDE.md - GitHub Release 가이드
```

---

## 📊 요약

```yaml
총 파일: 30개

유지 (루트): 4개
  - README, CHANGELOG, CURRENT_STATUS, ARCHITECTURE_BLUEPRINT

이동 필요: 26개
  - docs/release_notes/: 3개
  - dev_docs/guestimation_v3/: 11개
  - dev_docs/analysis/: 3개
  - dev_docs/fermi/: 3개
  - dev_docs/reports/: 4개
  - dev_docs/summary/: 1개
  - docs/guides/: 1개
```

---

## 🚀 이동 명령

```bash
# 1. 디렉토리 생성
mkdir -p docs/release_notes
mkdir -p dev_docs/guestimation_v3
mkdir -p dev_docs/fermi
mkdir -p dev_docs/reports
mkdir -p dev_docs/summary
mkdir -p docs/guides

# 2. Release Notes
git mv RELEASE_NOTES_v7.0.0.md RELEASE_NOTES_v7.2.0.md RELEASE_NOTES_v7.3.0.md docs/release_notes/

# 3. Guestimation v3.0
git mv GUESTIMATION_V3_*.md SESSION_SUMMARY_20251107_GUESTIMATION_V3_DESIGN.md dev_docs/guestimation_v3/
git mv PHASE_5_*.md dev_docs/guestimation_v3/
git mv CONFIDENCE_CALCULATION_GUIDE.md RULE_VS_LLM_TRADEOFF_ANALYSIS.md dev_docs/guestimation_v3/

# 4. Fermi
git mv FERMI_*.md SESSION_SUMMARY_20251106_FERMI_COMPLETE.md dev_docs/fermi/

# 5. Reports
git mv FINAL_ORGANIZATION_REPORT_20251105.md INTEGRITY_TEST_COMPLETE.md dev_docs/reports/
git mv DEPRECATED_FILES_LIST.md SETTINGS_ARCHITECTURE_FINAL.md dev_docs/reports/

# 6. Analysis
git mv GUESTIMATION_ARCHITECTURE.md GUESTIMATION_FLOWCHART.md dev_docs/analysis/
git mv SEARCH_CONSENSUS_DEFINITION.md dev_docs/analysis/

# 7. Summary
git mv V7.2.1_FINAL_SUMMARY.md dev_docs/summary/

# 8. Guides
git mv GITHUB_RELEASE_GUIDE.md docs/guides/
```

---

**분류 완료!** 명확한 폴더 구조로 정리됩니다.

