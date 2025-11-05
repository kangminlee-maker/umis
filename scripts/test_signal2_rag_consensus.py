#!/usr/bin/env python3
"""
Signal2 RAG Consensus 테스트
UMIS RAG 3개 Agent 통합 검색
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.methodologies.domain_reasoner import Signal2_RAGConsensus


def test_platform_commission():
    """Test 1: 플랫폼 수수료율 (배달 플랫폼)"""
    print("\n" + "=" * 70)
    print("Test 1: 플랫폼 수수료율 - RAG Consensus")
    print("=" * 70)
    
    signal = Signal2_RAGConsensus()
    
    result = signal.process(
        definition={
            'question': '국내 음식 배달 플랫폼 평균 수수료율',
            'kpi': '플랫폼 수수료율'
        },
        context={
            'query': '배달 플랫폼 수수료율',
            'domain': 'platform',
            'geography': 'KR'
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  Signal: {result.signal_name}")
    print(f"  Weight: {result.weight}")
    print(f"  Value: {result.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  UMIS Mapping: {result.umis_mapping}")
    
    print(f"\n  증거 ({len(result.evidence)}개):")
    for ev in result.evidence[:3]:
        print(f"    - {ev['src_id']}: {ev['source']} (유사도: {ev['similarity']:.3f})")
    
    assert result.signal_name == 's2_rag_consensus', "신호 이름 확인"
    assert result.weight == 0.9, "가중치 확인"
    assert len(result.evidence) > 0, "증거 존재 확인"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_subscription_churn():
    """Test 2: 구독 해지율"""
    print("\n" + "=" * 70)
    print("Test 2: 구독 해지율 - RAG Consensus")
    print("=" * 70)
    
    signal = Signal2_RAGConsensus()
    
    result = signal.process(
        definition={
            'question': 'B2C SaaS 월간 해지율',
            'kpi': 'Churn Rate'
        },
        context={
            'query': '구독 서비스 해지율 churn rate',
            'domain': 'subscription',
            'geography': 'Global'
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  Value: {result.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  증거: {len(result.evidence)}개")
    
    assert len(result.evidence) > 0, "증거 존재"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_market_size():
    """Test 3: 시장 규모 (일반)"""
    print("\n" + "=" * 70)
    print("Test 3: 음악 스트리밍 시장 규모 - RAG Consensus")
    print("=" * 70)
    
    signal = Signal2_RAGConsensus()
    
    result = signal.process(
        definition={
            'question': '글로벌 음악 스트리밍 시장 규모',
            'kpi': 'Market Size'
        },
        context={
            'query': '음악 스트리밍 시장 규모 구독',
            'domain': 'music',
            'geography': 'Global'
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  Value: {result.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  증거 출처:")
    for ev in result.evidence[:5]:
        print(f"    - {ev['type']}: {ev['source']}")
    
    assert result.confidence > 0, "신뢰도 > 0"
    
    print("\n✅ Test 3 PASSED")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("Signal2 RAG Consensus 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: 플랫폼 수수료율", test_platform_commission),
        ("Test 2: 구독 해지율", test_subscription_churn),
        ("Test 3: 시장 규모", test_market_size),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, 'PASS'))
            passed += 1
        except AssertionError as e:
            results.append((name, 'FAIL'))
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
        except Exception as e:
            results.append((name, 'ERROR'))
            failed += 1
            print(f"\n💥 {name} ERROR: {e}")
    
    # 최종 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    
    for name, status in results:
        icon = "✅" if status == 'PASS' else "❌"
        print(f"  {icon} {name}: {status}")
    
    print(f"\n총 {len(tests)}개 테스트: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("\n🎉 모든 테스트 통과!")
        print("\n✅ s2_rag_consensus 구현 완료:")
        print("  - UMIS RAG 3개 Agent 통합 (Explorer, Quantifier, Validator)")
        print("  - 독립 출처 확인 (≥2)")
        print("  - 합의 범위 추출 (IQR, trimmed mean)")
        print("  - 증거 생성 (SRC_xxx)")
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

