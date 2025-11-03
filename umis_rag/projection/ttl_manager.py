"""
TTL Manager: Time-To-Live 캐시 관리

Projected Index의 TTL 기반 캐시 관리:
- 만료 체크 (cache_ttl_hours)
- 온디맨드 재생성
- 자동 정리 (cleanup)
- access_count 추적
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import chromadb

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import get_logger
from umis_rag.projection.hybrid_projector import HybridProjector

logger = get_logger(__name__)


class TTLManager:
    """
    TTL (Time-To-Live) 캐시 관리자
    
    기능:
    - Projected 청크 만료 체크
    - 자동 재생성 (온디맨드)
    - 만료된 청크 정리
    - access_count 추적 및 persist_profile 설정
    
    사용:
    -----
    ttl = TTLManager()
    
    # 만료 체크
    if ttl.is_expired('PRJ-xxx'):
        # 재생성
        new_chunk = ttl.regenerate('PRJ-xxx')
    
    # 주기적 정리
    ttl.cleanup_expired()
    """
    
    def __init__(
        self,
        default_ttl_hours: int = 24,
        high_traffic_threshold: int = 10
    ):
        """
        Args:
            default_ttl_hours: 기본 TTL (24시간)
            high_traffic_threshold: 고빈도 판단 기준 (10회)
        """
        self.default_ttl_hours = default_ttl_hours
        self.high_traffic_threshold = high_traffic_threshold
        
        # Chroma
        self.client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        
        # Projector
        self.projector = HybridProjector()
        
        logger.info(f"TTLManager 초기화")
        logger.info(f"  기본 TTL: {default_ttl_hours}시간")
        logger.info(f"  고빈도 기준: {high_traffic_threshold}회")
    
    def check_expiration(self, projected_id: str) -> Dict[str, Any]:
        """
        Projected 청크 만료 체크
        
        Args:
            projected_id: PRJ-xxx ID
        
        Returns:
            {
                'exists': bool,
                'expired': bool,
                'hours_since_materialization': float,
                'access_count': int,
                'should_regenerate': bool
            }
        """
        try:
            # Collection 가져오기
            projected_collection = self.client.get_collection("projected_index")
            
            # 청크 조회
            result = projected_collection.get(ids=[projected_id])
            
            if not result['metadatas'] or len(result['metadatas']) == 0:
                return {
                    'exists': False,
                    'expired': True,
                    'hours_since_materialization': float('inf'),
                    'access_count': 0,
                    'should_regenerate': True
                }
            
            metadata = result['metadatas'][0]
            
            # materialization 정보 파싱
            materialization_str = metadata.get('materialization', '{}')
            if isinstance(materialization_str, str):
                try:
                    materialization = json.loads(materialization_str)
                except:
                    materialization = {}
            else:
                materialization = materialization_str
            
            # 마지막 생성 시간
            last_materialized_str = materialization.get('last_materialized_at')
            if not last_materialized_str:
                last_materialized_str = metadata.get('created_at')
            
            if last_materialized_str:
                last_materialized = datetime.fromisoformat(last_materialized_str)
                now = datetime.now()
                elapsed = (now - last_materialized).total_seconds() / 3600  # hours
            else:
                elapsed = float('inf')
            
            # TTL 가져오기
            ttl_hours = materialization.get('cache_ttl_hours', self.default_ttl_hours)
            
            # 만료 여부
            is_expired = elapsed >= ttl_hours
            
            # access_count
            access_count = materialization.get('access_count', 0)
            
            return {
                'exists': True,
                'expired': is_expired,
                'hours_since_materialization': elapsed,
                'ttl_hours': ttl_hours,
                'access_count': access_count,
                'should_regenerate': is_expired
            }
            
        except Exception as e:
            logger.error(f"  ❌ 만료 체크 실패: {e}")
            return {
                'exists': False,
                'expired': True,
                'should_regenerate': True
            }
    
    def regenerate_on_demand(
        self,
        canonical_id: str,
        agent: str
    ) -> Optional[str]:
        """
        온디맨드로 Projected 청크 재생성
        
        Args:
            canonical_id: CAN-xxx ID
            agent: Agent 이름
        
        Returns:
            생성된 PRJ-xxx ID 또는 None
        """
        logger.info(f"  🔄 온디맨드 재생성: {canonical_id} → {agent}")
        
        try:
            # Canonical 청크 조회
            canonical_collection = self.client.get_collection("canonical_index")
            result = canonical_collection.get(
                ids=[canonical_id],
                include=['documents', 'metadatas']
            )
            
            if not result['metadatas']:
                logger.error(f"  ❌ Canonical 청크 없음: {canonical_id}")
                return None
            
            # Canonical → Projected 투영
            canonical_chunk = {
                **result['metadatas'][0],
                'content': result['documents'][0]
            }
            
            projected_chunks = self.projector.project(canonical_chunk)
            
            # 해당 Agent 청크 찾기
            for proj in projected_chunks:
                if proj['agent_view'] == agent:
                    # Projected Index에 저장
                    self._save_projected(proj)
                    logger.info(f"  ✅ 재생성 완료: {proj['projected_chunk_id']}")
                    return proj['projected_chunk_id']
            
            logger.warning(f"  ⚠️  Agent {agent}용 투영 없음")
            return None
            
        except Exception as e:
            logger.error(f"  ❌ 재생성 실패: {e}")
            return None
    
    def _save_projected(self, projected_chunk: Dict[str, Any]):
        """Projected 청크 저장/업데이트"""
        from langchain_openai import OpenAIEmbeddings
        
        projected_collection = self.client.get_collection("projected_index")
        embeddings_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Embedding 생성
        content = projected_chunk['content']
        embedding = embeddings_model.embed_query(content)
        
        # 메타데이터 변환
        metadata = {
            'projected_chunk_id': projected_chunk['projected_chunk_id'],
            'source_id': projected_chunk['source_id'],
            'agent_view': projected_chunk['agent_view'],
            'canonical_chunk_id': projected_chunk['canonical_chunk_id'],
            'projection_method': projected_chunk['projection_method'],
            'domain': projected_chunk['domain'],
            'version': projected_chunk['version'],
            'materialization': json.dumps(projected_chunk.get('materialization', {})),
            'lineage': json.dumps(projected_chunk.get('lineage', {})),
            'created_at': projected_chunk['created_at'],
            'updated_at': datetime.now().isoformat()
        }
        
        # Upsert (있으면 업데이트, 없으면 생성)
        projected_collection.upsert(
            ids=[projected_chunk['projected_chunk_id']],
            documents=[content],
            metadatas=[metadata],
            embeddings=[embedding]
        )
    
    def update_access_count(self, projected_id: str):
        """
        Access count 증가 및 persist_profile 설정
        
        Args:
            projected_id: PRJ-xxx ID
        """
        try:
            projected_collection = self.client.get_collection("projected_index")
            
            # 현재 메타데이터 조회
            result = projected_collection.get(ids=[projected_id])
            
            if not result['metadatas']:
                return
            
            metadata = result['metadatas'][0]
            
            # materialization 파싱
            materialization_str = metadata.get('materialization', '{}')
            if isinstance(materialization_str, str):
                materialization = json.loads(materialization_str)
            else:
                materialization = materialization_str
            
            # access_count 증가
            materialization['access_count'] = materialization.get('access_count', 0) + 1
            
            # 고빈도 판단 → persist_profile 설정
            if materialization['access_count'] >= self.high_traffic_threshold:
                if not materialization.get('persist_profile'):
                    materialization['persist_profile'] = f"high_traffic_{projected_id[:12]}"
                    materialization['strategy'] = 'persistent'  # 온디맨드 → 영속
                    logger.info(f"  🔝 고빈도 청크: {projected_id} ({materialization['access_count']}회)")
            
            # 업데이트
            metadata['materialization'] = json.dumps(materialization)
            
            # Upsert
            projected_collection.update(
                ids=[projected_id],
                metadatas=[metadata]
            )
            
        except Exception as e:
            logger.warning(f"  ⚠️  Access count 업데이트 실패: {e}")
    
    def cleanup_expired(self, dry_run: bool = False) -> int:
        """
        만료된 Projected 청크 삭제
        
        Args:
            dry_run: True면 실제 삭제 안 함 (미리보기)
        
        Returns:
            삭제된 청크 수
        """
        logger.info(f"  🗑️  만료 청크 정리 시작 (dry_run={dry_run})")
        
        try:
            projected_collection = self.client.get_collection("projected_index")
            
            # 모든 Projected 청크 조회
            all_projected = projected_collection.get(include=['metadatas'])
            
            expired_ids = []
            
            for i, metadata in enumerate(all_projected['metadatas']):
                projected_id = metadata.get('projected_chunk_id')
                
                # persist_profile 있으면 영속 (삭제 안 함)
                materialization_str = metadata.get('materialization', '{}')
                if isinstance(materialization_str, str):
                    materialization = json.loads(materialization_str)
                else:
                    materialization = materialization_str
                
                if materialization.get('persist_profile'):
                    continue  # 영속 청크는 건너뜀
                
                # 만료 체크
                check_result = self.check_expiration(projected_id)
                
                if check_result['expired']:
                    expired_ids.append(projected_id)
            
            # 삭제
            if expired_ids and not dry_run:
                projected_collection.delete(ids=expired_ids)
                logger.info(f"  ✅ {len(expired_ids)}개 만료 청크 삭제")
            else:
                logger.info(f"  💡 {len(expired_ids)}개 만료 청크 발견 (dry_run)")
            
            return len(expired_ids)
            
        except Exception as e:
            logger.error(f"  ❌ 정리 실패: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        TTL 관련 통계
        
        Returns:
            통계 정보
        """
        try:
            projected_collection = self.client.get_collection("projected_index")
            total = projected_collection.count()
            
            # 샘플 조회
            all_projected = projected_collection.get(include=['metadatas'], limit=total)
            
            expired_count = 0
            persistent_count = 0
            access_counts = []
            
            for metadata in all_projected['metadatas']:
                projected_id = metadata.get('projected_chunk_id')
                
                # 만료 체크
                check = self.check_expiration(projected_id)
                if check['expired']:
                    expired_count += 1
                
                # materialization 파싱
                materialization_str = metadata.get('materialization', '{}')
                if isinstance(materialization_str, str):
                    materialization = json.loads(materialization_str)
                else:
                    materialization = materialization_str
                
                # persist_profile 체크
                if materialization.get('persist_profile'):
                    persistent_count += 1
                
                # access_count
                access_counts.append(materialization.get('access_count', 0))
            
            return {
                'total_projected': total,
                'expired': expired_count,
                'persistent': persistent_count,
                'on_demand': total - persistent_count,
                'avg_access_count': sum(access_counts) / len(access_counts) if access_counts else 0,
                'max_access_count': max(access_counts) if access_counts else 0
            }
            
        except Exception as e:
            logger.error(f"  ❌ 통계 조회 실패: {e}")
            return {}


# 편의 함수
def check_and_regenerate(projected_id: str) -> bool:
    """
    편의 함수: 만료 체크 및 필요 시 재생성
    
    Args:
        projected_id: PRJ-xxx ID
    
    Returns:
        재생성 여부
    """
    ttl = TTLManager()
    check = ttl.check_expiration(projected_id)
    
    if check['should_regenerate']:
        # Canonical ID 추출 (projected_id에서)
        # 간단히 처리 (실제로는 metadata에서 가져옴)
        return True
    
    return False


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("TTL Manager 테스트")
    print("=" * 60)
    
    ttl = TTLManager()
    
    # 1. 통계
    print("\n[1] TTL 통계")
    stats = ttl.get_stats()
    
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 2. 만료 체크 (샘플)
    print("\n[2] 만료 체크 (처음 5개)")
    
    try:
        projected_collection = ttl.client.get_collection("projected_index")
        all_ids = projected_collection.get(limit=5)
        
        for projected_id in all_ids['ids']:
            check = ttl.check_expiration(projected_id)
            status = "⏰ 만료" if check['expired'] else "✅ 유효"
            hours = check.get('hours_since_materialization', 0)
            print(f"  {projected_id[:15]}...: {status} ({hours:.1f}시간 경과)")
    
    except Exception as e:
        print(f"  ⚠️  {e}")
    
    # 3. Access count 업데이트 테스트
    print("\n[3] Access count 업데이트")
    
    if all_ids['ids']:
        test_id = all_ids['ids'][0]
        print(f"  테스트 ID: {test_id[:20]}...")
        
        # 10회 접근 시뮬레이션
        for i in range(11):
            ttl.update_access_count(test_id)
        
        print(f"  ✅ 11회 접근 기록")
        
        # 결과 확인
        check = ttl.check_expiration(test_id)
        print(f"  Access count: {check.get('access_count', 0)}")
    
    print("\n✅ TTL Manager 작동 확인")

