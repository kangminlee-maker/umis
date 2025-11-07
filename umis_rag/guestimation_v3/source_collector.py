"""
Source Collector

11개 Source를 수집하고 통합
"""

from typing import List, Dict, Optional, Any
import concurrent.futures
import time

from umis_rag.utils.logger import logger
from .models import (
    Context,
    Boundary,
    SoftGuide,
    ValueEstimate,
    SourceOutput,
    SourceCategory
)

from .sources.physical import (
    SpacetimeConstraintSource,
    ConservationLawSource,
    MathematicalDefinitionSource
)

from .sources.soft import (
    LegalNormSource,
    StatisticalPatternSource,
    BehavioralInsightSource
)

from .sources.value import (
    DefiniteDataSource,
    LLMEstimationSource,
    WebSearchSource,
    RAGBenchmarkSource,
    StatisticalValueSource
)


class SourceCollector:
    """
    Source 수집기
    
    역할:
    -----
    - 11개 Source 통합 관리
    - 맥락 기반 선택적 수집
    - 병렬 수집 지원
    
    사용:
    ----
    collector = SourceCollector()
    result = collector.collect_all(question, context)
    """
    
    def __init__(self, llm_mode: str = "native"):
        """
        초기화
        
        Args:
            llm_mode: LLM 모드 ("native" | "external" | "skip")
        """
        logger.info("[Source Collector] 초기화")
        
        # Physical (3개)
        self.spacetime = SpacetimeConstraintSource()
        self.conservation = ConservationLawSource()
        self.mathematical = MathematicalDefinitionSource()
        
        # Soft (3개)
        self.legal = LegalNormSource()
        self.statistical_pattern = StatisticalPatternSource()
        self.behavioral = BehavioralInsightSource()
        
        # Value (5개)
        self.definite_data = DefiniteDataSource()
        self.llm = LLMEstimationSource(llm_mode)
        self.web = WebSearchSource()
        self.rag = RAGBenchmarkSource()
        self.statistical_value = StatisticalValueSource()
        
        logger.info(f"  ✅ 11개 Source 준비 완료")
    
    def collect_all(
        self,
        question: str,
        context: Optional[Context] = None,
        mode: str = "parallel"
    ) -> Dict[str, Any]:
        """
        모든 Source 수집
        
        Args:
            question: 질문
            context: 맥락
            mode: "parallel" or "sequential"
        
        Returns:
            {
                'boundaries': List[Boundary],
                'soft_guides': List[SoftGuide],
                'value_estimates': List[ValueEstimate]
            }
        """
        logger.info(f"[Source Collector] 수집 시작: {question}")
        start_time = time.time()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: Physical Constraints (항상, 빠름)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        boundaries = self._collect_physical(question, context)
        logger.info(f"  Physical: {len(boundaries)}개 제약")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: Value Sources (병렬 or 순차)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if mode == "parallel":
            value_estimates = self._collect_values_parallel(question, context)
        else:
            value_estimates = self._collect_values_sequential(question, context)
        
        logger.info(f"  Value: {len(value_estimates)}개 추정")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: Soft Constraints (선택적)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        soft_guides = self._collect_soft(question, context)
        logger.info(f"  Soft: {len(soft_guides)}개 가이드")
        
        elapsed = time.time() - start_time
        logger.info(f"  ✅ 수집 완료 ({elapsed:.2f}초)")
        
        return {
            'boundaries': boundaries,
            'soft_guides': soft_guides,
            'value_estimates': value_estimates,
            'execution_time': elapsed
        }
    
    def _collect_physical(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[Boundary]:
        """Physical Constraints 수집 (모두)"""
        
        boundaries = []
        
        # 시공간
        boundaries.extend(self.spacetime.collect(question, context))
        
        # 보존
        boundaries.extend(self.conservation.collect(question, context))
        
        # 수학
        boundaries.extend(self.mathematical.collect(question, context))
        
        return boundaries
    
    def _collect_soft(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[SoftGuide]:
        """Soft Constraints 수집 (선택적)"""
        
        guides = []
        
        # 법률 (항상)
        guides.extend(self.legal.collect(question, context))
        
        # 통계 패턴 (항상)
        guides.extend(self.statistical_pattern.collect(question, context))
        
        # 행동경제학 (선택적)
        # TODO: 맥락 기반 선택
        guides.extend(self.behavioral.collect(question, context))
        
        return guides
    
    def _collect_values_sequential(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[ValueEstimate]:
        """Value Sources 순차 수집"""
        
        estimates = []
        
        # 1. 확정 데이터 (항상)
        estimates.extend(self.definite_data.collect(question, context))
        
        # 2. LLM (간단한 질문)
        estimates.extend(self.llm.collect(question, context))
        
        # 3. 웹 검색 (TODO)
        estimates.extend(self.web.collect(question, context))
        
        # 4. RAG 벤치마크
        estimates.extend(self.rag.collect(question, context))
        
        # 5. 통계값 (다른 것 없을 때만) ⭐
        if len(estimates) == 0:
            # Soft Guides 먼저 수집
            soft_guides = self._collect_soft(question, context)
            
            # 통계에서 값 추출
            for soft_guide in soft_guides:
                if soft_guide.distribution:
                    stat_values = self.statistical_value.collect(
                        question, context, soft_guide
                    )
                    estimates.extend(stat_values)
                    
                    if stat_values:
                        logger.info(f"  통계값 활성화: {len(stat_values)}개")
        
        return estimates
    
    def _collect_values_parallel(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[ValueEstimate]:
        """Value Sources 병렬 수집"""
        
        # TODO: ThreadPoolExecutor로 병렬화
        # 현재는 순차로
        return self._collect_values_sequential(question, context)

