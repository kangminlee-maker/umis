"""
LLM Provider Module for UMIS RAG System

UMIS 전역 설정(llm_mode)에 따라 적절한 LLM 제공:
- cursor: Cursor Agent LLM 사용 (비용 $0, RAG만 수행)
- gpt-4o-mini, o1-mini 등: External LLM API 호출 (완전 자동화)

핵심 철학:
----------
Cursor 모드는 "RAG 검색만 수행 → Cursor LLM이 분석"
External LLM 모드는 "RAG 검색 + API 호출 → 완성된 결과"

v7.8.1 변경 (2025-11-25): umis_mode → llm_mode, native/external → 직접 모델명
v7.7.0 신규 추가 (2025-11-10)
"""

from typing import Optional, Any, Dict
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


class LLMProvider:
    """
    UMIS LLM Provider

    역할:
    -----
    llm_mode 설정에 따라 적절한 LLM 객체 생성

    사용 예시:
    ---------
    ```python
    # Agent에서 사용
    from umis_rag.core.llm_provider import LLMProvider

    class ExplorerRAG:
        def __init__(self):
            self.llm = LLMProvider.create_llm()
            self.mode = settings.llm_mode

        def generate_hypothesis(self, ...):
            if self.mode == "cursor":
                # RAG 검색만 수행
                return self._prepare_for_cursor(rag_results)
            else:
                # API 호출
                return self._call_llm_api(rag_results)
    ```

    모드별 동작:
    -----------
    Cursor Mode (llm_mode='cursor'):
        - LLM 객체 생성하지 않음 (None 반환)
        - Agent는 RAG 검색만 수행
        - 결과를 Cursor Composer/Chat에 전달
        - Cursor LLM이 직접 분석 수행
        - 비용: $0 (Cursor 구독에 포함)

    External LLM Mode (llm_mode='gpt-4o-mini', 'o1-mini' 등):
        - ChatOpenAI 객체 생성
        - Agent가 RAG + API 호출까지 완료
        - 완성된 결과 반환
        - 비용: 토큰당 과금 ($0.01-0.10/요청)
    """

    @staticmethod
    def create_llm() -> Optional[BaseChatModel]:
        """
        llm_mode에 따라 LLM 객체 생성

        Returns:
        --------
        - None: Cursor 모드 (LLM 사용 안 함, RAG만)
        - ChatOpenAI: External LLM 모드 (API 호출)

        Raises:
        -------
        ValueError: 알 수 없는 llm_mode 값
        """
        mode = settings.llm_mode.lower()

        if mode == "cursor":
            logger.info("🎯 Cursor 모드: LLM 객체 생성 안 함 (Cursor가 직접 처리)")
            return None

        else:
            # External LLM (gpt-4o-mini, o1-mini 등)
            logger.info(f"🌐 External LLM 모드: OpenAI API 사용 (모델: {settings.llm_model})")
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                openai_api_key=settings.openai_api_key,
                max_tokens=settings.llm_max_tokens
            )

    @staticmethod
    def is_cursor_mode() -> bool:
        """
        Cursor 모드 여부 확인

        Returns:
        --------
        True: Cursor 모드 (Cursor LLM 사용)
        False: External LLM 모드 (API 호출)
        """
        return settings.llm_mode.lower() == "cursor"

    @staticmethod
    def is_external_mode() -> bool:
        """
        External LLM 모드 여부 확인

        Returns:
        --------
        True: External LLM 모드 (API 호출)
        False: Cursor 모드 (Cursor LLM 사용)
        """
        return settings.llm_mode.lower() != "cursor"

    @staticmethod
    def get_mode_info() -> Dict[str, Any]:
        """
        현재 모드 정보 반환

        Returns:
        --------
        Dict with keys:
            - mode: 'cursor' or model name (e.g., 'gpt-4o-mini')
            - uses_api: bool
            - cost: str (비용 설명)
            - automation: bool (자동화 가능 여부)
        """
        mode = settings.llm_mode.lower()

        if mode == "cursor":
            return {
                "mode": "cursor",
                "uses_api": False,
                "cost": "$0 (Cursor 구독 포함)",
                "automation": False,
                "description": "RAG 검색만 수행 → Cursor LLM이 분석"
            }
        else:
            return {
                "mode": mode,
                "uses_api": True,
                "cost": f"토큰당 과금 (모델: {settings.llm_model})",
                "automation": True,
                "description": "RAG 검색 + API 호출 → 완성된 결과"
            }


class CursorModeMixin:
    """
    Cursor 모드 헬퍼 Mixin

    Agent가 Cursor/External LLM 모드를 쉽게 처리하도록 돕는 유틸리티

    사용 예시:
    ---------
    ```python
    class ExplorerRAG(CursorModeMixin):
        def generate_hypothesis(self, rag_results):
            if self.is_cursor():
                return self.prepare_cursor_output(
                    rag_results,
                    instruction="위 패턴을 바탕으로 기회 가설 3개를 생성해주세요."
                )
            else:
                # External LLM: API 호출
                return self._call_api(rag_results)
    ```
    """

    def is_cursor(self) -> bool:
        """Cursor 모드 여부"""
        return LLMProvider.is_cursor_mode()

    def is_external(self) -> bool:
        """External LLM 모드 여부"""
        return LLMProvider.is_external_mode()

    def prepare_cursor_output(
        self,
        rag_results: Any,
        instruction: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cursor 모드용 출력 준비

        RAG 검색 결과를 Cursor LLM이 사용할 수 있는 형태로 포맷팅

        Parameters:
        -----------
        rag_results: RAG 검색 결과
        instruction: Cursor LLM에게 전달할 지시사항
        metadata: 추가 메타데이터

        Returns:
        --------
        Dict with keys:
            - mode: 'cursor'
            - rag_results: 검색 결과
            - instruction: LLM 지시사항
            - metadata: 메타데이터
        """
        return {
            "mode": "cursor",
            "rag_results": rag_results,
            "instruction": instruction,
            "metadata": metadata or {},
            "next_step": "Cursor Composer/Chat에서 위 결과를 활용하여 분석하세요."
        }


# ========================================
# 사용 가이드
# ========================================

"""
Agent 수정 가이드:
-----------------

1. LLM 초기화 수정
-------------------
# Before (항상 ChatOpenAI)
self.llm = ChatOpenAI(
    model=settings.llm_model,
    temperature=settings.llm_temperature,
    openai_api_key=settings.openai_api_key
)

# After (모드에 따라)
from umis_rag.core.llm_provider import LLMProvider

self.llm = LLMProvider.create_llm()
self.mode = settings.umis_mode


2. LLM 호출 메서드 수정
-----------------------
# Before (무조건 API 호출)
def generate_hypothesis(self, patterns, cases):
    prompt = ChatPromptTemplate.from_messages([...])
    chain = prompt | self.llm | StrOutputParser()
    return chain.invoke({...})

# After (모드 분기)
def generate_hypothesis(self, patterns, cases):
    rag_results = self._prepare_rag_context(patterns, cases)

    if self.mode == "native":
        # Native: RAG 결과만 반환
        return {
            'mode': 'native',
            'rag_results': rag_results,
            'instruction': '위 패턴과 사례를 바탕으로 기회 가설을 생성해주세요.'
        }
    else:
        # External: API 호출
        prompt = ChatPromptTemplate.from_messages([...])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({'context': rag_results})


3. 스크립트 사용 예시
--------------------
# Native 모드 (.env: UMIS_MODE=native)
python scripts/test_explorer.py

# 출력:
# {
#   'mode': 'native',
#   'rag_results': [...패턴 검색 결과...],
#   'instruction': '위 패턴을 바탕으로 가설을 생성해주세요.'
# }
#
# → Cursor Composer에서:
#   "@Explorer 결과를 바탕으로 음악 스트리밍 시장 기회 3개 제시"

# External 모드 (.env: UMIS_MODE=external)
python scripts/test_explorer.py

# 출력:
# 가설 1: 구독 모델 기반 음악 플랫폼
# ...완성된 가설...


4. 비용 비교
-----------
Native Mode:
    - RAG 임베딩: $0.0001
    - LLM 호출: $0 (Cursor)
    - 합계: $0

External Mode:
    - RAG 임베딩: $0.0001
    - LLM 호출: $0.10
    - 합계: $0.10

100회 분석:
    - Native: $0
    - External: $10
"""

