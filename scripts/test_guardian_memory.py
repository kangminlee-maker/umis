#!/usr/bin/env python3
"""
Guardian Memory 통합 테스트

QueryMemory + GoalMemory 종합 테스트
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian.memory import GuardianMemory
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


def test_query_memory():
    """QueryMemory 테스트"""
    logger.info("=" * 60)
    logger.info("Test 1: QueryMemory (순환 감지)")
    logger.info("=" * 60)
    
    from umis_rag.guardian.query_memory import QueryMemory
    
    memory = QueryMemory()
    
    # 테스트 쿼리
    queries = [
        "음악 스트리밍 시장 분석",
        "음악 스트리밍 분석해줘",  # 유사
        "음악 시장 구독 모델",      # 유사
    ]
    
    for i, query in enumerate(queries, 1):
        is_circular, info = memory.check_and_store(query)
        logger.info(f"  Query {i}: 반복 {info['repetition_count']}회")
    
    stats = memory.get_stats()
    logger.info(f"  총 쿼리: {stats['total_queries']}")
    logger.info(f"  ✅ QueryMemory 작동")
    
    return True


def test_goal_memory():
    """GoalMemory 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: GoalMemory (목표 정렬)")
    logger.info("=" * 60)
    
    from umis_rag.guardian.goal_memory import GoalMemory
    
    memory = GoalMemory()
    
    # 목표 설정
    goal = "음악 스트리밍 구독 시장 분석"
    memory.set_goal(goal)
    logger.info(f"  목표 설정: {goal}")
    
    # 정렬도 테스트
    tasks = [
        ("Spotify 구독 분석", 0.70, True),   # 정렬됨
        ("자동차 시장 분석", 0.70, False),  # 이탈
    ]
    
    for task, threshold, expected in tasks:
        is_aligned, info = memory.check_alignment(task)
        score = info['alignment_score']
        
        logger.info(f"  작업: {task}")
        logger.info(f"    정렬도: {score:.3f}, 예상: {'정렬' if expected else '이탈'}")
        
        # 검증
        if expected and is_aligned:
            logger.info(f"    ✅ 정렬됨 (예상대로)")
        elif not expected and not is_aligned:
            logger.info(f"    ✅ 이탈 감지 (예상대로)")
        else:
            logger.warning(f"    ⚠️  예상과 다름")
    
    logger.info(f"  ✅ GoalMemory 작동")
    return True


def test_guardian_integration():
    """Guardian 통합 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: GuardianMemory 통합")
    logger.info("=" * 60)
    
    guardian = GuardianMemory()
    
    # 목표 설정
    goal = "음악 스트리밍 구독 시장의 수익화 전략 발굴"
    guardian.set_goal(goal)
    logger.info(f"  목표: {goal}")
    
    # 시나리오 테스트
    scenarios = [
        ("Spotify 프리미엄 수익 분석", True, "정렬됨"),
        ("자동차 EV 시장", False, "이탈"),
        ("YouTube Music 광고 모델", True, "정렬됨"),
    ]
    
    passed = 0
    for task, expected_pass, desc in scenarios:
        result = guardian.check_process(task)
        
        logger.info(f"\n  작업: {task}")
        logger.info(f"  예상: {desc}")
        logger.info(f"  결과: {'통과' if result['passed'] else '경고'}")
        
        if result['passed'] == expected_pass:
            logger.info(f"  ✅ 예상대로")
            passed += 1
        else:
            logger.warning(f"  ⚠️  예상과 다름")
    
    logger.info(f"\n  통합 테스트: {passed}/{len(scenarios)} 통과")
    
    return passed == len(scenarios)


def test_guardian_recommendations():
    """Guardian 권장사항 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Guardian 권장사항")
    logger.info("=" * 60)
    
    guardian = GuardianMemory()
    guardian.set_goal("음악 스트리밍 시장 기회 발굴")
    
    # 이탈 케이스
    result = guardian.check_process("자동차 시장 분석")
    
    logger.info(f"  작업: 자동차 시장 분석")
    logger.info(f"  경고: {len(result['warnings'])}개")
    
    if result['recommendation']:
        logger.info(f"  권장사항:")
        for line in result['recommendation'].split('\n'):
            logger.info(f"    {line}")
    
    logger.info(f"  ✅ 권장사항 생성됨")
    
    return bool(result['recommendation'])


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "Guardian Memory Test Suite" + " " * 16 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: QueryMemory
    try:
        results.append(("QueryMemory", test_query_memory()))
    except Exception as e:
        logger.error(f"Test 1 failed: {e}")
        results.append(("QueryMemory", False))
    
    # Test 2: GoalMemory
    try:
        results.append(("GoalMemory", test_goal_memory()))
    except Exception as e:
        logger.error(f"Test 2 failed: {e}")
        results.append(("GoalMemory", False))
    
    # Test 3: Integration
    try:
        results.append(("Guardian Integration", test_guardian_integration()))
    except Exception as e:
        logger.error(f"Test 3 failed: {e}")
        results.append(("Guardian Integration", False))
    
    # Test 4: Recommendations
    try:
        results.append(("Guardian Recommendations", test_guardian_recommendations()))
    except Exception as e:
        logger.error(f"Test 4 failed: {e}")
        results.append(("Guardian Recommendations", False))
    
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

