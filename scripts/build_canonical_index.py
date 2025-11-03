#!/usr/bin/env python3
"""
Canonical Index 구축 (v3.0)

data/raw/*.yaml → canonical_index Collection
- ID: CAN-xxxxxxxx
- sections: anchor_path + content_hash
- Lineage 추적
- config/schema_registry.yaml 100% 준수
"""

import sys
from pathlib import Path
from datetime import datetime
import hashlib

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.schema import SchemaRegistry, generate_id, calculate_content_hash
from umis_rag.core.config import settings
from umis_rag.utils.logger import logger
import yaml
import json
import chromadb
from langchain_openai import OpenAIEmbeddings

class CanonicalIndexBuilder:
    """
    Canonical Index 빌더
    
    기능:
    - YAML 사례 → 정규화 청크
    - ID: CAN-xxxxxxxx
    - sections: anchor_path + content_hash
    - Lineage 생성
    """
    
    def __init__(self):
        self.schema = SchemaRegistry()
        self.data_dir = Path("data/raw")
        
        # Chroma
        self.client = chromadb.PersistentClient(path="data/chroma")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        logger.info("CanonicalIndexBuilder 초기화")
    
    def load_yaml(self, filename: str):
        """YAML 파일 로드"""
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def extract_sections(self, pattern_data: dict, pattern_id: str):
        """
        패턴에서 Agent별 섹션 추출
        → anchor_path + content_hash 방식
        """
        sections = []
        
        # Explorer 섹션
        if 'opportunity_structure' in pattern_data:
            content = yaml.dump(pattern_data['opportunity_structure'])
            sections.append({
                'agent_view': 'explorer',
                'anchor_path': f"{pattern_id}.opportunity_structure",
                'content_hash': calculate_content_hash(content),
                'span_hint': {
                    'tokens': len(content.split())
                }
            })
        
        # Observer 섹션 (향후)
        # Quantifier 섹션 (향후)
        
        return sections
    
    def build_canonical_chunk(self, pattern_id: str, pattern_data: dict, domain: str):
        """
        Canonical 청크 생성 (schema 준수!)
        """
        
        # ID 생성
        canonical_id = generate_id("CAN", pattern_id)
        
        # 전체 내용
        content = yaml.dump(pattern_data, allow_unicode=True)
        
        # Sections
        sections = self.extract_sections(pattern_data, pattern_id)
        
        # Lineage
        lineage = {
            'from': f"yaml:{pattern_id}",  # YAML 원본
            'via': [],  # 최초 생성
            'evidence_ids': [],
            'created_by': {
                'agent': 'system',
                'overlay_layer': 'core',
                'tenant_id': None
            }
        }
        
        # Chunk (Chroma는 복잡한 객체를 JSON 문자열로 저장)
        chunk = {
            'canonical_chunk_id': canonical_id,
            'source_id': pattern_id,
            'domain': domain,
            'version': '6.3.0-alpha',
            'content_type': 'normalized_full',
            'sections': json.dumps(sections),  # list → JSON string
            'total_tokens': len(content.split()),
            'lineage': json.dumps(lineage),  # dict → JSON string
            'embedding_model': 'text-embedding-3-large',
            'embedding_dimension': 3072,
            'embedding_space': 'cosine',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return {
            'id': canonical_id,
            'content': content,
            'metadata': chunk
        }
    
    def build(self):
        """Canonical Index 전체 구축"""
        
        logger.info("🔨 Canonical Index 구축 시작")
        
        # Collection 생성
        try:
            self.client.delete_collection("canonical_index")
        except:
            pass
        
        collection = self.client.create_collection(
            name="canonical_index",
            metadata={
                "hnsw:space": "cosine",
                "version": "1.0",
                "architecture": "v3.0"
            }
        )
        
        logger.info("  ✅ canonical_index Collection 생성")
        
        # Business Model Patterns
        bm_data = self.load_yaml("umis_business_model_patterns.yaml")
        
        chunks = []
        for pattern_id, pattern_data in bm_data.items():
            if pattern_id.startswith('_'):
                continue
            
            chunk = self.build_canonical_chunk(
                pattern_id,
                pattern_data,
                domain='pattern'
            )
            chunks.append(chunk)
        
        logger.info(f"  ✅ Business Model: {len(chunks)}개 청크")
        
        # Disruption Patterns
        dp_data = self.load_yaml("umis_disruption_patterns.yaml")
        
        for pattern_id, pattern_data in dp_data.items():
            if pattern_id.startswith('_'):
                continue
            
            chunk = self.build_canonical_chunk(
                pattern_id,
                pattern_data,
                domain='pattern'
            )
            chunks.append(chunk)
        
        logger.info(f"  ✅ Disruption: 총 {len(chunks)}개 청크")
        
        # Embedding 및 저장
        logger.info("  🔄 Embedding 생성 중...")
        
        texts = [c['content'] for c in chunks]
        embeddings = self.embeddings.embed_documents(texts)
        
        collection.add(
            ids=[c['id'] for c in chunks],
            documents=texts,
            metadatas=[c['metadata'] for c in chunks],
            embeddings=embeddings
        )
        
        logger.info(f"  ✅ {len(chunks)}개 Canonical 청크 저장 완료!")
        
        # 검증
        count = collection.count()
        logger.info(f"\n📊 Canonical Index: {count}개")
        
        return count


if __name__ == "__main__":
    builder = CanonicalIndexBuilder()
    count = builder.build()
    
    print(f"\n✅ Canonical Index 구축 완료!")
    print(f"📊 Collection: canonical_index")
    print(f"📝 Documents: {count}개")
    print(f"🔑 ID: CAN-xxxxxxxx")
    print(f"⚓ Sections: anchor_path + content_hash")

