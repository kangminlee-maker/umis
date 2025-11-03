# UMIS Archive

**목적**: 과거 버전 및 Deprecated 파일 보관  
**버전**: v7.0.0

---

## 📁 구조

```
archive/
├── deprecated/           # Deprecated 파일들 (루트와 동일 구조)
│   ├── docs/            # deprecated된 docs 문서들 (v6.2 이전)
│   └── README.md
│
├── reports/             # 리팩토링 보고서 (일회성 작업 기록)
│   ├── REFACTORING_SUMMARY_20251103.md
│   ├── FINAL_CLEANUP_REPORT_20251103.md
│   ├── REFACTORING_COMPLETE_20251103.md
│   └── README.md
│
├── v1.x/                # v1.x 가이드라인들
├── v2.x/                # v2.x 가이드라인들
├── v3.x/                # v3.x 가이드라인들
├── v4.x/                # v4.x 가이드라인들
├── v5.x/                # v5.x 가이드라인들
├── v6.x/                # v6.x 가이드라인들
└── README.md            # 이 파일
```

**Note**: alpha 브랜치에서만 추적, main 브랜치에서는 .gitignore로 제외  
**설정 방법**: `../docs/MAIN_BRANCH_SETUP.md` 참조

---

## 📋 deprecated/ 폴더

### 설계 원칙
루트 디렉토리와 **동일한 구조**를 유지합니다.

```
umis/
├── docs/              현재 활성 문서
├── setup/             현재 활성 설치
└── scripts/           현재 활성 스크립트

archive/deprecated/
├── docs/              과거 deprecated된 docs 문서
├── setup/             과거 deprecated된 setup 파일 (향후)
└── scripts/           과거 deprecated된 scripts (향후)
```

### 현재 내용

#### deprecated/docs/
- `UMIS_v6.2_Complete_Guide.md` - v6.2 전체 가이드
- `UMIS v6.2 Executive Summary` - v6.2 요약
- `umis_format_comparison.md` - 포맷 비교 (v6.2)

### 파일 추가 규칙

새로운 파일이 deprecated될 때:

```bash
# 현재 위치 확인
umis/docs/old_protocol.md

# 이동 위치
archive/deprecated/docs/old_protocol.md

# 버전 정보 추가 (권장)
archive/deprecated/docs/old_protocol_v7.0.md
```

---

## 📊 reports/ 폴더

**목적**: 리팩토링 및 작업 보고서 보관

### 2025-11-03 리팩토링
- `REFACTORING_SUMMARY_20251103.md` - 요약 보고서
- `FINAL_CLEANUP_REPORT_20251103.md` - 정리 보고서
- `REFACTORING_COMPLETE_20251103.md` - 완료 보고서

**내용**:
- 루트 폴더: 40+ → 10개 (75% 감소)
- 루트 파일: 33개 → 10개 (70% 감소)
- config/, docs/ 폴더 생성
- 모든 참조 업데이트 (~570개)

---

## 📚 버전별 가이드라인

### v6.x/
- `umis_guidelines_v6.0.yaml`
- `umis_guidelines_v6.1.yaml`
- `umis_guidelines_v6.0.2.yaml`
- `umis_guidelines_v6.0.3.yaml`
- `v6.0.3/` (상세 문서)
- `validation_report_v6.0.md`

### v5.x/
- v5.0 ~ v5.2.2 가이드라인들
- `V5_FILES_NOTE.md`

### v4.x, v3.x, v2.x, v1.x
- 각 버전별 가이드라인 파일들

---

## 🔍 버전 히스토리 추적

전체 버전 변경 사항은:
- **[../CHANGELOG.md](../CHANGELOG.md)** - 상세 변경 이력
- **[../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md)** - 현재 버전 구조

---

## ⚠️ 주의사항

### 이 폴더의 파일들은:
- ✅ 참조용으로 보관
- ✅ Git에 추적 (히스토리 보존, alpha만)
- ❌ 현재 시스템에서 사용 안 함
- ❌ 신규 사용자가 볼 필요 없음

### Git 추적 정책

**alpha 브랜치**: 
- ✅ archive/ 전체 추적 (개발 히스토리 보존)
- ✅ dev_docs/ 전체 추적 (아키텍처 문서 보존)

**main 브랜치**: 
- ❌ archive/ 제외 (.gitignore)
- ❌ dev_docs/ 제외 (.gitignore)
- ✅ 릴리즈 버전만 포함

**설정 방법**: `../docs/MAIN_BRANCH_SETUP.md` 참조

---

**업데이트**: 2025-11-03  
**구조 개선**: deprecated/ (루트 구조 동일) + reports/ (작업 기록) 추가
