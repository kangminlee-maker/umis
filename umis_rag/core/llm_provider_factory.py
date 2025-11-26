"""
LLM Provider Factory for UMIS RAG System

LLMProvider 팩토리 함수

역할:
- settings.llm_mode 기반 Provider 선택
- Cursor vs External 자동 분기
- 싱글톤 패턴 (옵션)

작성: 2025-11-26
"""

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
            - "cursor": CursorLLMProvider (Native)
            - 그 외: ExternalLLMProvider (External)
    
    Returns:
        LLMProvider 구현체
    
    Example:
        >>> # .env: LLM_MODE=cursor
        >>> provider = get_llm_provider()
        >>> isinstance(provider, CursorLLMProvider)  # True
        
        >>> # .env: LLM_MODE=gpt-4o-mini
        >>> provider = get_llm_provider()
        >>> isinstance(provider, ExternalLLMProvider)  # True
        
        >>> # 명시적 모드 지정
        >>> provider = get_llm_provider(mode="cursor")
        >>> provider.is_native()  # True
    """
    mode = mode or settings.llm_mode
    mode = mode.lower().strip()
    
    # 빈 문자열은 settings 사용
    if not mode:
        mode = settings.llm_mode.lower().strip()
    
    if mode == "cursor":
        logger.info("[LLMProviderFactory] CursorLLMProvider 선택")
        return CursorLLMProvider()
    
    else:
        logger.info(f"[LLMProviderFactory] ExternalLLMProvider 선택 (모델: {mode})")
        return ExternalLLMProvider()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 싱글톤 패턴 (옵션)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_provider_instance: Optional[LLMProvider] = None


def get_default_llm_provider() -> LLMProvider:
    """
    기본 LLMProvider 반환 (싱글톤)
    
    Returns:
        LLMProvider 인스턴스
    
    Note:
        같은 Provider 인스턴스를 재사용합니다.
        테스트에서는 reset_llm_provider()로 초기화하세요.
    
    Example:
        >>> provider1 = get_default_llm_provider()
        >>> provider2 = get_default_llm_provider()
        >>> provider1 is provider2  # True (같은 인스턴스)
    """
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = get_llm_provider()
    return _provider_instance


def reset_llm_provider():
    """
    Provider 싱글톤 초기화 (테스트용)
    
    Example:
        >>> # 테스트 시작 전
        >>> reset_llm_provider()
        >>> provider = get_default_llm_provider()  # 새 인스턴스
    """
    global _provider_instance
    _provider_instance = None
    logger.debug("[LLMProviderFactory] 싱글톤 초기화")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Usage Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
사용 가이드
==========

1. 기본 사용 (settings 기반)
---------------------------

from umis_rag.core.llm_provider_factory import get_llm_provider

# .env: LLM_MODE=cursor
provider = get_llm_provider()
# → CursorLLMProvider

# .env: LLM_MODE=gpt-4o-mini
provider = get_llm_provider()
# → ExternalLLMProvider


2. 명시적 모드 지정
------------------

# Cursor 모드 강제
provider = get_llm_provider(mode="cursor")

# External 모드 강제
provider = get_llm_provider(mode="gpt-4o-mini")


3. Estimator에서 사용
--------------------

from umis_rag.core.llm_provider_factory import get_default_llm_provider

class EstimatorRAG:
    def __init__(self, llm_provider=None):
        # None이면 기본 Provider (싱글톤)
        self.llm_provider = llm_provider or get_default_llm_provider()


4. 테스트에서 사용
-----------------

from umis_rag.core.llm_provider_factory import reset_llm_provider, get_default_llm_provider

def test_estimator():
    # 테스트 전 싱글톤 초기화
    reset_llm_provider()
    
    # Mock Provider 주입
    mock_provider = MockLLMProvider()
    estimator = EstimatorRAG(llm_provider=mock_provider)


5. 모드 전환
-----------

# .env 파일만 변경
LLM_MODE=cursor  →  LLM_MODE=gpt-4o-mini

# 코드 수정: 0줄
# Provider 자동 전환

# 싱글톤 사용 시 재시작 필요 (또는 reset_llm_provider() 호출)
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Debugging 유틸리티
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_current_mode_info() -> dict:
    """
    현재 LLM 모드 정보 반환 (디버깅용)
    
    Returns:
        Dict with keys:
            - mode: 현재 모드 (cursor or model name)
            - provider: Provider 클래스명
            - uses_api: API 사용 여부
            - cost: 비용 설명
            - automation: 자동화 가능 여부
    
    Example:
        >>> info = get_current_mode_info()
        >>> print(info["mode"])  # "cursor"
        >>> print(info["cost"])  # "$0 (Cursor 구독 포함)"
    """
    provider = get_llm_provider()
    return provider.get_mode_info()


if __name__ == "__main__":
    # 디버깅: 현재 모드 출력
    import json
    
    print("=" * 60)
    print("LLM Provider Factory - Current Mode")
    print("=" * 60)
    
    info = get_current_mode_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print(f"Mode: {info['mode']}")
    print(f"Provider: {info['provider']}")
    print(f"Uses API: {info['uses_api']}")
    print(f"Cost: {info['cost']}")
    print(f"Automation: {info['automation']}")
    print("=" * 60)
