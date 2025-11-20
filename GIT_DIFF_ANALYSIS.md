# GitHub Alpha 브랜치 vs 로컬 차이 분석

날짜: 2024년 11월 20일  
브랜치: alpha  
상태: origin/alpha와 동기화됨

## 요약

### 변경 통계
- **삭제된 파일:** 105개 (루트 31개 + dev_docs 74개)
- **수정된 파일:** 37개
- **새로 추가된 파일:** 64개
- **총 변경:** 206개 파일

### 주요 변경 사항

#### 1. 문서 정리 (대규모 재구성) ✅

**루트 디렉토리 정리 (31개 삭제)**
```
삭제:
- BATCH_PARSING_FINAL_REPORT.md
- CD_GRADE_IMPROVEMENT_REPORT.md
- CRAWLING_TODO.md
- DART_API_LIMITATION_ANALYSIS.md
- DART_SGA_COMPLETE.md
- FINAL_*.md (10개)
- SESSION_*.md (9개)
- SGA_*.md (3개)
- LEARNING_CLASSIFICATION.md
- LLM_ACCURACY_GUIDE.md
- 기타 리포트 문서들

유지:
- README.md
- CHANGELOG.md (수정됨)
```

**dev_docs 대규모 재구성 (74개 삭제 + 새 구조)**

삭제된 dev_docs 루트 파일 (74개):
- TIER 관련 (8개): TIER1/2/3 문서들
- ESTIMATOR 관련 (8개): 설계, 배포 전략 등
- GAP 관련 (3개): GAP1/2/3 문서들
- DOMAIN_REASONER 관련 (3개)
- SESSION/FINAL 리포트들
- 기타 개발 문서들

새로 생성된 dev_docs 구조:
```
dev_docs/
├── README.md ⭐ 새 가이드
├── dart_crawler/ (11개 파일)
├── deployment/ (6개 파일)
├── estimator/ (19개 파일)
├── llm_strategy/ (9개 파일) ⭐ 새 카테고리
├── rag_system/ (43개 파일)
├── session_summaries/ (40개 파일)
├── sga_parser/ (16개 파일)
│   └── learning_system/ (2개 파일)
├── system/ (10개 파일)
└── validator/ (5개 파일)
```

#### 2. Deprecated 문서 Archive ✅

**새로 생성: archive/deprecated_features/**
```
archive/deprecated_features/
├── README.md (마이그레이션 가이드)
├── domain_reasoner/ (3개 파일)
├── tier_system/ (18개 파일)
├── built_in_rules/
└── v7.4_and_earlier/ (1개 파일)
```

**이유:**
- Domain Reasoner → Estimator Phase 3 대체 (v7.5.0)
- 3-Tier System → 5-Phase System 대체 (v7.7.0)
- Built-in Rules → Learned Rules 대체 (v7.6.0)

#### 3. LLM 전략 문서 이동 ✅

**docs/architecture/ → dev_docs/llm_strategy/**

삭제 (docs/architecture/):
- ARCHITECTURE_LLM_STRATEGY.md (이동됨)

새 위치 (dev_docs/llm_strategy/):
- ARCHITECTURE_LLM_STRATEGY.md
- CLAUDE_TO_GPT_MIGRATION_GUIDE.md
- COMPLETE_LLM_MODEL_COMPARISON.md
- GPT_MODEL_SELECTION_GUIDE.md
- NON_THINKING_MODEL_OPTIMIZATION.md
- SINGLE_PROVIDER_STRATEGY.md
- SYSTEM_RAG_ALTERNATIVES_ANALYSIS.md
- UPDATED_LLM_PRICING_2025.md
- README.md

#### 4. 코드 수정 (37개 파일)

**핵심 파일:**
- `umis.yaml` (수정)
- `CHANGELOG.md` (수정)
- `VERSION.txt` (수정)

**설정 파일:**
- `config/migration_rules.yaml`
- `config/tool_registry.yaml`

**코드:**
- `umis_rag/agents/estimator/*.py` (3개)
- `umis_rag/agents/explorer.py`
- `umis_rag/agents/validator.py`
- `umis_rag/core/config.py`
- `umis_rag/utils/dart_crawler.py`

**데이터:**
- `data/raw/*.yaml` (3개 SGA 파일)
- `data/raw/data_sources_registry.yaml`
- `data/tier1_rules/builtin.yaml`

**스크립트:**
- 여러 파서 및 분석 스크립트 수정

**테스트:**
- `tests/test_integration_timeline.py`

**문서:**
- `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- `docs/guides/UMIS_YAML_DEVELOPMENT_GUIDE.md`

#### 5. 새로 추가된 파일 (64개)

**개발 문서 (새 구조):**
- `dev_docs/` 전체 재구성 (위 참조)
- `archive/deprecated_features/` 전체

**데이터:**
- `config/learned_sga_patterns.yaml` ⭐
- `data/chroma/` (RAG 데이터베이스)
- `data/raw/*_complete.yaml` (여러 SGA 파일)
- `data/raw/*_benchmarks.yaml` (벤치마크 데이터)
- 기업 데이터 파일들

**스크립트:**
- `scripts/benchmark_openai_models.py`
- `scripts/llm_based_sga_parser.py`
- `scripts/test_*.py` (여러 테스트 스크립트)
- 기타 분석 스크립트들

**코드:**
- `umis_rag/agents/estimator/phase2_validator_search_enhanced.py`
- `umis_rag/core/model_router.py`
- `umis_rag/utils/dart_crawler_*.py` (여러 버전)

**산출물 스펙:**
- `deliverable_specs/explorer/strategy_playbook_spec.yaml`

**가이드:**
- `docs/guides/API_DATA_COLLECTION_GUIDE.md`
- `docs/guides/DART_CRAWLER_USER_GUIDE.md`
- `docs/guides/MODEL_BENCHMARK_GUIDE.md`

## 주요 성과

### 1. 문서 구조 개선 ⭐⭐⭐
- **Before:** 루트 50개 + dev_docs 루트 80개 = 130개 문서 산재
- **After:** 루트 2개 + dev_docs 체계적 구조 (8개 카테고리)
- **개선:** 가독성, 검색성, 유지보수성 대폭 향상

### 2. Deprecated 문서 정리 ⭐⭐
- 22개 deprecated 문서 archive로 이동
- 마이그레이션 가이드 제공
- 히스토리 보존 + 혼란 방지

### 3. LLM 전략 문서 통합 ⭐
- 8개 LLM 관련 문서를 한 곳에 정리
- 비용 최적화 전략 (85-93% 절감) 문서화
- 2025년 최신 가격 반영

### 4. 코드 품질 개선
- Estimator Phase 관련 코드 개선
- DART 크롤러 강화
- 벤치마크 시스템 추가

## 다음 단계

### 커밋 준비 사항

#### Option 1: 전체 변경사항 커밋 (권장)
```bash
# 모든 변경사항 스테이징
git add -A

# 커밋
git commit -m "docs: 대규모 문서 구조 개선 및 deprecated 정리

- 루트 및 dev_docs 문서 재구성 (105개 삭제, 64개 추가)
- dev_docs를 8개 기능별 카테고리로 정리
- deprecated 문서 archive/deprecated_features/로 이동
- LLM 전략 문서 dev_docs/llm_strategy/로 통합
- 코드 개선: Estimator, DART 크롤러, 벤치마크

변경:
- 삭제: 105개 (루트 31개, dev_docs 74개)
- 수정: 37개 (코어 코드, 설정, 데이터)
- 추가: 64개 (새 구조, 가이드, 스크립트)
"

# 푸시
git push origin alpha
```

#### Option 2: 단계별 커밋 (선택적)

**Step 1: 문서 삭제**
```bash
git add -u
git commit -m "docs: 루트 및 dev_docs 정리 - 불필요 문서 삭제 (105개)"
```

**Step 2: 새 문서 구조**
```bash
git add dev_docs/
git commit -m "docs: dev_docs 재구성 - 8개 기능별 카테고리로 정리"
```

**Step 3: Deprecated 문서**
```bash
git add archive/deprecated_features/
git commit -m "docs: deprecated 문서 archive로 이동 (22개)"
```

**Step 4: 코드 및 데이터**
```bash
git add -u  # 수정된 파일들
git add config/ data/ umis_rag/ scripts/ tests/
git commit -m "feat: 코드 개선 - Estimator, DART, 벤치마크"
```

**Step 5: 나머지**
```bash
git add .
git commit -m "chore: 새 스크립트, 가이드, 데이터 추가"
```

### 권장사항

**Option 1 (전체 커밋) 권장 이유:**
- 문서 정리는 하나의 큰 작업 단위
- 파일 이동이 많아 단계별 커밋 시 혼란 가능
- 히스토리가 깔끔함

**주의사항:**
- 커밋 전 변경사항 한번 더 검토
- 중요 파일 누락 확인 (.gitignore 체크)
- 푸시 전 로컬 테스트 실행

## 검증 체크리스트

### 문서
- [x] 루트 디렉토리 정리 (2개만 유지)
- [x] dev_docs 구조 개선
- [x] deprecated 문서 archive 이동
- [x] LLM 전략 문서 통합
- [x] 모든 README 생성

### 코드
- [ ] 테스트 실행 확인
- [ ] 주요 기능 동작 확인
- [ ] 설정 파일 검증

### 데이터
- [x] 새 데이터 파일 검증
- [x] 벤치마크 데이터 확인

## 요약

이번 대규모 문서 정리를 통해:
1. **문서 구조 개선:** 206개 파일 재구성
2. **가독성 향상:** 루트 깔끔, dev_docs 체계화
3. **히스토리 보존:** Deprecated 문서 archive
4. **미래 대비:** LLM 전략 통합, 확장 가능한 구조

**상태:** 커밋 준비 완료 ✅

