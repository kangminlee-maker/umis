"""
Estimator Agent Redirect

⚠️ 이 파일은 리다이렉트 전용입니다.
실제 구현: estimator/ 폴더 (5,200줄, 14개 파일)

왜? Estimator만 복잡도가 높아 모듈화됨 (다른 Agent의 8-17배)
상세: estimator/README.md

v7.11.1 변경:
- compat.py 제거 (Phase3Guestimation, Phase4FermiDecomposition)
- 완전한 Stage 1-4 기반 구조
"""

from .estimator.estimator import EstimatorRAG, get_estimator_rag
from .estimator.models import (
    Context, EstimationResult,
    Phase1Config, Phase3Config, Phase4Config
)
from .estimator.phase1_direct_rag import Phase1DirectRAG
from .estimator.learning_writer import LearningWriter, UserContribution

# v7.11.0 Stage 기반 구현
from .estimator.prior_estimator import PriorEstimator
from .estimator.fermi_estimator import FermiEstimator
from .estimator.fusion_layer import FusionLayer
from .estimator.evidence_collector import EvidenceCollector

__all__ = [
    'EstimatorRAG', 'get_estimator_rag',
    'Phase1DirectRAG',
    'Phase1Config', 'Phase3Config', 'Phase4Config',
    'LearningWriter', 'UserContribution',
    'Context', 'EstimationResult',
    
    # v7.11.0 Stage 기반 (권장)
    'PriorEstimator',
    'FermiEstimator',
    'FusionLayer',
    'EvidenceCollector',
]
