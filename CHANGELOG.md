# UMIS (Universal Market Intelligence System) 변경 이력

## 개요
이 문서는 UMIS의 모든 버전 변경사항을 기록합니다.

---

## v7.1.0-dev3 (2025-11-04) - Excel 엔진 완성

### 🚀 Sprint 2: Excel 자동 생성 시스템

**Excel 생성 모듈 5개 구현 (1,226줄)**:
- FormulaEngine: Excel 함수 생성 엔진 (286줄)
- AssumptionsBuilder: 가정 시트 자동 생성 (197줄)
- MethodBuilders: 4가지 SAM 계산 방법 (244줄)
- ConvergenceBuilder: 수렴 분석 (209줄)
- MarketSizingGenerator: 통합 생성기 (163줄)

**피드백 반영**:
- ✅ Named Range 절대참조 ($D$5)
- ✅ SAM Named Range 2단계 정의 (셀 → Named Range)
- ✅ 조건부 서식 Rule 객체 사용
- ✅ fullCalcOnLoad=True 설정

**테스트**:
- Excel 파일 생성 성공 (9개 시트)
- Named Range 16개 정의
- 50+ Excel 함수 작동

---

## v7.1.0-dev2 (2025-11-04) - System RAG + 6개 Collection

### 🚀 Sprint 1: System RAG 안정화

**System RAG 구현**:
- SystemRAG 클래스 (KeyDirectory O(1) 매칭)
- Key-first · Vector-fallback 2단계 검색
- 평균 지연시간 0.10ms (목표 대비 10배 빠름!)
- 결정성 100% (50회 반복 테스트 통과)

**Tool Registry**:
- 10개 도구 작성 (450줄)
- Agent별 분류 (Explorer, Quantifier, Validator, Observer, Framework)

### 🗄️ 6개 RAG Collection 완성

**데이터 작성 (360개 항목, ~10,000줄)**:
- calculation_methodologies: 30개 (SAM 계산, 성장률, 예측)
- market_benchmarks: 100개 (시장 규모, SaaS, 이커머스 등)
- data_sources_registry: 50개 (통계청, Gartner, DART 등)
- definition_validation_cases: 100개 (MAU, ARPU, Churn 등)
- market_structure_patterns: 30개 (경쟁 구조, 유통, 가격)
- value_chain_benchmarks: 50개 (제조, 유통, 서비스 등)

**품질 향상**:
- 국가별 벤치마크 (한국, 일본, 미국, 글로벌)
- 서비스별 Churn 재구조화 (Netflix 2.4% vs 일반 6%)
- 논리적 오류 수정 (쿠팡 DART 역산 기반)
- 검증 메타데이터 추가 (confidence, sources)

**RAG Index 구축**:
- 6개 Collection ChromaDB 인덱싱 (344개 문서)
- Agent RAG 검색 테스트 통과

### 📦 ChromaDB 배포 전략

**Hybrid 전략 수립**:
- Option 1: 자동 재생성 (setup.py 통합)
- Option 2: 사전 빌드 다운로드 (Google Drive)
- 압축 파일 준비 (16MB)

**문서 & 스크립트**:
- RAG_DATABASE_SETUP.md
- download_prebuilt_db.py
- README.md 업데이트

### 🔧 검증 & 도구

**검증 시스템**:
- validate_benchmarks.py (566줄)
- validate_all_yaml.py (96줄)
- BENCHMARK_VALIDATION_GUIDE.md

---

## v7.0.0-week3 (2025-11-03) - Knowledge Graph & Hybrid Search

### 🚀 주요 기능 추가

**Knowledge Graph (Neo4j)**
- Neo4j 5.13 Docker 환경 구축
- 13개 비즈니스 패턴 노드 (7 Business Models + 6 Disruptions)
- 45개 Evidence-based 관계 정의
- Multi-Dimensional Confidence 시스템
  - similarity (Vector 임베딩, 질적)
  - coverage (분포 분석, 양적)
  - validation (체크리스트, 검증)
  - overall (0-1 종합 신뢰도)
  - reasoning (자동 생성)
- Evidence & Provenance 추적 (근거, 검토자, 시간)
- GND-xxx, GED-xxx ID 네임스페이스
- config/schema_registry.yaml 100% 준수

**Hybrid Search (Vector + Graph)**
- Vector RAG (유사성) + Knowledge Graph (관계성) 통합
- 패턴 조합 자동 발견
- Confidence 기반 결과 정렬
- 인사이트 자동 생성
- `HybridSearch` 클래스 및 API

**Explorer 통합**
- `search_patterns_with_graph()` 메서드 추가
- Vector + Graph 자동 활용
- 선택적 Neo4j 활성화 (없어도 Vector만으로 작동)
- Graceful fallback 및 투명한 에러 처리

### 🛠️ 인프라 & 도구

**Neo4j 환경**
- `docker-compose.yml`: Neo4j 5.13 컨테이너 설정
- `umis_rag/graph/connection.py`: Neo4j 연결 관리 (210줄)
- `umis_rag/graph/schema_initializer.py`: 스키마 초기화 (180줄)
- Constraints (4개) + Indexes (5개)

**Graph 모듈**
- `umis_rag/graph/confidence_calculator.py`: Multi-Dimensional Confidence (360줄)
- `umis_rag/graph/hybrid_search.py`: Vector + Graph 통합 검색 (470줄)
- `umis_rag/graph/__init__.py`: 모듈 초기화

**스크립트**
- `scripts/build_knowledge_graph.py`: Graph 구축 자동화 (350줄)
- `scripts/test_neo4j_connection.py`: Neo4j 테스트 (170줄)
- `scripts/test_hybrid_explorer.py`: Hybrid Search 테스트 (180줄)

**데이터**
- `config/pattern_relationships.yaml`: 45개 관계 정의 (1,200줄)
- 실제 사례 기반 (Amazon, Spotify, Netflix, Tesla 등 50+ 사례)

### 📚 문서화

**개발 히스토리 정리**
- `rag/docs/dev_history/` 폴더 생성 및 체계화
- Week 2 (Dual-Index): 5개 문서
- Week 3 (Knowledge Graph): 9개 문서
- 인덱스 및 타임라인: 7개 문서
- 총 21개 문서 체계적 정리

**신규 문서**
- `CURRENT_STATUS.md`: 현재 시스템 상태 요약
- `docs/knowledge_graph_setup.md`: Neo4j 설치 및 설정 가이드
- Week 3 문서 9개 (Day별 진행, 최종 보고서 등)
- `DEVELOPMENT_TIMELINE.md`: 2일간 전체 타임라인

**문서 구조 개선**
- 루트 md 파일: 19개 → 6개 (68% 감소)
- 핵심 문서만 루트에 유지
- 개발 산출물은 dev_history로 이동

### 🧪 테스트

**Neo4j Tests (3/3 통과)**
- Connection test
- Schema initialization test
- Basic operations test (CRUD)

**Hybrid Search Tests (4/4 통과)**
- Hybrid Search direct test
- Explorer integration test
- Multiple patterns test
- Confidence filtering test

**총 7/7 테스트 100% 통과**

### 🔧 기술 개선

**설정 파일**
- `requirements.txt`: neo4j>=5.13.0 추가
- `env.template`: Neo4j 환경 변수 추가
- `umis_rag/core/config.py`: Neo4j 설정 추가
- `.gitignore`: Neo4j 데이터, Chroma 바이너리 제외

**코드 품질**
- Linter 에러: 0개
- config/schema_registry.yaml 100% 준수
- Type hints 완비
- 상세한 docstrings

### 📊 통계

**코드**
- Python: +2,130줄
- YAML: +1,565줄
- Markdown: +8,425줄
- 총: +12,120줄

**파일**
- 신규: 41개
- 수정: 5개
- 삭제: 5개 (중복 제거)

**커밋**
- Week 3 커밋: 6개
- 논리적 단위별 분리
- 의미있는 커밋 메시지

### 🎯 주요 성과

**Production-Ready System**
- Vector RAG: 354 chunks
- Knowledge Graph: 13 노드, 45 관계
- Hybrid Search: Vector + Graph 통합
- 모든 테스트 통과
- 즉시 배포 가능

**Evidence-Based Data**
- 45개 관계 모두 실제 사례 기반
- 50+ 검증된 비즈니스 케이스
- Multi-Dimensional Confidence
- 완전한 Provenance 추적

**완벽한 문서화**
- 21개 dev_history 문서
- Day별 진행 기록
- 인덱스 및 가이드 완비
- 깔끔한 프로젝트 루트

---

## v7.0.0 (2025-11-03) - Repository Rename & Documentation Update

### 📝 문서 업데이트

**레포지토리 이름 변경**
- 구: `umis-monolithic-guidelines`
- 신: `umis`
- 이유: "monolithic"은 더 이상 구조를 반영하지 않음. RAG + Multi-Agent 플랫폼에 적합한 간결한 이름으로 변경

**파일명 참조 수정 (Deprecated 정보 제거)**
- ~~`@umis.yaml`~~ → `umis.yaml` (@ 제거, Cursor 첨부 방식 명확화)
- ~~`umis_guidelines.yaml`~~ → `umis.yaml` (실제 파일명 반영)
- `.cursorrules` 경로 수정 (UMIS 자동화 규칙)
- 날짜 업데이트: 2025-11-02 → 2025-11-03

**업데이트된 파일**
- README.md: 
  - GitHub 배지 추가 (GitHub, Version, License)
  - 설치 가이드 추가
  - 프로젝트 구조 상세화 (실제 파일명 반영)
  - 기여 가이드라인 추가
  - 문의 섹션 추가 (Issues, Discussions)
  - 📚 주요 파일 섹션 추가
- START_HERE.md: 레포 URL 업데이트, 프로젝트 구조 수정, 링크 섹션 추가
- SETUP.md: 클론 명령어 및 사용법 업데이트
- CHANGELOG.md: 레포 이름 및 변경 이력 업데이트
- .gitignore: `docs/market_analysis/` 추가, `data/chroma/` Git 포함으로 변경

**Git 연결**
- Remote URL: `https://github.com/kangminlee-maker/umis.git`
- GitHub 자동 리다이렉트 제공 (기존 링크도 작동)

---

## v7.0.0 (2025-11-02) - Multi-Agent RAG System [ALPHA RELEASE]

### 🎉 주요 추가사항

**Multi-Agent RAG System**
- Vector RAG 시스템 추가 (54 chunks, text-embedding-3-large)
- Explorer (Steve) agent에 검증된 패턴 라이브러리 통합
- 사업모델 패턴 31개 + Disruption 패턴 23개 자동 검색

**Cursor Composer 통합**
- `.cursorrules` 자동화: YAML 수정 → RAG 자동 재구축
- Agent 모드 자동 실행: 코딩 불필요
- 30초 피드백 루프: 발견 → 추가 → 반영

**Agent 커스터마이징**
- `config/agent_names.yaml` 추가: 양방향 이름 매핑
- 기본값: Albert, Steve, Bill, Rachel, Stewart
- 커스텀: Jane, Alex, 관찰자, 탐색자 등 자유 변경
- 입력: @Steve → Explorer / 출력: Explorer → Steve

**Agent ID 통일**
- 문서: Observer, Explorer, Quantifier, Validator, Guardian
- 코드: observer, explorer, quantifier, validator, guardian
- 파일: explorer.py, explorer_*.jsonl

**문서 체계화**
- rag/docs/ 폴더: 15개 RAG 관련 문서
- guides/ (3개): Cursor 사용 가이드
- architecture/ (3개): 4-Layer 설계 (향후 계획)
- 레거시 완전 제거: -10,610줄

### 🔄 변경사항

**구현**
- Vector RAG with text-embedding-3-large (3072 dim)
- Explorer agent: pattern matching, case search
- Chroma vector database
- LangChain 1.0 integration

**문서**
- Cursor Composer 중심 재편성
- 실제 구현 vs 향후 계획 명확 구분
- 개발자 전용 내용 완전 제거

**구조**
- rag/ 폴더: 순수 문서 모음
- 실행: umis-main 루트에서
- 중복 파일 제거: rag/code/, rag/config/

### ⚠️ 주의사항

**v7.0.0 제한사항**
- Explorer만 RAG 사용 (Observer, Quantifier, Validator, Guardian은 YAML 기반)
- Layer 1 (Vector RAG)만 구현
- Layer 2-4 (Meta-RAG, Graph, Memory)는 설계만 완료

**향후 개발 계획**
- Knowledge Graph RAG (패턴 조합)
- Guardian monitoring (순환 감지, 목표 정렬)
- Multi-agent modular RAG (6개 Agent 전체)
- Meta-RAG evaluation (품질 자동 평가)

### 📦 릴리스 정보

- GitHub Branch: alpha
- Tag: v7.0.0
- 날짜: 2025-11-02
- 개발 시간: 4시간
- Commits: 17개

### 🚀 사용 방법

```
Cursor Composer (Cmd+I):
  @umis.yaml
  "@Steve, 음악 스트리밍 구독 서비스 시장 기회 분석해줘"
```

Agent 커스터마이징:
```yaml
config/agent_names.yaml:
  explorer: Alex
```

### 📚 문서

- START_HERE.md: 빠른 시작
- rag/docs/guides/01_CURSOR_QUICK_START.md: 상세 가이드
- rag/docs/architecture/: 4-Layer 설계 (향후 계획)

### 🔄 추가 변경사항 (v7.0.0 개선)

**파일명 버전 제거**
- 모든 UMIS YAML 파일명에서 v6.2 제거
- umis_guidelines.yaml (v6.2 제거, 영구 고정!)
- Cursor 참조 안정성 향상: @umis_guidelines.yaml (항상 동일)
- 각 YAML 첫 줄에 버전 표기: "Compatible with v7.0.0"

**Agent ID 완전 통일**
- 문서 + 코드 완전 일치
- Python: observer, explorer, quantifier, validator, guardian
- 파일: explorer.py, explorer_*.jsonl
- Collection: explorer_knowledge_base
- 총 124개 항목 변경

**Agent 이름 커스터마이징 강화**
- config/agent_names.yaml 최소화 (1줄로 설정!)
- 양방향 매핑: @Steve → Explorer, Explorer → Steve
- 기본값: Albert, Steve, Bill, Rachel, Stewart
- 커스텀: Jane, Alex, 관찰자, 탐색자 등

**대규모 리팩토링**
- 레거시 완전 제거: -10,610줄!
- 파일 삭제: 47개 (개발자 전용, 중복, 백업)
- 문서 정리: 30개 → 15개 핵심
- rag/ 폴더: 순수 문서 모음으로 명확화

**Cursor Composer 완전 전환**
- 모든 문서 Cursor 중심 재편성
- 개발자 전용 내용 완전 제거 (Hot-Reload, make dev, IPython 등)
- .cursorrules 최소화 형식 반영

**루트 디렉토리 정리**
- .md 파일: 10개 → 5개 핵심만
- .yaml 파일: 버전 제거, 영구 고정
- VERSION_UPDATE_CHECKLIST.md 추가 (버전 관리 가이드)

**아키텍처 v2.0 설계**
- 8가지 구조적 개선안 검토 (50개 문서)
  1. Dual-Index (채택, P0)
  2. Schema-Registry (채택, P0)
  3. Routing YAML (채택, P0)
  4. Multi-Dimensional Confidence (채택, P0)
  5. RAE Index (제외, 오버엔지니어링)
  6. Overlay Layer (설계만, 향후)
  7. Fail-Safe (채택, P0)
  8. System RAG + Tool Registry (채택, P1) ⭐
- COMPLETE_ARCHITECTURE_V2.md 작성
- umis_rag_architecture_v2.0.yaml 작성
- IMPLEMENTATION_ROADMAP_V2.md 작성

**Clean Design**
- umis_guidelines.yaml → umis.yaml
- name 필드 제거 (단일 진실: config/agent_names.yaml)
- patterns → data/raw/ 이동
- ai_guide → data/raw/ 백업
- .cursorrules 최적화 (243줄 → 148줄, 40% 압축)
- 루트 YAML: 7개 → 4개

**전체 QA 통과**
- 논리적 무결성: ✅
- 구조적 건전성: ✅
- 실행 테스트: ✅ (3/3)
- YAML 문법: ✅ (7/7)

**날짜 정정**
- 2024-11-01/02 → 2025-11-01/02 (33개 항목)

### 🔄 Architecture v3.0 설계 (2025-11-02 추가)

**전문가 피드백 반영**
- 16개 개선안 (8개 → 16개 확장)
- P0 보완 7개 채택
  1. ID & Lineage 표준화 (CAN/PRJ/GND/GED/MEM/RAE)
  2. anchor_path + content_hash (재현성)
  3. TTL + 온디맨드 (비용 통제)
  4. Graph Evidence & Provenance (설명가능성)
  5. RAE Index 복원 (평가 일관성)
  6. Overlay 메타 선반영 (미래 안전)
  7. Retrieval Policy (세밀한 제어)

**config/schema_registry.yaml v1.0 완성**
- 845줄 완전 스펙
- 모든 Layer 통합 정의
- ID 네임스페이스, Lineage, Validation Rules

**Dual-Index 구현 시작 (4/7)**
- SchemaRegistry 로더
- config/projection_rules.yaml (15개 규칙)
- build_canonical_index.py
- HybridProjector (규칙 90% + LLM 10%)

강화된 가치:
- 감사성(A): Lineage, Evidence, Provenance
- 재현성(A): anchor, hash, ID
- 비용 통제: TTL (Lazy 제안 복원)
- 평가 일관성: RAE Index

---

## v6.2.2 (2024-10-30) - Support & Validation System Redesign [MAJOR UPDATE]

### 🔄 시스템 아키텍처 재설계
**핵심 철학**: "가설과 판단에는 근거와 검증이 필요하다"

**지원 모델 업데이트**:
- **Claude-4-sonnet-1m / Claude-4.5-sonnet (1M)**: 권장 모델 ✅
- **GPT-5 (272K)**: 지원 모델
- **Claude-4.1-opus (200K)**: 제한적 지원

**신규 파일 추가**:
- **umis_business_model_patterns.yaml** (985줄): Steve 기회 발굴용 검증된 사업모델 패턴 라이브러리
  - 7개 주요 패턴 (플랫폼, 구독, 프랜차이즈, D2C, 광고, 라이선싱, 프리미엄)
  - 패턴별 트리거 관찰 → 기회 가설 → 검증 프레임워크
  - 50+ 국내외 성공사례 분석

- **umis_disruption_patterns.yaml** (1,912줄): 지배적 사업자 추월 패턴 라이브러리
  - 5개 Disruption 패턴 (혁신, 저가, 채널, 경험, 지속혁신)
  - Counter-Positioning 프레임워크 ("1등이 따라할 수 없는 전략")
  - 9개 실제 추월 사례 심층 분석 (애플-노키아, 넷플릭스-블록버스터, 쿠팡-이베이 등)
  - 1등의 딜레마 → 후발 전략 → 검증 체계

#### 주요 변경사항:

**1. SECTION 0: SYSTEM ARCHITECTURE OVERVIEW 신규 추가**
- **AI 전용 5분 시스템 파악**: 상태 기계 방식으로 전체 구조 명확화
- **정보 흐름 상태 기계**: 7개 상태로 단순화된 프로세스 플로우
- **에이전트 협업 매트릭스**: 역할, 의존성, 지원 관계 명확화
- **의무 검증 체크포인트**: 4개 핵심 검증 지점 정의

**2. SECTION 4: 협업 프로토콜 완전 재설계**
- **Before**: 복잡한 collaboration_protocols (6개 프로토콜, 상세 트리거/모드)
- **After**: 간결한 support_validation_system (1개 원칙 + 4개 체크포인트)

**3. Albert-Steve 검증 균형화**
- **Albert 의무 검증**: Bill + Rachel + Stewart (3명)
- **Steve 의무 검증**: Albert + Bill + Rachel (3명)  
- **균등한 품질 보장**: 중요 결론의 동등한 검증 강도

**4. 자연스러운 지원 시스템**
- **Bill**: 정량 분석 상시 지원 (시장 규모, ROI, 수익성)
- **Rachel**: 데이터 검증 상시 지원 (정의, 신뢰성, 소싱)
- **요청 방식**: "이 시장 규모는?" 같은 자연스러운 질문
- **응답 시간**: Bill(2-4시간), Rachel(30분-2시간)

**5. Steve 기회 발굴 프레임워크 대폭 강화**
- **사업모델 패턴 (7개)**: 플랫폼, 구독, 프랜차이즈, D2C, 광고, 라이선싱, 프리미엄
  - 공백 시장 진입 기회
  - 건설적 전략
  
- **Disruption 패턴 (5개)**: 혁신, 저가, 채널, 경험, 지속혁신
  - 지배적 사업자 추월 기회
  - 파괴적 전략
  - Counter-Positioning: "1등이 따라할 수 없는 전략"

- **통합 접근**: Phase 2에 8개 프레임워크로 확대
  - 패턴 1-7: 건설적 기회 (공백)
  - 패턴 8: 파괴적 기회 (추월)
  - 포트폴리오 균형 (건설 70% + 파괴 30%)

#### 시스템 우아함 달성:

| 개선 영역 | Before | After |
|-----------|--------|-------|
| **협업 복잡도** | 6개 복잡한 프로토콜 | 1개 간단한 원칙 |
| **검증 균형** | Steve만 3명 검증 | Albert-Steve 모두 3명 |
| **지원 접근** | 특정 트리거만 | 자연스러운 상시 지원 |
| **AI 시스템 파악** | 4857줄 전체 읽기 | SECTION 0로 5분 |
| **Steve 프레임워크** | 6개 | 8개 (사업모델 7 + Disruption 1) |
| **기회 발굴 범위** | 공백 시장만 | 공백 + 기존 시장 재편 |

#### 기대 효과:
- **품질 향상**: Albert 결론도 Steve와 동등한 엄격한 검증
- **효율성 증대**: 복잡한 프로토콜 제거, 자연스러운 협업  
- **AI 친화성**: 상태 기계로 명확한 시스템 이해
- **자의성 방지**: 의무 검증으로 품질 보장 체계화
- **기회 발굴 강화**: 검증된 사업모델 패턴으로 체계적 기회 탐색

---

## v6.2.1 (2024-10-29) - ChatGPT Modular Version [RELEASE]

### 📦 ChatGPT 모듈러 버전 생성
**위치**: `.chatgpt/umis_v6.2_modular/`

**주요 구성요소**:
- **custom_instructions_v6.2.txt**: ChatGPT 커스텀 인스트럭션
- **agents/**: 5개 에이전트 모듈 파일
  - `manalyst_albert.yaml`: 시장 구조 관찰 전문
  - `mexplorer_steve.yaml`: 7단계 기회 발굴 프로세스  
  - `mquant_bill.yaml`: SAM 4방법론 + 지속가치 정량화
  - `mvalidator_rachel.yaml`: 창의적 데이터 소싱 + 검증
  - `mcurator_stewart.yaml`: 자율 모니터링 + 토큰 최적화
- **workflows/adaptive_workflow.yaml**: 적응형 워크플로우 시스템
- **UMIS_ChatGPT_Guide_v6.2.md**: 종합 활용 가이드
- **example_usage_v6.2.md**: 5가지 시나리오별 상세 사용 예시

**핵심 특징**:
- 20-30% 낮은 명확도로도 시작 가능한 Discovery Sprint
- 모델별 동적 토큰 관리 (Claude-1M 계열 최적화, GPT-5 지원)
- Stewart의 자율적 진행 모니터링 및 개입
- 완전 자동 문서화 및 세션 연속성 보장
- 필수/선택 파일 구분으로 유연한 모듈 사용

**사용법**: ChatGPT 커스텀 인스트럭션 설정 + 필요 모듈 파일 첨부

---

## v6.2 (2025-10-25) - Autonomous Intelligence Edition [MAJOR UPDATE]

### 🎯 핵심 개선사항
**AI 자율성과 체계적 관리의 균형**: AI의 창의성을 극대화하면서 사용자 부담은 최소화
- **동적 토큰 관리**: 에이전트별 차등 계수 적용으로 효율성 극대화 (v6.2.1 신규)
- **모델별 최적화**: Claude 1M (권장), GPT-5 (지원), Claude 200K (제한) 명시 (v6.2.1 신규)
- **병렬 탐색 프로토콜**: 2-4시간 자율 탐색으로 AI 창의성 극대화
- **스마트 체크포인트**: 필요할 때만 개입하는 적응형 시스템
- **문서 완전 자동화**: Stewart의 지능형 문서 관리로 사용자 부담 제로
- **3가지 실행 모드**: 프로젝트 특성에 따른 동적 모드 전환
- **세분화된 구조**: 4-5 depth 작업리스트와 프로젝트 문서 구조

### 🏗️ 주요 개선사항

#### 1. 병렬 탐색 프로토콜 (Line 313-352)
- **Phase 1**: 2-4시간 완전 자율 탐색 (AI 자율성 100%)
- **스마트 체크포인트**: 30분 발견 공유 및 방향 선택
- **Phase 2**: 방향성 있는 자율 탐색
- **AI 자율성 지표**: creative_discovery, deep_analysis, convergence
- **개입 규칙**: 창의적 발견 중 개입 연기, 중요 피벗 시 즉시 알림

#### 2. 3가지 실행 모드 (Line 354-383)
- **Exploration Mode**: 불확실성 높은 프로젝트 (AI 자율성 90-100%)
- **Collaboration Mode**: 일반 프로젝트 기본값 (AI 자율성 60-70%)
- **Precision Mode**: 중요/민감한 프로젝트 (AI 자율성 30-40%)
- **동적 모드 전환**: Stewart가 프로젝트 진행에 따라 자동 제안

#### 3. Stewart 문서 자동화 (v6.2 신규 기능)
- **실시간 캡처**: 모든 작업 자동 문서화
- **지능형 구조화**: 중요도 기반 자동 분류 및 요약
- **스마트 파일링**: 작업 유형별 자동 경로 지정
- **점진적 문서화**: 핵심 요약 우선, 필요시 확장

#### 4. Data Integrity System 강화
- **4-5 depth 프로젝트 구조**: 세분화된 단계별 문서 관리
- **자동화 기능**: 파일 생성, 메타데이터, 연관 링크, 버전 관리
- **스마트 압축**: 사용 빈도 기반 자동 아카이빙

#### 5. 실행 효율성 극대화
- **병렬 처리 우선**: 독립 작업 모두 동시 실행
- **중복 제거**: 이전 결과 재활용
- **핵심 집중**: 80/20 원칙 적용
- **압축 기법**: 요약 우선, 시각화 활용

#### 6. 파일 구조 최적화 (2025-10-25 추가)
- **AI 가이드 분리**: 657줄의 AI 사용 가이드를 별도 파일로 분리
  - `umis_guidelines.yaml`: 메인 시스템 (4,747줄)
  - `umis_ai_guide.yaml`: AI 가이드 (656줄)
- **가독성 향상**: 메인 파일 12% 경량화
- **유지보수 개선**: 가이드와 시스템 독립적 업데이트 가능

#### 7. 에이전트 이름 체계 개선 (2025-10-25 추가)
- **역할 기반 이름**: 에이전트의 기능을 명확히 반영
  - Albert: Observer (시장 구조 관찰자)
  - Steve: Explorer (시장 기회 탐색가)
  - Bill: Quantifier (시장 규모 수치화 전문가)
  - Rachel: Validator (데이터 검증 전문가)
  - Stewart: Guardian (프로젝트 수호자)

#### 8. 동적 토큰 관리 시스템 (v6.2.1 - 2025-10-25) 🆕
**에이전트별 차등 계수를 통한 컨텍스트 윈도우 최적 활용**

##### 핵심 개선
- **모델별 자동 적응**: 컨텍스트 윈도우 크기 자동 감지 → 최적 계수 선택
- **3단계 모델 티어**: Large (>=500K), Medium (250-500K), Small (<250K)
- **에이전트별 차등**: 작업 특성에 따라 0.60-0.85 범위 적용
- **안전성 강화**: 3단계 안전장치 (70% 경고, 95% 차단, 98% 긴급)
- **공간 효율성**: 큰 모델은 최대 활용, 작은 모델은 안전 확보

##### 모델별 자동 적응형 계수 (Line 1096-1166)
**컨텍스트 윈도우 크기에 따라 자동으로 계수 조정**

```yaml
대형 모델 (>= 500K): Claude 1M 등
  Steve: 0.75, Albert: 0.80, Bill/Rachel: 0.85
  # 넉넉한 공간 → 효율 극대화

중형 모델 (250K-500K): GPT-5 (272K) 등
  Steve: 0.65, Albert: 0.70, Bill/Rachel: 0.75
  # 적당한 공간 → 안전성과 효율 균형

소형 모델 (< 250K): Claude 200K 등
  Steve: 0.60, Albert: 0.65, Bill/Rachel: 0.70
  # 좁은 공간 → 최대 안전성
```

##### 계산 공식 (Line 1168-1211)
```
# 1단계: 모델 크기 감지
if context_window >= 500K → Large Model
elif context_window >= 250K → Medium Model
else → Small Model

# 2단계: 에이전트 + 모델 조합으로 계수 선택
agent_coefficient = coefficients[model_tier][agent]

# 3단계: 최대 쿼리 크기 계산
max_query_size = remaining_context × agent_coefficient

예시:
• 1M, Steve: 600K × 0.75 = 450K (효율)
• 272K, Steve: 182K × 0.65 = 118K (균형)
• 200K, Steve: 110K × 0.60 = 66K (안전)
```

##### 3단계 안전장치 (Line 1122-1153)
1. **경고 임계값 (70%)**
   - 다음 쿼리 크기 제한 (20%만 허용)
   - 세션 종료 권장

2. **차단 임계값 (95% 예측)**
   - 공식: `projected = current + (next × 1.25) + 20K`
   - 예측치가 95% 초과 시 세션 즉시 종료
   - 안전 승수: 1.25 (최악 25% 오차 대비)

3. **긴급 차단 (98% 실제)**
   - 실행 중 예상 외 상황 대비
   - 즉시 중단 및 복구 프로토콜

##### 모델별 지원 상태 (Line 1325-1345)
- **Claude-4-sonnet-1m / Claude-4.5-sonnet (1M)**: 최적 - 권장 모델 ✅
  - 가용 공간: ~910K (91%)
  - 세션당: 3-5개 쿼리
  - Comprehensive Mode: 8-12 세션
  - 대용량 분석에 최적
  
- **GPT-5 (272K)**: 양호 - 지원 ⭐
  - 가용 공간: ~182K (현재) / ~237K (최적화 시)
  - 세션당: 1-2개 / 2-3개 쿼리
  - Comprehensive Mode: 30-40 / 15-20 세션
  
- **Claude-4.1-opus (200K)**: 제한적 - Quick Mode만 ⚠️
  - 가용 공간: ~110K (55%)
  - 세션당: 1개 쿼리
  - Quick Mode만 실행 가능

##### 효과
- **1M 모델**: 최고 효율 (계수 0.75-0.85, 세션당 3-5개 쿼리)
- **272K 모델**: 안전성 확보 (계수 0.65-0.75, 누적 85-90%, 세션당 1-2개 쿼리)
- **200K 모델**: 실행 가능 (계수 0.60-0.70, 누적 89%, Quick Mode)
- **자동 적응**: 모델 감지하여 최적 계수 자동 선택
- **안전성**: 모델별 특성 반영 + 예측 기반 차단으로 컨텍스트 초과 방지

---

## v6.1 (2025-10-25) - AI-Optimized Edition [MAJOR UPDATE]

### 🎯 핵심 개선사항
**UMIS 실행 프로토콜**: AI가 효율적으로 UMIS를 실행할 수 있도록 최적화
- **작업리스트 기반 실행**: 모든 프로젝트는 작업리스트 작성으로 시작
- **50% 토큰 제한**: 각 작업은 가용 토큰의 50% 이하로 설계
- **90% 긴급 중단**: 토큰 90% 도달 시 즉시 중단하여 품질 보장
- **적응적 재평가**: 각 작업 완료 후 재평가 프로토콜

### 🏗️ 주요 개선사항

#### 1. UMIS 실행 프로토콜 (Line 237-307)
- 항상 작업리스트로 시작 (예외 없음)
- 개별 작업 토큰 사용량 명시
- 작업별 재평가 포인트 설정
- 토큰 초과 긴급 프로토콜 추가

#### 2. AI 가독성 향상
- 명확한 AI GUIDE 섹션 추가 (Line 24-435)
- 섹션별 검색 가이드 제공
- 주요 기능 인덱스 구성
- 라인 번호 참조 정확성 개선

#### 3. Stewart 모니터링 강화
- 작업리스트 관리 모니터링 추가
- 40% 토큰 사용 시 경고
- 90% 도달 시 자동 중단
- 작업 완료마다 재평가 실행

#### 4. 프로세스 개선
- 기본 프로세스를 Staged Analysis Mode로 재정의
- Discovery Sprint 후 자동 작업리스트 생성
- 세션 간 컨텍스트 보존 강화
- 적응형 체크포인트 시스템 개선

---

## v6.0.3 (2025-10-25) - Validated Opportunity Discovery Process [CRITICAL UPDATE]

### 🎯 핵심 개선사항
**Steve 가설 검증 프로토콜**: 모든 기회는 체계적으로 검증됨
- **3개 에이전트 병렬 검증**: Albert(구조적), Bill(경제적), Rachel(데이터) 타당성 검증
- **조건부 기회 추적**: Stewart의 월별 모니터링 시스템
- **Stewart 예외 조항**: Steve 가설 검증은 반복 제한에서 제외
- **학습 기반 개선**: 실패를 통한 체계적 학습과 진화

### 🏗️ 주요 개선사항

#### 1. 가설 검증 사이클 (신규)
- 30분 가설 제출 → 2-4시간 병렬 검증 → 2시간 종합 회의
- 검증 결과: 검증됨/조건부/기각
- 최대 5회 반복을 통한 가설 정교화
- 모든 Steve 기회는 자동으로 검증 프로세스 진입

#### 2. 조건부 기회 관리 (신규)
- Stewart가 월별 조건 충족도 모니터링
- 70% 충족: 재검증 준비
- 85% 충족: 실행팀 구성
- 100% 충족: 즉시 실행

#### 3. 검증 효율성 개선
- Fast Track Mode: 긴급 시 2시간 내 Go/No-Go
- Adaptive Depth: 프로젝트 명확도에 따른 검증 깊이 조정
- 중복 검증 방지: 개별 가설과 포트폴리오 검증 분리

#### 4. Steve 프로세스 업데이트
- Phase 6: "검증 준비 및 종합"으로 변경
- Phase 8: "검증 후 처리" 신규 추가
- 검증 결과별 차별화된 후속 조치

---

## v6.0.2 (2025-10-24) - Integrated Opportunity Discovery Process [MAJOR UPDATE]

### 🎯 핵심 개선사항
**Steve의 통합 기회 발굴 프로세스**: 체계적인 7단계 프로세스 도입
- **Extended → Core**: extended_frameworks를 핵심 분석 프레임워크로 통합
- **시간 할당**: 최소 8시간 ~ 최대 3일 명시
- **품질 기준**: 완성도, 깊이, 검증, 실행 가능성 표준화
- **다차원 분석**: 6개 프레임워크 필수 적용

### 🏗️ 주요 개선사항

#### 1. 7단계 통합 프로세스
- Phase 1: 초기 기회 스캔 (2-4시간)
- Phase 2: 다차원 심층 분석 (4-8시간)
- Phase 3: 융합 기회 발굴 (2-3시간)
- Phase 4: 현실성 검증 (2-4시간)
- Phase 5: 우선순위화 (1-2시간)
- Phase 6: 전략적 종합 (2-3시간)
- Phase 7: 최종 문서화 (1-2시간)

#### 2. 6개 핵심 분석 프레임워크
- Defensive Structure Analysis
- Platform Power Interpretation
- Information Asymmetry Mapping
- Regulatory Impact Assessment
- Technology Disruption Scan
- Affinity Economy Exploration

#### 3. 품질 기준 강화
- 프레임워크 적용 완성도
- 분석의 깊이와 구체성
- 검증 프로토콜 통과율
- 실행 가능성과 구체성

#### 4. 협업 터치포인트 명확화
- 각 단계별 협업 시점과 목적 정의
- Albert, Bill, Rachel, Owner와의 상호작용 구조화

---

## v6.0.1 (2025-10-24) - Information Flow Optimization [MINOR UPDATE]

### 🎯 핵심 개선사항
**정보 흐름 최적화**: 에이전트 간 역할과 협업 구조 명확화
- **정보 흐름**: Albert → Steve → Owner의 명확한 단계별 진행
- **계층 구조**: Raw Data → Processed Data → Insights
- **해석 구분**: 구조적 해석(Albert) vs 가설적 해석(Steve)
- **Stewart 강화**: 자율 개입 트리거 구체화

### 🏗️ 주요 개선사항

#### 1. 정보 흐름 아키텍처 신규 추가
- Main Flow: 관찰 → 해석 → 결정
- Information Layers: 4계층 구조 정의
- Support Functions: Rachel/Bill 역할 명확화
- Oversight Function: Stewart 모니터링 강화

#### 2. 에이전트 역할 명확화
- **Albert**: "How" - 구조적 해석 전문
- **Steve**: "Why & What if" - 가설적 해석 전문
- 해석의 명확한 구분으로 중복 제거

#### 3. 협업 프로토콜 개선
- Albert-Bill 병렬 분석 동기화 강화
- 2시간 단위 체크포인트 명시
- 구조-정량 통합 리포트 표준화

#### 4. Stewart 자율 개입 확대
- 4가지 개입 트리거 정의
- 임계값 기반 자동 개입
- 구체적 액션 가이드라인

---

## v6.1a (2025-10-24) - Modular Architecture Edition [ARCHITECTURE UPDATE]

### 🎯 핵심 변경사항
**아키텍처 업데이트**: BMAD-METHOD 분석을 통한 모듈화 구조 도입
- **파일 크기**: 177KB → 16KB (90% 감소)
- **토큰 효율성**: 70% 개선
- **선택적 로딩**: 필요한 모듈만 로드

### 🏗️ 주요 개선사항

#### 1. 모듈화 아키텍처
- **Core Module**: 핵심 에이전트와 워크플로우 유지
- **Meta Workflow**: 지능형 진입점 도입
- **Data Management**: 1차/2차 데이터 분리
- **Lifecycle Management**: 30일 규칙 적용

#### 2. 데이터 관리 체계
- **자동 분류 시스템**: 가치 기반 자동 분류
- **데이터 계보 추적**: 모든 2차 데이터의 출처 추적
- **Working Directory**: 프로젝트 진행 중 데이터 실시간 저장

#### 3. 성능 최적화
- **캐싱 전략**: Hot/Cold 캐시 구분
- **지연 로딩**: 필요시에만 모듈 로드
- **배치 처리**: 일일/주간/월간 자동화

#### 4. 프로젝트 구조 정리
- **core 폴더 제거**: 중복 제거 및 구조 단순화
- **VERSION.txt**: 프로젝트 루트로 이동
- **문서 업데이트**: 모든 참조 경로 수정

### 📁 간소화된 구조
```
umis/
├── umis_guidelines_v6.0.yaml   # 기준 버전
├── umis_guidelines_v6.1a.yaml  # 모듈화 버전
├── VERSION.txt                 # 현재 버전
└── [기타 폴더들]
```

---

## v6.0 (2025-10-22) - Progressive Intelligence Edition [MAJOR UPDATE]

### 🎯 핵심 철학 변화
**메이저 업데이트 핵심**: 실행력과 현실성 대폭 강화
- **명확도 프레임워크**: "뭔가 기회가 있을 것 같아"(20-30%)도 시작 가능
- **병렬 분석 구조**: 현실(Albert)과 기회(Steve)의 균형
- **검증된 의사결정**: 상상이 아닌 데이터 기반 판단

### 🚀 v5.x → v6.0 업그레이드 이유
1. **시스템 전반 재구조화**: 9개 섹션 전체 재정의
2. **핵심 개념 진화**: 적응형 → 점진적 지능
3. **실행 메커니즘 혁신**: 추상적 → 구체적 가이드
4. **에이전트 역할 재정립**: 표준화 + 협업 강화
5. **사용자 경험 혁신**: 진입 장벽 대폭 낮춤

### 🏗️ 1. 시스템 구조 재편

#### 전체 구조 개선
- **9개 섹션 체제**로 재구성 (기존 11개 → 9개)
- **Section 통합/분리**:
  - Section 2: Adaptive Intelligence System으로 통합 (기존 Section 8 흡수)
  - Section 4: COLLABORATION PROTOCOLS 독립 (기존 Section 3에서 분리)
  - Section 10, 11 제거 (불필요한 과거 참조 정리)

#### Market Analysis Framework 체계화
- **3단계 구조의 완성도 향상**:
  - Step 1: Purpose Alignment (WHY) - 12개 관점 (창업자/기업/투자자)
  - Step 2: Market Boundary (WHAT×WHERE×WHO) - 13개 차원
  - Step 3: Market Dynamics (HOW×WHEN×WHY) - 3-part 구조

#### 파일 최적화
- **크기 감소**: 176KB → 169KB (4.0%)
- **실행 예시 분리**: umis_examples.yaml

### 🧠 2. 개념적 강화

#### 이론적 기반 확장
- **immediate_value** (6개 영역): problem_solution_fit, value_proposition_design, customer_discovery, time_to_value, innovation_patterns, lean_validation
- **sustainable_value** (7 Powers 완전 포함): scale/network/switching/brand/resource/process/counter-positioning dynamics

#### Market Dynamics 3-Part 구조
- **Part A**: 경계의 진화 패턴 (13개 차원별)
- **Part B**: 시장 작동 메커니즘 (value/force/lifecycle)
- **Part C**: 통합적 시장 역학 (상호작용/패턴/신호)

### 🤝 3. 협업 메커니즘 강화

#### Albert-Bill 병렬 분석 구조
- **실시간 동기화**: 2시간마다 중간 결과 공유
- **통합 리포트**: Steve에게 구조-정량 통합 데이터 제공
- **예상 효과**: 재작업 빈도 60% → 15% 감소

#### 의사결정 검증 체계 (4단계)
1. Albert, Steve, Bill: 최종 산출물 제출
2. Rachel: 근거 신뢰도 평가 (Evidence Reliability Matrix)
3. Stewart: 논리적 건전성 검증 (Decision Readiness Assessment)
4. Owner + 전체: 최종 의사결정 회의

### 🎯 4. 실행력 강화

#### 명확도 프레임워크 구체화
- **3개 핵심 차원**: 의도 명확도(40%), 도메인 지식(35%), 시급성(25%)
- **Sprint Customization Matrix**: 의도×지식 조합별 4가지 접근법
- **예상 효과**: 프로젝트 시작 시간 -50%, 방향 전환 빈도 -40%

#### Adaptive Safeguards
- **3회 순환 차단**: 동일 주제 3회 반복 시 Stewart 자동 개입
- **예외 처리**: 10x 기회, 블랙스완 이벤트는 제한 없음

### 🔍 5. 모니터링 개선

#### Proactive Monitoring 재구성
**목표 정렬 중심의 4가지 문제 유형**:
- **A. 목표 자체**: obsolete goal, superior opportunity, goal conflict
- **B. 실행 과정**: micro obsession, scope inflation, analysis paralysis
- **C. 방향성**: goal drift, wrong vector, circular motion
- **D. 리소스**: resource drain, capability mismatch

### 📉 6. 대폭 간소화된 섹션들

- **DATA INTEGRITY SYSTEM**: 620줄 → 152줄 (75% 감소)
- **CREATIVE BOOST MODULE**: 800줄 → 120줄 (85% 감소)

### 🎁 7. 에이전트/오너 표준화

- **Agent 4-섹션 구조**: IDENTITY, CAPABILITIES, WORK DOMAIN, BOUNDARIES & INTERFACES
- **Extended Frameworks**: 모든 에이전트에 새로운 시장 차원 대응 능력 추가

### 📊 예상 효과 요약

| 영역 | 개선 효과 |
|------|-----------|
| 프로젝트 시작 시간 | -50% |
| 방향 전환 빈도 | -40% |
| 재작업 빈도 | -45% |
| 의사결정 신뢰도 | +50% |
| 현실성 | +40% |
| 논리 오류 | -60% |

---

## v6.1a (2025-10-23) - [DEPRECATED - Replaced by v6.1a Modular Architecture]

*Note: 이 버전은 2025-10-24 모듈화 아키텍처 버전으로 대체되었습니다.*

원래 v6.1a는 사용자 접근성 강화를 위해 Brownfield Intelligence System과 Activation System을 추가했으나, 
모듈화 아키텍처가 더 효율적인 솔루션을 제공하므로 대체되었습니다.

### 주요 변경사항 (참고용)
- Brownfield Intelligence System 추가 (Section 13)
- Activation Code System 추가 (umis_activation_system.yaml, umis_activation_prompt.md)
- 사용자 친화적 인터페이스 강화

---

## v5.3 (2025-10-21) - Sustainable Advantage Edition
### 추가
- **7 Powers Framework 통합**
  - Market Dynamics에 sustainable_value 개념 통합
  - 지속 가능한 경쟁 우위 메커니즘 분석
- **Agent 역할 강화**
  - Steve: 지속가능성 평가 추가 (step_3_sustainability_assessment)
  - Steve: 방어 구조 분석 추가 (defensive_structure_analysis) 
  - Bill: 시간 가치 정량화 추가 (sustainable_value_quantification)
- **Owner 평가 프레임워크**
  - opportunity_evaluation_framework 추가
  - 즉각적 가치와 지속가능한 가치 균형 평가
  - 2x2 의사결정 매트릭스

### 개선
- value_creation을 immediate_value와 sustainable_value로 구분
- 4가지 지속가능성 다이나믹스 정의
  - scale_dynamics (규모의 경제)
  - network_dynamics (네트워크 효과)
  - lock_in_dynamics (전환 비용)
  - uniqueness_dynamics (독점적 차별화)
- Albert-Steve 협업 강화: 시간 경과 관찰 데이터 전달

---

## v5.2.2 - Enhanced Market Definition (2025-10-21)
### 주요 변경사항
- **Universal Market Definition 개선**: 2단계 계층구조로 확장
- **Market Boundary Dimensions**: 4개 → 10개 (6 core + 4 contextual)
- **Market Dynamics Framework**: 4개 → 10개 (6 core + 4 contextual)
- **파일 크기**: 164KB → 167KB (약 2% 증가)

### 개선된 Core 차원들
#### Boundary Dimensions (6개)
- 기존 4개 유지 (geographic, product_service, value_chain, customer_type)
- 신규 2개 추가 (technology_maturity, temporal_dynamics)

#### Market Dynamics (6개)
- 기존 4개 유지 (value_creation, competitive_forces, market_evolution, regulatory_impact)
- 신규 2개 추가 (technology_evolution, information_asymmetry)

### Contextual 차원들
- 선택적으로 추가 가능한 보조 차원
- Boundary: transaction_model, access_level, price_positioning, channel_structure
- Dynamics: market_signals, cultural_momentum, ecosystem_health, sustainability_factors

---

## v5.2.1 - Simplified Edition (2025-10-21)
### 추가 단순화 (같은 날 업데이트)
- **Section 7 (Workflow Management) 제거**: 단일 워크플로우만 있으므로 불필요
- **UMIS_MODE 환경변수 제거**: 선택지가 없으므로 무의미
- **파일 크기 추가 감소**: 4,116줄 → 4,096줄
- **UMIS_CREATIVE만 유지**: Creative Boost on/off 제어용

---

## v5.2.1 - Simplified Edition (2025-10-21)
### 주요 변경사항
- **Classic Workflow v4 제거**: 단일 Adaptive workflow로 통합
- **Migration Guide 제거**: 더 이상 필요하지 않음
- **파일 크기 최적화**: 약 8% 감소 (4,473줄 → 4,116줄)
- **단순화된 워크플로우 관리**: 모든 명확도 수준을 하나의 워크플로우로 처리

### 제거된 섹션
- Classic Workflow v4 전체 섹션
- Migration from v4 가이드
- Classic 관련 모든 Appendix (6개)
- workflow_modes의 classic 옵션

### 개선사항
- 품질 관리: Stewart의 실시간 모니터링으로 Classic의 정적 게이트보다 우수
- 유연성: 명확도 1-9 모두 대응 가능
- 일관성: 단일 워크플로우로 혼란 제거

---

## v5.2 - Creative Boost Edition (2025-10-21)
### 주요 변경사항
- **AI Brainstorming Framework 통합**: 선택적 Creative Boost 모듈로 통합
- **창의성 증강 도구**: 필요시에만 활용하는 명시적 창의성 도구 추가
- **기존 워크플로우 유지**: 보조 도구로서의 역할 명확화
- **[BRAINSTORM] 태그**: 창의적 프로세스 결과물 명시적 표시

### 새로운 기능
- 10개의 브레인스토밍 모듈 (M1~M10)
- 4개의 Creative Workflows
- 5개의 실행 패턴
- 모듈 간 관계 정의

### 통합 원칙
- 명시적 요청 시에만 활용
- 기존 UMIS 프로세스와 명확히 구분
- 모든 결과물에 [BRAINSTORM] 태그 필수

---

## v5.1.3 - Optimization Update (2025-10-21)
### 최적화
- **구조 최적화**: 중복 주석 통합, 구조적 빈 줄 제거
- **크기 절감**: 7.7% 파일 크기 감소
- **AI 이해도 유지**: 토큰 사용량 최적화하면서 가독성 보존

---

## v5.1.2 - Collaboration Enhancement (2025-10-19)
### 주요 변경사항
- **Albert 역할 확장**: Stage 2의 MECE 기반 사용자 의도 파악 담당
- **Steve 역할 재정의**: 사용자 선택 후 기회 해석으로 변경
- **표현 개선**: Albert의 해석적 표현 제거 ("이유" → 관찰 가능한 표현)
- **기회 원천 통합**: 모든 Stage에 두 가지 기회 원천 반영
  - 비효율성 해소
  - 환경 변화 활용
- **협업 패턴 강화**: Albert → Steve 협업을 핵심 원칙으로 명시

### 연결성 강화
- Stage 간 입력/출력 관계 명확화
- 워크플로우 연결성 개선

---

## v5.1.1 - Market Opportunity Clarification (2025-10-19)
### 주요 변경사항
- **시장 기회 원천 명확화**:
  1. 비효율성 해소
  2. 환경 변화 활용
- **Progressive Narrowing 개선**: 다차원적 관점과 Bottom-up 접근법 추가
- **Steve 역할 변경**: 추론에서 MECE 옵션 제시로 전환
- **Smart Default 강화**: 명시적 Depth 선택 메커니즘 추가
- **편향 제거**: 투자자 중심 편향 제거, 중립적 분석 프레임워크 강화

---

## v5.1 - Enhanced Adaptive Intelligence (2025-10-19)
### 개선사항
- Discovery Sprint 프로세스 정교화
- Stewart의 자율적 모니터링 기능 상세화
- 적응형 워크플로우 단계별 가이드 강화

---

## v5.0 - Adaptive Intelligence Edition (2025-09-16)
### 혁신적 변경
- **적응형 프레임워크 도입**: 20-30% 명확도로도 시작 가능 (기존 80-90%)
- **Discovery Sprint**: 1-2일 빠른 탐색으로 방향 설정
- **Stewart 역할 확장**: Progress Guardian으로 능동적 개입
- **실시간 피벗**: 발견에 따른 유연한 방향 전환
- **자동 데이터 보호**: 2시간마다 체크포인트, 5분 내 복구
- **목표 진화 추적**: 명확도 점수(1-10) 관리

### 새로운 철학
- "Know → Plan → Execute" (v4.0)에서
- "Explore → Discover → Adapt → Succeed" (v5.0)로 전환

### 주요 시스템
1. **Adaptive Framework**: 불확실성 수용과 발견 기반 진화
2. **Proactive Monitoring**: Stewart의 자율적 프로젝트 모니터링
3. **Data Integrity System**: 3단계 데이터 보호 체계
4. **Goal Evolution Tracking**: 목표의 적응적 진화 추적

---

## v4.0 - MECE Framework (2025-09-07)
### 핵심 변경
- **MECE 원칙 전면 도입**: 상호배타적이며 전체를 포괄하는 분석
- **체계적 워크플로우**: Phase 기반 구조화된 프로세스
- **품질 게이트**: 각 Phase 종료 시 검증 체크포인트
- **명확한 역할 분담**: 에이전트별 독립적 책임 영역

### 워크플로우
1. Project Initiation
2. Market Structure Analysis
3. Opportunity Exploration
4. Market Quantification
5. Synthesis & Decision
6. Knowledge Preservation

---

## v3.0 - Simplified Architecture (2025-09-07)
### 주요 변경
- 복잡도 대폭 감소
- 핵심 기능에 집중
- 사용성 개선

---

## v2.0 - Enhanced Collaboration (2025-09-07)
### 개선사항
- 에이전트 간 협업 프로토콜 강화
- 정보 흐름 최적화
- 실시간 협업 지원

---

## v1.x Series - Foundation Building
### v1.8 (2025-09-07)
- 추가 기능 통합
- 안정성 개선

### v1.7 (2025-09-07)
- 성능 최적화
- 버그 수정

### v1.6 (2025-09-03)
- 사용자 피드백 반영
- 인터페이스 개선

### v1.5 (2025-09-03)
- 새로운 분석 도구 추가
- 문서화 강화

### v1.4 (2025-09-03)
- 시장 정의 프레임워크 개선
- 에이전트 역할 명확화

### v1.3 (2025-09-03)
- 첫 안정화 버전
- 기본 기능 완성

### v1.2 (2025-09-03)
- 초기 프로토타입
- 기본 구조 확립

---

## 버전 관리 원칙

### Semantic Versioning
- **Major (X.0.0)**: 큰 구조적 변경, 철학적 전환
- **Minor (x.X.0)**: 새로운 기능 추가, 중요한 개선
- **Patch (x.x.X)**: 버그 수정, 작은 개선, 최적화

### 호환성
- v5.x는 v4.0과 하위 호환 (classic mode 지원)
- v4.0은 v3.0과 비호환 (완전히 새로운 구조)

### 마이그레이션
- 각 Major 버전 업그레이드 시 마이그레이션 가이드 제공
- 점진적 전환 지원

---

*이 문서는 UMIS의 공식 변경 이력입니다. 각 버전의 상세한 변경사항은 해당 버전의 가이드라인 파일을 참조하세요.*
