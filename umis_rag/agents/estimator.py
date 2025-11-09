"""
Estimator Agent Redirect

⚠️ 이 파일은 리다이렉트 전용입니다.
실제 구현: estimator/ 폴더 (5,200줄, 14개 파일)

왜? Estimator만 복잡도가 높아 모듈화됨 (다른 Agent의 8-17배)
상세: estimator/README.md
"""

from .estimator.estimator import EstimatorRAG, get_estimator_rag
from .estimator.models import Context, EstimationResult, Tier1Config, Tier2Config
from .estimator.tier1 import Tier1FastPath
from .estimator.tier2 import Tier2JudgmentPath
from .estimator.learning_writer import LearningWriter, UserContribution

__all__ = [
    'EstimatorRAG', 'get_estimator_rag',
    'Tier1FastPath', 'Tier2JudgmentPath',
    'LearningWriter', 'UserContribution',
    'Context', 'EstimationResult', 'Tier1Config', 'Tier2Config',
]

