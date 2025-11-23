"""
LLM Model Router for UMIS RAG System

Phase별 최적 모델 자동 선택 (v7.7.0+)
기반: UMIS_LLM_OPTIMIZATION_FINAL.md

효과:
- 98% 비용 절감 ($15 → $0.30/1,000회)
- 40-70% 속도 개선
- 품질 유지 (98-100% 정확도)

v7.8.0 추가:
- select_model_with_config(): 모델 + API 설정 함께 반환
- config/model_configs.yaml 기반
"""

from typing import Literal, Optional, Tuple
from umis_rag.core.config import settings
from umis_rag.core.model_configs import model_config_manager, ModelConfig
import logging

logger = logging.getLogger(__name__)

PhaseType = Literal[0, 1, 2, 3, 4]


class ModelRouter:
    """
    Phase별 최적 LLM 모델 자동 선택

    최적화 전략 (실측 기반):

    Phase 0-2 (45%): gpt-4.1-nano
      - 비용: $0.000033/작업
      - 속도: 1.02초
      - 정확도: 100%
      - 작업: Literal, Inferred, Formula

    Phase 3 (48%): gpt-4o-mini
      - 비용: $0.000121/작업
      - 속도: 4.61초
      - 정확도: 100% (개선된 프롬프트)
      - 작업: Guestimation (템플릿 있음/없음)

    Phase 4 (7%): o1-mini
      - 비용: $0.0033/작업 (추정)
      - 속도: 5-15초
      - 정확도: 90-95% (추정)
      - 작업: Fermi Decomposition, Discovery Sprint
    """

    def __init__(self):
        self.routing_enabled = settings.use_phase_based_routing
        logger.info(
            f"ModelRouter 초기화 (Phase 기반 라우팅: {self.routing_enabled})"
        )

    def select_model(self, phase: PhaseType) -> str:
        """
        Phase에 맞는 최적 모델 선택

        Args:
            phase: Estimator Phase (0, 1, 2, 3, 4)

        Returns:
            모델명 (예: "gpt-4.1-nano", "gpt-4o-mini", "o1-mini")

        Example:
            >>> router = ModelRouter()
            >>> router.select_model(0)
            'gpt-4.1-nano'
            >>> router.select_model(3)
            'gpt-4o-mini'
            >>> router.select_model(4)
            'o1-mini'
        """
        if not self.routing_enabled:
            # Phase 라우팅 비활성화 시 레거시 모델 사용
            logger.debug("Phase 라우팅 비활성화 - 레거시 모델 사용")
            return settings.llm_model

        if phase in [0, 1, 2]:
            model = settings.llm_model_phase0_2
            logger.debug(
                f"Phase {phase} → {model} "
                f"(비용: $0.000033, 속도: 1.02초, 정확도: 100%)"
            )
            return model

        elif phase == 3:
            model = settings.llm_model_phase3
            logger.debug(
                f"Phase {phase} → {model} "
                f"(비용: $0.000121, 속도: 4.61초, 정확도: 100%)"
            )
            return model

        elif phase == 4:
            model = settings.llm_model_phase4
            logger.debug(
                f"Phase {phase} → {model} "
                f"(비용: $0.0033, 속도: 5-15초, 정확도: 90-95%)"
            )
            return model

        else:
            logger.warning(
                f"알 수 없는 Phase {phase} - 레거시 모델 사용"
            )
            return settings.llm_model
    
    def select_model_with_config(self, phase: PhaseType) -> Tuple[str, ModelConfig]:
        """
        Phase에 맞는 최적 모델과 API 설정을 함께 반환 (v7.8.0)
        
        Args:
            phase: Estimator Phase (0, 1, 2, 3, 4)
        
        Returns:
            (model_name, model_config) 튜플
        
        Example:
            >>> router = ModelRouter()
            >>> model_name, config = router.select_model_with_config(4)
            >>> model_name
            'o1-mini'
            >>> config.api_type
            'responses'
            >>> config.max_output_tokens
            16000
        """
        # 모델 선택 (기존 로직)
        model_name = self.select_model(phase)
        
        # API 설정 조회
        config = model_config_manager.get_config(model_name)
        
        logger.debug(
            f"Phase {phase} → {model_name} "
            f"(api_type={config.api_type}, "
            f"max_output_tokens={config.max_output_tokens}, "
            f"reasoning_effort={config.reasoning_effort_support})"
        )
        
        return model_name, config

    def get_model_info(self, phase: PhaseType) -> dict:
        """
        Phase에 대한 모델 정보 반환 (모니터링/디버깅용)

        Args:
            phase: Estimator Phase

        Returns:
            모델 정보 (모델명, 비용, 속도, 정확도 등)
        """
        model = self.select_model(phase)

        # Phase별 실측 데이터
        model_info = {
            0: {
                "model": settings.llm_model_phase0_2,
                "phase_name": "Literal (Phase 0)",
                "cost_per_task": 0.000033,
                "avg_time_sec": 1.02,
                "accuracy": 100,
                "tested": True,
                "tasks": ["확정 데이터 조회", "직접 추론"],
            },
            1: {
                "model": settings.llm_model_phase0_2,
                "phase_name": "Inferred (Phase 1)",
                "cost_per_task": 0.000033,
                "avg_time_sec": 1.02,
                "accuracy": 100,
                "tested": True,
                "tasks": ["직접 추론", "단순 계산"],
            },
            2: {
                "model": settings.llm_model_phase0_2,
                "phase_name": "Formula (Phase 2)",
                "cost_per_task": 0.000033,
                "avg_time_sec": 1.02,
                "accuracy": 100,
                "tested": True,
                "tasks": ["공식 계산", "벤치마크 적용"],
            },
            3: {
                "model": settings.llm_model_phase3,
                "phase_name": "Guestimation (Phase 3)",
                "cost_per_task": 0.000121,
                "avg_time_sec": 4.61,
                "accuracy": 100,
                "tested": True,
                "tasks": ["템플릿 기반 추정", "벤치마크 조정"],
                "note": "개선된 프롬프트 적용 (v7.7.0+)",
            },
            4: {
                "model": settings.llm_model_phase4,
                "phase_name": "Fermi (Phase 4)",
                "cost_per_task": 0.0033,
                "avg_time_sec": 10.0,
                "accuracy": 90,
                "tested": False,
                "tasks": ["Fermi 분해", "복잡한 추론", "Discovery Sprint"],
                "note": "추정치 - 실제 테스트 필요",
            },
        }

        info = model_info.get(phase, {})
        info["current_model"] = model
        info["routing_enabled"] = self.routing_enabled

        return info

    def estimate_cost(
        self,
        phase_distribution: Optional[dict] = None
    ) -> dict:
        """
        Phase별 작업 분포에 따른 비용 추정

        Args:
            phase_distribution: Phase별 비율 (기본값: 실측 데이터)
                예: {0: 0.15, 1: 0.15, 2: 0.15, 3: 0.48, 4: 0.07}

        Returns:
            비용 정보 (평균 비용, 1,000회 비용, 10,000회 비용 등)
        """
        # 기본 분포 (실측 데이터)
        if phase_distribution is None:
            phase_distribution = {
                0: 0.15,  # Phase 0
                1: 0.15,  # Phase 1
                2: 0.15,  # Phase 2 (합계 45% - Phase 0-2)
                3: 0.48,  # Phase 3
                4: 0.07,  # Phase 4
            }

        # Phase별 비용
        phase_costs = {
            0: 0.000033,
            1: 0.000033,
            2: 0.000033,
            3: 0.000121,
            4: 0.0033,
        }

        # 가중 평균 계산
        avg_cost = sum(
            phase_distribution.get(phase, 0) * cost
            for phase, cost in phase_costs.items()
        )

        return {
            "avg_cost_per_task": avg_cost,
            "cost_per_1000": avg_cost * 1000,
            "cost_per_10000": avg_cost * 10000,
            "cost_per_100000": avg_cost * 100000,
            "phase_distribution": phase_distribution,
            "phase_costs": phase_costs,
            "routing_enabled": self.routing_enabled,
            "savings_vs_baseline": {
                "baseline_cost_per_1000": 15.0,
                "optimized_cost_per_1000": avg_cost * 1000,
                "savings_percent": (1 - (avg_cost * 1000) / 15.0) * 100,
            }
        }


# 글로벌 인스턴스 (싱글톤 패턴)
_router_instance: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """
    글로벌 ModelRouter 인스턴스 반환 (싱글톤)

    Returns:
        ModelRouter 인스턴스
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance


# 편의 함수
def select_model(phase: PhaseType) -> str:
    """
    Phase에 맞는 최적 모델 선택 (편의 함수)

    Args:
        phase: Estimator Phase (0, 1, 2, 3, 4)

    Returns:
        모델명

    Example:
        >>> from umis_rag.core.model_router import select_model
        >>> model = select_model(3)
        >>> print(model)
        'gpt-4o-mini'
    """
    router = get_model_router()
    return router.select_model(phase)


def select_model_with_config(phase: PhaseType) -> Tuple[str, ModelConfig]:
    """
    Phase에 맞는 모델 + API 설정 반환 (편의 함수, v7.8.0)
    
    Args:
        phase: Estimator Phase (0, 1, 2, 3, 4)
    
    Returns:
        (model_name, model_config) 튜플
    
    Example:
        >>> from umis_rag.core.model_router import select_model_with_config
        >>> model_name, config = select_model_with_config(4)
        >>> print(model_name)
        'o1-mini'
        >>> params = config.build_api_params(prompt="Test", reasoning_effort='medium')
    """
    router = get_model_router()
    return router.select_model_with_config(phase)


def get_model_info(phase: PhaseType) -> dict:
    """
    Phase에 대한 모델 정보 반환 (편의 함수)
    """
    router = get_model_router()
    return router.get_model_info(phase)


def estimate_cost(phase_distribution: Optional[dict] = None) -> dict:
    """
    비용 추정 (편의 함수)
    """
    router = get_model_router()
    return router.estimate_cost(phase_distribution)


# Usage Example
if __name__ == "__main__":
    import json

    router = get_model_router()

    print("=" * 60)
    print("UMIS LLM Model Router - Phase별 최적 모델 선택")
    print("=" * 60)
    print()

    # Phase별 모델 선택
    for phase in [0, 1, 2, 3, 4]:
        model = router.select_model(phase)
        info = router.get_model_info(phase)
        print(f"Phase {phase} ({info['phase_name']}):")
        print(f"  모델: {model}")
        print(f"  비용: ${info['cost_per_task']}/작업")
        print(f"  속도: {info['avg_time_sec']}초")
        print(f"  정확도: {info['accuracy']}%")
        print(f"  작업: {', '.join(info['tasks'])}")
        if 'note' in info:
            print(f"  참고: {info['note']}")
        print()

    # 비용 추정
    print("=" * 60)
    print("비용 추정 (실측 분포 기반)")
    print("=" * 60)
    cost_info = router.estimate_cost()
    print(json.dumps(cost_info, indent=2, ensure_ascii=False))
    print()

    print(f"📊 평균 비용: ${cost_info['avg_cost_per_task']:.6f}/작업")
    print(f"💰 1,000회: ${cost_info['cost_per_1000']:.2f}")
    print(f"💰 10,000회: ${cost_info['cost_per_10000']:.2f}")
    print()
    savings = cost_info['savings_vs_baseline']
    print(f"📉 기존 대비 절감: {savings['savings_percent']:.1f}%")
    print(f"   (${savings['baseline_cost_per_1000']:.2f} → "
          f"${savings['optimized_cost_per_1000']:.2f}/1,000회)")


