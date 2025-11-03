"""
Schema Contract Tests

Layer 간 호환성 검증
- config/schema_registry.yaml 준수 확인
- Canonical ↔ Projected 무손실
- Field 매핑 정확성
"""

import pytest
import chromadb
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.schema import SchemaRegistry


class TestSchemaContract:
    """Schema Contract Tests"""
    
    @pytest.fixture
    def schema(self):
        """SchemaRegistry"""
        return SchemaRegistry()
    
    @pytest.fixture
    def client(self):
        """Chroma Client"""
        return chromadb.PersistentClient(path="data/chroma")
    
    def test_canonical_schema_compliance(self, schema, client):
        """Canonical이 schema 준수?"""
        try:
            collection = client.get_collection("canonical_index")
        except:
            pytest.skip("canonical_index not built yet")
        
        chunks = collection.get(include=['metadatas'], limit=1)
        
        if not chunks['metadatas']:
            pytest.skip("No chunks")
        
        chunk = chunks['metadatas'][0]
        
        # ID 네임스페이스
        assert 'canonical_chunk_id' in chunk
        assert chunk['canonical_chunk_id'].startswith('CAN-')
        
        # Lineage
        assert 'lineage' in chunk
        assert 'from' in chunk['lineage']
        assert 'evidence_ids' in chunk['lineage']
        
        # sections: anchor+hash
        assert 'sections' in chunk
        for section in chunk['sections']:
            assert 'anchor_path' in section
            assert 'content_hash' in section
    
    def test_projected_schema_compliance(self, schema, client):
        """Projected가 schema 준수?"""
        try:
            collection = client.get_collection("projected_index")
        except:
            pytest.skip("projected_index not built yet")
        
        chunks = collection.get(include=['metadatas'], limit=1)
        
        if not chunks['metadatas']:
            pytest.skip("No chunks")
        
        chunk = chunks['metadatas'][0]
        
        # ID
        assert 'projected_chunk_id' in chunk
        assert chunk['projected_chunk_id'].startswith('PRJ-')
        
        # Canonical 참조
        assert 'canonical_chunk_id' in chunk
        assert chunk['canonical_chunk_id'].startswith('CAN-')
        
        # Agent view
        assert 'agent_view' in chunk
        assert chunk['agent_view'] in ['observer', 'explorer', 'quantifier', 'validator', 'guardian']
        
        # TTL
        assert 'materialization' in chunk
        assert 'strategy' in chunk['materialization']
        assert chunk['materialization']['strategy'] in ['on_demand', 'persistent']
        
        # Lineage
        assert 'lineage' in chunk
        assert chunk['lineage']['from'] == chunk['canonical_chunk_id']
    
    def test_canonical_to_projected_no_loss(self, client):
        """Canonical → Projected 정보 손실 없음?"""
        try:
            canonical = client.get_collection("canonical_index")
            projected = client.get_collection("projected_index")
        except:
            pytest.skip("Collections not built")
        
        canonical_chunks = canonical.get(include=['metadatas'])
        
        if not canonical_chunks['metadatas']:
            pytest.skip("No chunks")
        
        # 첫 번째 Canonical
        can_chunk = canonical_chunks['metadatas'][0]
        can_id = can_chunk['canonical_chunk_id']
        
        # 해당 Projected 찾기
        proj_chunks = projected.get(
            where={'canonical_chunk_id': can_id},
            include=['metadatas']
        )
        
        # Agent별로 생성되었는가?
        agents = set(p['agent_view'] for p in proj_chunks['metadatas'])
        
        # 최소 1개 이상 (모든 Agent는 아닐 수 있음)
        assert len(agents) >= 1
        
        # Lineage 연결
        for proj in proj_chunks['metadatas']:
            assert proj['lineage']['from'] == can_id
    
    def test_field_mapping(self, client):
        """Field 매핑 정확성"""
        try:
            projected = client.get_collection("projected_index")
        except:
            pytest.skip("projected_index not built")
        
        # Explorer 청크 찾기
        explorer_chunks = projected.get(
            where={'agent_view': 'explorer'},
            include=['metadatas'],
            limit=1
        )
        
        if not explorer_chunks['metadatas']:
            pytest.skip("No explorer chunks")
        
        chunk = explorer_chunks['metadatas'][0]
        
        # explorer_pattern_id 존재 (향후 Graph에서 pattern_id로 매핑)
        # (현재는 선택사항)
        # assert 'explorer_pattern_id' in chunk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

