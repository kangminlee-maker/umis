#!/usr/bin/env python3
"""
모든 Excel Generator 테스트 및 검증
생성 → 즉시 검증으로 신뢰성 확보
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.market_sizing_generator import MarketSizingWorkbookGenerator
from umis_rag.deliverables.excel.unit_economics import UnitEconomicsGenerator
from umis_rag.deliverables.excel.financial_projection import FinancialProjectionGenerator
from umis_rag.deliverables.excel.excel_validator import validate_excel


def test_market_sizing():
    """Market Sizing 생성 및 검증"""
    
    print("\n" + "="*70)
    print("1️⃣ Market Sizing Workbook 테스트")
    print("="*70)
    
    generator = MarketSizingWorkbookGenerator()
    
    # 테스트 데이터
    test_data = {
        'market_name': 'test_market_sizing',
        'assumptions': [
            {'id': 'TAM_VALUE', 'category': 'TAM', 'description': '글로벌 시장',
             'value': 1000_0000_0000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_001', 'confidence': 'High'},
            {'id': 'FILTER_KOREA', 'category': '지역', 'description': '한국',
             'value': 0.15, 'unit': '%', 'data_type': '직접데이터',
             'source': 'SRC_002', 'confidence': 'High'},
        ],
        'tam': {
            'value': 1000_0000_0000,
            'definition': '글로벌 시장',
            'source': 'TAM_VALUE',
            'narrowing_steps': [
                {'dimension': '지역', 'ratio_source': 'FILTER_KOREA', 'description': '한국 15%'},
            ]
        },
        'segments': [
            {'name': '세그먼트1', 'target_customers': 'SEG1_CUSTOMERS',
             'purchase_rate': 'SEG1_RATE', 'aov': 'SEG1_AOV', 'frequency': 'SEG1_FREQ'}
        ],
        'proxy_data': {'proxy_market': 'PROXY_SIZE', 'correlation': 'PROXY_CORR',
                      'application_rate': 'PROXY_APP'},
        'competitors': [
            {'company': '경쟁사A', 'revenue': 'COMP1_REV', 'market_share': 'COMP1_SHARE'}
        ],
        'output_dir': Path('test_output')
    }
    
    # 누락된 assumptions 추가
    test_data['assumptions'].extend([
        {'id': 'SEG1_CUSTOMERS', 'category': '세그먼트1', 'description': '고객',
         'value': 100000, 'unit': '명', 'data_type': '추정치',
         'source': 'EST_001', 'confidence': 'Medium'},
        {'id': 'SEG1_RATE', 'category': '세그먼트1', 'description': '구매율',
         'value': 0.2, 'unit': '%', 'data_type': '추정치',
         'source': 'EST_002', 'confidence': 'Medium'},
        {'id': 'SEG1_AOV', 'category': '세그먼트1', 'description': '객단가',
         'value': 50000, 'unit': '원', 'data_type': '직접데이터',
         'source': 'SRC_004', 'confidence': 'High'},
        {'id': 'SEG1_FREQ', 'category': '세그먼트1', 'description': '구매빈도',
         'value': 2, 'unit': '회', 'data_type': '추정치',
         'source': 'EST_003', 'confidence': 'Medium'},
        {'id': 'PROXY_SIZE', 'category': 'Proxy', 'description': '유사 시장',
         'value': 500_0000_0000, 'unit': '원', 'data_type': '직접데이터',
         'source': 'SRC_005', 'confidence': 'Medium'},
        {'id': 'PROXY_CORR', 'category': 'Proxy', 'description': '상관계수',
         'value': 0.3, 'unit': '', 'data_type': '추정치',
         'source': 'EST_004', 'confidence': 'Low'},
        {'id': 'PROXY_APP', 'category': 'Proxy', 'description': '적용비율',
         'value': 0.5, 'unit': '%', 'data_type': '추정치',
         'source': 'EST_005', 'confidence': 'Medium'},
        {'id': 'COMP1_REV', 'category': '경쟁사1', 'description': '매출',
         'value': 100_0000_0000, 'unit': '원', 'data_type': '직접데이터',
         'source': 'SRC_006', 'confidence': 'High'},
        {'id': 'COMP1_SHARE', 'category': '경쟁사1', 'description': '점유율',
         'value': 0.4, 'unit': '%', 'data_type': '추정치',
         'source': 'EST_006', 'confidence': 'Medium'},
    ])
    
    try:
        # 생성
        filepath = generator.generate(**test_data)
        print(f"✅ 생성 완료: {filepath.name}")
        
        # 검증
        print(f"\n🔍 검증 시작...")
        passed = validate_excel(filepath)
        
        return passed
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unit_economics():
    """Unit Economics 생성 및 검증"""
    
    print("\n" + "="*70)
    print("2️⃣ Unit Economics Analyzer 테스트")
    print("="*70)
    
    generator = UnitEconomicsGenerator()
    
    test_data = {
        'market_name': 'test_unit_economics',
        'inputs_data': {
            'arpu': 10000,
            'cac': 30000,
            'gross_margin': 0.40,
            'monthly_churn': 0.05,
            'customer_lifetime': 20,
            'sm_spend_monthly': 10_0000_000,
            'new_customers_monthly': 300
        },
        'industry': 'SaaS',
        'output_dir': Path('test_output')
    }
    
    try:
        # 생성
        filepath = generator.generate(**test_data)
        print(f"✅ 생성 완료: {filepath.name}")
        
        # 검증
        print(f"\n🔍 검증 시작...")
        passed = validate_excel(filepath)
        
        return passed
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_financial_projection():
    """Financial Projection 생성 및 검증"""
    
    print("\n" + "="*70)
    print("3️⃣ Financial Projection Model 테스트")
    print("="*70)
    
    generator = FinancialProjectionGenerator()
    
    test_data = {
        'market_name': 'test_financial_projection',
        'assumptions_data': {
            'base_revenue_y0': 1000_0000_0000,
            'growth_rate_yoy': 0.25,
            'gross_margin': 0.60,
            'ebitda_margin': 0.12,
            'net_margin': 0.08,
            'sm_percent': 0.25,
            'rd_percent': 0.12,
            'ga_percent': 0.08,
            'tax_rate': 0.25,
            'discount_rate': 0.10
        },
        'segments': [
            {'name': 'Segment1', 'y0_revenue': 600_0000_0000, 'growth': 0.20},
            {'name': 'Segment2', 'y0_revenue': 400_0000_0000, 'growth': 0.30},
        ],
        'years': 5,
        'output_dir': Path('test_output')
    }
    
    try:
        # 생성
        filepath = generator.generate(**test_data)
        print(f"✅ 생성 완료: {filepath.name}")
        
        # 검증
        print(f"\n🔍 검증 시작...")
        passed = validate_excel(filepath)
        
        return passed
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 모든 Excel Generator 테스트 + 자동 검증")
    print("="*70)
    print("\n전략: 생성 → 즉시 검증 → 신뢰성 확보")
    
    results = {}
    
    # 1. Market Sizing
    results['Market Sizing'] = test_market_sizing()
    
    # 2. Unit Economics
    results['Unit Economics'] = test_unit_economics()
    
    # 3. Financial Projection
    results['Financial Projection'] = test_financial_projection()
    
    # 최종 결과
    print("\n" + "="*70)
    print("🏁 전체 검증 결과")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {'통과' if passed else '실패'}")
    
    total = len(results)
    passed_count = sum(results.values())
    
    print(f"\n총 {total}개 Generator")
    print(f"통과: {passed_count}개")
    print(f"실패: {total - passed_count}개")
    
    if all(results.values()):
        print("\n✅ 모든 Excel Generator 검증 통과!")
        print("\n💡 신뢰할 수 있는 Excel 생성 시스템입니다.")
        sys.exit(0)
    else:
        print("\n❌ 일부 Generator 검증 실패")
        print("\n⚠️ 수식 오류 수정 필요!")
        sys.exit(1)

