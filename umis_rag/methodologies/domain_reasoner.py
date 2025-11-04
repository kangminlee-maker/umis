"""
Domain-Centric Reasoner Engine
10-Signal Stack 기반 정밀 추론

신호 우선순위:
s3 → s8 → s6 → s10 → s2 → s9 → s7 → s5 → s4 → s1
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import yaml
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


# ========================================
# 데이터 클래스
# ========================================

@dataclass
class SignalResult:
    """신호 처리 결과"""
    signal_name: str
    weight: float
    value: Any
    confidence: float
    evidence: List[Dict]
    umis_mapping: str


@dataclass
class DomainReasonerResult:
    """Domain Reasoner 최종 결과"""
    point_estimate: float
    range_estimate: Tuple[float, float]
    should_vs_will: Dict[str, Any]
    signal_breakdown: Dict[str, SignalResult]
    evidence_table: List[Dict]
    verification_log: Dict[str, Any]
    residual_unknowns: List[str]
    confidence: str  # 'Low', 'Medium', 'High'
    next_actions: List[Dict]


# ========================================
# Signal 클래스들
# ========================================

class BaseSignal:
    """신호 기본 클래스"""
    
    def __init__(self, weight: float):
        self.weight = weight
        self.logger = get_logger(self.__class__.__name__)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """신호 처리 (하위 클래스에서 구현)"""
        raise NotImplementedError


class Signal1_LLMGuess(BaseSignal):
    """s1: LLM Guess (0.15)"""
    
    def __init__(self, weight=0.15):
        super().__init__(weight)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """LLM 기반 초안 생성"""
        # TODO: 구현
        pass


class Signal2_RAGConsensus(BaseSignal):
    """s2: RAG Consensus (0.9) - 핵심!"""
    
    def __init__(self, weight=0.9):
        super().__init__(weight)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """RAG에서 합의 범위 추출 (독립 출처 ≥2)"""
        # TODO: UMIS RAG 검색 구현
        pass


class Signal3_Laws(BaseSignal):
    """s3: Laws/Ethics/Physics (1.0) - 최우선!"""
    
    def __init__(self, weight=1.0):
        super().__init__(weight)
    
    def check(self, definition: Dict) -> Dict[str, Any]:
        """법/윤리/물리 제약 확인"""
        # TODO: 규제 검증 구현
        pass


class Signal4_BehavioralEcon(BaseSignal):
    """s4: Behavioral Economics (0.6)"""
    
    def __init__(self, weight=0.6):
        super().__init__(weight)
        self.biases = {
            'loss_aversion': 2.5,
            'status_quo_bias': 0.5,
            'anchoring': (0.7, 1.3),
            'hyperbolic_discounting': 0.5
        }
    
    def adjust_should_vs_will(self, fused_result: Dict) -> Dict[str, Any]:
        """
        Should (규범) vs Will (현실) 분리
        
        Args:
            fused_result: {
                'value': float (융합된 추정값),
                'range': tuple (하한, 상한),
                'context': dict (시장 맥락)
            }
        
        Returns:
            {
                'should': {...},  # 규범적 결론
                'will': {...},    # 현실적 예측
                'gap': {...}      # 차이 분석
            }
        """
        
        value = fused_result.get('value', 0)
        context = fused_result.get('context', {})
        
        self.logger.info(f"  행동경제학 보정 시작 (기준값: {value:,.0f})")
        
        # ===== Should: 편향 없는 이상적 값 =====
        
        should = {
            'value': value,
            'rationale': '이상적/규범적 결론 (편향 제거)',
            'assumptions': [
                '합리적 의사결정',
                '완전 정보',
                '시간 일관성 (현재=미래)'
            ],
            'use_case': '정책 권고, 목표 설정, 잠재 시장'
        }
        
        self.logger.info(f"  Should: {should['value']:,.0f} (이상적)")
        
        # ===== Will: 현실적 예측 (편향 반영) =====
        
        will_value = value
        adjustments = []
        
        # 1. 가격 인상/변경 → 손실회피
        if context.get('price_change', False):
            factor = 0.4  # 60% 저항
            will_value *= factor
            adjustments.append({
                'bias': 'loss_aversion',
                'factor': factor,
                'reason': '가격 인상 저항 (손실 = 이득 × 2.5)',
                'impact': f'{(1-factor)*100:.0f}% 감소'
            })
            self.logger.info(f"    - 손실회피: ×{factor} (가격 인상 저항)")
        
        # 2. 현상 유지 vs 전환 → 현상유지 편향
        if context.get('requires_switch', False):
            factor = 0.5  # 50% 전환율
            will_value *= factor
            adjustments.append({
                'bias': 'status_quo_bias',
                'factor': factor,
                'reason': '전환 저항 (현상 유지 선호)',
                'impact': f'{(1-factor)*100:.0f}% 감소'
            })
            self.logger.info(f"    - 현상유지 편향: ×{factor} (전환 저항)")
        
        # 3. 시장 지배력 → 가격 결정력
        market_power = context.get('market_power', 0)  # 0-1
        if market_power > 0.7:
            factor = 1 + (market_power * 0.3)  # 최대 1.3배
            will_value *= factor
            adjustments.append({
                'bias': 'market_power',
                'factor': factor,
                'reason': f'독과점 시장 (지배력 {market_power*100:.0f}%)',
                'impact': f'{(factor-1)*100:.0f}% 증가'
            })
            self.logger.info(f"    - 시장 지배력: ×{factor} (독과점)")
        
        # 4. 기술 거부감 (노인, 보수 산업)
        if context.get('tech_resistance', False):
            factor = 0.3  # 70% 거부
            will_value *= factor
            adjustments.append({
                'bias': 'tech_resistance',
                'factor': factor,
                'reason': '기술 거부감 (노인층, 보수 산업)',
                'impact': f'{(1-factor)*100:.0f}% 감소'
            })
            self.logger.info(f"    - 기술 거부감: ×{factor} (채택 장벽)")
        
        # 5. 가격 부담 (고가 제품)
        if context.get('high_price', False):
            factor = 0.6  # 40% 구매 주저
            will_value *= factor
            adjustments.append({
                'bias': 'price_burden',
                'factor': factor,
                'reason': '가격 부담 (고가 제품)',
                'impact': f'{(1-factor)*100:.0f}% 감소'
            })
            self.logger.info(f"    - 가격 부담: ×{factor} (구매 주저)")
        
        will = {
            'value': will_value,
            'rationale': '현실적 예측 (행동경제학 편향 반영)',
            'adjustments': adjustments,
            'use_case': '실제 채택률, 매출 예측, 현실 전망'
        }
        
        self.logger.info(f"  Will: {will['value']:,.0f} (현실)")
        
        # ===== Gap 분석 =====
        
        gap_absolute = should['value'] - will['value']
        gap_relative = gap_absolute / should['value'] if should['value'] > 0 else 0
        
        gap = {
            'absolute': gap_absolute,
            'relative': gap_relative,
            'percentage': gap_relative * 100,
            'main_drivers': [adj['bias'] for adj in adjustments],
            'interpretation': self._interpret_gap(gap_relative)
        }
        
        self.logger.info(f"  Gap: {gap['percentage']:.1f}% ({gap['interpretation']})")
        
        return {
            'should': should,
            'will': will,
            'gap': gap,
            'signal': 's4_behavioral_econ',
            'weight': self.weight
        }
    
    def _interpret_gap(self, gap_relative: float) -> str:
        """Gap 해석"""
        if gap_relative < 0.1:
            return "작은 차이 (< 10%)"
        elif gap_relative < 0.3:
            return "중간 차이 (10-30%)"
        elif gap_relative < 0.5:
            return "큰 차이 (30-50%)"
        else:
            return "매우 큰 차이 (> 50%)"


# (나머지 Signal 클래스들은 다음 단계에서 추가)


# ========================================
# Domain Reasoner 엔진
# ========================================

class DomainReasonerEngine:
    """
    10-Signal Stack 기반 정밀 추론 엔진
    
    파이프라인:
    1. 정의 고정 (s10)
    2. 제약 확인 (s3, s8)
    3. 구조 분해
    4. RAG 검색 (s2, s9, s10)
    5. 융합 (우선순위 적용)
    6. 행동경제학 보정 (s4)
    7. 검증
    8. 리포트 생성
    """
    
    def __init__(self):
        """초기화"""
        logger.info("=" * 60)
        logger.info("Domain-Centric Reasoner 엔진 초기화")
        logger.info("=" * 60)
        
        # 방법론 로드
        self.methodology = self._load_methodology()
        
        # 10가지 신호 초기화
        self.signals = self._initialize_signals()
        
        logger.info("✅ Domain Reasoner 준비 완료")
        logger.info("  • 10가지 신호 스택 로드")
        logger.info("  • 우선순위: s3 → s8 → s6 → s10 → s2 → s9 → s7 → s5 → s4 → s1")
    
    def _load_methodology(self) -> Dict:
        """방법론 YAML 로드"""
        yaml_path = Path("data/raw/umis_domain_reasoner_methodology.yaml")
        
        if not yaml_path.exists():
            logger.warning(f"방법론 파일 없음: {yaml_path}")
            return {}
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_signals(self) -> Dict:
        """10가지 신호 초기화"""
        return {
            's1_llm_guess': Signal1_LLMGuess(weight=0.15),
            's2_rag_consensus': Signal2_RAGConsensus(weight=0.9),
            's3_laws_ethics_physics': Signal3_Laws(weight=1.0),
            's4_behavioral_econ': Signal4_BehavioralEcon(weight=0.6),
            # s5-s10은 다음 단계에서 추가
        }
    
    def execute(
        self,
        question: str,
        domain: str,
        geography: str = 'KR',
        time_horizon: str = '2025-2030',
        phase_1_context: Optional[Dict] = None
    ) -> DomainReasonerResult:
        """
        6단계 파이프라인 실행
        
        Args:
            question: 추정 질문
            domain: 산업/영역
            geography: 지리 (기본 'KR')
            time_horizon: 시간 범위
            phase_1_context: Phase 1 (Guestimation) 결과 (선택)
        
        Returns:
            DomainReasonerResult
        """
        logger.info("\n" + "=" * 60)
        logger.info(f"Domain Reasoner 실행: {question}")
        logger.info("=" * 60)
        logger.info(f"  도메인: {domain}")
        logger.info(f"  지리: {geography}")
        logger.info(f"  시간: {time_horizon}")
        
        # Step 1: 정의 고정 (s10)
        logger.info("\n[Step 1] 정의 고정 (s10)")
        definition = self._clarify_definition(question, domain)
        
        # Step 2: 제약 확인 (s3, s8)
        logger.info("\n[Step 2] 제약 확인 (s3, s8)")
        constraints = self._check_constraints(definition)
        
        # Step 3: 구조 분해
        logger.info("\n[Step 3] 구조 분해")
        structure = self._decompose_structure(definition)
        
        # Step 4: RAG 검색 (s2, s9, s10)
        logger.info("\n[Step 4] RAG 검색 (s2, s9, s10)")
        rag_results = self._retrieve_from_rag(definition, domain, geography)
        
        # Step 5: 융합 (우선순위 적용)
        logger.info("\n[Step 5] 신호 융합")
        fused_result = self._fuse_signals(rag_results, constraints, structure)
        
        # Step 6: 행동경제학 보정 (Should vs Will)
        logger.info("\n[Step 6] Should vs Will 분석")
        final_result = self._adjust_should_vs_will(fused_result)
        
        # Step 7: 검증
        logger.info("\n[Step 7] 검증")
        verification = self._verify(final_result, constraints, definition)
        
        # Step 8: 리포트 생성
        logger.info("\n[Step 8] 리포트 생성")
        report = self._generate_report(
            definition,
            final_result,
            verification,
            rag_results
        )
        
        logger.info("\n✅ Domain Reasoner 완료")
        
        return report
    
    # ========================================
    # 파이프라인 메서드들 (Stub - 다음 단계에서 구현)
    # ========================================
    
    def _clarify_definition(self, question: str, domain: str) -> Dict:
        """Step 1: 정의 고정"""
        # TODO: s10 (Industry KPI Library) 활용
        return {
            'question': question,
            'domain': domain,
            'kpi_id': 'KPI_TBD',
            'definition': 'TBD'
        }
    
    def _check_constraints(self, definition: Dict) -> Dict:
        """Step 2: 제약 확인"""
        # TODO: s3 (Laws), s8 (Time/Space Bounds)
        return {
            'laws': {},
            'bounds': {}
        }
    
    def _decompose_structure(self, definition: Dict) -> Dict:
        """Step 3: 구조 분해"""
        # TODO: 도메인 모형 생성
        return {
            'model': 'TBD',
            'components': []
        }
    
    def _retrieve_from_rag(
        self,
        definition: Dict,
        domain: str,
        geography: str
    ) -> Dict:
        """Step 4: RAG 검색"""
        # TODO: s2 (RAG Consensus), s9 (Case Analogies), s10 (KPI)
        return {
            's2_consensus': {},
            's9_cases': [],
            's10_definitions': {}
        }
    
    def _fuse_signals(
        self,
        rag_results: Dict,
        constraints: Dict,
        structure: Dict
    ) -> Dict:
        """Step 5: 신호 융합"""
        # TODO: 가중 평균, IQR, trimmed mean
        return {
            'value': 0,
            'range': (0, 0),
            'signals_used': []
        }
    
    def _adjust_should_vs_will(self, fused_result: Dict) -> Dict:
        """Step 6: Should vs Will 분리"""
        # TODO: s4 (Behavioral Econ) 활용
        return {
            'should': {},
            'will': {},
            'gap': {}
        }
    
    def _verify(
        self,
        final_result: Dict,
        constraints: Dict,
        definition: Dict
    ) -> Dict:
        """Step 7: 검증"""
        # TODO: 체크리스트 검증
        return {
            'dimensional_consistency': True,
            'regulatory_compliance': True,
            'case_consensus': True,
            'should_will_separated': True
        }
    
    def _generate_report(
        self,
        definition: Dict,
        final_result: Dict,
        verification: Dict,
        rag_results: Dict
    ) -> DomainReasonerResult:
        """Step 8: 리포트 생성"""
        # TODO: 7개 섹션 리포트
        
        return DomainReasonerResult(
            point_estimate=0,
            range_estimate=(0, 0),
            should_vs_will={},
            signal_breakdown={},
            evidence_table=[],
            verification_log=verification,
            residual_unknowns=[],
            confidence='Medium',
            next_actions=[]
        )


# ========================================
# 예시 사용
# ========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Domain-Centric Reasoner 엔진 테스트")
    print("=" * 60)
    
    engine = DomainReasonerEngine()
    
    # 테스트 실행
    result = engine.execute(
        question="국내 음식 배달 플랫폼 평균 수수료율",
        domain="platform",
        geography="KR"
    )
    
    print(f"\n점추정: {result.point_estimate}")
    print(f"범위: {result.range_estimate}")
    print(f"신뢰도: {result.confidence}")
    
    print("\n✅ 엔진 초기화 완료")
