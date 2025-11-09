#!/usr/bin/env python3
"""
Signal10 Industry KPI 테스트
Rachel Validator 연동 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.methodologies.domain_reasoner import Signal10_IndustryKPI


def test_platform_commission():
    """Test 1: 플랫폼 수수료율 정의"""
    print("\n" + "=" * 70)
    print("Test 1: 플랫폼 수수료율 정의 명확화")
    print("=" * 70)
    
    signal = Signal10_IndustryKPI()
    
    result = signal.clarify_definition(
        question="국내 음식 배달 플랫폼 평균 수수료율",
        domain="platform"
    )
    
    print(f"\n📊 결과:")
    print(f"  KPI ID: {result['kpi_id']}")
    print(f"  Metric Name: {result['metric_name']}")
    print(f"  Status: {result['status']}")
    print(f"  Comparability: {result['comparability_score']:.2f}")
    
    if result['standard_definition']:
        std_def = result['standard_definition']
        print(f"\n  표준 정의:")
        if 'definition' in std_def:
            defn = std_def['definition']
            if isinstance(defn, dict):
                print(f"    한국어: {defn.get('korean', 'N/A')}")
            else:
                print(f"    {defn}")
        
        if 'formula' in std_def:
            formula = std_def['formula']
            print(f"\n  공식:")
            if isinstance(formula, dict):
                print(f"    분자: {formula.get('numerator', 'N/A')}")
                print(f"    분모: {formula.get('denominator', 'N/A')}")
    
    assert result['kpi_id'].startswith('KPI_'), "KPI ID 형식"
    assert result['metric_name'] == '플랫폼 수수료율', "메트릭 이름 추출"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_churn_rate():
    """Test 2: 월간 해지율 정의"""
    print("\n" + "=" * 70)
    print("Test 2: 월간 해지율 정의 명확화")
    print("=" * 70)
    
    signal = Signal10_IndustryKPI()
    
    result = signal.clarify_definition(
        question="B2C SaaS 월간 해지율은 얼마?",
        domain="subscription"
    )
    
    print(f"\n📊 결과:")
    print(f"  KPI ID: {result['kpi_id']}")
    print(f"  Metric Name: {result['metric_name']}")
    print(f"  Status: {result['status']}")
    
    assert '해지' in result['metric_name'] or 'Churn' in result['metric_name'], "메트릭 이름 확인"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_market_size():
    """Test 3: 시장 규모 정의"""
    print("\n" + "=" * 70)
    print("Test 3: 시장 규모 정의 명확화")
    print("=" * 70)
    
    signal = Signal10_IndustryKPI()
    
    result = signal.clarify_definition(
        question="음악 스트리밍 시장 규모 SAM",
        domain="music"
    )
    
    print(f"\n📊 결과:")
    print(f"  KPI ID: {result['kpi_id']}")
    print(f"  Metric Name: {result['metric_name']}")
    print(f"  Status: {result['status']}")
    
    assert '시장' in result['metric_name'] or 'Market' in result['metric_name'], "메트릭 이름 확인"
    
    print("\n✅ Test 3 PASSED")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("Signal10 Industry KPI 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: 플랫폼 수수료율", test_platform_commission),
        ("Test 2: 월간 해지율", test_churn_rate),
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
        print("\n✅ s10_industry_kpi 연동 완료:")
        print("  - Rachel Validator.validate_kpi_definition() 활용")
        print("  - KPI 정의 자동 조회 (10개 라이브러리)")
        print("  - 메트릭 이름 자동 추출")
        print("  - 표준 정의 반환")
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

