"""
Soft Constraints Sources

범위 제시, 검증, 통찰
- 법률/규범
- 통계 패턴  
- 행동경제학
"""

from typing import Optional, List, Dict, Any
import statistics

from umis_rag.utils.logger import logger
from ..models import SoftGuide, SourceType, Context, DistributionType, DistributionInfo


class SoftConstraintBase:
    """Soft Constraint Base Class"""
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """제약 수집"""
        raise NotImplementedError


class LegalNormSource(SoftConstraintBase):
    """
    법률/규범
    
    역할:
    -----
    - range 제시 (base + exceptions)
    - 예: 최저임금 [9860, 15000]
    """
    
    def __init__(self):
        # 주요 법률 상수 (Built-in과 다르게 range 제공)
        self.legal_norms = {
            '최저임금': {
                'base_value': 9860,
                'typical_range': (9860, 15000),
                'exceptions': [
                    {'condition': '수습', 'multiplier': 0.90}
                ],
                'confidence': 0.90
            },
            '주당근로': {
                'base_value': 52,
                'typical_range': (40, 52),
                'note': '기본 40 + 연장 12',
                'confidence': 0.95
            }
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """법률 규범 수집"""
        
        guides = []
        
        # 키워드 매칭
        for norm_key, norm_data in self.legal_norms.items():
            if norm_key in question:
                guide = SoftGuide(
                    source_type=SourceType.LEGAL,
                    suggested_range=norm_data['typical_range'],
                    typical_value=norm_data['base_value'],
                    exceptions=norm_data.get('exceptions', []),
                    confidence=norm_data['confidence'],
                    reasoning=f"법률 규범: {norm_key}"
                )
                guides.append(guide)
        
        return guides


class StatisticalPatternSource(SoftConstraintBase):
    """
    통계 패턴
    
    역할:
    -----
    - 분포 정보 제공
    - 분포 타입별 다른 처리
    - Soft + Value 겸용 (조건부)
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """통계 패턴 수집"""
        
        guides = []
        
        # TODO: 실제로는 RAG 검색 or DB 조회
        # 현재는 샘플 구현
        
        # 음식점 관련 질문
        if '음식점' in question or '식당' in question:
            if '매출' in question or '수익' in question:
                # 샘플 분포 (실제로는 데이터에서)
                distribution = DistributionInfo(
                    distribution_type=DistributionType.POWER_LAW,
                    percentiles={
                        'p10': 1000,
                        'p25': 1500,
                        'p50': 2000,  # median
                        'p75': 3000,
                        'p90': 4500
                    },
                    alpha=2.0,
                    sample_size=500,
                    data_year=2024,
                    cv=0.60  # 높은 변동
                )
                
                guide = SoftGuide(
                    source_type=SourceType.STATISTICAL,
                    suggested_range=(1000, 4500),  # p10-p90
                    distribution=distribution,
                    confidence=0.65,
                    reasoning="음식점 매출 통계 패턴 (Power Law 분포)"
                )
                
                guides.append(guide)
        
        # SaaS 관련
        if 'saas' in question.lower() or '구독' in question:
            if 'churn' in question.lower() or '해지' in question or '이탈' in question:
                distribution = DistributionInfo(
                    distribution_type=DistributionType.NORMAL,
                    mean=0.06,
                    std_dev=0.01,
                    percentiles={
                        'p10': 0.05,
                        'p50': 0.06,
                        'p90': 0.07
                    },
                    sample_size=100,
                    cv=0.17  # 낮은 변동
                )
                
                guide = SoftGuide(
                    source_type=SourceType.STATISTICAL,
                    suggested_range=(0.05, 0.07),
                    typical_value=0.06,
                    distribution=distribution,
                    confidence=0.80,
                    reasoning="SaaS Churn Rate 통계 (정규분포)"
                )
                
                guides.append(guide)
        
        return guides


class BehavioralInsightSource(SoftConstraintBase):
    """
    행동경제학 통찰
    
    역할:
    -----
    - 정성적 통찰만
    - 정량화 포기
    - 해석 보조
    """
    
    def __init__(self):
        # 주요 행동경제학 패턴
        self.patterns = {
            'loss_aversion': {
                'insight': '손실은 이득의 약 2배 크게 느껴짐',
                'implication': '가격 인상 시 이탈 증가, 할인 시 유입 증가',
                'quantitative_hint': {'direction': 'asymmetric', 'ratio': 2.0}
            },
            'hyperbolic_discounting': {
                'insight': '먼 미래보다 가까운 미래를 과대평가',
                'implication': '장기 구독보다 단기 선호',
            },
            'power_law': {
                'insight': '20%가 80%를 차지 (파레토 법칙)',
                'implication': '상위 고객에 집중',
            }
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """행동경제학 통찰 수집"""
        
        guides = []
        
        # 구독/Churn 관련 → Loss Aversion
        if any(word in question for word in ['구독', 'churn', '해지', '이탈']):
            pattern = self.patterns['loss_aversion']
            
            guide = SoftGuide(
                source_type=SourceType.BEHAVIORAL,
                insight=pattern['insight'],
                quantitative_hint=pattern.get('quantitative_hint'),
                confidence=0.60,
                reasoning="행동경제학: Loss Aversion"
            )
            
            guides.append(guide)
        
        # 시장 분포 → Power Law
        if any(word in question for word in ['시장', '분포', '점유율']):
            pattern = self.patterns['power_law']
            
            guide = SoftGuide(
                source_type=SourceType.BEHAVIORAL,
                insight=pattern['insight'],
                confidence=0.70,
                reasoning="행동경제학: Power Law"
            )
            
            guides.append(guide)
        
        return guides

