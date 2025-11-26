"""
UMIS Multi-Agent RAG System

Universal Market Intelligence System의 지식 베이스를 위한
Multi-Agent Retrieval-Augmented Generation 시스템입니다.
"""

__version__ = "7.11.0"
__author__ = "UMIS Team"

# ============================================================================
# 환경변수 자동 로드 (UMIS 패키지 import 시 자동 실행)
# ============================================================================
import os
from pathlib import Path

def _load_environment():
    """
    .env 파일 자동 로드 (UMIS 패키지 최초 import 시 1회 실행)
    
    검색 순서:
    1. 현재 작업 디렉토리 (os.getcwd())
    2. UMIS 프로젝트 루트 (umis_rag/.. 상위)
    3. 사용자 홈 디렉토리 (~/.env)
    
    Returns:
    --------
    bool: 환경변수 로드 성공 여부
    """
    try:
        from dotenv import load_dotenv
        
        # 검색 경로 리스트
        search_paths = [
            Path.cwd() / '.env',  # 현재 디렉토리
            Path(__file__).parent.parent / '.env',  # UMIS 루트
            Path.home() / '.env',  # 홈 디렉토리
        ]
        
        loaded = False
        for env_path in search_paths:
            if env_path.exists():
                load_dotenv(env_path, override=False)  # 기존 환경변수 우선
                loaded = True
                break
        
        # OPENAI_API_KEY 체크
        if os.getenv('OPENAI_API_KEY'):
            return True
        elif loaded:
            # .env는 있지만 OPENAI_API_KEY 없음
            import warnings
            warnings.warn(
                "⚠️  .env 파일이 로드되었지만 OPENAI_API_KEY가 설정되지 않았습니다.\n"
                "   .env 파일에 다음을 추가하세요:\n"
                "   OPENAI_API_KEY=your-api-key-here\n"
                "   API 키 받기: https://platform.openai.com/api-keys",
                UserWarning
            )
        
        return loaded
        
    except ImportError:
        # python-dotenv 미설치
        import warnings
        warnings.warn(
            "⚠️  python-dotenv가 설치되지 않았습니다.\n"
            "   설치: pip install python-dotenv",
            UserWarning
        )
        return False

# 패키지 import 시 자동 실행
_env_loaded = _load_environment()

# ============================================================================
# UMIS 전역 설정 로드 (v7.2.1+)
# ============================================================================

def _get_global_mode():
    """
    UMIS LLM 제공자 설정 반환
    
    .env 파일의 LLM_MODE 환경변수:
      - 'cursor'   : Cursor Agent LLM 사용 (기본)
      - 'external' : External LLM API 사용 (OpenAI/Anthropic)
    
    Stage별 모델 설정: config/model_configs.yaml
    영향 범위: UMIS 전체 시스템 (모든 Agent, 모든 LLM 호출)
    """
    mode = os.getenv('LLM_MODE', 'cursor').lower()
    # cursor 또는 external만 허용
    if mode not in ['cursor', 'external']:
        import warnings
        warnings.warn(
            f"⚠️  LLM_MODE={mode}는 유효하지 않습니다. 'cursor' 또는 'external'만 허용됩니다.\n"
            f"   기본값 'cursor'를 사용합니다.",
            UserWarning
        )
        return 'cursor'
    return mode

# UMIS 전역 설정 (시스템 전체 적용)
LLM_MODE = _get_global_mode()  # LLM 제공자 (cursor/external)

# 참고: 
# - LLM 모드: .env의 LLM_MODE (cursor/external)
# - Stage별 모델: config/model_configs.yaml (TaskType별 설정)
# - UMIS 실행 모드: config/runtime.yaml (hybrid/rag_full 등)

# ============================================================================
# 기존 설정 import
# ============================================================================
from umis_rag.core.config import settings

__all__ = [
    "settings", 
    "__version__", 
    "_env_loaded",
    "LLM_MODE",           # LLM 제공자 설정 (전역, .env)
]

