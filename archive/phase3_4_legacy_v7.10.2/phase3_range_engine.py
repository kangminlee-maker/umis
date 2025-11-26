"""
Phase 3: Guardrail Range Engine (v7.10.0)

순수 Range 엔진: Hard Guardrails 기반으로 값이 존재해야 하는 안전한 범위 계산
"""

from typing import Optional, List, Dict, Any, Tuple
import time

from umis_rag.utils.logger import logger
from .models import (
    Context, EstimationResult, Phase3Config,
    Guardrail, GuardrailType, GuardrailCollector
)
from .source_collector import SourceCollector


class Phase3GuardrailRangeEngine:
    """Phase 3: Guardrail Range Engine (v7.10.0)"""
    
    def __init__(self, config: Optional[Phase3Config] = None, llm_mode: Optional[str] = None):
        self.config = config or Phase3Config()
        self._llm_mode = llm_mode
        logger.info("[Phase 3] Guardrail Range Engine 초기화")
        self.source_collector = SourceCollector(llm_mode=self.llm_mode)
    
    @property
    def llm_mode(self) -> str:
        if self._llm_mode is None:
            from umis_rag.core.config import settings
            return settings.llm_mode
        return self._llm_mode
    
    async def calculate_range(
        self,
        question: str,
        context: Context,
        guardrail_collector: GuardrailCollector
    ) -> EstimationResult:
        """Range 계산 (Hard Guardrails 기반)"""
        start_time = time.time()
        
        try:
            # Step 1: 절대 경계
            min_val, max_val = self._get_absolute_bounds(context)
            
            # Step 2: Stage 1 Hard Guardrails 적용
            bounds = guardrail_collector.get_hard_bounds()
            min_val = max(min_val, bounds['min'])
            max_val = min(max_val, bounds['max']) if bounds['max'] != float('inf') else max_val
            
            # Step 3: 11개 Source에서 Hard Constraints 추출
            source_constraints = await self._extract_hard_constraints(question, context)
            
            # Step 4: 교집합
            for c in source_constraints:
                if c['type'] == 'upper':
                    max_val = min(max_val, c['value'])
                elif c['type'] == 'lower':
                    min_val = max(min_val, c['value'])
            
            final_range = [min_val, max_val]
            
            # Step 5: value는 Range 중앙값 (부수적)
            value = None
            if max_val != float('inf'):
                value = (min_val + max_val) / 2
            
            # Step 6: Confidence (Hard 기반)
            confidence = self._calculate_confidence(
                len(guardrail_collector.hard_guardrails),
                len(source_constraints)
            )
            
            return EstimationResult(
                question=question,
                value=value,
                value_range=tuple(final_range),
                confidence=confidence,
                phase=3,
                reasoning_detail={
                    "method": "hard_guardrail_intersection",
                    "hard_count": len(guardrail_collector.hard_guardrails),
                    "source_count": len(source_constraints)
                },
                execution_time=time.time() - start_time
            )
        
        except Exception as e:
            logger.error(f"Range 계산 실패: {e}")
            min_val, max_val = self._get_absolute_bounds(context)
            return EstimationResult(
                question=question,
                value=None,
                value_range=(min_val, max_val),
                confidence=0.50,
                phase=3,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _get_absolute_bounds(self, context: Context) -> Tuple[float, float]:
        """절대 경계"""
        min_val = 0.0
        if context.region and "한국" in context.region:
            max_val = 51_000_000 * 10
        else:
            max_val = 8_000_000_000 * 10
        return min_val, max_val
    
    async def _extract_hard_constraints(self, question: str, context: Context) -> List[Dict]:
        """11개 Source에서 Hard Constraints 추출"""
        constraints = []
        sources = await self.source_collector.collect_all(question, context)
        
        for source in sources:
            if source.source_category.value == "physical" and source.boundary:
                if source.boundary.max_value is not None:
                    constraints.append({'type': 'upper', 'value': source.boundary.max_value})
                if source.boundary.min_value is not None:
                    constraints.append({'type': 'lower', 'value': source.boundary.min_value})
        
        return constraints
    
    def _calculate_confidence(self, hard_count: int, source_count: int) -> float:
        """Confidence 계산"""
        base_conf = 0.90
        hard_bonus = min(0.05, hard_count * 0.01)
        source_bonus = min(0.05, source_count * 0.005)
        return min(0.95, base_conf + hard_bonus + source_bonus)
