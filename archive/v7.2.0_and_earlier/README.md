# v7.2.0 이하 버전 Archive

**Archive Date**: 2025-11-07  
**Reason**: v7.3.0 (Guestimation v3.0)으로 대체  
**Status**: Deprecated

---

## 📦 포함된 파일

### Guides (3개)

```
GUESTIMATION_COMPARISON.md (2025-11-04, v7.1.0)
  - Guestimation vs Domain Reasoner 비교
  - v1.0 기반 비교
  - 대체: v3.0은 근본적으로 다른 아키텍처

GUESTIMATION_FRAMEWORK.md (2025-11-04)
  - Guestimation v1.0 프레임워크
  - 비교 가능성 검증 중심
  - 대체: guestimation_v3/ 코드 및 주석

HYBRID_GUESTIMATION_GUIDE.md (2025-11-05, v7.2.0)
  - Multi-Layer v2.1 가이드
  - Sequential Fallback 방식
  - 대체: dev_docs/guestimation_v3/ (v3.0 문서)
```

### Reports (4개)

```
SESSION_SUMMARY_20251105_HYBRID_GUESTIMATION.md
  - 2025-11-05, v7.1.0 → v7.2.0
  - Multi-Layer v2.1 세션 요약
  - 대체: SESSION_SUMMARY_20251107_GUESTIMATION_V3_DESIGN.md

V7.2.0_FINAL_STATUS.md
  - 2025-11-05, v7.2.0 "Fermi + Native"
  - v7.2.0 최종 상태
  - 대체: CURRENT_STATUS.md (v7.3.0)

FINAL_COMPLETION_REPORT_v7.2.0.md
  - 2025-11-05, v7.2.0
  - v7.2.0 완성 보고
  - 대체: PHASE_5_AND_INTEGRITY_FINAL_SUMMARY.md

PHASE_A_COMPLETION_REPORT.md
  - Phase A 완료 보고
  - 대체: v7.3.0 Phase 5 문서
```

### Planning (2개)

```
HYBRID_GUESTIMATION_INTEGRATION_PLAN.md
  - 2025-11-04, v7.1.0 → v7.2.0
  - Multi-Layer 통합 계획
  - 대체: v3.0에서 불필요 (다른 아키텍처)

NEXT_STEPS_v7.2.md
  - 2025-11-05, v7.2.0-dev
  - v7.2.0 다음 단계
  - 대체: v7.3.0으로 실현됨
```

### Analysis (2개)

```
GUESTIMATION_ARCHITECTURE.md
  - 2025-11-05, v7.2.1
  - Multi-Layer 아키텍처
  - 대체: GUESTIMATION_V3_DESIGN.yaml

GUESTIMATION_FLOWCHART.md
  - 2025-11-05, v2.1
  - Multi-Layer 플로우차트
  - 대체: v3.0 3-Tier 아키텍처
```

### Summary (1개)

```
V7.2.1_FINAL_SUMMARY.md
  - 2025-11-05, v7.2.1
  - v7.2.1 최종 요약 (Multi-Layer + Fermi)
  - 대체: v7.3.0 문서들
```

---

## 🔄 v7.3.0 대체 매핑

### Multi-Layer v2.1 → v3.0 (3-Tier)

```yaml
v2.1 문제:
  - Sequential Fallback (첫 성공만)
  - 판단 없음
  - 정보 종합 없음

v3.0 해결:
  - 3-Tier Architecture
  - Context-Aware Judgment
  - 모든 증거 수집 + 종합
  - 학습하는 시스템

문서 대체:
  v2.1 가이드 → dev_docs/guestimation_v3/ (11개 문서)
```

### v7.2.0 → v7.3.0

```yaml
v7.2.0 (2025-11-05):
  - Multi-Layer v2.1
  - Fermi Model Search
  - Native LLM 모드

v7.3.0 (2025-11-07):
  - Guestimation v3.0 (3-Tier)
  - Phase 5 학습 시스템
  - 무결성 검증 완료

문서 대체:
  V7.2.0_FINAL_STATUS → CURRENT_STATUS.md
  V7.2.1_FINAL_SUMMARY → v7.3.0 문서들
```

---

## 📊 요약

```yaml
총 파일: 12개

가이드: 3개 (v1.0/v2.1 관련)
리포트: 4개 (v7.2.0 완료 보고)
계획: 2개 (v7.2.0 관련)
분석: 2개 (v2.1 아키텍처)
요약: 1개 (v7.2.1 요약)

이동 이유:
  - 모두 v7.2.x 이하 버전
  - Multi-Layer v2.1 관련
  - v7.3.0 (v3.0)으로 대체됨

현재 버전: v7.3.0 (Guestimation v3.0)
작성일: 2025-11-07
```

---

## 🔧 복원 방법 (필요 시)

```bash
# Archive에서 복원
git mv archive/v7.2.0_and_earlier/guides/HYBRID_GUESTIMATION_GUIDE.md docs/guides/

# 주의: v7.3.0과 동시 사용 불가!
# v2.1과 v3.0은 근본적으로 다른 아키텍처
```

---

**Archive 이유**: v7.3.0 (Guestimation v3.0)으로 전면 개편  
**권장**: v7.3.0 문서 사용  
**복원**: 필요 시 가능하나 비권장

