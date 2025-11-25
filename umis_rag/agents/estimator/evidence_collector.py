"""
EvidenceCollector - 증거 및 가드레일 수집기 (v7.11.0 Stage 1)

역할:
- Phase 0-2 (Literal, Direct RAG, Validator Search)를 통합
- 확정 값, Hard Constraints, Soft Hints 수집
- Guardrail Engine 통합

설계 원칙:
- 증거는 "찾는 것"이지 "생성하는 것"이 아님
- 확정 값이 있으면 즉시 반환 (추정 불필요)
- Hard Constraints는 절대 위반 불가
- Soft Hints는 경고만
"""

from typing import Optional, List, Dict, Any, Tuple
import time

from umis_rag.utils.logger import logger
from umis_rag.core.config import settings

from .common.estimation_result import Evidence, EstimationResult, create_definite_result
from .phase1_direct_rag import Phase1DirectRAG
from .phase2_validator_search_enhanced import Phase2ValidatorSearchEnhanced
from .guardrail_analyzer import GuardrailAnalyzer
from .models import Context


class EvidenceCollector:
    """
    EvidenceCollector - 증거 수집기 (v7.11.0)
    
    역할:
    -----
    - Phase 0: Literal (프로젝트 데이터)
    - Phase 1: Direct RAG (학습된 규칙)
    - Phase 2: Validator Search (확정 데이터)
    - Guardrail Engine: 논리적/경험적 제약
    
    출력:
    -----
    - Evidence 객체 (definite_value, hard_bounds, soft_hints, logical_relations)
    - 확정 값이 있으면 EstimationResult 반환 (추정 불필요)
    """
    
    def __init__(self, llm_mode: Optional[str] = None):
        """
        초기화
        
        Args:
            llm_mode: LLM 모드 (None이면 settings에서 읽기)
        """
        self._llm_mode = llm_mode
        
        logger.info("[EvidenceCollector] 초기화 시작")
        
        # Phase 1: Direct RAG
        self.phase1 = Phase1DirectRAG()
        logger.info("  ✅ Phase 1 (Direct RAG)")
        
        # Phase 2: Validator Search
        self.phase2 = Phase2ValidatorSearchEnhanced()
        logger.info("  ✅ Phase 2 (Validator Search Enhanced)")
        
        # Guardrail Analyzer
        self.guardrail_analyzer = GuardrailAnalyzer(llm_mode=self.llm_mode)
        logger.info("  ✅ Guardrail Analyzer")
        
        logger.info("[EvidenceCollector] 초기화 완료")
    
    @property
    def llm_mode(self) -> str:
        """LLM 모드 동적 읽기"""
        if self._llm_mode is None:
            return settings.llm_mode
        return self._llm_mode
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 인터페이스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect(
        self,
        question: str,
        context: Optional[Context] = None,
        collect_guardrails: bool = True
    ) -> Tuple[Optional[EstimationResult], Evidence]:
        """
        증거 수집 (v7.11.0)
        
        Args:
            question: 질문
            context: 맥락 (선택)
            collect_guardrails: Guardrail 수집 여부
        
        Returns:
            (EstimationResult, Evidence)
            - EstimationResult: 확정 값이 있으면 반환, 없으면 None
            - Evidence: 수집된 모든 증거
        """
        logger.info(f"[EvidenceCollector] 수집 시작: {question}")
        start_time = time.time()
        
        evidence = Evidence()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 0: Literal (프로젝트 데이터)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TODO: 프로젝트 데이터 구현
        # 현재는 스킵
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 1: Direct RAG (학습된 규칙)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            # Phase1DirectRAG.estimate() 사용
            phase1_result = self.phase1.estimate(question, context)
            
            if phase1_result and phase1_result.confidence >= 0.95:
                logger.info(f"  ✅ Phase 1: 확정 값 발견 ({phase1_result.value:,.0f})")
                evidence.definite_value = phase1_result.value
                evidence.source = "Phase 1 Direct RAG"
                evidence.confidence = phase1_result.confidence
                evidence.reasoning = phase1_result.reasoning or "학습된 규칙"
                
                # 확정 값 있으면 즉시 반환
                elapsed = time.time() - start_time
                result = create_definite_result(
                    value=phase1_result.value,
                    evidence=evidence,
                    reasoning=f"Phase 1 Direct RAG (확정, {elapsed:.2f}초)"
                )
                result.cost['time'] = elapsed
                
                logger.info(f"  ⚡ 확정 값 발견 (Phase 1) → 추정 불필요")
                return result, evidence
        
        except Exception as e:
            logger.warning(f"  Phase 1 실패: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2: Validator Search (확정 데이터)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            # Phase2에서는 search_with_context() 사용
            # Context에서 필요한 정보 추출
            context_dict = {}
            if context:
                context_dict = {
                    'domain': context.domain,
                    'region': context.region,
                    'industry': context.domain if context.domain else None
                }
            
            phase2_result = self.phase2.search_with_context(question, context_dict)
            
            if phase2_result and phase2_result.confidence >= 0.95:
                logger.info(f"  ✅ Phase 2: 확정 값 발견 ({phase2_result.value:,.0f})")
                evidence.definite_value = phase2_result.value
                evidence.source = "Phase 2 Validator Search"
                evidence.confidence = phase2_result.confidence
                evidence.reasoning = getattr(phase2_result, 'reasoning', None) or "확정 데이터"
                
                # 확정 값 있으면 즉시 반환
                elapsed = time.time() - start_time
                result = create_definite_result(
                    value=phase2_result.value,
                    evidence=evidence,
                    reasoning=f"Phase 2 Validator Search (확정, {elapsed:.2f}초)"
                )
                result.cost['time'] = elapsed
                
                logger.info(f"  ⚡ 확정 값 발견 (Phase 2) → 추정 불필요")
                return result, evidence
            
            # 확정 값은 없지만 soft hint로 활용 가능
            if phase2_result and hasattr(phase2_result, 'value_range') and phase2_result.value_range:
                evidence.soft_hints.append({
                    'type': 'range',
                    'min': phase2_result.value_range[0],
                    'max': phase2_result.value_range[1],
                    'source': 'Phase 2 Validator',
                    'confidence': phase2_result.confidence
                })
                logger.info(f"  Soft Hint: 범위 {phase2_result.value_range}")
        
        except Exception as e:
            logger.warning(f"  Phase 2 실패: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Guardrail Engine (논리적/경험적 제약)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if collect_guardrails:
            try:
                guardrails = self._collect_guardrails(question, context)
                
                # Hard Bounds 추출
                hard_min, hard_max = self._extract_hard_bounds(guardrails)
                if hard_min is not None or hard_max is not None:
                    evidence.hard_bounds = (hard_min, hard_max)
                    logger.info(f"  Hard Bounds: ({hard_min}, {hard_max})")
                
                # Soft Hints 추가
                soft_guardrails = [g for g in guardrails if not g.is_hard]
                for g in soft_guardrails:
                    evidence.soft_hints.append({
                        'type': 'guardrail',
                        'value': g.value,
                        'direction': 'upper' if 'UPPER' in g.type.value else 'lower',
                        'source': g.source,
                        'confidence': g.confidence,
                        'reasoning': g.reasoning
                    })
                
                logger.info(f"  Guardrails: {len(guardrails)}개 수집")
            
            except Exception as e:
                logger.warning(f"  Guardrail 수집 실패: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 결과 반환
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elapsed = time.time() - start_time
        evidence.source = "EvidenceCollector"
        
        logger.info(f"[EvidenceCollector] 수집 완료 ({elapsed:.2f}초)")
        logger.info(f"  - Definite Value: {evidence.definite_value}")
        logger.info(f"  - Hard Bounds: {evidence.hard_bounds}")
        logger.info(f"  - Soft Hints: {len(evidence.soft_hints)}개")
        
        # 확정 값 없음 → 추정 필요
        return None, evidence
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Private Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _collect_guardrails(
        self,
        question: str,
        context: Optional[Context]
    ) -> List[Any]:
        """
        Guardrail 수집
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            Guardrail 리스트
        """
        # TODO: Guardrail Engine 구현
        # 현재는 빈 리스트 반환
        return []
    
    def _extract_hard_bounds(
        self,
        guardrails: List[Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Hard Guardrails에서 상/하한 추출
        
        Args:
            guardrails: Guardrail 리스트
        
        Returns:
            (hard_min, hard_max)
        """
        hard_min = None
        hard_max = None
        
        for g in guardrails:
            if not g.is_hard:
                continue
            
            if 'LOWER' in g.type.value:
                if hard_min is None or g.value > hard_min:
                    hard_min = g.value
            
            elif 'UPPER' in g.type.value:
                if hard_max is None or g.value < hard_max:
                    hard_max = g.value
        
        return hard_min, hard_max
