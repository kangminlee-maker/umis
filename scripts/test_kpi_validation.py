#!/usr/bin/env python3
"""
KPI 정의 검증 테스트
Rachel Validator의 s10 Industry KPI Library
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.validator import ValidatorRAG


def test_kpi_match():
    """Test 1: 완전 일치"""
    print("\n" + "=" * 70)
    print("Test 1: 플랫폼 수수료율 - 완전 일치")
    print("=" * 70)
    
    rachel = ValidatorRAG()
    
    result = rachel.validate_kpi_definition(
        metric_name="플랫폼 수수료율",
        provided_definition={
            'numerator': "플랫폼 중개 수수료 (KRW)",
            'denominator': "거래 금액 (KRW)",
            'unit': "%",
            'scope': {
                'includes': ["중개 수수료", "거래 촉진 수수료"],
                'excludes': ["광고비", "배달비", "결제 수수료"]
            }
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  상태: {result['status']}")
    print(f"  KPI ID: {result['kpi_id']}")
    print(f"  비교 가능성: {result['comparability_score']*100:.0f}%")
    print(f"  권고: {result['recommendation']}")
    print(f"  Gap: {len(result['gaps'])}개")
    
    # 검증
    assert result['status'] == 'match', "완전 일치여야 함"
    assert result['comparability_score'] == 1.0, "비교 가능성 100%"
    assert len(result['gaps']) == 0, "Gap 없어야 함"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_kpi_mismatch_numerator():
    """Test 2: 분자 불일치"""
    print("\n" + "=" * 70)
    print("Test 2: 플랫폼 수수료율 - 분자 불일치")
    print("=" * 70)
    
    rachel = ValidatorRAG()
    
    result = rachel.validate_kpi_definition(
        metric_name="플랫폼 수수료율",
        provided_definition={
            'numerator': "총 수수료 (광고 포함)",  # ← 다름!
            'denominator': "거래 금액 (KRW)",
            'unit': "%",
            'scope': {
                'includes': ["중개 수수료"],
                'excludes': ["배달비"]
            }
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  상태: {result['status']}")
    print(f"  비교 가능성: {result['comparability_score']*100:.0f}%")
    print(f"  Gap: {len(result['gaps'])}개")
    
    if result['gaps']:
        print(f"\n  Gap 상세:")
        for gap in result['gaps']:
            print(f"    - {gap['field']} (severity: {gap['severity']})")
            print(f"      제공: {gap.get('provided', 'N/A')}")
            print(f"      표준: {gap.get('standard', 'N/A')}")
    
    print(f"\n  권고: {result['recommendation']}")
    
    # 검증
    assert result['status'] == 'mismatch', "불일치여야 함"
    assert result['comparability_score'] < 1.0, "비교 가능성 낮음"
    assert any(g['field'] == 'numerator' for g in result['gaps']), "분자 Gap 존재"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_kpi_partial_match():
    """Test 3: 부분 일치 (scope만 다름)"""
    print("\n" + "=" * 70)
    print("Test 3: 플랫폼 수수료율 - 부분 일치")
    print("=" * 70)
    
    rachel = ValidatorRAG()
    
    result = rachel.validate_kpi_definition(
        metric_name="플랫폼 수수료율",
        provided_definition={
            'numerator': "플랫폼 중개 수수료 (KRW)",
            'denominator': "거래 금액 (KRW)",
            'unit': "%",
            'scope': {
                'includes': ["중개 수수료"],  # "거래 촉진 수수료" 누락
                'excludes': ["광고비"]  # "배달비", "결제 수수료" 누락
            }
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  상태: {result['status']}")
    print(f"  비교 가능성: {result['comparability_score']*100:.0f}%")
    print(f"  Gap: {len(result['gaps'])}개")
    
    if result['gaps']:
        print(f"\n  Gap 상세:")
        for gap in result['gaps']:
            print(f"    - {gap['field']} (severity: {gap['severity']})")
            if 'missing' in gap:
                print(f"      누락: {gap['missing']}")
    
    # 검증
    assert result['status'] == 'partial_match' or result['status'] == 'mismatch', "부분 일치 또는 불일치"
    assert len(result['gaps']) > 0, "Gap 존재"
    
    print("\n✅ Test 3 PASSED")
    return result


def test_kpi_not_found():
    """Test 4: KPI 없음"""
    print("\n" + "=" * 70)
    print("Test 4: 존재하지 않는 KPI")
    print("=" * 70)
    
    rachel = ValidatorRAG()
    
    result = rachel.validate_kpi_definition(
        metric_name="존재하지_않는_메트릭",
        provided_definition={
            'numerator': "무언가",
            'denominator': "무언가",
            'unit': "%"
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  상태: {result['status']}")
    print(f"  메시지: {result.get('message', 'N/A')}")
    print(f"  권고: {result.get('recommendation', 'N/A')}")
    print(f"  신규 생성 필요: {result.get('create_new', False)}")
    
    # 검증
    assert result['status'] == 'not_found', "not_found여야 함"
    assert result.get('create_new') == True, "신규 생성 제안"
    
    print("\n✅ Test 4 PASSED")
    return result


def test_churn_rate():
    """Test 5: 월간 해지율"""
    print("\n" + "=" * 70)
    print("Test 5: 월간 해지율 검증")
    print("=" * 70)
    
    rachel = ValidatorRAG()
    
    result = rachel.validate_kpi_definition(
        metric_name="월간 해지율",
        provided_definition={
            'numerator': "월간 해지 고객 수",
            'denominator': "월초 총 고객 수",
            'unit': "%",
            'scope': {
                'includes': ["자발적 해지", "비자발적 해지 (결제 실패)"],
                'excludes': ["무료 체험 해지"]
            }
        }
    )
    
    print(f"\n📊 결과:")
    print(f"  상태: {result['status']}")
    print(f"  KPI ID: {result.get('kpi_id', 'N/A')}")
    print(f"  비교 가능성: {result.get('comparability_score', 0)*100:.0f}%")
    print(f"  권고: {result.get('recommendation', 'N/A')}")
    
    # 검증
    assert result['status'] in ['match', 'partial_match'], "일치 또는 부분 일치"
    
    print("\n✅ Test 5 PASSED")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("KPI 정의 검증 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: 완전 일치", test_kpi_match),
        ("Test 2: 분자 불일치", test_kpi_mismatch_numerator),
        ("Test 3: 부분 일치", test_kpi_partial_match),
        ("Test 4: KPI 없음", test_kpi_not_found),
        ("Test 5: 해지율", test_churn_rate),
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
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

