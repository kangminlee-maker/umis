#!/usr/bin/env python3
"""
Unit Economics Batch 1 테스트
Inputs + LTV + CAC 시트 생성 테스트
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.unit_economics.unit_economics_generator import UnitEconomicsGenerator


def test_batch1_music_streaming():
    """음악 스트리밍 케이스 테스트"""
    
    print("🧪 Unit Economics Batch 1 테스트 - 음악 스트리밍\n")
    
    generator = UnitEconomicsGenerator()
    
    # 음악 스트리밍 데이터 (실제 사례)
    test_data = {
        'market_name': 'music_streaming',
        'inputs_data': {
            'arpu': 9000,  # ₩9,000/월
            'cac': 25000,  # ₩25,000
            'gross_margin': 0.35,  # 35%
            'monthly_churn': 0.04,  # 4%/월
            'customer_lifetime': 25,  # 25개월
            'sm_spend_monthly': 5000000,  # ₩5,000,000/월
            'new_customers_monthly': 200  # 200명/월
        },
        'channels_data': [
            {'channel': '검색 광고', 'spend': 2000000, 'customers': 80},
            {'channel': 'SNS 광고', 'spend': 1500000, 'customers': 60},
            {'channel': '제휴 마케팅', 'spend': 1000000, 'customers': 40},
            {'channel': '오프라인', 'spend': 500000, 'customers': 20},
        ],
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        # 파일 존재 확인
        if filepath.exists():
            print(f"✅ 파일 생성 확인: {filepath.stat().st_size} bytes")
            
            # 예상 결과
            print(f"\n📊 예상 결과:")
            print(f"   LTV (방법 1): ₩{9000 * 25 * 0.35:,.0f} = ₩78,750")
            print(f"   LTV (방법 2): ₩{9000 * 0.35 / 0.04:,.0f} = ₩78,750")
            print(f"   LTV (평균): ₩78,750")
            print(f"   CAC (계산): ₩{5000000 / 200:,.0f} = ₩25,000")
            print(f"   LTV/CAC: {78750 / 25000:.1f} = 3.2 ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch1_saas():
    """SaaS 케이스 테스트"""
    
    print("\n" + "="*60)
    print("🧪 Unit Economics Batch 1 테스트 - SaaS\n")
    
    generator = UnitEconomicsGenerator()
    
    # SaaS 데이터
    test_data = {
        'market_name': 'saas_b2b',
        'inputs_data': {
            'arpu': 50000,  # ₩50,000/월
            'cac': 200000,  # ₩200,000
            'gross_margin': 0.75,  # 75%
            'monthly_churn': 0.03,  # 3%/월
            'customer_lifetime': 33,  # 33개월
            'sm_spend_monthly': 10000000,  # ₩10,000,000/월
            'new_customers_monthly': 50  # 50개 기업/월
        },
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        if filepath.exists():
            print(f"✅ 파일 생성 확인: {filepath.stat().st_size} bytes")
            
            # 예상 결과
            print(f"\n📊 예상 결과:")
            print(f"   LTV (방법 1): ₩{50000 * 33 * 0.75:,.0f} = ₩1,237,500")
            print(f"   LTV (방법 2): ₩{50000 * 0.75 / 0.03:,.0f} = ₩1,250,000")
            print(f"   LTV (평균): ₩1,243,750")
            print(f"   CAC (계산): ₩{10000000 / 50:,.0f} = ₩200,000")
            print(f"   LTV/CAC: {1243750 / 200000:.1f} = 6.2 ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Unit Economics Batch 1 테스트")
    print("="*60 + "\n")
    
    results = []
    
    # 테스트 1: 음악 스트리밍
    results.append(test_batch1_music_streaming())
    
    # 테스트 2: SaaS
    results.append(test_batch1_saas())
    
    # 결과
    print("\n" + "="*60)
    print("테스트 결과")
    print("="*60)
    print(f"총 {len(results)}개 테스트")
    print(f"성공: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")
    
    if all(results):
        print("\n✅ 모든 테스트 통과!")
        print("\n📋 다음 단계:")
        print("   - Excel 파일 열어서 함수 작동 확인")
        print("   - Batch 2 진행 (Ratio, Payback, Sensitivity)")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)

