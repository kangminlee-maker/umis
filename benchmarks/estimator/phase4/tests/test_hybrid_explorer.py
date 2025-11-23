#!/usr/bin/env python3
"""
Explorer + Hybrid Search 통합 테스트

Vector RAG + Knowledge Graph 결합 테스트
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger
from umis_rag.graph.hybrid_search import print_hybrid_results

logger = get_logger(__name__)


def test_hybrid_search_direct():
    """Hybrid Search 직접 테스트"""
    logger.info("=" * 60)
    logger.info("Test 1: Hybrid Search Direct")
    logger.info("=" * 60)
    
    from umis_rag.graph.hybrid_search import search_by_id
    
    # Platform 패턴 검색
    result = search_by_id("platform_business_model", max_combinations=5)
    print_hybrid_results(result)
    
    return True


def test_explorer_with_graph():
    """Explorer + Hybrid Search 통합 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Explorer + Hybrid Search Integration")
    logger.info("=" * 60)
    
    try:
        from umis_rag.agents.explorer import ExplorerRAG
        
        # Explorer 초기화
        explorer = ExplorerRAG()
        
        # Hybrid Search 사용 가능 여부 확인
        if not explorer.hybrid_search:
            logger.warning("⚠️ Hybrid Search 비활성 - Explorer가 Vector만 사용")
            return False
        
        # 테스트 쿼리: 음악 스트리밍
        query = "음악 스트리밍 구독 서비스 시장"
        
        logger.info(f"\n🔍 Query: {query}")
        
        # Hybrid Search 실행
        result = explorer.search_patterns_with_graph(
            trigger_observation=query,
            top_k=3,
            max_combinations=8
        )
        
        if result:
            print_hybrid_results(result)
            return True
        else:
            logger.error("❌ Hybrid search returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ Explorer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pattern_combinations():
    """여러 패턴의 조합 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Multiple Pattern Combinations")
    logger.info("=" * 60)
    
    from umis_rag.graph.hybrid_search import search_by_id
    
    patterns = [
        "subscription_model",
        "freemium_model",
        "innovation_disruption"
    ]
    
    for pattern in patterns:
        logger.info(f"\n📊 Pattern: {pattern}")
        result = search_by_id(pattern, max_combinations=3)
        
        print(f"\n{pattern}:")
        print(f"  Combinations: {len(result.combinations)}")
        for combo in result.combinations[:3]:
            print(f"    • {combo.target_pattern} ({combo.relationship_type}, {combo.confidence.get('overall', 0):.2f})")
    
    return True


def test_confidence_filtering():
    """Confidence 기반 필터링 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Confidence Filtering")
    logger.info("=" * 60)
    
    from umis_rag.graph.hybrid_search import search_by_id
    
    # 낮은 신뢰도 (더 많은 결과)
    result_low = search_by_id("platform_business_model", min_confidence=0.5)
    logger.info(f"  Min confidence 0.5: {len(result_low.combinations)} combinations")
    
    # 높은 신뢰도 (적은 결과)
    result_high = search_by_id("platform_business_model", min_confidence=0.8)
    logger.info(f"  Min confidence 0.8: {len(result_high.combinations)} combinations")
    
    return len(result_high.combinations) <= len(result_low.combinations)


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "Explorer + Hybrid Search Test" + " " * 19 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: Hybrid Search Direct
    try:
        results.append(("Hybrid Search Direct", test_hybrid_search_direct()))
    except Exception as e:
        logger.error(f"Test 1 failed: {e}")
        results.append(("Hybrid Search Direct", False))
    
    # Test 2: Explorer Integration
    try:
        results.append(("Explorer Integration", test_explorer_with_graph()))
    except Exception as e:
        logger.error(f"Test 2 failed: {e}")
        results.append(("Explorer Integration", False))
    
    # Test 3: Multiple Patterns
    try:
        results.append(("Multiple Patterns", test_pattern_combinations()))
    except Exception as e:
        logger.error(f"Test 3 failed: {e}")
        results.append(("Multiple Patterns", False))
    
    # Test 4: Confidence Filtering
    try:
        results.append(("Confidence Filtering", test_confidence_filtering()))
    except Exception as e:
        logger.error(f"Test 4 failed: {e}")
        results.append(("Confidence Filtering", False))
    
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

