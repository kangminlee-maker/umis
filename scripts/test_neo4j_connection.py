#!/usr/bin/env python3
"""
Neo4j 연결 및 스키마 테스트

Usage:
    python scripts/test_neo4j_connection.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.graph.connection import Neo4jConnection
from umis_rag.graph.schema_initializer import GraphSchemaInitializer
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


def test_connection():
    """연결 테스트"""
    logger.info("=" * 60)
    logger.info("Neo4j Connection Test")
    logger.info("=" * 60)
    
    try:
        with Neo4jConnection() as conn:
            # 연결 확인
            if conn.verify_connection():
                logger.info("✅ Connection test PASSED")
                
                # 통계 조회
                stats = conn.get_stats()
                logger.info(f"\nCurrent Graph Stats:")
                for key, value in stats.items():
                    logger.info(f"  {key}: {value}")
                
                return True
            else:
                logger.error("❌ Connection test FAILED")
                return False
                
    except Exception as e:
        logger.error(f"❌ Connection test ERROR: {e}")
        return False


def test_schema_initialization():
    """스키마 초기화 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Neo4j Schema Initialization Test")
    logger.info("=" * 60)
    
    try:
        with Neo4jConnection() as conn:
            initializer = GraphSchemaInitializer(conn)
            
            # 스키마 생성
            if initializer.initialize_schema():
                logger.info("✅ Schema initialization PASSED")
                
                # 스키마 검증
                if initializer.verify_schema():
                    logger.info("✅ Schema verification PASSED")
                    return True
                else:
                    logger.warning("⚠️ Schema verification FAILED")
                    return False
            else:
                logger.error("❌ Schema initialization FAILED")
                return False
                
    except Exception as e:
        logger.error(f"❌ Schema test ERROR: {e}")
        return False


def test_basic_operations():
    """기본 CRUD 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Neo4j Basic Operations Test")
    logger.info("=" * 60)
    
    try:
        with Neo4jConnection() as conn:
            # 1. 테스트 노드 생성
            logger.info("\n1. Creating test node...")
            result = conn.execute_write(
                """
                CREATE (p:Pattern {
                    graph_node_id: 'GND-test001',
                    pattern_id: 'test_pattern',
                    domain: 'test',
                    version: '1.0.0'
                })
                RETURN p
                """
            )
            logger.info(f"   Created {result['nodes_created']} node(s)")
            
            # 2. 노드 조회
            logger.info("\n2. Reading test node...")
            nodes = conn.execute_query(
                "MATCH (p:Pattern {graph_node_id: 'GND-test001'}) RETURN p"
            )
            logger.info(f"   Found {len(nodes)} node(s)")
            if nodes:
                logger.info(f"   Node: {nodes[0]['p']}")
            
            # 3. 노드 삭제
            logger.info("\n3. Deleting test node...")
            delete_result = conn.execute_write(
                "MATCH (p:Pattern {graph_node_id: 'GND-test001'}) DELETE p"
            )
            logger.info(f"   Deleted node")
            
            logger.info("\n✅ Basic operations test PASSED")
            return True
            
    except Exception as e:
        logger.error(f"❌ Basic operations test ERROR: {e}")
        return False


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 12 + "UMIS Neo4j Test Suite" + " " * 25 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_connection()))
    
    # Test 2: Schema
    results.append(("Schema Initialization", test_schema_initialization()))
    
    # Test 3: Basic Operations
    results.append(("Basic Operations", test_basic_operations()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

