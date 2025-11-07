"""
UMIS Guestimation System v3.0

Context-Aware Judgment + Learning System
"""

__version__ = "3.0.0"
__author__ = "UMIS Development Team"

from .models import (
    Context,
    Boundary,
    SoftGuide,
    ValueEstimate,
    SourceOutput,
    EstimationResult
)

# core는 나중에 구현
# from .core import estimate

__all__ = [
    'Context',
    'Boundary',
    'SoftGuide',
    'ValueEstimate',
    'SourceOutput',
    'EstimationResult',
    # 'estimate'
]

