"""
UMIS Agents (v7.7.0)

6-Agent 시스템:
- Observer, Explorer, Quantifier: 단일 파일 (295-659줄)
- Validator: 단일 파일 + search_definite_data() (v7.6.0+)
- Estimator: 모듈화 폴더 (5,200줄, 14개 파일)
- Guardian: 품질 관리

v7.7.0 주요 변경:
-----------------
- Native 모드 진짜 구현 (비용 $0)
- 용어 체계 명확화 (Phase + Step)
- 3-Tier 완전 Deprecated
- Explorer: Native/External 분기
- LLMProvider 클래스 추가

⚠️ Estimator만 estimator/ 폴더로 분리
상세: estimator/README.md
"""

from .explorer import ExplorerRAG, ExplorerAgenticRAG
from .observer import ObserverRAG, get_observer_rag
from .quantifier import QuantifierRAG, get_quantifier_rag
from .validator import ValidatorRAG, get_validator_rag
from .estimator import EstimatorRAG, get_estimator_rag

__all__ = [
    # Explorer
    'ExplorerRAG',
    'ExplorerAgenticRAG',
    
    # Observer (v7.1.0)
    'ObserverRAG',
    'get_observer_rag',
    
    # Quantifier (v7.1.0)
    'QuantifierRAG',
    'get_quantifier_rag',
    
    # Validator (v7.1.0)
    'ValidatorRAG',
    'get_validator_rag',
    
    # Estimator (v7.7.0) ⭐ Native 모드 + 5-Phase!
    'EstimatorRAG',
    'get_estimator_rag',
]
