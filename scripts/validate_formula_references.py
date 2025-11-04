#!/usr/bin/env python3
"""
수식 참조 검증
Summary 시트의 모든 참조가 의도한 셀을 참조하는지 확인
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.formula_reference_validator import FormulaReferenceValidator


def validate_market_sizing():
    """Market Sizing 참조 검증"""
    
    filepath = project_root / 'examples' / 'excel' / 'market_sizing_piano_subscription_example_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음")
        return False
    
    validator = FormulaReferenceValidator(filepath)
    result = validator.validate()
    
    return result['passed']


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 수식 참조 검증 시스템")
    print("="*70)
    print("\n목적: 수식이 의도한 셀을 정확히 참조하는지 확인")
    print("검증: Summary!B23 = =Scenarios!B13")
    print("  → Scenarios!B13에 뭐가 있나?")
    print("  → 'Proxy Corr' vs 기대값 'Average SAM'")
    print("  → 불일치하면 오류!\n")
    
    # Market Sizing 검증
    passed = validate_market_sizing()
    
    if passed:
        print("\n✅ 모든 참조 검증 통과!")
        sys.exit(0)
    else:
        print("\n❌ 참조 오류 발견!")
        print("\n💡 다음 단계:")
        print("  1. 오류 메시지에서 잘못된 참조 확인")
        print("  2. Generator 코드에서 해당 셀 참조 수정")
        print("  3. 재생성 후 다시 검증")
        sys.exit(1)

