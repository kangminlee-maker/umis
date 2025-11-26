"""
LLM Interface Module for UMIS RAG System

완전 추상화 아키텍처 (v7.11.0)

목적:
- Native/External 분기를 비즈니스 레이어에서 완전히 제거
- 의존성 역전 (Dependency Inversion Principle)
- Estimator는 LLMProvider 인터페이스만 의존

작성: 2025-11-26
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Task Types
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TaskType(Enum):
    """
    LLM 작업 타입 (Stage 기반)
    
    v7.11.0: Estimator 4-Stage Fusion Architecture
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stage 1: Evidence Collection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVIDENCE_COLLECTION = "evidence_collection"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stage 2: Generative Prior
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    PRIOR_ESTIMATION = "prior_estimation"
    CERTAINTY_EVALUATION = "certainty_evaluation"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stage 3: Structural Explanation (Fermi)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    FERMI_DECOMPOSITION = "fermi_decomposition"
    FERMI_VARIABLE_ESTIMATION = "fermi_variable_estimation"  # = Stage 2 재사용
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stage 4: Fusion & Validation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    FUSION_CALCULATION = "fusion_calculation"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 기타 (Boundary, Guardrail 등)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    BOUNDARY_VALIDATION = "boundary_validation"
    GUARDRAIL_ANALYSIS = "guardrail_analysis"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models (EstimationResult, Context는 기존 사용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# EstimationResult, Context, Budget는 기존 models.py, common/budget.py 사용
# 여기서는 import만 (실제 사용 시)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM Interfaces
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class BaseLLM(ABC):
    """
    LLM 추상 인터페이스
    
    모든 LLM 구현체(Cursor, External)가 준수해야 할 인터페이스
    
    설계 원칙:
    - Estimator 비즈니스 로직은 이 인터페이스만 의존
    - Native(Cursor) vs External 분기는 구현체에서만 처리
    - 메서드 시그니처는 Estimator Stage에 맞춤
    
    Example:
        >>> provider = get_llm_provider()
        >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate(question="What is LTV?", context=context)
    """
    
    @abstractmethod
    def estimate(
        self,
        question: str,
        context: Any,  # Context 객체
        **kwargs
    ) -> Optional[Any]:  # EstimationResult 또는 None (Cursor)
        """
        값 추정 (Stage 2: Generative Prior)
        
        Args:
            question: 추정 질문 (예: "What is average SaaS churn rate?")
            context: 컨텍스트 정보 (Context 객체)
            **kwargs: 추가 파라미터
                - temperature: LLM temperature
                - max_tokens: 최대 토큰 수
        
        Returns:
            - External 모드: EstimationResult (완성된 추정 결과)
            - Cursor 모드: None (포맷만 로깅, Cursor Composer가 처리)
        
        Example:
            >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
            >>> result = llm.estimate(
            ...     question="What is SaaS average churn rate?",
            ...     context=Context(industry="SaaS")
            ... )
            >>> # External: result = EstimationResult(value=5.0, unit="%", ...)
            >>> # Cursor: result = None
        """
        pass
    
    @abstractmethod
    def decompose(
        self,
        question: str,
        context: Any,  # Context 객체
        budget: Any,  # Budget 객체
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Fermi 분해 (Stage 3: Structural Explanation)
        
        Args:
            question: 분해할 질문 (예: "What is Spotify's annual revenue?")
            context: 컨텍스트 정보
            budget: 예산 제약 (Budget 객체)
            **kwargs: 추가 파라미터
        
        Returns:
            - External 모드: Dict (분해 결과)
                {
                    "variables": [{"name": "var1", "description": "..."}],
                    "formula": "var1 * var2 * ...",
                    "reasoning": "분해 이유"
                }
            - Cursor 모드: None (포맷만 로깅)
        
        Example:
            >>> llm = provider.get_llm(TaskType.FERMI_DECOMPOSITION)
            >>> result = llm.decompose(
            ...     question="What is Spotify's annual revenue?",
            ...     context=Context(industry="Music Streaming"),
            ...     budget=create_standard_budget()
            ... )
            >>> # External: {"variables": [...], "formula": "..."}
            >>> # Cursor: None
        """
        pass
    
    @abstractmethod
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Any,
        **kwargs
    ) -> str:
        """
        확신도 평가 (Stage 2)
        
        Args:
            question: 원래 질문
            value: 추정값
            context: 컨텍스트
        
        Returns:
            certainty: "high" | "medium" | "low"
        
        Example:
            >>> llm = provider.get_llm(TaskType.CERTAINTY_EVALUATION)
            >>> certainty = llm.evaluate_certainty(
            ...     question="What is SaaS churn rate?",
            ...     value=5.0,
            ...     context=Context(industry="SaaS")
            ... )
            >>> certainty  # "high"
        """
        pass
    
    @abstractmethod
    def validate_boundary(
        self,
        value: Any,
        context: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        경계 검증
        
        Args:
            value: 검증할 값
            context: 컨텍스트
        
        Returns:
            검증 결과:
                {
                    "is_valid": True/False,
                    "reason": "검증 이유",
                    "suggested_range": [min, max] 또는 None
                }
        
        Example:
            >>> llm = provider.get_llm(TaskType.BOUNDARY_VALIDATION)
            >>> result = llm.validate_boundary(
            ...     value=500.0,
            ...     context=Context(industry="SaaS")
            ... )
            >>> result["is_valid"]  # True
        """
        pass
    
    @abstractmethod
    def is_native(self) -> bool:
        """
        Native(Cursor) 모드 여부
        
        Returns:
            True: Cursor 모드 (수동)
            False: External 모드 (자동)
        
        Example:
            >>> llm.is_native()  # True (Cursor) or False (External)
        """
        pass


class LLMProvider(ABC):
    """
    LLM Provider 인터페이스
    
    Task별 적절한 LLM 객체를 제공하는 팩토리
    
    역할:
    - TaskType → BaseLLM 매핑
    - Native(Cursor) vs External 분기 결정
    - LLM 객체 생성 및 관리
    
    Example:
        >>> provider = get_llm_provider()  # settings.llm_mode 기반
        >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate(question, context)
    """
    
    @abstractmethod
    def get_llm(self, task: TaskType) -> BaseLLM:
        """
        Task에 맞는 LLM 객체 반환
        
        Args:
            task: TaskType (prior_estimation, fermi_decomposition 등)
        
        Returns:
            BaseLLM 구현체 (CursorLLM 또는 ExternalLLM)
        
        Example:
            >>> provider = get_llm_provider()
            >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
            >>> isinstance(llm, BaseLLM)  # True
        """
        pass
    
    @abstractmethod
    def is_native(self) -> bool:
        """
        Native(Cursor) Provider 여부
        
        Returns:
            True: CursorLLMProvider
            False: ExternalLLMProvider
        """
        pass
    
    @abstractmethod
    def get_mode_info(self) -> Dict[str, Any]:
        """
        현재 모드 정보 반환 (디버깅/모니터링용)
        
        Returns:
            Dict with keys:
                - mode: "cursor" or model name (e.g., "gpt-4o-mini")
                - provider: Provider 클래스명
                - uses_api: bool (External API 사용 여부)
                - cost: str (비용 설명)
                - automation: bool (자동화 가능 여부)
                - description: str (설명)
        
        Example:
            >>> provider.get_mode_info()
            {
                "mode": "cursor",
                "provider": "CursorLLMProvider",
                "uses_api": False,
                "cost": "$0 (Cursor 구독 포함)",
                "automation": False,
                "description": "RAG 검색만 수행 → Cursor LLM이 분석"
            }
        """
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Usage Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
사용 가이드
==========

1. LLMProvider 획득
-------------------

from umis_rag.core.llm_provider_factory import get_llm_provider

# settings.llm_mode 기반 자동 선택
provider = get_llm_provider()

# 또는 명시적 모드 지정
provider = get_llm_provider(mode="cursor")
provider = get_llm_provider(mode="gpt-4o-mini")


2. Estimator에서 사용
--------------------

class EstimatorRAG:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()
        # ❌ self.llm_mode 제거
    
    def estimate(self, question: str, context: Context) -> EstimationResult:
        # ✅ LLM 획득 (분기 없음!)
        llm = self.llm_provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        # ✅ 추정 실행 (분기 없음!)
        result = llm.estimate(question, context)
        
        # Cursor 모드: None 반환 → Cursor 포맷 응답
        if result is None:
            return self._prepare_cursor_response(...)
        
        # External 모드: 결과 반환
        return result


3. 테스트에서 사용 (Mock 주입)
-----------------------------

class MockLLMProvider(LLMProvider):
    def get_llm(self, task):
        return MockLLM()
    
    def is_native(self):
        return False
    
    def get_mode_info(self):
        return {"mode": "mock"}


def test_estimator():
    mock_provider = MockLLMProvider()
    estimator = EstimatorRAG(llm_provider=mock_provider)
    
    result = estimator.estimate("What is LTV?", Context())
    assert result is not None


4. Native/External 전환
-----------------------

# .env 파일만 변경
LLM_MODE=cursor  →  LLM_MODE=gpt-4o-mini

# 코드 수정: 0줄
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage Mapping (참고용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK_TO_STAGE = {
    TaskType.EVIDENCE_COLLECTION: 1,
    TaskType.PRIOR_ESTIMATION: 2,
    TaskType.CERTAINTY_EVALUATION: 2,
    TaskType.FERMI_DECOMPOSITION: 3,
    TaskType.FERMI_VARIABLE_ESTIMATION: 2,  # Stage 3에서 Stage 2 재사용
    TaskType.FUSION_CALCULATION: 4,
    TaskType.BOUNDARY_VALIDATION: 2,  # Stage 2에서 사용
    TaskType.GUARDRAIL_ANALYSIS: 1,  # Stage 1에서 사용
}
"""
Task → Stage 매핑

이 매핑은 ExternalLLM에서 ModelRouter를 사용할 때 필요합니다.
CursorLLM은 Stage를 사용하지 않습니다 (포맷만 반환).
"""
