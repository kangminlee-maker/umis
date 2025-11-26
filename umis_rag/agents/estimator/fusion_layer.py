"""
FusionLayer - 센서 융합 계층 (v7.11.0 Stage 4)

역할:
- Evidence, Prior, Fermi 결과를 융합
- 가중 평균 + 범위 교집합
- Hard Bounds 클리핑

설계 원칙:
- 센서 융합 (Sensor Fusion) 패턴
- 증거 > Prior > Fermi (우선순위)
- Hard Bounds 절대 준수
- 가중치 투명성 (fusion_weights)
"""

from typing import Optional, List, Tuple, Dict, Any
import math

from umis_rag.utils.logger import logger

from .common.estimation_result import EstimationResult, Evidence


class FusionLayer:
    """
    FusionLayer - 센서 융합 계층 (v7.11.0)
    
    역할:
    -----
    - 여러 추정 결과를 융합하여 최종 값 결정
    - 가중 평균 + 범위 교집합
    - Hard Bounds 클리핑
    
    융합 전략:
    ---------
    1. Evidence (확정 값): 있으면 100% 사용
    2. Evidence + Prior: 가중 평균 (certainty 기반)
    3. Evidence + Prior + Fermi: 3-way 융합
    4. Hard Bounds 클리핑 (최종)
    
    가중치 계산:
    -----------
    - Certainty 기반: high=0.9, medium=0.6, low=0.3
    - 정규화: 합이 1이 되도록
    """
    
    def __init__(self):
        """초기화"""
        logger.info("[FusionLayer] 초기화")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 인터페이스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def synthesize(
        self,
        evidence: Evidence,
        prior_result: Optional[EstimationResult] = None,
        fermi_result: Optional[EstimationResult] = None
    ) -> EstimationResult:
        """
        융합 (v7.11.0)
        
        Args:
            evidence: 수집된 증거
            prior_result: Prior 추정 결과 (선택)
            fermi_result: Fermi 추정 결과 (선택)
        
        Returns:
            융합된 EstimationResult
        """
        logger.info("[FusionLayer] 융합 시작")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Case 1: 확정 값이 있으면 100% 사용
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if evidence.definite_value is not None:
            logger.info(f"  확정 값 사용: {evidence.definite_value:,.0f}")
            
            from .common.estimation_result import create_definite_result
            result = create_definite_result(
                value=evidence.definite_value,
                evidence=evidence,
                reasoning="확정 값 (증거 기반)"
            )
            result.fusion_weights = {'evidence': 1.0}
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Case 2: Prior만 있음
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if prior_result and not fermi_result:
            logger.info(f"  Prior만 사용: {prior_result.value:,.0f}")
            
            # Hard Bounds 클리핑
            final_value = self._clip_to_hard_bounds(prior_result.value, evidence)
            
            result = EstimationResult(
                value=final_value,
                value_range=prior_result.value_range,
                certainty=prior_result.certainty,
                uncertainty=prior_result.uncertainty,
                source="Fusion(Prior)",
                reasoning=f"Prior 추정 (Hard Bounds 클리핑)",
                cost=prior_result.cost,
                used_evidence=[evidence],
                fusion_weights={'prior': 1.0}
            )
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Case 3: Fermi만 있음
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if fermi_result and not prior_result:
            logger.info(f"  Fermi만 사용: {fermi_result.value:,.0f}")
            
            # Hard Bounds 클리핑
            final_value = self._clip_to_hard_bounds(fermi_result.value, evidence)
            
            result = EstimationResult(
                value=final_value,
                certainty=fermi_result.certainty,
                uncertainty=fermi_result.uncertainty,
                source="Fusion(Fermi)",
                reasoning=f"Fermi 분해 (Hard Bounds 클리핑)",
                decomposition=fermi_result.decomposition,
                cost=fermi_result.cost,
                used_evidence=[evidence],
                fusion_weights={'fermi': 1.0}
            )
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Case 4: Prior + Fermi 융합
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if prior_result and fermi_result:
            logger.info(f"  Prior + Fermi 융합")
            
            # 가중치 계산
            weights = self._calculate_weights(prior_result, fermi_result)
            
            logger.info(f"  가중치: prior={weights['prior']:.2f}, fermi={weights['fermi']:.2f}")
            
            # 가중 평균
            weighted_value = (
                prior_result.value * weights['prior'] +
                fermi_result.value * weights['fermi']
            )
            
            # Hard Bounds 클리핑
            final_value = self._clip_to_hard_bounds(weighted_value, evidence)
            
            # 범위 교집합
            final_range = self._intersect_ranges(
                prior_result.value_range,
                fermi_result.value_range if fermi_result.value_range else None
            )
            
            # Certainty 종합
            avg_certainty_score = (
                prior_result.get_certainty_score() * weights['prior'] +
                fermi_result.get_certainty_score() * weights['fermi']
            )
            
            if avg_certainty_score >= 0.8:
                certainty = 'high'
            elif avg_certainty_score >= 0.5:
                certainty = 'medium'
            else:
                certainty = 'low'
            
            # 비용 합산
            total_cost = {
                'llm_calls': prior_result.cost.get('llm_calls', 0) + fermi_result.cost.get('llm_calls', 0),
                'variables': prior_result.cost.get('variables', 0) + fermi_result.cost.get('variables', 0),
                'time': prior_result.cost.get('time', 0) + fermi_result.cost.get('time', 0)
            }
            
            result = EstimationResult(
                value=final_value,
                value_range=final_range,
                certainty=certainty,
                uncertainty=(prior_result.uncertainty + fermi_result.uncertainty) / 2,
                source="Fusion(Prior+Fermi)",
                reasoning=f"Prior + Fermi 가중 융합 (가중치: {weights})",
                decomposition=fermi_result.decomposition,
                cost=total_cost,
                used_evidence=[evidence],
                fusion_weights=weights
            )
            
            logger.info(f"  융합 결과: {final_value:,.0f} (certainty={certainty})")
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Case 5: 아무것도 없음 (Fallback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.warning("  융합 실패: 추정 결과 없음")
        
        # Hard Bounds 중간값 사용
        if evidence.hard_bounds:
            min_val, max_val = evidence.hard_bounds
            if min_val is not None and max_val is not None:
                fallback_value = (min_val + max_val) / 2
                logger.info(f"  Fallback: Hard Bounds 중간값 = {fallback_value:,.0f}")
            elif min_val is not None:
                fallback_value = min_val * 2  # 하한의 2배
                logger.info(f"  Fallback: 하한의 2배 = {fallback_value:,.0f}")
            elif max_val is not None:
                fallback_value = max_val / 2  # 상한의 절반
                logger.info(f"  Fallback: 상한의 절반 = {fallback_value:,.0f}")
            else:
                fallback_value = 1.0
        else:
            fallback_value = 1.0
        
        result = EstimationResult(
            value=fallback_value,
            certainty='low',
            uncertainty=0.8,
            source="Fusion(Fallback)",
            reasoning="추정 실패 → Hard Bounds 기반 Fallback",
            used_evidence=[evidence],
            fusion_weights={}
        )
        
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Private Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _calculate_weights(
        self,
        prior_result: EstimationResult,
        fermi_result: EstimationResult
    ) -> Dict[str, float]:
        """
        가중치 계산 (certainty 기반)
        
        Args:
            prior_result: Prior 결과
            fermi_result: Fermi 결과
        
        Returns:
            {'prior': 0.6, 'fermi': 0.4}
        """
        # Certainty 점수
        prior_score = prior_result.get_certainty_score()
        fermi_score = fermi_result.get_certainty_score()
        
        # 정규화
        total = prior_score + fermi_score
        
        if total > 0:
            prior_weight = prior_score / total
            fermi_weight = fermi_score / total
        else:
            # 동일 가중치
            prior_weight = 0.5
            fermi_weight = 0.5
        
        return {
            'prior': prior_weight,
            'fermi': fermi_weight
        }
    
    def _clip_to_hard_bounds(
        self,
        value: float,
        evidence: Evidence
    ) -> float:
        """
        Hard Bounds 클리핑
        
        Args:
            value: 원본 값
            evidence: 증거 (hard_bounds)
        
        Returns:
            클리핑된 값
        """
        if not evidence.hard_bounds:
            return value
        
        min_val, max_val = evidence.hard_bounds
        
        original_value = value
        
        if min_val is not None:
            value = max(value, min_val)
        
        if max_val is not None:
            value = min(value, max_val)
        
        if value != original_value:
            logger.warning(f"  Hard Bounds 클리핑: {original_value:,.0f} → {value:,.0f}")
        
        return value
    
    def _intersect_ranges(
        self,
        range1: Optional[Tuple[float, float]],
        range2: Optional[Tuple[float, float]]
    ) -> Optional[Tuple[float, float]]:
        """
        범위 교집합
        
        Args:
            range1: (min1, max1)
            range2: (min2, max2)
        
        Returns:
            (min, max) 교집합
        """
        if not range1 and not range2:
            return None
        
        if not range1:
            return range2
        
        if not range2:
            return range1
        
        min1, max1 = range1
        min2, max2 = range2
        
        # 교집합
        intersect_min = max(min1, min2)
        intersect_max = min(max1, max2)
        
        # 교집합이 비어있으면 합집합 사용
        if intersect_min > intersect_max:
            logger.warning(f"  범위 교집합 없음 → 합집합 사용")
            union_min = min(min1, min2)
            union_max = max(max1, max2)
            return (union_min, union_max)
        
        return (intersect_min, intersect_max)
