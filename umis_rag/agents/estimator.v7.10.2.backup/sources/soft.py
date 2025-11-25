"""
Soft Constraints Sources (v7.8.0 재설계)

Knock-out Gate: 명백한 위반 감지
- 법률/규범: 70% 규칙 (명백한 위반)
- 통계 패턴: 자연법칙 (p5-p95)
- 행동경제학: 인간본능 범위

v7.8.0 핵심 변경:
------------------
- "Soft"이지만 실제로는 명백한 제약
- 준수율 계산 불필요 (추가 데이터 없음)
- 임계값 기반 간단한 Knock-out
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
    
    def validate(self, question: str, estimated_value: float) -> Optional[Dict[str, Any]]:
        """
        Soft Constraint 검증 (v7.8.0)
        
        Soft는 자동 Knock-out 아님 → 경고 + 사용자 확인
        
        Args:
            question: 질문
            estimated_value: 추정값
        
        Returns:
            None: 통과 ✅
            Dict: 경고 정보 ⚠️ (사용자 확인 필요)
                {
                    'warning': True,
                    'message': '경고 메시지',
                    'severity': 'high' | 'medium' | 'low',
                    'user_confirmation_needed': True
                }
        """
        raise NotImplementedError


class LegalNormSource(SoftConstraintBase):
    """
    법률/규범 (v7.8.0 재설계)
    
    역할:
    -----
    - Knock-out Gate: 명백한 위반 감지
    - 70% 규칙 (최저의 70% 미만 or 최대의 130% 초과)
    
    원칙:
    -----
    - 법률은 대부분 지킴 (사회 유지 조건)
    - 70% 미만 = 명백히 비현실적
    - 준수율 계산 불필요 (추가 데이터 없음)
    """
    
    def __init__(self):
        # 법률 규범 DB (Knock-out 임계값)
        self.legal_norms = {
            '최저임금': {
                'legal_value': 9860,
                'direction': 'minimum',  # 최소값 제약
                'tolerance': 0.70,  # 70% 미만이면 knock-out
                'reasoning': '최저임금의 70% 미만은 명백한 위반 (사회 유지 불가)'
            },
            '시급': {
                'legal_value': 9860,
                'direction': 'minimum',
                'tolerance': 0.70,
                'reasoning': '최저임금의 70% 미만은 명백한 위반'
            },
            '주당근로': {
                'legal_value': 52,
                'direction': 'maximum',  # 최대값 제약
                'tolerance': 1.30,  # 130% 초과면 knock-out
                'reasoning': '법정 최대의 130% 초과는 명백한 위반'
            },
            '근로시간': {
                'legal_value': 52,
                'direction': 'maximum',
                'tolerance': 1.30,
                'reasoning': '주당 근로시간 법정 최대의 130% 초과는 비현실적'
            }
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """법률 규범 수집 (정보 제공용, deprecated)"""
        
        # v7.8.0: collect는 거의 사용 안 됨
        # validate() 메서드 사용 권장
        return []
    
    def validate(self, question: str, estimated_value: float) -> Optional[Dict[str, Any]]:
        """
        Soft Constraint 검증 (경고 + 사용자 확인)
        
        Args:
            question: 질문
            estimated_value: 추정값
        
        Returns:
            None: 통과 ✅
            Dict: 경고 정보 ⚠️
        """
        
        # 키워드 매칭
        for norm_key, norm_data in self.legal_norms.items():
            if norm_key in question:
                
                # 최소값 제약 (예: 최저임금)
                if norm_data.get('direction') == 'minimum':
                    threshold = norm_data['legal_value'] * norm_data['tolerance']
                    
                    if estimated_value < threshold:
                        violation_pct = (threshold - estimated_value) / threshold * 100
                        
                        return {
                            'warning': True,
                            'severity': 'high',  # 법률 위반은 high
                            'message': (
                                f"⚠️ 법률 제약 위반 가능성\n"
                                f"  추정값: {estimated_value:,.0f}원\n"
                                f"  임계값: {threshold:,.0f}원 (최저 {norm_data['legal_value']:,}원 × {norm_data['tolerance']})\n"
                                f"  차이: -{violation_pct:.0f}%\n\n"
                                f"📋 근거: {norm_data['reasoning']}\n\n"
                                f"⚠️ 이 추정값을 사용하시겠습니까?\n"
                                f"   - 예외 상황 (지하경제, 특수 케이스)일 수 있음\n"
                                f"   - 또는 추정 오류일 수 있음"
                            ),
                            'threshold': threshold,
                            'legal_value': norm_data['legal_value'],
                            'user_confirmation_needed': True
                        }
                
                # 최대값 제약 (예: 최대 근로시간)
                elif norm_data.get('direction') == 'maximum':
                    threshold = norm_data['legal_value'] * norm_data['tolerance']
                    
                    if estimated_value > threshold:
                        violation_pct = (estimated_value - threshold) / threshold * 100
                        
                        return {
                            'warning': True,
                            'severity': 'high',
                            'message': (
                                f"⚠️ 법률 제약 위반 가능성\n"
                                f"  추정값: {estimated_value:,.0f}시간\n"
                                f"  임계값: {threshold:,.0f}시간 (최대 {norm_data['legal_value']:,}시간 × {norm_data['tolerance']})\n"
                                f"  차이: +{violation_pct:.0f}%\n\n"
                                f"📋 근거: {norm_data['reasoning']}\n\n"
                                f"⚠️ 이 추정값을 사용하시겠습니까?\n"
                                f"   - 예외 상황일 수 있음\n"
                                f"   - 또는 추정 오류일 수 있음"
                            ),
                            'threshold': threshold,
                            'legal_value': norm_data['legal_value'],
                            'user_confirmation_needed': True
                        }
        
        return None  # 통과 ✅


class StatisticalPatternSource(SoftConstraintBase):
    """
    통계 패턴 (v7.8.0 재설계)
    
    역할:
    -----
    - Knock-out Gate: 자연법칙 범위 (p5-p95)
    - 예: 흡연율 5-60%, 이탈률 0-50%
    
    원칙:
    -----
    - 통계 패턴은 자연법칙 수준
    - p5-p95 범위 벗어남 = 명백히 비현실적
    """
    
    def __init__(self):
        # 통계 패턴 DB (자연 범위)
        self.statistical_ranges = {
            '흡연율': {
                'natural_range': (0.05, 0.60),  # 5-60%
                'reasoning': '성인 흡연율의 자연 범위 (세계 통계 p5-p95)'
            },
            '이탈률': {
                'natural_range': (0.00, 0.50),  # 0-50%
                'reasoning': '비즈니스 이탈률의 자연 범위 (50% 초과는 비정상)'
            },
            'churn': {
                'natural_range': (0.00, 0.50),
                'reasoning': 'Churn rate 50% 초과는 비즈니스 지속 불가능'
            }
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """통계 패턴 수집 (deprecated)"""
        
        # v7.8.0: validate() 사용 권장
        return []
    
    def validate(self, question: str, estimated_value: float) -> Optional[Dict[str, Any]]:
        """
        Soft Constraint 검증 (경고 + 사용자 확인)
        
        Args:
            question: 질문
            estimated_value: 추정값
        
        Returns:
            None: 통과 ✅
            Dict: 경고 정보 ⚠️
        """
        
        # 키워드 매칭
        for pattern_key, pattern_data in self.statistical_ranges.items():
            if pattern_key in question.lower():
                
                lower, upper = pattern_data['natural_range']
                
                if estimated_value < lower or estimated_value > upper:
                    
                    severity = 'high' if (estimated_value < lower * 0.5 or estimated_value > upper * 1.5) else 'medium'
                    
                    return {
                        'warning': True,
                        'severity': severity,
                        'message': (
                            f"⚠️ 통계 패턴 이상치 감지\n"
                            f"  추정값: {estimated_value:.3f}\n"
                            f"  자연 범위: [{lower}, {upper}] (p5-p95)\n\n"
                            f"📋 근거: {pattern_data['reasoning']}\n\n"
                            f"⚠️ 이 추정값을 사용하시겠습니까?\n"
                            f"   - 특수한 상황일 수 있음\n"
                            f"   - 또는 추정 오류일 수 있음"
                        ),
                        'natural_range': (lower, upper),
                        'user_confirmation_needed': True
                    }
        
        return None  # 통과 ✅
   
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 이하 기존 코드 (샘플 구현, deprecated)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _collect_deprecated(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """통계 패턴 수집 (deprecated)"""
        
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
                    source_type=SourceType.SOFT,  # v7.8.1: STATISTICAL deprecated
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
                    source_type=SourceType.SOFT,  # v7.8.1: STATISTICAL deprecated
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
    행동경제학 (v7.8.0 재설계)
    
    역할:
    -----
    - Knock-out Gate: 인간본능 범위
    - 예: 전환율 0.5-30%, 가격 민감도 0.3-2.5
    
    원칙:
    -----
    - 인간 행동은 일정 범위 내
    - 범위 벗어남 = 명백히 비현실적
    """
    
    def __init__(self):
        # 행동경제학 패턴 DB (자연 범위)
        self.behavioral_ranges = {
            '전환율': {
                'natural_range': (0.005, 0.30),  # 0.5-30%
                'reasoning': '전환율 30% 초과는 비현실적 (인간 행동 한계)'
            },
            'conversion': {
                'natural_range': (0.005, 0.30),
                'reasoning': 'Conversion rate > 30%는 극히 드뭄'
            },
            '가격민감도': {
                'natural_range': (0.3, 2.5),
                'reasoning': '가격 탄력성의 일반적 범위'
            }
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """행동경제학 패턴 수집 (deprecated)"""
        
        # v7.8.0: validate() 사용 권장
        return []
    
    def validate(self, question: str, estimated_value: float) -> Optional[Dict[str, Any]]:
        """
        Soft Constraint 검증 (경고 + 사용자 확인)
        
        Args:
            question: 질문
            estimated_value: 추정값
        
        Returns:
            None: 통과 ✅
            Dict: 경고 정보 ⚠️
        """
        
        # 키워드 매칭
        for pattern_key, pattern_data in self.behavioral_ranges.items():
            if pattern_key in question.lower():
                
                lower, upper = pattern_data['natural_range']
                
                if estimated_value < lower or estimated_value > upper:
                    
                    severity = 'medium'  # 행동경제학은 medium
                    
                    return {
                        'warning': True,
                        'severity': severity,
                        'message': (
                            f"⚠️ 행동 패턴 이상치 감지\n"
                            f"  추정값: {estimated_value:.3f}\n"
                            f"  인간본능 범위: [{lower}, {upper}]\n\n"
                            f"📋 근거: {pattern_data['reasoning']}\n\n"
                            f"⚠️ 이 추정값을 사용하시겠습니까?\n"
                            f"   - 혁신적 비즈니스 모델일 수 있음\n"
                            f"   - 또는 추정 오류일 수 있음"
                        ),
                        'natural_range': (lower, upper),
                        'user_confirmation_needed': True
                    }
        
        return None  # 통과 ✅
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 이하 기존 코드 (deprecated)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _collect_deprecated(self, question: str, context: Optional[Context] = None) -> List[SoftGuide]:
        """행동경제학 통찰 수집 (deprecated)"""
        
        guides = []
        
        # 구독/Churn 관련 → Loss Aversion
        if any(word in question for word in ['구독', 'churn', '해지', '이탈']):
            pattern = self.patterns['loss_aversion']
            
            guide = SoftGuide(
                source_type=SourceType.SOFT,  # v7.8.1: BEHAVIORAL deprecated
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
                source_type=SourceType.SOFT,  # v7.8.1: BEHAVIORAL deprecated
                insight=pattern['insight'],
                confidence=0.70,
                reasoning="행동경제학: Power Law"
            )
            
            guides.append(guide)
        
        return guides

