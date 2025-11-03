"""
Observer RAG Agent Module

Observer (Albert) 에이전트의 RAG 기반 시장 구조 분석 시스템입니다.

핵심 개념:
-----------
1. **Structure Pattern Matching**: 관찰 → 구조 패턴 매칭
2. **Value Chain Benchmarks**: 유사 산업 가치사슬 참조
3. **Transaction Pattern Recognition**: 거래 패턴 인식
4. **Market Structure Comparison**: 시장 구조 비교

Observer의 핵심 역할:
--------------------
1. 시장 구조 관찰 및 해석
2. 가치사슬 맵핑
3. 거래 패턴 분석
4. 비효율성 발견

RAG Collections:
----------------
- market_structure_patterns: 시장 구조 패턴 (30개)
- value_chain_benchmarks: 가치사슬 벤치마크 (50개)
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


class ObserverRAG:
    """
    Observer (Albert) RAG Agent
    
    역할:
    -----
    - 시장 구조 분석
    - 가치사슬 맵핑
    - 거래 패턴 인식
    - 비효율성 발견
    
    핵심 메서드:
    -----------
    - search_structure_pattern(): 구조 패턴 검색
    - search_value_chain(): 가치사슬 벤치마크 검색
    - search_inefficiency(): 비효율성 패턴 검색
    
    협업:
    -----
    - Validator: 관찰 데이터 검증
    - Quantifier: 구조 정량화
    """
    
    def __init__(self):
        """Observer RAG 에이전트 초기화"""
        logger.info("Observer RAG 에이전트 초기화")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Vector Stores
        try:
            # 1. 시장 구조 패턴
            self.structure_store = Chroma(
                collection_name="market_structure_patterns",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 구조 패턴: {self.structure_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  구조 패턴 Collection 없음 (구축 필요): {e}")
            self.structure_store = None
        
        try:
            # 2. 가치사슬 벤치마크
            self.chain_store = Chroma(
                collection_name="value_chain_benchmarks",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 가치사슬: {self.chain_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  가치사슬 Collection 없음 (구축 필요): {e}")
            self.chain_store = None
    
    def search_structure_pattern(
        self,
        observations: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        시장 구조 패턴 검색
        
        사용 시점:
        ----------
        시장을 관찰하고 유사한 구조 패턴을 찾을 때
        
        예시:
        -----
        Input: "공급자-중개-수요자 3단계, 중개 수수료 20%"
        Output: [플랫폼 양면시장, 다단계 유통, ...]
        
        Parameters:
        -----------
        observations: 관찰 내용
        top_k: 반환할 패턴 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.structure_store:
            logger.warning("  ⚠️  구조 패턴 RAG 미구축")
            return []
        
        logger.info(f"[Observer] 구조 패턴 검색")
        logger.info(f"  관찰: {observations[:100]}...")
        
        results = self.structure_store.similarity_search_with_score(
            observations,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 패턴 발견")
        for doc, score in results:
            pattern_name = doc.metadata.get('structure_type', 'Unknown')
            logger.info(f"    - {pattern_name} (유사도: {score:.2f})")
        
        return results
    
    def search_value_chain(
        self,
        industry: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        가치사슬 벤치마크 검색
        
        사용 시점:
        ----------
        산업의 가치사슬을 파악할 때, 유사 산업 참조
        
        예시:
        -----
        Input: "음악 산업"
        Output: [아티스트→레이블→플랫폼→청취자 (마진 40%/20%/15%), ...]
        
        Parameters:
        -----------
        industry: 산업 이름
        top_k: 반환할 벤치마크 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.chain_store:
            logger.warning("  ⚠️  가치사슬 RAG 미구축")
            return []
        
        logger.info(f"[Observer] 가치사슬 검색")
        logger.info(f"  산업: {industry}")
        
        results = self.chain_store.similarity_search_with_score(
            industry,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 벤치마크 발견")
        for doc, score in results:
            industry_name = doc.metadata.get('industry', 'Unknown')
            logger.info(f"    - {industry_name} (유사도: {score:.2f})")
        
        return results
    
    def search_inefficiency(
        self,
        structure_description: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        비효율성 패턴 검색
        
        사용 시점:
        ----------
        관찰한 구조에서 비효율성을 찾을 때
        
        예시:
        -----
        Input: "3단계 유통, 각 20% 마진"
        Output: [중개 비효율 패턴, D2C 기회, ...]
        """
        if not self.structure_store:
            return []
        
        logger.info(f"[Observer] 비효율성 패턴 검색")
        
        results = self.structure_store.similarity_search_with_score(
            structure_description,
            k=top_k,
            filter={"type": "inefficiency"}
        )
        
        return results
    
    def analyze_structure_with_rag(
        self,
        observations: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        RAG 기반 구조 분석
        
        프로세스:
        ---------
        1. 구조 패턴 검색 → 유사 구조 파악
        2. 가치사슬 검색 → 벤치마크 참조
        3. 비효율성 검색 → 기회 영역
        
        Returns:
        --------
        구조 분석 결과 + 패턴 매칭 + 벤치마크
        """
        logger.info(f"[Observer] RAG 기반 구조 분석")
        
        result = {
            'structure_patterns': [],
            'value_chain_benchmarks': [],
            'inefficiencies': []
        }
        
        # 1. 구조 패턴
        patterns = self.search_structure_pattern(observations, top_k=2)
        if patterns:
            result['structure_patterns'] = [
                {
                    'pattern': doc.metadata.get('structure_type'),
                    'description': doc.page_content[:200],
                    'confidence': score
                }
                for doc, score in patterns
            ]
        
        # 2. 가치사슬
        chains = self.search_value_chain(industry, top_k=2)
        if chains:
            result['value_chain_benchmarks'] = [
                {
                    'industry': doc.metadata.get('industry'),
                    'chain': doc.metadata.get('chain_structure'),
                    'margins': doc.metadata.get('margins'),
                    'confidence': score
                }
                for doc, score in chains
            ]
        
        # 3. 비효율성
        inefficiencies = self.search_inefficiency(observations, top_k=2)
        if inefficiencies:
            result['inefficiencies'] = [
                {
                    'pattern': doc.metadata.get('inefficiency_type'),
                    'opportunity': doc.page_content[:150],
                    'confidence': score
                }
                for doc, score in inefficiencies
            ]
        
        logger.info("  ✅ RAG 기반 분석 완료")
        return result


# Observer RAG 인스턴스 (싱글톤)
_observer_rag_instance = None

def get_observer_rag() -> ObserverRAG:
    """Observer RAG 싱글톤 인스턴스 반환"""
    global _observer_rag_instance
    if _observer_rag_instance is None:
        _observer_rag_instance = ObserverRAG()
    return _observer_rag_instance

