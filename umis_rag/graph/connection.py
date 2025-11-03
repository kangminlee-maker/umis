"""
Neo4j Connection Manager

schema_registry.yaml 준수:
- GND-xxx (Graph Node ID)
- GED-xxx (Graph Edge ID)
"""

import os
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session
from contextlib import contextmanager

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jConnection:
    """Neo4j 연결 관리자"""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Args:
            uri: Neo4j URI (기본: bolt://localhost:7687)
            user: 사용자명 (기본: neo4j)
            password: 비밀번호 (기본: umis_password)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "umis_password")
        
        self._driver: Optional[Driver] = None
        
        logger.info(f"Neo4j Connection initialized: {self.uri}")
    
    def connect(self) -> None:
        """Neo4j에 연결"""
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # 연결 테스트
            self._driver.verify_connectivity()
            logger.info("✅ Neo4j connected successfully")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise
    
    def close(self) -> None:
        """연결 종료"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
    
    @contextmanager
    def session(self, database: str = "neo4j") -> Session:
        """
        Context manager로 세션 생성
        
        Usage:
            with conn.session() as session:
                result = session.run("MATCH (n) RETURN n")
        """
        if not self._driver:
            self.connect()
        
        session = self._driver.session(database=database)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """
        쿼리 실행 및 결과 반환
        
        Args:
            query: Cypher 쿼리
            parameters: 쿼리 파라미터
            database: 데이터베이스명
        
        Returns:
            결과 리스트
        """
        with self.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j"
    ) -> Dict[str, Any]:
        """
        쓰기 트랜잭션 실행
        
        Args:
            query: Cypher 쿼리
            parameters: 쿼리 파라미터
            database: 데이터베이스명
        
        Returns:
            실행 결과
        """
        def _execute_write_tx(tx, query, params):
            result = tx.run(query, params)
            return result.consume()
        
        with self.session(database=database) as session:
            summary = session.execute_write(
                _execute_write_tx,
                query,
                parameters or {}
            )
            
            return {
                'nodes_created': summary.counters.nodes_created,
                'relationships_created': summary.counters.relationships_created,
                'properties_set': summary.counters.properties_set
            }
    
    def verify_connection(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 성공 여부
        """
        try:
            if not self._driver:
                self.connect()
            
            self._driver.verify_connectivity()
            
            # 간단한 쿼리로 추가 확인
            with self.session() as session:
                result = session.run("RETURN 1 as test")
                test = result.single()
                if test and test['test'] == 1:
                    logger.info("✅ Neo4j connection verified")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Connection verification failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        그래프 통계 조회
        
        Returns:
            노드, 관계 수 등
        """
        try:
            stats = {}
            
            # 노드 수
            node_count = self.execute_query(
                "MATCH (n) RETURN count(n) as count"
            )
            stats['total_nodes'] = node_count[0]['count'] if node_count else 0
            
            # 관계 수
            rel_count = self.execute_query(
                "MATCH ()-[r]->() RETURN count(r) as count"
            )
            stats['total_relationships'] = rel_count[0]['count'] if rel_count else 0
            
            # Pattern 노드 수
            pattern_count = self.execute_query(
                "MATCH (p:Pattern) RETURN count(p) as count"
            )
            stats['pattern_nodes'] = pattern_count[0]['count'] if pattern_count else 0
            
            # Case 노드 수
            case_count = self.execute_query(
                "MATCH (c:Case) RETURN count(c) as count"
            )
            stats['case_nodes'] = case_count[0]['count'] if case_count else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def __enter__(self):
        """Context manager 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

