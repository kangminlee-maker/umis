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
from umis_rag.core.llm_interface import LLMProvider
from umis_rag.core.llm_provider_factory import get_default_llm_provider

from .common.estimation_result import Evidence, EstimationResult, create_definite_result
from .literal_source import LiteralSource
from .rag_source import RAGSource
from .validator_source import ValidatorSource
from .guardrail_analyzer import GuardrailAnalyzer
from .models import Context


class EvidenceCollector:
    """
    EvidenceCollector - 증거 수집기 (v7.11.0)
    
    역할:
    -----
    - Literal Source: Literal (프로젝트 데이터)
    - RAG Source: Direct RAG (학습된 규칙)
    - Validator Source: Validator Search (확정 데이터)
    - Guardrail Engine: 논리적/경험적 제약
    
    출력:
    -----
    - Evidence 객체 (definite_value, hard_bounds, soft_hints, logical_relations)
    - 확정 값이 있으면 EstimationResult 반환 (추정 불필요)
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        project_id: Optional[str] = None
    ):
        """
        초기화
        
        Args:
            llm_provider: LLMProvider (None이면 기본 Provider)
            project_id: 프로젝트 ID (Phase 0용)
        
        Note:
            v7.11.0: llm_mode 파라미터 제거됨
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        self._project_id = project_id
        
        logger.info("[EvidenceCollector] 초기화 시작")
        
        # Literal Source (프로젝트 데이터)
        self.literal_source = LiteralSource(project_id=project_id)
        logger.info("  ✅ Literal Source")
        
        # RAG Source (학습된 규칙)
        self.rag_source = RAGSource()
        logger.info("  ✅ RAG Source")
        
        # Validator Source (외부 데이터)
        self.validator_source = ValidatorSource()
        logger.info("  ✅ Validator Source")
        
        # Guardrail Analyzer (같은 Provider 사용)
        self.guardrail_analyzer = GuardrailAnalyzer(llm_provider=self.llm_provider)
        logger.info("  ✅ Guardrail Analyzer")
        
        logger.info("[EvidenceCollector] 초기화 완료")
    
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
        # Literal Source: Literal (프로젝트 데이터)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            phase0_result = self.literal_source.get(question, context)
            
            if phase0_result and phase0_result.confidence >= 0.95:
                logger.info(f"  ✅ Literal Source: 프로젝트 데이터 발견 ({phase0_result.value:,.0f})")
                evidence.definite_value = phase0_result.value
                evidence.source = "Phase 0 Literal (프로젝트 데이터)"
                evidence.confidence = phase0_result.confidence
                evidence.reasoning = phase0_result.reasoning
                
                # 확정 값 있으면 즉시 반환
                elapsed = time.time() - start_time
                result = create_definite_result(
                    value=phase0_result.value,
                    evidence=evidence,
                    reasoning=f"Phase 0 Literal (프로젝트 확정 데이터, {elapsed:.2f}초)"
                )
                result.cost['time'] = elapsed
                
                logger.info(f"  ⚡ 프로젝트 확정 데이터 발견 (Phase 0) → 추정 불필요")
                return result, evidence
        
        except Exception as e:
            logger.warning(f"  Phase 0 실패: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RAG Source: Direct RAG (학습된 규칙)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            # Phase1DirectRAG.estimate() 사용
            phase1_result = self.rag_source.estimate(question, context)
            
            if phase1_result and phase1_result.confidence >= 0.95:
                logger.info(f"  ✅ RAG Source: 확정 값 발견 ({phase1_result.value:,.0f})")
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
        # Validator Source: Validator Search (확정 데이터)
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
            
            phase2_result = self.validator_source.search_with_context(question, context_dict)
            
            if phase2_result and phase2_result.confidence >= 0.95:
                logger.info(f"  ✅ Validator Source: 확정 값 발견 ({phase2_result.value:,.0f})")
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
        Guardrail 수집 - Phase 2 유사 데이터를 자동 변환
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            Guardrail 리스트
        """
        guardrails = []
        
        try:
            logger.info(f"[Guardrail Engine] 자동 수집 시작")
            
            # Phase 2에서 유사 데이터 검색
            context_dict = {}
            if context:
                # Context 형식 처리: 객체 또는 딕셔너리
                if isinstance(context, dict):
                    context_dict = {k: v for k, v in context.items() if k in ['domain', 'region', 'industry']}
                else:
                    if hasattr(context, 'domain') and context.domain:
                        context_dict['domain'] = context.domain
                    if hasattr(context, 'region') and context.region:
                        context_dict['region'] = context.region
                    if hasattr(context, 'industry') and context.industry:
                        context_dict['industry'] = context.industry
            
            # Phase 2 검색 (similar_data 수집용)
            phase2_search_result = self.validator_source.search_with_context(
                question,
                context_dict
            )
            
            # 유사 데이터 추출
            similar_items = []
            
            if isinstance(phase2_search_result, dict):
                similar_items = phase2_search_result.get('similar_data', [])
            elif hasattr(phase2_search_result, 'metadata'):
                similar_items = phase2_search_result.metadata.get('similar_data', [])
            
            if not similar_items:
                logger.info(f"  유사 데이터 없음")
                return guardrails
            
            logger.info(f"  유사 데이터 {len(similar_items)}개 발견")
            
            # 각 유사 데이터를 Guardrail로 변환 (최대 5개)
            for i, item in enumerate(similar_items[:5]):
                try:
                    # 유사 데이터 형식 파싱
                    if isinstance(item, dict):
                        similar_question = item.get('question', '')
                        similar_value = item.get('value', 0)
                        similar_context = item.get('context', '')
                    elif isinstance(item, (tuple, list)) and len(item) >= 2:
                        similar_question = item[0]
                        similar_value = item[1]
                        similar_context = item[2] if len(item) > 2 else None
                    else:
                        logger.warning(f"    항목 {i+1}: 지원하지 않는 형식 ({type(item)})")
                        continue
                    
                    # Guardrail 분석
                    guardrail = self.guardrail_analyzer.analyze(
                        target_question=question,
                        similar_question=similar_question,
                        similar_value=similar_value,
                        target_context=f"{context.domain} | {context.region}" if context else None,
                        similar_context=similar_context
                    )
                    
                    if guardrail:
                        guardrails.append(guardrail)
                        logger.info(f"    ✅ Guardrail {i+1}: {guardrail.type.value} = {guardrail.value:,.0f}")
                    else:
                        logger.info(f"    ℹ️  Guardrail {i+1}: 무관")
                
                except Exception as e:
                    logger.warning(f"    항목 {i+1} 변환 실패: {e}")
                    continue
            
            logger.info(f"[Guardrail Engine] 수집 완료: {len(guardrails)}개")
            
        except Exception as e:
            logger.error(f"[Guardrail Engine] 실패: {e}")
        
        return guardrails
    
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
