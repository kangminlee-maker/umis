"""
Compatibility Layer for Phase 3-4 Legacy Code (v7.11.0)

이 모듈은 Phase 3-4 레거시 코드의 하위 호환성을 제공합니다.

v7.11.0 변경 사항:
- Phase 3 Guestimation → Stage 2 Generative Prior (PriorEstimator)
- Phase 4 Fermi Decomposition → Stage 3 Structural Explanation (FermiEstimator)

레거시 코드가 계속 동작하도록 Alias와 DeprecationWarning을 제공합니다.

사용 (Deprecated):
    >>> from umis_rag.agents.estimator import Phase3Guestimation  # Deprecated!
    >>> phase3 = Phase3Guestimation()
    DeprecationWarning: Phase3Guestimation은 v7.11.0에서 Deprecated되었습니다.
    대신 PriorEstimator를 사용하세요.

신규 사용 (권장):
    >>> from umis_rag.agents.estimator import PriorEstimator
    >>> prior = PriorEstimator()

마이그레이션 완료 후:
    이 파일은 v7.11.1 패치에서 제거됩니다 (프로덕션 배포 후 2주).
"""

import warnings
from typing import Optional

# v7.11.0 신규 구현 Import
from .prior_estimator import PriorEstimator
from .fermi_estimator import FermiEstimator


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deprecated Aliases (하위 호환성)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class Phase3Guestimation(PriorEstimator):
    """
    Phase 3 Guestimation (Deprecated)
    
    ⚠️ Deprecated in v7.11.0
    대신 `PriorEstimator`를 사용하세요.
    
    이 클래스는 하위 호환성을 위해서만 제공됩니다.
    v7.11.1에서 제거될 예정입니다.
    """
    
    def __init__(self, config=None, llm_mode: Optional[str] = None, learning_writer=None):
        warnings.warn(
            "Phase3Guestimation은 v7.11.0에서 Deprecated되었습니다. "
            "대신 PriorEstimator를 사용하세요.\n"
            "마이그레이션 가이드: docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md",
            DeprecationWarning,
            stacklevel=2
        )
        
        # PriorEstimator 초기화 (llm_mode만 사용)
        super().__init__(llm_mode=llm_mode)


class Phase4FermiDecomposition(FermiEstimator):
    """
    Phase 4 Fermi Decomposition (Deprecated)
    
    ⚠️ Deprecated in v7.11.0
    대신 `FermiEstimator`를 사용하세요.
    
    주요 변경 사항:
    - 재귀 완전 제거 (Recursion FORBIDDEN)
    - max_depth=2 강제
    - Budget 기반 탐색
    - PriorEstimator 주입 (의존성 역전)
    
    이 클래스는 하위 호환성을 위해서만 제공됩니다.
    v7.11.1에서 제거될 예정입니다.
    """
    
    def __init__(self, config=None, llm_mode: Optional[str] = None):
        warnings.warn(
            "Phase4FermiDecomposition은 v7.11.0에서 Deprecated되었습니다. "
            "대신 FermiEstimator를 사용하세요.\n"
            "주요 변경: 재귀 제거, Budget 기반 탐색, PriorEstimator 주입\n"
            "마이그레이션 가이드: docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md",
            DeprecationWarning,
            stacklevel=2
        )
        
        # FermiEstimator 초기화
        # PriorEstimator 자동 생성 (레거시 호환용)
        prior_estimator = PriorEstimator(llm_mode=llm_mode)
        super().__init__(llm_mode=llm_mode, prior_estimator=prior_estimator)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Export
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

__all__ = [
    'Phase3Guestimation',          # Deprecated, use PriorEstimator
    'Phase4FermiDecomposition',    # Deprecated, use FermiEstimator
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deprecation Notice
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _show_deprecation_notice():
    """모듈 Import 시 Deprecation Notice 출력"""
    warnings.warn(
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️  Compatibility Layer (compat.py) 사용 중\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "Phase 3-4 레거시 Import가 감지되었습니다.\n"
        "v7.11.0에서 Deprecated되었으며, v7.11.1에서 제거될 예정입니다.\n"
        "\n"
        "마이그레이션 가이드:\n"
        "  - Phase3Guestimation → PriorEstimator\n"
        "  - Phase4FermiDecomposition → FermiEstimator\n"
        "  - docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md 참조\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        DeprecationWarning,
        stacklevel=2
    )


# 모듈 Import 시 Notice 출력 (1회만)
_show_deprecation_notice()

