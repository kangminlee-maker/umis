# UMIS v7.11.0 Folder Structure
**목적**: 전체 폴더 구조 한눈에 파악  
**업데이트**: 2025-11-26

---

## 📁 루트 레벨 폴더 (10개)

```
umis/
├── config/          # 모든 설정 파일 (6개) ⭐
├── setup/           # 설치 관련 모든 파일
├── umis_rag/        # RAG 코드 (실제 시스템)
├── scripts/         # 모든 실행 스크립트 (빌드 + 쿼리 + 테스트)
├── data/            # Vector DB 및 패턴 데이터
├── docs/            # 활성 UMIS 프로토콜
├── dev_docs/        # RAG 개발 히스토리 (시스템 비의존)
├── projects/        # 실제 분석 프로젝트 (Git 제외)
├── deliverable_specs/  # AI 최적화 스펙
└── archive/         # Deprecated 및 버전 히스토리
```

**Note**: alpha 브랜치 (개발) - 모두 포함 | main 브랜치 (릴리즈) - archive/, dev_docs/ 제외

---

## 🎯 폴더별 역할

### config/ - 모든 설정 파일 ⭐
**목적**: UMIS 설정 중앙 관리

```
config/
├── README.md                  # Config 폴더 설명
├── agent_names.yaml           # Agent 이름 커스터마이징
├── schema_registry.yaml       # RAG 레이어 스키마 (845줄)
├── overlay_layer.yaml         # Overlay (core/team/personal)
├── projection_rules.yaml      # Projection 규칙 (90% 커버리지)
├── routing_policy.yaml        # Explorer Workflow (4단계)
└── runtime.yaml               # 실행 모드 (hybrid)
```

**사용**:
- Agent 이름 변경: `config/agent_names.yaml` 수정
- 실행 모드 변경: `config/runtime.yaml` 수정
- Projection 규칙 추가: `config/projection_rules.yaml` 수정

---

### setup/ - 설치 관련
**목적**: 신규 사용자 온보딩

```
setup/
├── setup.py                 # 자동 설치 스크립트
├── AI_SETUP_GUIDE.md        # AI Assistant용 가이드
├── SETUP.md                 # 상세 설치 가이드 (사용자용)
├── START_HERE.md            # UMIS 빠른 시작
└── README.md                # 폴더 설명
```

**사용**:
- AI: `"UMIS 설치해줘"` → `AI_SETUP_GUIDE.md` 참조
- 스크립트: `python setup/setup.py`
- 수동: `setup/SETUP.md` 참조

---

### umis_rag/ - RAG 코드 (실제 시스템)
**목적**: RAG 시스템 핵심 패키지

```
umis_rag/
├── core/           # 핵심 컴포넌트
│   ├── schema.py
│   ├── layer_manager.py
│   ├── workflow_executor.py
│   └── ...
├── graph/          # Knowledge Graph (Neo4j)
├── projection/     # Canonical → Projected 변환
├── guardian/       # Guardian Memory (Query/Goal/RAE)
├── learning/       # 규칙 학습
├── agents/         # Explorer 에이전트
└── utils/          # 유틸리티
```

**시스템 의존**: ✅ (실제 RAG 동작 코드)

---

### scripts/ - 모든 실행 스크립트
**목적**: RAG 빌드, 검색, 테스트

```
scripts/
├── 빌드 스크립트
│   ├── 01_convert_yaml.py             # YAML → JSONL 변환
│   ├── 02_build_index.py              # RAG 인덱스 빌드 (통합)
│   ├── build_canonical_index.py       # Canonical 빌드
│   ├── build_projected_index.py       # Projected 빌드
│   └── build_knowledge_graph.py       # Graph 빌드
│
├── 쿼리 스크립트
│   └── query_rag.py                   # RAG 검색 CLI
│
├── 테스트 스크립트
│   ├── 03_test_search.py              # 검색 테스트
│   ├── test_neo4j_connection.py       # Neo4j 연결 테스트
│   ├── test_hybrid_explorer.py        # Hybrid Search 테스트
│   ├── test_schema_contract.py        # 스키마 계약 테스트
│   ├── test_guardian_memory.py        # Guardian Memory 테스트
│   └── test_all_improvements.py       # 통합 테스트
│
└── README.md                           # 스크립트 사용법
```

**사용**:
- 빌드: `python scripts/02_build_index.py --agent explorer`
- 검색: `python scripts/query_rag.py "구독 모델"`
- 테스트: `python scripts/test_schema_contract.py`

---

### data/ - 데이터
**목적**: Vector DB 및 패턴 원본

```
data/
├── raw/                      # 원본 YAML
│   ├── umis_business_model_patterns.yaml (31개)
│   ├── umis_disruption_patterns.yaml (23개)
│   └── umis_ai_guide.yaml
├── chunks/                   # 변환된 JSONL
│   ├── explorer_business_models.jsonl
│   └── explorer_disruption_patterns.jsonl
├── chroma/                   # ChromaDB (Git 제외)
│   ├── canonical_index/
│   ├── projected_index/
│   ├── query_memory/
│   ├── goal_memory/
│   └── rae_index/
├── core/                     # Core Layer (Overlay)
├── team/                     # Team Layer (향후)
├── personal/                 # Personal Layer (향후)
└── config/pattern_relationships.yaml  # Graph 관계 정의
```

---

### docs/ - 활성 UMIS 프로토콜 및 가이드
**목적**: 현재 사용 중인 프로토콜, API 문서, 아키텍처, 사용자 가이드

```
docs/
├── README.md                              # docs 폴더 설명
├── FOLDER_STRUCTURE.md                    # 전체 폴더 구조 (이 파일)
├── VERSION_UPDATE_CHECKLIST.md           # 버전 업데이트 체크리스트
├── MIGRATION_QUICKSTART_v7_11_0.md       # v7.11.0 마이그레이션 퀵스타트
├── MIGRATION_GUIDE_v7_11_0.md            # v7.11.0 완전 마이그레이션 가이드
├── UMIS-DART-재무제표-조사-프로토콜.md      # Rachel 재무 데이터 조사 표준
│
├── api/
│   └── ESTIMATOR_API_v7_11_0.md          # Estimator API (4-Stage Fusion)
│
├── guides/
│   ├── 기본 설정
│   ├── INSTALL.md
│   ├── MAIN_BRANCH_SETUP.md
│   ├── NATIVE_MODE_GUIDE.md
│   ├── RAG_DATABASE_SETUP.md
│   │
│   ├── 데이터 수집
│   ├── DART_CRAWLER_USER_GUIDE.md
│   ├── API_DATA_COLLECTION_GUIDE.md
│   ├── WEB_SEARCH_SETUP_GUIDE.md
│   ├── WEB_SEARCH_CRAWLING_GUIDE.md
│   │
│   ├── Estimator & LLM
│   ├── ESTIMATOR_USER_GUIDE_v7_11_0.md   # Estimator 사용자 가이드
│   ├── BUDGET_CONFIGURATION_GUIDE.md     # Budget 설정 (Stage 3)
│   ├── LLM_MODEL_SELECTION.md            # LLM 모델 선택
│   │
│   └── System RAG
│       ├── SYSTEM_RAG_GUIDE.md           # System RAG 사용법
│       └── SYSTEM_RAG_INTERFACE.md       # System RAG 인터페이스
│
└── architecture/
    ├── UMIS_ARCHITECTURE_BLUEPRINT.md    # 전체 시스템 구조 (1,400줄)
    ├── LLM_ABSTRACTION_v7_11_0.md        # LLM Complete Abstraction
    └── LLM_STRATEGY.md                   # LLM 전략 및 최적화
```

**특징**:
- ✅ 활성 문서만 (현재 버전에서 사용)
- ✅ 에이전트 참조 가능
- ✅ 사용자 직접 참조 가능
- ✅ v7.11.0 아키텍처 완전 반영
- ❌ Deprecated 문서 제외 (→ archive/)

**v7.11.0 업데이트**:
- API 문서 추가 (Estimator)
- 아키텍처 문서 중앙 집중화 (3개)
- LLM & System RAG 가이드 추가 (7개)
- Deprecated 문서 archive 이동 (3개)

---

### dev_docs/ - RAG 개발 히스토리 (시스템 비의존)
**목적**: RAG 개발 과정 및 아키텍처 설계 문서

```
dev_docs/
├── README.md
├── INDEX.md
├── architecture/         # RAG v3.0 아키텍처 설계
│   ├── 01_projection/
│   ├── 02_schema_registry/
│   ├── ...
│   └── COMPLETE_ARCHITECTURE_V3.md
├── dev_history/          # 주차별 개발 히스토리
│   ├── week_2_dual_index/
│   ├── week_3_knowledge_graph/
│   └── week_4_guardian/
├── analysis/             # 시스템 분석 문서
│   ├── MULTI_AGENT_RAG_ARCHITECTURE.md
│   ├── ADVANCED_RAG_CHALLENGES.md
│   └── ...
├── guides/               # 개발 가이드
│   ├── knowledge_graph_setup_20251103.md
│   └── README_RAG.md
├── planning/             # 계획 문서
└── summary/              # 요약 문서
```

**특징**:
- ❌ 시스템 동작과 무관 (코드 실행에 불필요)
- ✅ 개발 과정 이해용
- ✅ 아키텍처 연구용
- ✅ **파일명에 날짜 포함 규칙** (새 문서)

**파일 네이밍**:
```
feature_analysis_20251103.md       # 날짜 포함 ✅
knowledge_graph_setup_20251103.md  # 날짜 포함 ✅
COMPLETE_ARCHITECTURE_V3.md        # 버전 번호로 충분
```

---

### projects/ - 프로젝트 산출물 (Git 제외)
**목적**: 실제 시장 분석 프로젝트 저장

```
projects/
├── README.md
├── market_analysis/                 # Legacy 프로젝트
│   ├── korean_adult_education_market_2024/
│   └── music_streaming_subscription_2024/
└── YYYYMMDD_project_name/           # v7.0.0 표준 구조
    ├── 00_overview/
    ├── 02_analysis/
    │   ├── validator/
    │   ├── quantifier/
    │   ├── observer/
    │   └── explorer/
    └── ...
```

**특징**:
- ❌ Git 추적 제외 (민감한 비즈니스 정보)
- ✅ 프로젝트명에 날짜 포함 (YYYYMMDD_name)
- ✅ Stewart 자동 관리

---

### deliverable_specs/ - AI 최적화 스펙
**목적**: 에이전트 산출물 스키마 정의

```
deliverable_specs/
├── observer/market_reality_report_spec.yaml
├── explorer/opportunity_hypothesis_spec.yaml
├── quantifier/market_sizing_workbook_spec.yaml
├── validator/source_registry_spec.yaml
└── project/
    ├── project_meta_spec.yaml
    └── deliverables_registry_spec.yaml
```

**시스템 의존**: ✅ (AI가 산출물 생성 시 참조)

---

### tests/ - 테스트
**목적**: 스키마 및 기능 테스트

```
tests/
├── test_schema_contract.py    # 스키마 계약 테스트
└── ...
```

---

### archive/ - Deprecated
**목적**: 과거 버전 보관

```
archive/
├── deprecated/                # Deprecated 파일들 (루트와 동일 구조)
│   └── docs/                 # deprecated된 docs 문서들
│       ├── UMIS_v6.2_Complete_Guide.md
│       ├── "UMIS v6.2 Executive Summary"
│       └── umis_format_comparison.md
├── v1.x/                      # v1.x 가이드라인들
├── v2.x/                      # v2.x 가이드라인들
├── v3.x/                      # v3.x 가이드라인들
├── v4.x/                      # v4.x 가이드라인들
├── v5.x/                      # v5.x 가이드라인들
├── v6.x/                      # v6.x 가이드라인들
└── README.md                  # Archive 폴더 설명
```

**Note**: alpha 브랜치에서만 추적, main 브랜치에서는 .gitignore로 제외

---

## 🔍 찾기 가이드

### "설치하고 싶어요"
→ **[INSTALL.md](INSTALL.md)** 또는 **[setup/](setup/)**

### "UMIS 전체 구조가 궁금해요"
→ **[UMIS_ARCHITECTURE_BLUEPRINT.md](UMIS_ARCHITECTURE_BLUEPRINT.md)**

### "사용 방법이 궁금해요"
→ **[umis.yaml](umis.yaml)** 또는 **[setup/START_HERE.md](setup/START_HERE.md)**

### "RAG가 어떻게 작동하는지 궁금해요"
→ **[dev_docs/architecture/](dev_docs/architecture/)**

### "코드를 수정하고 싶어요"
→ **[umis_rag/](umis_rag/)** (실제 코드)

### "프로젝트 예시를 보고 싶어요"
→ **[projects/market_analysis/](projects/market_analysis/)**

### "재무 데이터 조사 방법은?"
→ **[docs/UMIS-DART-재무제표-조사-프로토콜.md](docs/UMIS-DART-재무제표-조사-프로토콜.md)**

---

## 📋 폴더 특성 요약

| 폴더 | 시스템 의존 | Git 추적 | 용도 |
|------|-----------|---------|------|
| `setup/` | ❌ | ✅ | 설치 가이드 |
| `umis_rag/` | ✅ | ✅ | RAG 코드 |
| `scripts/` | ✅ | ✅ | 모든 실행 스크립트 (빌드+테스트) |
| `data/raw/` | ✅ | ✅ | 패턴 원본 |
| `data/chroma/` | ✅ | ❌ | Vector DB (재생성) |
| `docs/` | ✅ | ✅ | 활성 프로토콜 |
| `dev_docs/` | ❌ | alpha: ✅, main: ❌ | 개발 히스토리 |
| `projects/` | ❌ | alpha: ✅, main: ⚠️* | 분석 산출물 |
| `deliverable_specs/` | ✅ | ✅ | AI 스펙 |
| `archive/` | ❌ | alpha: ✅, main: ❌ | 과거 버전 |

**\* projects/ 특별 정책**: 
- alpha: 전체 추적
- main: 폴더 구조만 유지 (README.md), 내용은 제외

---

## 🔄 정리 히스토리

### 2025-11-03 대대적 정리

**Before**: 루트 폴더 혼잡 (40+ 파일/폴더)

**After**: 논리적 구조 (10개 폴더)
1. ✅ **setup/** 신규 생성 - 설치 관련 4개 파일 모음
2. ✅ **rag/** → **dev_docs/** 리네이밍 - 목적 명확화
3. ✅ **dev_docs/docs/** → **dev_docs/** 플랫화 - 중복 제거
4. ✅ **docs/market_analysis/** → **projects/market_analysis/** 이동
5. ✅ **docs/** 정리 - 활성 프로토콜만 유지 (2개 파일)
6. ✅ **archive/deprecated/** 신규 - 루트와 동일 구조
7. ✅ **backups/** 삭제 - 불필요
8. ✅ **README.md** 추가 - 각 폴더 설명 (4개)

**효과**:
- 루트 폴더 깔끔 (10개 폴더로 정리)
- 각 폴더 역할 명확
- 파일 찾기 쉬움
- 논리적 그룹핑
- 확장 가능한 구조 (deprecated/루트구조)

---

## 📝 네이밍 규칙

### 폴더명
- **소문자_언더스코어**: `dev_docs`, `deliverable_specs`
- **명확한 목적**: `setup` (설치), `projects` (프로젝트), `archive` (보관)

### 파일명

#### 개발 문서 (dev_docs/)
```
{주제}_{YYYYMMDD}.md           # 날짜 필수 (최신 여부 확인)

예시:
knowledge_graph_setup_20251103.md
architecture_review_20251103.md
```

#### 프로젝트 (projects/)
```
YYYYMMDD_{project_name}/       # 날짜 Prefix

예시:
20251103_piano_subscription/
20251103_ev_charging_korea/
```

#### 루트 문서
```
UMIS_ARCHITECTURE_BLUEPRINT.md  # 주요 문서는 대문자
README.md                       # 표준 파일
INSTALL.md                      # 명확한 이름
```

---

## 🎓 Best Practices

### 1. 새 파일 추가 시

**설치 관련** → `setup/`  
**RAG 코드** → `umis_rag/`  
**개발 문서** → `dev_docs/` (날짜 포함!)  
**활성 프로토콜** → `docs/`  
**분석 프로젝트** → `projects/`

### 2. 파일 이동 시

**Deprecated 문서** → `archive/docs_deprecated/`  
**과거 버전** → `archive/v{X}.x/`  
**실수로 잘못 위치한 파일** → 적절한 폴더로

### 3. 날짜 추가

**개발 문서** (dev_docs/): 필수  
**프로젝트** (projects/): 필수  
**루트 파일**: 선택 (버전 번호로 충분하면 생략)

---

## 🚀 빠른 참조

```bash
# 설치
python setup/setup.py

# RAG 빌드
python scripts/02_build_index.py --agent explorer

# RAG 검색
python scripts/query_rag.py "구독 모델"

# 테스트
python tests/test_schema_contract.py

# 프로젝트 시작
"@Stewart, 새 프로젝트 시작"
```

---

**버전**: v7.0.0  
**정리일**: 2025-11-03  
**다음 리뷰**: 버전 업데이트 시

