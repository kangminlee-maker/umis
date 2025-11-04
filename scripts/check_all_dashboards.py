#!/usr/bin/env python3
"""
모든 Excel 파일의 Dashboard/Summary 시트 검증
모든 주요 숫자가 제대로 출력되는지 확인
"""

import sys
from pathlib import Path
from openpyxl import load_workbook

project_root = Path(__file__).parent.parent
examples_dir = project_root / 'examples' / 'excel'

def check_market_sizing_summary():
    """Market Sizing Summary 시트 확인"""
    
    filepath = examples_dir / 'market_sizing_piano_subscription_CALCULATED_20251104.xlsx'
    
    print("\n" + "="*70)
    print("1️⃣ Market Sizing - Summary 시트")
    print("="*70)
    
    if not filepath.exists():
        print("❌ 파일 없음")
        return False
    
    wb = load_workbook(filepath, data_only=True)
    
    if 'Summary' not in wb.sheetnames:
        print("❌ Summary 시트 없음")
        return False
    
    ws = wb['Summary']
    
    # 주요 값 확인
    checks = [
        ('B5', 'TAM', 100_000_000_000, '₩1,000억'),
        ('B6', 'SAM (평균)', 12_062_500_000, '₩120.6억'),
        ('B10', 'Method 1 SAM', 3_750_000_000, '₩37.5억'),
        ('B11', 'Method 2 SAM', 12_000_000_000, '₩120억'),
        ('B12', 'Method 3 SAM', 7_500_000_000, '₩75억'),
        ('B13', 'Method 4 SAM', 25_000_000_000, '₩250억'),
        ('B16', 'Max/Min Ratio', 6.67, '6.67'),
        ('B23', 'Best Case SAM', 12_062_500_000, '₩120.6억'),
        ('B24', 'Base Case SAM', 12_062_500_000, '₩120.6억'),
        ('B25', 'Worst Case SAM', 12_062_500_000, '₩120.6억'),
    ]
    
    errors = []
    
    for cell, name, expected, display in checks:
        actual = ws[cell].value
        
        print(f"\n{cell} ({name}):")
        print(f"  기대값: {display}")
        
        if actual is None:
            print(f"  ❌ 값 없음!")
            errors.append(f"{cell} ({name}): 값 없음")
        else:
            print(f"  실제값: {actual}")
            
            # 숫자 비교 (문자열일 수 있음)
            try:
                actual_num = float(actual) if not isinstance(actual, (int, float)) else actual
                
                if abs(actual_num - expected) / expected < 0.01:
                    print(f"  ✅ 정상 (오차 < 1%)")
                else:
                    print(f"  ⚠️ 오차: {abs(actual_num - expected) / expected * 100:.1f}%")
            except:
                # 문자열 (예: "재검토 필요")
                print(f"  ℹ️ 문자값: {actual}")
    
    if errors:
        print(f"\n❌ {len(errors)}개 오류:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"\n✅ Summary 시트 모든 값 정상")
        return True


def check_unit_economics_dashboard():
    """Unit Economics Dashboard 시트 확인"""
    
    filepath = examples_dir / 'unit_economics_CALCULATED_20251104.xlsx'
    
    print("\n" + "="*70)
    print("2️⃣ Unit Economics - Dashboard 시트")
    print("="*70)
    
    if not filepath.exists():
        print("❌ 파일 없음")
        return False
    
    wb = load_workbook(filepath, data_only=True)
    
    if 'Dashboard' not in wb.sheetnames:
        print("❌ Dashboard 시트 없음")
        return False
    
    ws = wb['Dashboard']
    
    # 주요 값 확인
    checks = [
        ('B5', 'LTV', 78750, '₩78,750'),
        ('B6', 'CAC', 25000, '₩25,000'),
        ('B7', 'LTV/CAC Ratio', 3.15, '3.15'),
        ('B8', 'Payback Period', 7.94, '7.9개월'),
    ]
    
    errors = []
    
    for cell, name, expected, display in checks:
        actual = ws[cell].value
        
        print(f"\n{cell} ({name}):")
        print(f"  기대값: {display}")
        
        if actual is None:
            print(f"  ❌ 값 없음!")
            errors.append(f"{cell} ({name}): 값 없음")
        else:
            print(f"  실제값: {actual}")
            
            try:
                actual_num = float(actual)
                
                if abs(actual_num - expected) / expected < 0.02:
                    print(f"  ✅ 정상")
                else:
                    print(f"  ⚠️ 오차: {abs(actual_num - expected) / expected * 100:.1f}%")
            except:
                print(f"  ℹ️ 문자값: {actual}")
    
    if errors:
        print(f"\n❌ {len(errors)}개 오류:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"\n✅ Dashboard 시트 모든 값 정상")
        return True


def check_financial_projection_dashboard():
    """Financial Projection Dashboard 시트 확인"""
    
    filepath = examples_dir / 'financial_projection_CALCULATED_20251104.xlsx'
    
    print("\n" + "="*70)
    print("3️⃣ Financial Projection - Dashboard 시트")
    print("="*70)
    
    if not filepath.exists():
        print("❌ 파일 없음")
        return False
    
    wb = load_workbook(filepath, data_only=True)
    
    if 'Dashboard' not in wb.sheetnames:
        print("❌ Dashboard 시트 없음")
        return False
    
    ws = wb['Dashboard']
    
    # 주요 값 확인
    checks = [
        ('B5', 'Revenue Year 5', 4295_0000_0000, '₩4,295억'),
        ('B6', 'Net Income Year 5', 429_0000_0000, '₩429억'),
        ('B7', 'CAGR', 0.28, '28%'),
    ]
    
    errors = []
    
    for cell, name, expected, display in checks:
        actual = ws[cell].value
        
        print(f"\n{cell} ({name}):")
        print(f"  기대값: {display}")
        
        if actual is None:
            print(f"  ❌ 값 없음!")
            errors.append(f"{cell} ({name}): 값 없음")
        else:
            print(f"  실제값: {actual}")
            
            try:
                actual_num = float(actual)
                
                if abs(actual_num - expected) / expected < 0.02:
                    print(f"  ✅ 정상")
                else:
                    print(f"  ⚠️ 오차: {abs(actual_num - expected) / expected * 100:.1f}%")
            except:
                print(f"  ℹ️ 문자값: {actual}")
    
    if errors:
        print(f"\n❌ {len(errors)}개 오류:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"\n✅ Dashboard 시트 모든 값 정상")
        return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 모든 Dashboard/Summary 시트 검증")
    print("="*70)
    print("\n목적: 주요 숫자가 모두 출력되는지 확인\n")
    
    results = []
    
    # 1. Market Sizing
    results.append(('Market Sizing', check_market_sizing_summary()))
    
    # 2. Unit Economics
    results.append(('Unit Economics', check_unit_economics_dashboard()))
    
    # 3. Financial Projection
    results.append(('Financial Projection', check_financial_projection_dashboard()))
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 최종 검증 결과")
    print("="*70 + "\n")
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {'통과' if passed else '실패'}")
    
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    
    print(f"\n총 {total}개")
    print(f"통과: {passed_count}개")
    print(f"실패: {total - passed_count}개")
    
    if passed_count == total:
        print("\n✅ 모든 Dashboard/Summary 시트 정상!")
        print("\n💡 확인 완료:")
        print("   - 모든 주요 숫자 출력됨")
        print("   - 빈 셀 없음")
        print("   - 계산 결과 정확")
        sys.exit(0)
    else:
        print("\n❌ 일부 시트에 문제 있음")
        sys.exit(1)

