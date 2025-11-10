"""
Estimator (Fermi) Agent - 값 추정 및 판단 전문가

역할:
- 맥락 기반 값 추정
- 11개 Source 통합 판단
- 학습하는 시스템 (6-16배 빠름)

사용:
    from umis_rag.agents.estimator import EstimatorRAG
    
    estimator = EstimatorRAG()
    result = estimator.estimate("B2B SaaS Churn Rate는?", domain="B2B_SaaS")
"""

from .estimator import EstimatorRAG, get_estimator_rag
from .phase1_direct_rag import Phase1DirectRAG
from .phase3_guestimation import Phase3Guestimation
from .learning_writer import LearningWriter, UserContribution
from .models import (
    Context, EstimationResult,
    Phase1Config, Phase3Config, Phase4Config
)

__all__ = [
    # 주요 인터페이스
    'EstimatorRAG',
    'get_estimator_rag',
    
    # Phase 기반 클래스
    'Phase1DirectRAG',
    'Phase3Guestimation',
    
    # Config
    'Phase1Config',
    'Phase3Config',
    'Phase4Config',
    
    # 기타
    'LearningWriter',
    'UserContribution',
    
    # 데이터 모델
    'Context',
    'EstimationResult',
]
