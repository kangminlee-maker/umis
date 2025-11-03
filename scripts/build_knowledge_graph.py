#!/usr/bin/env python3
"""
Knowledge Graph Builder

config/pattern_relationships.yaml을 읽어서 Neo4j Graph 구축

config/schema_registry.yaml 준수:
- GND-xxxxxxxx (Graph Node ID)
- GED-xxxxxxxx (Graph Edge ID)
- Evidence & Provenance
- Multi-Dimensional Confidence
"""

import sys
from pathlib import Path
import yaml
import hashlib
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.graph.connection import Neo4jConnection
from umis_rag.graph.schema_initializer import GraphSchemaInitializer
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraphBuilder:
    """Knowledge Graph 구축"""
    
    def __init__(self, connection: Neo4jConnection = None):
        """
        Args:
            connection: Neo4j 연결 (없으면 자동 생성)
        """
        self.conn = connection or Neo4jConnection()
        self.pattern_ids = set()
        self.created_nodes = 0
        self.created_relationships = 0
    
    def load_relationships(self, yaml_path: str) -> Dict[str, Any]:
        """
        config/pattern_relationships.yaml 로드
        
        Args:
            yaml_path: YAML 파일 경로
        
        Returns:
            Relationships 데이터
        """
        logger.info(f"Loading relationships from: {yaml_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        relationships = data.get('relationships', [])
        logger.info(f"Loaded {len(relationships)} relationships")
        
        # 모든 패턴 ID 수집
        for rel in relationships:
            self.pattern_ids.add(rel['source'])
            self.pattern_ids.add(rel['target'])
        
        logger.info(f"Found {len(self.pattern_ids)} unique patterns")
        
        return data
    
    def generate_node_id(self, pattern_id: str) -> str:
        """
        Graph Node ID 생성 (GND-xxxxxxxx)
        
        Args:
            pattern_id: 패턴 ID
        
        Returns:
            GND-xxx 형식의 ID
        """
        # 패턴 ID를 해시하여 8자리 생성
        hash_obj = hashlib.md5(pattern_id.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        return f"GND-{hash_hex}"
    
    def generate_edge_id(self, rel_id: str) -> str:
        """
        Graph Edge ID 생성 (GED-xxxxxxxx)
        
        Args:
            rel_id: 관계 ID (REL-001, ...)
        
        Returns:
            GED-xxx 형식의 ID
        """
        # REL-001 -> GED-xxx 변환
        hash_obj = hashlib.md5(rel_id.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        return f"GED-{hash_hex}"
    
    def create_pattern_nodes(self):
        """패턴 노드 생성"""
        logger.info(f"\n{'='*60}")
        logger.info("Creating Pattern Nodes")
        logger.info(f"{'='*60}")
        
        for pattern_id in sorted(self.pattern_ids):
            node_id = self.generate_node_id(pattern_id)
            
            # 패턴 유형 판별
            if 'disruption' in pattern_id:
                pattern_type = 'disruption'
            else:
                pattern_type = 'business_model'
            
            # 노드 생성
            try:
                query = """
                MERGE (p:Pattern {pattern_id: $pattern_id})
                ON CREATE SET
                    p.graph_node_id = $node_id,
                    p.pattern_type = $pattern_type,
                    p.domain = $domain,
                    p.version = $version,
                    p.created_at = datetime(),
                    p.updated_at = datetime()
                ON MATCH SET
                    p.updated_at = datetime()
                RETURN p
                """
                
                self.conn.execute_write(
                    query,
                    {
                        'pattern_id': pattern_id,
                        'node_id': node_id,
                        'pattern_type': pattern_type,
                        'domain': pattern_type,
                        'version': '1.0.0'
                    }
                )
                
                self.created_nodes += 1
                logger.info(f"✅ Created node: {node_id} ({pattern_id})")
                
            except Exception as e:
                logger.error(f"❌ Failed to create node {pattern_id}: {e}")
        
        logger.info(f"\nTotal nodes created: {self.created_nodes}")
    
    def create_relationships(self, relationships: List[Dict[str, Any]]):
        """관계 생성"""
        logger.info(f"\n{'='*60}")
        logger.info("Creating Relationships")
        logger.info(f"{'='*60}")
        
        for rel in relationships:
            try:
                edge_id = self.generate_edge_id(rel['id'])
                
                # Confidence를 JSON 문자열로 변환
                confidence_json = str(rel.get('confidence', {}))
                provenance_json = str(rel.get('provenance', {}))
                
                query = """
                MATCH (source:Pattern {pattern_id: $source_id})
                MATCH (target:Pattern {pattern_id: $target_id})
                MERGE (source)-[r:RELATIONSHIP {
                    graph_edge_id: $edge_id
                }]->(target)
                ON CREATE SET
                    r.relationship_type = $rel_type,
                    r.synergy = $synergy,
                    r.description = $description,
                    r.evidence_ids = $evidence_ids,
                    r.provenance = $provenance,
                    r.confidence = $confidence,
                    r.created_at = datetime()
                ON MATCH SET
                    r.updated_at = datetime()
                RETURN r
                """
                
                self.conn.execute_write(
                    query,
                    {
                        'source_id': rel['source'],
                        'target_id': rel['target'],
                        'edge_id': edge_id,
                        'rel_type': rel['type'],
                        'synergy': rel.get('synergy', ''),
                        'description': rel.get('description', ''),
                        'evidence_ids': rel.get('evidence_ids', []),
                        'provenance': provenance_json,
                        'confidence': confidence_json
                    }
                )
                
                self.created_relationships += 1
                logger.info(f"✅ Created relationship: {edge_id} ({rel['id']})")
                logger.info(f"   {rel['source']} -[{rel['type']}]-> {rel['target']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create relationship {rel['id']}: {e}")
        
        logger.info(f"\nTotal relationships created: {self.created_relationships}")
    
    def verify_graph(self):
        """그래프 검증"""
        logger.info(f"\n{'='*60}")
        logger.info("Verifying Knowledge Graph")
        logger.info(f"{'='*60}")
        
        # 노드 수
        node_count = self.conn.execute_query(
            "MATCH (p:Pattern) RETURN count(p) as count"
        )
        logger.info(f"Pattern nodes: {node_count[0]['count']}")
        
        # 관계 수
        rel_count = self.conn.execute_query(
            "MATCH ()-[r:RELATIONSHIP]->() RETURN count(r) as count"
        )
        logger.info(f"Relationships: {rel_count[0]['count']}")
        
        # 관계 유형별 통계
        type_stats = self.conn.execute_query(
            """
            MATCH ()-[r:RELATIONSHIP]->()
            RETURN r.relationship_type as type, count(*) as count
            ORDER BY count DESC
            """
        )
        
        logger.info("\nRelationship types:")
        for stat in type_stats:
            logger.info(f"  {stat['type']}: {stat['count']}")
        
        # 가장 많은 연결을 가진 패턴
        hub_patterns = self.conn.execute_query(
            """
            MATCH (p:Pattern)
            OPTIONAL MATCH (p)-[r]-(other)
            WITH p, count(r) as degree
            WHERE degree > 0
            RETURN p.pattern_id as pattern, degree
            ORDER BY degree DESC
            LIMIT 10
            """
        )
        
        logger.info("\nTop 10 hub patterns:")
        for hub in hub_patterns:
            logger.info(f"  {hub['pattern']}: {hub['degree']} connections")
    
    def build(self, yaml_path: str = None):
        """
        전체 그래프 구축
        
        Args:
            yaml_path: relationships YAML 경로 (기본: config/pattern_relationships.yaml)
        """
        if yaml_path is None:
            yaml_path = project_root / "config" / "pattern_relationships.yaml"
        
        logger.info("=" * 60)
        logger.info("Knowledge Graph Builder Started")
        logger.info("=" * 60)
        
        try:
            # 1. YAML 로드
            data = self.load_relationships(str(yaml_path))
            
            # 2. 연결 확인
            if not self.conn.verify_connection():
                raise Exception("Neo4j connection failed")
            
            # 3. 스키마 초기화
            initializer = GraphSchemaInitializer(self.conn)
            initializer.initialize_schema()
            
            # 4. 노드 생성
            self.create_pattern_nodes()
            
            # 5. 관계 생성
            self.create_relationships(data['relationships'])
            
            # 6. 검증
            self.verify_graph()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Knowledge Graph Built Successfully")
            logger.info("=" * 60)
            logger.info(f"Nodes: {self.created_nodes}")
            logger.info(f"Relationships: {self.created_relationships}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Graph building failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build UMIS Knowledge Graph")
    parser.add_argument(
        '--yaml',
        type=str,
        default=None,
        help="Path to config/pattern_relationships.yaml"
    )
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help="Rebuild graph (delete existing data)"
    )
    
    args = parser.parse_args()
    
    try:
        with Neo4jConnection() as conn:
            # Rebuild 옵션이면 기존 데이터 삭제
            if args.rebuild:
                logger.warning("⚠️ Rebuilding graph - deleting existing data...")
                initializer = GraphSchemaInitializer(conn)
                initializer.drop_all()
            
            # 그래프 구축
            builder = KnowledgeGraphBuilder(conn)
            success = builder.build(args.yaml)
            
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

