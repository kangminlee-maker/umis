"""
Guestimation Sources (v7.8.0 재설계)

11개 → 10개 Source (LLM + Web 통합)
"""

from .physical import (
    UnifiedPhysicalConstraintSource,  # v7.8.0: 신규 통합
    SpacetimeConstraintSource,  # deprecated
    ConservationLawSource,  # deprecated
    MathematicalDefinitionSource  # deprecated
)

from .soft import (
    LegalNormSource,
    StatisticalPatternSource,
    BehavioralInsightSource
)

from .value import (
    DefiniteDataSource,
    AIAugmentedEstimationSource,  # v7.8.0: 신규
    LLMEstimationSource,  # deprecated
    WebSearchSource,  # deprecated
    RAGBenchmarkSource,
    StatisticalValueSource
)

__all__ = [
    # Physical
    'UnifiedPhysicalConstraintSource',  # v7.8.0: 신규 통합
    'SpacetimeConstraintSource',  # deprecated
    'ConservationLawSource',  # deprecated
    'MathematicalDefinitionSource',  # deprecated
    
    # Soft
    'LegalNormSource',
    'StatisticalPatternSource',
    'BehavioralInsightSource',
    
    # Value
    'DefiniteDataSource',
    'AIAugmentedEstimationSource',  # v7.8.0: 신규
    'LLMEstimationSource',  # deprecated
    'WebSearchSource',  # deprecated
    'RAGBenchmarkSource',
    'StatisticalValueSource',
]

