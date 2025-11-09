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

# v7.3.1: Estimator (Fermi) Agent 통합
from umis_rag.agents.estimator import get_estimator_rag
from umis_rag.agents.estimator.models import EstimationResult


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
        
        # v7.3.1: Estimator (Fermi) Agent
        self.estimator = None  # Lazy 초기화
        
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

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # calculate_sam_with_hybrid() 제거됨 (v7.5.0)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 
    # v7.2.0 이하: Guestimation = 기능 (Quantifier가 직접 호출)
    # v7.3.0+: Guestimation → Estimator Agent로 진화
    # v7.5.0: Estimator Tier 2/3 완성 → Domain Reasoner 대체
    # 
    # 대체 방법:
    #   Before: quantifier.calculate_sam_with_hybrid(market_def)
    #   After:  estimator.estimate(question, context)
    # 
    # Archive:
    #   - umis_rag/methodologies/domain_reasoner.py
    #   - data/raw/umis_domain_reasoner_methodology.yaml
    #   - scripts/test_quantifier_hybrid.py
    #   - scripts/test_e2e_full_workflow.py
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def estimate(
        self,
        question: str,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None
    ) -> EstimationResult:
        """
        Estimator (Fermi) Agent로 추정
        
        v7.3.1: Estimator Agent 통합 (간결화)
        
        Args:
            question: 추정 질문 (예: "한국 SaaS Churn Rate는?")
            domain: 도메인 (예: "B2B_SaaS", "Food_Service")
            region: 지역 (예: "한국", "서울")
            time_period: 시점 (예: "2024")
        
        Returns:
            EstimationResult
        
        Usage:
            quantifier = QuantifierRAG()
            result = quantifier.estimate(
                "한국 SaaS 평균 Churn Rate는?",
                domain="B2B_SaaS",
                region="한국"
            )
        """
        logger.info(f"[Quantifier] Estimator Agent 호출: {question}")
        
        # Lazy 초기화
        if self.estimator is None:
            self.estimator = get_estimator_rag()
            logger.info("  ✅ Estimator Agent 로드")
        
        # Estimator Agent에 위임
        result = self.estimator.estimate(
            question=question,
            domain=domain,
            region=region,
            time_period=time_period
        )
        
        if result:
            logger.info(f"  ✅ 완료: {result.value} (Tier {result.tier})")
        else:
            logger.warning("  ❌ 추정 실패")
        
        return result


# Quantifier RAG 인스턴스 (싱글톤)
_quantifier_rag_instance = None

def get_quantifier_rag() -> QuantifierRAG:
    """Quantifier RAG 싱글톤 인스턴스 반환"""
    global _quantifier_rag_instance
    if _quantifier_rag_instance is None:
        _quantifier_rag_instance = QuantifierRAG()
    return _quantifier_rag_instance

