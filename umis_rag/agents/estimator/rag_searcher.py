"""
Estimator RAG Searcher

projected_index Collection에서 학습된 규칙 검색 (agent_view="estimator")
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger
from .models import Context, LearnedRule


class EstimatorRAGSearcher:
    """
    학습된 규칙 검색 (projected_index)
    
    역할:
    -----
    - projected_index에서 agent_view="estimator" 검색
    - 맥락 기반 필터링
    - 시점 조정
    
    사용:
    ----
    searcher = EstimatorRAGSearcher()
    results = searcher.search("한국 음식점 월매출은?", context)
    """
    
    def __init__(self):
        """초기화"""
        logger.info("[Estimator RAG] 초기화")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Projected Index
        try:
            self.projected_store = Chroma(
                collection_name="projected_index",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            
            # 전체 청크 수
            total_count = self.projected_store._collection.count()
            logger.info(f"  ✅ projected_index: {total_count}개 청크")
            
            # guestimation 청크 수 (현재는 0개)
            # TODO: 실제로는 filter로 카운트 필요
            logger.info(f"  ℹ️  estimator 청크: 0개 (학습되면 증가)")
            
        except Exception as e:
            logger.error(f"  ❌ projected_index 로드 실패: {e}")
            self.projected_store = None
    
    def search(
        self,
        question: str,
        context: Optional[Context] = None,
        top_k: int = 5,
        min_similarity: float = 0.85
    ) -> List[Tuple[LearnedRule, float]]:
        """
        학습된 규칙 검색
        
        Args:
            question: 질문
            context: 맥락 (필터링용)
            top_k: 반환 개수
            min_similarity: 최소 유사도
        
        Returns:
            List[(LearnedRule, similarity)]
        """
        if not self.projected_store:
            logger.warning("[Estimator RAG] projected_index 없음")
            return []
        
        logger.info(f"[Estimator RAG] 검색: {question}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: 기본 필터 (agent_view)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        base_filter = {"agent_view": "estimator"}
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: 맥락 기반 필터 추가
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if context:
            if context.domain and context.domain != "General":
                base_filter["estimator_domain"] = context.domain
            
            if context.region:
                base_filter["estimator_region"] = context.region
        
        logger.info(f"  필터: {base_filter}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: 벡터 검색
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            results = self.projected_store.similarity_search_with_score(
                query=question,
                k=top_k * 2,  # 필터링 여유
                filter=base_filter
            )
            
            logger.info(f"  ✅ {len(results)}개 후보 발견")
            
        except Exception as e:
            logger.error(f"  ❌ 검색 실패: {e}")
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: 유사도 필터링
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        filtered = []
        
        for doc, score in results:
            similarity = 1.0 - score  # ChromaDB는 distance 리턴
            
            if similarity >= min_similarity:
                # LearnedRule로 변환
                rule = self._doc_to_learned_rule(doc)
                filtered.append((rule, similarity))
                
                logger.info(f"    - {rule.rule_id}: {similarity:.3f}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 5: Top K
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        final = filtered[:top_k]
        
        logger.info(f"  → 최종 {len(final)}개 (유사도 >={min_similarity})")
        
        return final
    
    def _doc_to_learned_rule(self, doc) -> LearnedRule:
        """Document → LearnedRule 변환"""
        
        metadata = doc.metadata
        
        # Context 재구성
        context = Context(
            intent=metadata.get('estimator_intent', 'get_value'),
            domain=metadata.get('estimator_domain', 'General'),
            region=metadata.get('estimator_region'),
            time_period=metadata.get('estimator_time_period')
        )
        
        # LearnedRule 생성
        rule = LearnedRule(
            rule_id=metadata.get('rule_id', 'UNKNOWN'),
            
            question_original=metadata.get('estimator_question', ''),
            question_normalized=metadata.get('estimator_question_normalized', ''),
            question_template=metadata.get('estimator_question_template', ''),
            question_keywords=metadata.get('estimator_question_keywords', []),
            
            context=context,
            
            value=metadata.get('estimator_value', 0.0),
            value_range=(
                metadata.get('estimator_value_min', 0.0),
                metadata.get('estimator_value_max', 0.0)
            ),
            unit=metadata.get('estimator_unit', ''),
            confidence=metadata.get('estimator_confidence', 0.0),
            uncertainty=metadata.get('estimator_uncertainty', 0.3),
            
            tier_origin=metadata.get('tier_origin', 'unknown'),
            sources=metadata.get('sources', []),
            judgment_strategy=metadata.get('judgment_strategy', ''),
            evidence_count=metadata.get('evidence_count', 0),
            
            usage_count=metadata.get('usage_count', 0),
            created_at=metadata.get('created_at', ''),
            last_used=metadata.get('last_used', ''),
            last_verified=metadata.get('last_verified', '')
        )
        
        return rule

