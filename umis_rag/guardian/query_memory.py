"""
QueryMemory: 순환 감지 시스템

Guardian (Stewart)의 순환 질문/작업 감지 기능

schema_registry.yaml 준수:
- memory_id: MEM-xxxxxxxx
- query_embedding: 3072 dim
- repetition_count: 반복 횟수
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class QueryMemory:
    """
    순환 질문/작업 감지 시스템
    
    기능:
    - 과거 질문 저장
    - 유사 질문 감지 (embedding similarity)
    - 반복 횟수 추적
    - 순환 경고
    
    사용:
    -----
    memory = QueryMemory()
    
    # 질문 저장 및 순환 체크
    is_circular, info = memory.check_and_store("음악 스트리밍 분석해줘")
    
    if is_circular:
        print(f"⚠️ 순환 감지: {info['repetition_count']}번째 반복")
    """
    
    def __init__(
        self,
        collection_name: str = "query_memory",
        similarity_threshold: float = 0.90,
        repetition_threshold: int = 3
    ):
        """
        Args:
            collection_name: Chroma collection 이름
            similarity_threshold: 유사 질문 판단 임계값 (0.90 = 매우 유사)
            repetition_threshold: 순환 경고 반복 횟수 (3회)
        """
        logger.info(f"QueryMemory 초기화: {collection_name}")
        
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.repetition_threshold = repetition_threshold
        
        # Embeddings 초기화
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Vector Store 초기화
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(settings.chroma_persist_dir)
        )
        
        current_count = self.vectorstore._collection.count()
        logger.info(f"  ✅ QueryMemory 로드: {current_count}개 쿼리")
        logger.info(f"  ✅ 유사도 임계값: {similarity_threshold}")
        logger.info(f"  ✅ 반복 임계값: {repetition_threshold}회")
    
    def generate_memory_id(self, query_text: str, timestamp: str = None) -> str:
        """
        Memory ID 생성 (MEM-xxxxxxxx)
        
        Args:
            query_text: 질문 텍스트
            timestamp: 타임스탬프 (선택, 없으면 현재 시간)
        
        Returns:
            MEM-xxx 형식의 ID
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # query + timestamp를 해시
        hash_input = f"{query_text}_{timestamp}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        
        return f"MEM-{hash_hex}"
    
    def extract_topic(self, query_text: str) -> str:
        """
        질문에서 주제 추출 (간단한 버전)
        
        Args:
            query_text: 질문 텍스트
        
        Returns:
            추출된 주제
        """
        # 간단한 키워드 추출 (향후 LLM 강화 가능)
        keywords = []
        
        # 자주 나오는 도메인 키워드
        domain_keywords = [
            '음악', '스트리밍', '구독', '플랫폼', '광고',
            '프랜차이즈', 'D2C', '라이센스', 'freemium',
            '혁신', 'disruption', '저가', '채널', '경험'
        ]
        
        for keyword in domain_keywords:
            if keyword.lower() in query_text.lower():
                keywords.append(keyword)
        
        if keywords:
            return ', '.join(keywords[:3])
        else:
            # 첫 20자
            return query_text[:20] + '...' if len(query_text) > 20 else query_text
    
    def check_similarity(
        self,
        query_text: str,
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        유사한 과거 질문 검색
        
        Args:
            query_text: 현재 질문
            top_k: 검색할 개수
        
        Returns:
            [(Document, similarity_score), ...]
        """
        if self.vectorstore._collection.count() == 0:
            return []
        
        results = self.vectorstore.similarity_search_with_score(
            query_text,
            k=top_k
        )
        
        return results
    
    def check_and_store(
        self,
        query_text: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        순환 체크 및 질문 저장
        
        Args:
            query_text: 질문 텍스트
        
        Returns:
            (is_circular, info)
            - is_circular: 순환 여부
            - info: 상세 정보 (repetition_count, similar_queries, ...)
        """
        logger.info(f"[QueryMemory] 순환 체크: {query_text[:50]}...")
        
        # 1. 유사 질문 검색
        similar_queries = self.check_similarity(query_text, top_k=3)
        
        is_circular = False
        repetition_count = 1
        similar_query_info = []
        
        # 2. 유사도 체크
        for doc, score in similar_queries:
            # 유사도가 임계값 이상이면 순환 가능성
            if score >= self.similarity_threshold:
                metadata = doc.metadata
                past_count = metadata.get('repetition_count', 1)
                repetition_count = past_count + 1
                
                similar_query_info.append({
                    'query': doc.page_content,
                    'similarity': score,
                    'past_count': past_count,
                    'memory_id': metadata.get('memory_id')
                })
                
                # 반복 횟수가 임계값 이상이면 순환
                if repetition_count >= self.repetition_threshold:
                    is_circular = True
                
                logger.warning(f"  ⚠️  유사 질문 발견: {score:.3f} (반복 {repetition_count}회)")
                break
        
        # 3. 메모리에 저장
        memory_id = self.generate_memory_id(query_text)
        topic = self.extract_topic(query_text)
        timestamp = datetime.now().isoformat()
        
        metadata = {
            'memory_id': memory_id,
            'query_topic': topic,
            'repetition_count': repetition_count,
            'version': '1.0.0',
            'created_at': timestamp
        }
        
        # Chroma에 저장
        self.vectorstore.add_texts(
            texts=[query_text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        logger.info(f"  ✅ QueryMemory 저장: {memory_id} (반복 {repetition_count}회)")
        
        # 4. 결과 반환
        info = {
            'memory_id': memory_id,
            'repetition_count': repetition_count,
            'topic': topic,
            'similar_queries': similar_query_info,
            'is_first_time': repetition_count == 1
        }
        
        return is_circular, info
    
    def get_query_history(
        self,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        질문 히스토리 조회
        
        Args:
            topic: 특정 주제만 (선택)
            limit: 최대 개수
        
        Returns:
            질문 히스토리 리스트
        """
        if topic:
            # 주제 필터 검색
            results = self.vectorstore.similarity_search(
                topic,
                k=limit,
                filter={'query_topic': topic}
            )
        else:
            # 전체 검색
            results = self.vectorstore.similarity_search(
                "",
                k=limit
            )
        
        history = []
        for doc in results:
            history.append({
                'query': doc.page_content,
                'topic': doc.metadata.get('query_topic'),
                'repetition_count': doc.metadata.get('repetition_count', 1),
                'created_at': doc.metadata.get('created_at')
            })
        
        return history
    
    def get_stats(self) -> Dict[str, Any]:
        """
        QueryMemory 통계
        
        Returns:
            통계 정보
        """
        total = self.vectorstore._collection.count()
        
        # 모든 문서 가져오기 (임시로 큰 k 값 사용)
        if total > 0:
            all_docs = self.vectorstore.similarity_search("", k=min(total, 100))
            
            # 반복 횟수별 통계
            repetition_counts = {}
            topics = {}
            
            for doc in all_docs:
                rep_count = doc.metadata.get('repetition_count', 1)
                topic = doc.metadata.get('query_topic', 'unknown')
                
                repetition_counts[rep_count] = repetition_counts.get(rep_count, 0) + 1
                topics[topic] = topics.get(topic, 0) + 1
            
            return {
                'total_queries': total,
                'repetition_distribution': repetition_counts,
                'top_topics': sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5],
                'circular_warnings': sum(1 for k in repetition_counts if k >= self.repetition_threshold)
            }
        
        return {
            'total_queries': 0,
            'repetition_distribution': {},
            'top_topics': [],
            'circular_warnings': 0
        }
    
    def clear_memory(self) -> bool:
        """
        ⚠️ 모든 메모리 삭제 (개발용)
        
        Returns:
            성공 여부
        """
        try:
            logger.warning("🗑️ QueryMemory 전체 삭제...")
            # Collection 삭제 후 재생성
            self.vectorstore._client.delete_collection(self.collection_name)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.warning("✅ QueryMemory 삭제 완료")
            return True
        except Exception as e:
            logger.error(f"❌ QueryMemory 삭제 실패: {e}")
            return False


# 편의 함수
def check_circular_query(query_text: str) -> Tuple[bool, Dict[str, Any]]:
    """
    편의 함수: 빠르게 순환 체크
    
    Args:
        query_text: 질문 텍스트
    
    Returns:
        (is_circular, info)
    """
    memory = QueryMemory()
    return memory.check_and_store(query_text)


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("QueryMemory 테스트")
    print("=" * 60)
    
    memory = QueryMemory()
    
    # 테스트 쿼리들
    queries = [
        "음악 스트리밍 구독 서비스 시장 분석해줘",
        "음악 스트리밍 시장에 대해 알려줘",  # 유사
        "음악 스트리밍 구독 모델 분석",      # 유사
        "반려동물 구독 서비스 분석해줘",      # 다름
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")
        
        is_circular, info = memory.check_and_store(query)
        
        print(f"순환 여부: {is_circular}")
        print(f"반복 횟수: {info['repetition_count']}")
        print(f"주제: {info['topic']}")
        
        if info['similar_queries']:
            print(f"\n유사 질문:")
            for sq in info['similar_queries']:
                print(f"  - {sq['query'][:50]}... (유사도: {sq['similarity']:.3f})")
    
    # 통계
    print(f"\n{'='*60}")
    print("통계")
    print(f"{'='*60}")
    
    stats = memory.get_stats()
    print(f"총 쿼리: {stats['total_queries']}")
    print(f"순환 경고: {stats['circular_warnings']}")
    print(f"\n반복 분포:")
    for count, num in sorted(stats['repetition_distribution'].items()):
        print(f"  {count}회: {num}개")

