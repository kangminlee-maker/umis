"""
UMIS Multi-Agent RAG System

Universal Market Intelligence System의 지식 베이스를 위한
Multi-Agent Retrieval-Augmented Generation 시스템입니다.
"""

__version__ = "0.1.0"
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
# 기존 설정 import
# ============================================================================
from umis_rag.core.config import settings

__all__ = ["settings", "__version__", "_env_loaded"]

