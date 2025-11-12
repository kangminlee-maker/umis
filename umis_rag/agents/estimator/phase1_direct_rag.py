"""
Phase 1: Direct RAG (v7.7.0)

학습된 규칙 RAG 검색 (Direct RAG)

v7.7.0 파일명 변경:
-------------------
- tier1.py → phase1_direct_rag.py
- Tier1FastPath → Phase1DirectRAG
- 용어 명확화 (Tier는 구현 개념, Phase는 사용자 개념)

v7.6.0 변경:
------------
- Built-in Rules 완전 제거 (답변 일관성 확보)
- Learned RAG만 사용
- threshold 0.95+ (엄격)
- 처음 추정 시 무조건 통과 (의도됨)
"""

from typing import Optional, List, Dict, Tuple
import yaml
from pathlib import Path

from umis_rag.utils.logger import logger
from .models import Context, EstimationResult, Phase1Config, LearnedRule
from .rag_searcher import EstimatorRAGSearcher


class Phase1DirectRAG:
    """
    Phase 1: Direct RAG (v7.7.0 - 학습 규칙 검색)
    
    원칙:
    -----
    - 학습된 규칙만 사용 (답변 일관성)
    - 확실하지 않으면 Validator로
    - False Negative 허용, False Positive 금지
    
    처리:
    -----
    1. 학습된 규칙 RAG 검색 (threshold 0.95+)
    2. 매칭 없으면 None (Validator로)
    
    변경사항 (v7.6.0):
    ------------------
    - ❌ Built-in Rules 제거 (일관성 문제)
    - ✅ Learned RAG만 사용
    - ✅ 처음 추정 → 무조건 통과 (의도됨)
    """
    
    def __init__(self, config: Optional[Phase1Config] = None):
        """
        초기화 (v7.7.0)
        
        Args:
            config: Phase 1 설정 (옵션)
        """
        self.config = config or Phase1Config()
        
        logger.info("[Phase 1] Direct RAG 초기화")
        
        # v7.6.0: Built-in 규칙 제거 (학습형만 사용)
        # 이유: 답변 일관성 확보
        
        # RAG Searcher (학습된 규칙만)
        self.rag_searcher = EstimatorRAGSearcher()
        logger.info(f"  ✅ RAG Searcher 준비 (학습형만)")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # v7.6.0: Built-in Rules 제거 (DEPRECATED)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 이유: 답변 일관성 확보 (학습형만 사용)
    # 대체: Validator 검색 (Phase 2)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        Phase 1 추정 시도 (v7.7.0: 학습 규칙 Direct RAG)
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult or None
            - 성공: EstimationResult (phase=1)
            - 실패: None (Phase 2 Validator로 넘김)
        """
        logger.info(f"[Phase 1] 시도: {question}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # v7.6.0: Built-in 제거, 학습된 규칙 RAG만
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        rag_result = self._try_rag_search(question, context)
        
        if rag_result:
            logger.info(f"  ✅ RAG 매칭: {rag_result.reasoning}")
            return rag_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: 매칭 없음 → Phase 2로
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info(f"  → Phase 2 (Validator)로 넘김 (학습 규칙 없음)")
        return None
    
    def _try_rag_search(
        self,
        question: str,
        context: Optional[Context]
    ) -> Optional[EstimationResult]:
        """
        학습된 규칙 RAG 검색
        
        유사도 >= 0.85 → 사용
        """
        # RAG 검색
        results = self.rag_searcher.search(
            question=question,
            context=context,
            top_k=3,
            min_similarity=self.config.min_similarity
        )
        
        if not results:
            logger.info("    RAG 매칭 없음 (유사도 <0.95)")
            return None
        
        # 최고 유사도 선택
        best_rule, best_similarity = results[0]
        
        logger.info(f"    RAG 매칭: {best_rule.rule_id} (유사도 {best_similarity:.3f})")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 맥락 일치도 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        context_match = self._check_context_match(best_rule, context)
        
        if context_match < 0.80:
            logger.info(f"    맥락 불일치 ({context_match:.2f}) → Phase 2로")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 시점 조정 (필요 시)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        adjusted_value, adjustment_note = self._adjust_for_time(
            best_rule,
            context
        )
        
        # EstimationResult 생성
        result = EstimationResult(
            question=question,
            phase=1,
            
            value=adjusted_value or best_rule.value,
            value_range=best_rule.value_range,
            unit=best_rule.unit,
            
            confidence=best_rule.confidence * best_similarity,
            uncertainty=best_rule.uncertainty,
            
            reasoning=f"학습된 규칙: {best_rule.rule_id} (유사도 {best_similarity:.2%})",
            logic_steps=[
                f"유사 질문: {best_rule.question_original}",
                f"유사도: {best_similarity:.2%}",
                f"맥락 일치: {context_match:.0%}",
                f"출처: {best_rule.tier_origin}",
                f"사용 횟수: {best_rule.usage_count}회"
            ]
        )
        
        if adjustment_note:
            result.logic_steps.append(adjustment_note)
        
        # 학습 메타데이터 (usage_count 증가용)
        result.learn_metadata = {
            'rule_id': best_rule.rule_id,
            'action': 'increment_usage'
        }
        
        return result
    
    def _check_context_match(
        self,
        rule: LearnedRule,
        context: Optional[Context]
    ) -> float:
        """
        맥락 일치도 체크
        
        Returns:
            일치도 (0.0 ~ 1.0)
        """
        if not context:
            return 1.0
        
        match_score = 0.0
        checks = 0
        
        # Domain 체크
        if context.domain and context.domain != "General":
            checks += 1
            if rule.context.domain == context.domain:
                match_score += 1.0
            elif rule.context.domain == "General":
                match_score += 0.5  # General은 중간
        
        # Region 체크
        if context.region:
            checks += 1
            if rule.context.region == context.region:
                match_score += 1.0
            elif rule.context.region is None:
                match_score += 0.5
        
        # Time 체크 (같은 년도)
        if context.time_period:
            checks += 1
            if rule.context.time_period == context.time_period:
                match_score += 1.0
            elif rule.context.time_period:
                # 년도 차이 계산 (간단히)
                try:
                    diff = abs(int(context.time_period) - int(rule.context.time_period))
                    if diff <= 1:
                        match_score += 0.8
                    elif diff <= 2:
                        match_score += 0.6
                except:
                    match_score += 0.5
        
        # 평균
        if checks == 0:
            return 1.0
        
        return match_score / checks
    
    def _adjust_for_time(
        self,
        rule: LearnedRule,
        context: Optional[Context]
    ) -> tuple[Optional[float], Optional[str]]:
        """
        시점 조정
        
        Returns:
            (adjusted_value, note)
        """
        if not context or not context.time_period:
            return None, None
        
        if not rule.context.time_period:
            return None, None
        
        # 같은 시점
        if context.time_period == rule.context.time_period:
            return None, None
        
        # TODO: 성장률 적용 로직
        # 현재는 조정 안 함
        return None, f"시점 차이 있음 (저장: {rule.context.time_period}, 질문: {context.time_period})"

