우선 첨부한 umis.yaml 및 umis_architecture_blueprint.md문서를 통해 umis 시스템의 전체 설계에 대해 정확히 파악해줘. 특히 agent의 역할과 workflow에 대한 충분한 이해가 필요해.

###### ChatGPT의 말:

Reasoned for 8m 8s

바로 요약부터 말하면,
 UMIS는 **6명의 비즈니스 에이전트 + 1명의 추정 전담 Estimator + 4-Layer RAG + 워크플로우 상태기계**로 움직이는 시장 분석 공장입니다.

질문하신 대로,

1. 전체 설계 구조,
2. 각 agent 역할,
3. agent들이 실제로 어떻게 워크플로우 안에서 협업하는지
    를 중심으로 정리해볼게요.

------

## 1. 전체 아키텍처 큰 그림

### 1) 3-Layer 시스템 구조

문서 기준으로 UMIS는 이렇게 3층으로 나뉩니다.

1. **Layer 1 – Business Layer (6 Agents)**
   - Observer (Albert): 시장 구조 관찰
   - Explorer (Steve): 기회 발굴 (RAG + Graph)
   - Quantifier (Bill): 시장/재무 숫자 계산
   - Validator (Rachel): 데이터 정의·신뢰도 검증
   - Guardian (Stewart): 메타-RAG, 진행 관리
   - Estimator (Fermi): **값 추정 전담 (4-Stage Fusion)**
2. **Layer 2 – RAG Data Layer**
   - Canonical Index (CAN-*): 원본 정규화 청크
   - Projected Index (PRJ-*): agent별 뷰 (agent_view=explorer 등)
   - Knowledge Graph (Neo4j, GND-*/GED-*): 패턴 조합/반대 관계
   - Memory Layer (MEM-*, RAE-*, EST-*): 질의/목표/평가/추정 결과 저장
3. **Layer 3 – RAG Runtime Layer**
   - `projection_rules.yaml`: Canonical → Projected 규칙(90% rule-based, 10% LLM 학습)
   - `routing_policy.yaml`: 어떤 질문에 어떤 워크플로우·agent·도구를 쓸지 정의
   - `runtime_config.yaml`: circuit breaker, fail-safe, 모드(hybrid, yaml_only, rag_full)

이 셋이 합쳐져서 “질문 → 적절한 agent와 도구 선택 → RAG/Graph/Memory 활용 → 검증된 산출물”까지 자동으로 흐르도록 설계돼 있습니다.

------

## 2. 6명의 Agent – 역할과 협업 구조

### 2-1. Observer (Albert) – 시장 구조 관찰자

**정체성**: Market Structure Observer. “돈이 실제로 어떻게 오가는지”만 관찰하는 현실주의자.umis

- **포커스**:
  - “시장 구조가 *어떻게* 작동하는가” (How it works)
  - 누가 누구에게 얼마를, 어떤 방식으로, 얼마나 자주 지불하는지
- **하지 않는 것**:
  - “왜 이런 구조가 되었는가” 해석은 Explorer(Steve)에게 넘김
- **주요 산출물**:
  - `market_reality_report.md` (시장 구조 리포트)
  - 가치사슬, 참여자 구조, 마진 구조 등 “구조적 사실” 모음
- **Estimator 협업**:
  - 공개 데이터로 안 나오는 비율/분배(수수료율, 마진, 집중도 등)는 모두 Fermi에게 `estimator.estimate()`로 위임.
- **다른 Agent와의 연결**:
  - Bill(Quantifier): 구조를 숫자로 풀 때 자주 동행
  - Steve(Explorer): Observer 리포트가 Explorer 기회 발굴의 인풋

------

### 2-2. Explorer (Steve) – RAG 기반 기회 탐색자

**정체성**: Market Explorer (RAG-Powered). 패턴/사례를 RAG+Graph로 뒤져서 “어디에 기회가 있는지”를 찾는 전략가.

- **RAG 능력**:
  - Vector 검색: `projected_index (agent_view=explorer)`에서 패턴 검색 (text-embedding-3-large, top_k=5)
  - Graph 검색: Neo4j에서 패턴 조합/관계 탐색
  - 사용 지식: 31개 비즈니스 모델 패턴 + 23개 disruption 패턴 + 성공사례 50+
- **검색 워크플로우** (Explorer 전용 micro-workflow):
  1. `pattern_search` (vector + graph) – 어떤 패턴이 현재 시장과 유사한지
  2. `case_search` – 비슷한 성공 사례(Netflix, Spotify 같은 것들)
  3. 필요 시 Bill(Quantifier)와 협업해 수익성/규모 대략 검증
  4. Fermi(Estimator)에게 “시장 크기/기회 크기” 순서를 묻고
  5. 가설을 `OPP_*.md`로 정리
- **해석 역할**:
  - Albert가 기록한 구조를 보고 “왜 이런 구조가 생겼는지”, “어디에 비효율/미충족 니즈가 있는지”를 해석하는 담당.umis
- **Estimator 협업**:
  - 기회 후보가 여러 개일 때, “대충 어느 정도 크기인지”를 Fermi에게 물어 우선순위를 정함 (잠재 시장 규모·ROI 가늠).
- **검증 & 협업**:
  - 최종 기회 가설을 내기 전,
    - Albert: 구조적으로 가능한지
    - Bill: 경제적으로 말이 되는지
    - Rachel: 근거 데이터가 믿을 만한지
       → **3명 모두 OK일 때만** “검증된 기회 포트폴리오”로 승격.

------

### 2-3. Quantifier (Bill) – 시장 숫자 담당 (SAM/LTV 등)

**정체성**: Market Quantifier. “공식과 엑셀로 말하는 사람”. SAM/TAM/SOM, LTV, ROI 등 정량 분석 책임자.

- **핵심 업무**:
  - SAM 계산 (4가지 방법론으로 ±30% 이내 수렴할 때까지)
  - TAM→SAM→SOM 단계 전환
  - 성장률, 민감도 분석
  - 모든 숫자에 “정의, 출처, 가정(ASM-*), 추정(EST-*)” 명시
- **Estimator와의 역할 분리**:
  - Bill: “공식과 계산”의 주인
    - 예: LTV = ARPU / Churn
  - Fermi: “값의 추정”의 주인
    - 예: ARPU는? Churn은? → 모두 Estimator에게 질문
- **엑셀 산출물**:UMIS_ARCHITECTURE_BLUEPRINT
  - `market_sizing.xlsx`
  - `unit_economics.xlsx`
  - `financial_projection.xlsx`
     → 모두 **100% 수식 기반**이라 재현성·추적성이 높음
- **Validator와의 의존성**:
  - 모든 계산은 Rachel이 데이터 정의를 검증해야 유효. 정의가 모호하면 계산을 멈추고 먼저 Validator 호출.

------

### 2-4. Validator (Rachel) – 데이터 정의·신뢰도 보초

**정체성**: Data Validator. “이 숫자가 정확하냐?”보다도 “이 숫자가 **무엇을 뜻하는지 정의가 맞냐?**”를 보는 사람.

- **역할**:
  - source_registry.yaml 관리 (SRC- ID 발급, 출처·정의·신뢰도 0~100 점수화)
  - Definition Gap 분석 – 같은 ‘매출’이라도 정의 범위가 다르면 경고
  - DART 등의 공시 데이터 / 외부 리포트 소싱·검증
- **워크플로우 상 위치**:
  - **데이터 준비 단계의 메인 에이전트**
  - data_preparation state에서 “신뢰도 ≥ 80%”가 되어야 다음 단계로 진행.umis
- **Estimator와의 관계**:
  - Estimator Stage 1에서 “Validator 확정값”이 있으면 그게 곧 정답 (Evidence 레벨).

------

### 2-5. Guardian (Stewart) – 메타-RAG & 진행 관리자

**정체성**: Knowledge Curator & Progress Guardian. “모든 걸 다 보고 있다가, 이상하면 개입하는 시스템 관리자 + PM + 철학자 혼종.”

- **역할**:
  - Query Memory (중복/순환 질의 감지)
  - Goal Memory (목표 변화 추적, alignment 유지)
  - RAE Memory (평가 기록 재사용)
  - 프로젝트 상태 모니터링 + 모드 전환 (Exploration / Collaboration / Precision)umis
- **프로젝트 라이프사이클에서**:
  - `project_start` 상태에서 명확도 평가 후 Discovery Sprint 유형 결정
  - `[DELIVERABLE_COMPLETE]`, `[PROJECT_END]`, `[PROJECT_CLEANUP]` 같은 call-sign을 보고 자동으로
    - deliverables_registry 업데이트
    - executive_summary 생성
    - 아카이브 작업 실행

------

### 2-6. Estimator (Fermi) – 값 추정 전담 센서 퓨전 엔진

**정체성**: EstimatorRAG. “추정만 한다. 계산은 하지 않는다.” 단 하나의 책임: 필요한 숫자를 **가능한 한 근거 있게** 만들어내고, 확신도를 함께 제공.

- **원칙: Single Source of Truth**
  - 어떤 agent도 스스로 값을 “때려잡지” 않음
  - 추정이 필요하면 모두 Fermi에게 `estimate()` 또는 `validate_estimation()` 호출
- **4-Stage Fusion 구조**:
  1. **Evidence Collection (Stage 1)** – Literal / Direct RAG / Validator / Guardrail
  2. **Generative Prior (Stage 2)** – LLM 지식에서 바로 값 생성
  3. **Structural Explanation (Fermi, Stage 3)** – Fermi 분해, **재귀 없음, max_depth=2**
  4. **Fusion & Validation (Stage 4)** – 위 세 결과를 가중 합성, 일관성 체크
- **budget 기반 탐색**:
  - depth와 LLM 호출 수를 예산으로 제한 (standard/aggressive/minimal 모드)
- **다른 에이전트에게 제공하는 것**:
  - `EstimationResult(value, certainty, source, reasoning_detail)`
  - certainty: high / medium / low
  - source: Literal / Direct_RAG / Validator / Prior / Fermi / Fusion

이 Estimator가 사실상 **전 agent의 공용 “센서”** 역할이라, 전체 시스템을 하나의 두뇌로 묶어주는 핵심입니다.

------

## 3. 워크플로우 – agent들이 실제로 어떻게 움직이는가

### 3-1. 정보 흐름 상태 기계 (system_architecture.information_flow_state_machine)

UMIS 전체 프로젝트는 아래처럼 상태(State)로 정의돼 있습니다.umis

1. **project_start**
   - active: Stewart (Guardian)
   - 작업:
     - 사용자 요청 수신
     - 명확도 평가, Discovery Sprint 유형 결정
2. **discovery**
   - active: all_agents_parallel (6명 전체)
   - fast_track vs full_sprint (명확도 ≥ 7 / < 7)에 따라 시간 조절
   - output: 목표, 시장 경계, 방향성
3. **data_preparation**
   - active: Rachel (Validator)
   - output: 검증된 데이터셋 + 신뢰도 평가 (quality gate: 신뢰도 ≥ 80%)
4. **structure_analysis**
   - active: Albert (Observer)
   - support: Bill, Rachel
   - output: Market Reality Report
   - Albert가 결론을 제시하면, Bill/Rachel/Stewart 3명이 필수 검증 (quality gate)
5. **opportunity_discovery**
   - active: Steve (Explorer)
   - prerequisite: `albert.market_reality_report`
   - Bill, Rachel 지원 받으면서 7단계 기회 발굴 프로세스 수행
   - 최종 기회 가설은 Albert/Bill/Rachel 3명 검증 필수
6. **decision_preparation**
   - active: Stewart (Guardian)
   - 모든 분석 결과를 모아 절차·논리·리스크를 점검
   - output: `Decision Readiness Assessment` (의사결정 준비 상태 보고서)
7. **strategic_decision**
   - Owner(사용자) + Stewart가 중심
   - Stewart가 decision_quality_report 형태로 의사결정 품질까지 평가해서 넘겨줌

요약하면:
 **Guardian(시작) → All Agents(Discovery) → Validator(데이터) → Observer(구조) → Explorer(기회) → Guardian(의사결정 준비) → Owner(결정)**
 이고, 그 사이사이에서 Bill, Rachel, Fermi가 계속 끼어드는 구조입니다.

------

### 3-2. 프로젝트 레벨 워크플로우들

#### (1) Discovery Sprint

- 모든 프로젝트의 기본 시작점. 명확도가 낮아도 일단 시작하고, **대화와 탐색을 통해 문제 정의를 정교화**.
- 명확도 < 7이면 full_sprint (1–3일), ≥7이면 fast_track (2–4시간).
- 이 구간에서는 6명이 거의 병렬로 “대충 전장을 훑는” 느낌으로 작동 (구조 관찰, 기회 스캔, 초기 규모 추정, 데이터 소스 발굴 등).

#### (2) Comprehensive Market Research (2–4주)

- Discovery Sprint 후 “이제 제대로 판다” 모드.
- 예시 구조:
  - Week 1: **market_mapping** – 전체 시장 구조와 경계 파악 (all_agents_deep_dive)
  - Week 2: **dimensional_analysis** – 13개 차원 심층 분석
  - Week 3: **dynamic_patterns** – 시간축·시나리오·와일드카드 분석
  - Week 4: **strategy_synthesis** – 전략·기회 포트폴리오·로드맵
- 중간중간 Guardian이 adaptive_checkpoints(20%, 40%, 60%, 80%)에서 방향성 재점검.

#### (3) Standard Market Analysis (1–2주)

- “standard”로 명시했을 때 쓰는 단축 버전.
- 그래도 Discovery 단계에서 여전히 all_agents_parallel 몫이 존재.umis

#### (4) 토큰/리소스 최적화 전략

- Albert+Bill 병렬 실행, Rachel은 백그라운드 데이터 수집, 독립 작업은 병렬화.
- 이전 세션 결과 재사용, 공통 데이터셋 중앙화, 증분 업데이트 위주.

이 워크플로우들은 `routing_policy.yaml` / `runtime_config.yaml` 쪽에서 모드와 함께 제어된다고 보면 됩니다.

------

### 3-3. Explorer 세부 워크플로우 (기회 발굴)

Explorer 하나만 떼어서 보면, 다음과 같은 **7단계 통합 기회 발굴 프로세스**를 갖고 있습니다.

- Phase 1 – 초기 기회 스캔
  - Albert의 Market Reality Report 해석
  - gap/inefficiency/unmet needs 카테고리별로 기회 후보 최소 9개 도출
- 이후 단계들(문서 상 7단계 전체)은
  - 패턴별 기회 정제
  - 정량·정성 평가
  - Fermi로 시장 규모/ROI 대략 추정
  - Bill/Rachel과 검증
  - 최종적으로 `검증된 기회 포트폴리오`로 정리

Explorer 입장에서의 micro-workflow는 Blueprint의 이 그림이 그대로입니다:
 **pattern_search → case_search → (필요 시) Estimator로 시장 규모 추정 → hypothesis_generation(OPP_\*.md)**.

------

### 3-4. Estimator 4-Stage Fusion 내부 워크플로우

Estimator는 자체적으로 또 하나의 작은 엔진입니다.

1. **Stage 1 – Evidence Collection**
   - Literal (프로젝트 설정에 박혀 있는 값)
   - Direct RAG (과거 추정·학습된 규칙)
   - Validator Search (Rachel이 확정한 데이터)
   - Guardrail Engine (논리/경험적 제약 자동 추출)
      → 확신이 high면 여기서 바로 반환 (fast path).
2. **Stage 2 – Generative Prior**
   - LLM에게 “당신이 책임지고 말할 수 있는 값”을 직접 요청
   - Evidence에서 가져온 hard_bounds를 넘겨서 미친 값 방지
3. **Stage 3 – Structural Explanation (Fermi)**
   - 질문을 2–4개의 변수로 한 번만 분해
   - 각 변수는 다시 Stage 1/2로 추정 (재귀 금지)
   - 구조적 설명(FermiModel) + 값 범위 생성
4. **Stage 4 – Fusion & Validation**
   - Evidence의 definite_value가 있으면 즉시 채택
   - 아니면 Prior/Fermi 결과를 certainty 기반 가중 평균으로 합성
   - 최종 certainty 계산, reasoning_detail 정리

이렇게 추정된 값은 `EST-*` ID로 저장되고, certainty가 높으면 Direct RAG로 편입돼 이후에는 Stage 1에서 바로 답이 나오는 식의 “학습하는 시스템”이 됩니다.

------

## 4. 머릿속에서 UMIS를 그리는 법 (요약)

마인드맵처럼 정리하면:

1. **데이터·값 레벨**
   - Rachel이 SRC-*를 관리해 “이 숫자가 *무엇을 의미하는지*”를 정의하고 신뢰도를 매김.
   - Fermi가 EST-*로 “값 자체”를 추정.
   - Bill이 ASM-* (가정) + SRC-* + EST-*를 엑셀에 얹어서 시장 규모/재무 모델 계산.
2. **구조·기회 레벨**
   - Albert: “지금 시장 구조가 이렇게 생겼다”
   - Steve: “그 구조 안에서 이런 기회들이 보인다” (RAG + Graph)
   - 검증된 기회는 OPP-*로 남음.
3. **프로세스·메타 레벨**
   - Stewart: 상태기계, 모드 전환, 품질 점검, 문서/아카이브 정리, Decision Readiness 평가.
4. **전체 철학**
   - “추정은 Estimator 한 명에게 몰고, 나머지는 구조·기회·계산·검증·메타에 집중한다.”
   - “모든 숫자/주장은 ID(SRC, EST, ASM, OPP, DEL…)를 통해 끝까지 역추적 가능하다.”

질문하신 “agent의 역할과 workflow 이해” 관점에서 보면,

- 각 agent가 맡는 책임이 완전 분리되어 있고,
- system_architecture의 상태기계를 따라 **누가 언제 앞에 나서고 누가 뒤에서 지원하는지**,
- 그리고 Estimator가 어떻게 “값 추정의 단일 관문”으로 쓰이는지
   까지는 지금 설명처럼 머릿속에 구조적으로 잡혀 있습니다.

------

## 사유 공개 블록

**가정**

- umis.yaml은 실제 코드/운영 기준의 최신 가이드라인이고, UMIS_ARCHITECTURE_BLUEPRINT.md는 그것을 재구성한 아키텍처 설명서라고 가정했습니다.
- 문서 내 버전(v7.5.0, v7.11.0, v7.11.1 등)이 섞여 있지만, 6-Agent + Estimator 구조와 4-Stage Fusion, 4-Layer RAG는 공통 코어로 유지된다고 보았습니다.

**근거**

- system_architecture.information_flow_state_machine에서 각 상태별 active_agents 및 outputs 정의.umis
- SECTION 6: AGENTS에서 각 agent의 role, capabilities, collaboration, boundaries 명시 (Observer, Explorer, Quantifier, Validator, Guardian, Estimator).
- Blueprint의 6-Agent 표와 데이터 흐름 다이어그램, Estimator 4-Stage Fusion 설명.
- RAG 4-Layer 구조 설명 (Canonical, Projected, Knowledge Graph, Memory) + ID namespace 표.
- Discovery / Comprehensive / Standard workflow 설명과 token_optimization, adaptive_checkpoints.

**추론 경로**

1. 먼저 Blueprint로 전체 구조(레이어, 6-Agent, Estimator, RAG)를 잡았습니다.
2. 이후 umis.yaml의 SECTION 0(정보 흐름 상태기계)와 SECTION 6(agents)을 매핑해서
   - “어느 상태에서 어느 agent가 front에 서는지”를 정리했습니다.
3. 각 agent 블록 내 `role_boundaries`, `support_and_validation`, `fermi_role_boundaries` 등을 기준으로
   - Estimator가 언제 호출되고
   - 어떤 agent가 누구에게 검증을 받는지
      를 그래프 형태로 재구성한 뒤 서술형으로 풀어냈습니다.
4. 마지막으로 Explorer/Estimator의 세부 워크플로우(Explorer workflow, 4-Stage Fusion) 부분을 세부 설명으로 붙여 전체 흐름의 “실행 감각”을 보완했습니다.

**대안적 해석**

- Estimator를 “7번째 agent”로 비즈니스 레이어에 올려놓고, 나머지 5명을 “라인 역할(관찰/기회/계산/검증/메타)”로 보는 관점도 가능합니다. 문서에서는 보통 6-Agent + Estimator로 표기하지만, 실제 작동은 사실상 7 역할 구조입니다.
- 또 다른 관점으로는 Guardian 중심의 “Meta-RAG + 상태기계” 관점에서, 나머지 agent들을 각 state에 붙는 worker로 보는 방식도 가능합니다.

**불확실성 / 리스크**

- 제공된 snippet 기준으로 Explorer의 7단계 프로세스 전체 텍스트, Guardian의 세부 메타-RAG 알고리즘 등은 일부만 보였기 때문에,
  - 세부 단계명이나 시간 배분은 약간 다를 수 있습니다.
- umis.yaml 안에 구버전(v7.5.x, 7.8.x) 레거시 설명이 섞여 있는데, Blueprint 기준(v7.11.x)으로 정리했기 때문에,
  - Phase/Stage 용어가 과거 문서와 완전히 일치하지 않을 수 있습니다.

**검증 방법 제안**

- 제가 정리한 구조가 맞는지 확인하시려면:
  1. umis.yaml의 `system_architecture.information_flow_state_machine` 블록과
  2. SECTION 6: AGENTS 각 agent 블록,
  3. Blueprint의 “6-Agent System” + “Estimator 4-Stage Fusion” + “4-Layer RAG Architecture”
      이 세 곳을 나란히 보시면, 여기서 서술한 흐름과 거의 1:1 매칭되는 것을 확인하실 수 있습니다.

------

이 상태에서라면, “UMIS 안에서 어떤 작업을 어느 agent한테 설계해야 하는지”, “Estimator를 언제 호출해야 하는지”, “새 워크플로우를 어디에 꽂을지” 같은 설계 논의를 바로 시작할 수 있는 수준의 이해는 확보된 상태입니다.

##### 나의 말:



UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.md

파일



DATA_SOURCE_PRIORITY_REDESIGN.md

파일

umis의 agent의 역할을 완전히 재설계 하고자 해. 이에 따라 workflow도 재설계 되어야 하고. 내가 첨부한 DATA_SOURCE_PRIORITY_REDESIGN.md, UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.md 두 개 파일을 꼼꼼히 읽고, 이 재설계안의 구조적 오류가 있는지 확인하고 장단점 및 개선방안에 대해 알려줘.

###### ChatGPT의 말:

Reasoned for 14m 48s

바로 핵심부터 갈게요.
 지금 `DATA_SOURCE_PRIORITY_REDESIGN.md`랑 `UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.md`는 “지향점”은 완전 일치하는데, 중간에 몇 군데 구조가 깨져 있습니다.
 (특히 Estimator, Tier 개념, Quantifier/Calculator 관계)

------

## 1. 이 재설계안이 하려는 것 (요약)

두 문서를 합치면 의도는 대략 이겁니다:

1. **데이터 사용 순서 고정**
   - 공식/검증된 데이터(Tier 1–2) → 안 나오면 **Estimator 추정(Tier 3)** → 그래도 안 되면 **LLM 일반지식(Tier 4)**.
2. **Observer/Explorer는 “비즈니스 판단”에 집중**
   - 구조/기회 자체는 Observer·Explorer가 책임
   - 수치 계산은 Calculator, 데이터 수집은 Validator, Pure guess는 Estimator에 위임.
3. **Calculator를 수학·수렴 엔진으로 승격**
   - Mode 1: Exact (모든 변수가 Tier 1–2면 정확 값) UMIS_ARCHITECTURE_BLUEPRINT
   - Mode 2: Convergence (여러 공식 + 변수별 Tier 1–4 조합 → CV, z-score, 가중 평균)
   - Fermi 분해도 Calculator 쪽으로 옮김. UMIS_v8_AGENT_ROLES_AND_WORKFLO…
4. **Estimator는 “진짜 마지막 Pure Guesser”로 축소**
   - Stage 3(Fermi), Stage 4(Fusion)을 떼어내고, **Generative Prior(내적 확신 기반 “찍기”)만 담당**.
5. **Validator는 “데이터 헌터 + Fact-check 게이트키퍼”**
   - Tier 1–2 자료를 끝까지 긁어오고, 최종 보고 전에 모든 주장에 신뢰도 태그 부여.

이 방향성 자체는 매우 일관적입니다. 문제는 **기존 아키텍처와의 접합부**에서 몇 군데가 서로 모순을 일으키고 있다는 점입니다.

------

## 2. 구조적 오류 / 충돌 포인트

### 2-1. Estimator: “4-Stage Fusion” vs “Pure Guesser” 모순

- 기존 설계 / `umis.yaml` / Blueprint에서는 Estimator가 **4-Stage Fusion (Evidence → Prior → Fermi → Fusion)** 전체를 소유하는 “값 추정 전문 Agent”입니다.

- Data Source Priority 문서도 Tier 3를 이렇게 정의합니다:

  > tier_3_estimator_fallback: sources: 4-Stage Fusion Architecture (Evidence → Prior → Fermi → Fusion) DATA_SOURCE_PRIORITY_REDESIGN

- 그런데 v8 설계에서는 Estimator_v8이 이렇게 정의됩니다:

  - removed: Stage 3(Fermi) → Calculator로 이동, Stage 4(Fusion) → 불필요
  - remaining: Stage 1(Evidence) Fast Path, Stage 2(Prior) 유일한 추정
  - role: Pure Guesser (Last Resort)

즉, **같은 Estimator를 두 문서가 서로 다른 존재로 정의**하고 있습니다.

- Data Source 문서: “4-Stage Fusion을 가진 Estimator가 Tier 3”
- v8 문서: “4-Stage Fusion은 없고, Estimator는 Pure Guesser”

이건 단순 디테일 문제가 아니라,
 **“단일 진실의 원천(Single Source of Truth)”로 설계된 Estimator 철학을 깨는 수준의 구조적 모순**입니다. UMIS_ARCHITECTURE_BLUEPRINT

------

### 2-2. Tier 개념의 이중 사용 + 번호 꼬임

1. **Data Source Tier (문맥 A: 데이터 신뢰도)** DATA_SOURCE_PRIORITY_REDESIGN
   - Tier 1: 공식 데이터 (KOSIS, DART...)
   - Tier 2: 검증된 상업 리포트
   - Tier 3: Estimator (4-Stage Fusion)
   - Tier 4: LLM 일반 지식 (Baseline)
2. **Calculator 4-Tier Pipeline (문맥 B: 변수 수집/분해)**
   - Observer → Calculator: “4-Tier Pipeline으로 변수 수집”이라고 서술. UMIS_v8_AGENT_ROLES_AND_WORKFLO…
   - Fermi 예시에서는:
     - 공연장수: tier_2 Validator
     - 가동일: tier_3_fermi (분해) → 365일 × 가동률
     - 가동률: tier_4 Estimator(0.27)

여기서 문제:

- Data Source 설계 기준으로는 **Estimator가 Tier 3**인데,
   Fermi 예시에서는 **Estimator를 Tier 4**로 부르고 있음.
- 게다가 Tier라는 단어가
  - “Agent Layer(Tier 1 Business / Tier 2 Evidence / Tier 3 Supervision)”에도 쓰이고 UMIS_v8_AGENT_ROLES_AND_WORKFLO…
  - “Data Source Tier 1–4”에도 쓰이고
  - “4-Tier Pipeline”에도 쓰입니다.

**같은 숫자, 다른 의미**가 세 군데에 겹쳐 있어서
 나중에 YAML/코드/로그에 `tier_3`가 찍히면 “도대체 어떤 tier냐?”가 안 보이는 구조입니다.

------

### 2-3. Quantifier 삭제 vs Bill 생존: Agent/ID 레벨 불일치

- 기존 시스템은 **6 Agent 체계** (Observer, Explorer, Quantifier, Validator, Guardian, Estimator) + ID Namespace(ASM-, EST-, ... )를 전제로 합니다.

- `umis.yaml`에서도 Quantifier는

  - SAM 계산 4가지 방법론 수행
  - `business_metric_calculation`의 owner
  - Bill이라는 캐릭터를 가진 **정량 분석 Agent**입니다.

- 그런데 v8 Agent 맵에는 **Quantifier가 빠져 있고**: UMIS_v8_AGENT_ROLES_AND_WORKFLO…

  - Tier 1: Observer, Explorer
  - Tier 2: Evidence Collector, Validator, Calculator, Estimator
  - Tier 3: Guardian

- 그럼 Quantifier는 죽었냐?
   → 아니요, v8 문서 안에서도 여전히 “Bill”이 검증자로 등장합니다.

  > Explorer.validation: “Albert, Bill, Rachel 검증 필수” UMIS_v8_AGENT_ROLES_AND_WORKFLO…

- 또, Data Source Priority 체크리스트에서도
   “umis.yaml: Quantifier Data Source Priority 수정”이 TODO로 살아 있습니다. DATA_SOURCE_PRIORITY_REDESIGN

즉,

- Bill/Quantifier는 여러 문서와 ID namespace에서 **핵심 엔티티로 가정**되어 있는데,
- v8 Agent 정의에서는 Agent로서의 Quantifier가 사라져 있음.

이 상태로 v8을 적용하면,

- `02_analysis/quantifier/market_sizing/` 폴더 구조, ASM- ID의 owner,
- `market_sizing.xlsx`의 책임자 등이 공중에 붕 뜹니다.

이건 “역할 합치기”를 하려다가 **ID/폴더/검증 프로토콜 레벨에서 구조가 깨지는 전형적인 패턴**입니다.

------

### 2-4. “LLM Complete Abstraction”이 Estimator 밖으로 새어 나감

- 기존 철학:
   “Business Logic은 LLM 모드를 모른다 → Estimator가 LLMProvider를 캡슐화”
  - TaskType: PRIOR_ESTIMATION, FERMI_DECOMPOSITION, FUSION_VALIDATION 등
  - LLM은 Estimator 내부에서만 사용, 나머지는 전부 인터페이스만 호출.
- 그런데 v8에서는:
  - Fermi Decomposition이 Calculator 영역으로 이동
  - Calculator가 `fermi_decomposition`, `convergence_analysis` 등을 수행하는데,
     이 로직이 실제로 LLM을 부를지, Estimator에만 위임할지 정의가 애매합니다.

문서만 보면, **Fermi용 LLM 호출이 Estimator 밖으로 튀어나갈 가능성**이 열려 있습니다.

- 이러면 “LLM Complete Abstraction = Estimator 안에만 LLM”이라는 원칙이 깨지고
  - Estimator
  - Calculator
  - (나중엔 Explorer도?)

여러 군데에서 제각각 LLM 호출을 하게 될 위험이 있습니다.

이건 구조적으로 **“LLM 사용 지점이 분산되는 방향”**이라,
 비용 최적화·모델 교체·로깅·학습 피드백이 다 난잡해지는 패턴입니다.

------

### 2-5. Data Source Priority Workflow vs v8 Workflow의 정렬 부족

Data Source 재설계 문서는 Observer 워크플로우를 이렇게 강하게 못 박습니다:

1. Phase 1: LLM 초안 (Draft, 보고 금지)
2. Phase 2: Validator가 Tier 1–2 데이터 수집
3. Phase 3: Fact-check (Validator 중심 교차 검증)
4. Phase 4: Validator 승인 후에만 사용자에게 보고

그런데 v8의 Observer Workflow는 이렇게 흘러갑니다:

- Phase 1: Structure Analysis (Evidence Collector + Validator)
- Phase 2: Market Sizing (Calculator 위임, 수렴 분석, 최종 SAM 결정)
- 바로 보고서 작성까지 이어지는데,

여기서:

- “Draft vs Fact-checked vs Final”이라는 **상태 구분이 명시적으로 안 들어가 있고**,
- “최종 보고 전 Validator Approval Gate”도 워크플로우 단계에선 빠져 있음
   (Data Source 문서에는 있음, v8 워크플로우에는 없음).

즉, **“Validator는 항상 마지막 문을 통과해야 한다”는 프로토콜이 v8 시퀀스에는 완전히 녹아 있지 않은 상태**입니다.

------

## 3. 장점 (이 재설계가 잘 잡은 포인트)

까는 얘기만 했으니, 이번 설계가 잘 잡은 장점도 정리해보겠습니다.

1. **Layering/책임 분리가 더 직관적**
   - Tier 1: 비즈니스 판단(Observer/Explorer)
   - Tier 2: 증거/수치 생성(Evidence Collector, Validator, Calculator, Estimator)
   - Tier 3: 감독(Guardian) 구조가 꽤 자연스럽습니다. UMIS_v8_AGENT_ROLES_AND_WORKFLO…
2. **Observer의 범위를 “구조 + 규모”로 통합**
   - Market Reality Report가 구조와 SAM/점유율/성장률을 한 몸으로 다루도록 설계되어 있음.
   - 사용자는 “Albert만 보면 시장 전체 그림”을 얻는 구조라 UX 측면에서 깔끔합니다.
3. **Calculator의 역할이 매우 잘 정의됨**
   - 모드 분리(Exact vs Convergence),
   - 여러 공식 생성 + evidence_ratio 기준 신뢰도 평가,
   - CV/Outlier 기반 가중 평균 수렴.
      실제로 “시장 크기 계산 로직”을 하나의 퓨어 함수로 잘 묶었습니다.
4. **Estimator를 “최후 수단”으로 밀어낸 철학**
   - 기존에 “Estimator 너무 많이 쓰인다”는 우려를 정확히 짚고,
   - Validator/공식 데이터 우선 → Estimator는 진짜로 데이터가 없을 때만 쓰도록 설계.
5. **Quick Estimate 시나리오가 현실적**
   - “콘서트 평균 관객수 빨리 알려줘” → Evidence/Validator 빠르게 체크 후, 변수 일부만 Estimator에 맡기는 계산 플로우는 실제 사용 케이스에 매우 잘 맞습니다. UMIS_v8_AGENT_ROLES_AND_WORKFLO…
6. **Evidence Collector를 별도 Agent로 뽑은 점**
   - <1초 Fast Path vs 5–30초 Active Search(Validator)를 분리해, 속도/비용 튜닝 포인트가 명확해졌습니다.

------

## 4. 단점 / 리스크 (구조 관점)

1. **“Estimator = 단일 진실의 원천” 철학이 깨짐**
   - v7.11 아키텍처의 가장 큰 강점 중 하나가
      “모든 추정값은 Estimator에서 나온다(EST-ID로 추적 가능)”였는데,
   - v8에서는 Calculator가 Estimator를 내부적으로 쓰면서도,
      Estimator 자체는 “Pure Guesser”로 축소되어 **중심성이 사라짐**.
2. **Tier 번호/의미 꼬임**
   - Agent Tier / Data Source Tier / 4-Tier Pipeline이 숫자를 공유하면서 서로 다른 의미를 가지므로,
      나중에 로그/메트릭/설정 파일을 해석하기 어려운 구조입니다.
3. **Quantifier 제거에 따른 호환성 붕괴**
   - ID Namespace(ASM-, Quantifier owner),
   - 프로젝트 폴더 구조(02_analysis/quantifier),
   - Validation Checkpoint(Bill SAM 검증) 등 기존 설계와 여러 레벨에서 충돌.
4. **LLM 사용 지점이 분산될 위험**
   - Estimator 내부에 캡슐화된 LLM Abstraction을 깨고,
      Calculator가 Fermi 분해/수렴에서 LLM을 직접 쓸 여지를 만들어버렸습니다.
5. **Fact-check 게이트가 워크플로우에 충분히 녹지 않음**
   - Data Source 문서에서 제안한 “최종 보고 전 Validator 필수 승인”이
      v8의 Observer/Explorer 워크플로우/시퀀스 다이어그램에는 아직 반영되지 않았습니다.

------

## 5. 개선 방향 제안

### 5-1. “보수적 정합화”: Estimator 중심을 유지하는 방향 (추천)

핵심 아이디어:
 **Estimator를 여전히 “추정의 단일 허브”로 두고, Calculator는 그 위에 얹는 수학 엔진**으로 정리합니다.

구체적으로:

1. **Estimator 역할 정의를 다시 묶기**
   - Estimator_v8 문서를 다음처럼 조정:
     - Stage 1 Evidence, Stage 2 Generative Prior, Stage 3 Structural Fermi, Stage 4 Fusion을 계속 소유.
     - 다만 Stage 3/4의 “검색/재귀” 부담을 줄이되,
        **외부(Layer 1/Calculator)에서는 여전히 `estimator.estimate()` 하나만 보도록 유지.**
   - Data Source Tier 3 정의(4-Stage Fusion)를 그대로 살릴 수 있음. DATA_SOURCE_PRIORITY_REDESIGN
2. **Calculator = Estimator + Validator + Evidence Collector 오케스트레이터**
   - Calculator는:
     - 공식 세트 생성
     - 각 변수에 대해 **Data Source Protocol 사용**
        → Tier 1–2: Validator / Evidence Collector
        → Tier 3: estimator.estimate(question, context=...)
        → Tier 4: 허용하지 않거나, 명시적으로 “LLM Baseline”으로 태깅.
   - Fermi 분해는 “질문을 다시 나누어 Estimator에 넘기는 프롬프트” 수준으로만 정의하고,
      실제 LLM 호출은 Estimator 안에서만 일어나는 구조로 맞추는 게 깔끔합니다.
3. **Tier naming 정리**
   - Agent Layer: `agent_tier_1/2/3`
   - Data Source: `data_tier_1_official`, `data_tier_2_commercial`, ...
   - Fermi Pipeline: `fermi_level_1/2` 또는 `component_level_1/2` 식으로 이름 분리.
   - 문서에서 `Tier` 숫자만 보고는 어떤 의미인지 구분이 가능하게.
4. **Quantifier를 “얇은 Agent”로 되살리고, Calculator를 그 툴로 두기**
   - Quantifier(Bill)를 v8 Agent 맵에 다시 넣되:
     - “계산 담당 Agent”
     - 내부 구현은 Calculator 도구 호출 + Excel 산출
   - 이렇게 하면:
     - ID Namespace(ASM-, SAM Validation Report) 유지
     - 기존 폴더 구조/검증 프로토콜과 호환
     - Observer는 “계산을 직접 하지 않고 Bill에게 위임”하는 구조 유지.
5. **Fact-check 프로토콜을 Observer/Explorer 워크플로우에 녹이기**
   - Observer Workflow 끝에
     - `phase_3_fact_check_gate` 추가:
       - Validator Fact-check + 신뢰도 태깅 + Guardian 최종 확인
   - Explorer Workflow도 “기회 포트폴리오 최종 보고 전 Validator/Albert/Bill 3자 검증”을
      Data Source 문서의 Fact-check Gate와 일치시키도록 명시.

이렇게 하면:

- v8에서 도입한 새로운 Calculator/Observer 워크플로우는 유지하면서,
- Estimator/LLM Abstraction/ID Namespace/Fact-check라는 **핵심 아키텍처 자산을 그대로 가져갈 수 있습니다.**

------

### 5-2. “공격적 간소화”: 진짜로 Estimator를 Pure Guesser로 만들고 싶다면

만약 의도가:

> “4-Stage Fusion이 너무 무겁다. Estimator는 진짜 LLM Prior만 하고,
>  나머지 수렴/퓨전은 Calculator에서 하겠다.”

라면, 그 대신 **다음들을 반드시 같이 바꿔야 합니다**:

1. **Blueprint와 Data Source 문서에서 “Estimator = 4-Stage Fusion” 문구 삭제/수정**
2. ID Namespace에서:
   - EST-의 의미를 “Estimator Prior + Calculator Fusion 결과 전체”로 재정의
   - Fusion은 Estimator가 아니라 Calculator 소유로 문서화
3. LLM Abstraction 문서를
   - “Business Logic (Calculator + Estimator) → LLMProvider” 구조로 재작성
   - TaskType도 Calculator 관점으로 재정의 (e.g., FORMULA_DECOMPOSITION, VARIABLE_PRIOR_ESTIMATION, RESULT_VALIDATION).
4. Data Source Tier 3 정의를
   - “Estimator Prior + Calculator Fusion 파이프라인 전체”로 업데이트.

이건 “전면 개편”이라, **v8.0 메이저 버전 업그레이드에 어울리는 선택**이고,
 그만큼 마이그레이션 비용도 큽니다.

------

## 6. 정리

요약하면,

- **의도**:
  - 데이터 우선순위 정렬(Validator → Estimator → LLM),
  - Observer/Explorer는 비즈니스, Calculator는 수학, Estimator는 최후 추정.
- **현재 구조적 문제**:
  - Estimator 정의 두 개가 서로 다름 (4-Stage Fusion vs Pure Guesser)
  - Tier 번호가 세 문맥에서 뒤섞여 있음
  - Quantifier/Bill의 존재 여부가 문서마다 다름
  - LLM Abstraction이 Estimator 밖으로 새어나갈 위험
  - Fact-check Gate가 워크플로우에 완전히 반영되지 않음.
- **추천 방향**은
  - Estimator를 여전히 “추정의 단일 허브”로 두고,
  - Calculator는 공식/수렴/다중 방법론 엔진으로 정의하는 쪽입니다.
  - 그리고 Tier/Agent/ID/Fact-check 네 군데만 일관성 있게 정리하면,
     지금 v8 설계의 장점을 대부분 보존하면서 구조적 모순은 깔끔하게 제거할 수 있습니다.

------

### 사유 공개 (가정 / 근거 / 추론 / 대안 / 리스크 / 검증)

- **가정**
  - v7.11 Blueprint와 `umis.yaml`이 “현재 실제 동작하는 기준선”이고,
     v8·Data Source 문서는 그 위에 얹는 “제안서/리팩토링안”이라고 가정했습니다.
- **근거**
  - Estimator/Quantifier/Validator 역할과 4-Stage Fusion 정의는 Blueprint + `umis.yaml`에서 일관되게 반복됩니다.
  - Data Source Priority 문서는 Estimator를 4-Stage Fusion 기반 Tier 3로 전제합니다.
  - v8 문서는 Estimator_v8을 Pure Guesser로 명시하고, Stage 3/4를 Calculator로 옮겼다고 적어두었습니다.
- **추론 경로**
  1. 세 문서에서 “Estimator가 뭘 하는지” 정의를 나란히 놓고 비교.
  2. Data Source Tier 정의와 Calculator 4-Tier Pipeline에서 Tier 번호/의미를 비교.
  3. v8 Agent 맵과 기존 Agent ID/폴더/Validation Matrix에서 Quantifier/ Bill의 존재 여부 비교.
  4. LLM Abstraction 문서에서 LLM 호출 책임이 어디에 있는지 확인 후, v8의 Fermi/Calculator 설계와 비교.
- **대안**
  - (A) Estimator 중심 모델 유지하면서 Calculator를 오케스트레이션 도구로 정리 (추천)
  - (B) Estimator를 진짜 Pure Guesser로 만들고, Calculator를 새 “Fusion Core”로 승격시키는 대신, Blueprint/ID/LLM Abstraction/Fact-check 문서를 전면 수정하는 공격적 리팩토링.
- **리스크 / 불확실성**
  - 실제 코드 베이스가 v7.11 문서와 100% 일치한다고 전제했는데, 이미 일부는 v8 방향으로 변경되어 있을 가능성. (문서/코드 간 드리프트)
  - Estimator 내부 구현(특히 Budget/Fermi 관련)이 문서와 다를 경우, 추천한 경로에서 조정 필요.
- **검증**
  - 다음과 같은 체크를 하면 제가 말한 구조적 모순이 실제로 코드/폴더에서도 재현되는지 확인할 수 있습니다:
    1. `umis_rag/agents/estimator/` 디렉터리에서 `fermi_estimator.py`, `fusion_layer.py`가 여전히 존재하는지.
    2. `02_analysis/quantifier/` 폴더 및 `market_sizing.xlsx` 생성 로직이 현재도 Quantifier/Bill을 전제로 돌아가는지.
    3. Estimator API (`EstimatorRAG.estimate`)를 호출하는 위치가 Calculator/Quantifier/Observer/Explorer 쪽에서 어떻게 쓰이고 있는지.

이제부터는 “어디까지 Estimator를 남길지”가 완전한 설계 철학의 선택 문제입니다.
 그 철학만 한 번 딱 정하면, 나머지 문서/워크플로우/ID 정리는 아주 기계적으로 밀어붙일 수 있습니다.

##### 나의 말:

2-1. V8 문서의 내용이 맞아. 이렇게 변경되면, 더 이상 estimatore는 Single source of truth가 아니지. 오히려 validator - calculator - estimator로 이어지는 3개의 agent가 business layer에서 활용할 single source of truth를 만들어내는 생산기지 역할을 하게 될꺼야. 2-2. Tier 개념은 정리가 필요해. calculator의 pipeline은 tier말고 다른 단어를 사용하는게 좋아보여.  2-3. Quantifier의 ID를 calculator로 변경하면서, 역할을 변경하는 건이야. 해당 방식이 반영되어야 해. 그리고 붕 떠있는 역할들도 calculator 혹은 guardian 등 몇명 agent에 적절한 agent에 분배해야겠지.  2-4, 2-5. 이 문제에 대한 대안을 정리 해 주었으면 좋겠어. 5-2. 안으로 위에 내용들을 반영해서 재설계 한다면 어떻게 설계할지 blueprint를 정리해줘.

------

###### ChatGPT의 말:

Reasoned for 13m 38s

바로 정리해볼게요.
 말 그대로 **V8 기준으로 “진실 공장(truth factory)”를 다시 설계한다**고 생각하고 갑니다.

------

## 2-1. Single Source of Truth 재정의

이제 이렇게 되는 거죠:

- **예전:** “값 추정 = Estimator 전담 → EST-* 가 곧 SSoT”
- **V8 이후:**
  - **Validator + Calculator + Estimator** 세 명이 함께 돌아가는 **Value Factory**가
     비즈니스 레이어에서 읽는 **단일 truth를 생산**
  - Estimator는 그 공장 안의 **추정 담당 엔진**일 뿐, “혼자 SSoT”는 아님

제안은 이렇게 잡으면 깔끔합니다.

1. **개념적 Single Source of Truth**
   - 이름 예: `Value Store`, `Truth Store`, `Value Registry`
   - “**모든 비즈니스 레이어 값 요청은 여기서 읽는다**”가 규칙
2. **생산 파이프라인(= Truth Factory)**
   - 순서: **Validator → Calculator → Estimator → Fusion**
   - Fusion 결과만 `Value Store`에 **Canonically** 저장

간단한 구조:

```
[비즈니스 레이어의 모든 Agent]
        │
        ▼
  value_service.get(metric, context)
        │
        ▼
  Truth Factory (Validator → Calculator → Estimator → Fusion)
        │
        ▼
  Value Store (canonical values, e.g. VAL-*)
```

여기서 **Estimator는 Truth Factory의 한 Stage**고,
 **SSoT는 “Value Store”**라고 분리해서 정의하면 됩니다.

------

## 2-2. Calculator 파이프라인에서 “Tier” 이름 바꾸기

`Tier`라는 말이 “계층/등급/우열” 느낌이라,
 **“사용 목적이 다른 계산 경로”**라는 의미가 잘 안 살아요.

저는 **“Track(트랙)”** 또는 **“Mode(모드)”** 중 하나를 추천합니다.

### 제안: “Calc Track” 용어로 통일

예시:

1. `deterministic_track`
   - 입력: 검증된 SRC / VAL만 사용
   - 용도: **Value Store에 들어갈 Canonical 계산** (공식 리포트용)
2. `scenario_track`
   - 입력: Canonical 값 + 가정(override)
   - 용도: **What-if, 민감도, 시나리오 분석**
   - 결과는 **Value Store에 안 넣고** 별도 `SCN-*` 정도로 관리
3. `exploratory_track`
   - 입력: 불완전/추정 값, 실험적 formula
   - 용도: Explorer/Observer용 실험 계산, **학습/연구**
   - 여기 결과는 Guardian이 보고 “승격할지 말지” 판단

코드/설정 쪽에서는:

```
calculator:
  default_track: deterministic
  tracks:
    deterministic:
      allow_overrides: false
      write_to_value_store: true
    scenario:
      allow_overrides: true
      write_to_value_store: false
    exploratory:
      allow_overrides: true
      write_to_value_store: false
```

이렇게 가면 `Tier1/2/3` 대신
 **“어디에 써먹을 계산인지”**가 이름에서 바로 읽혀요.

------

## 2-3. quantifier → calculator 리네이밍 + 역할 재배분

### 1) Agent ID 변경

- **기존 ID:** `quantifier`
- **신규 ID:** `calculator`

규칙상 **ID는 불변**이었지만, 지금은 **버전 점프 & 역할 정의 자체가 바뀌는 수준**이라
 “사실상 신규 Agent” 취급을 하는 쪽이 일관성에 맞습니다.

- 코드
  - `umis_rag/agents/quantifier.py` → `calculator.py`
  - config 전부: `agent_id: quantifier` → `calculator`
- RAG / Index
  - `agent_view: quantifier` → `agent_view: calculator`
- ID namespace는 그대로:
  - `ASM-*`, `market_sizing.xlsx` 등은 owner를 **calculator**로 변경

### 2) Calculator의 핵심 역할 정의 (업데이트)

**이제 calculator는 단순 “계산 봇”이 아니라, 완전히 이렇게 정의하는 게 좋습니다.**

1. **Metric Schema Owner**
   - “ARPU가 정확히 뭐냐, 단위/기간은 뭐냐” 같은 **정의/단위/도메인**을 관리
   - `metric_registry.yaml` 같은 걸 calculator가 책임
2. **Formula & Method Library Owner**
   - 31개 방법론 + 그 이상을 **계산 레시피**로 관리
   - 각 formula가 **어떤 Track에서 허용되는지** 정책 포함
3. **Scenario Engine**
   - 모든 “시나리오/민감도/What-if 계산”은 calculator 밑에서 돌아감
   - 가정(ASM-*) 생성/적용/버전 관리까지 담당
4. **Value Factory 내부 계산 허브**
   - Validator가 들고 온 원시 값, Estimator가 제공한 추정 값 등을 조합해
      LTV, CAC Payback 등 **2차/3차 지표를 생산**

### 3) 붕 떠 있던 역할 분배

관성상 지금까지 **주인 없는 역할**일 가능성이 높은 것들 정리해보면:

1. **지표 정의 & 사전 (Metric Dictionary)**
    → **Calculator** 소유
   - 어떤 metric이 어떤 formula/입력/단위를 갖는지
2. **가정(assumption) 묶음의 관리 (Scenario 패키징)**
    → **Calculator + Guardian 분담**
   - Calculator: 실제 숫자/포맷/적용
   - Guardian: 이 Scenario가 “공식/비공식/실험”인지, 메타 레벨 관리
3. **계산 품질 정책**
    → **Guardian**
   - “4개 방법론이 ±30% 이내여야 Canonical로 승격” 같은 규칙
   - Track별로 “어떤 output까지 SSoT 후보로 인정할지” 정의

이렇게 나누면:

- **숫자를 “어떻게” 만드는지는 Calculator**
- **그 숫자를 “어디까지 믿어줄지”는 Guardian**
- **숫자의 원천(원시 데이터)은 Validator**
- **추정이 꼭 필요한 순간은 Estimator**

로 딱 맞게 들어갑니다.

------

## 2-4 / 2-5. “Truth Factory” 구조에 대한 두 가지 대안

여기부터는 “이 문제” =
 **“Estimator 단독 SSoT를 버리고, 3-Agent 공장 구조를 어떻게 노출할 것인가?”**라고 해석해서 씁니다.

### 2-4안. 외부 인터페이스는 그대로 `estimator`, 내부에서 공장 호출

- 비즈니스 레이어에서는 계속:
  - `estimator.estimate("ARPU", context)` 만 호출
- Estimator 내부에서:
  1. Validator에게 확정 값 질문
  2. Calculator에게 2차 계산 위임
  3. 자기 Stage 2~4 돌려서 추정
  4. 이 셋을 Fusion해서 최종 값 반환 & 저장

**장점**

- 기존 인터페이스를 거의 안 바꿈
- “Estimator = 진실 담당”이라는 정신 모델이 유지됨

**단점**

- 실제로는 3-Agent 공장인데, **빌드업이 전부 Estimator 아래 숨겨져서**
   Responsibility 경계가 다시 흐려짐
- “Calculator/Validator가 Truth Factory core다”라는 메시지가 잘 안 먹힘

### 2-5안. `ValueService / TruthService`를 전면에 세우고, 세 Agent는 공장 내부 컴포넌트

새로 이렇게 정의합니다:

- `value_service.get(metric_id, context, policy)`
  - 내부에서:
    - Validator → Calculator → Estimator → Fusion 순으로 호출
  - 결과를 `Value Store`(예: `VAL-*`)에 기록
- Estimator는 이제:
  - `estimator.estimate(...)`가 아니라
  - `truth_factory.estimate_with_fermi(...)` 같은 **내부 컴포넌트 인터페이스**

**장점**

- “SSoT = Value Store”, “Truth Factory = 3 Agent”가 개념적으로 매우 선명
- 나중에 **LLM 모델 바꾸거나, 공장 안에 또다른 Stage 추가**해도
   비즈니스 레이어 인터페이스는 그대로

**단점**

- API, 문서, 정신 모델을 꽤 크게 바꿔야 함
- 기존 “Estimator 중심 설계” 문서와 충돌 → 마이그레이션 작업 필요

> 제안: 이미 V8에서 구조를 큰 폭으로 갈아엎는 중이라면,
>  **2-5안(ValueService 전면 노출)**로 가는 게 장기적으로 훨씬 깔끔합니다.

------

## 5-2. V8을 반영한 전체 Blueprint

이제 위 내용 다 반영해서, **UMIS v8 Blueprint**를 요약 버전으로 다시 그려보겠습니다.
 (기존 Blueprint UMIS_ARCHITECTURE_BLUEPRINT 기준으로 차이만 집중해서요.)

------

### 1) Business Layer Agent 구성 (v8)

| Agent ID     | Name    | 역할 (v8 기준)                                               |
| ------------ | ------- | ------------------------------------------------------------ |
| `observer`   | Albert  | 시장 구조/가치사슬 분석, 정성 인사이트                       |
| `explorer`   | Steve   | 패턴/기회 발굴 (RAG + Graph)                                 |
| `calculator` | Bill    | Metric Schema + Formula Library + Scenario Engine + 계산 허브 |
| `validator`  | Rachel  | 원천 데이터 검증/수집 (SRC-*), Definition Gap 분석           |
| `guardian`   | Stewart | Meta-RAG, 품질 정책, Scenario 등급, 평가 재사용              |
| `estimator`  | Fermi   | Fermi/4-Stage 추정 엔진 (Truth Factory 내부 컴포넌트)        |

**핵심 변화**

- `quantifier` → `calculator`로 ID/역할 전면 교체
- “값의 진실”은 Estimator가 아니라,
   **Validator + Calculator + Estimator가 합쳐진 Truth Factory + Value Store**가 담당

------

### 2) Truth Factory & Value Store

#### Value Store: 새로운 SSoT 층

새 Prefix 하나를 도입하는 버전을 제안합니다.

- **`VAL-\*` : Canonical Value Record**
  - metric_id (예: `ARPU_MRR_monthly_kr_consumer`)
  - value, unit, period
  - source_mix (literal / calculated / estimated 비중)
  - lineage: `SRC-*`, `ASM-*`, `EST-*` 리스트
  - certainty: high / medium / low
  - policy_tag: `official / scenario / experimental`

`EST-*`는 이렇게 의미가 바뀝니다.

- 예전: “Estimator 최종 추정 결과 = 곧 진실”
- 이제: “Estimator Stage 결과(추정 이벤트)”
  - 여러 `EST-*`가 하나의 `VAL-*`에 기여할 수 있음
  - Fusion 결과가 `VAL-*`가 되는 구조

#### Truth Factory 파이프라인

```
[Value Query] (metric_id, context, policy)
        │
        ▼
 Guardian
  - Query Memory 확인 (중복/루프 방지)
  - Policy 로딩 (ex: 'official_strict')
        │
        ▼
 Validator
  - SRC-* 조회 + 신규 원천 검색
  - 확정 값 후보(LiteralCandidate) 생성
        │
        ▼
 Calculator
  - Metric Registry 조회
  - Formula Library 적용
  - Track별 계산 (deterministic / scenario / exploratory)
  - CalculatedCandidate 생성
        │
        ▼
 Estimator (4-Stage)
  - Evidence → Prior → Fermi → Fusion
  - EstimatedCandidate 생성
        │
        ▼
 Fusion Layer (Truth Factory Core)
  - Policy에 따라 Literal > Calculated > Estimated 순으로 가중
  - 일관성 검증 (Guardian 규칙 활용)
  - 최종 CanonicalValue → VAL-*로 기록
        │
        ▼
 Value Store
  - 이후 모든 Agent는 VAL-*만 읽어서 사용
```

------

### 3) Calculator 설계 (Track 기반)

#### Calculator 역할 세분

1. **Metric Registry**

```
metrics:
  ARPU_MRR_monthly_kr_consumer:
    unit: KRW
    period: month
    owner: calculator
    definition: "한국 소비자 월 MRR 기준 ARPU"
    formula:
      default: "total_mrr / active_subscribers"
      inputs: [total_mrr, active_subscribers]
```

1. **Formula Library**

- “31개 방법론” → `formulas/` 아래 YAML/JSONL로 선언적 정의
- 각 formula에:
  - applicable_metrics
  - required_inputs
  - allowed_tracks (deterministic/scenario/exploratory)
  - convergence_rule_id (Guardian가 관리하는 정책 ID)

1. **Calc Track 구조**

```
calculator:
  default_track: deterministic
  tracks:
    deterministic:
      allow_estimated_inputs: false
      allow_scenario_overrides: false
      converge_required: true
      write_to_value_store: true
    scenario:
      allow_estimated_inputs: true
      allow_scenario_overrides: true
      converge_required: false
      write_to_value_store: false
    exploratory:
      allow_estimated_inputs: true
      allow_scenario_overrides: true
      converge_required: false
      write_to_value_store: false
```

- **Truth Factory에서 공장 가동할 때**,
   `policy → track` 매핑해서 어떤 계산 경로 쓸지 선택

------

### 4) Guardian의 새 역할 정리

Guardian은 이제 단순 Meta 로그 관리자에서,
 **“품질 정책 관리자 + 시나리오 심사관”**으로 올라갑니다.

1. **Policy 관리**

```
policies:
  official_strict:
    min_literal_ratio: 0.7
    allow_exploratory_track: false
    min_convergence_methods: 2
    max_spread_ratio: 0.3

  scenario_fast:
    min_literal_ratio: 0.0
    allow_exploratory_track: true
    min_convergence_methods: 1
    max_spread_ratio: 1.0
```

1. **Scenario 등급**

- Scenario마다:
  - `scenario_id`, `base_val_ids`, `overrides(ASM-*)`, `grade(official/sandbox/experimental)`
- Calculator가 계산한 Scenario 결과에 대해:
  - Guardian이 보고 “공식 리포트에 써도 되는지, 내부 실험인지” 라벨링

1. **RAE Memory / Evaluation 재사용**

- Truth Factory 결과에 대한 Guardian의 평가를 `RAE-*`로 저장
- 같은 유형의 질의가 들어오면, 기존 평가를 활용해
   “이 정책이면 previous run에서도 문제가 없었다” 판단

------

### 5) Agent별 Truth Factory 사용 패턴 (v8)

- **Observer / Explorer**
  - 대부분 `scenario` / `exploratory` track을 사용
  - 가설/패턴 검증용 Value를 뽑아서 리포트에 반영
- **Calculator**
  - 자기 자신이 Truth Factory 안의 계산 허브지만,
     다른 Agent 요청에 대해서도 Value Store를 통해 **Canonical 값**만 열람
- **Validator**
  - Truth Factory에 들어갈 **LiteralCandidate의 질** 개선에 집중
  - “Definition Gap”을 찾아 metric_registry / schema에 피드백
- **Guardian**
  - Truth Factory 실행 로그를 기준으로
     품질/비용/정확도 메타 분석 → 정책 업데이트
- **Estimator**
  - 이제는 “SSoT를 찍어내는 주인”이 아니라
     **“Literal/Calculated로 안 되는 값을 Fermi로 채우는 고급 모듈”**
  - 실패율 0% / 커버리지 100%라는 철학은 그대로 유지

------

## 사유 공개 (가정 · 근거 · 추론 · 대안 · 리스크 · 검증)

### 1. 가정

- V8 문서에서 이미:
  - Estimator 단독 SSoT 구조를 내려놓고,
  - Validator–Calculator–Estimator 3 Agent를 생산기지로 재해석하려 한다고 전제
- “Tier”는 Calculator 내부 파이프라인의 등급/레이블 개념에서 나온 용어였고,
   아직 외부와 강하게 결합된 명칭은 아니라서 바꿀 여지가 크다고 가정
- Quantifier → Calculator 변경은 “이름만 바꾸는 리팩토링”이 아니라
   **역할 자체를 재정의하는 기회**로 보는 것이 목표라고 가정

### 2. 근거

- 기존 Blueprint에서 이미:
  - Estimator가 **모든 추정의 SSoT**였음 UMIS_ARCHITECTURE_BLUEPRINT
  - Validator가 85%의 확정 데이터 담당
  - Quantifier가 31개 방법론으로 Excel 계산 담당
- 이 셋을 파이프라인으로 묶으면,
  - Estimator를 “공장 내부 컴포넌트”화 하는 게 자연스럽고,
  - Value Store 레이어를 따로 두는 게 SSoT 개념에 더 잘 맞음

### 3. 추론 경로

1. “Estimator 단독 SSoT”를 유지한 채 3 Agent를 공장처럼 쓰면,
   - 개념이 꼬이거나, Estimator 아래에 나머지 둘이 들러붙는 구조가 됨
2. 대신, “결과 레코드(VAL-*)가 SSoT”라고 정의하면,
   - Truth Factory(Validator+Calculator+Estimator)가
      “진실을 만들어내는 생산공정”으로 자연스럽게 모델링됨
3. Truth Factory를 어디에 붙이느냐가 2-4/2-5의 본질이라 보고,
   - Estimator 인터페이스 유지형 vs ValueService 전면 노출형 두 가지로 정리
4. Calculator는 이름을 바꾸는 김에,
   - Metric/Formula/Scenario를 다 끌어안는 허브로 격상시키면
      “붕 떠 있던 역할”을 다 빨아들이는 형태가 된다 → 경계가 선명해짐

### 4. 대안

- **대안 A (2-4안)**:
   외부에선 Estimator만 보게 유지, 내부에서 Truth Factory 운영
   → 변경 영향 최소, 개념은 조금 더 애매
- **대안 B (2-5안, 제안안)**:
   ValueService/TruthService를 전면에 세우고
   Truth Factory와 Value Store를 1급 개념으로 승격
   → 마이그레이션 비용은 있지만, V9+ 확장성이 훨씬 좋음

또 다른 변형 대안도 가능하지만,
 **“SSoT = Estimator”라는 문장을 완전히 지우는 방향**만큼은 공통으로 유지하는 게 설계 일관성에 맞습니다.

### 5. 리스크

- **ID Namespace 복잡도 증가**
  - VAL-*까지 추가하면, ID 종류가 더 늘어남
  - 하지만 추적성이 중요하니, 적절한 도구/뷰를 곁들이면 감당 가능
- **마이그레이션 비용**
  - 기존 문서와 코드에서 “Estimator = SSoT” 가정이 많이 박혀 있을 것
  - v8 마이그레이션 가이드에 “Truth Factory & Value Store 전환” 섹션이 필요
- **Track/Policy 조합 폭발**
  - Calculator Track + Guardian Policy 조합이 많아지면 관리가 피곤해질 수 있음
  - 초기에는 2~3개 Track + 2~3개 Policy로 제한해서 시작하는 게 좋음

### 6. 검증 포인트

- 작은 파일럿 프로젝트에서:
  1. **하나의 대표 Metric** (예: B2C 국내 ARPU)에 대해
  2. `official_strict` Policy + `deterministic_track`만 사용해서
  3. Validator → Calculator → Estimator → VAL-*까지 한 번 end-to-end로 돌려본 뒤,
  4. 기존 “Estimator SSoT” 방식과 결과/근거/라인리지 비교해보기

이 테스트를 통과하면,
 Truth Factory + Value Store 구조가 실제로도 잘 작동한다는 실증이 될 거예요.

------

이렇게 정리하면, V8은
 “Estimator 제국”에서 “Truth Factory 공화국”으로 넘어가는 버전이라고 볼 수 있습니다.
 앞으로 세부 스키마/폴더 구조까지 리팩토링할 때도 이 틀을 계속 기준으로 삼을 수 있을 거예요.

##### 나의 말:

이 내용을 기준으로 umis.yaml을 다시 쓴다고 하면 작업을 어떻게 진행하는게 좋을까? 작업 설계를 부탁해

###### ChatGPT의 말:

Reasoned for 8m 57s

요약부터 말하면,
 **“새 umis.yaml을 한 번에 쓰는 게 아니라, 설계 → 뼈대 → 내용 이관 → RAG/코드 연동 테스트” 4단계 프로젝트로 보는 게 좋습니다.**
 그리고 지금 갖고 계신 아키텍처 설계도는 그 4단계의 “정답지” 역할을 하게 되고요. UMIS_ARCHITECTURE_BLUEPRINT

------

## 0. 새 umis.yaml의 목표를 먼저 못박기

작업 들어가기 전에, umis.yaml의 역할을 딱 정리해두면 좋습니다:

1. **“UMIS 사용 설명서”이자 “Cursor 시스템 룰북”**
2. 코드/설정(yaml, 스크립트)과 **1:1로 매핑되는 상위 스펙 문서**
3. RAG 온보딩 스크립트(`sync_umis_to_rag.py`)가 읽어가는 **정규화된 소스** UMIS_ARCHITECTURE_BLUEPRINT

그래서 새 umis.yaml은:

- 길이는 길어도 되지만,
- **중복 정의 X**,
- `config/*.yaml`, `scripts/*.py`, `umis_core.yaml`에 **권한을 위임하는 구조**로 설계하는 게 핵심 목표입니다.

------

## 1. 전체 프로젝트 플로우

단계로 끊으면 이렇게 보는 걸 추천드립니다:

1. **아웃라인/스키마 설계** – 새 umis.yaml의 목차와 섹션 구조를 먼저 정의
2. **“진실의 원천” 분리** – 설정/리스트성 정보는 `config/*.yaml`로 떼어내고, umis.yaml엔 레퍼런스만 남김
3. **섹션 단위 리라이트** – Agent / Workflow / RAG / ID / Runtime 순으로 내용 이관 및 리팩터링
4. **RAG & 실행 테스트** – `sync_umis_to_rag.py`, `02_build_index.py`, 실제 @Agent 호출까지 검증

아래에서 각 단계별로 구체적으로 어떻게 움직이면 좋은지 정리할게요.

------

## 2. 1단계 – 새 umis.yaml 아웃라인/스키마 설계

### 2-1. 최상위 구조 제안

설계도에 나와 있는 구조를 그대로 YAML 목차로 매핑해버리는 식으로 갑니다. UMIS_ARCHITECTURE_BLUEPRINT

예시:

```
umis:
  meta:
    version: "v8.0.0"
    last_updated: "2025-xx-xx"
    description: "Universal Market Intelligence System – Master Rules"

  philosophy:
    core_principles: ...
    design_goals: ...

  agents:
    observer: ...
    explorer: ...
    quantifier: ...
    validator: ...
    guardian: ...
    estimator: ...

  rag_architecture:
    layers:
      canonical_index: ...
      projected_index: ...
      knowledge_graph: ...
      memory_layer: ...

  workflows:
    explorer_workflow: ...
    estimator_4_stage_fusion: ...
    validator_flow: ...
    session_closure: "dev_docs/SESSION_CLOSURE_PROTOCOL.yaml#anchor"  # 참조만

  id_namespace:
    prefixes: ...

  runtime_policies:
    modes: ...
    circuit_breaker: ...

  integration:
    llm_abstraction:
      provider_interface: ...
      task_types: ...
    tooling:
      tool_registry_ref: "config/tool_registry.yaml"
      schema_registry_ref: "config/schema_registry.yaml"

  onboarding:
    cursor_commands: ...
    example_prompts: ...
```

핵심은:

- **“섹션 = 설계도에 있는 큰 박스들”**로 1:1 매핑
- 리스트/표/스키마는 최대한 `config/*.yaml`로 빼고, 여기선 **개념 + 레퍼런스만 남기기**

### 2-2. “Anchor Path” 먼저 설계하기

RAG에서 중요한 게 **anchor_path**였죠. UMIS_ARCHITECTURE_BLUEPRINT

- 새 umis.yaml의 각 블록에
   `anchor_path: "agents.observer.responsibilities"`
   같은 식으로 **안정적인 경로를 먼저 설계**해두면,
- 나중에 `sync_umis_to_rag.py`가 이 anchor_path 기준으로 Canonical Index를 만들 수 있습니다.

그래서 아웃라인 설계할 때:

- “이 블록은 나중에 `CAN-*`로 어떤 패턴을 대표하게 될까?”
- “어떤 agent_view에서 `PRJ-*`로 뽑아볼까?”

이 관점으로 **RAG 친화적인 key 이름**을 미리 정해두는 게 좋습니다.

------

## 3. 2단계 – 진실의 원천(Single Source of Truth) 분리

설계도에 이미 `config/agent_names.yaml`, `config/model_configs.yaml`, `config/tool_registry.yaml` 같은 파일이 정의되어 있습니다. UMIS_ARCHITECTURE_BLUEPRINT

여기서 해야 할 일은:

1. **현재 umis.yaml에 박혀 있는 “리스트/테이블성 정보”를 전부 인벤토리화**
   - Agent 이름/역할/ID
   - Tool 목록 및 파라미터
   - RAG 레이어별 필드 정의
   - Knowledge Graph 패턴/관계
2. 이걸 각각 대응되는 `config/*.yaml`로 이사:
   - Agent: `config/agent_names.yaml`, `config/routing_policy.yaml`
   - RAG 스키마: `config/schema_registry.yaml`
   - Graph 관계: `config/pattern_relationships.yaml`
   - Tool: `config/tool_registry.yaml`
3. 새 umis.yaml에서는 이렇게만 쓰도록 강제:

```
agents:
  registry_ref: "config/agent_names.yaml"
  invariant_ids:
    - observer
    - explorer
    - quantifier
    - validator
    - guardian
    - estimator
  design_rules:
    - "ID는 불변, 이름은 config에서 커스터마이징"
```

이렇게 해두면:

- umis.yaml은 **“철학/원칙과 연결 규칙”**만 남고,
- 실제 값 변경은 항상 `config/*.yaml`에서만 하게 됩니다.

------

## 4. 3단계 – 섹션 단위 리라이트 전략

여기서부터는 실제로 텍스트를 다시 쓰는 단계입니다. 추천 순서는:

### 4-1. Agents 섹션 먼저

1. 각 Agent에 대해 **딱 네 줄만 먼저 정의**:
   - 책임(Single Responsibility)
   - 산출물 (파일/ID prefix)
   - Estimator와의 관계
   - “하지 말아야 할 것”

예시:

```
agents:
  observer:
    id: "observer"
    name_ref: "config/agent_names.yaml#observer"
    responsibility: "시장 구조 분석 및 가치사슬 관찰"
    produces:
      - "market_reality_report.md"
    collaborates_with:
      - "estimator"
    must_not:
      - "값 추정 직접 수행 금지 (Estimator 호출 필수)"
```

1. 그 다음에 **협업 플로우**를 YAML로 선언:

```
collaboration_rules:
  estimator_is_single_source_of_truth: true
  value_estimation:
    allowed_agents: ["estimator"]
    other_agents_must:
      - "질문을 구조화하고 Estimator에 위임"
      - "결과를 검증하거나 재사용만 수행"
```

설계도에 있는 “Single Source of Truth” 원칙을 그대로 옮기되, 자연어 설명 대신 **기계가 읽기 좋아 보이는 규칙형 YAML**로 바꾸는 게 목표입니다. UMIS_ARCHITECTURE_BLUEPRINT

### 4-2. Estimator 4-Stage Fusion을 “정책 YAML”로 재표현

현재 설계도엔 4단계가 텍스트/도식으로 설명되어 있죠. UMIS_ARCHITECTURE_BLUEPRINT

새 umis.yaml에서는:

- Stage 정의
- 각 Stage의 종료 조건
- Budget/Mode 정책

을 전부 구조화합니다:

```
estimator:
  stages:
    - id: 1
      name: "evidence_collection"
      description: "Literal / Direct RAG / Validator / Guardrails"
      early_return_if:
        certainty: "high"
    - id: 2
      name: "generative_prior"
      early_return_if:
        certainty: "high"
    - id: 3
      name: "structural_explanation"
      budget_ref: "config/budget.yaml#stage_3"
    - id: 4
      name: "fusion_and_validation"

  modes:
    standard:
      max_llm_calls: 3
      max_depth: 2
      certainty_threshold: "medium"
    aggressive:
      max_llm_calls: 10
      max_depth: 3
      certainty_threshold: "high"
```

이렇게 해두면:

- Estimator 코드는 **이 YAML을 그대로 읽어서 동작**할 수 있고,
- 나중에 모드를 바꿀 때도 umis.yaml 또는 별도 `config/budget.yaml`만 수정하면 됩니다.

### 4-3. RAG 4-Layer를 “스키마 선언 + 예시”로 나누기

설계도에 있는 Canonical / Projected / Graph / Memory 레이어 설명을, umis.yaml에서는 두 층으로 나눕니다: UMIS_ARCHITECTURE_BLUEPRINT

1. **개념/역할 요약 (umis.yaml에 둠)**
2. **필드 스키마/구체 설정 (`config/schema_registry.yaml`)에 둠**

예:

```
rag_architecture:
  canonical_index:
    id_prefix: "CAN-"
    purpose: "정규화된 원본 청크 – 업데이트 및 Lineage 추적"
    anchor_strategy: "anchor_path + content_hash"
    schema_ref: "config/schema_registry.yaml#canonical_chunk"
  projected_index:
    id_prefix: "PRJ-"
    purpose: "Agent별 검색용 뷰"
    projection_rules_ref: "config/projection_rules.yaml"
  knowledge_graph:
    id_prefix_node: "GND-"
    id_prefix_edge: "GED-"
    db: "neo4j"
    pattern_relationships_ref: "config/pattern_relationships.yaml"
  memory:
    types:
      - "query_memory"
      - "goal_memory"
      - "rae_memory"
      - "estimation_results"
```

------

## 5. 4단계 – RAG & 실행 통합 테스트 설계

새 umis.yaml이 완성되면, 바로 코드/스크립트들과 통합 테스트까지 한 번에 묶어서 “프로젝트 종결 기준”을 만들어두는 게 좋습니다.

### 5-1. RAG 온보딩 테스트

1. `python scripts/sync_umis_to_rag.py` 실행
2. `python scripts/02_build_index.py --agent explorer` 실행
3. `python scripts/query_system_rag.py --q "Estimator Stage 3가 뭐 하는지 설명해줘"`
    → 답변이 **새 umis.yaml의 anchor_path 기반 설명**으로 나오는지 확인

### 5-2. Agent 실행 테스트

Cursor에서:

- `@Observer, UMIS의 6-Agent 구조를 설명해줘`
- `@Fermi, UMIS에서 Churn Rate는 누가 추정해?`

이런 질문을 던졌을 때:

- 답의 내용이 **새 규칙(Estimator만 추정)**을 정확히 반영하는지,
- 이전 세대 umis.yaml에 있던 모호하거나 중복된 지시사항이 사라졌는지

를 체크리스트로 검증하면 됩니다.

------

## 6. 실제 작업 순서를 한 번에 정리해보면

1. **메타 설계 (0.5~1일)**
   - 새 umis.yaml의 최상위 목차/anchor_path 스키마 확정
2. **정보 분리 (1일)**
   - 기존 umis.yaml에서 리스트/테이블성 정보 추출 → `config/*.yaml`로 이동
3. **섹션 리라이트 (에이전트 → Estimator → RAG → Runtime 순, 2~3일)**
   - 각 섹션 작성 후, “이 내용이 어느 코드/설정 파일과 연결되는지” 주석으로 명시
4. **RAG/실행 통합 테스트 (0.5~1일)**
   - 온보딩 스크립트, System RAG 검색, 실제 @Agent 호출까지

이 정도 단위로 잡으면, 중간에 설계 방향을 바꾸지 않는 이상 꽤 안정적으로 리라이트를 진행할 수 있을 겁니다.

------

## 7. 사유 요약 블록

- **가정**
  - 기존 umis.yaml은 길고(6k+ 라인), 중복/산재된 규칙이 많고, 현재 설계도(UMIS Architecture Blueprint)가 “최신 진실”이다. UMIS_ARCHITECTURE_BLUEPRINT
- **근거**
  - 설계도에서 이미 `config/*.yaml`, `umis_core.yaml`, `scripts/*` 구조가 명시되어 있어, umis.yaml이 “메인 스펙 + 룰북” 역할을 하는 것이 자연스럽다.
- **추론 경로**
  - 중복을 없애고 추적성을 높이려면, 값/리스트는 config로, 원칙/관계는 umis.yaml로 분리 → 그걸 RAG 온보딩 스크립트와 직접 연결하는 구조가 합리적.
- **대안**
  - 모든 걸 하나의 초거대 umis.yaml에 몰아넣고, 나머지 파일을 전부 파생물로 취급하는 방식도 가능하지만, 유지보수/자동화/RAG 관점에서 불리함.
- **리스크/불확실성**
  - 기존 코드나 스크립트 일부가 “옛 umis.yaml의 특정 라인 번호” 등을 하드코딩했을 수 있음 → 이관 시 깨질 수 있으므로, 반드시 코드 레벨에서 anchor_path 기반 참조로 수정 필요.
- **검증**
  - 새 umis.yaml만 보고도 UMIS를 재구현 가능한지(설계도와 동일한 수준의 self-contained 문서인지) 점검하는 걸 최종 검증 기준으로 삼는 게 좋습니다.

이렇게 설계를 잡아두면, 나중에 “umis.yaml v9, v10…”로 갈 때도 구조는 그대로 두고 내용만 진화시키는 패턴으로 가져갈 수 있어서, 장기적으로 훨씬 편해집니다.

##### 나의 말:

그럼, 0과 1번 작업을 먼저 시작 해 보자. 정말 중요한 작업인만큼, 다양한 경우의 수를 충분히 고려해서 작업 진행 부탁해

###### ChatGPT의 말:

Reasoned for 12m 27s

바로 0번·1번부터 박살(?) 내 보겠습니다.
 제가 이해한 기준으로 0번/1번 작업을 이렇게 정의하고, 그걸 그냥 지금 수행하겠습니다.

- **0번 작업**:
   v8 설계에서
  - *“Single Source of Truth” 개념*
  - *validator–calculator–estimator 3-Agent truth factory 구조*
  - *Tier/Mode 용어, Quantifier→Calculator ID 변경, Estimator 역할 축소*
     이 네 가지를 **여러 설계안으로 열어 본 뒤, UMIS 철학과의 정합성이 높은 기본 방침을 확정**하는 단계
- **1번 작업**:
   0번에서 확정한 방침을 기준으로, **umis.yaml v8 상위 구조와 agent/truth-factory 관련 스켈레톤을 설계**하는 단계
   (실제 6,000줄짜리 전체 리라이트가 아니라, 그 위를 지배하는 “뼈대” 정의)

------

## 0번 작업: v8 핵심 개념/철학 정리 + 설계 선택지 확정

### 0-1. “Single Source of Truth”를 어떻게 재정의할 것인가

#### 현재 상태 정리

- v7 Blueprint에서 SoT는 **Estimator 4-Stage Fusion**이 사실상 독점하고 있음
   (Evidence → Prior → Fermi → Fusion, failure rate 0%, Estimator만 추정 권한)

- v8 설계에서는 Estimator가

  - Stage 3(Fermi), Stage 4(Fusion)을 잃고
  - **“Pure Guesser (Last Resort)”** 역할만 남음 UMIS_v8_AGENT_ROLES_AND_WORKFLO…

- 대신 **Evidence Collector + Validator + Calculator + Estimator**가 함께 “근거 기반 계산 + 부족한 변수 Fermi + 마지막 Priors”를 수행하는 구조로 재구성되어 있음

- 사용자가 명시:

  > 더 이상 estimator는 Single source of truth가 아니고,
  >  **validator – calculator – estimator**가 Business Layer가 쓰는 SoT를 만들어내는 생산기지

#### 설계안 3개

**안 A. “Truth Factory = 3-Agent Pipeline” + SoT는 “산출물 기준”**

- 개념:
  - SoT의 “주체”는 **하나의 Agent가 아니라, 파이프라인**
     `EvidenceCollector → Validator → Calculator → Estimator`
  - 이 파이프라인이 만들어내는 **TruthRecord(예: EST-*, TRU-*)**가 Business Layer의 SoT
- 특징:
  - Estimator는 그 안의 한 단계(Generative Prior)일 뿐, SoT의 주인 아님
  - Guardian은 이 TruthRecord들의 품질과 사용을 감독하는 “Meta 오너”

장점

- 사용자의 의도와 완전 정합 (“3개 Agent가 SoT 생산기지”)
- v7의 “Estimator 4-Stage Architecture”를 **개념 레벨 truth_engine**으로 재해석 가능
  - Stage 1 Evidence = Evidence Collector + Validator
  - Stage 3 Fermi, Stage 4 Fusion = Calculator의 Fermi + Convergence로 매핑
- SoT가 “데이터 구조(TruthRecord)” 단위로 정의되므로, 나중에 구현에서 agent 구성이 바뀌어도 안정적

단점

- 기존 문서의 “Estimator = SoT” 표현과 살짝 어긋남
- ID prefix(EST-)의 의미를 “Estimator 전용”에서 “Truth Engine 결과”로 바꾸는 해석 전환 필요

------

**안 B. “Calculator 중심 SoT 엔진”**

- 개념:
  - Validator/Evidence Collector는 **데이터 공급자**, Estimator는 **값 채우는 보조**,
     최종적으로 SoT를 확정하는 것은 **Calculator**
- 구현:
  - `Calculator.calculate()` 호출 시 내부적으로
    - EvidenceCollector/Validator 호출
    - 부족한 변수에 Estimator Priors 사용
    - Convergence Engine으로 최종 값 도출 UMIS_v8_AGENT_ROLES_AND_WORKFLO…
  - 결과물(TruthRecord)의 owner를 `calculator`로 둠

장점

- “공식 설계 + 수렴 엔진”이라는 v8의 Calculator 정의와 잘 맞음 UMIS_v8_AGENT_ROLES_AND_WORKFLO…
- “계산 기반 진실”이라는 메시지가 명확해짐

단점

- 사용자가 의도한 “validator–calculator–estimator 3인 공동 생산기지” 라는 스토리와 살짝 충돌
- Validator의 기여가 “전처리”처럼 느껴져 역할이 상대적으로 약해 보일 수 있음

------

**안 C. “Guardian 중심 SoT Registry 오너”**

- 개념:
  - TruthRecord를 물리적으로 보관하는 `truth_registry.yaml`의 공식 오너는 Guardian
  - Validator/Calculator/Estimator는 “truth_candidate”를 만들고, Guardian이 review 후 “truth”로 승격
- 장점:
  - Guardian의 “Process Overseer + 품질 관리” 역할과 잘 맞음
  - SoT 승격/폐기/버저닝 정책을 한 곳에서 관리 가능
- 단점:
  - Guardian 로직이 과도하게 비대해질 위험
  - Business Layer 입장에서는 “Guardian까지 들어가야 SoT가 되네?” 라는 추가 복잡도

------

#### 0-1 결론 (권장 방침)

- **개념적 SoT 주체**:
  - **“Truth Factory Pipeline (EvidenceCollector → Validator → Calculator → Estimator)”**
  - Estimator는 그 안의 **마지막 Prior 단계**일 뿐, SoT의 단독 오너가 아님 (사용자 의도 반영)
- **데이터 관점 SoT**:
  - `TruthRecord`(기존 EST-*를 확장/재해석)
  - owner는 “파이프라인 전체”, Guardian은 “Registry 관리 + 품질 메타”
- 문서화 방침:
  - Blueprint 계열에서는
    - “Estimator 4-Stage Architecture”를 **Truth Engine 4-Stage**로 승격
    - Stage별 담당 Agent를 분리 명시
  - `umis.yaml`과 v8 문서에서는
    - “validator–calculator–estimator 3 Agent가 Truth Factory를 구성”한다고 정식 정의

------

### 0-2. Tier 용어 문제 (Agent Tier vs Data Tier vs Calculator Pipeline)

현재 “Tier”는 최소 3 군데에서 쓰이고 있습니다.

1. **Agent 계층**
   - `tier_1_business_analysis` (observer, explorer)
   - `tier_2_evidence_generation` (evidence_collector, validator, calculator, estimator)
   - `tier_3_supervision` (guardian) UMIS_v8_AGENT_ROLES_AND_WORKFLO…
2. **Data Source Priority Tier**
   - `tier_1_official_data`
   - `tier_2_verified_commercial`
   - `tier_3_estimator_fallback`
   - `tier_4_llm_baseline`
3. **Calculator Fermi 파이프라인에서의 tier_1~4 참조**
   - 변수 수집 시 `tier_1_2`, `tier_3_fermi`, `tier_4_estimator` 등으로 부름

이대로 가면 “Tier가 대체 몇 가지 의미냐?”라는 지옥이 열립니다.

#### 설계안

- **Agent 층위**:
  - 현재 이름 유지: `tier_1_business_analysis`, `tier_2_evidence_generation`, `tier_3_supervision`
  - 이건 “조직/역할 계층”의 의미라 크게 문제 없음
- **Data Source Priority 층위**:
  - 용어를 **`source_tier_\*`로 명확하게 고정**
    - `source_tier_1_official`
    - `source_tier_2_commercial`
    - `source_tier_3_structured_estimation` (기존 estimator_fallback을 확장)
    - `source_tier_4_llm_baseline`
  - `umis.yaml`에 “Tier라는 말은 Source Priority context에서는 항상 `source_tier_*`로만 쓴다”라고 규칙 명시
- **Calculator 파이프라인 층위**:
  - 여기서는 **Tier라는 말 자체를 버리는 것이 깔끔**
  - 예를 들어:
    - `band_1_literal_and_cache` (Evidence Collector)
    - `band_2_validated_data` (Validator, source_tier_1~2)
    - `band_3_fermi_structured` (Calculator Fermi 분해로 얻은 값)
    - `band_4_prior_guess` (Estimator generative prior)
  - 내부 로직에서는 `variable.source_band` + `variable.source_tier` 조합으로 정밀하게 관리
    - 예: `source_band=2, source_tier=1` = “Validator가 찾은 공식 통계”

#### 0-2 결론 (권장 방침)

- 용어 전략:
  - **Agent 계층**: `tier_1/2/3` 유지 (조직 계층)
  - **Data Source Priority**: 항상 `source_tier_*` 네이밍으로 고정
  - **Calculator 내부**: `band` 또는 `source_band`로 용어 변경
- `umis.yaml` v8 상단에 “Tier, Source Tier, Band” 용어 정의 섹션을 하나 두는 것이 좋음

------

### 0-3. Quantifier → Calculator ID 변경 전략

v7 Blueprint는 **Agent ID는 불변 (observer, explorer, quantifier, validator, guardian, estimator)**를 원칙으로 잡고 있었습니다. UMIS_ARCHITECTURE_BLUEPRINT
 하지만 v8에서:

- Quantifier는 사실상 사라지고
- **Calculator**가 “Formula Designer & Convergence Engine”을 맡음 UMIS_v8_AGENT_ROLES_AND_WORKFLO…
- 사용자의 의도는 **“ID도 quantifier → calculator로 바꾸자”**는 것

여기서 선택지가 갈립니다.

#### 설계안 A. 하드 리네임 (quantifier → calculator)

- `umis.yaml`의 canonical ID 자체를 `calculator`로 변경
- RAG 인덱스, tool_registry, 코드 상의 `quantifier`는 모두 `calculator`로 마이그레이션

장점

- 정신 건강에 좋음. 새로 보는 사람은 Quantifier란 말을 아예 안 봄
- v8 이후 문서가 모두 일관된 언어 사용

단점

- v7에서 학습된 System RAG, 기존 문서, commit history 등 모든 곳에 `quantifier`가 남아 있음
- 하위 호환성 이슈: 오래된 프로젝트/세션에서 `quantifier` 언급 시 깨질 수 있음

------

#### 설계안 B. Canonical ID는 그대로, Calculator는 role/name

- canonical ID: `quantifier` 유지
- `agent_names.yaml`에서 `quantifier: name: "Calculator"` 형태로 이름만 바꿈 UMIS_ARCHITECTURE_BLUEPRINT
- 역할 정의에서는 “Quantifier(=Calculator)”로 주장

장점

- 완벽한 하위 호환성
- RAG, 코드 변경 최소

단점

- 문서/코드 곳곳에서 “quantifier / calculator” 이중 언어로 헷갈림
- v8의 명확한 역할 전환(“계산 전문 도구”)이 반쯤 가려짐

------

#### 설계안 C. Migration Layer 도입 (권장)

- canonical ID를 **`calculator`로 바꾸되**, `umis.yaml` 맨 위에 별도 Migration 섹션을 둠:

```
agent_id_migration:
  quantifier:
    new_id: calculator
    deprecated_since: "v8.0.0"
    behavior:
      - "기존 umis_core.yaml 및 RAG 인덱스에서 quantifier는 calculator로 매핑"
      - "tool_registry에서 tool:quantifier:* → tool:calculator:* alias 유지 (1~2 버전)"
```

- System RAG 빌드 스크립트에서
  - 기존 `quantifier` 관련 도구/지식은 자동으로 calculator 네임스페이스로 옮기고
  - alias를 유지하는 호환 계층만 제공

장점

- 사용자 관점: 이제부터는 그냥 calculator만 보면 됨
- 시스템 관점: 과거 자산 최대로 재사용하면서도, 앞으로의 설계는 깨끗해짐

단점

- Migration 코드/설정이 하나 필요
- 1~2 버전 동안은 alias 관리를 해줘야 함

#### 0-3 결론

- **권장**: 설계안 C (Canonical ID = `calculator`, `quantifier`는 migration alias로 처리)
- `umis.yaml v8`에는
  - `agents.tier_2_evidence_generation.calculator`가 canonical
  - 최상단 `agent_id_migration` 섹션에 quantifier→calculator를 명시

------

### 0-4. Truth를 어디에 어떻게 저장할 것인가 (TruthRecord 포맷)

지금 문서 세트에는:

- `source_registry.yaml` (Validator가 raw data 출처 + 신뢰도)
- Estimator 결과용 `EST-*` ID (추정 결과) UMIS_ARCHITECTURE_BLUEPRINT
- Excel 산출물(market_sizing.xlsx 등) UMIS_ARCHITECTURE_BLUEPRINT

는 있지만, “**최종 진실 테이블**”이라는 명시적인 구조는 없습니다. SoT를 깔끔히 다루려면 최소 아래 세 가지 안이 있습니다.

#### 안 1. `truth_registry.yaml` 신설 (TRU-* ID)

- 새로운 아티팩트:

```
truth_registry:
  - truth_id: TRU_market_size_kor_concert_2023
    question: "2023년 한국 공연 시장 규모"
    value: 1.2e12
    unit: "KRW"
    source_tier: source_tier_2_commercial
    pipeline:
      stages_passed: [evidence_collector, validator, calculator]
      last_stage: calculator
    lineage:
      src_ids: [SRC_2025..., SRC_2024...]
      formulas: [CAL_FORM_001, CAL_FORM_002]
      priors: [EST_123]  # 사용된 prior들 (있다면)
    reliability: "high"
```

- TruthRecord는 항상 여기서 조회

장점

- 개념적으로 가장 깔끔
- Guardian에게 registry 관리 책임을 부여하기 좋음

단점

- `EST-*`와의 관계를 새로 정의해야 함
- 기존 Estimator 결과와의 이중 관리 가능성

------

#### 안 2. 기존 `EST-*`를 TruthRecord로 확장

- `EST-*`의 의미를
  - “Estimator가 직접 추정한 값” → “Truth Factory Pipeline이 만들어낸 최종 추정값”으로 확장
- 내부 필드에 `produced_by`와 `source_tier`, `calculator_formulas`를 추가해 Truth 수준까지 끌어올림

장점

- ID 스킴 변경 최소
- 기존 Estimator 문서, 가이드와의 연결을 유지

단점

- 이름이 Estimator 기반이라, “이제는 pipeline 결과다”라는 의미 전환이 문서로 충분히 설명되어야 함
- `truth_registry.yaml` 같은 전용 파일이 없어도 괜찮을지 고민 필요

------

#### 안 3. Excel이 사실상의 Truth (숨은 SoT)

- market_sizing.xlsx / unit_economics.xlsx / financial_projection.xlsx를 “실질 Truth”로 보고,
   각 시트의 핵심 값만 메타 레벨에서 참조

장점

- 구현 변경 거의 없음
- 이미 존재

단점

- LLM/RAG 입장에서 이건 **조회하기 매우 나쁜 형식**
- 출처·신뢰도·Tier·파이프라인 정보가 엑셀 셀에 묻혀버림

------

#### 0-4 결론 (권장 방침)

- 중장기적으로 **안 1 + 안 2 혼합**이 가장 현실적:
  - **단기(v8)**:
    - `EST-*` 스키마를 TruthRecord 수준으로 확장 (source_tier, pipeline, lineage, reliability 필드 추가)
    - Guardian이 “EST-레벨 Truth를 모아 관리”하는 메타 기능만 추가
  - **중장기(v8.x)**:
    - `truth_registry.yaml` 신설
    - 내부적으로 `EST-*`를 truth_id로 사용하거나, TRU-*로 alias 제공
- `umis.yaml v8`에는
  - “TruthRecord = 확장된 EST 스키마 (pipeline 전체 결과)”
  - “향후 truth_registry.yaml로 분리 예정” 정도로 명시

------

### 0-5. 붕 떠 있는 역할 재배치 (Calculator / Guardian / 기타)

v8 문서와 Blueprint를 비교하면, 역할이 붕 뜨는 부분이 몇 가지 있습니다.

정리:

1. **Fermi Decomposition + Fusion**
   - v7 Estimator Stage 3/4 → v8에서는 Calculator의
     - `fermi_decomposition`
     - `convergence_analysis`
        로 이동한 상태
   - 이건 전부 **calculator_v8** 책임으로 보는 것이 자연스럽습니다.
2. **Data Source Priority 적용 로직**
   - “Tier 1 → Tier 2 → Estimator → LLM baseline” 순으로 데이터 소스를 선택하는 로직은
   - **Validator + Evidence Collector + Calculator**가 공동 사용해야 하는 “정책”
   - 현실적으로는
     - 정책 정의: `umis.yaml.data_source_priority` (전역 규칙)
     - 개별 Agent는 이 정책을 호출만 하는 쪽(consumer)
3. **Fail-safe / Circuit Breaker / Mode Toggle**
   - Blueprint의 Runtime Layer(Circuit Breaker)는 Guardian의 “Meta-RAG / 품질 관리” 맥락과 잘 맞음
   - 계산/추정 실패 패턴 추적, 반복 쿼리 탐지 등은 Guardian이 owner
4. **Knowledge Graph / Pattern-level Reasoning**
   - Graph 쪽의 패턴 조합/카운터는 주로 Explorer/Observer의 분석에 쓰임
   - TruthFactory 쪽에서는 Graph를 “고급 Evidence” 수준으로만 사용 → Evidence Collector 범주에 포함

#### 0-5 결론 (역할 배분 요약)

- **Calculator**
  - 공식 생성, Fermi 분해, 변수 수집, 수렴 분석, multi-formula convergence → 전부 여기
- **Validator**
  - Data Source Priority Tier 1~2를 책임지는 “Active Hunter” (공식 통계 + 상업 리포트)
- **Estimator**
  - Tier 3/4에서 쓰이는 Pure Prior (Last Resort), 개별 변수 또는 전체 값에 대한 Priors 제공
- **Evidence Collector (Infra)**
  - Literal / Direct RAG / Cache / Guardrail → “Band 1”의 역할
- **Guardian**
  - TruthRecord 품질 Meta, Runtime Fail-safe, Query/Goal/RAE Memory 관리

------

## 1번 작업: umis.yaml v8 상위 구조·스켈레톤 설계

이제 0번에서 정한 방침을 바탕으로, 실제로 **umis.yaml v8의 상위 구조를 어떻게 짤지** 설계하겠습니다.
 여기서 목표는 “이 구조대로만 가면 실제 6,000줄도 일관되게 채울 수 있다” 수준의 뼈대입니다.

### 1-1. 최상위 구조 패턴 선택지

#### 패턴 A. Agent 중심 구조

```
umis_v8:
  meta: ...
  terminology: ...
  agents:
    tier_1_business_analysis: ...
    tier_2_evidence_generation: ...
    tier_3_supervision: ...
  truth_factory: ...
  workflows: ...
  universal_protocols: ...
```

장점

- v8 문서의 `umis_v8_agents` 구조와 거의 1:1 매핑 가능 UMIS_v8_AGENT_ROLES_AND_WORKFLO…
- Agent를 호출하는 Cursor 관점과 친화적 (사용자가 agent에게 말을 거는 구조)

단점

- Workflow 관점에서 각 Agent가 어떻게 묶이는지 이해하는 데 한 번 더 이동해야 함

------

#### 패턴 B. Workflow 중심 구조

```
umis_v8:
  meta: ...
  terminology: ...
  workflows:
    market_reality_analysis:
      owner: observer
      uses: [evidence_collector, validator, calculator, estimator, guardian]
    opportunity_portfolio:
      owner: explorer
      uses: [...]
  agents: ...
  truth_factory: ...
```

장점

- “사용자가 실제로 수행하는 작업(시장 분석, 기회 발굴, 시나리오 분석)”을 중심으로 읽기 좋음

단점

- Agent 정의가 부록처럼 보일 수 있음
- 기존 umis.yaml이 Agent 규칙 중심 구조였다는 점을 고려하면 이질감

------

#### 권장: 패턴 A 기반 + Workflow를 별도 섹션으로

- 기존 `umis.yaml`의 성격(“Cursor에서 Agent에게 뭘 시켜야 하는지” 가이드)와 잘 맞고,
- v8 문서의 형식과도 거의 동일

------

### 1-2. umis.yaml v8 상위 스켈레톤 (초안)

아래는 “실제 umis.yaml v8을 다시 쓴다”라고 했을 때의 상단 1,000줄의 큰 틀이라고 보시면 됩니다.

```
umis_v8:
  meta:
    version: "8.0.0"
    base_version: "7.11.1"
    status: "design_review"
    migration_notes:
      - "quantifier → calculator ID migration"
      - "Estimator 4-Stage → Truth Factory Pipeline로 일반화"

  terminology:
    agent_tier:
      tier_1_business_analysis: "Observer, Explorer"
      tier_2_evidence_generation: "Evidence Collector, Validator, Calculator, Estimator"
      tier_3_supervision: "Guardian"

    source_tier:
      source_tier_1_official: "정부 통계, DART, 국제기구 등"
      source_tier_2_commercial: "시장조사·컨설팅·증권사 리포트"
      source_tier_3_structured_estimation: "Truth Factory를 통한 구조적 추정"
      source_tier_4_llm_baseline: "일반 LLM 지식 (Fact-check 필요)"

    source_band:
      band_1_literal_and_cache: "Literal, Cache, Guardrail"
      band_2_validated: "Validator가 확보한 확정 데이터 (source_tier_1~2)"
      band_3_fermi_structured: "Calculator Fermi 분해로 얻은 구조적 추정값"
      band_4_prior_guess: "Estimator Generative Prior"

  agent_id_migration:
    quantifier:
      new_id: calculator
      deprecated_since: "8.0.0"
      notes:
        - "v7까지의 quantifier는 calculator로 통합"
        - "tool_registry 및 RAG index에서 alias 유지 (8.x 동안)"

  agents:

    tier_1_business_analysis:

      observer:
        name: "Albert"
        role: "Market Structure + Sizing Analyst"
        classification: "Domain Agent"
        responsibility:
          - "시장 구조 + 규모 통합 분석"
          - "Market Reality Report 최종 책임"
        orchestrates: ["calculator", "validator", "estimator"]
        output:
          - type: "Market Reality Report"
            id_pattern: "DEL_MRR_*"
        interface_ref: "observer_interface_v8"  # dev 문서 스키마 참조

      explorer:
        name: "Steve"
        role: "Opportunity Scout"
        classification: "Domain Agent"
        responsibility:
          - "검증된 기회 포트폴리오 제공"
          - "기회별 시장 크기, ROI 계산 (Calculator 사용)"
        uses: ["observer", "calculator", "validator"]
        output:
          - type: "Validated Opportunity Portfolio"
            id_pattern: "OPP_*"

    tier_2_evidence_generation:

      evidence_collector:
        type: "Infrastructure"
        role: "Fast Path 데이터 확인"
        sources: ["Literal", "System RAG", "Cache", "Guardrail"]
        speed: "<1s"
        band: "band_1_literal_and_cache"

      validator:
        name: "Rachel"
        type: "Support Agent"
        role: "Active Data Hunter"
        responsibility:
          - "Tier 1-2 공식/상업 데이터 적극 수집"
          - "Definition 일치·신뢰도 평가·교차 검증"
        sources: ["DART", "KOSIS", "Official Web", "Reports"]
        operates_on_source_tiers: ["source_tier_1_official", "source_tier_2_commercial"]

      calculator:
        name: "Calculator"
        type: "Tool"
        role: "Formula Designer & Convergence Engine"
        responsibility:
          - "공식 설계, 변수 수집, 수렴 분석"
          - "Fermi 분해 및 convergence"
        modes:
          exact:
            when: "필요 변수 모두 band_1~2에서 확보"
            reliability: "⭐⭐⭐⭐⭐"
          convergence:
            when: "일부 변수 band_3~4 필요"
            reliability: "⭐⭐⭐⭐"
        uses_bands: ["band_1_literal_and_cache", "band_2_validated", "band_3_fermi_structured", "band_4_prior_guess"]

      estimator:
        name: "Fermi"
        type: "Support Agent"
        role: "Pure Guesser (Last Resort)"
        responsibility:
          - "Generative Prior 기반 추정"
          - "Truth Factory에서 band_4_prior_guess 제공"
        when_to_use:
          - "source_tier_1~3에서 데이터를 확보하지 못한 변수"
          - "Calculator convergence 모드에서 필요한 마지막 Priors"

    tier_3_supervision:

      guardian:
        name: "Stewart"
        type: "Supervision Agent"
        role: "Process Overseer & Truth Meta-Manager"
        responsibility:
          - "Workflow 감독 및 품질 관리"
          - "TruthRecord(EST-*) 메타 관리"
          - "Query/Goal/RAE Memory 운영"
          - "Runtime fail-safe (circuit breaker 등) 정책 책임"

  truth_factory:

    description: >
      Validator–Calculator–Estimator 3 Agent와 Evidence Collector가
      함께 TruthRecord(EST-*)를 생산하는 파이프라인.

    artifacts:
      truth_record:
        id_prefix: "EST-"
        fields:
          - question
          - value
          - unit
          - source_tier
          - source_band
          - pipeline:
              - stages_passed
              - last_stage
          - lineage:
              - src_ids
              - formulas
              - priors
          - reliability

    data_source_priority:
      source_tier_1_official:
        priority: 1
        agent: "validator"
        reliability: "HIGH"
      source_tier_2_commercial:
        priority: 2
        agent: "validator"
        reliability: "MEDIUM_HIGH"
      source_tier_3_structured_estimation:
        priority: 3
        agent: "calculator"
        reliability: "MEDIUM"
      source_tier_4_llm_baseline:
        priority: 4
        agent: "estimator"
        reliability: "LOW"

    data_request_protocol:
      step_1_validator:
        description: "모든 Agent는 먼저 Validator에게 데이터 요청"
      step_2_calculator_truth_factory:
        description: "Validator가 실패할 경우, Calculator가 Truth Factory 모드로 구조적 추정 수행"
      step_3_estimator_prior:
        description: "Calculator가 특정 변수에 대해 Prior가 필요할 때 Estimator 호출"
      step_4_record_truth:
        description: "계산 완료 시 TruthRecord(EST-*)로 기록, Guardian이 메타 관리"

  workflows:

    market_reality_analysis:
      owner: "observer"
      phases:
        draft:
          description: "LLM 기반 구조 초안 (사용자에게 보고 금지)"
        data_collection:
          description: "Observer가 필요한 데이터 목록 정의 → Validator/Evidence Collector 호출"
        fact_check:
          description: "Validator가 official/commercial 데이터로 Fact-check"
        final_report:
          description: "모든 값에 TruthRecord/Source/신뢰도 명시, Guardian 통과 후 사용자 보고"

    opportunity_portfolio:
      owner: "explorer"
      steps:
        - "Observer의 Market Reality Report 입력"
        - "비효율성/공백 탐지"
        - "기회별 규모를 Calculator로 계산 (Truth Factory 호출)"
        - "Validator/Guardian 검증 후 검증된 포트폴리오 출력"

  universal_protocols:
    fact_check_gate:
      validator_approval_required: true
      applies_to:
        - "모든 최종 보고서 (Observer, Explorer)"
        - "사용자에게 노출되는 수치가 포함된 산출물"
    circuit_breaker:
      enabled: true
      owner: "guardian"
      levels:
        - "vector_fail → yaml_only"
        - "hybrid → yaml_only"
        - "open state after 3 failures"
```

이 정도 스켈레톤이면:

- v8 문서의 **Agent 역할 정의**와 **Tier 구조**
- Data Source Priority 재설계 문서의 **Tier 1~4 우선순위와 Protocol**
- 기존 Blueprint의 **Estimator 4-Stage, Fail-safe, RAG Layer 구조**

를 모두 포괄하면서도, “이제는 truth_factory가 SoT를 생산한다”는 새로운 철학을 표현할 수 있습니다.

------

## 사유 공개 (요약)

### 1. 가정

- v8 설계 문서와 Data Source Priority 재설계 문서가 **향후 기준선**이 된다.
- Estimator를 SoT에서 떼어내고, validator–calculator–estimator 3 Agent가 truth factory를 구성해야 한다는 사용자의 의도가 최우선이다.
- v7 Blueprint의 4-Stage Estimator 설계는 “버리는 것”이 아니라 “일반화된 Truth Engine 설계”로 재해석 가능하다.

### 2. 근거

- v8에서 Estimator가 Stage 3/4를 잃고 Pure Guesser로 단순화된 점, Calculator가 Fermi·Convergence를 맡고 있는 점
- Data Source Priority 문서에서 Tier 1~4를 강하게 정의하고, Fact-check Gate를 필수로 넣은 점
- Blueprint에서 Agent ID 불변, RAG 4-Layer, Fail-safe, SoT 철학이 이미 강하게 박혀 있는 점

### 3. 추론 경로

1. “Estimator = SoT”라는 v7의 설정과, v8에서의 Estimator 축소가 충돌하므로
    → “SoT = Agent가 아니라 Truth Factory Pipeline의 산출물”로 재정의.
2. Tier가 Agent Tier / Data Tier / Calculator 내부 Tier에 섞여 있는 상황을 분석
    → Agent Tier는 그대로, Data Tier는 `source_tier_*`, Calculator 내부는 `band_*`로 분리.
3. Quantifier→Calculator ID 변경은 v7의 “ID 불변” 원칙과 충돌
    → Canonical ID를 calculator로 바꾸되, migration 계층으로 정리 (설계안 C).
4. TruthRecord 저장 위치는 EST-* 확장 vs truth_registry 신설 vs 엑셀 의존을 비교
    → 단기에는 EST를 TruthRecord로 승격, 장기에는 truth_registry.yaml 도입.
5. 이 모든 결정을 담을 수 있는 umis.yaml 상위 스켈레톤을 Agent 중심 패턴으로 설계.

### 4. 대안

- SoT를 Calculator 단일 오너로 두는 설계 (안 B)
- truth_registry.yaml만을 SoT로 보고 EST-*는 deprecated시키는 급진적 설계
- Agent Tier 명칭까지 전부 바꾸고 “tier”라는 단어 자체를 전체에서 없애는 설계

이 대안들은 각각 단순함/급진성을 가졌지만,

- 기존 문서 자산과의 연결,
- 사용자의 의도(3 Agent 생산기지),
- 마이그레이션 리스크
   를 함께 고려했을 때 현재 제안이 균형점이라고 판단했습니다.

### 5. 불확실성/리스크

- 실제 `umis.yaml`의 전체 구조(현 버전 6,000+ 줄)를 보지 않은 상태에서 상위 스켈레톤을 설계했기 때문에,
   일부 세부 섹션과의 충돌 가능성 존재
- System RAG와 코드 레벨에서 quantifier→calculator alias를 구현할 때 예상치 못한 edge-case 가능성
- TruthRecord를 EST-*로 확장할 때, 기존 “Estimator 전용 결과”라는 인식과 충돌할 수 있는 문서적 리스크

### 6. 검증

- 다음 단계에서:
  - (a) 기존 umis.yaml 상단 500~1,000줄과 이 스켈레톤을 diff 형태로 맞춰 보고,
  - (b) 한 개 도메인(예: “한국 공연시장 분석”)을 v8 flow로 실제로 수행하면서,
    - TruthRecord(EST-*)가 잘 쌓이는지
    - Observer/Explorer/Calculator/Validator 호출 플로우가 자연스러운지
       를 점검하면 설계 타당성을 꽤 정확히 검증할 수 있습니다.

------

여기까지가 0번(개념·정책 확정) + 1번(umis.yaml 상위 스켈레톤 설계)의 실제 작업 결과입니다.
 이 위에서 이어서 2번 작업(구체 workflow 정의·세부 스키마화)로 내려가면, 이제는 비교적 “채우기” 작업이 될 겁니다.

##### 나의 말:

\- 아직 일반 사용자가 없는 런칭 전 소프트웨어이기 때문에, 하위 호환성은 아직 중요하지 않아. 같은 의미에서 기존 RAG prefix EST 또한 중요하지 않아. 쌓아놓은 데이터가 아직 없는 상황이야. 다만, 기존 py 스크립트 및 yaml config 파일들의 migration이 필요해. v7에서 quantifier가 연결된 기능들을 v8에서는 어디로 연결시킬지에 대한 mapping 기준이 필요해. - knowledge graph / pattern-level reasoning의 source data는 사용자가 직접 검수한 내용들을 yaml로 변경 후 주입하고 있어. 때문에 사전 검증작업이 필요하지 않아. 하지만 SoT 관점에서 온보딩 시킨다면 어떻게 포함시키는게 좋을지는 네가 정리해 주면 좋겠어. - 최상위 구조 패턴은 agent 중심 구조가 무조건 더 나아. workflow는 언제든 바뀔 수 있고, 심지어 같은 agent과 system을 활용해 다른 용도의 workflow를 구현해서 다른 system을 구축할 수도 있기 때문이야. - 위 내용들을 참고해서 skeleton을 다시 작성 해 볼래? 위 내용을 반영하는 것 외에도, 네가 작성한 내용을 리뷰 해 보면서 좀 더 나은 방식이 있는지 찾아보고 고도화 해 보자.

------

###### ChatGPT의 말:

Reasoned for 14m 19s

바로 v8 기준으로 다시 뼈대를 짜보겠습니다.
 정리하면:

- **최상위는 무조건 Agent 중심**
- **Quantifier 관련 v7 → v8 매핑 기준 제시**
- **KG / 패턴 YAML은 이미 검수된 SoT로 보고 온보딩 경로만 설계**
- **EST prefix는 “과거 호환” 고려 안 하고, v8 관점에서 제일 깔끔한 네이밍으로 재정의**

아래 스켈레톤은 기존 아키텍처 문서 흐름을 유지하면서, 구조를 v8스럽게 정리한 버전입니다. UMIS_ARCHITECTURE_BLUEPRINT

------

## 1. v8 리포지토리 최상위 스켈레톤 (Agent 중심)

```
umis/
├── agents/                      # ⭐ 최상위: Agent 중심 구조
│   ├── observer/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── observer_agent.py
│   ├── explorer/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── explorer_agent.py
│   ├── quantifier/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   ├── quantifier_agent.py
│   │   └── bindings/            # v7 → v8 매핑 포인트
│   │       ├── estimator_bindings.yaml
│   │       └── source_bindings.yaml
│   ├── validator/
│   ├── guardian/
│   └── estimator/
│       ├── __init__.py
│       ├── estimator_agent.py   # EstimatorRAG facade
│       ├── evidence_stage.py    # Stage 1
│       ├── prior_stage.py       # Stage 2
│       ├── fermi_stage.py       # Stage 3
│       ├── fusion_stage.py      # Stage 4
│       └── models.py
│
├── workflows/                   # Workflow는 “Agent 조합 레시피”로만 존재
│   ├── market_analysis.yaml
│   ├── opportunity_scan.yaml
│   └── custom/                  # 동일 Agent 조합으로 다른 System 가능
│       └── investor_pitch.yaml
│
├── rag/                         # RAG Runtime + Data Layer
│   ├── config/
│   │   ├── schema_registry.yaml
│   │   ├── projection_rules.yaml
│   │   ├── runtime.yaml
│   │   └── tool_registry.yaml
│   ├── canonical/               # CAN-* 관리
│   │   ├── builder.py
│   │   └── loader.py
│   ├── projected/               # PRJ-* 관리 (Agent View)
│   │   ├── projector.py
│   │   └── ttl_manager.py
│   ├── graph/                   # KG (Neo4j)
│   │   ├── schema_initializer.py
│   │   ├── loader.py
│   │   └── hybrid_search.py
│   ├── memory/                  # MEM-*, RAE-*, EST-* (메모리 계층)
│   │   ├── query_memory.py
│   │   ├── goal_memory.py
│   │   └── rae_memory.py
│   └── runtime/                 # Circuit breaker, routing
│       ├── layer_manager.py
│       ├── circuit_breaker.py
│       └── routing_policy.yaml
│
├── sot/                         # ⭐ Single Source of Truth 온보딩 영역
│   ├── patterns/                # 사람이 검수한 pattern-level YAML
│   │   ├── subscription.yaml
│   │   ├── platform.yaml
│   │   └── ...
│   ├── graph/                   # KG 노드/간선 정의 YAML
│   │   ├── nodes.yaml
│   │   └── edges.yaml
│   ├── domains/                 # 도메인별 SoT 패키지 (B2B_SaaS, 배민 등)
│   │   └── b2b_saas/
│   │       ├── entities.yaml
│   │       ├── metrics.yaml
│   │       └── estimation_hints.yaml
│   └── onboarding/              # 온보딩 스크립트/정책
│       ├── onboarding_policy.yaml
│       └── run_onboarding.py
│
├── core/                        # LLM abstraction + 공용 infra
│   ├── llm/
│   │   ├── interface.py         # LLMProvider, BaseLLM, TaskType
│   │   ├── cursor_provider.py
│   │   ├── external_provider.py
│   │   └── model_router.py
│   ├── ids/
│   │   ├── id_schema.yaml       # SRC-/EST-/ASM-/CAN-/...
│   │   └── id_generator.py
│   ├── schema/                  # pydantic / dataclass 정의
│   └── utils/
│       └── logging.py
│
├── migration/                   # v7 → v8 마이그레이션
│   ├── quantifier_v7_map.yaml   # v7 함수 → v8 바인딩 매핑 기준
│   ├── migrate_quantifier.py
│   ├── migrate_configs.py
│   └── README.md
│
└── scripts/
    ├── build_all_rag.py         # 02_build_index.py 후속 통합 버전
    ├── build_canonical_index.py
    ├── build_projected_index.py
    ├── build_knowledge_graph.py
    └── sync_sot_to_rag.py       # umis.yaml → RAG가 아니라 sot/* → RAG 동기화
```

핵심 포인트:

- **최상위 폴더 이름이 곧 개념 구분**: `agents/`, `workflows/`, `rag/`, `sot/`, `core/`, `migration/`.
- Workflow는 *어디까지나 레시피*이고, 실제 “똑똑함”은 전부 Agent와 SoT/RAG 쪽에 박혀있도록 정리했습니다.
- SoT는 `sot/` 폴더 하나로 모으고, onboarding 경로를 명시적으로 관리합니다.

------

## 2. Quantifier v7 → v8 매핑 기준

### 2.1. 먼저 “역할 분해 기준”을 고정

Quantifier 쪽 v7 코드를 **3가지 역할**로 나누는 게 좋습니다:

1. **순수 계산 로직**
   - 예: `LTV = ARPU / Churn`
   - 엑셀 수식, Python 계산 함수 등.
2. **값 추정 + RAG 호출 / LLM 호출 / EST prefix 참조**
   - 예: “ARPU 없으면 과거 케이스 기반으로 추정”
3. **입력/출력 바인딩**
   - 예: “ARPU는 시트 A의 셀 B3에 들어간다”, “이 셀은 EST_ARPU를 참조한다” 같은 wiring 로직.

v8에서의 기준:

- **① 순수 계산** → 그대로 `agents/quantifier/` 밑으로 이관 (또는 엑셀 수식 유지).
- **② 값 추정 / LLM 호출** → 100% Estimator로 이관 (quantifier에서 제거).
- **③ 바인딩** → `quantifier/bindings/*.yaml`로 모아서 선언적(Declarative)하게 관리.

### 2.2. v7 Quantifier 연결 지점 → v8 매핑 테이블

예상되는 v7 길:

- `quantifier`가 직접 **EST_* prefix**를 RAG에서 읽거나, LLM을 직접 호출했을 가능성.
- 셀 이름/네이밍이 `EST_ARPU`, `EST_CHURN` 이런 식으로 되어 있었을 가능성.

v8에서는 아래 기준으로 재맵핑하면 깔끔합니다:

| v7 패턴                                 | v8에서의 기준 연결 지점                          |
| --------------------------------------- | ------------------------------------------------ |
| Quantifier 내부에서 LLM 직접 호출       | `EstimatorAgent.estimate()` 호출로 100% 이동     |
| `EST_*` prefix 값을 RAG에서 끌어옴      | `source: estimator` + `key` 기반 바인딩          |
| 정해진 값이 없으면 “가정”으로 박아 넣음 | `ASM-*` assumption으로 분리 후 SoT / YAML로 관리 |
| 특정 보고서/도메인에 하드코딩된 값      | `sot/domains/{domain}/metrics.yaml`로 이동       |

### 2.3. v8 Quantifier 바인딩 YAML 예시

```
# agents/quantifier/bindings/estimator_bindings.yaml

domain: "b2b_saas"

inputs:
  arpu:
    source: estimator        # or literal/src/assumption
    estimator_key: "b2b_saas.arpu"
    required: true
    fallback:
      type: assumption
      id: "ASM_001"          # sot/domains/b2b_saas/metrics.yaml에 정의

  churn_rate:
    source: estimator
    estimator_key: "b2b_saas.churn_rate"
    required: true
    fallback:
      type: estimator
      mode: "aggressive"     # Stage 3까지 적극 활용

  discount_rate:
    source: assumption
    id: "ASM_002"

outputs:
  ltv:
    formula: "arpu / churn_rate"
    sheet: "unit_economics"
    cell: "B10"
```

이렇게 해두면:

- v7에서 `EST_ARPU`를 직접 읽던 코드는
  - v8에서 “`arpu`라는 논리 키 → Estimator 호출”로 치환됩니다.
- Quantifier는 **“숫자 신”이 아니라 “계산기”** 역할만 수행합니다.

### 2.4. Quantifier Python 코드 레벨 스켈레톤

```
# agents/quantifier/quantifier_agent.py

class QuantifierAgent:
    def __init__(self, estimator_client, bindings_config):
        self.estimator = estimator_client
        self.bindings = bindings_config

    def _resolve_input(self, name, spec):
        if spec["source"] == "estimator":
            return self.estimator.estimate(
                key=spec["estimator_key"],
                mode=spec.get("mode", "standard"),
            ).value
        elif spec["source"] == "assumption":
            return self._load_assumption(spec["id"])
        elif spec["source"] == "literal":
            return spec["value"]
        else:
            raise ValueError(f"Unknown source: {spec['source']}")

    def compute_unit_economics(self, domain: str):
        cfg = self.bindings.for_domain(domain)
        ctx = {}
        for name, spec in cfg.inputs.items():
            ctx[name] = self._resolve_input(name, spec)

        ltv = ctx["arpu"] / ctx["churn_rate"]
        # 엑셀/리포트에 쓰는 부분은 별도 writer로 분리
        return {"ltv": ltv}
```

**마이그레이션 가이드라인**:

1. v7 Quantifier 함수마다
   - “입력 파라미터” / “LLM, RAG 호출” / “수식” 세 칸으로 나눠 봅니다.
2. LLM/RAG 호출 부분을 전부 Estimator client 호출로 옮기고,
3. 수식 부분만 순수 함수로 살려두고,
4. 입출력 wiring은 YAML 바인딩으로 뺍니다.

------

## 3. EST Prefix / ID 네임스페이스 v8 정리

이제 과거 데이터 호환성을 안 봐도 되니, 깔끔하게 다시 정의해 두는 편이 낫습니다.
 v8 기준으로 ID prefix를 이렇게 고정하는 것을 제안드립니다: UMIS_ARCHITECTURE_BLUEPRINT

- **SRC-**: 원천 데이터 (Validator)
- **EST-**: Estimator 결과 (메모리/SoT에서만 사용, RAG 청크 ID로는 사용 X)
- **ASM-**: Assumption (Quantifier 입력 가정)
- **CAN-**: Canonical 청크 (RAG Layer 1)
- **PRJ-**: Projected 청크 (Agent View, RAG Layer 2)
- **GND-/GED-**: KG 노드/간선
- **MEM-**, **RAE-**: 메모리 / 평가

즉 v8에서는:

- **RAG Vector/Graph 쪽에는 CAN-/PRJ-/GND-/GED-만 사용**
- **EST-*는 “Estimator가 낳은 구조화된 결과 세트”**에만 사용

이렇게 하면 이후에:

- “같은 질문 → 같은 EST-ID”라는 캐시/학습 구조를 만들기도 훨씬 쉽습니다.

예:

```
# sot/domains/b2b_saas/metrics.yaml
estimation_keys:
  b2b_saas.arpu:
    est_id: "EST_b2b_saas_arpu_001"
    last_updated: "2025-11-29"
    src_ids: ["SRC_20251129_001", "SRC_20251129_002"]
```

------

## 4. SoT 관점에서 KG / Pattern YAML 온보딩

이미 사람이 검수한 YAML이 들어오고 있으니, 검증 파이프라인 대신 **온보딩 파이프라인**에만 집중하면 됩니다.

### 4.1. SoT YAML 스키마 스켈레톤

#### 4.1.1. 패턴 YAML (`sot/patterns/*.yaml`)

```
id: "pattern.subscription_model"
version: 1
description: "구독 모델의 일반 구조"

anchors:
  - path: "revenue_model.subscription"
  - path: "pricing.recurring"
agents:
  - explorer
  - quantifier

fields:
  core_metrics:
    - "arpu"
    - "churn_rate"
    - "ltv"
  canonical_examples:
    - "Netflix"
    - "Spotify"
    - "Adobe"
```

이 내용은 Onboarding 시:

- Canonical Index의 **메타데이터**로 들어가고,
- Projected Index에서 **어떤 agent_view에 어떤 필드를 projection할지**를 결정하는 기준이 됩니다.

#### 4.1.2. Graph YAML (`sot/graph/nodes.yaml`, `edges.yaml`)

```
# nodes.yaml
nodes:
  - id: "GND-platform-001"
    type: "pattern"
    pattern_id: "pattern.platform_model"
  - id: "GND-subscription-001"
    type: "pattern"
    pattern_id: "pattern.subscription_model"
# edges.yaml
edges:
  - id: "GED-plat-sub-001"
    from: "GND-platform-001"
    to:   "GND-subscription-001"
    relationship_type: "COMBINES_WITH"
    confidence:
      similarity: 0.92
      coverage: 0.10
      validation: true
      overall: 0.85
    evidence_ids:
      - "CAN-amazon-001"
      - "PRJ-spotify-exp-002"
```

여기서 중요한 점:

- 이 YAML 자체가 이미 “사람이 검수한 SoT”이므로,
- Onboarding은 이걸 **Neo4j / Vector Index에 옮기는 작업**일 뿐, “검증”이 아니라 “동기화”에 가깝습니다.

### 4.2. SoT 온보딩 정책 (`sot/onboarding/onboarding_policy.yaml`)

```
sources:
  - name: "patterns"
    path: "sot/patterns/*.yaml"
    target: "rag.canonical"
    mode: "replace"        # v8에서는 하위 호환 필요 없으니 덮어쓰기 중심
  - name: "graph_nodes"
    path: "sot/graph/nodes.yaml"
    target: "rag.graph.nodes"
    mode: "merge"
  - name: "graph_edges"
    path: "sot/graph/edges.yaml"
    target: "rag.graph.edges"
    mode: "merge"

estimation_hints:
  path: "sot/domains/**/estimation_hints.yaml"
  target: "agents.estimator"
  mode: "merge"
```

이렇게 해두면:

- 새로운 도메인이나 패턴을 추가할 때, **SoT(YAML)를 고치고 `run_onboarding.py`만 돌리면 시스템 전체에 반영**됩니다.
- “SoT → RAG / Agent 설정”이라는 단방향 흐름이 고정되기 때문에, 나중에 Schema 바꿀 때도 훨씬 수월합니다.

------

## 5. Agent 중심 구조에서 Workflow 다루는 방식

최상위 구조를 Agent 중심으로 가져가면, Workflow는 사실상 “조합 스크립트”가 됩니다.

### 5.1. Workflow YAML 스켈레톤

```
# workflows/market_analysis.yaml

id: "workflow.market_analysis.v1"
description: "시장 구조 분석 + 기회 발굴 + 사이징"

entrypoint: "observer"   # 첫 호출 Agent

agents:
  - id: "observer"
    strategy: "single"
  - id: "explorer"
    strategy: "pattern_search"
  - id: "quantifier"
    strategy: "excel_pipeline"
  - id: "validator"
    strategy: "dart_first"
  - id: "guardian"
    strategy: "meta_monitor"
  - id: "estimator"
    strategy: "4_stage_fusion"

routing:
  - from: "observer"
    to: "explorer"
    condition: "observer.found_opportunities == true"

  - from: "explorer"
    to: "estimator"
    condition: "explorer.needs_market_size == true"

  - from: "estimator"
    to: "quantifier"
    condition: "estimator.certainty in ['high','medium']"

  - from: "quantifier"
    to: "validator"
    condition: "quantifier.outputs_ready == true"
```

이 구조의 장점:

- **Agent 구현은 그대로, Routing만 갈아끼워서 다른 Workflow / System을 만드는 게 쉬워집니다.**
- `workflows/custom/*.yaml`만 새로 쓰면, **동일 Agent + 동일 SoT/RAG**를 이용해 완전히 다른 비즈니스 플로우를 만들 수 있습니다.

------

## 6. v7 → v8 마이그레이션 실무용 체크리스트

구체적인 “작업 순서” 기준도 하나 두겠습니다.

1. **Quantifier 코드 스캔**
   - LLM 호출 / RAG 호출 / EST prefix 직접 참조 부분을 전부 리스트업
   - 순수 수식/계산과 분리
2. **`migration/quantifier_v7_map.yaml` 작성**
   - v7 함수명/모듈명 → v8의
     - `bindings.estimator_key`
     - `assumption_id`
     - `domain`
        맵핑 테이블을 정의
3. **Assumption / Domain SoT로 이관**
   - 하드코딩된 할인율, 마진율 등은
      `sot/domains/{domain}/metrics.yaml` / `assumptions.yaml`로 옮김
4. **Estimator 연동**
   - Quantifier 내부 LLM 호출 → `EstimatorAgent.estimate(key=...)`로 치환
   - Estimator는 4-Stage 구조 그대로 사용하되, v8에서는 `estimation_key` 중심으로 호출
5. **엑셀 템플릿 업데이트**
   - `EST_ARPU` 같은 셀 네이밍 대신,
      “논리 키” 기준으로 바인딩하는 레이어를 하나 두거나,
   - 스크립트에서 셀에 값 주입할 때
      “`key → 값` 매핑”만 알고 있으면 되도록 리팩토링

------

## 7. 사유 공개 (가정 / 근거 / 추론 / 대안 / 리스크 / 검증)

**가정**

- v7에서 Quantifier가 값 추정 + 계산 + wiring을 모두 가지고 있었고, EST prefix 기반 참조가 존재했다고 가정했습니다.
- 현재는 히스토리 데이터(EST-* 결과 저장분)가 사실상 없어서, 호환성보다 구조 정리가 중요하다고 가정했습니다.
- KG / Pattern YAML은 신뢰도 높은 SoT이며, 추가적인 자동 검증은 필요하지 않다고 전제했습니다.

**근거**

- 기존 설계 문서에 나와 있는 6-Agent 구조, Estimator 4-Stage Fusion, 4-Layer RAG 구조를 그대로 유지하는 방향이므로, 큰 철학은 바뀌지 않습니다. UMIS_ARCHITECTURE_BLUEPRINT
- Agent ID 불변, SoT 단일화, Estimator를 단일 추정 엔진으로 두는 원칙도 그대로 살렸습니다.

**추론 경로**

1. “Agent 중심 최상위 구조” 요구 → `agents/`를 맨 위에 두고, Workflow는 별도 `workflows/`로 분리.
2. Quantifier 매핑 기준은 “역할 리스트업 → 추정 부분만 Estimator로 이동 → 나머지는 계산/바인딩으로 분리”라는 3단계로 정리.
3. EST prefix는 과거 데이터가 없으므로, “RAG ID”에서 떼어내고 “Estimator 결과 SoT ID”로만 쓰는 게 장기적으로 추적성과 학습 구조에 유리하다고 판단.
4. 사람이 검수한 YAML은 SoT로 보고, `sot/` 폴더로 모은 다음 Onboarding policy만 정의하는 쪽이 검증 파이프라인보다 효율적이라고 판단.

**대안**

- 최상위 구조를 `domains/` 중심으로 잡고, Agent를 도메인 안으로 넣는 방식도 가능하지만,
  - 그 경우 domain × agent 조합마다 중복 코드/설정이 발생하고,
  - “같은 Agent로 여러 시스템 만들기”가 어려워집니다.
- Quantifier 바인딩을 코드(파이썬)로만 관리하고 YAML을 쓰지 않는 방식도 가능하지만,
  - 코드/모델 동기화 비용이 커지고,
  - 비개발자가 수정하기 어렵습니다.

**불확실성 / 리스크**

- v7 Quantifier 코드에서 실제로 어떤 패턴으로 LLM/RAG를 호출하고 있는지에 따라,
   제안한 “3단 분리(계산/추정/바인딩)” 구조가 일부 함수에서는 더 복잡해질 수 있습니다.
- Excel 템플릿 내부 이름/구조가 지금 제안한 바인딩 구조와 상이할 수 있어서,
   1회성으로 약간의 매뉴얼 수정이 필요할 수 있습니다.

**검증**

- 첫 단계에서는 **단일 도메인 (예: B2B SaaS)** 에 대해서만:
  - v7 Quantifier를 v8 구조로 옮기고,
  - 동일 입력에 대해 **결과 수치가 동일하게 나오는지** 비교하는 방식으로 검증하는 게 좋습니다.
- 이때 Estimator는 초기에는 “Stage 1 + Stage 2” 정도만 사용해도 되며,
   구조 검증이 끝난 뒤에 Stage 3/4를 켜서 고급 추정 기능을 붙이는 방식이 안정적입니다.

------

이 스켈레톤을 기준으로,

- 하나의 도메인(예: B2B SaaS)과
- 하나의 대표 Workflow(예: market_analysis)를 골라

실제 v7 코드를 v8 구조에 얹어보면, “어디가 아직 애매한지”가 바로 드러날 겁니다. 그 지점을 다시 역으로 반영해 v8 스켈레톤을 조정하면, 거의 한 번에 정착할 수 있습니다.

##### 나의 말:

응 한번 얹어서 확인하고 조정 해 보자.

##### 나의 말:

스켈레톤의 내용을 채워나가보자.

##### 나의 말:

v7 코드를 v8 구조에 얹어서, “어디가 아직 애매한지” 확인 해 보자. 그 지점을 다시 역으로 반영해 v8 스켈레톤을 조정해보자.

###### ChatGPT의 말:

###### ChatGPT의 말:

좋아요, 이제 진짜로 “v7 구현을 v8 설계 위에 얹어서” 어디가 부딪히는지 하나씩 까보겠습니다.
 그 다음에 그 애매한 부분을 v8 스켈레톤 구조에 역으로 반영하는 쪽으로 정리할게요.

------

## 1. v7 → v8 매핑: 어디까지는 깔끔한지

### 1-1. 공통으로 잘 맞는 부분

- **Business Layer (Observer / Explorer / Validator / Guardian)**
  - Observer(Albert), Explorer(Steve), Validator(Rachel), Guardian(Stewart) 역할 자체는 v7–v8 사이에 철학적으로 크게 안 흔들립니다.
  - v8에서는 Observer가 **구조+규모 통합 분석 + 오케스트레이션**을 책임지고, Calculator/Validator/Estimator를 orchestration 대상으로 명시했죠.UMIS_v8_AGENT_ROLES_AND_WORKFLO…
  - Validator는 “Active Data Hunter”로 DART/KOSIS/Web/Creative 검색을 도는 워크플로도 이미 잘 정의돼 있고요.
- **Estimator Stage 1–2 재사용**
  - v7에서 Estimator의 Stage 1(Evidence & Guardrails) + Stage 2(Generative Prior)는 이미 별도 파일로 잘 분리돼 있고, 역할도 깔끔합니다.
  - v8에서 Estimator를 **“Pure Guesser (Generative Prior Only)”**로 단순화하는 방향은, 이 Stage 2를 그대로 가져다 쓰는 구조니까 코드 재사용 관점에서는 꽤 자연스럽습니다.
- **Quantifier의 정량화 로직 → Calculator**
  - v7 Quantifier가 담당하던 31개 계산 방법론(LTV, CAC, SAM 4-method convergence 등)은 `data/raw/calculation_methodologies.yaml`에 정의돼 있고, 역할 자체가 “공식 기반 계산 + 수렴”이라서 v8의 Calculator 역할과 자연스럽게 이어집니다.
  - v8 Calculator 정의도 “Formula Designer & Convergence Engine + fermi_decomposition + convergence_analysis”라 이쪽은 거의 1:1로 매핑 가능합니다.

여기까지는 큰 충돌 없이 “이식 가능”한 영역입니다.

------

## 2. 실제로 애매한 지점들

이제 문제 되는 모서리들을 짚어볼게요.

### 2-1. Estimator 4-Stage → Evidence/Calculator/Estimator 분해가 덜 정리된 부분

**v7 상태**

- Estimator = 4-Stage Fusion (Evidence → Prior → Fermi → Fusion).
  - Stage 1: Literal / Direct RAG / Validator Search / Guardrail Engine
  - Stage 2: Generative Prior (prior_estimator)
  - Stage 3: Fermi 분해 (재귀 금지, Budget 기반)
  - Stage 4: Evidence + Prior + Fermi 센서 퓨전(가중 평균, hard bound clipping)
- Single source policy: “모든 값/데이터 추정은 Estimator만 수행” + EstimationResult가 공통 인터페이스.

**v8 설계**

- Stage 3(Fermi)와 Stage 4(Fusion)를 Estimator에서 제거하고, Fermi는 Calculator로 넘기고, Fusion은 “없애기”로 되어 있습니다.UMIS_v8_AGENT_ROLES_AND_WORKFLO…
- 대신 Calculator 쪽에서
  - fermi_decomposition (max_depth=2 재귀),
  - convergence_analysis(CV, outlier 제거, 가중 평균)
     를 맡고 있고, 여러 공식의 결과를 수렴시키는 역할만 정의돼 있습니다.

**여기서 애매한 점**

1. **Stage 4의 “센서 퓨전”이 어디로 갔는지 명확하지 않음**
   - v7 Stage 4는 “Evidence(확정값/guardrail) + Prior(LLM 추정) + Fermi(구조적 분해 결과)”를 하나의 EstimationResult로 합성하는 레이어였는데, v8에서는
     - Calculator는 “여러 공식”의 결과를 합성하는 역할,
     - Observer는 “여러 공식의 결과”를 비즈니스 판단으로 가중평균하는 역할,
        로만 등장합니다.
   - 즉, “Evidence vs Prior vs Fermi” 세 계층을 하나로 모으는 **중앙 합성기**가 사라져 있고, SoT 정의가 흐려집니다.
2. **Evidence Collector vs Validator vs Guardrail Engine의 경계**
   - v7에서는 Stage 1 내부에서 `validator_search + guardrail_engine`이 Estimator 안에 붙어 있습니다.
   - v8에서는 Evidence Collector(Infra)와 Validator(Agent)가 분리돼 있지만,
     - Guardrail 생성 로직이 Evidence Collector 것인지,
     - Validator Search의 “확정 데이터”는 어디까지 Evidence로 캐싱하는지,
        가 스펙 상 애매합니다.
3. **v7의 “재귀 금지” vs v8 Calculator의 제한적 재귀 허용**
   - v7: Estimator 설계 철학이 “재귀 완전 제거, Budget 기반 탐색”이 핵심.
   - v8: Calculator.fermi에서 max_depth=2 재귀를 허용하고, 여기서 다시 Tier 1-4 변수를 채우는 구조로 돌아갑니다.
   - “재귀를 어디까지 허용할지”에 대한 global principle이 지금은 문서간 엇갈립니다.

→ 요약하면, **Estimator 4-Stage의 Stage 3/4를 어떻게 EvidenceCollector/Calculator/Observer로 재구성할지**가 아직 정리 안 되어 있습니다.

------

### 2-2. Quantifier → Calculator/Observer로 쪼개진 구조

**v7**

- Quantifier(Bill)는 “SAM 4-method + ±30% 수렴 + 정량화 담당”이라는 굉장히 명확한 Agent였습니다.
- 폴더 구조도 `02_analysis/quantifier/`로 완전히 분리.UMIS_ARCHITECTURE_BLUEPRINT

**v8**

- `umis_v8_agents` 안에서는 tier_1_business_analysis에 **observer, explorer만** 있고, quantifier ID는 사라집니다.
- quantifier의 역할은
  - Observer.market_sizing capability(“TAM/SAM/SOM 계산 + 수렴 판단”),
  - Calculator(Formula Designer & Convergence Engine),
     로 분산되어 있습니다.
- 동시에 Calculator는 **type: Tool (Tier 2)**로 정의되어 있어서 “Agent”라기보다는 라이브러리 느낌.UMIS_v8_AGENT_ROLES_AND_WORKFLO…

**여기서 애매한 점**

1. **사용자/코드 레벨 mental model**
   - v7에서는 “Bill에게 물어본다”는 mental model이 명확했는데, v8 문서만 따르면
     - Observer가 Calculator를 직접 부르고,
     - Explorer도 Calculator를 부르고,
     - Calculator는 Tool로만 취급되고,
     - “Bill”이라는 역할/페르소나가 사라집니다.
   - 그런데 사용자 요청에서는 “Quantifier의 ID를 calculator로 변경하면서 역할을 변경”이라고 했으니, **ID는 그대로 Agent로 유지하되 내부적으로 Tool을 쓰는 구조**가 더 자연스럽습니다.
2. **v7 코드 마이그레이션 기준**
   - v7의 `umis_rag/agents/quantifier.py` 혹은 그에 준하는 코드가 있다면, 이걸
     - “Calculator Agent” 클래스로 승격시킬지,
     - 그냥 Tool로만 둔 채 Observer에 흡수할지,
        에 대한 기준이 아직 없습니다.
   - 사용자가 말한 것처럼 “최상위 패턴은 agent 중심 구조”를 유지하려면, **Calculator를 Agent로 올리고(=새 Bill), 내부에서 calculator_engine Tool을 쓰는 이중 구조**가 필요해 보입니다.

------

### 2-3. Single Source of Truth: Estimator 중심 → Validator-Calculator-Estimator 생산라인

**v7**

- 명시적인 single_source_policy: “모든 값/데이터 추정은 Estimator만 수행” + 다른 Agent는 계산/검증만 하고 추정은 금지.
- EstimationResult(EST-ID)가 사실상 모든 수치 추론의 단일 진실 원천이었고, Quantifier/Observer/Explorer는 EST-ID 또는 SRC-ID만 참조.

**v8 + Data Source Priority Redesign**

- Data Source Priority 문서는
  - tier_1_official_data (Validator) →
  - tier_2_verified_commercial (Validator) →
  - tier_3_estimator_fallback →
  - tier_4_llm_baseline
     순서를 정의하면서 “Estimator는 Validator의 fallback”으로 재정의하고 있습니다.
- 동시에, 사용자는 “Validator - Calculator - Estimator 3개 Agent가 Business layer에서 쓸 SSoT를 만들어내는 생산기지”라고 방향을 잡았죠.

**여기서 애매한 점**

1. **새 SoT 엔티티의 스펙이 없다**
   - v7에서는 SoT가 `EstimationResult`로 명시돼 있고, ID 네임스페이스(EST-*)와 source 필드(Literal/Direct_RAG/Validator/Prior/Fermi/Fusion)가 완성돼 있습니다.
   - v8에서는
     - Validator가 반환하는 ValidatedData,
     - Calculator가 반환하는 CalculationResult,
     - Estimator가 반환하는 EstimationResult,
        세 개가 따로 존재할 뿐,
     - “Business Layer가 최종적으로 참조하는 단일 ValueRecord/ValueID” 같은 개념이 아직 없습니다.
2. **ID 네임스페이스 재설계가 비어 있음**
   - v7: SRC_*, EST_* 로 깔끔하게 갈렸는데,
   - v8: Validator-Calculator-Estimator 생산라인에서 나온 값들을 어떤 ID 네임스페이스로 묶을지 (VAL-*, NUM-* 등), origin과 reliability를 어떻게 encode할지 설계가 없습니다.
3. **Observer/Explorer가 무엇을 SoT로 본다고 가정하는지 명시되지 않음**
   - Observer v8 인터페이스는 `MarketRealityReport`만 정의돼 있고, 내부에서 어떤 ID를 참조하는지는 아직 서술이 없습니다.
   - Explorer도 “Calculator로 기회 크기 계산”까지만 있고, SoT로서 어떤 등급의 값을 허용하는지 기준이 없습니다.

------

### 2-4. Tier 용어의 이중 사용 (레이어 vs 변수 출처)

- v8 문서에는 두 종류의 “tier”가 공존합니다.
  1. `tier_1_business_analysis / tier_2_evidence_generation / tier_3_supervision` – Agent 레이어 구분.UMIS_v8_AGENT_ROLES_AND_WORKFLO…
  2. Calculator cascade에서 `tier_1_evidence / tier_2_validator / tier_3_calculator_fermi / tier_4_estimator` – 변수의 출처 레벨.
- 사용자가 “Calculator pipeline은 tier 말고 다른 단어를 쓰는 게 좋겠다”고 한 이유가 여기 있습니다.
- 현재 상태는:
  - “Tier 2”가 한 곳에선 Evidence Generation 레이어,
  - 다른 곳에선 “Validator에서 온 변수 출처”라는 뜻으로 쓰이기 때문에, 문서만 보고는 헷갈릴 수밖에 없습니다.

------

### 2-5. Knowledge Graph / 패턴 YAML의 위치

- v7: Canonical Index(CAN-*), Projected Index(PRJ-*), Knowledge Graph(Neo4j)가 RAG Layer에서 명확히 정의돼 있고, Explorer/Observer가 패턴 검색과 케이스 검색에서 이걸 적극 활용합니다.
- 사용자는 “KG/pattern YAML은 이미 사람이 검수한 데이터라 사전 검증 필요 없음”이라고 했습니다.

**애매한 포인트**

1. **Data Source Priority 안에서 이들이 어디에 속하는지 안 박혀 있음**
   - official_data? commercial_data? internal_curated_data?
   - 현재 Tier 정의에는 이 YAML/Graph가 명시되지 않습니다.DATA_SOURCE_PRIORITY_REDESIGN
2. **Evidence Collector vs Validator vs Explorer 사이의 역할**
   - 패턴/그래프 기반의 정량값(예: 어떤 패턴에서 가져온 평균 churn, ARPU)은
     - Evidence Collector가 바로 “확정 값”처럼 써도 되는지,
     - 아니면 Validator를 거쳐야 하는지,
     - 아니면 Estimator Stage1의 Direct RAG처럼 “learned rule” 취급을 할지,
        명시가 없습니다.

이게 그대로 코드/폴더 구조에도 영향을 줍니다. (예: `data/raw/umis_business_model_patterns.yaml`에서 나온 값을 SRC_로 볼지, 별도 CUR_*로 볼지 등)

------

## 3. 이 애매함을 반영해서 v8 스켈레톤을 어떻게 조정할지

이제 위에서 나온 애매한 부분들을 기준으로, v8용 `umis.yaml` 스켈레톤을 어떻게 바꿔야 할지 방향성을 제안해볼게요.

### 3-1. 6 Agent 셋 재정의: Quantifier → Calculator (Agent) + 내부 Tool

**제안**

- 상위 “에이전트 집합”은 v7과 동일하게 유지하되, ID만 교체:

  - `Observer, Explorer, Calculator, Validator, Guardian, Estimator`

- v8 문서의 `calculator_v8`는

  - `CalculatorAgent`의 내부 구현으로 보고,

  - yaml 상에서는 `id: Calculator`를 Agent로 명시:

    ```
    - id: Calculator
      classification: "Support Agent (Business-side)"
      role: "Market Quantification + Formula Orchestration"
      internal_tools:
        - "calculator_engine"   # stateless, pure function
        - "fermi_decomposer"
      provides_to: ["Observer", "Explorer"]
      depends_on: ["Validator", "Estimator", "EvidenceCollector"]
    ```

- 즉,

  - **사용자/워크플로우 레벨**: “Bill(=Calculator Agent)에게 SAM 계산을 맡긴다”
  - **구현 레벨**: Bill은 내부에서 `calculator_engine.calculate(...)`를 호출하는 thin wrapper

이렇게 하면

- v7 Quantifier 코드/폴더(`02_analysis/quantifier/` 등)를
  - `CalculatorAgent` 밑으로 그대로 옮길 수 있고,
- “최상위 구조는 agent 중심”이라는 사용자의 요구를 유지하면서,
- v8 설계 문서의 Calculator Tool 철학도 살릴 수 있습니다.

------

### 3-2. Value Factory / SoT 파이프라인을 명시적으로 추가

**새 섹션 제안 (스켈레톤)**

```
value_factory:
  description: "Validator → Calculator → Estimator 3-Agent 생산라인이 만들어내는 단일 ValueRecord 레이어"

  value_record:
    id_prefix: "VAL-"          # 새 SoT ID
    fields:
      - value: float
      - unit: string
      - origin: ["validator", "calculator", "estimator"]
      - source_ids: [SRC_*, CUR_*, EST_*]
      - reliability: ["A", "B", "C", "D"]
      - method: ["official", "formula_exact", "formula_convergence", "prior_guess"]
      - metadata: {domain, region, timestamp, author_agent}

  pipeline:
    step_1_validator:
      agent: "Validator"
      input: "data_request(query, domain, region)"
      output: "VAL-* with origin=validator, source_ids=[SRC_*]"
      when: "Tier 1-2 official/commercial data exists"

    step_2_calculator:
      agent: "Calculator"
      input: "target metric + needed variables"
      output: "VAL-* with origin=calculator, source_ids=[SRC_*, CUR_*, EST_*]"
      when: "직접 데이터 부족, 공식 기반 조합으로 계산 가능"

    step_3_estimator:
      agent: "Estimator"
      input: "question + guardrails + context"
      output: "VAL-* with origin=estimator, source_ids=[EST_*]"
      when: "Validator/Calculator 둘 다 부족할 때 fallback"

  business_layer_usage:
    rule: "Observer/Explorer는 항상 VAL-*만 직접 참조"
```

이렇게 하면:

- v7의 `EstimationResult(EST-ID)`는
  - value_factory 안에서 **origin=estimator**인 `ValueRecord`의 내부 evidence로 들어가고,
- SoT의 외형은 항상 동일(`VAL-*`), 내부 origin만 다르게 가져가는 구조가 됩니다.

기존 `single_source_policy`는 이렇게 수정하면 됩니다:

```
single_source_policy_v8:
  principle: "Business Layer는 모든 수치에 대해 VAL-*만 직접 사용한다."
  production_line:
    - "Validator → 공식 데이터 기반 VAL-* 생산 (우선)"
    - "Calculator → 공식/추정 조합 계산 VAL-* 생산 (차선)"
    - "Estimator → Prior 기반 VAL-* 생산 (최후)"
```

------

### 3-3. Estimator/Calculator 역할 재정의 & Stage 분리

스켈레톤에서 Estimator/Calculator 부분을 다음처럼 정리하는 걸 추천합니다.

1. **Estimator**

   ```
   - id: Estimator
     role: "Generative Prior Specialist (Pure Guess)"
     stage_responsibility:
       stage_1_evidence: "EvidenceCollector 결과를 guardrail로만 사용"
       stage_2_prior: "LLM 내적 확신 기반 값 추정 (유일한 Stage)"
       stage_3_fermi: "❌ responsibility 없음 (Calculator로 이동)"
       stage_4_fusion: "❌ responsibility 없음 (Value Factory / Calculator / Observer로 분산)"
     when_to_call:
       - "Validator/Calculator가 충분한 품질의 VAL-*를 만들지 못했을 때"
   ```

2. **Calculator (Agent + Engine)**

   ```
   - id: Calculator
     role: "Formula Orchestrator & Fermi Layer"
     responsibilities:
       - "공식 선택/생성 (여러 method)"
       - "Fermi-style 분해 (max_depth=2, 단 Estimator는 호출만 하고 재귀는 Calculator 내부에서 통제)"
       - "각 공식 결과의 수렴 분석 (CV, outlier 제거)"
       - "origin=calculator 인 VAL-*를 Value Factory에 등록"
     recursion_policy:
       global_rule: "재귀는 Calculator 내부에서만 허용, Estimator는 재귀 금지"
   ```

   여기서 v7의 “재귀 금지” 원칙은

   - “Estimator가 스스로 자신을 다시 부르지 않는다”에 집중시키고,
   - Calculator 내부에서는 엄격한 max_depth=2 + 예산 기반 탐색으로 제한된 재귀를 허용하는 형태로 재해석할 수 있습니다.

------

### 3-4. Tier 용어 정리: 레이어 vs 변수 출처

스켈레톤에서 용어를 아예 갈라놓는 게 좋습니다.

- **레이어 구분**: `layer_1_business_agents / layer_2_value_factory / layer_3_supervision`처럼 “layer”라는 단어만 사용.
- **변수 출처 레벨**: Calculator/Value Factory 쪽에서는 `origin_level` 또는 `source_level` 같은 새 이름을 사용.

예시:

```
value_origin_levels:
  level_1_official:
    previous_name: "tier_1_official_data"
    produced_by: "Validator"
  level_2_curated_internal:
    sources: ["KG Patterns", "Business Model YAML"]
    produced_by: "EvidenceCollector"
  level_3_calculated:
    produced_by: "Calculator"
  level_4_prior_guess:
    produced_by: "Estimator"
```

Calculator 예시에서 등장하는 `Tier1-4` 용어는 스켈레톤에선 위 `origin_level` 네이밍으로 바꾸는 걸 기본으로 잡으면 됩니다.

------

### 3-5. Knowledge Graph / Pattern YAML의 온보딩 위치

사용자 말처럼 이 데이터는 이미 사람이 검수한 것이고, YAML로 고정돼 있으니, SoT 관점에서 **공식 통계와 거의 동급의 “curated internal” source**로 보면 됩니다.

스켈레톤에선 이렇게 박는 걸 추천합니다:

```
data_sources:
  official_data:
    owner: "Validator"
    examples: ["DART", "KOSIS", "OECD", "World Bank"]

  curated_internal_patterns:
    owner: "EvidenceCollector"
    files:
      - "data/raw/umis_business_model_patterns.yaml"
      - "data/raw/umis_disruption_patterns.yaml"
    usage:
      - "Explorer/Observer의 구조적/패턴적 인사이트"
      - "일부 평균값(예: churn 범위, ARPU range)은 level_2_curated_internal로 VAL-* 생산에 사용 가능"
    pre_validation: "Manual (user-reviewed, 추가 검증 불필요)"
```

그리고 Data Source Priority 문서에 이걸 한 줄로 추가:

```
data_source_priority:
  level_1_official_data: ...
  level_1b_curated_internal_patterns:
    priority: 1.5
    agent: EvidenceCollector
    reliability: HIGH
    protocol: "공식 통계가 없고, 패턴 YAML에 값이 있을 때 사용"
```

이렇게 하면:

- 패턴 YAML/Graph는 **Validator를 안 거쳐도 된다**는 사용자의 요구를 만족하면서,
- SoT 파이프라인에서도 명확한 위치를 갖게 됩니다.

------

### 3-6. v7 코드 마이그레이션 관점에서의 “매핑 기준”

스켈레톤에 직접 넣을 내용은 아니지만, v7 코드를 v8 구조에 올릴 때 기준을 정리해보면:

1. **Quantifier 관련 코드/폴더**

   - `umis_rag/agents/quantifier.py` → `umis_v8/agents/calculator_agent.py`
   - `02_analysis/quantifier/**` → `02_analysis/calculator/**` (또는 symlink/alias)
   - YAML `id: Quantifier` → `id: Calculator`로 변경하되, 역할 설명은 “Market Quantifier + Calculator Agent”로 업데이트.

2. **Estimator 관련 코드**

   - `EstimatorRAG`를
     - 내부적으로 `EvidenceCore(Stage1) + PriorCore(Stage2)`로 쪼개고,
     - 기존 Stage3/4 부분은 `legacy_estimator` 또는 `legacy_fusion`으로 마킹해둔 뒤,
     - CalculatorAgent가 Fermi/Convergence 역할을 새로 구현하면서 점진적으로 교체.
   - v8에서는 Estimator API는 유지하되, SoT는 `ValueRecord(VAL-*)`로 승격시키는 방향.

3. **기존 호출 지점 매핑**

   - v7에서 `Quantifier`를 직접 호출하던 코드:

     ```
     quantifier.calculate_sam(...)
     ```

     → v8:

     ```
     calculator_agent.calculate(target="SAM", mode="convergence", ...)
     ```

   - v7에서 Estimator를 직접 SoT로 보던 부분은:

     - Observer/Explorer 쪽에서는 `VAL-*`만 직접 쓰고, EstimationResult는 `origin_level=prior` evidence로만 남기는 방식으로 API를 정리.

------

## 4. 정리

요약하면, v7 코드를 v8 설계 위에 얹어봤을 때 **특히 애매한 지점**은:

1. Estimator 4-Stage 중 Stage 3/4의 “센서 퓨전” 위치가 Calculator/Observer/EvidenceCollector 사이에서 공중에 떠 있음.
2. Quantifier가 Calculator/Observer 사이에 찢어지면서, “Bill”이라는 Agent mental model이 사라진 상태.
3. SoT가 Estimator → Validator-Calculator-Estimator 생산라인으로 이동했는데, 이를 대표하는 새 ValueRecord/ID 스펙이 없다.
4. “tier”라는 단어가 레이어/출처 두 군데에서 중복 사용되며 혼란 가능성이 높음.
5. KG/Pattern YAML이 Data Source Priority 안에서 어디에 속하는지 명확히 정의되지 않았음.

위에서 제안한 스켈레톤 조정(6 Agent 재정의 + Value Factory 섹션 추가 + 역할 분리 + 용어 정리 + KG 위치 명시)을 반영하면,

- v7의 강점(4-Stage Fusion, SoT 추적성, 6-Agent 페르소나)을 최대한 유지하면서,
- v8이 지향하는 구조(Validator-Calculator-Estimator 생산기지, Data Source Priority, Calculator 중심 정량화)를 자연스럽게 수용할 수 있습니다.

------

## 사유 공개 블록

### 가정

- v7의 실제 코드 구조는 `umis.yaml`과 Blueprint에 기술된 내용과 크게 다르지 않다고 가정했습니다.
- v8 문서(UMIS_v8_AGENT_ROLES_AND_WORKFLOWS)는 “완성된 스펙”이 아니라 Design Review 단계 초안이라, 수정 여지가 충분하다고 가정했습니다.UMIS_v8_AGENT_ROLES_AND_WORKFLO…
- 호환성은 중요하지 않지만, v7의 py/yaml 자산을 가능한 한 재사용하는 것이 목표라고 이해했습니다.

### 근거

- Estimator 4-Stage 구조, single_source_policy, EstimationResult 정의는 umis.yaml + Blueprint에 명시.
- v8에서 Estimator simplification, Calculator 역할, Evidence Collector/Validator 설계는 v8 문서에 명시.
- Data Source Priority 재정의는 별도 문서에서 Tier 1–4와 Validator/Estimator 관계를 명확히 정의.

### 추론 경로

1. 먼저 v7의 Estimator/Quantifier/Validator/Observer 역할과 4-Stage Fusion 구조를 정리해 “지금 구현된 현실”을 잡았습니다.
2. 그 다음 v8 Agent Map과 Tier 1–3 정의, Calculator/Estimator 재설계를 읽고, 어떤 기능이 어느 쪽으로 이동했는지 기능별로 매핑했습니다.
3. 매핑 과정에서 “어디는 깔끔히 1:1, 어디는 1:N, 어디는 사라지거나 분산”되는지를 표면화했고,
4. 애매한 지점들은
   - **SoT 엔티티 부재**,
   - **센서 퓨전의 주인 부재**,
   - **Quantifier mental model 붕괴**,
   - **tier 중복 사용**,
   - **KG 위치 미정**
      의 다섯 가지로 압축했습니다.
5. 마지막으로 이 다섯 가지 문제를 모두 해결하는 방향으로 v8 스켈레톤에 들어갈 만한 새 섹션(Agent 재정의, Value Factory, origin_level, KG 위치)을 제안했습니다.

### 대안

- **대안 1: Estimator 4-Stage를 그대로 유지**
  - v8에서도 Estimator를 그대로 SoT로 두고 Calculator는 단순 계산기(공식만 실행)로 두는 방식.
  - 장점: 마이그레이션 최소화, 이해 구조 단순.
  - 단점: “Validator-Calculator-Estimator 생산기지”라는 새 철학과 Data Source Priority 문서와 충돌.
- **대안 2: Calculator를 완전한 Agent로 승격하지 않고 Observer 내부 기능으로 흡수**
  - Quantifier를 완전히 제거하고, Observer가 직접 계산/수렴까지 수행.
  - 장점: Agent 수 감소, UX 측면에서 단순.
  - 단점: v7의 Bill 페르소나/폴더 구조/코드 재사용성이 떨어지고, 역할 분리가 흐려짐.
- **대안 3: Value Factory 없이 각 Agent가 제각각 Result 타입을 가진 채 loosely coupled**
  - Validator/Calculator/Estimator가 각자 자기 타입만 반환하고 Observer가 알아서 섞는 구조.
  - 장점: 초기 구현 간단.
  - 단점: SoT/ID 네임스페이스가 다시 분산되고, “단일 진실의 원천” 철학이 희미해짐.

제안안은 위 세 가지를 모두 고려했을 때,

- v7의 장점(SoT/ID/4-Stage 개념)을 최대한 보존하면서
- v8에서 추구하는 Data Source Priority + Validator-first + Calculator 중심 정량화를 수용하는 절충안입니다.

### 리스크 / 불확실성

- 실제 v7 Python 코드(biz 로직, 호스트 프로젝트)에서 Quantifier/Estimator를 어떻게 호출하고 있는지에 따라,
  - 제안한 Agent/Value Factory 구조가 일부 안 맞을 수 있습니다.
- ValueRecord(VAL-*)를 새 SoT로 정의하면,
  - 초기에는 EstimationResult, CalculationResult, ValidatedData를 모두 감싸는 어댑터/래퍼 계층을 만들어야 해서 구현 복잡도가 상승합니다.

### 검증 아이디어

- **1단계**: 간단한 SAM 계산 시나리오 하나를 골라,
  - v7: Quantifier + Estimator 4-Stage
  - v8: Validator + Calculator + Estimator + ValueRecord
     두 버전의 call graph를 실제 코드 기준으로 그려보면, 제안 구조의 틈이 더 명확하게 드러납니다.
- **2단계**: Prototype 수준으로 `ValueRecord` 클래스를 만들고,
  - Validator/Calculator/Estimator 각각에서 이 타입으로만 값을 내보내게 한 뒤,
  - Observer가 “VAL-*만 본다”는 규칙으로 MarketRealityReport를 만드는 간이 테스트를 작성하면 설계 타당성을 빠르게 검증할 수 있습니다.

이제 여기서 나온 기준을 바탕으로, 다음 단계에서 실제 `umis_v8.yaml` 스켈레톤에 이 구조를 녹여 넣으면서 구체적인 필드/섹션을 같이 다듬어 가면 좋겠습니다.

##### 나의 말:

검증 아이디어를 실행 해 보자.

###### ChatGPT의 말:

###### ChatGPT의 말:

좋습니다, 이제 진짜로 “v7 → v8 검증 실험” 한 번 돌려보겠습니다.
 목표는 **실제 v7 사용 예시들(umis.yaml)을 v8 구조에 얹어보면서, 어디가 자연스럽게 매핑되고 어디가 애매하게 뜨는지**를 찾아내는 겁니다.

------

## 1. 이번에 실행할 검증 아이디어 정리

이번 검증은 이렇게 정의하겠습니다:

1. **v7에서 Estimator(Single SoT)를 호출하던 대표 케이스 3개**를 잡습니다.
   - Observer → Estimator (구조 비율/수수료율 등) umis
   - Explorer → Estimator (기회 크기 빠른 추정) umis
   - Quantifier → Estimator (Churn Rate 등 계산용 값) umis
2. 이 3개를 **v8 설계(Validator + Calculator + Estimator 3-Agent SoT 팩토리)** 위에 올려놓고,
   - 누구를 호출해야 하는지 (Observer/Explorer/Calculator/Validator/Estimator)
   - `DATA_SOURCE_PRIORITY_REDESIGN`에서 정의한 **Validator 우선, Estimator Fallback** 프로토콜과 모순이 없는지
   - v8 문서 상에 실제로 그 길이 정의돼 있는지를 점검합니다.
3. **매핑이 깔끔히 되는 부분 / 애매하게 붕 뜨는 부분**을 나누고,
   - 애매한 부분은 “v8 스켈레톤/umis.yaml에서 어디를 고쳐야 해결되는지”까지 역추론합니다.

이게 말하자면 미니 마이그레이션 드라이런입니다.

------

## 2. 케이스 1 – Observer → Estimator (시장 구조 비율/수수료율)

### 2-1. v7에서의 사용 패턴

umis.yaml에서 Observer는 다음과 같이 **구조 비율/수수료율**이 필요할 때 Estimator를 직접 호출합니다. umis

- 예: “플랫폼 평균 수수료율은?”
- 규칙: “비율/분배 추정 시: Estimator(Fermi) 호출”
- universal_tools: `estimator_collaboration` (하드하게 “모든 값 추정은 Estimator만 수행 (Single Source of Truth)”라고 못 박혀 있음)

즉 v7의 mental model:

> “Observer는 계산은 안 하고, **비율이든 뭐든 숫자만 필요하면 Estimator를 바로 부른다**.”

### 2-2. v8 구조에 올려보면?

v8에서 Observer workflow는 이렇게 바뀌어 있습니다.

- phase_1_structure_analysis: Evidence Collector + Validator로 구조 분석
- **phase_2_market_sizing** (신규):
  - step_1: 방법 4가지 선택 (Top-down / Bottom-up / Proxy / Competitor)
  - step_2: **Calculator에게 각 방법 계산 위임**
  - step_3: Observer가 4개 결과를 보고 수렴 분석 + 가중치 조정
- step_4: 주요 플레이어 매출/점유율 계산(Validator + Calculator)

또, Calculator는 다음 역할을 가집니다.

- role: Formula Designer & Convergence Engine
- capabilities:
  - `formula_generation`
  - `fermi_decomposition` (Fermi Stage를 Calculator로 옮김)
  - `convergence_analysis`

v8 Estimator는 더욱 뒤로 물러나 **Pure Guesser (Last Resort)**가 되었습니다.

- Stage 3(Fermi), Stage 4(Fusion) 제거
- Tier 1-2-3 모두 실패했을 때만 generative prior로 “찍기”

게다가 `DATA_SOURCE_PRIORITY_REDESIGN`에서 **universal_tools.data_request_protocol**을 정의하면서:

- tier_1: Validator (공식 데이터)
- tier_2: Estimator fallback

을 명시합니다.

### 2-3. 실제로 매핑해보면 생기는 애매함

Observer가 “플랫폼 평균 수수료율은?”이 필요하다고 해 봅시다.

- v7 방식:
  - Observer → Estimator.estimate("플랫폼 평균 수수료율은?")
- v8에서 논리적으로 “이상적인” 경로:
  1. **Validator 우선** (`data_request_protocol.tier_1_validator_first`)로 실제 데이터 있는지 검색 → 없으면
  2. Calculator의 **4-Stage Variable Pipeline**에서
     - Tier 1: Literal/Direct RAG
     - Tier 2: Validator
     - Tier 3: Calculator Fermi decomposition
     - Tier 4: Estimator Prior
  3. 최종 `Calculator.calculate(target="플랫폼 수수료율", mode="auto")` 결과를 Observer가 사용

여기서 **실제 v8 문서 상 애매한 부분**이 드러납니다:

1. **Observer가 값을 어디서 받는지가 통일돼 있지 않음**
   - Observer workflow는 “Calculator에게 각 방법 계산 위임”까지만 있고,
   - `플랫폼 수수료율` 같은 “구조 비율”을 위해 Observer가 **직접 Calculator를 부르는지**,
   - 아니면 여전히 Estimator를 부를 수 있는지에 대한 명시가 없음.
2. Calculator와 Observer 사이에 **convergence 역할이 겹침**
   - Calculator capability에 `convergence_analysis`가 정의되어 있고, UMIS_v8_AGENT_ROLES_AND_WORKFLO…
   - Observer workflow에도 `step_3_convergence_analysis`가 따로 있음. UMIS_v8_AGENT_ROLES_AND_WORKFLO…
   - 그러면 “수렴 분석은 누가 최종 권한을 갖는가?”가 모호해집니다.
3. data_source_priority와 **Calculator의 4-Tier Pipeline 용어가 따로 논다**
   - 데이터 우선순위 문서: Tier_1=Validator, Tier_2=Estimator.
   - Calculator 쪽: “4-Tier Pipeline으로 변수 수집”이라고 쓰여 있지만, 그 Tier의 정의가 저 문서와 1:1로 이어져 있다고 되어 있지는 않음.
   - 사용자 입장에서 “Tier”가 두 군데에서 다른 의미로 쓰이는 셈이라, 머릿속에 두 개의 계층 체계가 생깁니다.

### 2-4. 이 케이스에서 나오는 개선 제안

**(A) v8에서 “값 요청”의 단일 진입점 다시 정의**

- v7: `EstimatorRAG.estimate(...)` = Single SoT 엔트리
- v8: **`Calculator.calculate(..., mode="auto")`를 “값 요청”의 기본 진입점**으로 삼는 쪽이 더 자연스럽습니다.
  - 내부에서:
    - Literal/Direct RAG 확인
    - Validator 호출
    - Fermi decomposition (Calculator 내부)
    - 그래도 안 되면 Estimator(v8) 마지막 호출

→ 이렇게 되면 v7에서 Observer가 Estimator를 직접 부르던 케이스는 거의 전부 **Calculator(auto 모드)** 호출로 통합 가능합니다.

**(B) Observer vs Calculator의 수렴 역할 분리**

- 제안 1:
  - Calculator: “숫자 수렴과 아웃라이어 제거까지 담당 → `final_sam`까지 계산”
  - Observer: “그 결과의 ‘해석’과 ‘텍스트 요약’만 담당”
- 제안 2:
  - Calculator: 각 방법별 결과만 내놓고,
  - Observer: CV 계산, outlier 제거, 가중 평균까지 직접 수행 (지금 v8 문서 흐름)
  - 이 경우에는 **Calculator capability에서 `convergence_analysis`는 제거**하는 편이 깔끔합니다.

둘 중 하나를 골라야 “누가 숫자에 대한 최종 책임을 지는지”가 명확해집니다.

**(C) Tier 용어 정리**

- system 전체에서 사용하는 이름을 새로 잡는 것이 좋아 보입니다:
  - level_1: Literal/Direct RAG
  - level_2: Validator
  - level_3: Calculator-Fermi (구조 분해 기반 추정)
  - level_4: Estimator-Prior (순수 guess, 최후)
- `DATA_SOURCE_PRIORITY_REDESIGN`와 `Calculator 4-Tier Pipeline` 모두를 이 네임스페이스로 통일하는 게 좋겠습니다.

------

## 3. 케이스 2 – Explorer → Estimator (기회 크기 빠른 추정)

### 3-1. v7에서의 사용 패턴

Explorer는 **기회 크기 초벌 추정**을 위해 Estimator에 상당히 자주 의존합니다.

- when: “기회 크기 빠른 가늠, 우선순위 판단”
- frequency: “★★★★ 자주 사용”
- note: “모든 값 추정은 Estimator만 수행 (Single Source of Truth)”

그리고 Estimator는 4-Stage Fusion으로 꽤 정교한 추정을 수행합니다.

### 3-2. v8에서 올려보면

v8 Estimator는 **Stage3/4가 제거되고 Pure Guesser**가 되었습니다.

- Tier 1-2-3 모두 실패했을 때만 generative prior “찍기”를 합니다.

하지만 Explorer는 “시장 기회 크기를 빠르게 몇 번이나 가늠해보는” 용도가 많고, 매번 Validator/Calculator full 파이프라인을 탈 필요는 없습니다.

그래서 v8 구조와 겹쳐보면:

- Explorer의 “빠른 가늠” 요구사항 ↔ v8 Estimator의 “Pure Guesser”가 **상당히 잘 맞습니다.**
  - 이 경우엔 오히려 v8에서 Estimator가 **“Explorer 전용 빠른 prior 엔진”**처럼 쓰이는 게 자연스러움.

하지만 여기서도 애매함이 하나 생깁니다:

- v8의 글로벌 규칙: “값 요청은 Calculator(auto) 경유”로 설계할 경우,
  - Explorer가 Estimator를 직접 부르는 **예외 케이스**를 어디까지 허용할지 정해야 합니다.

### 3-3. 개선 제안

- **규칙 제안**:
  - “기회 후보 스캔 / 우선순위 러프 정렬” 단계에서는 Explorer가 **Estimator를 직접 호출**해도 된다.
  - 다만 이 경우 결과는 **절대 SoT가 아니고, ‘Draft/heuristic’ 태그가 붙은 값**으로 취급한다.
  - 실제 투자 의사결정이나 보고용 수치로 쓸 때는
    - 반드시 Observer+Calculator+Validator 파이프라인으로 다시 계산해야 한다.
- 이를 umis.yaml v8 스켈레톤에 반영할 때:
  - Explorer의 `universal_tools.estimator_collaboration` 설명을
    - “Single Source of Truth” → “Heuristic Prior Only (Draft용)”
       로 바꿔주는 게 필요해 보입니다.

------

## 4. 케이스 3 – Quantifier(→ Calculator) → Estimator (계산용 값)

### 4-1. v7에서의 사용 패턴

umis.yaml의 예시: Quantifier가 Churn Rate를 추정하기 위해 Estimator를 호출합니다. umis

- `estimator.estimate('Churn Rate는?', domain='B2B_SaaS')`
- 결과는 `EstimationResult(value=0.06, confidence=0.85, reasoning_detail={...})`
- 이후 SAM/수익성 계산에 그대로 사용

또, 전체 설계는 “모든 값/데이터 추정은 Estimator만 수행”이라는 Single SoT 원칙을 깔고 있습니다.

### 4-2. v8 구조로 올려보면

v8에서는:

- Quantifier가 **Calculator로 개명/재정의**되고,
- Calculator는 스스로 fermi_decomposition과 convergence을 할 수 있는 “공식 엔진”입니다.
- Estimator는 Tier 4 pure guess로 밀려났기 때문에,
  - “Churn Rate 같은 값”은 가능한 한 Validator + Calculator(Fermi)에서 끝내고,
  - 그래도 안 되면 Estimator를 쓰는 게 자연스러운 그림입니다.

즉, v8에서는 **Quantifier가 Estimator에 직접 붙어있던 구조가 해체되고**, Calculator가 중간에 껴야 합니다.

### 4-3. 실제 매핑에서 드러나는 애매한 지점

v7 코드를 상상해 보면:

```
result = estimator.estimate("Churn Rate는?", domain="B2B_SaaS")
use(result.value)
```

이 호출을 v8로 옮기면, 아래 중 하나를 선택해야 합니다:

1. `calculator.calculate(target="B2B_SaaS Churn Rate", mode="auto")`
2. `validator.active_search(...)` 후 없으면 `estimator.estimate(...)` 직접 호출

지금 v8 문서에는 **1번을 명시적으로 “이게 새로운 표준이다”라고 못 박는 문장이 없음**이 문제입니다.

또 하나:

- `DATA_SOURCE_PRIORITY_REDESIGN`에서 Quantifier 섹션은 여전히
  - “데이터 수집 프로토콜: Validator → 없으면 Estimator”라는 2단계만 정의하고 있습니다. DATA_SOURCE_PRIORITY_REDESIGN
- 하지만 v8에서는 중간에 Calculator(Fermi)라는 Tier 3가 새로 들어왔습니다.

→ 즉, **문서 상 pipeline은 2단계인데, 실제 아키텍처는 3단계가 되어버린 상태**입니다.

### 4-4. 개선 제안 (마이그레이션 가이드 레벨)

**v7 → v8 코드 매핑 기준 제안:**

1. **모든 `estimator.estimate()` 호출 중에서**
   - “순수 계산/공식에 들어가는 값” (Churn Rate, ARPU, Conversion Rate 등)은
      → v8에서 `calculator.calculate(target=..., mode="auto")`로 전환
      → Calculator 내부에서 Validator/Estimator를 적절히 호출
2. “기회 크기 빠른 가늠” 같은 Explorer용 prior는
    → 여전히 Estimator(v8)를 직접 호출
    → 결과는 SoT가 아닌 “draft_prior”로 태깅
3. `DATA_SOURCE_PRIORITY_REDESIGN`의 Quantifier 섹션을 v8용으로 업데이트:
   - step_0: Validator
   - step_1: Calculator(Fermi 포함)
   - step_2: Estimator (pure guess, 최후)

이렇게 해놓으면 v7 코드를 훑으면서 **“이건 Calculator로 이관 / 이건 Estimator 직통 유지”**라는 분류 기준을 잡을 수 있습니다.

------

## 5. 문서 간 모순/잉여 설계도 같이 드러난 부분

이번 검증을 돌려보니, **아키텍처 문서들끼리 충돌하는 포인트**도 선명하게 보입니다.

1. **UMIS_ARCHITECTURE_BLUEPRINT & umis.yaml vs v8 문서**
   - blueprint & umis.yaml: Estimator = Single SoT (4-Stage Fusion)
   - v8: Estimator = Last Resort Pure Guesser, Stage3/4는 Calculator로 이동, Fusion 제거
   - → v8을 진짜로 채택한다면,
     - blueprint의 “Single Source of Truth” 섹션과
     - umis.yaml의 Estimator 설명(도구 템플릿 포함)을 **완전히 덮어쓰는 작업**이 필요합니다.
2. **LLM_ABSTRACTION_v7_11_0 TaskType vs v8 책임 이동**
   - v7: TaskType에 `stage_3_fermi`, `stage_4_fusion`이 Estimator 영역으로 정의 umis
   - v8: Stage3(fermi) 기능은 Calculator가 담당, Stage4(Fusion)는 제거
   - → `model_configs.yaml`의 TaskType 설명 및 LLM 라우팅 로직도,
     - “fermi_decomposition은 이제 Calculator 관련 TaskType이다” 쪽으로 리팩터링 필요.
3. **Tier라는 단어의 중복 사용**
   - Data Source Priority 문서의 Tier1/Tier2 (Validator/Estimator)
   - Calculator의 “4-Tier Pipeline” (실제론 Literal/Validator/Fermi/Estimator 순으로 쓰이는 듯)
   - Estimator v8의 “Tier 1-2-3 모두 실패 시 호출” 표현
   - → 같은 단어에 서로 다른 레이어 의미가 섞여 있어, 실제 구현자가 보면 헷갈릴 수밖에 없는 상태입니다.

------

## 6. 이번 검증에서 도출된 “스켈레톤 수정 포인트” 요약

**v8 umis.yaml 스켈레톤을 손볼 때 반영해야 할 핵심 정리만 뽑으면:**

1. **값 요청 엔트리포인트 재정의**
   - `EstimatorRAG.estimate()` → SoT 엔트리가 아니라
   - `Calculator.calculate(..., mode="auto")`가 SoT factory의 외부 인터페이스가 되도록 문서/예시에 반영
2. **Observer/Explorer/Validator/Calculator의 값 요청 규칙 명시**
   - Observer/Quantifier(=Calculator)/Validator는 **값이 필요할 때 기본적으로 Calculator(auto) 호출**
   - Explorer만 “Draft Prior용”으로 Estimator 직접 호출 허용 (결과는 SoT 아님 명시)
3. **Tier/Stage/Source-Level 용어 정리**
   - Stage는 더 이상 Estimator 내부 4-Stage가 아니고,
   - system-wide `source_level`(Literal/Validator/Calculator-Fermi/Estimator-Prior) 같은 공용 용어로 재정의
   - Calculator 문서와 Data Source Priority 문서를 이 공통 용어로 동기화
4. **v7 문서/예시 싹 정리**
   - umis.yaml에서 “모든 값 추정은 Estimator만 수행 (Single SoT)” 문구는 전부 제거/교체
   - Estimator Agent 템플릿/가이드 문서에서도 Single SoT 언급 삭제 후,
     - “Last Resort Guesser + Explorer Quick Prior용”으로 역할 축소
5. **LLM TaskType/모델 라우팅 재정의**
   - `stage_3_fermi` 관련 TaskType은 Calculator 쪽 작업으로 이동
   - Estimator 관련 TaskType은 Prior + Certainty 평가 위주로 축소

------

## 7. 사유 공개 (가정/근거/추론/대안/리스크/검증)

**가정**

- v8 설계안(UMIS_v8_AGENT_ROLES_AND_WORKFLOWS)이 “최신 진실”이며, blueprint/umis.yaml은 v7 기준이라고 가정했습니다.
- 사용자가 말한 “Validator–Calculator–Estimator 3-Agent SoT 팩토리”는
  - v8의 Calculator/Validator/Estimator 정의 + Data Source Priority 문서를 합친 개념이라고 해석했습니다.

**근거**

- v7의 Single SoT 구조 및 Estimator 4-Stage Fusion 정의: umis.yaml + Architecture Blueprint.
- v8의 Observer/Validator/Calculator/Estimator 역할 정의 및 Workflow: UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.
- Data Source Priority 재설계: DATA_SOURCE_PRIORITY_REDESIGN.

**추론 경로**

1. v7의 Estimator 호출 예시들을 실제 코드/예제 수준에서 뽑았습니다. (Observer, Explorer, Quantifier)
2. 각 예시를 v8에서 **누가 담당해야 자연스러운지** 역할 정의와 워크플로우에 대입했습니다.
3. 그 과정에서
   - 엔트리포인트 부재,
   - convergence 역할 중복,
   - Tier 용어 상이
      같은 구조적 모순이 드러나는 부분을 수집했습니다.
4. 이를 기준으로 “v8 스켈레톤에서 어디를 바꾸면 이 모순이 사라지는지” 역으로 도출했습니다.

**대안**

- SoT 엔트리포인트를 Calculator가 아니라 **새로운 “ValueFactory” 서비스**로 정의하고,
  - 그 안에서 Validator/Calculator/Estimator를 orchestration 하는 구조로 만드는 것도 한 가지 대안입니다.
- 다만 이미 v8 문서에 Calculator가 상당히 중앙에 서 있으므로,
  - 지금 단계에서는 Calculator를 엔트리포인트로 삼는 것이 마이그레이션 비용이 더 낮아 보입니다.

**리스크/불확실성**

- 실제 v7 파이썬 코드(umis_rag/agents/…)의 세부 구현이 여기 문서와 100% 일치한다고 보장할 수는 없습니다.
  - 구현에서 이미 일부 역할이 다르게 나뉘어 있을 수도 있습니다.
- v8 문서도 “초안”일 가능성이 있고, 내부에서 아직 합의되지 않은 표현(특히 Tier 용어)이 남아 있을 수 있습니다.

**검증**

- 다음 단계에서 할 수 있는 추가 검증은:
  1. v7 코드베이스에서 `estimator.estimate(` 호출을 전부 grep해서
     - “계산용 값 / 기회 prior / 구조 비율”로 실제로 분류해보는 것.
  2. 이 분류 결과를 방금 제안한 매핑 규칙(Calculator vs Estimator direct)과 비교해서
     - 예외 케이스가 얼마나 나오는지 보는 것.
  3. 그 결과를 토대로 v8 umis.yaml 스켈레톤에
     - “migration mapping table” 섹션을 하나 추가해도 좋겠습니다.

이제 이 검증 결과를 기반으로, **v8 스켈레톤에 어떤 항목을 어떻게 바꿀지**를 한 덩어리씩 구체적으로 적어 나가면 됩니다.

##### 나의 말:

좋아. 추가 검증 진행하자. 그리고 fusion 단계가 없어져도 괜찮을지 한번 더 검증이 필요해 보여.

###### ChatGPT의 말:

###### ChatGPT의 말:

결론부터 말씀드리면, **fusion 단계(Stage 4)를 “완전히 삭제”하는 건 아직은 위험하고**,
 대신 아래 두 가지를 같이 가져가는 쪽이 안전합니다.

1. **실제 동작은 “선택/검증 레이어”로 단순화**해서 *숫자 혼합(fusion)*을 사실상 끄고,
2. **runtime에서 `fusion_enabled` 플래그로 켜고 끄는 A/B 검증**을 한 번 더 돌려보는 것.

즉, 설계 상으로는 4-Stage 구조를 유지하되,
 **“숫자 가중 합성하는 fusion”을 제거해도 되는지**를 *실측 데이터*로 확인하는 쪽이 좋습니다. UMIS_ARCHITECTURE_BLUEPRINT

------

## 1. 지금 fusion(Stage 4)이 실제로 하고 있는 일 재정리

문서 상 Stage 4는 이렇게 정의되어 있습니다: UMIS_ARCHITECTURE_BLUEPRINT

- 상위 Stage 1–3의 결과를 **가중합(fusion)**
- 일관성 검증
- 최종 certainty 계산 후 반환

그리고 전체 파이프라인은:

- Stage 1–3에서 **certainty=high**면 *early return*
- **fusion은 “다 애매할 때 마지막으로 돌리는 레이어”**

그래서 현실적으로는:

- **“확정적(evidence-rich) 쿼리”**에서는 Stage 4가 *거의 안 쓰이고*
- **데이터 빈약 + 추정 난이도 높은 케이스**에서만 의미 있게 등장합니다.

이 말은 곧:

> *fusion을 건드려도 영향 받는 영역은 “가장 어려운 꼬리 분포 사례들”이다.*

여기를 날려버리면,

- 아키텍처는 단순해지는데
- “가장 힘든 케이스에서의 방어 레이어”를 하나 빼는 셈이라서
- 검증 없이 없애긴 좀 아슬아슬합니다.

------

## 2. “fusion 삭제” 시 실제로 깨질 수 있는 것들

조금 더 구체적으로, Stage 4가 사라지면 이런 것들이 영향권에 들어갑니다:

### 2-1. **다중 후보 관리 방식**

지금 구조에서는 (개념적으로):

- Stage 2(Generative Prior)와 Stage 3(Fermi)가
  - 비슷한 값 / 다른 값
  - 비슷한 certainty / 다른 certainty
     이런 조합으로 결과를 내고,
- Stage 4가 **“누굴 최종 대표값으로 삼을지 + certainty를 어떻게 잡을지”**를 전담합니다. UMIS_ARCHITECTURE_BLUEPRINT

fusion을 없애면:

- “가장 certainty 높은 Stage만 선택” 같은 **단순 규칙**이 필요
- 그럼,
  - Fermi가 구조적으로는 맞는데 certainty가 보수적으로 잡힌 경우,
  - Prior가 우연히 high로 평가된 경우
     → *오히려 fusion이 있던 것보다 나빠질 수 있음*

### 2-2. **certainty 스케일의 의미**

지금 설계에서는 최종 certainty가:

- Stage별 confidence
- 일관성(variance)
- guardrail 통과 여부

를 종합해서 나오는 “최종 스케일”입니다. UMIS_ARCHITECTURE_BLUEPRINT

fusion이 사라지면:

- Stage 2/3의 **로컬 certainty 값 = 곧 최종 certainty** 가 되는데,
- 이 둘의 스케일이 *현재 전제대로 충분히 보정(calibration)되어 있지 않다면*,
  - 어떤 도메인에서는 무조건 prior가 세고,
  - 어떤 도메인에서는 무조건 Fermi가 세지는 식으로
     **스케일 붕괴**가 발생할 수 있습니다.

### 2-3. **Guardian / Memory 쪽 계약**

Guardian/Meta-RAG 쪽에서 보는 것은:

- “최종 EstimationResult의 certainty”와
- “reasoning_detail + source” 조합입니다. UMIS_ARCHITECTURE_BLUEPRINT

fusion이 사라지고:

- Stage 2/3 중 하나를 즉시 선택하는 구조가 되면,
- “다른 Stage의 반대 의견”이
  - log에는 남더라도
  - Guardian 입장에서는 *한 번 가공된 메타 정보*로만 보이게 됩니다.

즉, 지금은:

> “fusion이 multi-stage 의견을 한 번 모아서 ‘최종 견적서’로 나온다”

였다면,

> fusion 삭제 후에는 “어느 한 Stage가 단독 견적서 작성자”

가 되어버립니다.

------

## 3. 그러면, 어떤 검증을 해야 “없애도 되겠다”고 말할 수 있나?

“추가 검증”을 **완전히 오프로딩 가능하게** 정리해 보겠습니다.

### 3-1. 실험 모드 정의

runtime에 플래그 하나만 추가해 두시면 됩니다:

```
# config/runtime.yaml 의 예시
estimator:
  fusion_mode: "full"      # full / selector_only / disabled
```

- `full`
  - 지금 문서에 정의된 4-Stage Fusion 그대로
- `selector_only`
  - Stage 4는 **숫자 가중합은 하지 않고**
  - 후보들 중 “한 명을 고르고, sanity-check만 수행”
- `disabled`
  - Stage 4 *완전 우회*
  - Stage 1–3 중에서 **가장 높은 priority/확신도의 출력**이 곧 최종값

실험은 **최소 2가지 모드**:

1. `full` vs `selector_only`
2. `selector_only` vs `disabled`

을 나란히 돌려보는 구조로 설계하는 게 좋습니다.
 바로 `full` vs `disabled`로 가면, 원인이 너무 섞여버립니다.

### 3-2. 평가 지표 세트

각 모드별로, 다음 세 가지 층위에서 비교하는 걸 추천드립니다.

1. **수치 정확도 (Ground Truth 있는 샘플)**
   - validator가 SRC로 가지고 있는 값들에 대해
   - Estimator가 추정한 값의 상대/절대 오차 분포
2. **certainty calibration**
   - 예: certainty=high인 샘플들의 실제 오차 평균/분산
   - certainty bucket별 Brier score 혹은 bin별 error rate
3. **다운스트림 영향 (Quantifier / 시트 레벨)**
   - market_sizing.xlsx / unit_economics.xlsx 결과 중
   - 주요 KPI (LTV, CAC payback, 시장규모 등)의
   - 모드별 차이(%)와 tolerance 이내 비율

여기서 **특히 중요한 건 1번+2번의 결합**입니다.

- `disabled` 모드에서
  - 평균 오차는 비슷한데
  - certainty calibration이 틀어지면:
     → Guardian / Explorer / Observer가 certainty를 믿고 써버릴 때
     리스크가 커집니다.

### 3-3. 케이스 분류별로 분해해서 보셔야 합니다

전체 평균만 보면 “거의 차이 없음”처럼 보일 수 있어서,
 반드시 **질문 타입별 slice**를 나눠서 보는 게 좋습니다.

예를 들면:

- evidence-rich (Validator 확정 데이터 있음)
- evidence-sparse (Validator / Direct RAG 둘 다 약한 케이스)
- prior-dominant (Stage 2가 주도)
- fermi-dominant (Stage 3가 주도)
- high-variance (Stage 2/3 값 차이가 큰 케이스)

fusion을 없앨 수 있는지의 핵심은:

> “high-variance + evidence-sparse 케이스에서
>  full vs disabled의 성능/리스크가 허용 가능한가?”

이 한 줄로 요약됩니다.

------

## 4. 제가 추천하는 현실적인 방향

### 4-1. 당장 할 수 있는 구조 정리

1. **fusion 레이어의 역할을 축소**
   - 숫자 가중 합성 로직을 전부 꺼버리고
   - 다음 정도만 담당하게 리팩토링:
     - 후보 중 **최고 priority + certainty**를 선택
       - 우선순위: Literal/Validator > Direct RAG > Fermi > Prior
     - 범위 검증 (예: 음수 방지, 0~1 범위 등 guardrail)
     - certainty 재스케일 (optional)
2. **이 상태를 `selector_only` 모드로 정의**
   - 코드 상 구조/파일(예: `fusion_layer.py`)은 그대로 유지
   - routing_policy.yaml 등에서 “4-Stage” 명세도 그대로 두되,
      “실제 fusion 없음”인 상태로 한 번 굴려봄

이렇게 하면:

- 아키텍처 상 4-Stage 철학과 문서 구조는 유지
- 운영 상 복잡도는 줄고
- 필요하면 **진짜 fusion 로직을 언제든 되돌릴 수 있음**

즉, “실제 삭제” 전에 **안전한 반쯤 은퇴** 상태로 만드는 셈입니다.

### 4-2. 그 다음 단계: 정말 삭제해도 되나?

위 `selector_only` 모드에서 충분히 데이터가 쌓이면:

- `full` vs `selector_only` 차이가 거의 없고
- `selector_only` vs `disabled`에서도
  - tail case에서 error / calibration 차이가 작다면

그때는:

- fusion을 **개념적으로는 “Stage 1–3의 공통 Finalizer”** 정도로 낮추고,
- 문서도 “Fusion & Validation → Finalization & Validation” 식으로
   살짝 리네이밍한 뒤
- “숫자 가중합”이라는 기능은 공식적으로 은퇴시키는 방향이 맞습니다.

반대로, 실험 결과:

- tail case에서 `disabled` 모드가 **명확히 더 나쁘다**
- 특히 high-variance 케이스에서 크게 흔들린다

라는 게 보이면,

> “fusion 단계는 *자주 쓰이진 않지만*,
>  사다리 아래 받쳐주는 마지막 안전망”

이라는 해석이 되기 때문에,
 코어 아키텍처에서는 유지하는 게 맞습니다.

------

## 사유 공개

**1) 가정**

- 현재 Estimator는 문서에 정리된 4-Stage 구조(1 Evidence, 2 Prior, 3 Fermi, 4 Fusion)를 그대로 사용 중이다. UMIS_ARCHITECTURE_BLUEPRINT
- Stage 1–3에서 high certainty면 early return 하는 로직은 유지된다.
- fusion 단계 삭제/단순화 논의는 **정확도 유지 + 복잡도 감소**를 목표로 한다.

**2) 근거**

- 설계상 Stage 4는 “모든 Stage 결과 가중 합성 + 일관성 검증 + 최종 certainty 계산” 역할로 정의되어 있음. UMIS_ARCHITECTURE_BLUEPRINT
- Estimator는 시스템 내에서 “단일 진실의 원천” 역할을 하므로, 최종 결과를 조정하는 레이어의 삭제는 전체 시스템에 파급이 큼. UMIS_ARCHITECTURE_BLUEPRINT
- Guardian/Meta-RAG는 최종 EstimationResult의 certainty와 reasoning_detail을 기반으로 작동하도록 설계되어 있음. UMIS_ARCHITECTURE_BLUEPRINT

**3) 추론 경로**

- fusion이 자주 호출되지 않는다 하더라도, 호출되는 상황은 “가장 불확실하고 어려운 케이스”일 가능성이 높음 → 여기가 바로 삭제 시 리스크가 집중되는 구간.
- 따라서 단순 이론 논의만으로 삭제 여부를 결정하는 것은 부적절하고,
  - runtime 플래그를 통한 모드 분리
  - offline 평가(정답/ground truth 비교 + calibration 검증)
     를 통한 데이터 기반 결정이 필요.
- 구조 및 문서 상 일관성을 유지하려면,
  - 먼저 fusion을 “선택+검증 레이어(selector_only)”로 축소
  - 이후 성능을 확인하고 필요 시 완전 삭제로 가는 2단계 전략이 합리적.

**4) 대안**

- **직접 삭제안**: fusion 레이어를 코드/문서에서 바로 제거하고, Stage 3를 최종 레이어로 승격
  - 장점: 설계 단순화
  - 단점: tail case에서의 품질/리스크를 사전 검증 없이 떠안게 됨
- **완전 유지안**: 아무것도 건드리지 않고 4-Stage Fusion을 계속 사용
  - 장점: 안정성
  - 단점: 복잡도 및 유지보수 비용, 그리고 실제 기여도가 낮을 가능성을 그대로 유지
- **제안한 절충안**: fusion을 selector_only로 축소 후, runtime 플래그 기반 실험
  - 구조 유지 + 위험 최소화 + 데이터 기반 의사결정 가능

**5) 리스크 / 불확실성**

- Estimator의 실제 구현에서 Stage별 certainty 스케일이 어느 정도로 잘 보정되어 있는지에 따라, selector_only / disabled 모드에서의 품질이 크게 달라질 수 있음.
- 기존 로그/데이터셋에 “진짜 어려운 질문들(tail case)”이 충분히 포함되어 있지 않다면, 실험 결과가 지나치게 낙관적으로 나올 위험이 있음.
- Guardian/Memory 쪽에서 certainty 값에 붙여둔 각종 휴리스틱/임계값이, fusion 삭제 후에도 그대로 유효할지 검증 필요.

**6) 검증**

- `fusion_mode = full / selector_only / disabled` 3가지 모드로
   같은 쿼리 세트를 재실행하여:
  - 수치 오차
  - certainty calibration
  - 다운스트림 시트 결과 차이
     를 비교하면, fusion 단계의 실질적 기여도를 계량적으로 파악할 수 있습니다.
- 특히 evidence-sparse + high-variance 케이스의 샘플을 별도 태깅해 분석하는 것이, “완전 삭제해도 괜찮다”라는 결론의 신뢰도를 좌우할 것입니다.

------

요약하면, **지금 단계에서 바로 fusion을 없애기보다는**
 운영상 기능을 최대한 줄인 상태(selector_only)로 돌리면서
 런타임 플래그 기반 실험을 한 번 더 거치고,
 그 결과를 보고 “진짜 은퇴” 여부를 결정하시는 게 제일 안전한 수순입니다.

##### 나의 말:

\- 난 fusion을 없애고 싶은게 아냐. 필요하다면 당연히 유지하고 발전시키고 싶어. 다만, clean architecture를 유지하고 싶을 뿐이야. 이 의견을 반영한다면 너라면 어떻게 합리적으로 처리할 것 같아? 

###### ChatGPT의 말:

###### ChatGPT의 말:

핵심만 먼저 말하면요:

- **fusion은 그대로 둡니다.**
- 대신 **“도메인 순수 함수 + 전략 객체(FusionPolicy)”로 고립**시키고,
- **RAG/LLM/Config 의존성은 모두 바깥 레이어(인프라/런타임)로 밀어내는 방향**으로 정리하는 게 제일 합리적입니다. UMIS_ARCHITECTURE_BLUEPRINT

즉, *“4-Stage Fusion 알고리즘은 남기되, 그게 아키텍처를 더럽히는 위치에만 두지 말자”*가 방향입니다.

------

## 1. 먼저 정리: fusion이 지금 하는 일

UMIS 설계에서 Estimator는:

- Stage 1: Evidence Collection
- Stage 2: Generative Prior
- Stage 3: Fermi Decomposition
- **Stage 4: Fusion & Validation (여러 Stage 결과를 합성)** UMIS_ARCHITECTURE_BLUEPRINT

지금 고민 포인트는 보통 이런 거일 가능성이 큽니다:

- Fusion이 **각 Stage 내부 구현 디테일 + RAG/LLM + runtime_config**를 다 알게 되면서
  - 의존성이 거꾸로 새고,
  - Estimator 패키지가 “도메인 + 인프라 + 정책”이 뒤섞인 덩어리가 되어버린다.

그래서 “fusion을 없앨까?”라는 생각이 나왔던 것 같은데,
 당신 말대로 **알고리즘 자체는 자산**이라서 없애는 건 손해입니다.

------

## 2. 내가 하면 이렇게 자를 것 같아요

### 2-1. 레이어 역할을 한 줄로 정의

Clean architecture 스타일로 아주 단순하게 나누면:

- **Domain Layer (estimation domain)**
  - *“추정”이라는 개념 자체를 정의하는 곳*
  - `EstimationQuestion`, `StageResult`, `EstimationTrace`, `EstimationResult`
  - `FusionPolicy` 인터페이스 + 기본 구현체들 (예: WeightedFusionPolicy)
  - **RAG/LLM/Chroma/Neo4j/파일 시스템 아무것도 모름**
- **Application Layer (EstimatorPipeline)**
  - “Stage 1~3를 어떻게 orchestration 하고, 언제 fusion을 호출할지”만 알고 있음
  - Budget 모드(standard/aggressive/minimal) 해석
  - 어느 Stage까지 갈지, 언제 early return 할지 결정
  - Domain의 `FusionPolicy`에 Stage 결과를 넘겨 최종 결과를 받음
- **Infrastructure Layer (RAG/LLM/Config adapters)**
  - `EvidenceCollector`, `PriorEstimator`, `FermiEstimator`의 구체 구현
  - Chroma, Neo4j, LLM Provider, YAML 설정 파일 로딩
  - Domain에서 정의한 인터페이스를 실제 서비스/DB/API에 매핑

fusion은 **무조건 Domain Layer 쪽에 둡니다.**
 그러면 “fusion을 유지하면서도 clean architecture”가 자동으로 따라옵니다.

------

### 2-2. fusion을 “도메인 순수 함수”로 고립

fusion을 이런 느낌으로 정의합니다 (개념만):

```
# domain/estimation/models.py
class StageId(Enum):
    EVIDENCE = "evidence"
    PRIOR = "prior"
    FERMI = "fermi"

@dataclass
class StageResult:
    stage: StageId
    value: float  # 혹은 Any
    confidence: float   # 0.0 ~ 1.0
    source_tag: str     # "Literal" / "Direct_RAG" / "Validator" / ...

@dataclass
class EstimationResult:
    value: float
    certainty: str      # "high" / "medium" / "low"
    source: str         # "Literal" / "Fusion" ...
    reasoning_summary: str
    trace: list[StageResult]
# domain/estimation/fusion_policy.py
class FusionPolicy(Protocol):
    def fuse(self, stage_results: list[StageResult]) -> EstimationResult:
        ...
```

그리고 실제 구현체:

```
class WeightedFusionPolicy(FusionPolicy):
    def __init__(self, config: FusionConfig):
        self.config = config  # Stage별 가중치, cutoff 등

    def fuse(self, stage_results: list[StageResult]) -> EstimationResult:
        # 여기서는 순수 수학 / 로직만
        # - Stage별 weight
        # - 일관성 체크
        # - certainty 계산
        # 외부 I/O, RAG 콜, LLM 콜 없음
        ...
```

포인트:

- **fusion은 인자로 들어온 StageResult 리스트만 보고 판단**
- “LLM이 뭐였는지”, “어느 index를 썼는지”, “config가 YAML에 어떻게 저장돼 있는지”는 전혀 모름
- 그래서 **Domain Layer를 더럽히지 않고 알고리즘만 유지**할 수 있습니다.

------

### 2-3. runtime_config / routing_policy와의 결합 정리

지금 `routing_policy.yaml`, `runtime_config.yaml`에 4-Stage Fusion 관련 정책이 들어가 있는데, 이걸 domain에 그대로 들이밀면 깨끗하지 않죠. UMIS_ARCHITECTURE_BLUEPRINT

그래서 중간에 **Adapter**를 둡니다:

- `FusionConfig` (Domain 모델)
  - `stage_weights: dict[StageId, float]`
  - `high_certainty_threshold: float`
  - `consistency_tolerance: float` (Stage 간 값 차이 허용 범위)
- `FusionConfigLoader` (Infrastructure)
  - `routing_policy.yaml` / `runtime_config.yaml`에서 값 읽어서
  - `FusionConfig` 객체로 변환해서 Domain에 전달

Application Layer에서 하는 일:

```
fusion_config = fusion_config_loader.load()   # infra
fusion_policy = WeightedFusionPolicy(fusion_config)  # domain

pipeline = EstimatorPipeline(
    evidence_stage=evidence_stage,   # infra 구현체
    prior_stage=prior_stage,         # infra
    fermi_stage=fermi_stage,         # infra
    fusion_policy=fusion_policy      # domain
)
```

이렇게 하면:

- YAML 스키마가 바뀌어도 **infra adapter만 수정**하면 됨
- Domain 쪽 `FusionPolicy`와 `FusionConfig`는 안정적인 계약으로 남음
- 당신이 좋아하는 **“LLM Complete Abstraction” 철학**이 fusion에도 그대로 적용됩니다. UMIS_ARCHITECTURE_BLUEPRINT

------

### 2-4. Estimator 패키지 구조를 약간 재정렬

현재 설계는 대략 이런 식이죠: UMIS_ARCHITECTURE_BLUEPRINT

```
umis_rag/agents/estimator/
  estimator.py         # 통합 인터페이스
  evidence_collector.py  # Stage 1
  prior_estimator.py     # Stage 2
  fermi_estimator.py     # Stage 3
  fusion_layer.py        # Stage 4
  models.py
  compat.py
```

이걸 clean architecture 기준으로 *논리적으로*만 쪼개면:

```
umis_rag/estimation/domain/
  models.py              # StageResult, EstimationResult, ...
  fusion_policy.py       # FusionPolicy, WeightedFusionPolicy

umis_rag/estimation/app/
  pipeline.py            # EstimatorPipeline (Stage orchestration)
  budget_modes.py        # standard/aggressive/minimal 처리

umis_rag/estimation/infra/
  evidence_collector_llm.py   # Stage 1 실제 구현
  prior_estimator_llm.py      # Stage 2
  fermi_estimator_llm.py      # Stage 3
  fusion_config_loader.py     # YAML → FusionConfig Adapter
```

그리고 `umis_rag/agents/estimator.py`는 이걸 감싸는 **Facade** 역할만 합니다:

```
class EstimatorRAG:
    def __init__(...):
        # 여기서 domain/app/infra를 조립
        self.pipeline = EstimatorPipeline(...)

    def estimate(self, question: str, domain: str) -> EstimationResult:
        return self.pipeline.run(question, domain)
```

이렇게 되면:

- fusion은 **domain 폴더** 안, “순수 로직” 느낌으로 살아 있음
- fusion을 교체/튜닝하더라도 다른 레이어는 거의 영향 없음
- Agent 입장에서는 여전히 `estimator.estimate(...)`만 쓰니까 사용성도 유지

------

### 2-5. Guardian, Memory, 학습과의 관계

fusion을 도메인 순수 함수로 만든 뒤에도:

- Guardian이 `EstimationResult`를 보고
  - certainty가 high인 것만 Memory에 쌓고
  - Direct RAG로 승격하는 학습 로직을 돌리는 구조는 그대로 유지 가능합니다. UMIS_ARCHITECTURE_BLUEPRINT

여기서 중요한 룰은 하나입니다:

> **Guardian/Memory 쪽이 fusion 내부 디테일을 알지 말고,
>  오직 `EstimationResult`의 공개 API만 사용하게 만든다.**

- `trace`를 보고 “어떤 Stage가 기여했는지” 정도만 읽게 하고,
- 가중치 계산, 편차 계산 등의 알고리즘 디테일은 fusion 내부에만 두면
   “단일 진실의 원천 + clean architecture”를 같이 챙길 수 있습니다.

------

## 3. 실무용 체크리스트 요약

당장 손댈 때는 이 정도 순서로 하면 됩니다:

1. **StageResult / EstimationResult 도메인 모델 먼저 고정**
2. `fusion_layer.py`를 “순수 로직 + FusionPolicy 인터페이스”만 남기도록 정리
   - RAG/LLM/config 관련 import 전부 밖으로 빼기
3. `EstimatorPipeline` 같은 orchestrator를 하나 두고
   - Stage1~3 실행 + FusionPolicy 호출만 담당하게 하기
4. YAML → FusionConfig adapter를 인프라 레이어에서 구현
5. `EstimatorRAG` (Agent용 Facade)는 pipeline을 조립만 하고,
   - 외부 Agent들은 지금처럼 `estimator.estimate(...)`만 부르게 유지

여기까지 되면:

- fusion 알고리즘은 그대로 살아 있고,
- Clean architecture 입장에서는 “도메인 규칙을 표현하는 순수한 한 레이어”로 격상됩니다.

------

## 4. 사유 요약 블록

- **가정**
  - fusion을 없애려 했던 동기는 “알고리즘 문제가 아니라 의존성 엉킴” 쪽이었다.
  - UMIS의 4-Stage 구조 자체는 유지하고 싶다. UMIS_ARCHITECTURE_BLUEPRINT
- **근거**
  - 현재 설계에서 fusion은 Estimator 내부 Stage 4로 분리돼 있으나,
     RAG/LLM/runtime 설정 등과의 결합 가능성이 크다. UMIS_ARCHITECTURE_BLUEPRINT
- **추론 경로(요약)**
  - Clean architecture의 핵심은 “의존성 방향” → fusion을 도메인 순수 함수로 만들면 됨.
  - 그러려면 fusion이 외부 시스템을 모르고 Stage 결과만 다루게 해야 함.
  - 나머지 (RAG, LLM, YAML)는 infra + app 레이어로 이동.
- **대안**
  - Fusion을 Guardian 쪽으로 보내서 “메타 평가 기능”으로 취급하는 방법
  - Stage별로 이미 최종값을 내고, Fusion을 완전히 없애는 방법
     → 하지만 기존 철학(4-Stage Fusion, 단일 진실의 원천)을 해친다는 단점.
- **리스크**
  - 폴더/모듈 구조를 재조직할 때, 기존 코드와의 import 순환이 생길 수 있음.
  - FusionConfig를 잘못 설계하면 YAML 스키마 변경 시 도메인까지 영향이 새어 들어올 수 있음.
- **검증 포인트**
  - fusion 모듈을 단독으로 import 했을 때,
     RAG/LLM/Neo4j/파일 관련 의존성이 *전혀* 없어야 함.
  - Estimator 전체를 통합 테스트할 때 결과값이 리팩터링 전과 동일하거나,
     의도한 범위 내에서만 바뀌는지 확인.

------

이렇게 정리해두면 “fusion은 유지하면서, 아키텍처는 더 깔끔하게”라는 두 목표를 동시에 잡을 수 있습니다.
 나중에 fusion 알고리즘을 갈아엎어도, 나머지 시스템은 거의 손댈 필요가 없어져요.

##### 나의 말:

그렇게 하도록 하자. 이 내용을 반영해서 앞서서 이야기 했던 아래 내용을 진행하자. ---- 다음 단계에서 할 수 있는 추가 검증은: 1. v7 코드베이스에서 estimator.estimate( 호출을 전부 grep해서  - “계산용 값 / 기회 prior / 구조 비율”로 실제로 분류해보는 것. 2. 이 분류 결과를 방금 제안한 매핑 규칙(Calculator vs Estimator direct)과 비교해서  - 예외 케이스가 얼마나 나오는지 보는 것. 3. 그 결과를 토대로 v8 umis.yaml 스켈레톤에  - “migration mapping table” 섹션을 하나 추가해도 좋겠습니다. 이제 이 검증 결과를 기반으로, v8 스켈레톤에 어떤 항목을 어떻게 바꿀지를 한 덩어리씩 구체적으로 적어 나가면 됩니다.

------

###### ChatGPT의 말:

###### ChatGPT의 말:

바로 이어서 구체화하겠습니다.
 이제 “grep + 분류 결과”를 받는다고 가정하고, v8 `umis.yaml` 스켈레톤에 어떤 섹션을 어떻게 추가/수정할지를 한 덩어리씩 정리해보겠습니다. (실제 값 채우기는 나중에 하시고, 지금은 **틀**을 만드는 단계라고 보시면 됩니다.) UMIS_ARCHITECTURE_BLUEPRINT

------

## 1. v7 → v8 분류 축 정리 (개념 레벨 정의)

먼저 `umis.yaml` 안에서, v7 `estimator.estimate()` 호출을 어떻게 분류할지 “공식 어휘”를 선언하는 블록을 하나 두는 게 좋습니다.

```
migration_from_v7:
  estimator_usage_categories:
    calc_value:
      label: "계산용 값"
      description: >
        엑셀/Quantifier 계산식의 중간 입력값으로만 사용되는 추정치.
        v8에서는 Quantifier의 Assumption(ASM_*)으로 귀속하고,
        필요시 Estimator를 간접 호출하여 값을 채운다.
      default_owner_agent: quantifier
      default_artifact_types: [ASM, EST]
      default_estimator_stage_policy:
        allowed_stages: [1, 2]     # Evidence, Prior
        prefer_structural_decomposition: false

    opp_prior:
      label: "기회 prior"
      description: >
        Explorer가 OPP_* 가설을 세울 때, 시장 크기/성장률 등에 대해
        빠르게 던지는 선행 추정치. v8에서는 OPP_* + EST_*로 기록.
      default_owner_agent: explorer
      default_artifact_types: [OPP, EST]
      default_estimator_stage_policy:
        allowed_stages: [1, 2, 3, 4]
        prefer_structural_decomposition: false

    struct_ratio:
      label: "구조 비율"
      description: >
        시장 구조/구성비(예: B2B/B2C 비중, 상위10% 고객 매출 비율 등).
        v8에서는 Estimator의 Fermi(Stage 3)와 Observer/Quantifier가
        함께 사용하는 구조 파라미터로 승격.
      default_owner_agent: estimator
      default_artifact_types: [EST, CAN, PRJ, GND]
      default_estimator_stage_policy:
        allowed_stages: [1, 3, 4]
        prefer_structural_decomposition: true

    # 필요시 예외/기타 카테고리
    other:
      label: "기타/예외"
      description: >
        상기 셋 중 어디에도 깔끔히 안 들어가는 v7 호출.
        개별적으로 수동 마이그레이션 필요.
      default_owner_agent: guardian
      default_artifact_types: [MEM]
      default_estimator_stage_policy:
        allowed_stages: [1, 2, 3, 4]
        prefer_structural_decomposition: false
```

이 블록은 “grep 결과에서 나온 각 호출이 어느 바구니에 들어가는가”를 기록할 때 공통 reference가 됩니다.

------

## 2. “migration mapping table” 섹션 설계 (스키마)

이제 본론인 `migration_mapping_table`을 같은 `migration_from_v7` 아래에 붙입니다.
 **목표:** v7의 각 `estimator.estimate()` 호출이 v8에서

- 누가 책임지는지(Agent),
- 어디에 쌓이는지(ASM/EST/OPP/엑셀 시트 등),
- Estimator를 어떻게 부를지(Stage 정책, 모드)

를 **한 줄로 정리**하는 표입니다.

```
migration_from_v7:
  # 1) 위에서 정의한 categories를 재사용
  estimator_usage_categories: … (위와 동일)

  # 2) 실제 매핑 테이블 (초기에는 빈 배열로 두고, grep/분류 후 채움)
  estimator_call_mapping_table:
    - id: MIG-0001
      legacy:
        module: "umis/quantifier/ltv.py"
        function: "estimate_ltv"
        line_hint: 120        # 대략적인 라인(Hint 수준)
        prompt_summary: "한국 B2B SaaS 평균 ARPU는?"
        notes: "LTV 계산식의 입력값으로만 사용"

      classification:
        category: calc_value
        domain: "B2B_SaaS_KR"
        tags: ["arpu", "ltv", "subscription"]
        is_exception: false

      v8_plan:
        owner_agent: quantifier
        estimator_usage:
          mode: "indirect"          # quantifier -> estimator
          preferred_stages: [1, 2]
        artifacts:
          # Estimator 결과를 어디에 연결할지
          est_id: "EST-arpu-b2b-saas-kr"
          assumption_id: "ASM_001"
          excel_binding:
            workbook: "unit_economics"
            sheet: "01_ARPU"
            cell: "B7"
        remarks: >
          v8에서는 ARPU 자체는 Estimator가 추정하지만,
          LTV 계산은 Quantifier 엑셀 수식에 남기고,
          ASM_001이 EST-arpu-b2b-saas-kr을 참조하도록 설계.

    - id: MIG-0002
      legacy:
        module: "umis/explorer/opportunity.py"
        function: "estimate_opp_size"
        line_hint: 45
        prompt_summary: "피아노 구독 시장의 대략적인 크기는?"
        notes: "기회 가설의 prior로만 사용"

      classification:
        category: opp_prior
        domain: "PIANO_SUBSCRIPTION_KR"
        tags: ["sam", "subscription", "music"]
        is_exception: false

      v8_plan:
        owner_agent: explorer
        estimator_usage:
          mode: "direct"            # explorer → estimator 직접 협업
          preferred_stages: [1, 2, 3, 4]
        artifacts:
          est_id: "EST-piano-subscription-sam-kr"
          opp_id: "OPP_2025xxxx_001"
        remarks: >
          v8에서는 OPP_* 파일에 market_size_estimate 필드로
          EST ID를 명시하고, Estimator는 full 4-Stage Fusion 허용.

    - id: MIG-0003
      legacy:
        module: "umis/observer/structure.py"
        function: "estimate_segment_mix"
        line_hint: 88
        prompt_summary: "B2B/B2C 매출 비중은?"
        notes: "시장 구조 설명용 비율"

      classification:
        category: struct_ratio
        domain: "GENERIC_KR_SAAS"
        tags: ["mix", "structure", "segment"]
        is_exception: false

      v8_plan:
        owner_agent: estimator
        estimator_usage:
          mode: "direct"
          preferred_stages: [1, 3, 4]
        artifacts:
          est_id: "EST-segment-mix-b2b-b2c-kr"
          # 이 비율은 Observer/Quantifier가 공유 사용
          observer_usage: "market_reality_report.structure_section"
          quantifier_usage: "market_sizing.xlsx: shared_parameters!B5:B6"
        remarks: >
          구조 비율은 Fermi 분해의 핵심 파라미터로 간주.
          v8에서는 구조 파라미터가 여러 산출물(Observer, Quantifier)에
          재사용되도록 공용 EST ID로 승격.
```

실제 스켈레톤엔 `estimator_call_mapping_table: []` 만 넣어 두고,
 나중에 grep/분류 결과를 하나씩 추가해 나가시면 됩니다.

------

## 3. Estimator 섹션에 “v7 호환 정책” 서브섹션 추가

`umis.yaml` 안에 이미 Estimator의 역할/4-Stage 설명이 있을 텐데,
 그 블록 아래에 **v7 마이그레이션용 서브섹션**을 붙여서, 위 매핑 테이블과 연결해 줍니다. UMIS_ARCHITECTURE_BLUEPRINT

예시:

```
agents:
  estimator:
    id: estimator
    name: Fermi
    role: "값 추정 전문 (4-Stage Fusion)"
    single_source_of_truth: true
    # ... (기존 설명: Stage 1-4, Budget, Modes 등)

    legacy_migration_policy:
      from_version: "v7.11.0"
      mapping_table_ref: "migration_from_v7.estimator_call_mapping_table"
      default_behavior:
        unknown_callsite: "fail-fast"   # 매핑 없는 v7 호출은 즉시 경고
        log_namespace: "legacy.estimator.v7"
      category_overrides:
        calc_value:
          estimator_stage_policy:
            allowed_stages: [1, 2]
            forbid_recursive_decomposition: true
        opp_prior:
          estimator_stage_policy:
            allowed_stages: [1, 2, 3, 4]
            prefer_quick_answer: true
        struct_ratio:
          estimator_stage_policy:
            allowed_stages: [1, 3, 4]
            prefer_recursive_decomposition: true
```

여기서 핵심은:

- “어떤 v7 호출이 **어떤 Stage 조합으로만** 돌아가야 하는가”를
- `category` 기준으로 정리해 두고,
- 실제 호환 구현(`umis_rag/agents/estimator/compat.py`)이 이 정책을 읽어서 동작하게 만드는 것. UMIS_ARCHITECTURE_BLUEPRINT

------

## 4. Quantifier(계산기) 섹션에 “계산용 값” 핸들링 규칙 추가

v8 아키텍처에서 **계산은 Quantifier, 추정은 Estimator 단일 소스**라는 원칙이 이미 있습니다.UMIS_ARCHITECTURE_BLUEPRINT
 `umis.yaml`의 Quantifier 설명 아래에, v7→v8 관점에서 **calc_value 카테고리**를 공식 정의해 주는 부분을 추가하는 게 좋습니다.

```
agents:
  quantifier:
    id: quantifier
    name: Bill
    role: "계산 전문 (엑셀 3개 워크북, 31개 방법론)"
    # ... (기존 설명)

    value_sourcing_policy:
      single_source_of_truth: estimator
      uses_estimator_for:
        - churn_rate
        - arpu
        - take_rate
        - market_size_inputs
      legacy_migration:
        # calc_value 카테고리만 Quantifier에서 직접 관리
        from_v7_category: "calc_value"
        mapping_table_ref: "migration_from_v7.estimator_call_mapping_table"
        default_binding:
          assumption_prefix: "ASM_"
          estimation_prefix: "EST-"
          excel_workbooks:
            - "market_sizing"
            - "unit_economics"
            - "financial_projection"
        rules:
          - id: "Q1"
            description: >
              v7에서 LTV 계산식에만 사용되던 추정값은
              v8에서는 ASM_*로 정의하고, ASM_* → EST_* 참조로 연결한다.
          - id: "Q2"
            description: >
              Estimator의 Stage 3(Fermi) 결과를 직접 계산식에 섞지 말고,
              항상 scalar 값만 ASM_*로 받아서 사용한다.
```

이렇게 써 두면,

- grep/분류 결과에서 `category: calc_value`로 들어간 항목들만
- 자연스럽게 “Quantifier 책임 + Estimator 간접 호출 + 엑셀 바인딩” 패턴으로 정리됩니다.

------

## 5. Explorer / Observer 쪽에 “기회 prior / 구조 비율” 연결

### 5-1. Explorer (opp_prior)

Explorer 설명 안에, `opp_prior` 카테고리를 어떻게 OPP_*와 연결할지 명시합니다. UMIS_ARCHITECTURE_BLUEPRINT

```
agents:
  explorer:
    id: explorer
    name: Steve
    role: "기회 발굴 (RAG + Graph + Estimator 협업)"
    # ... (기존 설명)

    opportunity_prior_policy:
      from_v7_category: "opp_prior"
      mapping_table_ref: "migration_from_v7.estimator_call_mapping_table"
      default_estimation_link:
        opp_field: "market_size_estimate"
        est_id_prefix: "EST-opp-"
      rules:
        - id: "E1"
          description: >
            v7의 기회 prior 추정은 v8에서
            OPP_*.md의 market_size_estimate 필드에 EST-* ID로 연결한다.
        - id: "E2"
          description: >
            동일 도메인/유사 질문의 prior는 단일 EST-*로 통합하고,
            certainty가 높으면 Direct RAG로 승격한다.
```

### 5-2. Observer (struct_ratio)

Observer는 시장 구조/가치사슬 분석에 집중하는 Agent이므로, `struct_ratio` 카테고리와 가장 잘 맞습니다. UMIS_ARCHITECTURE_BLUEPRINT

```
agents:
  observer:
    id: observer
    name: Albert
    role: "시장 구조 분석"
    # ... (기존 설명)

    structural_ratio_policy:
      from_v7_category: "struct_ratio"
      mapping_table_ref: "migration_from_v7.estimator_call_mapping_table"
      usage:
        report_field: "market_reality_report.structure"
        share_with_agents: [quantifier, guardian]
      rules:
        - id: "O1"
          description: >
            v7에서 시장/세그먼트 구성비를 추정하던 호출은
            v8에서 EST-* 구조 비율로 승격하여,
            Observer 보고서와 Quantifier 엑셀에서 공통으로 참조한다.
        - id: "O2"
          description: >
            구조 비율은 Knowledge Graph 패턴의 속성으로도 저장할 수 있으며,
            반복 사용되는 경우 Canonical/Projected Index에 반영한다.
```

------

## 6. Guardian 쪽에 “예외 케이스 집계” 담당 추가

마지막으로, `category: other` 또는 `classification.is_exception: true` 같은 케이스를 Guardian이 관리하도록, Guardian 섹션에 간단한 정책을 붙입니다.UMIS_ARCHITECTURE_BLUEPRINT

```
agents:
  guardian:
    id: guardian
    name: Stewart
    role: "프로세스/Meta-RAG 관리"
    # ... (기존 설명)

    migration_exception_policy:
      mapping_table_ref: "migration_from_v7.estimator_call_mapping_table"
      track_fields:
        - id
        - legacy.module
        - legacy.function
        - classification.category
        - classification.is_exception
      memory_artifact:
        type: "MEM-query"
        prefix: "MEM-migration-exception-"
      rules:
        - id: "G1"
          description: >
            classification.is_exception = true 인 v7 호출은
            Guardian이 MEM-*로 기록하고,
            세션 종료 시 SESSION_CLOSURE_PROTOCOL에 따라 별도 보고한다.
        - id: "G2"
          description: >
            예외 케이스 수가 threshold 이상이면,
            v8 스키마 자체를 재검토하는 trigger로 사용한다.
```

이렇게 하면 “grep + 분류”를 해본 결과,
 생각보다 이상한 호출이 많을 경우 Guardian이 공식 채널로 문제를 끌어올릴 수 있습니다.

------

## 7. 정리: 지금 단계에서 실제로 해두면 좋은 것

1. **`umis.yaml`에 `migration_from_v7` 토막 추가**
   - `estimator_usage_categories` 정의
   - `estimator_call_mapping_table: []` 빈 배열로 선언
2. **각 Agent 섹션에 3개 카테고리의 연결 규칙 서브섹션 추가**
   - Estimator: category별 Stage/모드 정책
   - Quantifier: `calc_value` 처리 규칙
   - Explorer: `opp_prior` → OPP_* 연결
   - Observer: `struct_ratio` → 구조 파라미터 승격
   - Guardian: 예외 케이스 집계
3. **나중에 grep 결과가 나오면**
   - 각 `estimator.estimate()` 호출을 3+1 카테고리 중 하나로 붙이고
   - `estimator_call_mapping_table`에 한 줄씩 채워 넣으면
   - 코드/엑셀/문서/ID Namespace(EST/ASM/OPP 등)이 전부 한 번에 정렬됩니다. UMIS_ARCHITECTURE_BLUEPRINT

이렇게 해두면, v7 코드를 완전히 지우더라도
 “이 추정치는 원래 어디서 어떻게 쓰이던 놈이었지?”를 언제든 되추적할 수 있는 구조가 됩니다.

------

## [사유 공개]

- **가정**
  - v8의 `umis.yaml`은 이미 6-Agent 구조, Estimator 4-Stage, ID Namespace(SRC/EST/ASM/OPP 등)를 설명하고 있으며, 이를 깨지 않는 선에서 “마이그레이션 전용 섹션”을 추가할 수 있다고 가정했습니다. UMIS_ARCHITECTURE_BLUEPRINT
  - v7 `estimator.estimate()` 호출은 크게 “계산용 값 / 기회 prior / 구조 비율 / 기타” 네 그룹으로 나뉠 수 있다고 가정했습니다.
- **근거**
  - UMIS 설계에서 Estimator는 “값 추정의 단일 진실의 원천”, Quantifier는 “계산 담당”으로 역할이 분리되어 있고, Explorer/Observer/Guardian의 책임도 이미 문서화되어 있습니다.UMIS_ARCHITECTURE_BLUEPRINT
  - ID Namespace(EST/ASM/OPP 등)가 존재하므로, v7 호출을 이 ID 체계 위에 매핑하는 것이 자연스러운 마이그레이션 경로입니다.UMIS_ARCHITECTURE_BLUEPRINT
- **추론 경로**
  1. v7 → v8 마이그레이션에서 가장 중요한 것은 “각 호출의 **의도/맥락**을 잃지 않는 것”입니다.
  2. 의도를 보존하려면, 먼저 공통 분류 축(계산용 값 / 기회 prior / 구조 비율)을 정의해야 합니다.
  3. 그 다음, 이 분류 축을 기준으로
     - 어떤 Agent가 책임을 질지,
     - 어떤 아티팩트(EST/ASM/OPP/엑셀)에 귀속될지,
     - Estimator는 어느 Stage를 주로 사용할지
        를 표 형태로 연결하면 재구현 시 실수가 줄어듭니다.
  4. 이 역할/아티팩트/Stage 정보가 모두 만나는 자리가 바로 `umis.yaml`이므로, 여기에 `migration_from_v7`와 per-Agent 정책을 넣는 것이 합리적이라고 판단했습니다.
- **대안**
  - `umis.yaml`에 테이블을 두지 않고, `config/migration/v7_estimator_calls.yaml` 같은 별도 파일에 전부 몰아 넣고, `umis.yaml`에서는 그 파일 경로만 가리키도록 만드는 방법도 있습니다.
  - 여기는 “v8 스켈레톤에서 어떤 블록을 만들지”가 초점이므로, 일단 스키마를 `umis.yaml` 안에 먼저 선언하는 쪽을 택했습니다.
- **리스크 / 불확실성**
  - 실제 v7 grep 결과를 보지 않은 상태라,
    - 카테고리 3+1개로 충분한지,
    - `mapping_table`의 필드가 과하거나 부족한지
       는 일부 불확실합니다.
  - 특히, 같은 질문을 여러 곳에서 다르게 사용하는 경우(예: ARPU가 “계산용 값”이면서 동시에 “기회 prior” 역할도 하는 상황)는 추가 서브카테고리나 플래그가 필요할 수 있습니다.
- **검증 아이디어**
  - v7 전체 `estimator.estimate()` 호출을 실제로 grep한 뒤, 샘플 50~100개 정도를 손으로 분류해 보면서
    - `category`가 모자라지 않는지,
    - `v8_plan.artifacts`에 꼭 필요한 필드가 빠진 것은 없는지
       를 점검하면 됩니다.
  - 예외 케이스 비율(예: `is_exception: true`가 5%를 넘는지)을 Guardian 쪽에서 자동 집계하게 하면, 스키마 설계가 적절했는지도 정량적으로 피드백 받을 수 있습니다.

이제 실제 grep/분류를 하신 다음에는, 위 스켈레톤에 한 줄씩 채워 넣으면서 “v7 의도를 v8 구조에 안착시키는 작업”만 남습니다.

