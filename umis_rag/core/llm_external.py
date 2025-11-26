"""
External LLM Implementation for UMIS RAG System

External (OpenAI, Anthropic 등) 모드 구현

특징:
- 실제 API 호출
- 완성된 결과 반환
- 토큰당 과금
- 완전 자동화 가능

작성: 2025-11-26
"""

from typing import Optional, Dict, Any
from umis_rag.core.llm_interface import BaseLLM, LLMProvider, TaskType, TASK_TO_STAGE
from umis_rag.core.model_router import ModelRouter, get_model_router
from umis_rag.core.model_configs import model_config_manager
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
import json
import re

logger = logging.getLogger(__name__)


class ExternalLLM(BaseLLM):
    """
    External LLM 구현 (OpenAI, Anthropic 등)
    
    특징:
    - 실제 API 호출
    - 완성된 결과 반환
    - 토큰당 과금
    - Task별 모델 자동 선택 (ModelRouter)
    
    설계:
    - Task → Stage → Model 매핑
    - 프롬프트 자동 생성
    - 응답 파싱
    
    Example:
        >>> llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate("What is LTV?", context)
        >>> result.value  # 1000 (완성된 추정)
    """
    
    def __init__(
        self,
        task: TaskType,
        router: Optional[ModelRouter] = None
    ):
        """
        Args:
            task: TaskType
            router: ModelRouter (None이면 기본 Router)
        """
        self.task = task
        self.stage = TASK_TO_STAGE.get(task, 2)  # 기본 Stage 2
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
        )
    
    def estimate(
        self,
        question: str,
        context: Any,
        **kwargs
    ) -> Optional[Any]:
        """
        External 모드: 실제 LLM 호출하여 추정
        
        Args:
            question: 추정 질문
            context: 컨텍스트
        
        Returns:
            EstimationResult (완성된 추정 결과)
        
        Note:
            실제 구현에서는 umis_rag.agents.estimator.models.EstimationResult 사용
            여기서는 Dict로 반환 (간소화)
        """
        logger.info(f"[External Prior] API 호출 시작")
        
        # 프롬프트 생성
        prompt = self._build_prior_prompt(question, context)
        
        # LLM 호출
        response = self._call_llm(prompt)
        
        # 파싱
        result = self._parse_prior_response(response, question, context)
        
        if result:
            logger.info(
                f"[External Prior] 완료: value={result.get('value')}, "
                f"certainty={result.get('certainty')}"
            )
        else:
            logger.warning(f"[External Prior] 파싱 실패")
        
        return result
    
    def decompose(
        self,
        question: str,
        context: Any,
        budget: Any,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        External 모드: Fermi 분해 실행
        
        Args:
            question: 분해할 질문
            context: 컨텍스트
            budget: 예산
        
        Returns:
            분해 결과 Dict
        """
        logger.info(f"[External Fermi] API 호출 시작")
        
        # 프롬프트 생성
        prompt = self._build_fermi_prompt(question, context, budget)
        
        # LLM 호출
        response = self._call_llm(prompt)
        
        # 파싱
        result = self._parse_fermi_response(response)
        
        if result:
            logger.info(
                f"[External Fermi] 완료: {len(result.get('variables', []))}개 변수 식별"
            )
        else:
            logger.warning(f"[External Fermi] 파싱 실패")
        
        return result
    
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Any,
        **kwargs
    ) -> str:
        """
        External 모드: LLM으로 확신도 평가
        
        Args:
            question: 질문
            value: 값
            context: 컨텍스트
        
        Returns:
            certainty: "high" | "medium" | "low"
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
        context: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        External 모드: LLM으로 경계 검증
        
        Args:
            value: 값
            context: 컨텍스트
        
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
        """External 모드"""
        return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LLM 호출
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 프롬프트 생성
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _build_prior_prompt(self, question: str, context: Any) -> str:
        """Prior 추정 프롬프트"""
        context_str = self._format_context(context)
        
        return f"""
You are an expert market analyst. Estimate the value for the following question.

Question: {question}

Context:
{context_str}

Task: Provide an estimation with your certainty level.

Output format (JSON):
{{
    "value": <estimated_value (number)>,
    "unit": "<unit (e.g., USD, %, users)>",
    "certainty": "high|medium|low",
    "reasoning": "<brief reasoning (1-2 sentences)>"
}}

Example:
{{
    "value": 5.0,
    "unit": "%",
    "certainty": "high",
    "reasoning": "Based on industry benchmarks, SaaS churn rate is typically 5-7%."
}}
"""
    
    def _build_fermi_prompt(self, question: str, context: Any, budget: Any) -> str:
        """Fermi 분해 프롬프트"""
        context_str = self._format_context(context)
        budget_str = self._format_budget(budget)
        
        return f"""
You are an expert at Fermi estimation. Decompose the following question into variables.

Question: {question}

Context:
{context_str}

Budget Constraints:
{budget_str}

Task: Break down the question into 3-5 key variables and provide a formula.

Output format (JSON):
{{
    "variables": [
        {{"name": "var1", "description": "description of var1", "unit": "unit"}},
        {{"name": "var2", "description": "description of var2", "unit": "unit"}}
    ],
    "formula": "var1 * var2 * ...",
    "reasoning": "<decomposition reasoning>"
}}

Example:
{{
    "variables": [
        {{"name": "total_users", "description": "Total number of users", "unit": "users"}},
        {{"name": "arpu", "description": "Average revenue per user", "unit": "USD"}}
    ],
    "formula": "total_users * arpu",
    "reasoning": "Revenue = number of users * average revenue per user"
}}
"""
    
    def _build_certainty_prompt(self, question: str, value: Any, context: Any) -> str:
        """확신도 평가 프롬프트"""
        context_str = self._format_context(context)
        
        return f"""
Evaluate your certainty in the following estimation.

Question: {question}
Estimated Value: {value}
Context: {context_str}

Task: Rate your certainty as "high", "medium", or "low".

Criteria:
- high: Based on reliable data/benchmarks, confident in estimate
- medium: Reasonable estimate but some uncertainty
- low: Rough estimate, significant uncertainty

Output: Just the certainty level (high/medium/low)
"""
    
    def _build_boundary_prompt(self, value: Any, context: Any) -> str:
        """경계 검증 프롬프트"""
        context_str = self._format_context(context)
        
        return f"""
Validate if the following value is within reasonable boundaries.

Value: {value}
Context: {context_str}

Task: Check if the value is realistic and provide feedback.

Output format (JSON):
{{
    "is_valid": true|false,
    "reason": "<reasoning>",
    "suggested_range": [<min>, <max>] or null
}}

Example:
{{
    "is_valid": true,
    "reason": "Value is within typical range for this industry",
    "suggested_range": null
}}
"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 응답 파싱
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _parse_prior_response(
        self,
        response: str,
        question: str,
        context: Any
    ) -> Optional[Dict[str, Any]]:
        """Prior 응답 파싱"""
        try:
            # JSON 추출 시도
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            # EstimationResult 형태로 변환 (간소화)
            return {
                "value": data.get("value"),
                "unit": data.get("unit", "unknown"),
                "source": "Prior",
                "certainty": data.get("certainty", "medium"),
                "reasoning": data.get("reasoning", ""),
                "cost": {"stage": 2, "model": self.model_name}
            }
        
        except Exception as e:
            logger.warning(f"[ExternalLLM] Prior 파싱 실패: {e}")
            logger.debug(f"  Response: {response[:200]}...")
            return None
    
    def _parse_fermi_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Fermi 응답 파싱"""
        try:
            # JSON 추출 시도
            json_match = re.search(r'\{.+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            return {
                "variables": data.get("variables", []),
                "formula": data.get("formula"),
                "reasoning": data.get("reasoning", "")
            }
        
        except Exception as e:
            logger.warning(f"[ExternalLLM] Fermi 파싱 실패: {e}")
            logger.debug(f"  Response: {response[:200]}...")
            return None
    
    def _parse_certainty(self, response: str) -> str:
        """확신도 파싱"""
        response = response.strip().lower()
        
        # "high", "medium", "low" 추출
        if "high" in response:
            return "high"
        elif "low" in response:
            return "low"
        elif "medium" in response:
            return "medium"
        
        # 기본값
        return "medium"
    
    def _parse_boundary_response(self, response: str) -> Dict[str, Any]:
        """경계 검증 파싱"""
        try:
            # JSON 추출 시도
            json_match = re.search(r'\{.+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            return {
                "is_valid": data.get("is_valid", True),
                "reason": data.get("reason", ""),
                "suggested_range": data.get("suggested_range")
            }
        
        except Exception as e:
            logger.warning(f"[ExternalLLM] Boundary 파싱 실패: {e}")
            return {
                "is_valid": True,
                "reason": "파싱 실패, 기본 통과",
                "suggested_range": None
            }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _format_context(self, context: Any) -> str:
        """컨텍스트 포맷팅"""
        if context is None:
            return "No context provided"
        
        if hasattr(context, "to_dict"):
            ctx_dict = context.to_dict()
        elif isinstance(context, dict):
            ctx_dict = context
        else:
            return str(context)
        
        # 주요 필드만 포맷
        parts = []
        if ctx_dict.get("industry"):
            parts.append(f"- Industry: {ctx_dict['industry']}")
        if ctx_dict.get("business_model"):
            parts.append(f"- Business Model: {ctx_dict['business_model']}")
        if ctx_dict.get("region"):
            parts.append(f"- Region: {ctx_dict['region']}")
        if ctx_dict.get("additional_info"):
            parts.append(f"- Additional: {ctx_dict['additional_info']}")
        
        return "\n".join(parts) if parts else str(ctx_dict)
    
    def _format_budget(self, budget: Any) -> str:
        """예산 포맷팅"""
        if budget is None:
            return "No budget constraints"
        
        if hasattr(budget, "__dict__"):
            budget_dict = budget.__dict__
        elif isinstance(budget, dict):
            budget_dict = budget
        else:
            return str(budget)
        
        parts = []
        if "max_variables" in budget_dict:
            parts.append(f"- Max variables: {budget_dict['max_variables']}")
        if "max_depth" in budget_dict:
            parts.append(f"- Max depth: {budget_dict['max_depth']}")
        if "max_llm_calls" in budget_dict:
            parts.append(f"- Max LLM calls: {budget_dict['max_llm_calls']}")
        
        return "\n".join(parts) if parts else str(budget_dict)


class ExternalLLMProvider(LLMProvider):
    """
    External LLM Provider
    
    Task별 적절한 External LLM 반환
    
    특징:
    - Task → Stage → Model 자동 선택
    - ModelRouter 기반
    - 완전 자동화
    
    Example:
        >>> provider = ExternalLLMProvider()
        >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate("What is LTV?", context)
    """
    
    def __init__(self, router: Optional[ModelRouter] = None):
        """
        Args:
            router: ModelRouter (None이면 기본 Router)
        """
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
        """External 모드"""
        return False
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        External 모드 정보
        
        Returns:
            모드 정보 dict
        """
        return {
            "mode": "external",
            "provider": "ExternalLLMProvider",
            "uses_api": True,
            "cost": "토큰당 과금 (Task별 모델 자동 선택)",
            "automation": True,
            "description": "RAG 검색 + API 호출 → 완성된 결과"
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Usage Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
사용 가이드
==========

1. 직접 사용
-----------

from umis_rag.core.llm_external import ExternalLLMProvider

provider = ExternalLLMProvider()
llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)

result = llm.estimate("What is LTV?", context)
# result = {"value": 1000, "unit": "USD", ...} (완성된 추정)


2. Estimator에서 사용
--------------------

class EstimatorRAG:
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider or ExternalLLMProvider()
    
    def estimate(self, question, context):
        llm = self.llm_provider.get_llm(TaskType.PRIOR_ESTIMATION)
        result = llm.estimate(question, context)
        
        # External 모드: 완성된 결과
        return result


3. External 모드 특징
--------------------

- LLM 호출: 실제 API 호출
- 비용: 토큰당 과금 ($0.01-0.10/요청)
- 속도: 2-10초
- 정확도: 모델 의존

- 장점:
  - 완전 자동화
  - 프로그래밍 가능
  - 높은 품질

- 단점:
  - 비용 발생
  - API 키 필요
  - 인터넷 필요


4. Task별 모델 선택
------------------

ExternalLLM은 Task → Stage → Model 자동 선택:

- Stage 1 (Evidence): gpt-4.1-nano
- Stage 2 (Prior): gpt-4.1-nano
- Stage 3 (Fermi): gpt-4o-mini
- Stage 4 (Fusion): 계산만 (LLM 불필요)

ModelRouter가 자동 선택합니다.
"""
