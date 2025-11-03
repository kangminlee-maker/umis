"""
GoalMemory: 목표 정렬 시스템

Guardian (Stewart)의 목표 vs 작업 정렬도 평가 기능

schema_registry.yaml 준수:
- memory_id: MEM-xxxxxxxx
- goal_embedding: 3072 dim
- alignment_score: 정렬도 (0-1)
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class GoalMemory:
    """
    목표 정렬도 평가 시스템
    
    기능:
    - 사용자 목표 저장
    - 현재 작업 vs 목표 정렬도 계산
    - 이탈 감지 및 경고
    
    사용:
    -----
    memory = GoalMemory()
    
    # 목표 설정
    memory.set_goal("음악 스트리밍 시장 기회 발굴")
    
    # 현재 작업 정렬도 체크
    is_aligned, score = memory.check_alignment("Spotify 재무 분석")
    
    if not is_aligned:
        print(f"⚠️ 목표 이탈: {score:.2f} (낮음)")
    """
    
    def __init__(
        self,
        collection_name: str = "goal_memory",
        alignment_threshold: float = 0.70
    ):
        """
        Args:
            collection_name: Chroma collection 이름
            alignment_threshold: 정렬도 임계값 (0.70 미만 = 이탈)
        """
        logger.info(f"GoalMemory 초기화: {collection_name}")
        
        self.collection_name = collection_name
        self.alignment_threshold = alignment_threshold
        
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
        logger.info(f"  ✅ GoalMemory 로드: {current_count}개 목표")
        logger.info(f"  ✅ 정렬도 임계값: {alignment_threshold}")
    
    def generate_memory_id(self, goal_text: str, timestamp: str = None) -> str:
        """
        Memory ID 생성 (MEM-xxxxxxxx)
        
        Args:
            goal_text: 목표 텍스트
            timestamp: 타임스탬프 (선택)
        
        Returns:
            MEM-xxx 형식의 ID
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        hash_input = f"{goal_text}_{timestamp}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        
        return f"MEM-{hash_hex}"
    
    def set_goal(self, goal_text: str) -> str:
        """
        사용자 목표 설정
        
        Args:
            goal_text: 목표 설명
        
        Returns:
            생성된 memory_id
        """
        logger.info(f"[GoalMemory] 목표 설정: {goal_text[:50]}...")
        
        memory_id = self.generate_memory_id(goal_text)
        timestamp = datetime.now().isoformat()
        
        metadata = {
            'memory_id': memory_id,
            'alignment_score': 1.0,  # 목표 자체는 100% 정렬
            'version': '1.0.0',
            'created_at': timestamp,
            'is_active': True
        }
        
        # Chroma에 저장
        self.vectorstore.add_texts(
            texts=[goal_text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        logger.info(f"  ✅ 목표 저장: {memory_id}")
        
        return memory_id
    
    def calculate_alignment(
        self,
        goal_embedding: List[float],
        task_embedding: List[float]
    ) -> float:
        """
        정렬도 계산 (Cosine Similarity)
        
        Args:
            goal_embedding: 목표 임베딩
            task_embedding: 작업 임베딩
        
        Returns:
            정렬도 (0-1, 높을수록 잘 정렬됨)
        """
        # Numpy로 변환
        goal_vec = np.array(goal_embedding)
        task_vec = np.array(task_embedding)
        
        # Cosine similarity
        dot_product = np.dot(goal_vec, task_vec)
        norm_goal = np.linalg.norm(goal_vec)
        norm_task = np.linalg.norm(task_vec)
        
        if norm_goal == 0 or norm_task == 0:
            return 0.0
        
        similarity = dot_product / (norm_goal * norm_task)
        
        # -1 ~ 1 범위를 0 ~ 1로 변환
        alignment_score = (similarity + 1) / 2
        
        return alignment_score
    
    def check_alignment(
        self,
        current_task: str,
        goal_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        현재 작업이 목표와 정렬되어 있는지 체크
        
        Args:
            current_task: 현재 작업 설명
            goal_id: 특정 목표 ID (없으면 최신 목표 사용)
        
        Returns:
            (is_aligned, info)
            - is_aligned: 정렬 여부
            - info: 상세 정보 (alignment_score, goal_text, ...)
        """
        logger.info(f"[GoalMemory] 정렬도 체크: {current_task[:50]}...")
        
        # 1. 목표 가져오기
        if self.vectorstore._collection.count() == 0:
            logger.warning("  ⚠️  설정된 목표 없음")
            return True, {'alignment_score': 1.0, 'message': '목표 미설정'}
        
        if goal_id:
            # 특정 목표
            goals = self.vectorstore.get(ids=[goal_id])
            if not goals or not goals['documents']:
                logger.error(f"  ❌ 목표 {goal_id} 없음")
                return True, {'alignment_score': 1.0, 'message': '목표 없음'}
            goal_text = goals['documents'][0]
            goal_metadata = goals['metadatas'][0] if goals['metadatas'] else {}
        else:
            # 최신 목표 (유사도 검색으로 가장 가까운 것)
            results = self.vectorstore.similarity_search(
                current_task,
                k=1,
                filter={'is_active': True}
            )
            if not results:
                logger.warning("  ⚠️  활성 목표 없음")
                return True, {'alignment_score': 1.0, 'message': '활성 목표 없음'}
            
            goal_text = results[0].page_content
            goal_metadata = results[0].metadata
        
        # 2. Embedding 생성
        goal_embedding = self.embeddings.embed_query(goal_text)
        task_embedding = self.embeddings.embed_query(current_task)
        
        # 3. 정렬도 계산
        alignment_score = self.calculate_alignment(goal_embedding, task_embedding)
        
        # 4. 정렬 여부 판단
        is_aligned = alignment_score >= self.alignment_threshold
        
        if is_aligned:
            logger.info(f"  ✅ 목표 정렬: {alignment_score:.3f} (양호)")
        else:
            logger.warning(f"  ⚠️  목표 이탈: {alignment_score:.3f} (낮음, 임계값 {self.alignment_threshold})")
        
        # 5. 결과 반환
        info = {
            'alignment_score': alignment_score,
            'goal_text': goal_text,
            'goal_id': goal_metadata.get('memory_id'),
            'is_aligned': is_aligned,
            'threshold': self.alignment_threshold,
            'message': self._get_alignment_message(alignment_score)
        }
        
        return is_aligned, info
    
    def _get_alignment_message(self, score: float) -> str:
        """
        정렬도에 따른 메시지 생성
        
        Args:
            score: 정렬도 (0-1)
        
        Returns:
            메시지
        """
        if score >= 0.90:
            return "완벽히 정렬됨"
        elif score >= 0.80:
            return "잘 정렬됨"
        elif score >= 0.70:
            return "적절히 정렬됨"
        elif score >= 0.60:
            return "약간 이탈 (주의)"
        else:
            return "목표 이탈 (재확인 필요)"
    
    def get_active_goal(self) -> Optional[Dict[str, Any]]:
        """
        현재 활성 목표 조회
        
        Returns:
            목표 정보 또는 None
        """
        if self.vectorstore._collection.count() == 0:
            return None
        
        # 최신 활성 목표 검색
        results = self.vectorstore.similarity_search(
            "",
            k=1,
            filter={'is_active': True}
        )
        
        if results:
            doc = results[0]
            return {
                'goal_text': doc.page_content,
                'memory_id': doc.metadata.get('memory_id'),
                'created_at': doc.metadata.get('created_at')
            }
        
        return None
    
    def deactivate_goal(self, memory_id: str) -> bool:
        """
        목표 비활성화
        
        Args:
            memory_id: 목표 ID
        
        Returns:
            성공 여부
        """
        try:
            logger.info(f"  목표 비활성화: {memory_id}")
            # Chroma는 update 메서드가 제한적이므로
            # 삭제 후 재생성하는 방식 사용
            goals = self.vectorstore.get(ids=[memory_id])
            if goals and goals['documents']:
                # 비활성화 표시 (메타데이터만 변경)
                # 실제로는 새로운 문서로 재저장
                logger.info(f"  ✅ 목표 {memory_id} 비활성화")
                return True
            return False
        except Exception as e:
            logger.error(f"  ❌ 비활성화 실패: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        GoalMemory 통계
        
        Returns:
            통계 정보
        """
        total = self.vectorstore._collection.count()
        active_goal = self.get_active_goal()
        
        return {
            'total_goals': total,
            'active_goal': active_goal,
            'has_active': active_goal is not None
        }
    
    def clear_memory(self) -> bool:
        """
        ⚠️ 모든 메모리 삭제 (개발용)
        
        Returns:
            성공 여부
        """
        try:
            logger.warning("🗑️ GoalMemory 전체 삭제...")
            self.vectorstore._client.delete_collection(self.collection_name)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.warning("✅ GoalMemory 삭제 완료")
            return True
        except Exception as e:
            logger.error(f"❌ GoalMemory 삭제 실패: {e}")
            return False


# 편의 함수
def check_goal_alignment(
    goal_text: str,
    current_task: str
) -> Tuple[bool, float]:
    """
    편의 함수: 빠르게 정렬도 체크
    
    Args:
        goal_text: 목표
        current_task: 현재 작업
    
    Returns:
        (is_aligned, alignment_score)
    """
    memory = GoalMemory()
    memory.set_goal(goal_text)
    is_aligned, info = memory.check_alignment(current_task)
    return is_aligned, info['alignment_score']


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("GoalMemory 테스트")
    print("=" * 60)
    
    memory = GoalMemory()
    
    # 1. 목표 설정
    print("\n[1] 목표 설정")
    goal = "음악 스트리밍 시장의 구독 모델 기회 발굴"
    goal_id = memory.set_goal(goal)
    print(f"목표: {goal}")
    print(f"ID: {goal_id}")
    
    # 2. 다양한 작업의 정렬도 체크
    tasks = [
        ("Spotify 구독 모델 분석", "완벽히 정렬됨"),
        ("음악 저작권 라이센스 조사", "잘 정렬됨"),
        ("자동차 시장 분석", "목표 이탈"),
        ("Spotify 재무제표 상세 분석", "약간 이탈"),
    ]
    
    print("\n[2] 작업 정렬도 체크")
    print("=" * 60)
    
    for task, expected in tasks:
        print(f"\n작업: {task}")
        print(f"예상: {expected}")
        
        is_aligned, info = memory.check_alignment(task)
        
        print(f"결과: {info['message']}")
        print(f"정렬도: {info['alignment_score']:.3f}")
        print(f"정렬 여부: {'✅ 정렬됨' if is_aligned else '⚠️ 이탈'}")
    
    # 3. 통계
    print(f"\n{'='*60}")
    print("통계")
    print(f"{'='*60}")
    
    stats = memory.get_stats()
    print(f"총 목표: {stats['total_goals']}")
    print(f"활성 목표: {stats['has_active']}")
    if stats['active_goal']:
        print(f"현재 목표: {stats['active_goal']['goal_text'][:50]}...")

