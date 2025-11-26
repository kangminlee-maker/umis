"""
Common Data Structures for v7.11.0 Fusion Architecture

이 패키지는 모든 Estimation Engine이 공유하는 공통 인터페이스를 정의합니다.
"""

from .budget import Budget, create_standard_budget, create_fast_budget, create_thorough_budget
from .estimation_result import EstimationResult, Evidence

__all__ = [
    'Budget',
    'create_standard_budget',
    'create_fast_budget',
    'create_thorough_budget',
    'EstimationResult',
    'Evidence'
]
