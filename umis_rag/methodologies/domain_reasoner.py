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
    """s1: LLM Guess (0.15) - 낮은 가중치"""
    
    def __init__(self, weight=0.15):
        super().__init__(weight)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """
        LLM 기반 초안 생성 (빠른 범위 설정)
        
        실제로는 LLM에게 직접 질문하여 초안을 얻지만,
        여기서는 간단한 휴리스틱으로 대체
        """
        
        query = context.get('query', definition.get('question', ''))
        
        self.logger.info(f"\n[s1 LLM Guess] 초안 생성")
        self.logger.info(f"  Query: {query}")
        
        # 간단한 fallback 값 (실제로는 LLM 호출)
        # 이것은 Stub - 실제 프로젝트에서는 OpenAI API 호출
        
        return SignalResult(
            signal_name='s1_llm_guess',
            weight=self.weight,
            value=None,  # LLM 호출 필요
            confidence=0.15,  # 낮은 신뢰도
            evidence=[{
                'src_id': 'LLM_GUESS',
                'source': 'GPT-4 Common Knowledge',
                'content': 'LLM 일반 지식 기반 추정 (검증 필요)',
                'type': 'llm_knowledge'
            }],
            umis_mapping='Guestimation 출처 2 (LLM 직접)'
        )


class Signal2_RAGConsensus(BaseSignal):
    """s2: RAG Consensus (0.9) - 핵심!"""
    
    def __init__(self, weight=0.9):
        super().__init__(weight)
        
        # UMIS RAG Agents 초기화
        try:
            from umis_rag.agents.explorer import ExplorerRAG
            from umis_rag.agents.quantifier import QuantifierRAG
            from umis_rag.agents.validator import ValidatorRAG
            
            self.explorer_rag = ExplorerRAG()
            self.quantifier_rag = QuantifierRAG()
            self.validator_rag = ValidatorRAG()
            
            self.logger.info("  ✅ UMIS RAG Agents 초기화 완료")
        except Exception as e:
            self.logger.warning(f"  ⚠️ UMIS RAG Agents 초기화 실패: {e}")
            self.explorer_rag = None
            self.quantifier_rag = None
            self.validator_rag = None
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """
        RAG에서 합의 범위 추출 (독립 출처 ≥2)
        
        Args:
            definition: KPI 정의
            context: {
                'domain': str (산업),
                'geography': str (지리),
                'query': str (원본 질문)
            }
        
        Returns:
            SignalResult with consensus range
        """
        
        query = context.get('query', definition.get('question', ''))
        domain = context.get('domain', 'general')
        
        self.logger.info(f"\n[s2 RAG Consensus] 검색 시작")
        self.logger.info(f"  Query: {query}")
        self.logger.info(f"  Domain: {domain}")
        
        # 결과 저장
        all_results = []
        sources = []
        
        # ===== 1. Explorer RAG 검색 (패턴 기반) =====
        if self.explorer_rag:
            try:
                explorer_results = self.explorer_rag.search_patterns(query, top_k=5)
                
                if explorer_results:
                    self.logger.info(f"  ✅ Explorer RAG: {len(explorer_results)}개 패턴 발견")
                    
                    for doc, score in explorer_results:
                        all_results.append({
                            'source': 'explorer_knowledge_base',
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'similarity': score,
                            'source_type': 'pattern'
                        })
                        sources.append('UMIS Explorer RAG')
            except Exception as e:
                self.logger.warning(f"  ⚠️ Explorer RAG 검색 실패: {e}")
        
        # ===== 2. Quantifier RAG 검색 (벤치마크) =====
        if self.quantifier_rag:
            try:
                # 방법론 검색
                methodology_results = self.quantifier_rag.search_methodology(query, top_k=3)
                
                if methodology_results:
                    self.logger.info(f"  ✅ Quantifier 방법론: {len(methodology_results)}개")
                    
                    for doc, score in methodology_results:
                        all_results.append({
                            'source': 'calculation_methodologies',
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'similarity': score,
                            'source_type': 'methodology'
                        })
                        sources.append('UMIS Quantifier Methodology')
                
                # 벤치마크 검색
                benchmark_results = self.quantifier_rag.search_benchmark(query, top_k=5)
                
                if benchmark_results:
                    self.logger.info(f"  ✅ Quantifier 벤치마크: {len(benchmark_results)}개")
                    
                    for doc, score in benchmark_results:
                        all_results.append({
                            'source': 'market_benchmarks',
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'similarity': score,
                            'source_type': 'benchmark'
                        })
                        sources.append('UMIS Market Benchmarks')
            except Exception as e:
                self.logger.warning(f"  ⚠️ Quantifier RAG 검색 실패: {e}")
        
        # ===== 3. Validator RAG 검색 (정의) =====
        if self.validator_rag:
            try:
                definition_results = self.validator_rag.search_definition_case(query, top_k=3)
                
                if definition_results:
                    self.logger.info(f"  ✅ Validator 정의: {len(definition_results)}개")
                    
                    for doc, score in definition_results:
                        all_results.append({
                            'source': 'definition_validation_cases',
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'similarity': score,
                            'source_type': 'definition'
                        })
                        sources.append('UMIS Validator Definitions')
            except Exception as e:
                self.logger.warning(f"  ⚠️ Validator RAG 검색 실패: {e}")
        
        # ===== 4. 독립성 확인 =====
        unique_sources = list(set(sources))
        is_independent = len(unique_sources) >= 2
        
        self.logger.info(f"\n  독립 출처: {len(unique_sources)}개")
        for src in unique_sources:
            self.logger.info(f"    - {src}")
        
        if not is_independent:
            self.logger.warning(f"  ⚠️ 독립 출처 부족 (< 2개)")
        
        # ===== 5. 합의 범위 추출 =====
        consensus = self._extract_consensus(all_results, context)
        
        # ===== 6. 증거 생성 =====
        evidence = [
            {
                'src_id': f"SRC_{idx+1:03d}",
                'source': result['source'],
                'content': result['content'][:200] + '...',
                'similarity': result['similarity'],
                'type': result['source_type']
            }
            for idx, result in enumerate(all_results[:5])  # Top 5
        ]
        
        self.logger.info(f"\n  합의 범위: {consensus.get('range', 'N/A')}")
        self.logger.info(f"  신뢰도: {consensus.get('confidence', 0):.2f}")
        
        return SignalResult(
            signal_name='s2_rag_consensus',
            weight=self.weight,
            value=consensus.get('value'),
            confidence=consensus.get('confidence', 0),
            evidence=evidence,
            umis_mapping='Explorer/Quantifier/Validator RAG'
        )
    
    def _extract_consensus(self, results: List[Dict], context: Dict) -> Dict:
        """
        합의 범위 추출 (IQR, trimmed mean)
        
        Args:
            results: RAG 검색 결과
            context: 맥락
        
        Returns:
            {
                'value': float (중간값),
                'range': tuple (하한, 상한),
                'confidence': float (0-1),
                'method': str (추출 방법)
            }
        """
        
        if not results:
            return {
                'value': None,
                'range': (None, None),
                'confidence': 0,
                'method': 'no_data'
            }
        
        # 수치 값 추출 (메타데이터 또는 content 파싱)
        values = []
        
        for result in results:
            # 메타데이터에서 값 추출 시도
            metadata = result.get('metadata', {})
            
            # benchmark_value, typical_range 등 찾기
            if 'value' in metadata:
                values.append(self._parse_value(metadata['value']))
            elif 'typical_range' in metadata:
                range_val = metadata['typical_range']
                if '-' in str(range_val):
                    # "6-12%" 형식
                    parts = str(range_val).replace('%', '').split('-')
                    if len(parts) == 2:
                        try:
                            low = float(parts[0])
                            high = float(parts[1])
                            values.append((low + high) / 2)  # 중간값
                        except:
                            pass
        
        if not values:
            return {
                'value': None,
                'range': (None, None),
                'confidence': 0.3,  # 낮은 신뢰도
                'method': 'no_numeric_data'
            }
        
        # IQR & Trimmed Mean
        import statistics
        
        if len(values) == 1:
            value = values[0]
            range_tuple = (value * 0.8, value * 1.2)  # ±20%
            confidence = 0.5
        elif len(values) == 2:
            value = statistics.mean(values)
            range_tuple = (min(values), max(values))
            confidence = 0.7
        else:
            # 3개 이상 → IQR
            sorted_values = sorted(values)
            
            # 이상치 제거 (간단 버전: 상하 10% 제거)
            trim_count = max(1, len(sorted_values) // 10)
            trimmed = sorted_values[trim_count:-trim_count] if len(sorted_values) > 4 else sorted_values
            
            value = statistics.mean(trimmed)
            q1 = statistics.quantiles(trimmed, n=4)[0] if len(trimmed) > 2 else min(trimmed)
            q3 = statistics.quantiles(trimmed, n=4)[2] if len(trimmed) > 2 else max(trimmed)
            
            range_tuple = (q1, q3)
            confidence = min(0.9, 0.5 + len(values) * 0.1)  # 데이터 많을수록 신뢰↑
        
        return {
            'value': value,
            'range': range_tuple,
            'confidence': confidence,
            'method': 'iqr_trimmed_mean',
            'sample_size': len(values)
        }
    
    def _parse_value(self, value_str: Any) -> Optional[float]:
        """문자열 값을 float로 변환"""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        if isinstance(value_str, str):
            # "8.5%" → 0.085
            if '%' in value_str:
                try:
                    return float(value_str.replace('%', '').strip()) / 100
                except:
                    pass
            
            # "1,000억" → 100_000_000_000
            if '억' in value_str:
                try:
                    num = value_str.replace('억', '').replace(',', '').strip()
                    return float(num) * 100_000_000
                except:
                    pass
            
            # 일반 숫자
            try:
                return float(value_str.replace(',', ''))
            except:
                pass
        
        return None


class Signal3_Laws(BaseSignal):
    """s3: Laws/Ethics/Physics (1.0) - 최우선!"""
    
    def __init__(self, weight=1.0):
        super().__init__(weight)
        
    def check(self, definition: Dict) -> Dict[str, Any]:
        """
        법/윤리/물리 제약 확인
        
        Returns:
            {
                'regulatory': [...],  # 규제 제약
                'physical': [...],    # 물리 제약
                'ethical': [...],     # 윤리 이슈
                'bounds': {           # 상한/하한
                    'lower': float,
                    'upper': float
                }
            }
        """
        
        # Stub 구현 - 향후 도메인별 규제 DB 연동
        self.logger.info(f"\n[s3 Laws/Ethics/Physics] 제약 확인")
        
        domain = definition.get('domain', 'general')
        
        # 간단한 도메인별 제약
        constraints = {
            'regulatory': [],
            'physical': [],
            'ethical': [],
            'bounds': {'lower': 0, 'upper': float('inf')}
        }
        
        # 도메인별 규제 (간단 버전)
        if domain in ['healthcare', 'medical']:
            constraints['regulatory'].append('의료기기법')
            constraints['regulatory'].append('개인정보보호법')
            constraints['ethical'].append('의료 윤리')
        elif domain in ['finance', 'banking']:
            constraints['regulatory'].append('금융위원회 규제')
            constraints['regulatory'].append('자본시장법')
        elif domain == 'education':
            constraints['regulatory'].append('교육법')
        
        if constraints['regulatory']:
            self.logger.info(f"  ⚠️ 규제 확인 필요: {', '.join(constraints['regulatory'])}")
        
        return constraints


class Signal5_StatPatterns(BaseSignal):
    """s5: Statistical Patterns (0.75)"""
    
    def __init__(self, weight=0.75):
        super().__init__(weight)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """통계 패턴 적용 (80-20, S-Curve, Elasticity)"""
        
        self.logger.info(f"\n[s5 Stat Patterns] 통계 패턴 적용")
        
        # Stub - 통계 패턴 적용
        return SignalResult(
            signal_name='s5_stat_patterns',
            weight=self.weight,
            value=None,
            confidence=0.75,
            evidence=[],
            umis_mapping='Guestimation 출처 6 (통계 패턴)'
        )


class Signal6_MathRelations(BaseSignal):
    """s6: Math Relations (1.0) - 최우선!"""
    
    def __init__(self, weight=1.0):
        super().__init__(weight)
    
    def verify_dimensional_consistency(
        self,
        numerator_unit: str,
        denominator_unit: str,
        result_unit: str
    ) -> bool:
        """차원 분석 (단위 일관성 검증)"""
        
        self.logger.info(f"\n[s6 Math Relations] 차원 분석")
        self.logger.info(f"  분자: {numerator_unit}")
        self.logger.info(f"  분모: {denominator_unit}")
        self.logger.info(f"  결과: {result_unit}")
        
        # 간단한 검증 (향후 강화)
        # TODO: 실제 차원 분석 구현
        
        return True  # Stub


class Signal7_RulesOfThumb(BaseSignal):
    """s7: Rules of Thumb (0.7)"""
    
    def __init__(self, weight=0.7):
        super().__init__(weight)
    
    def process(self, definition: Dict, context: Dict) -> SignalResult:
        """산업별 Rule of Thumb 적용"""
        
        self.logger.info(f"\n[s7 Rules of Thumb] 산업 공식 적용")
        
        # Stub - UMIS RAG Rule of Thumb 활용
        return SignalResult(
            signal_name='s7_rules_of_thumb',
            weight=self.weight,
            value=None,
            confidence=0.7,
            evidence=[],
            umis_mapping='Guestimation 출처 7 (Rule of Thumb)'
        )


class Signal8_TimeSpaceBounds(BaseSignal):
    """s8: Time/Space Bounds (1.0) - 최우선!"""
    
    def __init__(self, weight=1.0):
        super().__init__(weight)
    
    def calculate_bounds(
        self,
        definition: Dict
    ) -> Dict:
        """
        시공간 제약 기반 상한/하한 계산
        
        Returns:
            {
                'time_bounds': {...},
                'space_bounds': {...},
                'capacity_limits': {...}
            }
        """
        
        self.logger.info(f"\n[s8 Time/Space Bounds] 시공간 제약")
        
        # Stub - 시공간 제약 분석
        return {
            'time_bounds': {
                'development_time': '3-5년',
                'market_entry': '1-2년'
            },
            'space_bounds': {
                'geographic_coverage': 'TBD'
            },
            'capacity_limits': {
                'production': 'TBD'
            }
        }


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


class Signal10_IndustryKPI(BaseSignal):
    """s10: Industry KPI Library (0.95) - RAG 중심!"""
    
    def __init__(self, weight=0.95):
        super().__init__(weight)
        
        # Rachel (Validator) RAG 초기화
        try:
            from umis_rag.agents.validator import ValidatorRAG
            
            self.validator_rag = ValidatorRAG()
            self.logger.info("  ✅ Validator RAG 초기화 완료")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Validator RAG 초기화 실패: {e}")
            self.validator_rag = None
    
    def clarify_definition(
        self,
        question: str,
        domain: str
    ) -> Dict:
        """
        KPI 정의 명확화 (Step 1: 정의 고정)
        
        Args:
            question: 추정 질문
            domain: 산업/영역
        
        Returns:
            {
                'kpi_id': str,
                'metric_name': str,
                'standard_definition': {...},
                'status': str,
                'comparability_score': float
            }
        """
        
        self.logger.info(f"\n[s10 Industry KPI] 정의 명확화")
        self.logger.info(f"  Question: {question}")
        self.logger.info(f"  Domain: {domain}")
        
        # 질문에서 메트릭 추출 (간단 파싱)
        metric_name = self._extract_metric_from_question(question)
        
        self.logger.info(f"  추출된 메트릭: {metric_name}")
        
        # Rachel의 KPI 검증 활용
        if self.validator_rag:
            try:
                kpi_result = self.validator_rag.validate_kpi_definition(
                    metric_name=metric_name,
                    provided_definition={}  # 표준 정의 조회만
                )
                
                if kpi_result['status'] in ['match', 'partial_match', 'not_found']:
                    self.logger.info(f"  ✅ KPI 정의: {kpi_result['status']}")
                    
                    if kpi_result['status'] != 'not_found':
                        self.logger.info(f"  KPI ID: {kpi_result.get('kpi_id', 'N/A')}")
                    
                    return {
                        'kpi_id': kpi_result.get('kpi_id', 'KPI_UNKNOWN'),
                        'metric_name': metric_name,
                        'standard_definition': kpi_result.get('standard_definition', {}),
                        'status': kpi_result['status'],
                        'comparability_score': kpi_result.get('comparability_score', 0),
                        'recommendation': kpi_result.get('recommendation', '')
                    }
            except Exception as e:
                self.logger.warning(f"  ⚠️ KPI 검증 실패: {e}")
        
        # Fallback: 기본 정의 생성
        return {
            'kpi_id': 'KPI_CUSTOM',
            'metric_name': metric_name,
            'standard_definition': {
                'question': question,
                'domain': domain
            },
            'status': 'custom',
            'comparability_score': 0.5
        }
    
    def _extract_metric_from_question(self, question: str) -> str:
        """질문에서 메트릭 이름 추출"""
        
        question_lower = question.lower()
        
        # 키워드 매칭
        if '수수료' in question or 'commission' in question_lower:
            return '플랫폼 수수료율'
        elif '해지' in question or 'churn' in question_lower:
            return '월간 해지율'
        elif 'ltv' in question_lower or '생애 가치' in question:
            return 'LTV'
        elif 'cac' in question_lower or '획득 비용' in question:
            return 'CAC'
        elif '시장 규모' in question or 'market size' in question_lower or 'sam' in question_lower:
            return '시장 규모'
        elif '전환율' in question or 'conversion' in question_lower:
            return '전환율'
        elif 'take rate' in question_lower:
            return 'Take Rate'
        elif 'gmv' in question_lower:
            return 'GMV'
        else:
            # 기본값: 질문 자체
            return question[:50]


class Signal9_CaseAnalogies(BaseSignal):
    """s9: Case Analogies (0.85) - RAG 중심!"""
    
    def __init__(self, weight=0.85):
        super().__init__(weight)
        
        # Explorer RAG 초기화 (success_case_library)
        try:
            from umis_rag.agents.explorer import ExplorerRAG
            
            self.explorer_rag = ExplorerRAG()
            self.logger.info("  ✅ Explorer RAG 초기화 (사례 검색)")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Explorer RAG 초기화 실패: {e}")
            self.explorer_rag = None
    
    def process(
        self,
        definition: Dict,
        context: Dict
    ) -> SignalResult:
        """
        유사 사례 전이 보정
        
        Args:
            definition: KPI 정의
            context: {
                'domain': str,
                'geography': str,
                'query': str
            }
        
        Returns:
            SignalResult with transferred estimate
        """
        
        query = context.get('query', '')
        domain = context.get('domain', 'general')
        target_geo = context.get('geography', 'KR')
        
        self.logger.info(f"\n[s9 Case Analogies] 유사 사례 검색")
        self.logger.info(f"  Query: {query}")
        self.logger.info(f"  Domain: {domain}")
        
        # Explorer RAG로 사례 검색
        cases = []
        
        if self.explorer_rag:
            try:
                # 패턴 검색으로 사례 찾기
                pattern_results = self.explorer_rag.search_patterns(query, top_k=5)
                
                if pattern_results:
                    self.logger.info(f"  ✅ 유사 패턴: {len(pattern_results)}개 발견")
                    
                    for doc, score in pattern_results:
                        # 메타데이터에서 사례 정보 추출
                        metadata = doc.metadata
                        
                        case_info = {
                            'pattern_id': metadata.get('pattern_id', 'unknown'),
                            'similarity': score,
                            'content': doc.page_content,
                            'metadata': metadata
                        }
                        
                        cases.append(case_info)
                        
                        self.logger.info(f"    - {case_info['pattern_id']} (유사도: {score:.3f})")
            
            except Exception as e:
                self.logger.warning(f"  ⚠️ 사례 검색 실패: {e}")
        
        # 전이 보정 (간단 버전)
        transferred_estimate = self._transfer_from_cases(cases, context)
        
        # 증거 생성
        evidence = [
            {
                'src_id': f"CASE_{idx+1:03d}",
                'source': f"UMIS Pattern: {case['pattern_id']}",
                'similarity': case['similarity'],
                'type': 'case_analogy',
                'content': case['content'][:200] + '...'
            }
            for idx, case in enumerate(cases[:3])  # Top 3
        ]
        
        return SignalResult(
            signal_name='s9_case_analogies',
            weight=self.weight,
            value=transferred_estimate.get('value'),
            confidence=transferred_estimate.get('confidence', 0.85),
            evidence=evidence,
            umis_mapping='UMIS Explorer RAG (success_case_library)'
        )
    
    def _transfer_from_cases(
        self,
        cases: List[Dict],
        context: Dict
    ) -> Dict:
        """
        사례에서 값 전이 보정
        
        조정 계수:
        - 인구 비율
        - 고령화율
        - GDP per capita
        - 시장 성숙도
        """
        
        if not cases:
            return {
                'value': None,
                'confidence': 0,
                'method': 'no_cases'
            }
        
        # Stub - 실제 전이 보정 로직
        # TODO: 6가지 특징 유사도 + 4가지 조정 계수
        
        self.logger.info(f"\n  전이 보정 (Stub):")
        self.logger.info(f"    유사 사례: {len(cases)}개")
        self.logger.info(f"    조정 계수: 인구, 고령화, GDP, 성숙도")
        
        return {
            'value': None,  # 전이 보정 값
            'confidence': 0.85,
            'method': 'case_transfer_stub',
            'cases_used': len(cases)
        }


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
        logger.info("  10가지 신호 스택 초기화 중...")
        
        signals = {
            's1_llm_guess': Signal1_LLMGuess(weight=0.15),
            's2_rag_consensus': Signal2_RAGConsensus(weight=0.9),
            's3_laws_ethics_physics': Signal3_Laws(weight=1.0),
            's4_behavioral_econ': Signal4_BehavioralEcon(weight=0.6),
            's5_stat_patterns': Signal5_StatPatterns(weight=0.75),
            's6_math_relations': Signal6_MathRelations(weight=1.0),
            's7_rules_of_thumb': Signal7_RulesOfThumb(weight=0.7),
            's8_time_space_bounds': Signal8_TimeSpaceBounds(weight=1.0),
            's9_case_analogies': Signal9_CaseAnalogies(weight=0.85),
            's10_industry_kpi': Signal10_IndustryKPI(weight=0.95),
        }
        
        logger.info(f"  ✅ 10개 신호 모두 초기화 완료!")
        logger.info(f"     우선순위: s3 → s8 → s6 → s10 → s2 → s9 → s7 → s5 → s4 → s1")
        logger.info(f"     완전 구현: s2, s4, s10")
        logger.info(f"     Stub 구현: s1, s3, s5, s6, s7, s8, s9")
        
        return signals
    
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
        """Step 1: 정의 고정 (s10 활용)"""
        
        # s10 (Industry KPI) 사용
        if 's10_industry_kpi' in self.signals:
            return self.signals['s10_industry_kpi'].clarify_definition(question, domain)
        else:
            # Fallback
            return {
            'question': question,
            'domain': domain,
                'kpi_id': 'KPI_UNKNOWN',
                'metric_name': question[:50]
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
