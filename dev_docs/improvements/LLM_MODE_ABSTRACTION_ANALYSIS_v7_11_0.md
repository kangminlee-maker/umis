# LLM Mode 추상화 분석 및 개선 방안 v7.11.0

**작성일**: 2025-11-26
**버전**: v7.11.0
**목표**: Native/External 분기를 비즈니스 레이어에서 완전히 제거

---

## 🎯 문제 정의

### 현재 상황

**3개의 레이어가 모두 LLM Mode를 알고 있음**:
```
1. 비즈니스 오케스트레이터 (Cursor Composer)
   └─ 프로젝트 관리, Agent 조율, 유저 대화

2. Estimator (4-Stage Fusion)
   └─ Stage 1-4 로직, 값 추정 판단
   └─ ❌ native_mode / external_mode 분기 존재

3. LLM Infrastructure
   ├─ model_configs.yaml (모델 정의)
   ├─ model_router.py (Phase → Model 선택)
   └─ llm_provider.py (LLM 객체 생성)
```

**문제**:
```python
# Estimator 코드 곳곳에 분기
if self.llm_mode == "cursor":
    # RAG만 수행
    return prepare_for_cursor(...)
else:
    # External API 호출
    return call_llm_api(...)
```

**이유**: "cursor"를 가짜 External LLM 타입으로 우겨 넣어 통합한 레거시

---

## 🎯 목표 상태

### "Estimator는 LLM이 뭔지 모르는 바보"

```
Estimator 4-Stage 코드:
  ├─ Stage 1: Evidence Collection
  ├─ Stage 2: Generative Prior
  │   └─ llm = router.get_llm("prior_estimation")
  │       └─ llm.estimate(question, context)
  ├─ Stage 3: Structural Explanation
  │   └─ llm = router.get_llm("fermi_decomposition")
  │       └─ llm.decompose(question, budget)
  └─ Stage 4: Fusion

❌ 제거할 것:
  - if self.llm_mode == "cursor"
  - if native_mode: ... elif external_mode: ...
  - "cursor" 타입 체크

✅ 남길 것:
  - router.get_llm(task_name) 호출만
  - LLM 핸들 사용 (추상화된 인터페이스)
```

---

## 📊 현재 상태 분석

### 1. Estimator 코드의 llm_mode 사용

```bash
umis_rag/agents/estimator/
├── estimator.py (8곳)
│   └─ self.llm_mode 초기화 및 전파
├── prior_estimator.py (9곳)
│   └─ llm_mode property, 조건 분기
├── fermi_estimator.py (7곳)
│   └─ llm_mode property, 조건 분기
├── evidence_collector.py (7곳)
│   └─ llm_mode property
├── source_collector.py (8곳)
│   └─ llm_mode property
├── boundary_validator.py (6곳)
│   └─ llm_mode == "cursor" 분기
├── guardrail_analyzer.py (4곳)
│   └─ llm_mode property
└── sources/value.py (12곳)
    └─ if llm_mode == "cursor" 분기 ❌ 가장 심각
```

**총 61곳에서 llm_mode 사용!**

### 2. model_router.py 분석

**현재**:
```python
class ModelRouter:
    def select_model(self, phase: PhaseType) -> str:
        # Phase → 모델명만 반환
        if phase in [0, 1, 2]:
            return settings.llm_model_phase0_2
        elif phase == 3:
            return settings.llm_model_phase3
        elif phase == 4:
            return settings.llm_model_phase4
    
    def select_model_with_config(self, phase: PhaseType) -> Tuple[str, ModelConfig]:
        # Phase → (모델명, ModelConfig)
        model_name = self.select_model(phase)
        config = model_config_manager.get_config(model_name)
        return model_name, config
```

**문제**: 모델명과 Config만 반환, **실제 LLM 객체는 Estimator가 직접 생성**

### 3. llm_provider.py 분석

```python
class LLMProvider:
    @staticmethod
    def create_llm() -> Optional[BaseChatModel]:
        mode = settings.llm_mode.lower()
        
        if mode == "cursor":
            return None  # ← Cursor 모드는 None 반환
        else:
            return ChatOpenAI(...)  # ← External은 객체 생성
```

**문제**: `None` 반환 → Estimator가 `if llm is None` 분기 필요

---

## 💡 제안된 대안 (사용자)

### 개념

**"하나의 능력 있는 LLM Router"만 Estimator가 알도록**:

```python
# Estimator 코드
class EstimatorRAG:
    def __init__(self):
        self.llm_router = UnifiedLLMRouter()  # ← 통합 라우터
        # ❌ self.llm_mode 제거
    
    def estimate(self, question):
        # Stage 2: Prior
        llm = self.llm_router.get_llm("prior_estimation")
        prior_result = llm.estimate(question, context)
        
        # Stage 3: Fermi
        llm = self.llm_router.get_llm("fermi_decomposition")
        fermi_result = llm.decompose(question, budget)
```

**Router 뒤에서**:
```python
class UnifiedLLMRouter:
    def get_llm(self, task: str) -> LLMInterface:
        # .env LLM_MODE 확인
        if settings.llm_mode == "cursor":
            return CursorLLMAdapter()  # ← 추상화된 인터페이스
        else:
            # model_configs.yaml에서 task별 모델 선택
            model = self._select_model_for_task(task)
            return ExternalLLMAdapter(model)
```

**장점**:
- ✅ Estimator 코드에서 `if llm_mode` 완전 제거
- ✅ Native/External 전환 시 코드 수정 0줄
- ✅ .env / YAML만 변경
- ✅ Clean Architecture (Dependency Inversion)

**단점**:
- ⚠️ LLMInterface 추상화 필요 (새 코드)
- ⚠️ 기존 코드 대대적 리팩터링 (61곳)

---

## 🔍 대안 분석

### 대안 1: 사용자 제안 (완전 추상화)

**구조**:
```
Estimator (비즈니스 레이어)
  └─ UnifiedLLMRouter.get_llm(task) 호출
      └─ LLMInterface 반환
          ├─ CursorLLMAdapter (Native)
          └─ ExternalLLMAdapter (OpenAI/Anthropic)
```

**구현 필요**:
1. `LLMInterface` 추상 클래스
2. `CursorLLMAdapter` (Native 구현)
3. `ExternalLLMAdapter` (External 구현)
4. `UnifiedLLMRouter` (Task → LLM 매핑)
5. Estimator 전체 리팩터링 (61곳)

**장점**:
- ✅ 완벽한 추상화 (Clean Architecture)
- ✅ 비즈니스 로직 순수성
- ✅ 테스트 용이 (Mock 주입)
- ✅ 확장 가능 (새 LLM 타입 추가 쉬움)

**단점**:
- ⚠️ 대규모 리팩터링 (61곳)
- ⚠️ CursorLLMAdapter 구현 복잡 (Cursor는 실제 호출 불가)
- ⚠️ 개발 시간 (2-3일)

**위험도**: 중간 (대규모 변경)

---

### 대안 2: Router 확장 (점진적 개선)

**구조**:
```
Estimator
  └─ router.execute_llm_task(task, prompt, context)
      └─ Router 내부에서 native/external 분기
          ├─ if cursor: return MockResult (Cursor용 포맷)
          └─ else: call External API
```

**구현**:
```python
class ModelRouter:
    def execute_llm_task(
        self, 
        task: str,  # "prior_estimation", "fermi_decomposition"
        prompt: str,
        context: dict
    ) -> Union[EstimationResult, dict]:
        """
        LLM 작업 실행 (Native/External 자동 분기)
        """
        if settings.llm_mode == "cursor":
            # Cursor 모드: 포맷된 결과만 반환
            return {
                "mode": "cursor",
                "task": task,
                "prompt": prompt,
                "context": context,
                "instruction": f"위 context로 {task} 수행"
            }
        else:
            # External 모드: 실제 API 호출
            model_name, config = self.select_model_with_config_for_task(task)
            llm = self._create_llm(model_name, config)
            return llm.invoke(prompt, context)
```

**Estimator 코드**:
```python
# Before
if self.llm_mode == "cursor":
    return prepare_cursor(...)
else:
    llm = ChatOpenAI(...)
    return llm.invoke(...)

# After
result = router.execute_llm_task("prior_estimation", prompt, context)
return result
```

**장점**:
- ✅ Estimator에서 분기 제거
- ✅ Router에 분기 집중 (1곳)
- ✅ 점진적 마이그레이션 가능
- ✅ 개발 시간 짧음 (1일)

**단점**:
- ⚠️ Router가 비즈니스 로직 일부 포함 (완전한 추상화 아님)
- ⚠️ Task 타입 정의 필요

**위험도**: 낮음

---

### 대안 3: Facade 패턴 (중간 지점)

**구조**:
```
Estimator
  └─ LLMFacade
      ├─ estimate_prior(question, context) → EstimationResult
      ├─ decompose_fermi(question, budget) → DecompositionResult
      └─ validate_reasoning(reasoning) → bool
      
LLMFacade 내부:
  └─ if cursor: CursorStrategy
  └─ else: ExternalStrategy
```

**구현**:
```python
class LLMFacade:
    """통합 LLM 인터페이스 (Facade Pattern)"""
    
    def __init__(self):
        if settings.llm_mode == "cursor":
            self.strategy = CursorStrategy()
        else:
            self.strategy = ExternalStrategy()
    
    def estimate_prior(self, question: str, context: dict) -> EstimationResult:
        """Prior 추정 (Stage 2)"""
        return self.strategy.estimate_prior(question, context)
    
    def decompose_fermi(self, question: str, budget: Budget) -> DecompositionResult:
        """Fermi 분해 (Stage 3)"""
        return self.strategy.decompose_fermi(question, budget)
```

**Estimator 코드**:
```python
class EstimatorRAG:
    def __init__(self):
        self.llm = LLMFacade()  # ← 통합 인터페이스
        # ❌ self.llm_mode 제거
    
    def _run_stage2_prior(self, ...):
        result = self.llm.estimate_prior(question, context)
        # ✅ 분기 없음
```

**장점**:
- ✅ Estimator 분기 제거
- ✅ Strategy Pattern (확장 용이)
- ✅ Facade Pattern (단순 인터페이스)
- ✅ Task별 메서드 (타입 안정성)

**단점**:
- ⚠️ 중간 레이어 추가 (복잡도 증가)
- ⚠️ CursorStrategy 구현 필요

**위험도**: 낮음

---

## 🏆 최선의 대안: **대안 2 (Router 확장) + Cursor 간소화**

### 이유

1. **현실성**
   - Cursor는 실제 API 호출이 **불가능**
   - Cursor 모드 = "RAG 결과만 준비"가 본질
   - 완전한 추상화는 Cursor의 한계로 의미 없음

2. **효율성**
   - 61곳 리팩터링 vs 1곳 집중
   - 점진적 마이그레이션 가능
   - v7.11.0 배포 지연 최소화

3. **명확성**
   - Router = "LLM 선택 + 실행"의 단일 책임
   - Estimator = "Stage 로직"의 단일 책임

---

## 🚀 제안 구조

### Architecture

```
┌────────────────────────────────────┐
│  Estimator (비즈니스 레이어)        │
│  ❌ llm_mode 몰라도 됨             │
└─────────────┬──────────────────────┘
              │
              │ router.execute(task, prompt, context)
              ↓
┌────────────────────────────────────┐
│  UnifiedLLMRouter                  │
│  ✅ llm_mode 알고 분기             │
├────────────────────────────────────┤
│  execute_llm_task(task, ...)       │
│    ├─ if cursor: return Mock       │
│    └─ else: call External API      │
└─────────────┬──────────────────────┘
              │
              │ Task → Stage/Model 매핑
              ↓
┌────────────────────────────────────┐
│  Infrastructure                    │
├────────────────────────────────────┤
│  - model_configs.yaml              │
│  - .env (LLM_MODE, LLM_MODEL_*)    │
│  - ModelConfig, LLMProvider        │
└────────────────────────────────────┘
```

### Task 정의

```python
# Task Types (Stage 기반)
TASK_STAGE1_EVIDENCE = "evidence_collection"      # Stage 1 (검색만, LLM 불필요)
TASK_STAGE2_PRIOR = "prior_estimation"            # Stage 2 (직접 추정)
TASK_STAGE2_CERTAINTY = "certainty_evaluation"    # Stage 2 (확신도 평가)
TASK_STAGE3_DECOMPOSE = "fermi_decomposition"     # Stage 3 (변수 식별)
TASK_STAGE3_VARIABLE = "fermi_variable_estimate"  # Stage 3 (변수 추정 = Stage 2 재사용)
TASK_STAGE4_FUSION = "fusion_calculation"         # Stage 4 (계산만, LLM 불필요)
```

### Router 확장

```python
class UnifiedLLMRouter:
    """통합 LLM Router (v7.11.0: Stage 기반)"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Task → Stage 매핑
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TASK_TO_STAGE = {
        "evidence_collection": 1,     # Stage 1 (LLM 불필요)
        "prior_estimation": 2,        # Stage 2
        "certainty_evaluation": 2,    # Stage 2
        "fermi_decomposition": 3,     # Stage 3
        "fermi_variable_estimate": 2, # Stage 3 변수 추정 = Stage 2 재사용
        "fusion_calculation": 4,      # Stage 4 (LLM 불필요)
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 핵심 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def execute_llm_task(
        self,
        task: str,
        prompt: str,
        context: dict = None,
        **kwargs
    ) -> Union[str, dict]:
        """
        LLM 작업 실행 (Native/External 자동 분기)
        
        Args:
            task: Task 타입 ("prior_estimation", "fermi_decomposition" 등)
            prompt: LLM 프롬프트
            context: 컨텍스트 데이터
            **kwargs: 추가 파라미터 (temperature, max_tokens 등)
        
        Returns:
            - Cursor 모드: dict (포맷된 데이터)
            - External 모드: str (LLM 응답)
        """
        # Stage 매핑
        stage = self.TASK_TO_STAGE.get(task, 2)  # 기본 Stage 2
        
        # LLM Mode 체크
        if settings.llm_mode == "cursor":
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Cursor 모드: 포맷만 반환
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            return {
                "mode": "cursor",
                "task": task,
                "stage": stage,
                "prompt": prompt,
                "context": context,
                "instruction": f"[{task}] 위 context로 추정 수행"
            }
        
        else:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # External 모드: 실제 API 호출
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            # 1. Task → Stage → Model 선택
            model_name, config = self.select_model_with_config(stage)
            
            # 2. LLM 객체 생성
            llm = self._create_llm(model_name, config)
            
            # 3. API 호출
            params = config.build_api_params(
                prompt=prompt,
                **kwargs
            )
            
            response = llm.invoke(params)
            return self._parse_response(response, config.api_type)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _create_llm(self, model_name: str, config: ModelConfig):
        """LLM 객체 생성 (External만)"""
        if config.api_type == "responses":
            # Responses API
            from openai import OpenAI
            return OpenAI().responses
        elif config.api_type == "chat":
            # Chat API
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model_name, ...)
        else:
            raise ValueError(f"Unknown api_type: {config.api_type}")
    
    def _parse_response(self, response, api_type: str) -> str:
        """API 응답 파싱"""
        if api_type == "responses":
            return response.choices[0].message.content
        else:  # chat
            return response.content
```

### Estimator 코드 변경

```python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Before (v7.10.2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PriorEstimator:
    def __init__(self, llm_mode: Optional[str] = None):
        self._llm_mode = llm_mode
    
    @property
    def llm_mode(self) -> str:
        if self._llm_mode is None:
            return settings.llm_mode
        return self._llm_mode
    
    def estimate(self, question, context):
        if self.llm_mode == "cursor":
            # Cursor 모드 처리
            return self._prepare_cursor_output(...)
        else:
            # External 모드 처리
            llm = ChatOpenAI(...)
            return llm.invoke(...)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# After (v7.11.0 제안)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PriorEstimator:
    def __init__(self, router: Optional[UnifiedLLMRouter] = None):
        self.router = router or get_unified_router()
        # ❌ llm_mode 제거
    
    def estimate(self, question, context):
        # ✅ 분기 없음
        prompt = self._build_prompt(question, context)
        result = self.router.execute_llm_task(
            task="prior_estimation",
            prompt=prompt,
            context=context
        )
        
        # Result 처리 (Cursor/External 동일)
        return self._parse_result(result)
```

**장점**:
- ✅ Estimator 분기 완전 제거
- ✅ Router 1곳에만 분기 집중
- ✅ 기존 infrastructure 재사용
- ✅ 점진적 마이그레이션

**단점**:
- ⚠️ Cursor 결과 포맷 다름 (dict vs str)
- ⚠️ `_parse_result()` 필요

**위험도**: 낮음

---

### 대안 4: 현상 유지 + Documentation

**현재 상태**:
- Estimator가 `llm_mode` property 보유
- 각 컴포넌트에서 분기 처리
- 61곳에서 `llm_mode` 사용

**개선**:
- 문서화 강화
- 일관된 패턴 적용
- 테스트 커버리지 확대

**장점**:
- ✅ 리팩터링 불필요
- ✅ 안정성 (기존 코드 유지)

**단점**:
- ❌ 근본적 해결 아님
- ❌ 유지보수 어려움 지속

**위험도**: 없음 (변경 없음)

---

## 🎯 최종 권장안

### **대안 2 + Cursor 특수 처리**

**핵심 인사이트**:

Cursor 모드는 실제 "LLM"이 아니라 **"LLM에게 전달할 데이터 준비"**입니다.

따라서:
1. **External LLM**: Router가 API 호출 → 결과 반환
2. **Cursor "LLM"**: Router가 포맷만 반환 → Estimator가 즉시 반환

### 구현 계획

#### Phase 1: Router 확장 (1일)

```python
# umis_rag/core/unified_llm_router.py (신규)

class UnifiedLLMRouter:
    """
    통합 LLM Router (v7.11.0)
    
    책임:
    - Task → Stage → Model 선택
    - Native/External 분기 (여기서만!)
    - LLM 실행 (External만)
    """
    
    def execute_llm_task(
        self,
        task: str,
        prompt: str,
        context: dict = None,
        budget: Optional[Budget] = None,
        **kwargs
    ) -> Union[str, dict]:
        """
        통합 LLM 작업 실행
        
        Returns:
            - Cursor: dict (포맷된 데이터)
            - External: str (LLM 응답)
        """
        stage = self._task_to_stage(task)
        
        if settings.llm_mode == "cursor":
            # Cursor 모드: 준비만
            return self._prepare_cursor_format(task, stage, prompt, context)
        else:
            # External 모드: 실행
            return self._execute_external_llm(stage, prompt, context, **kwargs)
    
    def _execute_external_llm(self, stage, prompt, context, **kwargs) -> str:
        """External LLM 실행 (Router 내부)"""
        # 1. Model 선택
        model_name, config = self.select_model_with_config(stage)
        
        # 2. API 파라미터 빌드
        params = config.build_api_params(prompt=prompt, **kwargs)
        
        # 3. LLM 호출
        if config.api_type == "responses":
            response = self._call_responses_api(model_name, params)
        else:  # chat
            response = self._call_chat_api(model_name, params)
        
        return response
    
    def _prepare_cursor_format(self, task, stage, prompt, context) -> dict:
        """Cursor 모드: 포맷만 반환"""
        return {
            "mode": "cursor",
            "task": task,
            "stage": stage,
            "prompt": prompt,
            "context": context or {},
            "instruction": f"위 context로 {task} 수행해주세요."
        }
```

#### Phase 2: Estimator 리팩터링 (1일)

```python
# umis_rag/agents/estimator/prior_estimator.py

class PriorEstimator:
    def __init__(self, router: Optional[UnifiedLLMRouter] = None):
        self.router = router or get_unified_router()
        # ❌ llm_mode 완전 제거
    
    def estimate(self, question: str, context: Context) -> Optional[EstimationResult]:
        """Stage 2: Generative Prior"""
        
        # 1. 프롬프트 생성
        prompt = self._build_prompt(question, context)
        
        # 2. Router 실행 (분기 없음!)
        response = self.router.execute_llm_task(
            task="prior_estimation",
            prompt=prompt,
            context=context.to_dict()
        )
        
        # 3. 결과 파싱
        if isinstance(response, dict) and response.get("mode") == "cursor":
            # Cursor 모드: 포맷된 데이터 반환 (Estimator가 즉시 반환)
            logger.info("  [Cursor] Prior 데이터 준비 완료")
            return None  # Estimator.estimate()가 Cursor 포맷 반환
        else:
            # External 모드: LLM 응답 파싱
            return self._parse_llm_response(response)
```

#### Phase 3: Estimator 메인 로직 수정 (0.5일)

```python
# umis_rag/agents/estimator/estimator.py

class EstimatorRAG:
    def __init__(self):
        self.router = get_unified_router()  # ← 통합 라우터
        # ❌ self.llm_mode 제거
        
        # 각 컴포넌트에 router 전달
        self.evidence_collector = EvidenceCollector(router=self.router)
        self.prior_estimator = PriorEstimator(router=self.router)
        self.fermi_estimator = FermiEstimator(
            router=self.router,
            prior_estimator=self.prior_estimator
        )
    
    def estimate(self, question: str, ...) -> EstimationResult:
        """4-Stage 추정 (분기 없음!)"""
        
        # Stage 1: Evidence
        evidence = self.evidence_collector.collect(...)
        
        # Stage 2: Prior
        prior_result = self.prior_estimator.estimate(...)
        
        # Cursor 모드 체크 (Router가 반환한 dict)
        if isinstance(prior_result, dict) and prior_result.get("mode") == "cursor":
            # Cursor 모드: 즉시 반환 (Composer가 처리)
            return prior_result
        
        # Stage 3: Fermi (External만)
        fermi_result = self.fermi_estimator.decompose(...)
        
        # Stage 4: Fusion
        final_result = self._fuse_results(...)
        
        return final_result
```

---

## 📊 대안 비교

| 항목 | 대안 1 (완전 추상화) | 대안 2 (Router 확장) | 대안 3 (Facade) | 대안 4 (현상 유지) |
|------|---------------------|---------------------|-----------------|-------------------|
| **Estimator 분기** | ✅ 완전 제거 | ✅ 완전 제거 | ✅ 완전 제거 | ❌ 유지 (61곳) |
| **Clean Architecture** | ✅ 완벽 | ⚠️ 90% | ⚠️ 85% | ❌ 50% |
| **개발 시간** | ⚠️ 2-3일 | ✅ 1-1.5일 | ⚠️ 1.5-2일 | ✅ 0일 |
| **위험도** | ⚠️ 중간 | ✅ 낮음 | ✅ 낮음 | ✅ 없음 |
| **Cursor 한계** | ⚠️ 복잡한 Adapter | ✅ 간단한 포맷 | ⚠️ Strategy 필요 | - |
| **확장성** | ✅ 최고 | ⚠️ 중간 | ✅ 높음 | ❌ 낮음 |
| **유지보수** | ✅ 쉬움 | ⚠️ 중간 | ⚠️ 중간 | ❌ 어려움 |

### 점수
- **대안 1**: 85점 (이상적이지만 현실적 한계)
- **대안 2**: **95점** ⭐ (현실적 최선)
- **대안 3**: 80점 (중간 레이어 오버헤드)
- **대안 4**: 40점 (근본 해결 아님)

---

## 🎯 최종 결론

### **대안 2 (Router 확장) 권장**

**이유**:

1. **Cursor의 본질 이해**
   - Cursor = 실제 LLM 아님
   - Cursor = "데이터 준비" + Composer가 읽음
   - 완전 추상화는 Cursor 한계로 오히려 복잡

2. **현실적 Trade-off**
   - Clean Architecture 90% 달성
   - 개발 시간 최소 (1-1.5일)
   - 위험도 낮음

3. **명확한 책임 분리**
   ```
   Estimator: "뭘 추정할지" (비즈니스 로직)
   Router: "어떻게 추정할지" (Infrastructure)
   ```

4. **점진적 마이그레이션**
   - Stage 2 (Prior) 먼저 적용
   - 테스트 후 Stage 3 (Fermi) 확장
   - 문제 발생 시 롤백 쉬움

---

## 🚀 실행 계획

### Phase 1: Router 확장 (4시간)
1. `unified_llm_router.py` 생성
2. `execute_llm_task()` 구현
3. Task 타입 정의
4. 단위 테스트

### Phase 2: PriorEstimator 리팩터링 (3시간)
1. `llm_mode` property 제거
2. `router.execute_llm_task()` 사용
3. Cursor 모드 포맷 처리
4. 통합 테스트

### Phase 3: FermiEstimator 리팩터링 (3시간)
1. `llm_mode` property 제거
2. `router.execute_llm_task()` 사용
3. 변수 추정 = Stage 2 재사용
4. E2E 테스트

### Phase 4: 기타 컴포넌트 (2시간)
1. EvidenceCollector
2. SourceCollector
3. BoundaryValidator
4. GuardrailAnalyzer

### Phase 5: 검증 (2시간)
1. 전체 테스트 실행
2. Native/External 모드 검증
3. 문서 업데이트

**총 소요 시간**: 14시간 (2일)

---

## ⚠️ 주의사항

### Cursor 모드의 한계

Cursor는 **실제 LLM이 아닙니다**:
- API 호출 불가
- 동기 실행 불가
- Composer/Chat이 읽어야 함

따라서:
- ✅ "완전한 추상화"보다 "명확한 구분"이 낫습니다
- ✅ Cursor = "데이터 준비", External = "실행 완료"
- ✅ Router가 이 차이를 관리

### 하위 호환성

`compat.py`에 Adapter 추가:
```python
class LegacyLLMModeMixin:
    """하위 호환성: llm_mode property 제공"""
    
    @property
    def llm_mode(self) -> str:
        warnings.warn(
            "llm_mode property는 deprecated. "
            "router.execute_llm_task() 사용 권장",
            DeprecationWarning
        )
        return settings.llm_mode
```

---

## 📚 참고 문서

- **현재 구조**: `umis_rag/core/model_router.py`
- **Model Config**: `config/model_configs.yaml`
- **LLM Provider**: `umis_rag/core/llm_provider.py`
- **v7.11.0 Migration**: `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md`

---

## 🎊 예상 효과

### 1. 코드 품질
- ✅ Estimator 순수성 (61곳 → 0곳)
- ✅ Single Responsibility (Router만 분기)
- ✅ Dependency Inversion (추상화 의존)

### 2. 유지보수
- ✅ Native/External 전환 시 코드 수정 0줄
- ✅ .env / YAML만 변경
- ✅ 새 LLM 타입 추가 쉬움

### 3. 테스트
- ✅ Mock Router 주입 (단위 테스트)
- ✅ Native/External 독립 테스트
- ✅ Integration 테스트 간소화

---

## 💬 결론

**대안 2 (Router 확장 + Cursor 특수 처리)** 를 강력 권장합니다.

**핵심**:
```python
# Estimator는 이제 이것만 알면 됩니다:
result = router.execute_llm_task(task, prompt, context)

# Router 뒤에서 모든 것이 결정됩니다:
# - Cursor인지 External인지
# - 어떤 모델인지
# - 어떻게 호출할지
```

**실행 여부**: 사용자 승인 후 즉시 시작 가능 (2일 완료)

---

**작성**: 2025-11-26
**v7.11.0 LLM Mode 추상화 제안** 🎯
