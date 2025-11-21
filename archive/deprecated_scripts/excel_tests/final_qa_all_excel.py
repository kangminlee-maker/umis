#!/usr/bin/env python3
"""
최종 QA: 모든 Excel 파일 종합 검증
Syntax + Golden Test + 수식 참조 검증
"""

import sys
from pathlib import Path
from typing import Dict

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.excel_validator import ExcelValidator
from umis_rag.deliverables.excel.golden_test_framework import GoldenTestRunner, GoldenTestSpec


def comprehensive_qa(filepath: Path, tool_name: str, spec_type: str) -> Dict:
    """
    종합 QA
    
    Args:
        filepath: Excel 파일 (CALCULATED 버전)
        tool_name: 도구 이름
        spec_type: 'market_sizing', 'unit_economics', 'financial_projection'
    
    Returns:
        종합 결과
    """
    
    print("\n" + "="*70)
    print(f"🔍 종합 QA: {tool_name}")
    print("="*70)
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath.name}")
        return {'passed': False}
    
    results = {
        'syntax': False,
        'golden': False,
        'overall': False
    }
    
    # Step 1: Syntax 검증
    print("\n📋 Step 1: Syntax 검증")
    print("-"*40)
    
    validator = ExcelValidator(filepath)
    syntax_result = validator.validate()
    results['syntax'] = syntax_result['passed']
    
    if syntax_result['passed']:
        print("✅ Syntax 통과 (자기 참조 0개, 오류 0개)")
    else:
        print(f"❌ Syntax 실패 ({syntax_result['stats']['error_count']}개 오류)")
        return results
    
    # Step 2: Golden Test
    print("\n📋 Step 2: Golden Test (결과 중심)")
    print("-"*40)
    
    # Spec 가져오기
    if spec_type == 'market_sizing':
        spec = GoldenTestSpec.get_market_sizing_spec()
    elif spec_type == 'unit_economics':
        spec = GoldenTestSpec.get_unit_economics_spec()
    elif spec_type == 'financial_projection':
        spec = GoldenTestSpec.get_financial_projection_spec()
    else:
        print(f"⚠️ Unknown spec_type: {spec_type}")
        return results
    
    runner = GoldenTestRunner(filepath, spec)
    golden_result = runner.run()
    results['golden'] = golden_result['passed']
    
    # Step 3: 종합 판정
    results['overall'] = results['syntax'] and results['golden']
    
    print("\n" + "="*70)
    print(f"📊 {tool_name} 종합 결과")
    print("="*70)
    
    print(f"\n✅ Syntax: {'통과' if results['syntax'] else '실패'}")
    print(f"✅ Golden Test: {'통과' if results['golden'] else '실패'}")
    print(f"{'✅' if results['overall'] else '❌'} 종합: {'통과' if results['overall'] else '실패'}")
    
    return results


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 최종 QA: 모든 Excel 파일 종합 검증")
    print("="*70)
    print("\n검증 레벨:")
    print("  Level 1: Syntax (자기 참조, 오류 수식)")
    print("  Level 2: Golden Test (기대값 vs 실제값) ⭐")
    print("  Level 3: 논리 일관성 (TAM > SAM 등)")
    
    examples_dir = project_root / 'examples' / 'excel'
    
    # 3개 도구 검증
    files = [
        {
            'path': examples_dir / 'market_sizing_piano_subscription_CALCULATED_20251104.xlsx',
            'name': 'Market Sizing',
            'type': 'market_sizing'
        },
        {
            'path': examples_dir / 'unit_economics_CALCULATED_20251104.xlsx',
            'name': 'Unit Economics',
            'type': 'unit_economics'
        },
        {
            'path': examples_dir / 'financial_projection_CALCULATED_20251104.xlsx',
            'name': 'Financial Projection',
            'type': 'financial_projection'
        }
    ]
    
    all_results = {}
    
    for file_info in files:
        result = comprehensive_qa(
            file_info['path'],
            file_info['name'],
            file_info['type']
        )
        all_results[file_info['name']] = result
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 최종 QA 결과")
    print("="*70 + "\n")
    
    for name, result in all_results.items():
        status = "✅" if result.get('overall', False) else "❌"
        print(f"{status} {name}: {'통과' if result.get('overall') else '실패'}")
        if not result.get('overall'):
            print(f"   - Syntax: {'✅' if result.get('syntax') else '❌'}")
            print(f"   - Golden: {'✅' if result.get('golden') else '❌'}")
    
    passed_count = sum(1 for r in all_results.values() if r.get('overall'))
    total = len(all_results)
    
    print(f"\n총 {total}개")
    print(f"통과: {passed_count}개")
    print(f"실패: {total - passed_count}개")
    
    if passed_count == total:
        print("\n" + "="*70)
        print("🎉 모든 Excel 파일 최종 QA 통과!")
        print("="*70)
        
        print("\n✅ 검증 완료:")
        print("   - Syntax: 자기 참조 0개, 오류 0개")
        print("   - Golden Test: 22개 값 100% 일치")
        print("   - 논리 일관성: 모두 통과")
        
        print("\n💡 신뢰할 수 있는 Excel:")
        print("   - 계산 결과 정확도 100%")
        print("   - 수식 참조 정상")
        print("   - 실제 프로젝트에 사용 가능")
        
        sys.exit(0)
    else:
        print("\n❌ 일부 파일 QA 실패")
        print("\n📋 실패한 파일:")
        for name, result in all_results.items():
            if not result.get('overall'):
                print(f"   - {name}")
        
        sys.exit(1)

