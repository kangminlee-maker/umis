# umis.yaml 대규모 업데이트 계획 (v7.11.0)

**목표**: v7.11.0 LLM 완전 추상화를 반영한 완결성 있는 최신 시스템 문서

## 📋 업데이트 원칙

1. **현재 상태만 기술** - "v7.8.1에서 변경되었다" 같은 히스토리 제거
2. **실행 가능성** - AI가 읽고 바로 사용할 수 있는 구체적인 API와 예시
3. **완결성** - v7.11.0 아키텍처가 현재의 표준
4. **간결성** - Deprecated API는 최소한으로만 언급

## 🎯 업데이트할 섹션

### 1. 시스템 개요 (Lines 1-45)
**현재**:
```yaml
# - 5-Phase Estimator (100% 커버리지)
# - Native/External 모드 (LLM 선택)
```

**변경**:
```yaml
# - 4-Stage Fusion Estimator (100% 커버리지)
# - LLM Complete Abstraction (Clean Architecture, Zero Branching)
```

### 2. System Description (Line 280)
**현재**:
```yaml
description: "6-Agent + 5-Phase Estimator + Model Config 시스템..."
```

**변경**:
```yaml
description: "6-Agent + 4-Stage Fusion Estimator + LLM Complete Abstraction + Model Config 시스템..."
```

### 3. Estimator Agent 섹션 완전 재작성 (Lines 6494-6596)

#### 3.1 기본 정보
**현재**:
```yaml
name: "Estimator (Fermi) Agent"
version: "v7.7.0"
status: "✅ 완성 (5-Phase, 100% 커버리지, 용어 명확화)"
```

**변경**:
```yaml
name: "Estimator Agent"
version: "v7.11.0"
status: "✅ Production (4-Stage Fusion, LLM Complete Abstraction)"
architecture: "Clean Architecture (DIP, SRP, OCP, ISP)"
```

#### 3.2 Architecture 섹션 신규 추가
```yaml
architecture_v7_11_0:
  principle: "Dependency Inversion (의존성 역전)"
  achievement: "61개 llm_mode 분기 → 0개 (100% 제거)"
  
  core_interfaces:
    BaseLLM:
      purpose: "Task별 LLM 작업 인터페이스"
      methods:
        - "estimate(question, context, **kwargs)"
        - "decompose(question, context, **kwargs)"
        - "evaluate_certainty(value, evidence, **kwargs)"
        - "validate_boundary(value, bounds, **kwargs)"
        - "is_native() -> bool"
      
    LLMProvider:
      purpose: "LLM Provider 추상화"
      methods:
        - "get_llm(task: TaskType) -> BaseLLM"
        - "is_native() -> bool"
        - "get_mode_info() -> Dict"
    
    TaskType:
      purpose: "14개 Task 유형 정의"
      tasks:
        stage1: ["EVIDENCE_COLLECTION", "GUARDRAIL_ANALYSIS"]
        stage2: ["PRIOR_ESTIMATION", "CERTAINTY_EVALUATION"]
        stage3: ["FERMI_DECOMPOSITION", "VARIABLE_ESTIMATION"]
        stage4: ["FUSION", "BOUNDARY_VALIDATION"]
  
  implementations:
    cursor_native:
      provider: "CursorLLMProvider"
      llm: "CursorLLM"
      cost: "$0 (API 호출 없음)"
      behavior:
        - "모든 메서드 None 또는 기본값 반환"
        - "로그 포맷팅 (Cursor Composer 수동 처리)"
        - "is_native() → True"
    
    external_api:
      provider: "ExternalLLMProvider"
      llm: "ExternalLLM"
      features:
        - "ModelRouter 통합 (Task별 모델 선택)"
        - "프롬프트 빌더 (Prior, Fermi, Certainty, Boundary)"
        - "JSON 응답 파서 (Regex fallback)"
        - "is_native() → False"
  
  factory:
    class: "LLMProviderFactory"
    method: "get_llm_provider(mode: str) -> LLMProvider"
    features:
      - "동적 Provider 선택"
      - "Singleton 패턴 (get_default_llm_provider)"
      - "테스트용 reset (reset_llm_provider)"
```

#### 3.3 4-Stage Architecture
**현재**: five_phase_architecture (Phase 0-4)

**변경**: four_stage_fusion_architecture

```yaml
four_stage_fusion_architecture:
  overview:
    principle: "증거 수집 → 생성적 추정 → 구조적 설명 → 융합"
    recursion: "완전 금지 (Recursion FORBIDDEN)"
    budget: "예산 기반 탐색 제어"
  
  stage_1_evidence_collection:
    class: "EvidenceCollector"
    purpose: "확정 데이터 및 제약 조건 수집"
    phases_included: ["Phase 0 (Literal)", "Phase 1 (Direct RAG)", "Phase 2 (Validator)"]
    speed: "<2초"
    coverage: "45% (Phase 0: 10% + Phase 1: 5% + Phase 2: 30%)"
    early_return: "확정 값 발견 시 즉시 반환"
    
    outputs:
      definite_value: "확정된 값 (있는 경우)"
      hard_bounds: "논리적 제약 (절대 위반 불가)"
      soft_hints: "경험적 힌트 (참고용)"
      logical_relations: "논리적 관계"
    
    guardrail_engine:
      purpose: "Hard/Soft Constraints 분석"
      llm_chain: "2-Step (관계 판단 + Hard/Soft 판정)"
  
  stage_2_generative_prior:
    class: "PriorEstimator"
    purpose: "LLM 직접 값 요청"
    model: "gpt-4.1-nano (Stage 2 최적화)"
    speed: "3-8초"
    coverage: "40%"
    
    approach:
      principle: "LLM = 경험 데이터의 압축"
      prompt: "당신이 확신 있게 말할 수 있는 값을 제시하세요"
      recursion: "금지 (단일 호출만)"
    
    outputs:
      value: "추정 값"
      value_range: "[min, max]"
      certainty: "high/medium/low"
      reasoning: "추정 근거"
  
  stage_3_structural_explanation:
    class: "FermiEstimator"
    purpose: "Fermi 분해로 구조 설명"
    model: "gpt-4o-mini (Stage 3 최적화)"
    speed: "10-30초"
    coverage: "10%"
    
    approach:
      decomposition: "2-4개 변수로 분해"
      variable_estimation: "각 변수 → PriorEstimator 호출"
      recursion: "금지 (depth=0만)"
      max_depth: "2 (강제)"
    
    outputs:
      value: "계산된 값"
      decomposition:
        formula: "공식 (예: LTV = ARPU / Churn)"
        variables: "변수별 추정 결과"
        depth: "현재 깊이"
      certainty: "변수들의 평균 certainty"
  
  stage_4_fusion_validation:
    class: "FusionLayer"
    purpose: "Stage 1-3 결과 융합"
    method: "Sensor Fusion (가중 평균)"
    
    strategy:
      evidence_priority: "Stage 1 (Evidence) 최우선"
      prior_baseline: "Stage 2 (Prior) 기준값"
      fermi_explanation: "Stage 3 (Fermi) 구조적 설명"
      hard_bounds_clipping: "Hard Bounds 절대 준수"
    
    outputs:
      value: "최종 융합 값"
      source: "Evidence/Generative Prior/Fermi/Fusion"
      certainty: "종합 확신도"
      decomposition: "구조적 설명 (있는 경우)"
```

#### 3.4 API Usage (실행 가능한 예시)
**현재**: 구버전 API

**변경**: v7.11.0 Clean API

```yaml
usage_examples:
  basic_usage:
    description: "가장 간단한 사용법"
    code: |
      from umis_rag.agents.estimator import EstimatorRAG
      
      # 기본 초기화 (settings.llm_mode 자동 사용)
      estimator = EstimatorRAG()
      
      # 추정 실행
      result = estimator.estimate(
          question="B2B SaaS 한국 시장 ARPU는?",
          domain="B2B_SaaS",
          region="한국"
      )
      
      # 결과 확인
      print(f"값: {result.value:,.0f}원")
      print(f"출처: {result.source}")
      print(f"확신도: {result.certainty}")
  
  with_context:
    description: "Context 객체 사용"
    code: |
      from umis_rag.agents.estimator import EstimatorRAG
      from umis_rag.agents.estimator.models import Context
      
      estimator = EstimatorRAG()
      
      context = Context(
          domain="B2B_SaaS",
          region="한국",
          time_period="2024"
      )
      
      result = estimator.estimate("ARPU는?", context=context)
  
  with_budget:
    description: "Budget 제어"
    code: |
      from umis_rag.agents.estimator import EstimatorRAG
      from umis_rag.agents.estimator.common import create_fast_budget
      
      estimator = EstimatorRAG()
      budget = create_fast_budget()  # max_llm_calls=3
      
      result = estimator.estimate(
          question="서울 음식점 수는?",
          budget=budget
      )
  
  custom_provider:
    description: "Custom LLMProvider 주입"
    code: |
      from umis_rag.agents.estimator import EstimatorRAG
      from umis_rag.core.llm_provider_factory import get_llm_provider
      
      # Cursor 모드 명시적 사용
      cursor_provider = get_llm_provider("cursor")
      estimator = EstimatorRAG(llm_provider=cursor_provider)
      
      # External 모드 명시적 사용
      external_provider = get_llm_provider("gpt-4o-mini")
      estimator = EstimatorRAG(llm_provider=external_provider)
```

#### 3.5 Deprecated APIs (최소한으로만 언급)
```yaml
backward_compatibility:
  note: "v7.10.0 이하 API는 compat.py를 통해 완전 호환"
  
  deprecated_classes:
    - "Phase3Guestimation → PriorEstimator (DeprecationWarning)"
    - "Phase4FermiDecomposition → FermiEstimator (DeprecationWarning)"
  
  removal_schedule: "v7.11.1에서 제거 예정"
  
  migration:
    old: "phase3 = Phase3Guestimation(llm_mode='cursor')"
    new: "prior = PriorEstimator()  # settings.llm_mode 자동 사용"
```

### 4. Universal Tools 섹션 업데이트 (Lines 2861, 3140, 3649)

**현재**:
```yaml
estimator_collaboration:
  method: "estimator.estimate()"
  note: "v7.3.2+: 직접 추정 금지, Estimator 호출 필수"
```

**변경**:
```yaml
estimator_collaboration:
  when: "값 추정이 필요할 때"
  agent: "Estimator"
  method: "estimator.estimate(question, domain=None, region=None, context=None, budget=None)"
  frequency: "★★★★★ 가장 많이 사용"
  common_cases: "ARPU, Churn, 전환율, 성장률, 시장 규모, 비율 등"
  
  architecture: "4-Stage Fusion (Evidence → Prior → Fermi → Fusion)"
  note: "모든 값 추정은 Estimator만 수행 (Single Source of Truth)"
  
  example:
    code: |
      from umis_rag.agents.estimator import EstimatorRAG
      
      estimator = EstimatorRAG()
      result = estimator.estimate("B2B SaaS ARPU는?", domain="B2B_SaaS", region="한국")
      
      if result and result.is_successful():
          arpu = result.value
          print(f"ARPU: {arpu:,.0f}원 (출처: {result.source})")
```

### 5. System Description 업데이트

**Line 17-22 업데이트**:
```yaml
# UMIS 기능:
# - 6-Agent 협업 시스템 (역할 MECE)
# - 4-Stage Fusion Estimator (100% 커버리지)
# - LLM Complete Abstraction (Clean Architecture, Zero Branching)
# - Model Config 시스템 (18개 모델: 17 External + cursor-native)
# - RAG 기반 패턴/사례 자동 검색 (54개)
# - Excel 자동 생성 + 완전 추적성
# - 통합 벤치마크 (98% 비용 절감)
```

## 📝 업데이트 순서

1. ✅ 계획 문서 작성 (현재)
2. 시스템 개요 업데이트 (Lines 1-45)
3. System description 업데이트 (Line 280)
4. Estimator Agent 섹션 재작성 (Lines 6494-6596)
5. Universal Tools 업데이트 (Lines 2861, 3140, 3649)
6. 버전 히스토리 제거 (전체)
7. 최종 검토 및 커밋

## 🎯 완료 기준

- [ ] "v7.X.X에서..." 같은 히스토리 언급 모두 제거
- [ ] v7.11.0 API가 현재의 표준으로 기술됨
- [ ] 모든 코드 예시가 v7.11.0 Clean API 사용
- [ ] Deprecated API는 1-2줄로만 언급
- [ ] AI가 읽고 바로 실행 가능한 수준의 구체성

---

**작성일**: 2025-11-26  
**작성자**: AI Assistant (Claude Sonnet 4.5)  
**검토자**: 사용자

