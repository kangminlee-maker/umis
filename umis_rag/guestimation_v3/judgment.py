"""
Judgment Synthesizer

증거 종합 판단
"""

from typing import List, Dict, Optional, Tuple
import statistics

from umis_rag.utils.logger import logger
from .models import (
    Context,
    ValueEstimate,
    SoftGuide,
    Boundary,
    Intent
)


class JudgmentSynthesizer:
    """
    증거 종합 판단
    
    역할:
    -----
    - 여러 값 추정 평가
    - 맥락 기반 전략 선택
    - 최종 값 결정
    
    전략:
    -----
    - weighted_average: 가중 평균
    - conservative: 보수적 하한
    - range: 범위 제시
    - single_best: 최고 증거만
    """
    
    def synthesize(
        self,
        value_estimates: List[ValueEstimate],
        context: Context,
        soft_guides: Optional[List[SoftGuide]] = None
    ) -> Dict:
        """
        증거 종합
        
        Args:
            value_estimates: 값 추정들
            context: 맥락
            soft_guides: Soft 가이드 (검증용)
        
        Returns:
            {
                'value': float,
                'range': tuple,
                'confidence': float,
                'strategy': str,
                'reasoning': str
            }
        """
        if not value_estimates:
            logger.warning("[Judgment] 증거 없음")
            return {
                'value': None,
                'confidence': 0.0,
                'strategy': 'none',
                'reasoning': '증거 없음'
            }
        
        logger.info(f"[Judgment] {len(value_estimates)}개 증거 종합")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: 전략 선택
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        strategy = self._select_strategy(value_estimates, context)
        logger.info(f"  전략: {strategy}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: 전략별 계산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if strategy == "conservative":
            result = self._conservative_judgment(value_estimates)
        
        elif strategy == "weighted_average":
            result = self._weighted_average_judgment(value_estimates)
        
        elif strategy == "range":
            result = self._range_judgment(value_estimates)
        
        elif strategy == "single_best":
            result = self._single_best_judgment(value_estimates)
        
        else:
            result = self._weighted_average_judgment(value_estimates)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: Soft Guide 검증 (선택)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if soft_guides and result['value']:
            validation = self._validate_with_soft_guides(result['value'], soft_guides)
            result['soft_validation'] = validation
        
        result['strategy'] = strategy
        
        return result
    
    def _select_strategy(
        self,
        estimates: List[ValueEstimate],
        context: Context
    ) -> str:
        """전략 자동 선택"""
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 의도 기반
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if context.intent == Intent.MAKE_DECISION:
            return "conservative"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 증거 개수
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if len(estimates) == 1:
            return "single_best"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. 값 분산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        values = [e.value for e in estimates]
        mean_val = statistics.mean(values)
        
        if mean_val == 0:
            return "weighted_average"
        
        cv = statistics.stdev(values) / mean_val if len(values) > 1 else 0
        
        if cv > 0.50:  # 분산 큼
            return "range"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. 가중치 차이
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        confidences = [e.confidence for e in estimates]
        max_conf = max(confidences)
        
        if max_conf > 0.9 and (max_conf - min(confidences)) > 0.3:
            return "single_best"
        
        # 기본값
        return "weighted_average"
    
    def _weighted_average_judgment(self, estimates: List[ValueEstimate]) -> Dict:
        """가중 평균 판단"""
        
        total_weight = sum(e.confidence for e in estimates)
        
        weighted_sum = sum(e.value * e.confidence for e in estimates)
        
        final_value = weighted_sum / total_weight
        
        # 불확실성 계산
        values = [e.value for e in estimates]
        uncertainty = statistics.stdev(values) / statistics.mean(values) if len(values) > 1 else 0.3
        
        return {
            'value': final_value,
            'confidence': min(total_weight / len(estimates), 1.0),
            'uncertainty': uncertainty,
            'reasoning': f"{len(estimates)}개 증거 가중 평균"
        }
    
    def _conservative_judgment(self, estimates: List[ValueEstimate]) -> Dict:
        """보수적 판단 (하한 선택)"""
        
        # 신뢰도 높은 순으로 정렬
        sorted_estimates = sorted(estimates, key=lambda x: x.confidence, reverse=True)
        
        # 상위 3개 중 최소값
        top_values = [e.value for e in sorted_estimates[:3]]
        conservative_value = min(top_values)
        
        return {
            'value': conservative_value,
            'confidence': sorted_estimates[0].confidence * 0.9,  # 보수적 할인
            'uncertainty': 0.30,
            'reasoning': f"보수적 하한 (상위 {len(top_values)}개 중 최소)"
        }
    
    def _range_judgment(self, estimates: List[ValueEstimate]) -> Dict:
        """범위 제시"""
        
        values = [e.value for e in estimates]
        
        min_val = min(values)
        max_val = max(values)
        median_val = statistics.median(values)
        
        return {
            'value': median_val,
            'range': (min_val, max_val),
            'confidence': 0.60,
            'uncertainty': (max_val - min_val) / (2 * median_val),
            'reasoning': f"범위 제시 ({min_val:,.0f} ~ {max_val:,.0f})"
        }
    
    def _single_best_judgment(self, estimates: List[ValueEstimate]) -> Dict:
        """최고 증거만 사용"""
        
        best = max(estimates, key=lambda x: x.confidence)
        
        return {
            'value': best.value,
            'confidence': best.confidence,
            'uncertainty': best.uncertainty,
            'reasoning': f"최고 신뢰 증거: {best.source_type.value}"
        }
    
    def _validate_with_soft_guides(
        self,
        value: float,
        soft_guides: List[SoftGuide]
    ) -> Dict:
        """Soft Guide로 검증"""
        
        warnings = []
        
        for guide in soft_guides:
            if guide.suggested_range:
                min_r, max_r = guide.suggested_range
                
                if value < min_r:
                    warnings.append(f"{guide.source_type.value}: 하한({min_r}) 미달")
                elif value > max_r:
                    warnings.append(f"{guide.source_type.value}: 상한({max_r}) 초과")
        
        return {
            'in_range': len(warnings) == 0,
            'warnings': warnings
        }

