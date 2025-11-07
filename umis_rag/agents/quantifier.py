"""
Quantifier RAG Agent Module

Quantifier (Bill) 에이전트의 RAG 기반 정량 분석 시스템입니다.

핵심 개념:
-----------
1. **Methodology Search**: 시장 유형 → 최적 계산 방법론 검색
2. **Benchmark Retrieval**: 유사 시장 벤치마크 데이터 검색
3. **Formula Library**: 검증된 계산 공식 라이브러리
4. **Data Definition**: 데이터 정의 검증 가이드

Quantifier의 4가지 방법:
-----------------------
Method 1: Top-Down (TAM → SAM)
Method 2: Bottom-Up (세그먼트 합산)
Method 3: Proxy (벤치마크 조정)
Method 4: Competitor Revenue (경쟁사 역산)

RAG Collections:
----------------
- calculation_methodologies: 계산 방법론 (30개)
- market_benchmarks: 시장 벤치마크 (100개)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

# v7.2.1: Multi-Layer Guestimation 통합
# DEPRECATED: v2.1 → v3.0으로 대체 (2025-11-07)
# TODO: Guestimation v3.0 통합 필요
# from umis_rag.utils.multilayer_guestimation import (
#     MultiLayerGuestimation,
#     BenchmarkCandidate,
#     EstimationResult as MultiLayerResult
# )

# v7.3.0: Guestimation v3.0 통합 (임시 주석)
# from umis_rag.guestimation_v3.tier1 import Tier1FastPath
# from umis_rag.guestimation_v3.tier2 import Tier2JudgmentPath


class QuantifierRAG:
    """
    Quantifier (Bill) RAG Agent
    
    역할:
    -----
    - SAM 계산 (4가지 방법)
    - 시장 규모 추정
    - 성장률 분석
    - 벤치마크 참조
    
    핵심 메서드:
    -----------
    - search_methodology(): 계산 방법론 검색
    - search_benchmark(): 벤치마크 데이터 검색
    - search_formula(): 계산 공식 검색
    
    협업:
    -----
    - Validator: 데이터 정의 검증 (필수 의존성)
    - Observer: 시장 구조 정보 활용
    """
    
    def __init__(self):
        """Quantifier RAG 에이전트 초기화"""
        logger.info("Quantifier RAG 에이전트 초기화")
        
        # v7.2.1: Multi-Layer Guestimation 엔진
        # DEPRECATED: v3.0으로 교체 필요
        # self.multilayer_guestimation = None  # Lazy 초기화
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Vector Stores (2개 Collection)
        try:
            # 1. 계산 방법론
            self.methodology_store = Chroma(
                collection_name="calculation_methodologies",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 방법론 Collection: {self.methodology_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  방법론 Collection 없음 (구축 필요): {e}")
            self.methodology_store = None
        
        try:
            # 2. 시장 벤치마크
            self.benchmark_store = Chroma(
                collection_name="market_benchmarks",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 벤치마크 Collection: {self.benchmark_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  벤치마크 Collection 없음 (구축 필요): {e}")
            self.benchmark_store = None
    
    def search_methodology(
        self,
        market_description: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        시장 유형 → 최적 계산 방법론 검색
        
        사용 시점:
        ----------
        SAM 계산 시작 시, 어떤 방법을 쓸지 결정
        
        예시:
        -----
        Input: "SaaS 기업용 소프트웨어, 세그먼트 명확"
        Output: [Bottom-Up by Cohort, ...]
        
        Parameters:
        -----------
        market_description: 시장 설명
        top_k: 반환할 방법 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.methodology_store:
            logger.warning("  ⚠️  방법론 RAG 미구축")
            return []
        
        logger.info(f"[Quantifier] 계산 방법론 검색")
        logger.info(f"  시장: {market_description[:100]}...")
        
        results = self.methodology_store.similarity_search_with_score(
            market_description,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 방법론 발견")
        for doc, score in results:
            method_name = doc.metadata.get('method_name', 'Unknown')
            logger.info(f"    - {method_name} (유사도: {score:.2f})")
        
        return results
    
    def search_benchmark(
        self,
        market: str,
        top_k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        유사 시장 벤치마크 데이터 검색
        
        사용 시점:
        ----------
        Method 3 (Proxy) 사용 시, 또는 크로스 체크용
        
        예시:
        -----
        Input: "한국 SaaS 시장"
        Output: [일본 SaaS $8B, 글로벌 SaaS 성장률 15%, ...]
        
        Parameters:
        -----------
        market: 시장 이름
        top_k: 반환할 벤치마크 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.benchmark_store:
            logger.warning("  ⚠️  벤치마크 RAG 미구축")
            return []
        
        logger.info(f"[Quantifier] 벤치마크 검색")
        logger.info(f"  시장: {market}")
        
        results = self.benchmark_store.similarity_search_with_score(
            market,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 벤치마크 발견")
        for doc, score in results:
            market_name = doc.metadata.get('market', 'Unknown')
            size = doc.metadata.get('size', 'N/A')
            logger.info(f"    - {market_name}: {size} (유사도: {score:.2f})")
        
        return results
    
    def search_formula(
        self,
        calculation_type: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        계산 공식 검색
        
        예시:
        -----
        Input: "Bottom-Up 세그먼트 계산"
        Output: [수량 × 빈도 × 단가, ...]
        """
        if not self.methodology_store:
            return []
        
        logger.info(f"[Quantifier] 공식 검색: {calculation_type}")
        
        results = self.methodology_store.similarity_search_with_score(
            calculation_type,
            k=top_k,
            filter={"type": "formula"}
        )
        
        return results
    
    def calculate_sam_with_rag(
        self,
        market_description: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        RAG 가이드 기반 SAM 계산
        
        프로세스:
        ---------
        1. 시장 유형 → 최적 방법론 검색
        2. 유사 시장 → 벤치마크 검색
        3. 방법론 적용 → SAM 계산
        4. 벤치마크 비교 → 타당성 검증
        
        Parameters:
        -----------
        market_description: 시장 설명
        data: 계산 데이터 (assumptions, segments, ...)
        
        Returns:
        --------
        SAM 계산 결과 + 방법론 + 벤치마크
        """
        logger.info("[Quantifier] RAG 기반 SAM 계산 시작")
        
        # 1. 방법론 검색
        methodologies = self.search_methodology(market_description, top_k=2)
        
        # 2. 벤치마크 검색
        benchmarks = self.search_benchmark(market_description, top_k=3)
        
        # 3. 결과 조합
        result = {
            'recommended_methods': [
                {
                    'method': doc.metadata.get('method_name'),
                    'confidence': score,
                    'rationale': doc.page_content[:200]
                }
                for doc, score in methodologies
            ],
            'benchmarks': [
                {
                    'market': doc.metadata.get('market'),
                    'size': doc.metadata.get('size'),
                    'similarity': score,
                    'data': doc.page_content[:200]
                }
                for doc, score in benchmarks
            ]
        }
        
        logger.info("  ✅ RAG 검색 완료")
        logger.info(f"    - 추천 방법: {len(result['recommended_methods'])}개")
        logger.info(f"    - 벤치마크: {len(result['benchmarks'])}개")
        
        return result

    def calculate_sam_with_hybrid(
        self,
        market_definition: Dict,
        method: str = 'auto'
    ) -> Dict:
        """
        Hybrid Guestimation: SAM 계산 (2단계 전략)
        
        Args:
            market_definition: {
                'market_name': str,
                'industry': str,
                'geography': str,
                'time_horizon': str,
                'context': {
                    'regulatory': bool,
                    'new_market': bool,
                    ...
                }
            }
            method: 'auto' | 'guestimation' | 'domain_reasoner'
        
        Returns:
            {
                'phase_1': {...},          # Guestimation 결과
                'recommendation': {...},    # Guardian 평가
                'phase_2': {...} | None,   # Domain Reasoner 결과 (조건부)
                'final_result': {...},      # 최종 결과
                'method_used': str
            }
        """
        
        logger.info("\n" + "=" * 70)
        logger.info("Hybrid Guestimation: SAM 계산")
        logger.info("=" * 70)
        logger.info(f"  시장: {market_definition.get('market_name', 'Unknown')}")
        logger.info(f"  방법: {method}")
        
        # ===== Phase 1: Guestimation (항상 실행) =====
        logger.info("\n[Phase 1] Guestimation 실행")
        logger.info("-" * 70)
        
        phase_1_result = self._execute_guestimation(market_definition)
        
        logger.info(f"  추정값: {phase_1_result.get('value', 'N/A')}")
        logger.info(f"  범위: {phase_1_result.get('range', 'N/A')}")
        logger.info(f"  신뢰도: {phase_1_result.get('confidence', 0)*100:.0f}%")
        
        # ===== Guardian 평가 =====
        logger.info("\n[Guardian] 방법론 평가")
        logger.info("-" * 70)
        
        from umis_rag.guardian.meta_rag import GuardianMetaRAG
        
        guardian = GuardianMetaRAG()
        
        recommendation = guardian.recommend_methodology(
            estimate_result=phase_1_result,
            context=market_definition.get('context', {})
        )
        
        logger.info(f"  권고: {recommendation['recommendation']}")
        logger.info(f"  이유: {recommendation['reason']}")
        logger.info(f"  우선순위: {recommendation['priority']}")
        
        # ===== Phase 2: Domain Reasoner (조건부) =====
        phase_2_result = None
        
        # 자동 모드 & Phase 2 권고
        if method == 'auto' and recommendation['recommendation'] == 'domain_reasoner':
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Guardian 권고: Phase 2 진행")
            logger.info(f"  이유: {recommendation['reason']}")
            logger.info(f"  우선순위: {recommendation['priority']}")
            logger.info(f"{'='*70}")
            
            # Required → 자동 실행
            if recommendation['priority'] == 'required':
                logger.info("\n→ 자동 실행 (필수)")
                phase_2_result = self._execute_domain_reasoner(market_definition, phase_1_result)
            
            # High → 사용자 확인 (실제로는 자동 실행, CLI에서는 확인 필요)
            elif recommendation['priority'] in ['high', 'medium']:
                logger.info(f"\n→ Phase 2 권고 (우선순위: {recommendation['priority']})")
                logger.info(f"  예상 시간: {recommendation['estimated_time']}")
                
                # CLI 모드에서는 자동 실행 (실제 Cursor에서는 사용자 확인)
                logger.info("  → 자동 실행 (CLI 모드)")
                phase_2_result = self._execute_domain_reasoner(market_definition, phase_1_result)
        
        # 명시적 Domain Reasoner 요청
        elif method == 'domain_reasoner':
            logger.info("\n[Phase 2] Domain Reasoner 명시적 실행")
            phase_2_result = self._execute_domain_reasoner(market_definition, phase_1_result)
        
        # ===== 최종 결과 =====
        final_result = phase_2_result if phase_2_result else phase_1_result
        method_used = 'domain_reasoner' if phase_2_result else 'guestimation'
        
        logger.info("\n" + "=" * 70)
        logger.info("최종 결과")
        logger.info("=" * 70)
        logger.info(f"  사용 방법론: {method_used}")
        logger.info(f"  추정값: {final_result.get('point_estimate', final_result.get('value', 'N/A'))}")
        
        return {
            'phase_1': phase_1_result,
            'recommendation': recommendation,
            'phase_2': phase_2_result,
            'final_result': final_result,
            'method_used': method_used
        }
    
    def _execute_guestimation(self, market_definition: Dict) -> Dict:
        """Phase 1: Guestimation 실행"""
        
        # Stub - 실제로는 Guestimation 로직 호출
        # 여기서는 간단한 추정
        
        return {
            'value': 100_000_000_000,  # 1,000억 (예시)
            'range': (50_000_000_000, 150_000_000_000),
            'confidence': 0.6,
            'method': 'guestimation',
            'est_id': 'EST_001'
        }
    
    def _execute_domain_reasoner(
        self,
        market_definition: Dict,
        phase_1_result: Dict
    ) -> Dict:
        """Phase 2: Domain Reasoner 실행"""
        
        logger.info("\n[Phase 2] Domain Reasoner 실행")
        logger.info("-" * 70)
        
        from umis_rag.methodologies.domain_reasoner import DomainReasonerEngine
        
        engine = DomainReasonerEngine()
        
        # Domain Reasoner 실행
        result = engine.execute(
            question=market_definition.get('market_name', 'Market'),
            domain=market_definition.get('industry', 'general'),
            geography=market_definition.get('geography', 'KR'),
            time_horizon=market_definition.get('time_horizon', '2025-2030'),
            phase_1_context=phase_1_result
        )
        
        return {
            'point_estimate': result.point_estimate,
            'range_estimate': result.range_estimate,
            'should_vs_will': result.should_vs_will,
            'confidence': result.confidence,
            'signal_breakdown': result.signal_breakdown,
            'evidence_table': result.evidence_table
        }


    # DEPRECATED: v7.3.0에서 Guestimation v3.0으로 대체 (2025-11-07)
    # TODO: Guestimation v3.0 통합 필요
    # def estimate_with_multilayer(
    #     self,
    #     question: str,
    #     project_context: Optional[Dict] = None,
    #     target_profile: Optional[BenchmarkCandidate] = None
    # ) -> MultiLayerResult:
    #     """
    #     Multi-Layer Guestimation으로 추정
    #     
    #     DEPRECATED: v2.1 → v3.0으로 대체
    #     대체: Tier1FastPath + Tier2JudgmentPath
    #     
    #     8개 레이어를 순차적으로 시도하여 최적의 추정 방법 자동 선택
    #     
    #     Args:
    #         question: 추정 질문 (예: "한국 음식점 재방문 주기는?")
    #         project_context: 프로젝트 데이터 (확정된 값들)
    #         target_profile: 타겟 프로필 (비교 기준)
    #     
    #     Returns:
    #         MultiLayerResult (EstimationResult)
    #     
    #     Usage:
    #         quantifier = QuantifierRAG()
    #         result = quantifier.estimate_with_multilayer(
    #             "한국 SaaS 평균 Churn Rate는?",
    #             target_profile=BenchmarkCandidate(...)
    #         )
    #     """
    #     logger.info(f"[Quantifier] Multi-Layer Guestimation 시작: {question}")
    #     
    #     # Lazy 초기화
    #     if self.multilayer_guestimation is None:
    #         self.multilayer_guestimation = MultiLayerGuestimation(
    #             project_context=project_context or {}
    #         )
    #     
    #     # RAG 벤치마크 검색 (Layer 7용)
    #     rag_candidates = []
    #     if self.benchmark_store and target_profile:
    #         logger.info("  🔍 RAG 벤치마크 검색 중...")
    #         
    #         # 키워드 추출하여 검색
    #         results = self.benchmark_store.similarity_search_with_score(
    #             question,
    #             k=5
    #         )
    #         
    #         # BenchmarkCandidate로 변환 (간소화)
    #         for doc, score in results:
    #             metadata = doc.metadata
    #             candidate = BenchmarkCandidate(
    #                 name=metadata.get('name', 'Unknown'),
    #                 value=metadata.get('value', 0.0),
    #                 product_type=metadata.get('product_type', 'unknown'),
    #                 consumer_type=metadata.get('consumer_type', 'unknown'),
    #                 price=metadata.get('price'),
    #                 is_essential=metadata.get('is_essential', False),
    #                 source=metadata.get('source', 'RAG'),
    #                 context=metadata
    #             )
    #             rag_candidates.append(candidate)
    #         
    #         logger.info(f"  ✅ RAG 후보: {len(rag_candidates)}개")
    #     
    #     # Multi-Layer 추정
    #     result = self.multilayer_guestimation.estimate(
    #         question=question,
    #         target_profile=target_profile,
    #         rag_candidates=rag_candidates
    #     )
    #     
    #     logger.info(f"  ✅ 추정 완료 - 출처: {result.source_layer.name if result.source_layer else 'None'}")
    #     logger.info(f"     값: {result.get_display_value()}, 신뢰도: {result.confidence:.0%}")
    #     
    #     return result


# Quantifier RAG 인스턴스 (싱글톤)
_quantifier_rag_instance = None

def get_quantifier_rag() -> QuantifierRAG:
    """Quantifier RAG 싱글톤 인스턴스 반환"""
    global _quantifier_rag_instance
    if _quantifier_rag_instance is None:
        _quantifier_rag_instance = QuantifierRAG()
    return _quantifier_rag_instance

