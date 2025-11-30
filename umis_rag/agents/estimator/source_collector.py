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
    UnifiedPhysicalConstraintSource,  # v7.8.0: 신규
    SpacetimeConstraintSource,  # deprecated
    ConservationLawSource,  # deprecated
    MathematicalDefinitionSource  # deprecated
)

from .sources.soft import (
    LegalNormSource,
    StatisticalPatternSource,
    BehavioralInsightSource
)

from .sources.value import (
    DefiniteDataSource,
    AIAugmentedEstimationSource,
    LLMEstimationSource,  # deprecated
    WebSearchSource,  # deprecated
    RAGBenchmarkSource,
    StatisticalValueSource
)


class SourceCollector:
    """
    Source 수집기 (v7.8.0 재설계)
    
    역할:
    -----
    - 핵심 Source 통합 관리
    - 맥락 기반 선택적 수집
    - 병렬 수집 지원
    
    v7.8.0 변경:
    -------------
    - 11개 → 10개 Source (LLM + Web 통합)
    - AIAugmentedEstimationSource 신규 추가
    
    사용:
    ----
    collector = SourceCollector()
    result = collector.collect_all(question, context)
    """
    
    def __init__(self, llm_mode: Optional[str] = None):
        """
        초기화 (v7.9.0)
        
        Args:
            llm_mode: LLM 모드 (None이면 settings에서 동적 읽기)
        """
        logger.info("[Source Collector] 초기화 (v7.8.0)")
        
        self._llm_mode = llm_mode  # None이면 Property에서 읽기
        
        # Physical (1개) ⭐ v7.8.0: 통합
        self.physical = UnifiedPhysicalConstraintSource()
        
        # Soft (3개)
        self.legal = LegalNormSource()
        self.statistical_pattern = StatisticalPatternSource()
        self.behavioral = BehavioralInsightSource()
        
        # Value (4개) ⭐ v7.8.0: LLM + Web 통합
        self.definite_data = DefiniteDataSource()
        self.ai_augmented = AIAugmentedEstimationSource(self.llm_mode)  # ⭐ 신규
        self.rag = RAGBenchmarkSource()
        self.statistical_value = StatisticalValueSource()
        
        # Deprecated (하위 호환 - alias로 대체)
        self.spacetime = SpacetimeConstraintSource()  # deprecated
        self.conservation = ConservationLawSource()  # deprecated
        self.mathematical = MathematicalDefinitionSource()  # deprecated
        self.llm = self.ai_augmented  # v7.10.0: AIAugmentedEstimationSource로 대체 (alias)
        self.web = self.ai_augmented  # v7.10.0: AIAugmentedEstimationSource로 대체 (alias)
        
        logger.info(f"  ✅ 8개 핵심 Source 준비 완료 (v7.8.0)")
        logger.info(f"  🆕 Physical 통합 (개념 기반)")
        logger.info(f"  🆕 AIAugmented (LLM+Web 통합)")
    
    @property
    def llm_mode(self) -> str:
        """
        LLM 모드 동적 읽기 (v7.9.0)
        
        _llm_mode가 None이면 settings에서 동적으로 읽음
        """
        if self._llm_mode is None:
            from umis_rag.core.config import settings
            return settings.llm_mode
        return self._llm_mode

    
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
        """Physical Constraints 수집 (v7.8.0: 통합)"""
        
        # v7.8.0: UnifiedPhysicalConstraintSource 사용
        return self.physical.collect(question, context)
    
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
        
        # 행동경제학 (맥락 기반 선택)
        # B2C 소비자 행동 또는 심리 관련 질문일 때만
        if context and self._should_use_behavioral(question, context):
            guides.extend(self.behavioral.collect(question, context))
        
        return guides
    
    def _should_use_behavioral(self, question: str, context: Context) -> bool:
        """행동경제학 소스 사용 여부 판단"""
        # B2C 비즈니스 모델
        if context.business_model and 'B2C' in context.business_model:
            return True
        
        # 소비자/심리/행동 키워드
        behavioral_keywords = [
            'consumer', 'customer behavior', 'psychology', 'decision making',
            '소비자', '구매', '선호', '행동', '심리'
        ]
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in behavioral_keywords):
            return True
        
        return False
    
    def _collect_values_sequential(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[ValueEstimate]:
        """Value Sources 순차 수집 (v7.8.0)"""
        
        estimates = []
        
        # 1. 확정 데이터 (항상)
        estimates.extend(self.definite_data.collect(question, context))
        
        # 2. AI 증강 추정 (v7.8.0: LLM + Web 통합) ⭐
        estimates.extend(self.ai_augmented.collect(question, context))
        
        # 3. RAG 벤치마크
        estimates.extend(self.rag.collect(question, context))
        
        # 4. 통계값 (다른 것 없을 때만) ⭐
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
        """
        Value Sources 병렬 수집
        
        Args:
            question: 질문
            context: 컨텍스트
        
        Returns:
            List of ValueEstimate
        
        Note:
            ThreadPoolExecutor를 사용한 병렬 실행
            타임아웃: 각 소스당 30초
        """
        
        from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
        
        all_values = []
        max_workers = min(len(self.value_sources), 5)  # 최대 5개 동시 실행
        timeout_per_source = 30  # 각 소스당 30초 제한
        
        def collect_from_source(source):
            """단일 소스에서 수집"""
            try:
                return source.collect(question, context)
            except Exception as e:
                logger.warning(f"    ⚠️ {source.__class__.__name__} 실패: {e}")
                return []
        
        # 병렬 실행
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(collect_from_source, source): source
                for source in self.value_sources
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source, timeout=timeout_per_source * len(self.value_sources)):
                source = future_to_source[future]
                try:
                    values = future.result(timeout=timeout_per_source)
                    if values:
                        all_values.extend(values)
                        logger.info(f"    ✅ {source.__class__.__name__}: {len(values)}개")
                except TimeoutError:
                    logger.warning(f"    ⏱️ {source.__class__.__name__}: 타임아웃 (30초)")
                except Exception as e:
                    logger.warning(f"    ⚠️ {source.__class__.__name__}: {e}")
        
        return all_values

