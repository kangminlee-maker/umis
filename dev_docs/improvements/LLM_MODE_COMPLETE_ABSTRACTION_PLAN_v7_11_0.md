# LLM Mode 완전 추상화 구현 계획 (대안 1)

**작성일**: 2025-11-26
**버전**: v7.11.0
**목표**: Native/External 분기를 비즈니스 레이어에서 **완전히** 제거

---

## 🎯 최종 목표 상태

### Estimator 코드 (비즈니스 레이어)

```python
class EstimatorRAG:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        # ✅ LLMProvider 인터페이스만 의존
        self.llm_provider = llm_provider or get_default_llm_provider()
        
        # ❌ 제거: self.llm_mode, native_mode, external_mode
    
    def estimate(self, question: str, ...) -> EstimationResult:
        """4-Stage 추정 (분기 없음!)"""
        
        # Stage 1: Evidence Collection
        evidence = self.evidence_collector.collect(...)
        
        # Stage 2: Prior Estimation
        llm = self.llm_provider.get_llm("prior_estimation")
        prior_result = llm.estimate(question, context)
        
        # Early Return 체크
        if prior_result.certainty == "high":
            return prior_result
        
        # Stage 3: Fermi Decomposition
        llm = self.llm_provider.get_llm("fermi_decomposition")
        fermi_result = llm.decompose(question, budget)
        
        # Stage 4: Fusion
        return self._fuse_results(evidence, prior_result, fermi_result)
```

**핵심**: `llm_provider.get_llm(task)` 호출만 존재, 분기 **0개**

---

## 📐 아키텍처 설계

### 1. 계층 구조

```
┌───────────────────────────────────────────────────────────┐
│  비즈니스 레이어 (Estimator)                               │
│  - EstimatorRAG                                           │
│  - PriorEstimator                                         │
│  - FermiEstimator                                         │
│  - EvidenceCollector                                      │
│  ❌ llm_mode 모름, 분기 없음                              │
└─────────────────┬─────────────────────────────────────────┘
                  │
                  │ LLMProvider Interface (의존성 역전)
                  │
                  ↓
┌───────────────────────────────────────────────────────────┐
│  추상화 레이어 (Interface)                                 │
│  - LLMProvider (ABC)                                      │
│  - BaseLLM (ABC)                                          │
│  - TaskType (Enum)                                        │
└─────────────────┬─────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ CursorLLMProvider│  │ExternalLLMProvider│
│  (Native 구현)   │  │  (External 구현) │
├──────────────────┤  ├──────────────────┤
│ - CursorLLM      │  │ - ExternalLLM    │
│ - 포맷만 반환    │  │ - API 실제 호출  │
└──────────────────┘  └──────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────────────────────┐
│  Infrastructure 레이어                                     │
│  - ModelRouter (Task → Stage → Model 선택)                │
│  - ModelConfig (model_configs.yaml)                       │
│  - Settings (.env)                                        │
└───────────────────────────────────────────────────────────┘
```

### 2. Dependency Inversion

```
High-level (Estimator) → Interface (LLMProvider) ← Low-level (CursorLLMProvider, ExternalLLMProvider)
                              ↑
                         의존성 역전
```

---

## 🔧 구현 컴포넌트

### Phase 1: 인터페이스 정의

#### 1.1 LLM 인터페이스

```python
# umis_rag/core/llm_interface.py (신규)

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from umis_rag.agents.estimator.models import EstimationResult, Context
from umis_rag.agents.estimator.common.budget import Budget


class TaskType(Enum):
    """LLM 작업 타입 (Stage 기반)"""
    
    # Stage 1 (LLM 불필요, 포함은 완전성 위해)
    EVIDENCE_COLLECTION = "evidence_collection"
    
    # Stage 2
    PRIOR_ESTIMATION = "prior_estimation"
    CERTAINTY_EVALUATION = "certainty_evaluation"
    
    # Stage 3
    FERMI_DECOMPOSITION = "fermi_decomposition"
    FERMI_VARIABLE_ESTIMATION = "fermi_variable_estimation"  # = Stage 2 재사용
    
    # Stage 4 (LLM 불필요, 포함은 완전성 위해)
    FUSION_CALCULATION = "fusion_calculation"
    
    # 기타
    BOUNDARY_VALIDATION = "boundary_validation"
    GUARDRAIL_ANALYSIS = "guardrail_analysis"


class BaseLLM(ABC):
    """
    LLM 추상 인터페이스
    
    모든 LLM 구현체(Cursor, External)가 준수해야 할 인터페이스
    """
    
    @abstractmethod
    def estimate(
        self,
        question: str,
        context: Context,
        **kwargs
    ) -> Optional[EstimationResult]:
        """
        값 추정 (Stage 2: Prior Estimation)
        
        Args:
            question: 추정 질문
            context: 컨텍스트 정보
            **kwargs: 추가 파라미터
        
        Returns:
            EstimationResult 또는 None (Early Return 실패 시)
        """
        pass
    
    @abstractmethod
    def decompose(
        self,
        question: str,
        context: Context,
        budget: Budget,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Fermi 분해 (Stage 3: Structural Explanation)
        
        Args:
            question: 분해할 질문
            context: 컨텍스트 정보
            budget: 예산 제약
            **kwargs: 추가 파라미터
        
        Returns:
            분해 결과 (variables, formula, reasoning 등)
        """
        pass
    
    @abstractmethod
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Context,
        **kwargs
    ) -> str:
        """
        확신도 평가 (Stage 2)
        
        Args:
            question: 질문
            value: 추정값
            context: 컨텍스트
        
        Returns:
            certainty: "high", "medium", "low"
        """
        pass
    
    @abstractmethod
    def validate_boundary(
        self,
        value: Any,
        context: Context,
        **kwargs
    ) -> Dict[str, Any]:
        """
        경계 검증
        
        Args:
            value: 검증할 값
            context: 컨텍스트
        
        Returns:
            검증 결과 (is_valid, reason, suggested_range)
        """
        pass
    
    @abstractmethod
    def is_native(self) -> bool:
        """Native(Cursor) 모드 여부"""
        pass


class LLMProvider(ABC):
    """
    LLM Provider 인터페이스
    
    Task별 적절한 LLM 객체를 제공하는 팩토리
    """
    
    @abstractmethod
    def get_llm(self, task: TaskType) -> BaseLLM:
        """
        Task에 맞는 LLM 객체 반환
        
        Args:
            task: TaskType (prior_estimation, fermi_decomposition 등)
        
        Returns:
            BaseLLM 구현체 (CursorLLM 또는 ExternalLLM)
        """
        pass
    
    @abstractmethod
    def is_native(self) -> bool:
        """Native(Cursor) Provider 여부"""
        pass
    
    @abstractmethod
    def get_mode_info(self) -> Dict[str, Any]:
        """현재 모드 정보 반환 (디버깅/모니터링용)"""
        pass
```

---

### Phase 2: Cursor 구현

#### 2.1 CursorLLM (Native 구현)

```python
# umis_rag/core/llm_cursor.py (신규)

from typing import Optional, Dict, Any
from umis_rag.core.llm_interface import BaseLLM, TaskType
from umis_rag.agents.estimator.models import EstimationResult, Context
from umis_rag.agents.estimator.common.budget import Budget
import logging

logger = logging.getLogger(__name__)


class CursorLLM(BaseLLM):
    """
    Cursor Native LLM 구현
    
    특징:
    - 실제 LLM 호출 불가 (Cursor Composer가 처리)
    - 포맷된 데이터만 반환
    - 비용 $0
    """
    
    def __init__(self, task: TaskType):
        self.task = task
        logger.info(f"[CursorLLM] 초기화: {task.value}")
    
    def estimate(
        self,
        question: str,
        context: Context,
        **kwargs
    ) -> Optional[EstimationResult]:
        """
        Cursor 모드: 포맷된 데이터 반환 (실제 추정 불가)
        
        Returns:
            None (Cursor가 처리할 수 있도록 특수 포맷 로깅)
        """
        logger.info(f"[Cursor Prior] 추정 데이터 준비")
        logger.info(f"  Question: {question}")
        logger.info(f"  Context: {context.to_dict()}")
        logger.info("  → Cursor Composer에서 위 데이터로 추정 수행")
        
        # ⚠️ None 반환 → Estimator가 Cursor 포맷 응답 생성
        return None
    
    def decompose(
        self,
        question: str,
        context: Context,
        budget: Budget,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Cursor 모드: Fermi 분해 데이터 준비
        
        Returns:
            None (Cursor 포맷 로깅)
        """
        logger.info(f"[Cursor Fermi] 분해 데이터 준비")
        logger.info(f"  Question: {question}")
        logger.info(f"  Budget: {budget}")
        logger.info(f"  Context: {context.to_dict()}")
        logger.info("  → Cursor Composer에서 위 데이터로 분해 수행")
        
        return None
    
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Context,
        **kwargs
    ) -> str:
        """
        Cursor 모드: 확신도 평가 불가
        
        Returns:
            "medium" (기본값)
        """
        logger.info(f"[Cursor Certainty] 기본값 반환 (medium)")
        return "medium"
    
    def validate_boundary(
        self,
        value: Any,
        context: Context,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cursor 모드: 경계 검증 스킵
        
        Returns:
            기본 통과 결과
        """
        logger.info(f"[Cursor Boundary] 검증 스킵")
        return {
            "is_valid": True,
            "reason": "Cursor 모드는 검증 스킵",
            "suggested_range": None
        }
    
    def is_native(self) -> bool:
        return True


class CursorLLMProvider(LLMProvider):
    """
    Cursor LLM Provider
    
    Task에 관계없이 항상 CursorLLM 반환
    """
    
    def __init__(self):
        logger.info("[CursorLLMProvider] 초기화 (Native 모드)")
    
    def get_llm(self, task: TaskType) -> BaseLLM:
        """
        Task별 CursorLLM 반환
        
        Args:
            task: TaskType
        
        Returns:
            CursorLLM 인스턴스
        """
        logger.debug(f"[CursorLLMProvider] {task.value} → CursorLLM")
        return CursorLLM(task)
    
    def is_native(self) -> bool:
        return True
    
    def get_mode_info(self) -> Dict[str, Any]:
        return {
            "mode": "cursor",
            "provider": "CursorLLMProvider",
            "uses_api": False,
            "cost": "$0 (Cursor 구독 포함)",
            "automation": False,
            "description": "RAG 검색 + 포맷 → Cursor Composer가 분석"
        }
```

**핵심 설계 결정**:

1. **None 반환**: Cursor는 실제 결과 생성 불가 → `None` 반환
2. **로깅**: 대신 포맷된 데이터를 로깅 → Cursor Composer가 읽음
3. **기본값**: `certainty="medium"`, `is_valid=True` (보수적)

---

### Phase 3: External 구현

#### 3.1 ExternalLLM (API 호출)

```python
# umis_rag/core/llm_external.py (신규)

from typing import Optional, Dict, Any
from umis_rag.core.llm_interface import BaseLLM, TaskType
from umis_rag.core.model_router import ModelRouter, get_model_router
from umis_rag.core.model_configs import ModelConfig, model_config_manager
from umis_rag.agents.estimator.models import EstimationResult, Context
from umis_rag.agents.estimator.common.budget import Budget
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
import json

logger = logging.getLogger(__name__)


class ExternalLLM(BaseLLM):
    """
    External LLM 구현 (OpenAI, Anthropic 등)
    
    특징:
    - 실제 API 호출
    - 완성된 결과 반환
    - 토큰당 과금
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Task → Stage 매핑
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TASK_TO_STAGE = {
        TaskType.EVIDENCE_COLLECTION: 1,
        TaskType.PRIOR_ESTIMATION: 2,
        TaskType.CERTAINTY_EVALUATION: 2,
        TaskType.FERMI_DECOMPOSITION: 3,
        TaskType.FERMI_VARIABLE_ESTIMATION: 2,  # Stage 2 재사용
        TaskType.FUSION_CALCULATION: 4,
        TaskType.BOUNDARY_VALIDATION: 2,
        TaskType.GUARDRAIL_ANALYSIS: 2,
    }
    
    def __init__(
        self,
        task: TaskType,
        router: Optional[ModelRouter] = None
    ):
        self.task = task
        self.stage = self.TASK_TO_STAGE.get(task, 2)
        self.router = router or get_model_router()
        
        # Model 선택
        self.model_name, self.model_config = self.router.select_model_with_config(self.stage)
        
        # LLM 객체 생성
        self.llm = self._create_llm()
        
        logger.info(
            f"[ExternalLLM] 초기화: {task.value} "
            f"(Stage {self.stage}, Model: {self.model_name})"
        )
    
    def _create_llm(self) -> ChatOpenAI:
        """LLM 객체 생성"""
        # API 파라미터 빌드
        params = self.model_config.build_api_params(
            prompt="",  # 실제 호출 시 설정
            reasoning_effort="medium" if self.stage == 3 else None
        )
        
        return ChatOpenAI(
            model=self.model_name,
            temperature=params.get("temperature", 0.7),
            max_tokens=params.get("max_tokens", 4000),
            openai_api_key=params.get("api_key")
        )
    
    def estimate(
        self,
        question: str,
        context: Context,
        **kwargs
    ) -> Optional[EstimationResult]:
        """
        External 모드: 실제 LLM 호출하여 추정
        
        Returns:
            EstimationResult (완성된 추정 결과)
        """
        logger.info(f"[External Prior] API 호출 시작")
        
        # 프롬프트 생성
        prompt = self._build_prior_prompt(question, context)
        
        # LLM 호출
        response = self._call_llm(prompt)
        
        # 파싱
        result = self._parse_prior_response(response, question, context)
        
        logger.info(
            f"[External Prior] 완료: value={result.value}, "
            f"certainty={result.certainty}, source={result.source}"
        )
        
        return result
    
    def decompose(
        self,
        question: str,
        context: Context,
        budget: Budget,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        External 모드: Fermi 분해 실행
        
        Returns:
            분해 결과 (variables, formula, reasoning)
        """
        logger.info(f"[External Fermi] API 호출 시작")
        
        # 프롬프트 생성
        prompt = self._build_fermi_prompt(question, context, budget)
        
        # LLM 호출
        response = self._call_llm(prompt)
        
        # 파싱
        result = self._parse_fermi_response(response)
        
        logger.info(
            f"[External Fermi] 완료: {len(result.get('variables', []))}개 변수 식별"
        )
        
        return result
    
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Context,
        **kwargs
    ) -> str:
        """
        External 모드: LLM으로 확신도 평가
        
        Returns:
            certainty: "high", "medium", "low"
        """
        logger.info(f"[External Certainty] 평가 시작")
        
        prompt = self._build_certainty_prompt(question, value, context)
        response = self._call_llm(prompt)
        certainty = self._parse_certainty(response)
        
        logger.info(f"[External Certainty] 완료: {certainty}")
        return certainty
    
    def validate_boundary(
        self,
        value: Any,
        context: Context,
        **kwargs
    ) -> Dict[str, Any]:
        """
        External 모드: LLM으로 경계 검증
        
        Returns:
            검증 결과
        """
        logger.info(f"[External Boundary] 검증 시작")
        
        prompt = self._build_boundary_prompt(value, context)
        response = self._call_llm(prompt)
        result = self._parse_boundary_response(response)
        
        logger.info(f"[External Boundary] 완료: valid={result['is_valid']}")
        return result
    
    def is_native(self) -> bool:
        return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _call_llm(self, prompt: str) -> str:
        """LLM API 호출"""
        try:
            chain = ChatPromptTemplate.from_messages([
                ("system", "You are an expert market analyst and estimator."),
                ("user", "{prompt}")
            ]) | self.llm | StrOutputParser()
            
            response = chain.invoke({"prompt": prompt})
            return response
        
        except Exception as e:
            logger.error(f"[ExternalLLM] API 호출 실패: {e}")
            raise
    
    def _build_prior_prompt(self, question: str, context: Context) -> str:
        """Prior 추정 프롬프트 생성"""
        return f"""
Question: {question}

Context:
- Industry: {context.industry}
- Business Model: {context.business_model}
- Region: {context.region}
- Additional: {context.additional_info}

Task: Estimate the value for the question above.

Output format (JSON):
{{
    "value": <estimated_value>,
    "unit": "<unit>",
    "certainty": "high|medium|low",
    "reasoning": "<brief reasoning>"
}}
"""
    
    def _build_fermi_prompt(self, question: str, context: Context, budget: Budget) -> str:
        """Fermi 분해 프롬프트 생성"""
        return f"""
Question: {question}

Context:
- Industry: {context.industry}
- Business Model: {context.business_model}

Budget:
- Max variables: {budget.max_variables}
- Max depth: {budget.max_depth}

Task: Decompose the question into Fermi variables.

Output format (JSON):
{{
    "variables": [
        {{"name": "var1", "description": "...", "unit": "..."}}
    ],
    "formula": "<mathematical formula>",
    "reasoning": "<decomposition reasoning>"
}}
"""
    
    def _build_certainty_prompt(self, question: str, value: Any, context: Context) -> str:
        """확신도 평가 프롬프트"""
        return f"""
Question: {question}
Estimated Value: {value}
Context: {context.to_dict()}

Task: Evaluate your certainty in this estimate.

Output: high|medium|low
"""
    
    def _build_boundary_prompt(self, value: Any, context: Context) -> str:
        """경계 검증 프롬프트"""
        return f"""
Value: {value}
Context: {context.to_dict()}

Task: Validate if this value is within reasonable boundaries.

Output format (JSON):
{{
    "is_valid": true|false,
    "reason": "<reasoning>",
    "suggested_range": [<min>, <max>]
}}
"""
    
    def _parse_prior_response(
        self,
        response: str,
        question: str,
        context: Context
    ) -> EstimationResult:
        """Prior 응답 파싱"""
        try:
            data = json.loads(response)
            
            return EstimationResult(
                value=data["value"],
                unit=data.get("unit", "unknown"),
                source="Prior",
                certainty=data.get("certainty", "medium"),
                reasoning=data.get("reasoning", ""),
                cost={"stage": 2, "model": self.model_name}
            )
        
        except Exception as e:
            logger.warning(f"[ExternalLLM] 파싱 실패, 기본값 반환: {e}")
            return None
    
    def _parse_fermi_response(self, response: str) -> Dict[str, Any]:
        """Fermi 응답 파싱"""
        try:
            return json.loads(response)
        except Exception as e:
            logger.warning(f"[ExternalLLM] Fermi 파싱 실패: {e}")
            return {"variables": [], "formula": None, "reasoning": ""}
    
    def _parse_certainty(self, response: str) -> str:
        """확신도 파싱"""
        response = response.strip().lower()
        if response in ["high", "medium", "low"]:
            return response
        return "medium"
    
    def _parse_boundary_response(self, response: str) -> Dict[str, Any]:
        """경계 검증 파싱"""
        try:
            return json.loads(response)
        except:
            return {"is_valid": True, "reason": "파싱 실패", "suggested_range": None}


class ExternalLLMProvider(LLMProvider):
    """
    External LLM Provider
    
    Task별 적절한 External LLM 반환
    """
    
    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or get_model_router()
        logger.info("[ExternalLLMProvider] 초기화 (External 모드)")
    
    def get_llm(self, task: TaskType) -> BaseLLM:
        """
        Task별 ExternalLLM 반환
        
        Args:
            task: TaskType
        
        Returns:
            ExternalLLM 인스턴스 (Task별 모델 자동 선택)
        """
        logger.debug(f"[ExternalLLMProvider] {task.value} → ExternalLLM")
        return ExternalLLM(task, router=self.router)
    
    def is_native(self) -> bool:
        return False
    
    def get_mode_info(self) -> Dict[str, Any]:
        return {
            "mode": "external",
            "provider": "ExternalLLMProvider",
            "uses_api": True,
            "cost": "토큰당 과금 (Task별 모델 자동 선택)",
            "automation": True,
            "description": "RAG 검색 + API 호출 → 완성된 결과"
        }
```

---

### Phase 4: Provider 팩토리

#### 4.1 Provider 선택 로직

```python
# umis_rag/core/llm_provider_factory.py (신규)

from typing import Optional
from umis_rag.core.llm_interface import LLMProvider
from umis_rag.core.llm_cursor import CursorLLMProvider
from umis_rag.core.llm_external import ExternalLLMProvider
from umis_rag.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_llm_provider(mode: Optional[str] = None) -> LLMProvider:
    """
    LLMProvider 팩토리 함수
    
    Args:
        mode: LLM 모드 (None이면 settings.llm_mode 사용)
            - "cursor": CursorLLMProvider
            - 그 외: ExternalLLMProvider
    
    Returns:
        LLMProvider 구현체
    
    Example:
        >>> # .env: LLM_MODE=cursor
        >>> provider = get_llm_provider()
        >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate(question, context)
    """
    mode = mode or settings.llm_mode
    mode = mode.lower().strip()
    
    if mode == "cursor":
        logger.info("[LLMProviderFactory] CursorLLMProvider 선택")
        return CursorLLMProvider()
    
    else:
        logger.info(f"[LLMProviderFactory] ExternalLLMProvider 선택 (모델: {mode})")
        return ExternalLLMProvider()


# 싱글톤 인스턴스 (옵션)
_provider_instance: Optional[LLMProvider] = None


def get_default_llm_provider() -> LLMProvider:
    """
    기본 LLMProvider 반환 (싱글톤)
    
    Returns:
        LLMProvider 인스턴스
    """
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = get_llm_provider()
    return _provider_instance


def reset_llm_provider():
    """Provider 싱글톤 초기화 (테스트용)"""
    global _provider_instance
    _provider_instance = None
```

---

### Phase 5: Estimator 리팩터링

#### 5.1 PriorEstimator (Stage 2)

```python
# umis_rag/agents/estimator/prior_estimator.py (수정)

from typing import Optional
from umis_rag.core.llm_interface import LLMProvider, TaskType
from umis_rag.core.llm_provider_factory import get_default_llm_provider
from umis_rag.agents.estimator.models import EstimationResult, Context
import logging

logger = logging.getLogger(__name__)


class PriorEstimator:
    """
    Stage 2: Generative Prior
    
    v7.11.0: LLMProvider 인터페이스 기반 (완전 추상화)
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Args:
            llm_provider: LLMProvider 구현체 (None이면 기본 Provider)
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        
        # ❌ 제거: self._llm_mode, self.llm_mode property
        
        logger.info(
            f"[PriorEstimator] 초기화 "
            f"(Provider: {self.llm_provider.__class__.__name__})"
        )
    
    def estimate(
        self,
        question: str,
        context: Context,
        **kwargs
    ) -> Optional[EstimationResult]:
        """
        Stage 2: Generative Prior 추정
        
        Args:
            question: 추정 질문
            context: 컨텍스트
        
        Returns:
            EstimationResult 또는 None
        """
        logger.info(f"[Prior] 추정 시작: {question}")
        
        # ✅ LLM 획득 (분기 없음!)
        llm = self.llm_provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        # ✅ 추정 실행 (분기 없음!)
        result = llm.estimate(question, context, **kwargs)
        
        # Cursor 모드: None 반환 (Estimator가 처리)
        if result is None:
            logger.info("[Prior] Cursor 모드: 데이터 준비 완료")
            return None
        
        # External 모드: 결과 반환
        logger.info(
            f"[Prior] 완료: value={result.value}, "
            f"certainty={result.certainty}"
        )
        
        # Certainty 평가
        if result.certainty is None:
            certainty_llm = self.llm_provider.get_llm(TaskType.CERTAINTY_EVALUATION)
            result.certainty = certainty_llm.evaluate_certainty(
                question, result.value, context
            )
        
        return result
```

**핵심 변경**:
1. ❌ `llm_mode` property 완전 제거
2. ✅ `llm_provider` 의존성 주입
3. ✅ `llm_provider.get_llm(task)` 호출만
4. ✅ 분기 **0개**

#### 5.2 FermiEstimator (Stage 3)

```python
# umis_rag/agents/estimator/fermi_estimator.py (수정)

from typing import Optional, Dict, Any
from umis_rag.core.llm_interface import LLMProvider, TaskType
from umis_rag.core.llm_provider_factory import get_default_llm_provider
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common.budget import Budget
from umis_rag.agents.estimator.prior_estimator import PriorEstimator
import logging

logger = logging.getLogger(__name__)


class FermiEstimator:
    """
    Stage 3: Structural Explanation (Fermi Decomposition)
    
    v7.11.0: LLMProvider 인터페이스 기반 (완전 추상화)
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        prior_estimator: Optional[PriorEstimator] = None
    ):
        """
        Args:
            llm_provider: LLMProvider 구현체
            prior_estimator: PriorEstimator (변수 추정용)
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        self.prior_estimator = prior_estimator or PriorEstimator(self.llm_provider)
        
        # ❌ 제거: self._llm_mode, self.llm_mode property
        
        logger.info(
            f"[FermiEstimator] 초기화 "
            f"(Provider: {self.llm_provider.__class__.__name__})"
        )
    
    def decompose(
        self,
        question: str,
        context: Context,
        budget: Budget,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Stage 3: Fermi 분해
        
        Args:
            question: 분해할 질문
            context: 컨텍스트
            budget: 예산 제약
        
        Returns:
            분해 결과 또는 None (Cursor 모드)
        """
        logger.info(f"[Fermi] 분해 시작: {question}")
        
        # ✅ LLM 획득 (분기 없음!)
        llm = self.llm_provider.get_llm(TaskType.FERMI_DECOMPOSITION)
        
        # ✅ 분해 실행 (분기 없음!)
        decomposition = llm.decompose(question, context, budget, **kwargs)
        
        # Cursor 모드: None 반환
        if decomposition is None:
            logger.info("[Fermi] Cursor 모드: 분해 데이터 준비 완료")
            return None
        
        # External 모드: 변수 추정
        logger.info(f"[Fermi] {len(decomposition['variables'])}개 변수 추정 시작")
        
        # 변수 추정 (Stage 2 재사용)
        estimated_variables = self._estimate_variables(
            decomposition['variables'],
            context,
            budget
        )
        
        decomposition['estimated_variables'] = estimated_variables
        
        # 공식 계산
        if decomposition.get('formula'):
            final_value = self._calculate_formula(
                decomposition['formula'],
                estimated_variables
            )
            decomposition['final_value'] = final_value
        
        logger.info(
            f"[Fermi] 완료: {len(estimated_variables)}개 변수 추정, "
            f"최종값: {decomposition.get('final_value')}"
        )
        
        return decomposition
    
    def _estimate_variables(
        self,
        variables: list,
        context: Context,
        budget: Budget
    ) -> Dict[str, Any]:
        """
        변수 추정 (Stage 2 Prior 재사용)
        
        ✅ 분기 없음 (prior_estimator가 처리)
        """
        estimated = {}
        
        for var in variables:
            var_name = var['name']
            question = f"What is the {var['description']}?"
            
            # ✅ Prior 추정 (분기 없음!)
            result = self.prior_estimator.estimate(question, context)
            
            if result:
                estimated[var_name] = result.value
            else:
                # Cursor 모드 or 실패
                estimated[var_name] = None
        
        return estimated
    
    def _calculate_formula(
        self,
        formula: str,
        variables: Dict[str, Any]
    ) -> Optional[float]:
        """공식 계산"""
        try:
            # 간단한 eval (실제로는 안전한 파서 사용)
            for var_name, var_value in variables.items():
                if var_value is None:
                    return None
                formula = formula.replace(var_name, str(var_value))
            
            return eval(formula)
        
        except Exception as e:
            logger.error(f"[Fermi] 공식 계산 실패: {e}")
            return None
```

**핵심 변경**:
1. ❌ `llm_mode` 완전 제거
2. ✅ `llm_provider` 의존성 주입
3. ✅ 변수 추정 = `prior_estimator.estimate()` (Stage 2 재사용)
4. ✅ 분기 **0개**

#### 5.3 EstimatorRAG (메인)

```python
# umis_rag/agents/estimator/estimator.py (수정)

from typing import Optional
from umis_rag.core.llm_interface import LLMProvider
from umis_rag.core.llm_provider_factory import get_default_llm_provider
from umis_rag.agents.estimator.models import EstimationResult, Context
from umis_rag.agents.estimator.common.budget import Budget, create_standard_budget
from umis_rag.agents.estimator.evidence_collector import EvidenceCollector
from umis_rag.agents.estimator.prior_estimator import PriorEstimator
from umis_rag.agents.estimator.fermi_estimator import FermiEstimator
import logging

logger = logging.getLogger(__name__)


class EstimatorRAG:
    """
    Estimator Agent: 4-Stage Fusion Architecture
    
    v7.11.0: 완전 추상화 (LLMProvider 인터페이스 기반)
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        project_id: Optional[str] = None
    ):
        """
        Args:
            llm_provider: LLMProvider 구현체 (None이면 settings 기반)
            project_id: 프로젝트 ID
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        self.project_id = project_id
        
        # ❌ 제거: self.llm_mode
        
        # Stage별 컴포넌트 초기화 (모두 같은 provider)
        self.evidence_collector = EvidenceCollector(
            llm_provider=self.llm_provider,
            project_id=project_id
        )
        self.prior_estimator = PriorEstimator(
            llm_provider=self.llm_provider
        )
        self.fermi_estimator = FermiEstimator(
            llm_provider=self.llm_provider,
            prior_estimator=self.prior_estimator
        )
        
        logger.info(
            f"[EstimatorRAG] 초기화 완료 "
            f"(Provider: {self.llm_provider.__class__.__name__})"
        )
        logger.info(f"  모드: {self._get_mode_display()}")
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None,
        budget: Optional[Budget] = None,
        **kwargs
    ) -> EstimationResult:
        """
        4-Stage Fusion 추정
        
        Args:
            question: 추정 질문
            context: 컨텍스트 (Optional)
            budget: 예산 제약 (Optional)
        
        Returns:
            EstimationResult (완성된 추정 결과)
        """
        logger.info("=" * 60)
        logger.info(f"[Estimator] 4-Stage Fusion 추정 시작")
        logger.info(f"  질문: {question}")
        logger.info("=" * 60)
        
        # 기본값
        context = context or Context()
        budget = budget or create_standard_budget()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 1: Evidence Collection
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 1] Evidence Collection")
        evidence = self.evidence_collector.collect(question, context, budget)
        
        # Early Return: Literal 발견
        if evidence.get("literal"):
            logger.info("  ✅ Early Return: Literal 증거 발견")
            return EstimationResult(
                value=evidence["literal"]["value"],
                source="Literal",
                certainty="high",
                reasoning=evidence["literal"]["reasoning"],
                cost={"stage": 1, "method": "literal"}
            )
        
        # Early Return: Direct RAG
        if evidence.get("direct_rag"):
            logger.info("  ✅ Early Return: Direct RAG 증거 발견")
            return EstimationResult(
                value=evidence["direct_rag"]["value"],
                source="DirectRAG",
                certainty="high",
                reasoning=evidence["direct_rag"]["reasoning"],
                cost={"stage": 1, "method": "direct_rag"}
            )
        
        # Early Return: Validator
        if evidence.get("validator"):
            logger.info("  ✅ Early Return: Validator 데이터 발견")
            return EstimationResult(
                value=evidence["validator"]["value"],
                source="Validator",
                certainty="high",
                reasoning=evidence["validator"]["reasoning"],
                cost={"stage": 1, "method": "validator"}
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 2: Generative Prior
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 2] Generative Prior")
        
        # ✅ Prior 추정 (분기 없음!)
        prior_result = self.prior_estimator.estimate(question, context)
        
        # Cursor 모드: None 반환 → Cursor 포맷 응답
        if prior_result is None:
            logger.info("  [Cursor] Stage 2 데이터 준비 완료")
            return self._prepare_cursor_response(
                stage=2,
                question=question,
                context=context,
                evidence=evidence
            )
        
        # External 모드: certainty 체크
        if prior_result.certainty == "high":
            logger.info("  ✅ Early Return: High certainty")
            return prior_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 3: Structural Explanation
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 3] Structural Explanation (Fermi)")
        
        # ✅ Fermi 분해 (분기 없음!)
        fermi_result = self.fermi_estimator.decompose(
            question, context, budget
        )
        
        # Cursor 모드: None 반환
        if fermi_result is None:
            logger.info("  [Cursor] Stage 3 데이터 준비 완료")
            return self._prepare_cursor_response(
                stage=3,
                question=question,
                context=context,
                evidence=evidence,
                prior_result=prior_result
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 4: Fusion & Validation
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 4] Fusion & Validation")
        
        final_result = self._fuse_results(
            evidence, prior_result, fermi_result
        )
        
        logger.info("=" * 60)
        logger.info(f"[Estimator] 추정 완료")
        logger.info(f"  최종값: {final_result.value}")
        logger.info(f"  Source: {final_result.source}")
        logger.info(f"  Certainty: {final_result.certainty}")
        logger.info("=" * 60)
        
        return final_result
    
    def _prepare_cursor_response(
        self,
        stage: int,
        question: str,
        context: Context,
        evidence: dict,
        prior_result: Optional[EstimationResult] = None,
        **kwargs
    ) -> dict:
        """
        Cursor 모드: 포맷된 응답 생성
        
        Returns:
            dict (Cursor Composer가 읽을 수 있는 포맷)
        """
        return {
            "mode": "cursor",
            "stage_reached": stage,
            "question": question,
            "context": context.to_dict(),
            "evidence": evidence,
            "prior_result": prior_result.to_dict() if prior_result else None,
            "instruction": (
                f"[Stage {stage}] 위 데이터를 바탕으로 추정을 완료해주세요.\n"
                f"Evidence: {len(evidence)}개 소스\n"
                f"Prior: {prior_result.value if prior_result else 'N/A'}"
            )
        }
    
    def _fuse_results(
        self,
        evidence: dict,
        prior_result: EstimationResult,
        fermi_result: dict
    ) -> EstimationResult:
        """
        Stage 4: 결과 융합
        
        가중 평균 또는 우선순위 기반
        """
        # 간단한 구현: Fermi 우선
        if fermi_result.get("final_value"):
            return EstimationResult(
                value=fermi_result["final_value"],
                source="Fusion",
                certainty="medium",
                reasoning=f"Fermi 분해 기반 ({len(fermi_result['variables'])}개 변수)",
                decomposition=fermi_result,
                cost={"stage": 4, "method": "fermi_fusion"}
            )
        
        # Fallback: Prior 결과
        return prior_result
    
    def _get_mode_display(self) -> str:
        """모드 디스플레이 (로깅용)"""
        info = self.llm_provider.get_mode_info()
        return f"{info['mode']} ({info['description']})"
```

**핵심 변경**:
1. ❌ `self.llm_mode` 완전 제거
2. ✅ `llm_provider` 의존성 주입
3. ✅ 모든 Stage 컴포넌트에 같은 `llm_provider` 전달
4. ✅ Cursor 모드 처리: `None` 반환 시 `_prepare_cursor_response()` 호출
5. ✅ 분기 **0개**

---

### Phase 6: 기타 컴포넌트

#### 6.1 EvidenceCollector, SourceCollector, BoundaryValidator 등

**동일한 패턴 적용**:

```python
class EvidenceCollector:
    def __init__(self, llm_provider: Optional[LLMProvider] = None, ...):
        self.llm_provider = llm_provider or get_default_llm_provider()
        # ❌ llm_mode 제거

class SourceCollector:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or get_default_llm_provider()
        # ❌ llm_mode 제거

class BoundaryValidator:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or get_default_llm_provider()
        # ❌ llm_mode 제거
```

---

## 🧪 테스트 계획

### Phase 7: 단위 테스트

```python
# tests/unit/test_llm_interface_v7_11_0.py (신규)

import pytest
from umis_rag.core.llm_interface import TaskType
from umis_rag.core.llm_cursor import CursorLLMProvider
from umis_rag.core.llm_external import ExternalLLMProvider
from umis_rag.core.llm_provider_factory import get_llm_provider
from umis_rag.agents.estimator.models import Context


class TestCursorLLM:
    """CursorLLM 테스트"""
    
    def test_cursor_provider_initialization(self):
        """CursorLLMProvider 초기화"""
        provider = CursorLLMProvider()
        assert provider.is_native() is True
    
    def test_cursor_llm_estimate_returns_none(self):
        """CursorLLM.estimate()는 None 반환"""
        provider = CursorLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        result = llm.estimate("What is LTV?", Context())
        assert result is None  # Cursor는 None 반환
    
    def test_cursor_llm_decompose_returns_none(self):
        """CursorLLM.decompose()는 None 반환"""
        provider = CursorLLMProvider()
        llm = provider.get_llm(TaskType.FERMI_DECOMPOSITION)
        
        from umis_rag.agents.estimator.common.budget import create_fast_budget
        result = llm.decompose("What is TAM?", Context(), create_fast_budget())
        assert result is None


class TestExternalLLM:
    """ExternalLLM 테스트"""
    
    @pytest.mark.skipif(
        os.getenv("LLM_MODE") == "cursor",
        reason="External LLM 테스트는 External 모드 필요"
    )
    def test_external_provider_initialization(self):
        """ExternalLLMProvider 초기화"""
        provider = ExternalLLMProvider()
        assert provider.is_native() is False
    
    @pytest.mark.skipif(
        os.getenv("LLM_MODE") == "cursor",
        reason="External LLM 테스트"
    )
    def test_external_llm_estimate_returns_result(self):
        """ExternalLLM.estimate()는 EstimationResult 반환"""
        provider = ExternalLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        result = llm.estimate("What is average SaaS churn rate?", Context(industry="SaaS"))
        
        assert result is not None
        assert result.value is not None
        assert result.source == "Prior"
        assert result.certainty in ["high", "medium", "low"]


class TestLLMProviderFactory:
    """LLMProviderFactory 테스트"""
    
    def test_factory_returns_cursor_provider_for_cursor_mode(self):
        """LLM_MODE=cursor → CursorLLMProvider"""
        provider = get_llm_provider(mode="cursor")
        assert isinstance(provider, CursorLLMProvider)
        assert provider.is_native() is True
    
    def test_factory_returns_external_provider_for_other_modes(self):
        """LLM_MODE=gpt-4o-mini → ExternalLLMProvider"""
        provider = get_llm_provider(mode="gpt-4o-mini")
        assert isinstance(provider, ExternalLLMProvider)
        assert provider.is_native() is False
```

### Phase 8: 통합 테스트

```python
# tests/integration/test_estimator_abstraction_v7_11_0.py (신규)

import pytest
from umis_rag.agents.estimator.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.core.llm_provider_factory import get_llm_provider


class TestEstimatorAbstraction:
    """Estimator 추상화 통합 테스트"""
    
    def test_estimator_with_cursor_provider(self):
        """Cursor Provider로 Estimator 실행"""
        provider = get_llm_provider(mode="cursor")
        estimator = EstimatorRAG(llm_provider=provider)
        
        result = estimator.estimate(
            "What is average SaaS LTV?",
            context=Context(industry="SaaS")
        )
        
        # Cursor 모드: dict 반환
        assert isinstance(result, dict)
        assert result["mode"] == "cursor"
        assert "question" in result
        assert "instruction" in result
    
    @pytest.mark.skipif(
        os.getenv("LLM_MODE") == "cursor",
        reason="External LLM 테스트"
    )
    def test_estimator_with_external_provider(self):
        """External Provider로 Estimator 실행"""
        provider = get_llm_provider(mode="gpt-4o-mini")
        estimator = EstimatorRAG(llm_provider=provider)
        
        result = estimator.estimate(
            "What is average SaaS churn rate?",
            context=Context(industry="SaaS")
        )
        
        # External 모드: EstimationResult 반환
        from umis_rag.agents.estimator.models import EstimationResult
        assert isinstance(result, EstimationResult)
        assert result.value is not None
        assert result.source in ["Literal", "DirectRAG", "Validator", "Prior", "Fermi", "Fusion"]
    
    def test_estimator_no_llm_mode_in_code(self):
        """Estimator 코드에 llm_mode 참조 없음 확인"""
        estimator = EstimatorRAG()
        
        # ❌ llm_mode 속성 없어야 함
        assert not hasattr(estimator, "llm_mode")
        assert not hasattr(estimator, "_llm_mode")
        
        # ✅ llm_provider 속성 존재
        assert hasattr(estimator, "llm_provider")
```

### Phase 9: E2E 테스트

```python
# tests/e2e/test_estimator_e2e_abstraction_v7_11_0.py (신규)

import pytest
from umis_rag.agents.estimator.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common.budget import create_standard_budget


class TestE2EAbstraction:
    """E2E 테스트: 완전 추상화"""
    
    def test_e2e_cursor_mode_full_workflow(self):
        """Cursor 모드: 전체 워크플로우"""
        estimator = EstimatorRAG()  # 기본 Provider (settings 기반)
        
        result = estimator.estimate(
            "What is Spotify's annual revenue?",
            context=Context(
                industry="Music Streaming",
                region="Global"
            ),
            budget=create_standard_budget()
        )
        
        # Cursor: dict 응답 (Composer가 처리)
        if isinstance(result, dict) and result.get("mode") == "cursor":
            assert "stage_reached" in result
            assert "evidence" in result
            pytest.skip("Cursor 모드: Composer 처리 필요")
    
    @pytest.mark.skipif(
        os.getenv("LLM_MODE") == "cursor",
        reason="External LLM 필요"
    )
    def test_e2e_external_mode_full_workflow(self):
        """External 모드: 전체 워크플로우"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            "What is average SaaS CAC?",
            context=Context(
                industry="SaaS",
                business_model="B2B"
            ),
            budget=create_standard_budget()
        )
        
        # External: EstimationResult
        from umis_rag.agents.estimator.models import EstimationResult
        assert isinstance(result, EstimationResult)
        assert result.value is not None
        assert result.source in ["Literal", "DirectRAG", "Validator", "Prior", "Fermi", "Fusion"]
        assert result.certainty in ["high", "medium", "low"]
```

---

## 📊 마이그레이션 체크리스트

### Phase 10: 점진적 마이그레이션

| 단계 | 작업 | 소요 시간 | 상태 |
|------|------|----------|------|
| **1. 인터페이스 정의** | | 4시간 | ⏸️ |
| 1.1 | `llm_interface.py` (BaseLLM, LLMProvider, TaskType) | 2시간 | ⏸️ |
| 1.2 | 인터페이스 단위 테스트 | 1시간 | ⏸️ |
| 1.3 | 문서화 (Docstring, 예시) | 1시간 | ⏸️ |
| **2. Cursor 구현** | | 3시간 | ⏸️ |
| 2.1 | `llm_cursor.py` (CursorLLM, CursorLLMProvider) | 2시간 | ⏸️ |
| 2.2 | Cursor 단위 테스트 | 1시간 | ⏸️ |
| **3. External 구현** | | 5시간 | ⏸️ |
| 3.1 | `llm_external.py` (ExternalLLM, ExternalLLMProvider) | 3시간 | ⏸️ |
| 3.2 | 프롬프트 템플릿 (Prior, Fermi, Certainty, Boundary) | 1시간 | ⏸️ |
| 3.3 | External 단위 테스트 | 1시간 | ⏸️ |
| **4. Provider 팩토리** | | 2시간 | ⏸️ |
| 4.1 | `llm_provider_factory.py` (get_llm_provider, 싱글톤) | 1시간 | ⏸️ |
| 4.2 | 팩토리 단위 테스트 | 1시간 | ⏸️ |
| **5. PriorEstimator 리팩터링** | | 3시간 | ⏸️ |
| 5.1 | `llm_mode` 제거, `llm_provider` 주입 | 1.5시간 | ⏸️ |
| 5.2 | 통합 테스트 (Cursor + External) | 1시간 | ⏸️ |
| 5.3 | 회귀 테스트 | 0.5시간 | ⏸️ |
| **6. FermiEstimator 리팩터링** | | 3시간 | ⏸️ |
| 6.1 | `llm_mode` 제거, `llm_provider` 주입 | 1.5시간 | ⏸️ |
| 6.2 | 변수 추정 = Prior 재사용 확인 | 1시간 | ⏸️ |
| 6.3 | 통합 테스트 | 0.5시간 | ⏸️ |
| **7. EstimatorRAG 리팩터링** | | 4시간 | ⏸️ |
| 7.1 | `llm_mode` 제거, `llm_provider` 주입 | 2시간 | ⏸️ |
| 7.2 | `_prepare_cursor_response()` 구현 | 1시간 | ⏸️ |
| 7.3 | 4-Stage 워크플로우 통합 테스트 | 1시간 | ⏸️ |
| **8. 기타 컴포넌트** | | 4시간 | ⏸️ |
| 8.1 | EvidenceCollector | 1시간 | ⏸️ |
| 8.2 | SourceCollector | 1시간 | ⏸️ |
| 8.3 | BoundaryValidator | 1시간 | ⏸️ |
| 8.4 | GuardrailAnalyzer | 1시간 | ⏸️ |
| **9. E2E 테스트** | | 3시간 | ⏸️ |
| 9.1 | Cursor 모드 E2E (10개 시나리오) | 1.5시간 | ⏸️ |
| 9.2 | External 모드 E2E (10개 시나리오) | 1.5시간 | ⏸️ |
| **10. 하위 호환성** | | 2시간 | ⏸️ |
| 10.1 | `compat.py` Adapter (llm_mode property → DeprecationWarning) | 1시간 | ⏸️ |
| 10.2 | 레거시 코드 테스트 | 1시간 | ⏸️ |
| **11. 문서화** | | 2시간 | ⏸️ |
| 11.1 | `LLM_INTERFACE_GUIDE_v7_11_0.md` | 1시간 | ⏸️ |
| 11.2 | `MIGRATION_FROM_LLM_MODE_v7_11_0.md` | 1시간 | ⏸️ |
| **12. 최종 검증** | | 2시간 | ⏸️ |
| 12.1 | 전체 테스트 실행 (Native + External) | 1시간 | ⏸️ |
| 12.2 | 성능 벤치마크 (속도, 비용 변화 없음 확인) | 1시간 | ⏸️ |
| **총 소요 시간** | | **37시간 (약 5일)** | ⏸️ |

---

## 🎯 핵심 성공 지표

### 코드 품질

1. **Estimator 순수성**
   - ✅ `llm_mode` 참조: **61곳 → 0곳**
   - ✅ 분기문 (`if llm_mode`): **완전 제거**
   - ✅ 의존성: 인터페이스만 의존

2. **Dependency Inversion**
   - ✅ High-level → Interface ← Low-level
   - ✅ Mock 주입 가능 (테스트)

3. **단일 책임 원칙**
   - ✅ Estimator: 비즈니스 로직
   - ✅ LLMProvider: Infrastructure
   - ✅ ModelRouter: Model 선택

### 테스트 커버리지

- ✅ 단위 테스트: 90%+
- ✅ 통합 테스트: Cursor + External 각 10개
- ✅ E2E 테스트: 20개 시나리오
- ✅ 회귀 테스트: 기존 기능 100% 유지

### 성능

- ✅ 속도: 변화 없음 (±5% 이내)
- ✅ 비용: 변화 없음
- ✅ API 호출 횟수: 동일

---

## ⚠️ 위험 요소 및 대응

### 위험 1: Cursor 모드 복잡도 증가

**문제**: Cursor는 실제 LLM 호출 불가 → `None` 반환 + 로깅

**대응**:
1. `CursorLLM`은 단순화 (포맷만)
2. `EstimatorRAG._prepare_cursor_response()` 중앙화
3. 문서 명확화 (Cursor = "데이터 준비")

### 위험 2: External LLM 프롬프트 품질

**문제**: 프롬프트가 부실하면 결과 품질 저하

**대응**:
1. 기존 프롬프트 재사용 (검증됨)
2. 프롬프트 템플릿화 (`_build_*_prompt`)
3. 프롬프트 단위 테스트

### 위험 3: 대규모 리팩터링 리스크

**문제**: 61곳 변경 → 버그 가능성

**대응**:
1. **점진적 마이그레이션** (Stage별)
2. **회귀 테스트 자동화**
3. **하위 호환성** (`compat.py`)

### 위험 4: 개발 시간 초과

**문제**: 예상 37시간 (5일)

**대응**:
1. 우선순위: Core → 테스트 → 기타
2. 병렬화: 인터페이스 + Cursor 동시 진행
3. 스킵 가능: 일부 기타 컴포넌트 (EvidenceCollector 등)

---

## 📈 예상 효과

### 1. Clean Architecture 달성

```
Before:
  Estimator (61곳 분기) ──┐
                          ├─ llm_mode 의존
  Infrastructure ─────────┘

After:
  Estimator ──→ Interface ←── Infrastructure
  (분기 0곳)      ↑               ↑
                  └─ Dependency Inversion
```

### 2. 유지보수성 향상

```bash
# Native ↔ External 전환
# Before: 코드 수정 필요 (61곳)
# After: .env만 변경

LLM_MODE=cursor  →  LLM_MODE=gpt-4o-mini
```

### 3. 테스트 용이성

```python
# Mock 주입
mock_provider = MockLLMProvider()
estimator = EstimatorRAG(llm_provider=mock_provider)

# 완벽한 격리 테스트
```

### 4. 확장성

```python
# 새 LLM 타입 추가 (예: Claude)
class ClaudeLLMProvider(LLMProvider):
    def get_llm(self, task):
        return ClaudeLLM(task)

# Estimator 코드 수정: 0줄
```

---

## 📚 다음 단계

1. **✅ 사용자 승인**
   - 이 계획 검토 및 피드백

2. **⏸️ Phase 1 시작: 인터페이스 정의**
   - `llm_interface.py` 구현
   - 단위 테스트 작성

3. **⏸️ Phase 2-4: Provider 구현**
   - Cursor + External + Factory

4. **⏸️ Phase 5-7: Estimator 리팩터링**
   - Prior → Fermi → Main

5. **⏸️ Phase 8-9: 기타 컴포넌트 + E2E**

6. **⏸️ Phase 10-12: 하위 호환 + 문서 + 검증**

---

## 💬 질문 및 피드백

**이 계획에 대해**:

1. **Phase 순서** 적절한가?
2. **Cursor 구현** (None 반환 + 로깅) 동의하는가?
3. **External 프롬프트** 템플릿화 방식 괜찮은가?
4. **총 37시간** (5일) 일정 합리적인가?
5. **우선순위** 조정 필요한 부분 있는가?

**피드백 주시면 즉시 반영하겠습니다!** 🚀

---

**작성**: 2025-11-26
**v7.11.0 완전 추상화 구현 계획** 🎯
