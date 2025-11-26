# UMIS Documentation

**목적**: UMIS 활성 참조 문서 및 프로토콜  
**버전**: v7.11.0  
**업데이트**: 2025-11-26

---

## 📌 이 폴더의 역할

`docs/` 폴더는 **활성 참조 문서**를 포함합니다.

- ✅ 현재 사용 중인 프로토콜
- ✅ 설치 및 설정 가이드 (guides/)
- ✅ 시스템 아키텍처 (architecture/)
- ✅ 버전 관리 가이드
- ❌ 개발 히스토리 (→ `dev_docs/`)
- ❌ 테스트 보고서 (→ `dev_docs/testing_reports/`)
- ❌ Deprecated 문서 (→ `archive/`)

---

## 📄 문서 목록

### 루트 문서 (5개)
- **README.md** - 이 파일
- **FOLDER_STRUCTURE.md** - 전체 폴더 구조 및 네이밍 규칙
- **VERSION_UPDATE_CHECKLIST.md** - 버전 업데이트 체크리스트
- **MIGRATION_QUICKSTART_v7_11_0.md** - v7.11.0 마이그레이션 퀵스타트
- **MIGRATION_GUIDE_v7_11_0.md** - v7.11.0 완전 마이그레이션 가이드
- **UMIS-DART-재무제표-조사-프로토콜.md** - Rachel 재무 데이터 조사 표준 (v0.1)

### API 문서 (api/, 1개)
- **ESTIMATOR_API_v7_11_0.md** - Estimator API 문서 (v7.11.0, 4-Stage Fusion)

### 설치 및 설정 가이드 (guides/, 14개)

#### 기본 설정
- **INSTALL.md** - 빠른 설치 가이드 (3가지 방법)
- **MAIN_BRANCH_SETUP.md** - main 브랜치 설정
- **NATIVE_MODE_GUIDE.md** - Native 모드 사용 가이드
- **RAG_DATABASE_SETUP.md** - RAG 데이터베이스 설정

#### 데이터 수집
- **DART_CRAWLER_USER_GUIDE.md** - DART 크롤러 사용법
- **API_DATA_COLLECTION_GUIDE.md** - API 데이터 수집 가이드
- **WEB_SEARCH_SETUP_GUIDE.md** - 웹 검색 설정
- **WEB_SEARCH_CRAWLING_GUIDE.md** - 웹 크롤링 가이드

#### Estimator & LLM
- **ESTIMATOR_USER_GUIDE_v7_11_0.md** - Estimator 사용자 가이드 (v7.11.0)
- **BUDGET_CONFIGURATION_GUIDE.md** - Budget 설정 가이드 (Stage 3)
- **LLM_MODEL_SELECTION.md** - LLM 모델 선택 가이드

#### System RAG
- **SYSTEM_RAG_GUIDE.md** - System RAG 사용 가이드
- **SYSTEM_RAG_INTERFACE.md** - System RAG 인터페이스

### 아키텍처 (architecture/, 4개)
- **UMIS_ARCHITECTURE_BLUEPRINT.md** - 전체 시스템 구조 (1,400줄)
- **LLM_ABSTRACTION_v7_11_0.md** - LLM Complete Abstraction 아키텍처
- **LLM_STRATEGY.md** - LLM 전략 및 최적화

---

## 🗂️ 다른 문서 위치

### 루트 핵심 문서 (5개)
- **[../README.md](../README.md)** - 프로젝트 관문 (GitHub 첫 페이지)
- **[../umis.yaml](../umis.yaml)** - UMIS 시스템 전체 가이드 (6,100줄)
- **[../umis_core.yaml](../umis_core.yaml)** - System RAG INDEX (150줄)
- **[../CURRENT_STATUS.md](../CURRENT_STATUS.md)** - 현재 작동 상태
- **[../CHANGELOG.md](../CHANGELOG.md)** - 버전 변경 이력

### 설치
- **[../setup/](../setup/)** - 설치 관련 모든 파일 (setup.py, 가이드)

### 설정
- **[../config/](../config/)** - 모든 설정 파일 (agent_names, schema_registry, ...)

### 개발 문서
- **[../dev_docs/](../dev_docs/)** - 개발 히스토리 및 아키텍처 설계
  - `release_notes/` - 릴리스 노트 (v7.0.0 ~ v7.5.0)
  - `testing_reports/` - 테스트 보고서 (Fermi, Benchmark)
  - `phase4_improvement/` - Phase 4 Few-shot 개선 문서
  - `guides/` - 개발 가이드 (Deployment, Benchmark 등)
  - `reports/` - 시스템 검증 보고서
  - `excel/` - Excel QA/검증 문서
  - `session_summaries/` - 개발 세션 요약

### Deprecated
- **[../archive/](../archive/)** - 과거 버전 문서 및 코드
  - `deprecated_features/` - Deprecated 기능 문서
  - `v1.x ~ v7.2.0_and_earlier/` - 과거 버전들
  - `testing_data_20251121/` - 테스트 JSON 데이터

### 프로젝트
- **[../projects/](../projects/)** - 시장 분석 프로젝트 산출물 (Git 제외)

---

## 📝 문서 작성 가이드

### 활성 프로토콜 추가 시
1. 이 폴더(`docs/`)에 추가
2. 파일명 형식: `UMIS-{주제}-프로토콜.md` 또는 `{주제}_protocol.md`
3. 버전 명시 (v0.1, v1.0 등)
4. 작성일 또는 업데이트 날짜 명시

### 설치/설정 가이드 작성 시
1. `docs/guides/` 폴더 사용
2. 사용자 관점 문서 (개발자는 `dev_docs/guides/`)
3. 명확한 단계별 지침

### 개발 관련 문서 작성 시
1. `dev_docs/` 폴더 사용
2. 적절한 서브폴더 선택:
   - `release_notes/` - 릴리스 노트
   - `testing_reports/` - 테스트 결과
   - `guides/` - 개발 가이드
   - `reports/` - 검증 보고서
   - `session_summaries/` - 세션 요약
3. 파일명에 날짜 포함 (예: `feature_analysis_20251121.md`)

### Deprecated 문서 처리
1. `archive/deprecated_features/` 폴더로 이동
2. 파일명에 버전 정보 유지
3. 이동 이유 기록

---

## 🔄 업데이트 정책

### 이 폴더의 문서는:
- ✅ 현재 버전에서 사용
- ✅ 에이전트가 참조 가능
- ✅ 사용자가 직접 참조
- ✅ 버전 업데이트 시 함께 검토

### 제외 대상:
- 과거 버전 문서 → `archive/`
- 개발 과정 문서 → `dev_docs/`
- 테스트 보고서 → `dev_docs/testing_reports/`
- 분석 프로젝트 → `projects/`

---

## 📊 문서 정리 이력

### 2025-11-26: v7.11.0 마이그레이션 (대규모 정리)
**Archive 이동** (3개):
- `api/ESTIMATOR_API_v7_9_0.md` → `archive/docs_deprecated_v7.10.2_and_below/api/`
- `guides/ESTIMATOR_USER_GUIDE_v7_9_0.md` → `archive/docs_deprecated_v7.10.2_and_below/guides/`
- `PHASE_IMPROVEMENT_OPPORTUNITIES_20251121.md` → `archive/docs_deprecated_v7.10.2_and_below/`

**dev_docs → docs 이동** (7개):
- `LLM_COMPLETE_ABSTRACTION_SUMMARY_v7_11_0.md` → `architecture/LLM_ABSTRACTION_v7_11_0.md`
- `ARCHITECTURE_LLM_STRATEGY.md` → `architecture/LLM_STRATEGY.md`
- `V7_11_0_MIGRATION_COMPLETE.md` → `MIGRATION_GUIDE_v7_11_0.md`
- `BUDGET_CONFIGURATION_GUIDE_v7_11_0.md` → `guides/BUDGET_CONFIGURATION_GUIDE.md`
- `SYSTEM_RAG_USAGE_GUIDE.md` → `guides/SYSTEM_RAG_GUIDE.md`
- `SYSTEM_RAG_INTERFACE_GUIDE.md` → `guides/SYSTEM_RAG_INTERFACE.md`
- `GPT_MODEL_SELECTION_GUIDE.md` → `guides/LLM_MODEL_SELECTION.md`

**결과**: 
- v7.11.0 아키텍처 문서 중앙 집중화
- 사용자 참조 가능한 가이드만 docs에 유지
- Deprecated 문서 명확히 분리

### 2025-11-21: 대규모 재구성
- 릴리스 노트 → `dev_docs/release_notes/` (7개)
- 테스트 보고서 → `dev_docs/testing_reports/` (12개)
- Phase 4 개선 → `dev_docs/phase4_improvement/` (8개)
- Excel 문서 → `dev_docs/excel/` (3개)
- 개발 가이드 → `dev_docs/guides/` (6개)
- 검증 보고서 → `dev_docs/reports/` (1개)
- 활성 프로토콜만 `docs/`에 유지

---

**현재 버전**: v7.11.0  
**마지막 업데이트**: 2025-11-26  
**활성 문서 수**: 24개 (루트 6개 + api 1개 + guides 14개 + architecture 4개)
