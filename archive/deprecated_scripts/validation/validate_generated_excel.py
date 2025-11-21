#!/usr/bin/env python3
"""
생성된 Excel 파일 자동 검증
모든 Excel Generator가 올바르게 작동하는지 확인
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.excel_validator import (
    ExcelValidator,
    GoldenWorkbookValidator,
    validate_excel,
    validate_with_golden
)


def validate_financial_projection_example():
    """Financial Projection 예제 파일 검증"""
    
    filepath = project_root / 'examples' / 'excel' / 'financial_projection_korean_adult_education_example_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath}")
        return False
    
    print("\n" + "="*70)
    print("📊 Financial Projection 예제 검증")
    print("="*70)
    
    # 기본 검증
    validator = ExcelValidator(filepath)
    result = validator.validate()
    
    if not result['passed']:
        return False
    
    # Golden Workbook 검증 (예상 결과)
    expected = {
        'revenue_y0': 1250_0000_0000,  # ₩125억
        'revenue_y5': 4295_0000_0000,  # ₩4,295억 (대략)
        # 더 추가 가능
    }
    
    print("\n" + "="*70)
    print("🎯 Golden Workbook 검증 (예상값 비교)")
    print("="*70)
    
    golden_validator = GoldenWorkbookValidator(filepath, expected)
    golden_result = golden_validator.validate()
    
    return result['passed'] and golden_result['passed']


def validate_unit_economics_example():
    """Unit Economics 예제 파일 검증"""
    
    filepath = project_root / 'examples' / 'excel' / 'unit_economics_music_streaming_example_20251104.xlsx'
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath}")
        return False
    
    print("\n" + "="*70)
    print("📊 Unit Economics 예제 검증")
    print("="*70)
    
    # 기본 검증만 (Golden은 선택)
    result = validate_excel(filepath)
    
    return result


def validate_all_test_outputs():
    """test_output/ 폴더의 모든 Excel 파일 검증"""
    
    test_output = project_root / 'test_output'
    
    if not test_output.exists():
        print("⚠️ test_output 폴더 없음")
        return True
    
    excel_files = list(test_output.glob('*.xlsx'))
    
    if not excel_files:
        print("⚠️ test_output에 Excel 파일 없음")
        return True
    
    print("\n" + "="*70)
    print(f"📊 Test Output 검증 ({len(excel_files)}개 파일)")
    print("="*70)
    
    results = []
    
    for filepath in excel_files[:5]:  # 최대 5개만
        print(f"\n검증 중: {filepath.name}")
        result = validate_excel(filepath)
        results.append(result)
    
    return all(results)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 Excel 자동 검증 시스템")
    print("="*70)
    print("\n목적: 생성된 Excel의 수식, 데이터, 구조 자동 검증")
    print("검증 항목:")
    print("  1. 수식 오류 (자기 참조, 순환 참조)")
    print("  2. 데이터 완성도 (빈 셀)")
    print("  3. Named Range 유효성")
    print("  4. 계산 결과 (예상값 vs 실제값)")
    
    results = []
    
    # 1. Financial Projection 예제 검증
    results.append(validate_financial_projection_example())
    
    # 2. Unit Economics 예제 검증
    results.append(validate_unit_economics_example())
    
    # 3. Test Output 검증 (선택)
    # results.append(validate_all_test_outputs())
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 최종 검증 결과")
    print("="*70)
    print(f"총 {len(results)}개 검증")
    print(f"통과: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")
    
    if all(results):
        print("\n✅ 모든 Excel 파일 검증 통과!")
        print("\n💡 신뢰할 수 있는 Excel 파일입니다.")
        sys.exit(0)
    else:
        print("\n❌ 일부 Excel 파일 검증 실패")
        print("\n⚠️ 생성 코드 수정 필요!")
        sys.exit(1)

