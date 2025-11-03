#!/usr/bin/env python3
"""
Projected Index 구축 (v3.0)

Canonical → Hybrid Projection → Projected Index
- ID: PRJ-xxxxxxxx
- TTL + 온디맨드
- Agent별 투영
- config/schema_registry.yaml 준수
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.projection.hybrid_projector import HybridProjector
from umis_rag.core.config import settings
from umis_rag.utils.logger import logger
import json
import chromadb
from langchain_openai import OpenAIEmbeddings


class ProjectedIndexBuilder:
    """
    Projected Index 빌더
    
    Canonical → Hybrid Projection → Projected
    - TTL + 온디맨드 기본
    - 고빈도만 영속화
    """
    
    def __init__(self):
        self.projector = HybridProjector()
        
        # Chroma
        self.client = chromadb.PersistentClient(path="data/chroma")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        logger.info("ProjectedIndexBuilder 초기화")
    
    def build(self):
        """Projected Index 전체 구축"""
        
        logger.info("🔨 Projected Index 구축 시작")
        
        # Canonical Index 로드
        canonical_collection = self.client.get_collection("canonical_index")
        
        # Projected Collection 생성
        try:
            self.client.delete_collection("projected_index")
        except:
            pass
        
        projected_collection = self.client.create_collection(
            name="projected_index",
            metadata={
                "hnsw:space": "cosine",
                "version": "1.0",
                "architecture": "v3.0",
                "materialization": "on_demand"
            }
        )
        
        logger.info("  ✅ projected_index Collection 생성")
        
        # Canonical → Projected 변환
        canonical_docs = canonical_collection.get(
            include=['documents', 'metadatas']
        )
        
        all_projected = []
        
        for i, metadata in enumerate(canonical_docs['metadatas']):
            canonical_chunk = {
                **metadata,
                'content': canonical_docs['documents'][i]
            }
            
            # Hybrid Projection
            projected_chunks = self.projector.project(canonical_chunk)
            all_projected.extend(projected_chunks)
        
        logger.info(f"  ✅ {len(all_projected)}개 Projected 청크 생성")
        
        # Embedding 및 저장
        logger.info("  🔄 Embedding 생성 중...")
        
        texts = [p['content'] for p in all_projected]
        embeddings = self.embeddings.embed_documents(texts)
        
        # 메타데이터를 Chroma 호환 형식으로 변환
        metadatas = []
        for p in all_projected:
            metadata = {
                'projected_chunk_id': p['projected_chunk_id'],
                'source_id': p['source_id'],
                'agent_view': p['agent_view'],
                'canonical_chunk_id': p['canonical_chunk_id'],
                'projection_method': p['projection_method'],
                'domain': p['domain'],
                'version': p['version'],
                'materialization': json.dumps(p.get('materialization', {})),
                'lineage': json.dumps(p.get('lineage', {})),
                'created_at': p['created_at'],
                'updated_at': p['updated_at']
            }
            metadatas.append(metadata)
        
        projected_collection.add(
            ids=[p['projected_chunk_id'] for p in all_projected],
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"  ✅ {len(all_projected)}개 Projected 청크 저장 완료!")
        
        # 통계
        count = projected_collection.count()
        logger.info(f"\n📊 Projected Index: {count}개")
        
        # Agent별 통계
        for agent in ['observer', 'explorer', 'quantifier', 'validator', 'guardian']:
            agent_count = len([p for p in all_projected if p['agent_view'] == agent])
            logger.info(f"   {agent}: {agent_count}개")
        
        return count


if __name__ == "__main__":
    builder = ProjectedIndexBuilder()
    count = builder.build()
    
    print(f"\n✅ Projected Index 구축 완료!")
    print(f"📊 Collection: projected_index")
    print(f"📝 Documents: {count}개")
    print(f"🔑 ID: PRJ-xxxxxxxx")
    print(f"⏰ TTL: 24시간 (온디맨드)")

