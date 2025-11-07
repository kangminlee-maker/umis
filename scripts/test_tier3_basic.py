#!/usr/bin/env python3
"""
Tier 3 기본 테스트

SimpleVariablePolicy 및 기본 동작 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.tier3 import (
    Tier3FermiPath,
    SimpleVariablePolicy,
    FermiModel,
    FermiVariable
)
from umis_rag.agents.estimator.models import Context
from umis_rag.utils.logger import logger


def test_simple_variable_policy():
    """SimpleVariablePolicy 테스트"""
    logger.info("=" * 60)
    logger.info("Test 1: SimpleVariablePolicy")
    logger.info("=" * 60)
    
    policy = SimpleVariablePolicy()
    
    # 테스트 케이스
    test_cases = [
        (3, True, None),           # 3개: 정상
        (6, True, None),           # 6개: 권장 상한 (정상)
        (7, True, "⚠️"),           # 7개: 경고 (허용)
        (10, True, "⚠️"),          # 10개: 경고 (허용)
        (11, False, "🛑"),         # 11개: 금지
    ]
    
    passed = 0
    for count, expected_allowed, expected_warning_type in test_cases:
        allowed, warning = policy.check(count)
        
        # 판정 확인
        if allowed == expected_allowed:
            # 경고 타입 확인
            if expected_warning_type is None and warning is None:
                logger.info(f"  ✅ {count}개: 정상 (예상대로)")
                passed += 1
            elif expected_warning_type and warning and expected_warning_type in warning:
                logger.info(f"  ✅ {count}개: {warning} (예상대로)")
                passed += 1
            else:
                logger.warning(f"  ⚠️  {count}개: 경고 타입 불일치")
        else:
            logger.error(f"  ❌ {count}개: allowed={allowed}, 예상={expected_allowed}")
    
    logger.info(f"\n  결과: {passed}/{len(test_cases)} 통과")
    
    return passed == len(test_cases)


def test_tier3_initialization():
    """Tier 3 초기화 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Tier3FermiPath 초기화")
    logger.info("=" * 60)
    
    try:
        tier3 = Tier3FermiPath()
        
        logger.info(f"  ✅ 초기화 성공")
        logger.info(f"    Max depth: {tier3.max_depth}")
        logger.info(f"    Variable policy: {tier3.variable_policy.recommended_max}개 권장")
        logger.info(f"    Tier 2 준비: {tier3.tier2 is not None}")
        
        return True
    
    except Exception as e:
        logger.error(f"  ❌ 초기화 실패: {e}")
        return False


def test_circular_detection():
    """순환 감지 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: 순환 의존성 감지")
    logger.info("=" * 60)
    
    tier3 = Tier3FermiPath()
    
    # Call stack 시뮬레이션
    tier3.call_stack = ["시장 규모는?", "점유율은?"]
    
    # 순환 테스트
    test_cases = [
        ("시장 규모는?", True),   # 순환!
        ("점유율은?", True),       # 순환!
        ("Churn Rate는?", False),  # 정상
    ]
    
    passed = 0
    for question, expected_circular in test_cases:
        is_circular = tier3._detect_circular(question)
        
        if is_circular == expected_circular:
            status = "순환" if is_circular else "정상"
            logger.info(f"  ✅ '{question}': {status} (예상대로)")
            passed += 1
        else:
            logger.error(f"  ❌ '{question}': 결과={is_circular}, 예상={expected_circular}")
    
    logger.info(f"\n  결과: {passed}/{len(test_cases)} 통과")
    
    return passed == len(test_cases)


def test_model_scoring():
    """모형 점수화 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: 모형 점수화")
    logger.info("=" * 60)
    
    tier3 = Tier3FermiPath()
    
    # 테스트 모형 생성
    model = FermiModel(
        model_id="TEST_001",
        name="테스트 모형",
        formula="market = a × b × c",
        description="3변수 모형",
        variables={
            'a': FermiVariable(name='a', available=True, value=1000, confidence=0.9),
            'b': FermiVariable(name='b', available=True, value=0.5, confidence=0.7),
            'c': FermiVariable(name='c', available=False, need_estimate=True)
        },
        total_variables=3
    )
    
    # 점수 계산
    score_result = tier3._score_model(model, depth=0)
    
    logger.info(f"  모형: {model.model_id}")
    logger.info(f"    변수: {model.total_variables}개 (가용: 2개)")
    logger.info(f"    Unknown: {score_result['unknown']:.3f}")
    logger.info(f"    Confidence: {score_result['confidence']:.3f}")
    logger.info(f"    Complexity: {score_result['complexity']:.3f}")
    logger.info(f"    Depth: {score_result['depth']:.3f}")
    logger.info(f"    총점: {score_result['total']:.3f}")
    logger.info(f"    상태: {score_result['status']}")
    
    # 검증
    if score_result['total'] > 0:
        logger.info(f"  ✅ 점수 계산 성공")
        return True
    else:
        logger.error(f"  ❌ 점수 계산 실패")
        return False


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 19 + "Tier 3 Basic Test" + " " * 22 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: SimpleVariablePolicy
    try:
        results.append(("SimpleVariablePolicy", test_simple_variable_policy()))
    except Exception as e:
        logger.error(f"Test 1 failed: {e}")
        results.append(("SimpleVariablePolicy", False))
    
    # Test 2: Initialization
    try:
        results.append(("Tier3 Initialization", test_tier3_initialization()))
    except Exception as e:
        logger.error(f"Test 2 failed: {e}")
        results.append(("Tier3 Initialization", False))
    
    # Test 3: Circular Detection
    try:
        results.append(("Circular Detection", test_circular_detection()))
    except Exception as e:
        logger.error(f"Test 3 failed: {e}")
        results.append(("Circular Detection", False))
    
    # Test 4: Model Scoring
    try:
        results.append(("Model Scoring", test_model_scoring()))
    except Exception as e:
        logger.error(f"Test 4 failed: {e}")
        results.append(("Model Scoring", False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name:.<40} {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Total: {passed_count}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

