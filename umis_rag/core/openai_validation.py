"""
OpenAI API Key validation helpers.

목적:
- settings.openai_api_key가 Optional(None)로 바뀐 이후,
  OpenAIEmbeddings/ChatOpenAI 등 OpenAI 기반 컴포넌트 초기화 시
  None/빈 문자열이 그대로 전달되어 런타임 크래시가 나는 문제를 방지합니다.
- "어디서 무엇을 설정해야 하는지"가 명확한 검증 에러를 조기에 제공합니다.
"""

from __future__ import annotations

from typing import Optional


class OpenAIAPIKeyMissingError(ValueError):
    """OPENAI_API_KEY가 필요한 경로에서 키가 누락/빈 값일 때 발생."""


def require_openai_api_key(
    openai_api_key: Optional[str],
    *,
    component: str,
) -> str:
    """
    OpenAI 기반 컴포넌트 초기화에 필요한 API 키를 검증 후 반환합니다.

    - None, "", "   " 같은 값은 모두 '미설정'으로 취급합니다.
    - 검증 실패 시, 사용자가 즉시 해결할 수 있는 메시지를 포함한 예외를 발생시킵니다.
    """

    normalized = (openai_api_key or "").strip()
    if normalized:
        return normalized

    raise OpenAIAPIKeyMissingError(
        f"{component} 초기화에 필요한 OPENAI_API_KEY가 설정되어 있지 않습니다.\n"
        f"- 해결: 환경변수 `OPENAI_API_KEY`를 설정하거나, `.env`의 `OPENAI_API_KEY=...`를 채워주세요.\n"
        f"- 참고: Docker에서는 `docker-compose.yml`의 environment 또는 `.env` 파일을 통해 주입됩니다."
    )

