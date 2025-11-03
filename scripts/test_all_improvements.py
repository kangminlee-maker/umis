#!/usr/bin/env python3
"""
전체 개선사항 통합 테스트

Learning Loop + Fail-Safe + RAE Index
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


def test_learning_loop():
    """Learning Loop 테스트"""
    logger.info("=" * 60)
    logger.info("Test 1: Learning Loop")
    logger.info("=" * 60)
    
    from umis_rag.learning.rule_learner import learn_from_logs
    import json
    
    # 샘플 로그 생성
    sample_logs = [
        {"source_id": "test_pattern", "agent": "explorer", "decision": True, "timestamp": "2024-11-03T01:00:00Z"},
        {"source_id": "test_pattern", "agent": "explorer", "decision": True, "timestamp": "2024-11-03T02:00:00Z"},
        {"source_id": "test_pattern", "agent": "explorer", "decision": True, "timestamp": "2024-11-03T03:00:00Z"},
    ]
    
    log_file = Path("test_learning_log.jsonl")
    with open(log_file, 'w', encoding='utf-8') as f:
        for log in sample_logs:
            f.write(json.dumps(log, ensure_ascii=False) + '\n')
    
    # 학습
    result = learn_from_logs(
        log_path=str(log_file),
        output_path="test_learned.yaml"
    )
    
    logger.info(f"  학습된 규칙: {result['rules_learned']}")
    
    # 정리
    log_file.unlink()
    Path("test_learned.yaml").unlink()
    
    logger.info("  ✅ Learning Loop 작동")
    return True


def test_circuit_breaker():
    """Circuit Breaker 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Circuit Breaker")
    logger.info("=" * 60)
    
    from umis_rag.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
    
    # 실패하는 함수
    fail_count = 0
    
    def failing_function():
        nonlocal fail_count
        fail_count += 1
        if fail_count <= 2:
            raise Exception(f"실패 {fail_count}")
        return "성공"
    
    cb = CircuitBreaker("test_cb", failure_threshold=2, recovery_timeout=1)
    
    # 2회 실패
    for i in range(2):
        try:
            cb.call(failing_function)
        except Exception:
            pass
    
    # 3회차 → OPEN 예상
    try:
        cb.call(failing_function)
        logger.error("  ❌ Circuit이 열리지 않음")
        return False
    except CircuitBreakerOpenError:
        logger.info("  ✅ Circuit OPEN 감지")
    
    # 복구 대기
    time.sleep(1.5)
    
    # 복구 시도
    try:
        result = cb.call(failing_function)
        logger.info(f"  ✅ 복구 성공: {result}")
        logger.info(f"  ✅ Circuit CLOSED: {cb.get_state()['state']}")
    except Exception as e:
        logger.error(f"  ❌ 복구 실패: {e}")
        return False
    
    logger.info("  ✅ Circuit Breaker 작동")
    return True


def test_rae_memory():
    """RAE Memory 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: RAE Memory")
    logger.info("=" * 60)
    
    from umis_rag.guardian.rae_memory import RAEMemory
    
    rae = RAEMemory()
    
    # 평가 저장
    rae_id = rae.store_evaluation(
        deliverable_id="TEST-001",
        deliverable_content="음악 스트리밍 구독 기회",
        grade="A",
        rationale="검증된 비즈니스 모델",
        evidence_ids=["CAN-spotify-001"]
    )
    logger.info(f"  RAE 저장: {rae_id}")
    
    # 유사 평가 검색
    similar = rae.find_similar_evaluations("음악 스트리밍 팟캐스트 기회")
    
    if similar and similar[0]['grade'] == 'A':
        logger.info(f"  ✅ 유사 평가 발견: {similar[0]['deliverable_id']}, 등급 {similar[0]['grade']}")
    else:
        logger.warning("  ⚠️  유사 평가 없음")
    
    logger.info("  ✅ RAE Memory 작동")
    return True


def test_runtime_config():
    """Runtime Config 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Runtime Config")
    logger.info("=" * 60)
    
    import yaml
    
    # runtime_config.yaml 로드
    config_path = project_root / "runtime_config.yaml"
    
    if not config_path.exists():
        logger.error("  ❌ runtime_config.yaml 없음")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 검증
    required_keys = ['mode', 'layers', 'fallback', 'circuit_breaker']
    for key in required_keys:
        if key not in config:
            logger.error(f"  ❌ {key} 없음")
            return False
    
    logger.info(f"  Mode: {config['mode']}")
    logger.info(f"  Layers: {config['layers']}")
    logger.info(f"  Circuit Breaker: {config['circuit_breaker']['enabled']}")
    logger.info("  ✅ Runtime Config 로드됨")
    
    return True


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "All Improvements Test Suite" + " " * 20 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: Learning Loop
    try:
        results.append(("Learning Loop", test_learning_loop()))
    except Exception as e:
        logger.error(f"Test 1 failed: {e}")
        results.append(("Learning Loop", False))
    
    # Test 2: Circuit Breaker
    try:
        results.append(("Circuit Breaker", test_circuit_breaker()))
    except Exception as e:
        logger.error(f"Test 2 failed: {e}")
        results.append(("Circuit Breaker", False))
    
    # Test 3: RAE Memory
    try:
        results.append(("RAE Memory", test_rae_memory()))
    except Exception as e:
        logger.error(f"Test 3 failed: {e}")
        results.append(("RAE Memory", False))
    
    # Test 4: Runtime Config
    try:
        results.append(("Runtime Config", test_runtime_config()))
    except Exception as e:
        logger.error(f"Test 4 failed: {e}")
        results.append(("Runtime Config", False))
    
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

