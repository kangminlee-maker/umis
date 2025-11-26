"""
Cursor LLM Implementation for UMIS RAG System

Native (Cursor) 모드 구현

특징:
- 실제 LLM 호출 불가 (Cursor Composer가 처리)
- 포맷된 데이터만 로깅
- 비용 $0
- Cursor Composer에서 수동 처리

작성: 2025-11-26
"""

from typing import Optional, Dict, Any
from umis_rag.core.llm_interface import BaseLLM, LLMProvider, TaskType
import logging

logger = logging.getLogger(__name__)


class CursorLLM(BaseLLM):
    """
    Cursor Native LLM 구현
    
    특징:
    - 실제 LLM 호출 불가 (Cursor Composer가 처리)
    - 포맷된 데이터만 로깅
    - 비용 $0
    - 수동 모드 (Cursor Composer에서 읽고 처리)
    
    설계 결정:
    - 모든 메서드는 None 반환 (또는 기본값)
    - 대신 포맷된 데이터를 로깅
    - Estimator가 None 체크 후 Cursor 포맷 응답 생성
    
    Example:
        >>> llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        >>> result = llm.estimate("What is LTV?", context)
        >>> result  # None (Cursor가 처리)
    """
    
    def __init__(self, task: TaskType):
        """
        Args:
            task: TaskType (로깅용)
        """
        self.task = task
        logger.info(f"[CursorLLM] 초기화: {task.value}")
    
    def estimate(
        self,
        question: str,
        context: Any,
        **kwargs
    ) -> Optional[Any]:
        """
        Cursor 모드: 추정 데이터 준비 (실제 추정 불가)
        
        Args:
            question: 추정 질문
            context: 컨텍스트
        
        Returns:
            None (Cursor Composer가 처리)
        
        Logging:
            포맷된 데이터를 로깅 → Cursor Composer가 읽음
        """
        logger.info(f"[Cursor Prior] 추정 데이터 준비")
        logger.info(f"  Task: {self.task.value}")
        logger.info(f"  Question: {question}")
        logger.info(f"  Context: {self._format_context(context)}")
        logger.info("  → Cursor Composer에서 위 데이터로 추정 수행")
        
        # ⚠️ None 반환 → Estimator가 Cursor 포맷 응답 생성
        return None
    
    def decompose(
        self,
        question: str,
        context: Any,
        budget: Any,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Cursor 모드: Fermi 분해 데이터 준비
        
        Args:
            question: 분해할 질문
            context: 컨텍스트
            budget: 예산
        
        Returns:
            None (Cursor Composer가 처리)
        """
        logger.info(f"[Cursor Fermi] 분해 데이터 준비")
        logger.info(f"  Task: {self.task.value}")
        logger.info(f"  Question: {question}")
        logger.info(f"  Context: {self._format_context(context)}")
        logger.info(f"  Budget: {self._format_budget(budget)}")
        logger.info("  → Cursor Composer에서 위 데이터로 분해 수행")
        
        return None
    
    def evaluate_certainty(
        self,
        question: str,
        value: Any,
        context: Any,
        **kwargs
    ) -> str:
        """
        Cursor 모드: 확신도 평가 불가
        
        Args:
            question: 질문
            value: 값
            context: 컨텍스트
        
        Returns:
            "medium" (기본값)
        
        Note:
            Cursor는 확신도 평가 불가 → 보수적 기본값
        """
        logger.info(f"[Cursor Certainty] 기본값 반환 (medium)")
        logger.info(f"  Question: {question}")
        logger.info(f"  Value: {value}")
        return "medium"
    
    def validate_boundary(
        self,
        value: Any,
        context: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cursor 모드: 경계 검증 스킵
        
        Args:
            value: 값
            context: 컨텍스트
        
        Returns:
            기본 통과 결과
        
        Note:
            Cursor는 검증 불가 → 기본 통과
        """
        logger.info(f"[Cursor Boundary] 검증 스킵")
        logger.info(f"  Value: {value}")
        
        return {
            "is_valid": True,
            "reason": "Cursor 모드는 검증 스킵",
            "suggested_range": None
        }
    
    def is_native(self) -> bool:
        """Native(Cursor) 모드"""
        return True
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _format_context(self, context: Any) -> str:
        """컨텍스트 포맷팅 (로깅용)"""
        if context is None:
            return "{}"
        
        if hasattr(context, "to_dict"):
            return str(context.to_dict())
        
        if isinstance(context, dict):
            return str(context)
        
        return str(context)
    
    def _format_budget(self, budget: Any) -> str:
        """예산 포맷팅 (로깅용)"""
        if budget is None:
            return "{}"
        
        if hasattr(budget, "__dict__"):
            return str(budget.__dict__)
        
        if isinstance(budget, dict):
            return str(budget)
        
        return str(budget)


class CursorLLMProvider(LLMProvider):
    """
    Cursor LLM Provider
    
    Task에 관계없이 항상 CursorLLM 반환
    
    특징:
    - Native 모드
    - 비용 $0
    - 수동 처리 (Cursor Composer)
    
    Example:
        >>> provider = CursorLLMProvider()
        >>> llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        >>> isinstance(llm, CursorLLM)  # True
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
        
        Note:
            모든 Task에 대해 같은 CursorLLM 반환
            (Task별 차이는 로깅에만 반영)
        """
        logger.debug(f"[CursorLLMProvider] {task.value} → CursorLLM")
        return CursorLLM(task)
    
    def is_native(self) -> bool:
        """Native(Cursor) Provider"""
        return True
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        Cursor 모드 정보
        
        Returns:
            모드 정보 dict
        """
        return {
            "mode": "cursor",
            "provider": "CursorLLMProvider",
            "uses_api": False,
            "cost": "$0 (Cursor 구독 포함)",
            "automation": False,
            "description": "RAG 검색 + 포맷 → Cursor Composer가 분석"
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Usage Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
사용 가이드
==========

1. 직접 사용
-----------

from umis_rag.core.llm_cursor import CursorLLMProvider

provider = CursorLLMProvider()
llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)

result = llm.estimate("What is LTV?", context)
# result = None (Cursor 모드)


2. Estimator에서 사용
--------------------

class EstimatorRAG:
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider or CursorLLMProvider()
    
    def estimate(self, question, context):
        llm = self.llm_provider.get_llm(TaskType.PRIOR_ESTIMATION)
        result = llm.estimate(question, context)
        
        if result is None:
            # Cursor 모드: 포맷된 응답 반환
            return {
                "mode": "cursor",
                "question": question,
                "context": context,
                "instruction": "위 데이터로 추정 수행"
            }
        
        return result


3. Cursor 모드 특징
------------------

- LLM 호출: 불가 (None 반환)
- 비용: $0
- 속도: 즉시 (처리 없음)
- 정확도: Cursor Composer 의존

- 장점:
  - 비용 없음
  - Cursor 구독에 포함
  - 대화형 추정 가능

- 단점:
  - 자동화 불가
  - 수동 처리 필요
  - Cursor IDE 필수
"""
