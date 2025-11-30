# 🎭 UMIS v8.0.0 Agent Roles & Workflow Blueprint

**문서 버전**: 1.0  
**작성일**: 2025-11-28  
**상태**: Design Review  

---

## 📋 목차

1. [Agent 역할 정의](#agent-역할-정의)
2. [Tier 1: Business Analysis Layer](#tier-1-business-analysis-layer)
3. [Tier 2: Evidence Generation Layer](#tier-2-evidence-generation-layer)
4. [Tier 3: Supervision Layer](#tier-3-supervision-layer)
5. [Agent 간 협업 패턴](#agent-간-협업-패턴)
6. [Workflow 시나리오](#workflow-시나리오)
7. [시퀀스 다이어그램](#시퀀스-다이어그램)

---

## 🎯 Agent 역할 정의

### **v8.0.0 Agent 전체 맵**

```yaml
umis_v8_agents:
  
  tier_1_business_analysis:
    observer:
      name: Albert
      role: Market Structure + Sizing Analyst
      type: Domain Agent
      responsibility: 완전한 시장 분석
      output: Market Reality Report (구조 + 규모)
      orchestration: Calculator, Validator, Estimator
    
    explorer:
      name: Steve
      role: Opportunity Scout
      type: Domain Agent
      responsibility: 검증된 기회 발견
      output: Validated Opportunity Portfolio
      uses: Calculator (기회 크기 계산)
  
  tier_2_evidence_generation:
    evidence_collector:
      type: Infrastructure
      role: Fast Path 데이터 확인
      speed: <1초
      sources: [Literal, RAG, Cache, Guardrail]
    
    validator:
      name: Rachel
      role: Active Data Hunter
      type: Support Agent
      responsibility: 적극적 데이터 탐색
      sources: [DART, KOSIS, Web, Creative]
    
    calculator:
      type: Tool
      role: Formula Designer & Convergence Engine
      modes: [Exact, Convergence]
      responsibility: 공식 설계, 계산, 수렴
    
    estimator:
      name: Fermi
      role: Pure Guesser (Last Resort)
      type: Support Agent
      responsibility: LLM 내적 확신 "찍기"
      method: Generative Prior only
  
  tier_3_supervision:
    guardian:
      name: Stewart
      role: Process Overseer
      type: Supervision Agent
      responsibility: 프로세스 감독, 품질 관리
```

---

## 🔷 Tier 1: Business Analysis Layer

### **1. Observer (Albert) - v8.0.0**

#### **1.1 역할 정의**

```yaml
observer_v8:
  name: Albert
  classification: Domain Agent (Tier 1)
  
  role: 완전한 시장 분석가
  
  tagline: "시장의 구조와 규모를 완전히 파악하는 전문가"
  
  responsibility:
    primary: 시장 구조 + 규모 통합 분석
    deliverable: Market Reality Report (완전판)
    
  capabilities:
    structure_analysis:
      - 가치 교환 구조
      - 거래 메커니즘
      - 시장 집중도
      - 플랫폼 파워
      - 규제 환경
    
    market_sizing:  # ⭐ v8.0.0 신규
      - TAM/SAM/SOM 계산
      - 세그먼트별 규모
      - 주요 플레이어 매출/점유율
      - 성장률 및 트렌드
      - 경제성 분석
    
    orchestration:
      - Calculator 공식 선택
      - Validator 데이터 요청
      - 4가지 방법 수렴 판단
      - 최종 보고서 작성
  
  characteristics:
    - 비즈니스 판단 (Domain-centric)
    - 오케스트레이션 (다른 Agent 활용)
    - 완전성 추구 (구조 + 규모)
```

#### **1.2 Workflow Blueprint**

```yaml
observer_workflow:
  
  phase_1_structure_analysis:
    duration: 1-2시간
    
    step_1_initial_research:
      action: Evidence Collection으로 기본 정보 수집
      tools: [Evidence Collector, RAG]
      output: 초기 구조 스케치
    
    step_2_validator_search:
      action: Validator에게 상세 데이터 요청
      queries:
        - "시장 참여자 목록"
        - "가치사슬 단계"
        - "주요 기업 정보"
      output: 확정 데이터 세트
    
    step_3_structure_synthesis:
      action: 구조 분석 및 정리
      output: 시장 구조 섹션 (정성)
  
  phase_2_market_sizing:  # ⭐ v8.0.0 신규
    duration: 2-3시간
    
    step_1_method_selection:
      action: SAM 계산 방법 4가지 선택
      methods:
        - Top-down: TAM에서 좁히기
        - Bottom-up: 구성 요소 쌓기
        - Proxy: 유사 시장 비교
        - Competitor: 경쟁사 매출 역산
      
      decision_factors:
        - 데이터 가용성
        - 시장 특성
        - 신뢰도 목표
    
    step_2_calculator_delegation:
      action: Calculator에게 각 방법 계산 위임
      
      for_each_method:
        input:
          - method: "Bottom-up"
          - target: "콘서트 시장 SAM"
          - domain: "Entertainment"
          - region: "Korea"
        
        calculator_process:
          - 공식 생성
          - 4-Tier Pipeline으로 변수 수집
          - 계산 수행
          - 신뢰도 평가
        
        output:
          - value: 1.95조
          - range: [1.7조, 2.2조]
          - evidence_ratio: 0.33
          - reliability: ⭐⭐⭐⭐
    
    step_3_convergence_analysis:
      action: 4가지 방법 결과 비교
      
      results:
        - Top-down: 1.5조
        - Bottom-up: 1.95조
        - Proxy: 0.97조
        - Competitor: 0.97조
      
      analysis:
        mean: 1.35조
        cv: 0.35 (35%)
        status: ACCEPTABLE
      
      observer_judgment:
        decision: "Bottom-up 과대 추정 가능성"
        weight_adjustment:
          - Top-down: 0.25
          - Bottom-up: 0.15 (하향)
          - Proxy: 0.30
          - Competitor: 0.30
        
        final_sam: 1.2조
        range: [1.0조, 1.5조]
        confidence: ±20%
    
    step_4_player_analysis:
      action: 주요 플레이어 매출/점유율 계산
      
      for_each_player:
        data_source: Validator (DART)
        calculation: Calculator (점유율 공식)
        
      output:
        - 하이브: 2.18조 (시장정의 재검토 필요)
        - SM: 0.90조
        - ...
  
  phase_3_integration:
    duration: 30분
    
    step_1_combine:
      action: 구조 + 규모 섹션 통합
    
    step_2_reliability_matrix:
      action: 모든 데이터의 출처 및 신뢰도 명시
      
      format:
        - ✅ VERIFIED (공식 통계)
        - ⭐⭐⭐⭐ CALCULATED (Evidence 기반)
        - ⭐⭐⭐ ESTIMATED (일부 추정)
    
    step_3_final_report:
      output: Market Reality Report
      
      structure:
        section_1_executive_summary:
          - 시장 규모 요약
          - 주요 발견사항
        
        section_2_market_structure:
          - 가치사슬
          - 거래 메커니즘
          - 시장 집중도
        
        section_3_market_sizing:
          - TAM/SAM/SOM
          - 계산 방법론
          - 신뢰도 분석
        
        section_4_key_players:
          - 주요 기업 분석
          - 시장 점유율
        
        section_5_appendix:
          - 데이터 출처
          - 계산 상세
          - 한계점
```

#### **1.3 입출력 명세**

```yaml
observer_interface:
  
  input:
    domain: string
    region: string
    scope: ["structure_only", "sizing_only", "complete"]
    depth: ["light", "medium", "deep"]
  
  output:
    market_reality_report:
      structure:
        value_chain: dict
        transaction_mechanism: dict
        concentration: dict
        key_players: list
      
      sizing:
        tam: float
        sam: float
        som: float
        segments: list[dict]
        growth_rate: float
      
      reliability:
        overall: string
        data_sources: list
        evidence_ratio: float
      
      metadata:
        created_at: datetime
        version: string
        completeness: "100%"
```

---

### **2. Explorer (Steve) - v8.0.0**

#### **2.1 역할 정의**

```yaml
explorer_v8:
  name: Steve
  classification: Domain Agent (Tier 1)
  
  role: 기회 발견 및 검증
  
  responsibility:
    primary: 검증된 기회 포트폴리오 제공
    input: Observer의 Market Reality Report
    
  capabilities:
    opportunity_discovery:
      - 시장 비효율성 탐지
      - 미충족 니즈 발견
      - 구조적 공백 식별
    
    opportunity_sizing:  # ⭐ Calculator 사용
      - 기회별 시장 크기 계산
      - 잠재 매출 추정
      - ROI 분석
    
    validation:
      - Albert, Bill, Rachel 검증 필수
```

#### **2.2 Workflow (간략)**

```yaml
explorer_workflow:
  step_1: Albert의 Market Reality Report 입력
  step_2: 비효율성/공백 탐지
  step_3: Calculator로 기회 크기 계산
  step_4: Validator로 가설 검증
  step_5: 검증된 기회 포트폴리오 출력
```

---

## 🔶 Tier 2: Evidence Generation Layer

### **3. Evidence Collector - v8.0.0**

#### **3.1 역할 정의**

```yaml
evidence_collector_v8:
  classification: Infrastructure (Tier 2)
  
  role: Fast Path 데이터 확인
  
  responsibility:
    primary: 캐시된 데이터 빠른 확인
    speed: <1초
    coverage: ~60%
  
  components:
    literal:
      source: 프로젝트 컨텍스트
      example: "이 프로젝트에서 명시한 값"
      confidence: 1.0
    
    direct_rag:
      source: 학습된 규칙
      criteria: confidence ≥ 0.80
      confidence: 0.95+
    
    validator_cache:  # ⭐ Passive
      source: 과거 Validator 탐색 결과
      note: 새 탐색 안함
      confidence: 1.0
    
    guardrail:
      source: 논리적/경험적 제약
      output:
        - hard_bounds: [min, max]
        - soft_hints: 경험적 힌트
```

#### **3.2 Workflow**

```yaml
evidence_collector_workflow:
  step_1_literal_check:
    duration: <10ms
    action: 프로젝트 데이터 확인
    if_found: 즉시 반환 (Fast Path ⚡)
  
  step_2_rag_search:
    duration: <100ms
    action: 학습된 규칙 검색
    if_found: 반환
  
  step_3_cache_check:
    duration: <100ms
    action: Validator 캐시 조회
    if_found: 반환
  
  step_4_guardrail:
    duration: <100ms
    action: 논리적 제약 수집
    always_run: true
    output: bounds, hints
  
  total_duration: <300ms
```

---

### **4. Validator (Rachel) - v8.0.0**

#### **4.1 역할 정의**

```yaml
validator_v8:
  name: Rachel
  classification: Support Agent (Tier 2)
  
  role: Active Data Hunter
  
  tagline: "데이터를 끝까지 찾아내는 탐정"
  
  responsibility:
    primary: 적극적 데이터 탐색
    speed: 5-30초
    coverage: +25% (Tier 1 후)
  
  capabilities:
    api_search:
      - DART (전자공시)
      - KOSIS (통계청)
    
    web_search:
      - Google Custom Search
      - 공식 리포트 다운로드
    
    creative_search:
      - 검색어 확장
      - 사용자 여정 기반
      - SEO 역추적
  
  characteristics:
    - Active (적극적)
    - Persistent (끈질김)
    - Creative (창의적)
```

#### **4.2 Workflow**

```yaml
validator_workflow:
  
  step_1_dart_search:
    duration: 3-5초
    action: DART API 호출
    
    process:
      - get_corp_code(company_name)
      - get_financials(corp_code, year)
      - extract_relevant_data()
    
    if_found: 반환 + 캐시 저장
    if_not_found: → step_2
  
  step_2_kosis_search:
    duration: 3-5초
    action: KOSIS API 호출
    
    if_found: 반환 + 캐시 저장
    if_not_found: → step_3
  
  step_3_web_search:
    duration: 5-10초
    action: Google Custom Search
    
    queries:
      - 공식 통계 키워드
      - 업계 리포트 키워드
    
    if_found: 반환 + 캐시 저장
    if_not_found: → step_4
  
  step_4_creative_search:
    duration: 10-20초
    action: 검색어 확장 및 재탐색
    
    expansion_strategies:
      - 초보자 관점: "공연" → "콘서트 가는 법"
      - 구매 의도: "티켓 구매"
      - 전문 용어: "공연산업 통계"
    
    if_found: 반환 + 캐시 저장
    if_not_found: return None
  
  step_5_cache_update:
    action: 결과를 Evidence Collector에 저장
    ttl: 7일
```

---

### **5. Calculator - v8.0.0**

#### **5.1 역할 정의**

```yaml
calculator_v8:
  classification: Tool (Tier 2)
  
  role: Formula Designer & Convergence Engine
  
  tagline: "증거로 계산 가능한 최적 공식을 찾는 엔진"
  
  responsibility:
    primary: 공식 설계, 계산, 수렴 분석
    
  modes:
    mode_1_exact:
      when: 모든 변수 Tier 1-2로 확정
      output: 정확한 값 (⭐⭐⭐⭐⭐)
    
    mode_2_convergence:
      when: 일부 변수 Tier 3-4 필요
      output: 추정값 + 범위 (⭐⭐⭐⭐)
  
  capabilities:
    formula_generation:
      - 여러 접근의 공식 생성 (2-4개)
      - Evidence 커버리지 평가
      - 최적 공식 선택
    
    fermi_decomposition:
      - 창의적 분해
      - 재귀적 탐색 (max_depth=2)
      - 하위 변수 수집
    
    convergence_analysis:
      - CV (Coefficient of Variation)
      - Outlier 탐지
      - 가중 평균 합성
  
  characteristics:
    - Stateless (상태 없음)
    - Pure function (순수 함수)
    - Reusable (공통 도구)
```

#### **5.2 Workflow: Mode 1 (Exact)**

```yaml
calculator_mode_1_exact:
  
  step_1_formula_selection:
    action: 단일 최적 공식 선택
    example: "점유율 = 기업매출 ÷ 전체시장"
  
  step_2_variable_collection:
    for_each_variable:
      tier_1: Evidence Collection
      tier_2: Validator Active Search
      
      if_not_found: raise Error "Cannot use exact mode"
  
  step_3_calculation:
    action: 공식 적용
    example: 2.18조 ÷ 1.8조 = 121%
  
  step_4_validation:
    check: 결과 논리성 검증
    example: "121% 불가능 → 재검토"
  
  output:
    value: 계산값
    reliability: ⭐⭐⭐⭐⭐
    confidence: 1.0
```

#### **5.3 Workflow: Mode 2 (Convergence)**

```yaml
calculator_mode_2_convergence:
  
  step_1_multi_formula_generation:
    action: 여러 공식 생성 (2-4개)
    
    example:
      formulas:
        - Bottom-up: 거래수 × 금액
        - Venue: 공연장 × 가동
        - Competitor: 매출 ÷ 점유율
        - Proxy: 일본 × 조정
  
  step_2_independent_calculation:
    for_each_formula:
      
      sub_step_1_variable_collection:
        for_each_variable:
          tier_1: Evidence Collection
          tier_2: Validator Active Search
          tier_3: Calculator Fermi
          tier_4: Estimator Prior
        
        collect_all_variables: true
      
      sub_step_2_calculation:
        apply_formula: true
        
      sub_step_3_reliability_assessment:
        evidence_ratio: count(tier_1+2) / total
        reliability: based_on_evidence_ratio
    
    results:
      - formula: "Bottom-up"
        value: 1.95조
        evidence_ratio: 0.33
        reliability: ⭐⭐⭐⭐
      
      - formula: "Proxy"
        value: 0.97조
        evidence_ratio: 0.67
        reliability: ⭐⭐⭐⭐
  
  step_3_convergence_analysis:
    metrics:
      mean: 1.35조
      std: 0.47조
      cv: 0.35 (35%)
    
    status: ACCEPTABLE (CV < 0.5)
    
    outlier_detection:
      threshold: z_score > 2
      outliers: [Bottom-up (z=2.1)]
  
  step_4_weighted_synthesis:
    weights:
      - Bottom-up: 0.15 (outlier 페널티)
      - Venue: 0.20
      - Competitor: 0.30
      - Proxy: 0.35 (highest evidence_ratio)
    
    weighted_avg: 1.2조
    range: [1.0조, 1.5조]
  
  output:
    value: 1.2조
    range: [1.0조, 1.5조]
    confidence: ±20%
    reliability: ⭐⭐⭐⭐
    evidence_ratio: 0.50
    
    method_breakdown:
      - Bottom-up: 1.95조 (weight: 0.15)
      - Proxy: 0.97조 (weight: 0.35)
      - ...
```

#### **5.4 Workflow: Fermi Decomposition**

```yaml
calculator_fermi:
  
  trigger: Tier 1-2 실패 시
  max_depth: 2 (재귀 제한)
  
  step_1_decomposition:
    input: "연간 공연 횟수"
    
    formulas_generated:
      option_1: 공연장수 × 연간가동일
      option_2: 아티스트수 × 평균공연수
      option_3: 티켓판매건수 ÷ 평균관객
  
  step_2_coverage_evaluation:
    for_each_formula:
      check_variables_in_tier_1_2: true
      
      coverage:
        - option_1: 1/2 = 50%
        - option_2: 0/2 = 0%
        - option_3: 0/2 = 0%
    
    selected: option_1 (highest coverage)
  
  step_3_recursive_collection:
    for_each_variable:
      공연장수:
        tier_2: ✅ Validator (150개)
      
      가동일:
        tier_1_2: ❌
        tier_3_fermi: depth=1, 더 분해 시도
          formula: 365일 × 가동률
          
          variables:
            365일: ✅ Literal
            가동률:
              tier_4: ✅ Estimator (0.27)
        
        result: 365 × 0.27 = 99일
  
  step_4_calculation:
    formula: 150개 × 99일
    result: 14,850회
  
  output:
    value: 14,850회
    reliability: ⭐⭐⭐⭐
    decomposition:
      - 공연장수: 150개 (Validator, ⭐⭐⭐⭐⭐)
      - 가동일: 99일 (Fermi, ⭐⭐⭐⭐)
        - 365일: Literal (⭐⭐⭐⭐⭐)
        - 가동률: 0.27 (Estimator, ⭐⭐⭐)
```

---

### **6. Estimator (Fermi) - v8.0.0**

#### **6.1 역할 정의**

```yaml
estimator_v8:
  name: Fermi
  classification: Support Agent (Tier 2)
  
  role: Pure Guesser (Last Resort)
  
  tagline: "내적 확신으로 '찍는' 최후의 전문가"
  
  simplification:
    removed:
      - Stage 3 (Fermi) → Calculator로 이동
      - Stage 4 (Fusion) → 불필요
    
    remaining:
      - Stage 1 (Evidence) → Fast Path
      - Stage 2 (Prior) → 유일한 추정
  
  responsibility:
    primary: LLM 내적 확신 기반 "찍기"
    when: Tier 1-2-3 모두 실패
    reliability: ⭐⭐⭐ (최저)
  
  method:
    generative_prior:
      input:
        - question
        - hard_bounds (Guardrail)
        - soft_hints
        - context
      
      llm_prompt: |
        "당신의 내적 확신에 기반해 값을 추정하세요.
         정확한 근거가 없어도 괜찮습니다.
         상식적으로 가장 그럴듯한 값을 제시하세요."
      
      output:
        - value
        - range
        - certainty (high/medium/low)
        - reasoning
```

#### **6.2 Workflow**

```yaml
estimator_workflow:
  
  step_1_evidence_check:
    action: Fast Path 확인
    duration: <1초
    
    if_found: 즉시 반환 (거의 호출 안됨)
    if_not_found: → step_2
  
  step_2_generative_prior:
    action: LLM "찍기"
    duration: 3초
    
    input_preparation:
      question: "한국/일본 문화조정계수는?"
      hard_bounds: [0.3, 1.5]
      soft_hints: "인구 비율, 한류 강세"
      context:
        - 일본 시장: 3,500억엔
        - 한국 인구: 일본의 40%
    
    llm_execution:
      model: gpt-4o-mini
      temperature: 0.7
      
      prompt: |
        당신은 시장 분석 전문가입니다.
        다음 질문에 답하세요:
        
        질문: {question}
        제약: {hard_bounds}
        힌트: {soft_hints}
        맥락: {context}
        
        요구사항:
        1. 가장 그럴듯한 값을 제시
        2. 범위 [최소, 최대] 제공
        3. 내적 확신도 (high/medium/low)
        4. 추정 근거 설명
    
    llm_response:
      value: 0.75
      range: [0.65, 0.85]
      certainty: medium
      reasoning: |
        "인구 비율 40%를 기준으로
         한류 보정 +80%를 반영하면
         0.40 × 1.8 ≈ 0.72-0.78"
  
  output:
    value: 0.75
    range: [0.65, 0.85]
    reliability: ⭐⭐⭐
    source: "Estimator (Prior)"
    certainty: "medium"
```

---

## 🔗 Agent 간 협업 패턴

### **Pattern 1: Observer → Calculator**

```yaml
observer_calculator_collaboration:
  
  scenario: Observer가 SAM 계산 필요
  
  observer_action:
    step_1: SAM 방법 4가지 선택
    step_2: Calculator에게 각각 위임
    
    delegation:
      calculator.calculate(
        target="콘서트 SAM (Bottom-up)",
        domain="Entertainment",
        region="Korea",
        mode="convergence"
      )
  
  calculator_action:
    - 공식 생성
    - 4-Tier로 변수 수집
    - 계산 수행
    - 결과 반환
  
  observer_receives:
    - Bottom-up: 1.95조
    - Venue: 1.8조
    - Competitor: 0.97조
    - Proxy: 0.97조
  
  observer_final_action:
    - 4가지 결과 수렴 분석
    - 가중치 조정 (비즈니스 판단)
    - 최종 SAM 결정: 1.2조 ±20%
```

### **Pattern 2: Calculator → Validator → Estimator**

```yaml
calculator_cascade:
  
  scenario: Calculator가 변수 수집
  
  variable: "평균 관객 수"
  
  tier_1_evidence:
    action: Evidence Collection
    result: ❌ None
  
  tier_2_validator:
    action: Validator.active_search("평균 관객 수")
    
    validator_process:
      - DART: ❌
      - KOSIS: ❌
      - Web: ❌
      - Creative: ❌
    
    result: None
  
  tier_3_calculator_fermi:
    action: Calculator.fermi_decompose("평균 관객 수")
    
    decomposition: 공연장 평균 좌석 × 객석점유율
    
    variables:
      공연장좌석:
        tier_2: ✅ 2,500석 (Validator)
      객석점유율:
        tier_4: ✅ 0.85 (Estimator)
    
    result: 2,500 × 0.85 = 2,125명
  
  tier_4_estimator:
    action: Estimator.estimate("객석점유율")
    
    result:
      value: 0.85
      range: [0.75, 0.95]
      certainty: medium
  
  final_variable:
    value: 2,125명
    tier: 3 (Fermi)
    reliability: ⭐⭐⭐⭐
    sub_variables:
      - 좌석: Validator (⭐⭐⭐⭐⭐)
      - 점유율: Estimator (⭐⭐⭐)
```

### **Pattern 3: Observer → Validator (Direct)**

```yaml
observer_validator_direct:
  
  scenario: Observer가 구조 분석 중 데이터 필요
  
  observer_request:
    query: "국내 주요 공연장 목록"
    domain: "Entertainment"
    region: "Korea"
  
  validator_search:
    dart: ❌
    kosis: ❌
    web: ✅
      source: "한국공연예술센터 협회"
      data: [잠실, KSPO돔, 예스24라이브홀, ...]
      count: 150개
  
  validator_return:
    data: 공연장 목록 (150개)
    source: "한국공연예술센터"
    reliability: ⭐⭐⭐⭐⭐
    
  observer_uses:
    - 시장 구조 섹션에 포함
    - Calculator Fermi에 활용 (공연장수 변수)
```

---

## 🎬 Workflow 시나리오

### **Scenario 1: 완전한 시장 분석 (Full Analysis)**

```yaml
scenario_full_market_analysis:
  
  user_request: "국내 콘서트 시장을 완전히 분석해줘"
  
  assigned_agent: Observer (Albert)
  
  workflow:
    
    # Phase 1: 구조 분석
    phase_1_structure:
      duration: 1.5시간
      
      step_1_1: Evidence Collection으로 기본 정보
        result: 공연 유형, 주요 기업 리스트 (RAG)
      
      step_1_2: Validator로 상세 정보 수집
        queries:
          - "국내 공연장 목록"
          - "주요 엔터 기업 매출 (DART)"
          - "공연산업 통계 (KOSIS)"
        
        results:
          - 공연장 150개 (Web)
          - 하이브 2.18조, SM 0.90조 (DART)
          - 전체 시장 1.8조 (KOSIS)
      
      step_1_3: 구조 분석 작성
        output:
          - 가치사슬: 기획사 → 공연장 → 플랫폼 → 관객
          - 거래 구조: 선예매 중심, 좌석등급제
          - 시장 집중도: 과점 (상위 3개사 58%)
    
    # Phase 2: 규모 계산
    phase_2_sizing:
      duration: 2.5시간
      
      step_2_1: 방법 4가지 선택
        methods: [Top-down, Bottom-up, Proxy, Competitor]
      
      step_2_2: Calculator에게 각각 위임
        
        method_1_topdown:
          calculator_mode: convergence
          formula: 문화시장 × 공연비중 × 콘서트비중
          
          variables:
            문화시장: 60조 (Validator, KOSIS)
            공연비중: 0.03 (Estimator)
            콘서트비중: 0.40 (Estimator)
          
          result: 0.72조
          evidence_ratio: 0.33
        
        method_2_bottomup:
          formula: 공연횟수 × 관객 × 티켓가
          
          variables:
            공연횟수: 8,000회 (Fermi)
            관객: 2,125명 (Fermi)
            티켓가: 120,000원 (Validator)
          
          result: 2.04조
          evidence_ratio: 0.33
        
        method_3_proxy:
          formula: 일본시장 × GDP비율 × 문화조정
          
          variables:
            일본: 3,500억엔 (Evidence, RAG)
            GDP: 0.35 (Evidence, RAG)
            조정: 0.75 (Estimator)
          
          result: 0.92조
          evidence_ratio: 0.67
        
        method_4_competitor:
          formula: Top5매출 ÷ 점유율
          
          variables:
            Top5: 5.8조 (Validator, DART)
            점유율: 0.60 (Estimator)
          
          result: 9.67조 (outlier!)
          evidence_ratio: 0.50
      
      step_2_3: Observer 수렴 분석
        results: [0.72조, 2.04조, 0.92조, 9.67조]
        
        analysis:
          mean: 3.34조
          cv: 1.12 (112%) → DIVERGED!
          outlier: Competitor (z=3.2)
        
        observer_diagnosis:
          issue: "Competitor 방법 문제"
          reason: |
            "Top5 매출(5.8조)이 전체 시장(1.8조)보다 큼
             → 매출에 해외/음반 포함된 것으로 추정
             → 콘서트만 분리 불가"
          
          action: Competitor 제외
        
        re_analysis:
          results: [0.72조, 2.04조, 0.92조]
          mean: 1.23조
          cv: 0.52 (52%) → ACCEPTABLE
          
        weights:
          - Top-down: 0.25
          - Bottom-up: 0.20 (과대 가능성)
          - Proxy: 0.55 (highest evidence)
        
        final_sam: 1.05조
        range: [0.85조, 1.25조]
        confidence: ±19%
    
    # Phase 3: 통합
    phase_3_integration:
      duration: 0.5시간
      
      output: Market Reality Report
        
        section_1_summary:
          - 시장 규모: 1.05조 (±19%)
          - 시장 구조: 과점, 플랫폼 중심
          - 신뢰도: MEDIUM-HIGH (⭐⭐⭐⭐)
        
        section_2_structure:
          - 가치사슬 상세
          - 거래 메커니즘
          - 주요 플레이어
        
        section_3_sizing:
          - SAM: 1.05조
          - 계산 방법: 3가지 수렴
          - 신뢰도: Evidence 43%
        
        section_4_appendix:
          - 데이터 출처 전체
          - Competitor 방법 제외 사유
          - 한계점 및 개선 방향
  
  total_duration: 4.5시간
  reliability: ⭐⭐⭐⭐ (MEDIUM-HIGH)
```

---

### **Scenario 2: 빠른 추정 (Quick Estimate)**

```yaml
scenario_quick_estimate:
  
  user_request: "콘서트 평균 관객수 빨리 알려줘"
  
  assigned_tool: Calculator (단일 계산)
  
  workflow:
    
    step_1_direct_search:
      tier_1: Evidence Collection
        result: ❌ None
      
      tier_2: Validator
        result: ❌ None (빠른 검색만)
    
    step_2_fermi:
      formula: 공연장 평균 좌석 × 객석점유율
      
      variables:
        좌석:
          tier_2: ✅ 2,500석 (Validator, 공연장 협회)
        점유율:
          tier_4: ✅ 0.85 (Estimator)
      
      result: 2,125명
    
    output:
      value: 2,125명
      range: [1,875, 2,375]
      reliability: ⭐⭐⭐⭐
      duration: 15초
```

---

## 📊 시퀀스 다이어그램

### **Diagram 1: Observer Full Workflow**

```
User → Observer: "콘서트 시장 분석"
  
  Observer → Evidence: "기본 정보 수집"
  Evidence → Observer: [공연 유형, 기업 리스트]
  
  Observer → Validator: "공연장 목록 검색"
  Validator → DART: API 호출
  Validator → KOSIS: API 호출
  Validator → Web: 검색
  Validator → Observer: [150개 공연장, 매출 데이터]
  
  Observer → Observer: "구조 분석 완료"
  
  Observer → Calculator: "SAM 계산 (Bottom-up)"
  
    Calculator → Calculator: "공식 생성"
    
    Calculator → Evidence: "공연횟수"
    Evidence → Calculator: ❌ None
    
    Calculator → Validator: "공연횟수"
    Validator → Calculator: ❌ None
    
    Calculator → Calculator: "Fermi 분해"
      Calculator → Evidence: "공연장수"
      Evidence → Calculator: ✅ 150개
      
      Calculator → Estimator: "가동일"
      Estimator → Calculator: ✅ 100일
    
    Calculator → Calculator: "150 × 100 = 15,000회"
    
  Calculator → Observer: [2.04조, evidence_ratio: 0.33]
  
  Observer → Calculator: "SAM 계산 (Proxy)"
  Calculator → Observer: [0.92조, evidence_ratio: 0.67]
  
  Observer → Observer: "수렴 분석 (CV=52%)"
  Observer → Observer: "가중 평균 (1.05조)"
  
  Observer → Observer: "보고서 작성"
  
Observer → User: [Market Reality Report]
```

---

### **Diagram 2: Calculator Convergence**

```
Observer → Calculator: "SAM 계산 (Mode 2)"

Calculator → Calculator: "4개 공식 생성"

# Formula 1
Calculator → Tier1-4: "변수 수집 (공연횟수, 관객, 티켓가)"
Tier1-4 → Calculator: [8000, 2125, 120000]
Calculator → Calculator: "계산: 2.04조"

# Formula 2
Calculator → Tier1-4: "변수 수집 (공연장, 가동, 수입)"
Tier1-4 → Calculator: [150, 100, 120M]
Calculator → Calculator: "계산: 1.8조"

# Formula 3
Calculator → Tier1-4: "변수 수집 (일본, GDP, 조정)"
Tier1-4 → Calculator: [3500억엔, 0.35, 0.75]
Calculator → Calculator: "계산: 0.92조"

# Formula 4
Calculator → Tier1-4: "변수 수집 (Top5, 점유율)"
Tier1-4 → Calculator: [5.8조, 0.60]
Calculator → Calculator: "계산: 9.67조 (outlier)"

Calculator → Calculator: "수렴 분석 (CV=112% → DIVERGED)"
Calculator → Calculator: "Outlier 제외 재분석"
Calculator → Calculator: "가중 평균 (1.2조)"

Calculator → Observer: [1.2조 ±20%]
```

---

## 📋 Agent Interface 명세

### **Observer Interface**

```python
class ObserverRAG:
    def analyze_market(
        self,
        domain: str,
        region: str,
        scope: Literal["structure", "sizing", "complete"] = "complete",
        depth: Literal["light", "medium", "deep"] = "medium"
    ) -> MarketRealityReport:
        """
        완전한 시장 분석
        
        Args:
            domain: 시장 도메인 (예: "Entertainment")
            region: 지역 (예: "Korea")
            scope: 분석 범위
            depth: 분석 깊이
        
        Returns:
            MarketRealityReport
        """
        pass
```

### **Calculator Interface**

```python
class Calculator:
    def calculate(
        self,
        target: str,
        domain: str,
        region: str = None,
        mode: Literal["auto", "exact", "convergence"] = "auto",
        formula_count: int = 4
    ) -> CalculationResult:
        """
        공식 기반 계산
        
        Args:
            target: 계산 목표
            domain: 도메인
            region: 지역
            mode: 계산 모드
            formula_count: 공식 개수 (Mode 2용)
        
        Returns:
            CalculationResult
        """
        pass
```

### **Validator Interface**

```python
class ValidatorRAG:
    def active_search(
        self,
        query: str,
        domain: str = None,
        region: str = None,
        timeout: int = 30
    ) -> Optional[ValidatedData]:
        """
        적극적 데이터 탐색
        
        Args:
            query: 검색 쿼리
            domain: 도메인 (검색 최적화)
            region: 지역
            timeout: 타임아웃 (초)
        
        Returns:
            ValidatedData or None
        """
        pass
```

### **Estimator Interface**

```python
class EstimatorRAG:
    def estimate(
        self,
        question: str,
        domain: str = None,
        region: str = None,
        context: Dict = None
    ) -> EstimationResult:
        """
        순수 추정
        
        Args:
            question: 추정 질문
            domain: 도메인
            region: 지역
            context: 맥락 정보
        
        Returns:
            EstimationResult
        """
        pass
```

---

## ✅ 체크리스트

### **설계 검증**

- [ ] 각 Agent 역할 명확성
- [ ] Workflow 완전성
- [ ] Agent 간 인터페이스 정의
- [ ] 시나리오 현실성
- [ ] 예외 상황 처리

### **구현 준비**

- [ ] 클래스 구조 설계
- [ ] 인터페이스 명세
- [ ] 테스트 시나리오 작성
- [ ] 성능 목표 설정

---

**문서 상태**: Design Review  
**다음 단계**: 사용자 피드백 반영 후 구현  
**작성 완료일**: 2025-11-28
