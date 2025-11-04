#!/usr/bin/env python3
"""
Golden Test: 결과 중심 검증
모든 Excel 파일을 CALCULATED 버전으로 Golden Test
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.golden_test_framework import (
    GoldenTestRunner,
    GoldenTestSpec
)


def test_market_sizing():
    """Market Sizing Golden Test"""
    
    # CALCULATED 버전 사용 (값이 계산되어 있음)
    filepath = project_root / 'examples' / 'excel' / 'market_sizing_piano_subscription_CALCULATED_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath.name}")
        print("   먼저 populate_all_excel_values.py 실행 필요")
        return False
    
    spec = GoldenTestSpec.get_market_sizing_spec()
    runner = GoldenTestRunner(filepath, spec)
    result = runner.run()
    
    return result['passed']


def test_unit_economics():
    """Unit Economics Golden Test"""
    
    filepath = project_root / 'examples' / 'excel' / 'unit_economics_CALCULATED_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath.name}")
        return False
    
    spec = GoldenTestSpec.get_unit_economics_spec()
    runner = GoldenTestRunner(filepath, spec)
    result = runner.run()
    
    return result['passed']


def test_financial_projection():
    """Financial Projection Golden Test"""
    
    filepath = project_root / 'examples' / 'excel' / 'financial_projection_CALCULATED_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath.name}")
        return False
    
    spec = GoldenTestSpec.get_financial_projection_spec()
    runner = GoldenTestRunner(filepath, spec)
    result = runner.run()
    
    return result['passed']


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 Golden Test: 결과 중심 검증")
    print("="*70)
    print("\n전략: Syntax + Golden Values 병행")
    print("  1. Syntax 검증 (자기 참조, 오류 수식)")
    print("  2. Golden Values 검증 (기대값 vs 실제값) ⭐")
    print("  3. 논리적 일관성 검증 (TAM > SAM 등)\n")
    
    results = {}
    
    # 1. Market Sizing
    results['Market Sizing'] = test_market_sizing()
    
    # 2. Unit Economics
    results['Unit Economics'] = test_unit_economics()
    
    # 3. Financial Projection
    results['Financial Projection'] = test_financial_projection()
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 Golden Test 최종 결과")
    print("="*70 + "\n")
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {'통과' if passed else '실패'}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n총 {total_count}개")
    print(f"통과: {passed_count}개")
    print(f"실패: {total_count - passed_count}개")
    
    if all(results.values()):
        print("\n✅ 모든 Golden Test 통과!")
        print("\n💡 신뢰할 수 있는 Excel:")
        print("   - Syntax 정상 (자기 참조 0개)")
        print("   - 결과 정확 (기대값과 일치)")
        print("   - 논리 일관 (TAM > SAM 등)")
        sys.exit(0)
    else:
        print("\n❌ 일부 Golden Test 실패")
        print("\n⚠️ 논리적 오류 수정 필요!")
        sys.exit(1)

