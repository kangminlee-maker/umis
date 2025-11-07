"""
Tier 1: Fast Path

Built-in 규칙 + 학습된 규칙 RAG 검색
"""

from typing import Optional, List, Dict, Tuple
import yaml
from pathlib import Path

from umis_rag.utils.logger import logger
from .models import Context, EstimationResult, Tier1Config, LearnedRule
from .rag_searcher import EstimatorRAGSearcher


class Tier1FastPath:
    """
    Tier 1: Fast Path
    
    원칙:
    -----
    - 명백한 케이스만 처리
    - 확실하지 않으면 Tier 2로
    - False Negative 허용, False Positive 금지
    
    처리:
    -----
    1. Built-in 규칙 체크 (패턴 매칭)
    2. 학습된 규칙 검색 (RAG)
    3. 매칭 없으면 None (Tier 2로)
    """
    
    def __init__(self, config: Optional[Tier1Config] = None):
        """
        초기화
        
        Args:
            config: Tier 1 설정 (옵션)
        """
        self.config = config or Tier1Config()
        
        logger.info("[Tier 1] Fast Path 초기화")
        
        # Built-in 규칙 로드
        self.builtin_rules = self._load_builtin_rules()
        logger.info(f"  ✅ Built-in 규칙: {len(self.builtin_rules)}개")
        
        # RAG Searcher
        self.rag_searcher = EstimatorRAGSearcher()
        logger.info(f"  ✅ RAG Searcher 준비")
    
    def _load_builtin_rules(self) -> List[Dict]:
        """Built-in 규칙 로드"""
        
        rules_path = Path(__file__).parent.parent.parent / "data" / "tier1_rules" / "builtin.yaml"
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return data.get('rules', [])
        
        except Exception as e:
            logger.warning(f"  ⚠️  Built-in 규칙 로드 실패: {e}")
            return []
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        Tier 1 추정 시도
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult or None
            - 성공: EstimationResult (tier=1)
            - 실패: None (Tier 2로 넘김)
        """
        logger.info(f"[Tier 1] 시도: {question}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: Built-in 규칙 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        builtin_result = self._try_builtin_rules(question)
        
        if builtin_result:
            logger.info(f"  ✅ Built-in 매칭: {builtin_result.reasoning}")
            return builtin_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: 학습된 규칙 RAG 검색
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        rag_result = self._try_rag_search(question, context)
        
        if rag_result:
            logger.info(f"  ✅ RAG 매칭: {rag_result.reasoning}")
            return rag_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: 매칭 없음 → Tier 2로
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info(f"  → Tier 2로 넘김 (명백한 패턴 없음)")
        return None
    
    def _try_builtin_rules(self, question: str) -> Optional[EstimationResult]:
        """
        Built-in 규칙 체크
        
        패턴 매칭:
        - matches 중 하나라도 포함
        - excludes 하나도 없어야
        - 모두 만족 → confidence 1.0
        """
        question_lower = question.lower()
        
        for rule in self.builtin_rules:
            # 매칭 체크
            matches = rule.get('matches', [])
            if not any(m in question_lower for m in matches):
                continue
            
            # 제외 체크
            excludes = rule.get('excludes', [])
            if any(e in question_lower for e in excludes):
                continue
            
            # 매칭 성공!
            logger.info(f"    Built-in 매칭: {rule['rule_id']}")
            
            result_data = rule.get('result', {})
            
            # EstimationResult 생성
            result = EstimationResult(
                question=question,
                tier=1,
                
                value=result_data.get('value'),
                value_range=result_data.get('range'),
                unit=result_data.get('unit', ''),
                
                confidence=result_data.get('confidence', 1.0),
                
                reasoning=f"Built-in 규칙: {rule['rule_id']} ({rule['pattern']})",
                logic_steps=[
                    f"Built-in 규칙 매칭: {rule['pattern']}",
                    f"출처: {result_data.get('source', 'Unknown')}"
                ]
            )
            
            # 노트 추가
            if 'notes' in result_data:
                result.logic_steps.extend([f"참고: {note}" for note in result_data['notes']])
            
            return result
        
        # 매칭 없음
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
            logger.info("    RAG 매칭 없음 (유사도 <0.85)")
            return None
        
        # 최고 유사도 선택
        best_rule, best_similarity = results[0]
        
        logger.info(f"    RAG 매칭: {best_rule.rule_id} (유사도 {best_similarity:.3f})")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 맥락 일치도 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        context_match = self._check_context_match(best_rule, context)
        
        if context_match < 0.80:
            logger.info(f"    맥락 불일치 ({context_match:.2f}) → Tier 2로")
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
            tier=1,
            
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

