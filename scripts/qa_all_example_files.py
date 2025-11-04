#!/usr/bin/env python3
"""
모든 예제 Excel 파일 QA
3개 도구 × 완성도 검증
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.excel_validator import ExcelValidator


def qa_example_file(filepath: Path, tool_name: str) -> bool:
    """
    예제 파일 QA
    
    Args:
        filepath: 예제 파일 경로
        tool_name: 도구 이름
    
    Returns:
        검증 통과 여부
    """
    
    print("\n" + "="*70)
    print(f"🔍 QA: {tool_name}")
    print("="*70)
    
    if not filepath.exists():
        print(f"❌ 파일 없음: {filepath}")
        return False
    
    print(f"📁 파일: {filepath.name}")
    print(f"📏 크기: {filepath.stat().st_size / 1024:.1f} KB\n")
    
    # 검증 실행
    validator = ExcelValidator(filepath)
    result = validator.validate()
    
    # 결과 요약
    print("\n" + "-"*70)
    print("📊 QA 결과 요약")
    print("-"*70)
    
    print(f"시트 개수: {result['stats']['total_sheets']}개")
    print(f"Named Range: {result['stats']['total_named_ranges']}개")
    print(f"오류: {result['stats']['error_count']}개")
    print(f"경고: {result['stats']['warning_count']}개")
    
    if result['passed']:
        print(f"\n✅ {tool_name}: QA 통과!")
    else:
        print(f"\n❌ {tool_name}: QA 실패!")
        print(f"\n주요 오류:")
        for error in result['errors'][:5]:
            print(f"  {error}")
    
    return result['passed']


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 모든 예제 Excel 파일 QA")
    print("="*70)
    print("\n목표: 3개 도구의 예제 파일 신뢰성 검증")
    print("검증 항목: 자기 참조, 오류 수식, 데이터 완성도, Named Range\n")
    
    examples_dir = project_root / 'examples' / 'excel'
    
    # 3개 예제 파일
    files_to_qa = [
        {
            'path': examples_dir / 'market_sizing_piano_subscription_example_20251104.xlsx',
            'name': 'Market Sizing Workbook'
        },
        {
            'path': examples_dir / 'unit_economics_music_streaming_example_20251104.xlsx',
            'name': 'Unit Economics Analyzer'
        },
        {
            'path': examples_dir / 'financial_projection_korean_adult_education_example_20251104.xlsx',
            'name': 'Financial Projection Model'
        }
    ]
    
    results = {}
    
    for file_info in files_to_qa:
        passed = qa_example_file(file_info['path'], file_info['name'])
        results[file_info['name']] = passed
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 전체 QA 결과")
    print("="*70 + "\n")
    
    for tool_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {tool_name}: {'통과' if passed else '실패'}")
    
    total = len(results)
    passed_count = sum(results.values())
    failed_count = total - passed_count
    
    print(f"\n총 {total}개 예제 파일")
    print(f"✅ 통과: {passed_count}개")
    print(f"❌ 실패: {failed_count}개")
    
    if all(results.values()):
        print("\n" + "="*70)
        print("🎉 모든 예제 파일 QA 통과!")
        print("="*70)
        
        print("\n✅ 신뢰성 확인:")
        print("   - 자기 참조: 0개")
        print("   - 오류 수식: 0개")
        print("   - Named Range: 정상")
        print("   - 데이터 완성도: 충분")
        
        print("\n💡 이제 안심하고 사용할 수 있습니다!")
        print("   - 예제 파일을 템플릿으로 활용")
        print("   - 실제 프로젝트에 적용")
        print("   - 고객/투자자 데모")
        
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ 일부 예제 파일 QA 실패")
        print("="*70)
        
        print("\n⚠️ 실패한 파일:")
        for tool_name, passed in results.items():
            if not passed:
                print(f"   - {tool_name}")
        
        print("\n📋 다음 단계:")
        print("   1. 오류 메시지 확인")
        print("   2. Generator 코드 수정")
        print("   3. 예제 파일 재생성")
        print("   4. QA 재실행")
        
        sys.exit(1)

