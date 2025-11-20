# UMIS 개발 문서 (dev_docs)

UMIS 시스템의 개발 관련 문서 모음입니다. 기능별로 정리되어 있습니다.

## 디렉토리 구조

### 핵심 기능별 문서

#### 1. DART 크롤러 (`dart_crawler/`)
DART Open API를 통한 기업 재무제표 크롤링 시스템

- 주요 기능: DART API 연동, SGA 데이터 파싱, Rate Limiting
- 관련 코드: `umis_rag/data_sources/dart/`

#### 2. SGA Parser (`sga_parser/`)
판매비와관리비(SGA) 파싱 시스템

- 주요 기능: LLM 기반 항목 추출, 다단계 파이프라인 (Phase 0-4), 품질 평가
- 하위 시스템: Learning System (학습 시스템)
- 관련 코드: `umis_rag/parsers/sga/`, `umis_rag/learning/`

#### 3. Estimator (`estimator/`)
Fermi Estimator 및 벤치마크 시스템

- 주요 기능: 5-Phase Architecture, 12개 비즈니스 지표 추정, 학습 시스템
- 관련 코드: `umis_rag/agents/estimator/`

#### 4. RAG System (`rag_system/`)
4-Layer RAG Architecture (v3.0)

- Layer 1: Canonical Store
- Layer 2: Projected Views (6-Agent)
- Layer 3: Graph Store (Neo4j)
- Layer 4: Memory Store
- 관련 코드: `umis_rag/core/`

#### 5. Validator (`validator/`)
데이터 검증 및 소싱 시스템

- 주요 기능: 데이터 정의 검증, 출처 검증, 창의적 소싱, DART 통합
- 관련 코드: `umis_rag/agents/validator/`

### 시스템 관리

#### 6. System (`system/`)
UMIS 시스템 전반 문서

- 시스템 상태 (CURRENT_STATUS)
- Agent MECE 분석
- 소스 통합 분석
- LLM 철학과 교훈

#### 7. Deployment (`deployment/`)
배포 및 운영 문서

- 배포 가이드
- API 통합
- PR 관리
- 운영 가이드

#### 8. LLM Strategy (`llm_strategy/`)
LLM 모델 선택 및 비용 최적화 문서

- 모델 비교 및 선택 가이드
- Claude ↔ GPT 마이그레이션
- 비용 최적화 전략 (85-93% 절감)
- 최신 가격 업데이트 (2025)
- System RAG 대안 분석
- 관련 코드: `umis_rag/core/llm_router.py`

### 버전별 개발 문서

#### 9. Fermi (`fermi/`)
Fermi Estimator 초기 개발 문서

#### 10. Guestimation v3 (`guestimation_v3/`)
Guestimation 시스템 v3 개발 문서

#### 11. v7.5.0 Development (`v7.5.0_development/`)
v7.5.0 버전 개발 문서
- V7.5.0 완료 보고서
- Interface 정리
- Estimator/Quantifier 분리

#### 12. v7.6.2 Development (`v7.6.2_development/`)
v7.6.2 버전 개발 문서
- `analysis/`: 분석 보고서
- `design/`: 설계 문서
- `reports/`: 개발 리포트

### 기타 문서

#### 13. Analysis (`analysis/`)
시스템 분석 문서 모음

#### 14. Reports (`reports/`)
개발 리포트 모음

#### 15. Session Summaries (`session_summaries/`)
개발 세션 요약 및 최종 보고서 모음

- 세션 요약 (`SESSION_*.md`)
- 최종 보고서 (`FINAL_*.md`)
- 프로젝트 완료 보고서 (`PROJECT_*.md`)
- 기능별 요약 (LLM 최적화, 웹 크롤링 등)

## 문서 정리 원칙

### dev_docs/
개발 관련 문서 (히스토리, 설계, 분석)

- 시스템 비의존: 문서가 삭제되어도 시스템 작동
- 컨텍스트 보존: 개발 과정과 의사결정 기록
- 기능별 분류: 각 기능마다 독립된 디렉토리

### docs/
활성 프로토콜 및 가이드 (시스템 의존)

- 시스템 운영에 필요한 문서
- 사용자 가이드, API 문서
- 실행 프로토콜

### projects/
실제 분석 프로젝트 (Git 제외)

- 프로젝트별 디렉토리
- 연구 데이터, 분석 결과
- `.gitignore`에 의해 Git에서 제외

### archive/
Deprecated 문서 (main 브랜치에서 제외)

- 더 이상 사용하지 않는 버전
- deprecated 기능 문서
- 히스토리 보존 목적
- 상세: `archive/deprecated_features/README.md`

## Deprecated 기능 (v7.7.0 기준)

다음 기능들은 deprecated 되어 `archive/deprecated_features/`로 이동되었습니다:

### 1. Domain Reasoner (v7.5.0 제거)
- **대체:** Estimator Phase 3 (Guestimation)
- **위치:** `archive/deprecated_features/domain_reasoner/`

### 2. 3-Tier System (v7.7.0 완전 Deprecated)
- **대체:** 5-Phase System (Phase 0-4)
- **위치:** `archive/deprecated_features/tier_system/`
- **용어 변경:**
  - Tier 1 → Phase 1 (Direct RAG)
  - Tier 2 → Phase 2 (Validator Search)
  - Tier 3 → Phase 3 (Guestimation)

### 3. Built-in Rules (v7.6.0 제거)
- **대체:** Learned Rules (학습 기반)
- **위치:** (코드 레벨 변경, 별도 문서 없음)

**참고:** 마이그레이션 가이드는 `archive/deprecated_features/README.md` 참조

## 문서 찾기

### 기능별
- DART 크롤링: `dart_crawler/`
- SGA 파싱: `sga_parser/` (하위: `learning_system/`)
- 값 추정: `estimator/`, `fermi/`
- RAG 시스템: `rag_system/`
- 데이터 검증: `validator/`
- 시스템 전반: `system/`
- 배포/운영: `deployment/`
- LLM 전략: `llm_strategy/` (비용 최적화 91-93%)

### 버전별
- v7.5.0: `v7.5.0_development/`
- v7.6.2: `v7.6.2_development/`

### 날짜별
- 세션 요약: `session_summaries/SESSION_SUMMARY_YYYYMMDD.md`
- 최종 보고서: `session_summaries/FINAL_*.md`

## 관련 파일

- `CHANGELOG.md` (프로젝트 루트): 전체 버전 변경 이력
- `umis.yaml` (프로젝트 루트): UMIS 시스템 가이드
- `umis_core.yaml` (프로젝트 루트): System RAG 인덱스

