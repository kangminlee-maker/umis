"""
Tier 2: Judgment Path

맥락 파악 → 증거 수집 → 평가 → 종합 판단
"""

from typing import Optional, List, Dict
import time

from umis_rag.utils.logger import logger
from .models import Context, EstimationResult, Tier2Config, Intent
from .source_collector import SourceCollector
from .judgment import JudgmentSynthesizer


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
        llm_mode: str = "native"
    ):
        """
        초기화
        
        Args:
            config: Tier 2 설정
            llm_mode: LLM 모드
        """
        self.config = config or Tier2Config()
        self.llm_mode = llm_mode
        
        logger.info("[Tier 2] Judgment Path 초기화")
        
        # Source Collector
        self.source_collector = SourceCollector(llm_mode=llm_mode)
        
        # Judgment Synthesizer
        self.synthesizer = JudgmentSynthesizer()
        
        logger.info(f"  ✅ Tier 2 준비 완료")
    
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
            
            execution_time=elapsed
        )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 7: 학습 판단
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result.should_learn = self._should_learn(result)
        
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
        """학습 가치 판단"""
        
        # 기준
        if result.confidence < 0.80:
            return False
        
        if len(result.value_estimates) < 2:
            return False
        
        # 학습 가치 있음
        return True

