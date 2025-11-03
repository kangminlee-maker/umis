"""
RAE (Rational Agent Evaluation) Memory

Guardian의 과거 평가 이력 저장 및 재사용

config/schema_registry.yaml 준수:
- rae_id: RAE-xxxxxxxx
- deliverable_id: 평가 대상 ID
- grade: A/B/C/D
- rationale: 평가 사유
- evidence_ids: 근거 청크
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


class RAEMemory:
    """
    RAE (Rational Agent Evaluation) Memory
    
    기능:
    - Guardian 평가 이력 저장
    - 유사 케이스 검색 및 재사용
    - 평가 일관성 보장
    
    사용:
    -----
    rae = RAEMemory()
    
    # 평가 저장
    rae.store_evaluation(
        deliverable_id="OPP-001",
        grade="A",
        rationale="명확한 근거와 실행 가능성",
        evidence_ids=["CAN-amazon-001"]
    )
    
    # 유사 케이스 검색
    similar = rae.find_similar_evaluations("음악 스트리밍 구독 기회")
    # → 과거 평가를 참고하여 일관성 유지
    """
    
    def __init__(
        self,
        collection_name: str = "rae_index",
        similarity_threshold: float = 0.85
    ):
        """
        Args:
            collection_name: Chroma collection 이름
            similarity_threshold: 유사 케이스 판단 임계값
        """
        logger.info(f"RAEMemory 초기화: {collection_name}")
        
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        
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
        logger.info(f"  ✅ RAEMemory 로드: {current_count}개 평가")
        logger.info(f"  ✅ 유사도 임계값: {similarity_threshold}")
    
    def generate_rae_id(
        self,
        deliverable_id: str,
        timestamp: str = None
    ) -> str:
        """
        RAE ID 생성 (RAE-xxxxxxxx)
        
        Args:
            deliverable_id: 산출물 ID
            timestamp: 타임스탬프
        
        Returns:
            RAE-xxx 형식의 ID
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        hash_input = f"{deliverable_id}_{timestamp}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        
        return f"RAE-{hash_hex}"
    
    def store_evaluation(
        self,
        deliverable_id: str,
        deliverable_content: str,
        grade: str,
        rationale: str,
        evidence_ids: List[str],
        agent_type: Optional[str] = None
    ) -> str:
        """
        평가 이력 저장
        
        Args:
            deliverable_id: 산출물 ID (OPP-001, MRS-001 등)
            deliverable_content: 산출물 내용 (요약)
            grade: 평가 등급 (A/B/C/D)
            rationale: 평가 사유
            evidence_ids: 근거 청크 ID 리스트
            agent_type: Agent 유형 (explorer, quantifier 등)
        
        Returns:
            생성된 rae_id
        """
        logger.info(f"[RAEMemory] 평가 저장: {deliverable_id} → {grade}")
        
        rae_id = self.generate_rae_id(deliverable_id)
        timestamp = datetime.now().isoformat()
        
        # 메타데이터 (Chroma는 list 직접 저장 불가 → JSON 문자열)
        import json
        
        metadata = {
            'rae_id': rae_id,
            'deliverable_id': deliverable_id,
            'grade': grade,
            'rationale': rationale,
            'evidence_ids': json.dumps(evidence_ids),  # list → JSON string
            'agent_type': agent_type or 'unknown',
            'version': '1.0.0',
            'created_at': timestamp
        }
        
        # Content: deliverable 요약 + rationale
        content = f"{deliverable_content}\n\n평가: {grade}\n사유: {rationale}"
        
        # Chroma에 저장
        self.vectorstore.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[rae_id]
        )
        
        logger.info(f"  ✅ RAE 저장: {rae_id}")
        
        return rae_id
    
    def find_similar_evaluations(
        self,
        deliverable_content: str,
        grade_filter: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        유사한 과거 평가 검색
        
        Args:
            deliverable_content: 현재 산출물 내용
            grade_filter: 특정 등급만 검색 (A/B/C/D, 선택)
            top_k: 검색할 개수
        
        Returns:
            유사 평가 리스트
        """
        logger.info(f"[RAEMemory] 유사 평가 검색: {deliverable_content[:50]}...")
        
        if self.vectorstore._collection.count() == 0:
            logger.warning("  ⚠️  저장된 평가 없음")
            return []
        
        # 필터 설정
        filter_dict = None
        if grade_filter:
            filter_dict = {'grade': grade_filter}
        
        # 유사도 검색
        results = self.vectorstore.similarity_search_with_score(
            deliverable_content,
            k=top_k,
            filter=filter_dict
        )
        
        import json
        
        similar_evals = []
        for doc, score in results:
            if score >= self.similarity_threshold:
                metadata = doc.metadata
                # JSON string → list 변환
                evidence_ids = metadata.get('evidence_ids', '[]')
                if isinstance(evidence_ids, str):
                    try:
                        evidence_ids = json.loads(evidence_ids)
                    except:
                        evidence_ids = []
                
                similar_evals.append({
                    'rae_id': metadata.get('rae_id'),
                    'deliverable_id': metadata.get('deliverable_id'),
                    'grade': metadata.get('grade'),
                    'rationale': metadata.get('rationale'),
                    'similarity': score,
                    'evidence_ids': evidence_ids
                })
                logger.info(f"  ✅ 유사 평가: {metadata.get('deliverable_id')} ({score:.3f}, 등급 {metadata.get('grade')})")
        
        if not similar_evals:
            logger.info("  💡 유사 평가 없음 (신규 케이스)")
        
        return similar_evals
    
    def get_evaluation_by_id(self, rae_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 평가 조회
        
        Args:
            rae_id: RAE ID
        
        Returns:
            평가 정보 또는 None
        """
        try:
            results = self.vectorstore.get(ids=[rae_id])
            
            if results and results['documents']:
                import json
                metadata = results['metadatas'][0] if results['metadatas'] else {}
                
                # JSON string → list 변환
                evidence_ids = metadata.get('evidence_ids', '[]')
                if isinstance(evidence_ids, str):
                    try:
                        evidence_ids = json.loads(evidence_ids)
                    except:
                        evidence_ids = []
                
                return {
                    'rae_id': rae_id,
                    'deliverable_id': metadata.get('deliverable_id'),
                    'grade': metadata.get('grade'),
                    'rationale': metadata.get('rationale'),
                    'evidence_ids': evidence_ids,
                    'created_at': metadata.get('created_at')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"  ❌ RAE 조회 실패: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        RAE Memory 통계
        
        Returns:
            통계 정보
        """
        total = self.vectorstore._collection.count()
        
        if total == 0:
            return {
                'total_evaluations': 0,
                'grade_distribution': {},
                'agent_distribution': {}
            }
        
        # 모든 평가 가져오기
        all_docs = self.vectorstore.similarity_search("", k=min(total, 100))
        
        # 등급 분포
        grade_dist = {}
        agent_dist = {}
        
        for doc in all_docs:
            grade = doc.metadata.get('grade', 'unknown')
            agent = doc.metadata.get('agent_type', 'unknown')
            
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
            agent_dist[agent] = agent_dist.get(agent, 0) + 1
        
        return {
            'total_evaluations': total,
            'grade_distribution': grade_dist,
            'agent_distribution': agent_dist
        }
    
    def clear_memory(self) -> bool:
        """
        ⚠️ 모든 메모리 삭제 (개발용)
        
        Returns:
            성공 여부
        """
        try:
            logger.warning("🗑️ RAEMemory 전체 삭제...")
            self.vectorstore._client.delete_collection(self.collection_name)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.warning("✅ RAEMemory 삭제 완료")
            return True
        except Exception as e:
            logger.error(f"❌ RAEMemory 삭제 실패: {e}")
            return False


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("RAE Memory 테스트")
    print("=" * 60)
    
    rae = RAEMemory()
    
    # 1. 평가 저장
    print("\n[1] 평가 저장")
    
    evaluations = [
        {
            'id': 'OPP-001',
            'content': '음악 스트리밍 구독 시장에서 Freemium + 광고 모델 기회',
            'grade': 'A',
            'rationale': '명확한 시장 근거, Spotify 유사 사례, 실행 가능성 높음',
            'evidence': ['CAN-spotify-001', 'CAN-youtube-002']
        },
        {
            'id': 'OPP-002',
            'content': '자동차 EV 충전소 플랫폼 비즈니스',
            'grade': 'B',
            'rationale': '시장 잠재력 크지만 초기 투자 부담',
            'evidence': ['CAN-tesla-001']
        },
        {
            'id': 'OPP-003',
            'content': '음악 스트리밍 플랫폼에서 아티스트 D2C 기회',
            'grade': 'A',
            'rationale': 'Spotify 유사 시장, 검증된 비즈니스 모델',
            'evidence': ['CAN-spotify-001', 'CAN-bandcamp-001']
        }
    ]
    
    for eval_data in evaluations:
        rae_id = rae.store_evaluation(
            deliverable_id=eval_data['id'],
            deliverable_content=eval_data['content'],
            grade=eval_data['grade'],
            rationale=eval_data['rationale'],
            evidence_ids=eval_data['evidence'],
            agent_type='explorer'
        )
        print(f"  {eval_data['id']}: {eval_data['grade']} → {rae_id}")
    
    # 2. 유사 평가 검색
    print("\n[2] 유사 평가 검색")
    
    new_opportunity = "음악 스트리밍에서 팟캐스트 광고 기회"
    similar = rae.find_similar_evaluations(new_opportunity)
    
    print(f"쿼리: {new_opportunity}")
    print(f"유사 평가: {len(similar)}개")
    
    for s in similar:
        print(f"  - {s['deliverable_id']}: {s['grade']} (유사도 {s['similarity']:.3f})")
        print(f"    사유: {s['rationale'][:50]}...")
    
    # 3. 통계
    print(f"\n[3] 통계")
    stats = rae.get_stats()
    print(f"총 평가: {stats['total_evaluations']}")
    print(f"등급 분포: {stats['grade_distribution']}")

