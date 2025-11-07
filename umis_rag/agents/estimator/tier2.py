"""
Tier 2: Judgment Path

맥락 파악 → 증거 수집 → 평가 → 종합 판단
"""

from typing import Optional, List, Dict, Any
import time

from umis_rag.utils.logger import logger
from .models import (
    Context, EstimationResult, Tier2Config, Intent,
    ComponentEstimation, DecompositionTrace
)
from .source_collector import SourceCollector
from .judgment import JudgmentSynthesizer
from .learning_writer import LearningWriter


class Tier2JudgmentPath:
    """
    Tier 2: Judgment Path
    
    역할:
    -----
    - 맥락 파악 (LLM)
    - 모든 Source 수집
    - 증거 평가
    - 종합 판단
    - 학습 (Tier 1 편입)
    
    원칙:
    -----
    - 정확도 > 속도
    - 모든 정보 활용
    - 맥락 고려
    """
    
    def __init__(
        self,
        config: Optional[Tier2Config] = None,
        llm_mode: str = "native",
        learning_writer: Optional[LearningWriter] = None
    ):
        """
        초기화
        
        Args:
            config: Tier 2 설정
            llm_mode: LLM 모드
            learning_writer: 학습 Writer (옵션)
        """
        self.config = config or Tier2Config()
        self.llm_mode = llm_mode
        self.learning_writer = learning_writer
        
        logger.info("[Tier 2] Judgment Path 초기화")
        
        # Source Collector
        self.source_collector = SourceCollector(llm_mode=llm_mode)
        
        # Judgment Synthesizer
        self.synthesizer = JudgmentSynthesizer()
        
        logger.info(f"  ✅ Tier 2 준비 완료")
        
        if self.learning_writer:
            logger.info(f"  ✅ Learning Writer 연결됨")
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        Tier 2 추정
        
        Args:
            question: 질문
            context: 맥락 (Tier 1에서 전달 or 생성)
        
        Returns:
            EstimationResult or None
        """
        logger.info(f"[Tier 2] 시작: {question}")
        start_time = time.time()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: 맥락 파악 (없으면 생성)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if not context:
            context = self._analyze_context(question)
        
        logger.info(f"  맥락: intent={context.intent.value}, domain={context.domain}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: Source 수집
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        sources = self.source_collector.collect_all(
            question,
            context,
            mode=self.config.collection_mode
        )
        
        boundaries = sources['boundaries']
        soft_guides = sources['soft_guides']
        value_estimates = sources['value_estimates']
        
        logger.info(f"  수집: Physical {len(boundaries)}, Soft {len(soft_guides)}, Value {len(value_estimates)}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: 충돌 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        conflicts = self._check_conflicts(boundaries, value_estimates)
        
        if conflicts:
            logger.warning(f"  ⚠️  충돌 {len(conflicts)}개 발견")
            # TODO: 충돌 해결
            # 현재는 경고만
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: 증거 평가 (간단히)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TODO: 맥락 기반 평가
        # 현재는 스킵
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 5: 종합 판단
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        judgment = self.synthesizer.synthesize(
            value_estimates,
            context,
            soft_guides
        )
        
        if not judgment['value']:
            logger.warning("  판단 실패")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 6: 결과 생성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elapsed = time.time() - start_time
        
        result = EstimationResult(
            question=question,
            tier=2,
            
            value=judgment['value'],
            value_range=judgment.get('range'),
            
            confidence=judgment['confidence'],
            uncertainty=judgment.get('uncertainty', 0.3),
            
            context=context,
            
            boundaries=boundaries,
            soft_guides=soft_guides,
            value_estimates=value_estimates,
            
            judgment_strategy=judgment['strategy'],
            reasoning=judgment['reasoning'],
            
            conflicts_detected=conflicts,
            conflicts_resolved=(len(conflicts) == 0),
            
            execution_time=elapsed,
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # v7.3.2: 추정 근거 및 추적
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            reasoning_detail=self._create_reasoning_detail(
                judgment, value_estimates, context
            ),
            
            component_estimations=self._create_component_estimations(
                value_estimates
            ),
            
            estimation_trace=self._build_estimation_trace(
                value_estimates, judgment
            ),
            
            decomposition=None  # Tier 3에서 구현
        )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 7: 학습 판단 및 실행
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result.should_learn = self._should_learn(result)
        
        if result.should_learn and self.learning_writer:
            try:
                rule_id = self.learning_writer.save_learned_rule(
                    question=question,
                    result=result,
                    context=context
                )
                logger.info(f"  📚 학습 완료: {rule_id}")
            except Exception as e:
                logger.error(f"  ❌ 학습 실패: {e}")
        
        logger.info(f"  ✅ 완료: {result.value:,.0f} (신뢰도 {result.confidence:.0%}, {elapsed:.2f}초)")
        
        return result
    
    def _analyze_context(self, question: str) -> Context:
        """
        맥락 파악
        
        TODO: LLM 활용
        현재는 간단한 규칙
        """
        # 간단한 규칙 기반
        intent = Intent.GET_VALUE
        
        if any(word in question for word in ['창업', '고려', '시작']):
            intent = Intent.MAKE_DECISION
        elif any(word in question for word in ['분석', '이해']):
            intent = Intent.UNDERSTAND_MARKET
        
        # 도메인 추정
        domain = "General"
        if 'saas' in question.lower() or '구독' in question:
            domain = "B2B_SaaS"
        elif '음식점' in question or '카페' in question or '식당' in question:
            domain = "Food_Service"
        
        # 지역
        region = None
        if '한국' in question or '국내' in question:
            region = "한국"
        elif '서울' in question:
            region = "서울"
        
        return Context(
            intent=intent,
            domain=domain,
            region=region,
            time_period="2024"  # 기본값
        )
    
    def _check_conflicts(
        self,
        boundaries: List,
        value_estimates: List
    ) -> List[Dict]:
        """충돌 체크"""
        
        conflicts = []
        
        # Physical boundary 위반 체크
        for boundary in boundaries:
            for estimate in value_estimates:
                if boundary.min_value and estimate.value < boundary.min_value:
                    conflicts.append({
                        'type': 'boundary_violation',
                        'boundary': boundary,
                        'estimate': estimate,
                        'reason': f"값 {estimate.value} < 최소 {boundary.min_value}"
                    })
                
                if boundary.max_value and estimate.value > boundary.max_value:
                    conflicts.append({
                        'type': 'boundary_violation',
                        'boundary': boundary,
                        'estimate': estimate,
                        'reason': f"값 {estimate.value} > 최대 {boundary.max_value}"
                    })
        
        return conflicts
    
    def _should_learn(self, result: EstimationResult) -> bool:
        """
        학습 가치 판단 (Confidence 기반 유연화)
        
        조건:
        1. confidence >= 0.80
        2. evidence_count:
           - confidence >= 0.90: 1개 OK
           - confidence >= 0.80: 2개 필요
        3. 충돌 해결
        """
        
        # Confidence 체크
        if result.confidence < 0.80:
            return False
        
        # Evidence 개수 체크 (Confidence 기반 유연화)
        if result.confidence >= 0.90:
            min_evidence = 1  # 매우 높은 신뢰도
        else:
            min_evidence = 2  # 일반
        
        if len(result.value_estimates) < min_evidence:
            return False
        
        # 충돌 해결 여부
        if result.conflicts_detected and not result.conflicts_resolved:
            return False
        
        # 학습 가치 있음
        return True
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # v7.3.2: 추정 근거 생성 메서드들
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _create_reasoning_detail(
        self,
        judgment: Dict,
        value_estimates: List,
        context: Context
    ) -> Dict[str, Any]:
        """
        상세 근거 생성
        
        Returns:
            {
                'method': 'weighted_average',
                'sources_used': ['statistical', 'rag'],
                'evidence_count': 3,
                'why_this_method': '...',
                'evidence_breakdown': [...]
            }
        """
        return {
            'method': judgment['strategy'],
            'sources_used': [est.source_type.value for est in value_estimates],
            'evidence_count': len(value_estimates),
            'why_this_method': self._explain_strategy(judgment['strategy']),
            
            # 각 증거의 상세
            'evidence_breakdown': [
                {
                    'source': est.source_type.value,
                    'value': est.value,
                    'confidence': est.confidence,
                    'reasoning': est.reasoning,
                    'source_detail': est.source_detail
                }
                for est in value_estimates
            ],
            
            # 판단 과정
            'judgment_process': [
                f"1. 맥락 파악: domain={context.domain}, region={context.region}",
                f"2. {len(value_estimates)}개 증거 수집 완료",
                f"3. 전략 선택: {judgment['strategy']}",
                f"4. 계산: {judgment['reasoning']}",
                f"5. 신뢰도: {judgment['confidence']:.0%}"
            ],
            
            # 맥락 정보
            'context_info': {
                'domain': context.domain,
                'region': context.region,
                'time_period': context.time_period
            }
        }
    
    def _explain_strategy(self, strategy: str) -> str:
        """
        전략 선택 이유 설명
        
        사용자가 이해할 수 있도록 명확히
        """
        explanations = {
            'weighted_average': '증거들의 신뢰도가 비슷하여 가중 평균 적용',
            'conservative': '의사결정용이므로 보수적 하한 선택',
            'range': '증거 분산이 커서 범위로 제시',
            'single_best': '하나의 증거가 압도적으로 신뢰도 높음'
        }
        return explanations.get(strategy, f'전략: {strategy}')
    
    def _create_component_estimations(
        self,
        value_estimates: List
    ) -> List[ComponentEstimation]:
        """
        개별 요소 추정 논리 생성
        
        각 증거(Source)를 ComponentEstimation으로 변환
        """
        components = []
        
        for est in value_estimates:
            component = ComponentEstimation(
                component_name=est.source_type.value,
                component_value=est.value,
                estimation_method=est.source_type.value,
                reasoning=est.reasoning,
                confidence=est.confidence,
                sources=[est.source_detail] if est.source_detail else [],
                raw_data=est.raw_data
            )
            components.append(component)
        
        return components
    
    def _build_estimation_trace(
        self,
        value_estimates: List,
        judgment: Dict
    ) -> List[str]:
        """
        추정 과정 추적 (스텝별 기록)
        
        Returns:
            ['맥락 파악 완료', '증거 수집 완료', ...]
        """
        trace = []
        
        trace.append("Step 1: 맥락 파악 완료")
        trace.append(f"Step 2: {len(value_estimates)}개 Source 수집 완료")
        
        for i, est in enumerate(value_estimates, 1):
            trace.append(
                f"  증거 {i}: {est.source_type.value} = {est.value} "
                f"(신뢰도 {est.confidence:.0%})"
            )
        
        trace.append(f"Step 3: 전략 선택 - {judgment['strategy']}")
        trace.append(f"Step 4: 종합 판단 완료 - {judgment['value']} (신뢰도 {judgment['confidence']:.0%})")
        
        return trace

