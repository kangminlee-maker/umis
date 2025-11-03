"""
Neo4j Schema Initializer

schema_registry.yaml의 Knowledge Graph 스키마 생성:
- Pattern 노드 제약
- Case 노드 제약
- 인덱스 생성
"""

from typing import Optional
from umis_rag.graph.connection import Neo4jConnection
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class GraphSchemaInitializer:
    """Neo4j 스키마 초기화"""
    
    def __init__(self, connection: Optional[Neo4jConnection] = None):
        """
        Args:
            connection: Neo4j 연결 (없으면 자동 생성)
        """
        self.conn = connection or Neo4jConnection()
    
    def initialize_schema(self) -> bool:
        """
        전체 스키마 초기화
        
        Returns:
            성공 여부
        """
        try:
            logger.info("🔧 Initializing Neo4j schema...")
            
            # 1. Constraints
            self._create_constraints()
            
            # 2. Indexes
            self._create_indexes()
            
            logger.info("✅ Schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema initialization failed: {e}")
            return False
    
    def _create_constraints(self) -> None:
        """제약 조건 생성"""
        
        constraints = [
            # Pattern 노드: graph_node_id 유니크
            """
            CREATE CONSTRAINT pattern_node_id IF NOT EXISTS
            FOR (p:Pattern) REQUIRE p.graph_node_id IS UNIQUE
            """,
            
            # Pattern 노드: pattern_id 유니크
            """
            CREATE CONSTRAINT pattern_pattern_id IF NOT EXISTS
            FOR (p:Pattern) REQUIRE p.pattern_id IS UNIQUE
            """,
            
            # Case 노드: graph_node_id 유니크
            """
            CREATE CONSTRAINT case_node_id IF NOT EXISTS
            FOR (c:Case) REQUIRE c.graph_node_id IS UNIQUE
            """,
            
            # Case 노드: source_id 유니크
            """
            CREATE CONSTRAINT case_source_id IF NOT EXISTS
            FOR (c:Case) REQUIRE c.source_id IS UNIQUE
            """,
        ]
        
        for constraint in constraints:
            try:
                self.conn.execute_write(constraint.strip())
                logger.info(f"✅ Constraint created")
            except Exception as e:
                # 이미 존재하는 경우 무시
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    logger.debug(f"Constraint already exists: {e}")
                else:
                    logger.warning(f"Failed to create constraint: {e}")
    
    def _create_indexes(self) -> None:
        """인덱스 생성"""
        
        indexes = [
            # Pattern: domain 인덱스
            """
            CREATE INDEX pattern_domain IF NOT EXISTS
            FOR (p:Pattern) ON (p.domain)
            """,
            
            # Pattern: version 인덱스
            """
            CREATE INDEX pattern_version IF NOT EXISTS
            FOR (p:Pattern) ON (p.version)
            """,
            
            # Case: domain 인덱스
            """
            CREATE INDEX case_domain IF NOT EXISTS
            FOR (c:Case) ON (c.domain)
            """,
            
            # Case: industry 인덱스
            """
            CREATE INDEX case_industry IF NOT EXISTS
            FOR (c:Case) ON (c.industry)
            """,
            
            # Relationship: graph_edge_id 인덱스
            # Note: Neo4j 5.x에서는 관계 프로퍼티 인덱스 지원
            """
            CREATE INDEX relationship_edge_id IF NOT EXISTS
            FOR ()-[r:COMBINES_WITH]-() ON (r.graph_edge_id)
            """,
        ]
        
        for index in indexes:
            try:
                self.conn.execute_write(index.strip())
                logger.info(f"✅ Index created")
            except Exception as e:
                # 이미 존재하는 경우 무시
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    logger.debug(f"Index already exists: {e}")
                else:
                    logger.warning(f"Failed to create index: {e}")
    
    def verify_schema(self) -> bool:
        """
        스키마 검증
        
        Returns:
            스키마가 올바르게 생성되었는지
        """
        try:
            # Constraints 확인
            constraints = self.conn.execute_query(
                "SHOW CONSTRAINTS"
            )
            logger.info(f"Total constraints: {len(constraints)}")
            
            # Indexes 확인
            indexes = self.conn.execute_query(
                "SHOW INDEXES"
            )
            logger.info(f"Total indexes: {len(indexes)}")
            
            return len(constraints) >= 4 and len(indexes) >= 5
            
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            return False
    
    def drop_all(self) -> bool:
        """
        ⚠️ 모든 노드/관계 삭제 (개발용)
        
        Returns:
            성공 여부
        """
        try:
            logger.warning("🗑️ Dropping all nodes and relationships...")
            
            result = self.conn.execute_write(
                "MATCH (n) DETACH DELETE n"
            )
            
            logger.warning(f"✅ Deleted {result.get('nodes_deleted', 0)} nodes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Drop failed: {e}")
            return False

