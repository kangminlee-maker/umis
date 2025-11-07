# UMIS Documentation

**목적**: UMIS 활성 참조 문서 및 프로토콜  
**버전**: v7.0.0

---

## 📌 이 폴더의 역할

`docs/` 폴더는 **활성 참조 문서**를 포함합니다.

- ✅ 현재 사용 중인 프로토콜
- ✅ 설치 및 설정 가이드
- ✅ 폴더 구조 참조
- ✅ 버전 관리 가이드
- 🚫 개발 히스토리 (→ `dev_docs/`)
- 🚫 Deprecated 문서 (→ `archive/deprecated/`)

---

## 📄 문서 목록 (6개)

### 설치 및 설정
- **INSTALL.md** - 빠른 설치 가이드 (3가지 방법)
- **MAIN_BRANCH_SETUP.md** - main 브랜치 설정 (alpha → main 병합)

### 참조 가이드
- **FOLDER_STRUCTURE.md** - 전체 폴더 구조 및 네이밍 규칙
- **VERSION_UPDATE_CHECKLIST.md** - 버전 업데이트 체크리스트

### 프로토콜
- **UMIS-DART-재무제표-조사-프로토콜.md** - Rachel 재무 데이터 조사 표준 (v0.1)

### 폴더 설명
- **README.md** - 이 파일

---

## 🗂️ 다른 문서 위치

### 루트 핵심 문서 (4개)
- **[../README.md](../README.md)** - 프로젝트 관문 (GitHub 첫 페이지)
- **[../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md)** - 전체 시스템 구조 (Comprehensive)
- **[../CURRENT_STATUS.md](../CURRENT_STATUS.md)** - 현재 작동 상태
- **[../CHANGELOG.md](../CHANGELOG.md)** - 버전 변경 이력

### 설치
- **[../setup/](../setup/)** - 설치 관련 모든 파일 (setup.py, 가이드)

### 설정
- **[../config/](../config/)** - 모든 설정 파일 (agent_names, schema_registry, ...)

### 개발 문서
- **[../dev_docs/](../dev_docs/)** - RAG 개발 히스토리 및 아키텍처 설계

### Deprecated
- **[../archive/deprecated/](../archive/deprecated/)** - 과거 버전 문서들

### 프로젝트
- **[../projects/](../projects/)** - 시장 분석 프로젝트 산출물

---

## 📝 문서 작성 가이드

### 활성 프로토콜 추가 시
1. 이 폴더(`docs/`)에 추가
2. 파일명 형식: `UMIS-{주제}-프로토콜.md` 또는 `{주제}_protocol.md`
3. 버전 명시 (v0.1, v1.0 등)
4. 작성일 또는 업데이트 날짜 명시

### 개발 관련 문서 작성 시
1. `dev_docs/` 폴더 사용
2. 적절한 서브폴더 선택 (analysis, architecture, guides 등)
3. 파일명에 날짜 포함 (예: `feature_analysis_20251103.md`)

### Deprecated 문서 처리
1. `archive/docs_deprecated/` 폴더로 이동
2. 파일명에 버전 정보 유지
3. 이동 이유 기록

---

## 🔄 업데이트 정책

### 이 폴더의 문서는:
- ✅ 현재 버전에서 사용
- ✅ 에이전트가 참조 가능
- ✅ 버전 업데이트 시 함께 검토

### 제외 대상:
- 과거 버전 문서 → `archive/`
- 개발 과정 문서 → `dev_docs/`
- 분석 프로젝트 → `projects/`

---

**현재 버전**: v7.0.0  
**마지막 업데이트**: 2025-11-03
