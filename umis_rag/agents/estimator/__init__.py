"""
Estimator (Fermi) Agent - 값 추정 및 판단 전문가

역할:
- 맥락 기반 값 추정
- 증거 + 생성 + 구조 융합
- 재귀 없는 Fermi 분해 (v7.11.0)

사용:
    from umis_rag.agents.estimator import EstimatorRAG
    
    estimator = EstimatorRAG()
    result = estimator.estimate("B2B SaaS Churn Rate는?", domain="B2B_SaaS")

v7.11.0:
    - 재귀 완전 제거
    - 예산 기반 탐색
    - Fusion Architecture
"""

from .estimator import EstimatorRAG, get_estimator
from .models import Context, EstimationResult

# v7.11.0 새 인터페이스
from .common.budget import Budget, create_standard_budget, create_fast_budget, create_thorough_budget
from .common.estimation_result import EstimationResult as EstimationResultV11, Evidence

# 호환성 alias (v7.11.0)
get_estimator_rag = get_estimator

__all__ = [
    # 메인 Agent
    'EstimatorRAG',
    'get_estimator',
    'get_estimator_rag',  # 호환성
    
    # 레거시 Models (호환성)
    'Context',
    'EstimationResult',
    
    # v7.11.0 새 인터페이스
    'Budget',
    'create_standard_budget',
    'create_fast_budget',
    'create_thorough_budget',
    'EstimationResultV11',
    'Evidence',
]
