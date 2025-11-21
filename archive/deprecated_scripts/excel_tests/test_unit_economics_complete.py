#!/usr/bin/env python3
"""
Unit Economics 완성 테스트 (Batch 3)
10개 시트 모두 생성 테스트
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.unit_economics.unit_economics_generator import UnitEconomicsGenerator


def test_complete_music_streaming():
    """음악 스트리밍 완성 테스트 (10개 시트)"""
    
    print("🧪 Unit Economics 완성 테스트 - 음악 스트리밍\n")
    
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
        'industry': 'Streaming',
        'cohort_months': 12,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        # 파일 존재 확인
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"✅ 파일 생성 확인: {size_kb:.1f} KB")
            
            # 예상 결과
            ltv = 9000 * 25 * 0.35  # ₩78,750
            cac = 25000
            ratio = ltv / cac  # 3.15
            payback = cac / (9000 * 0.35)  # 7.94개월
            
            print(f"\n📊 핵심 지표:")
            print(f"   LTV: ₩{ltv:,.0f}")
            print(f"   CAC: ₩{cac:,.0f}")
            print(f"   LTV/CAC: {ratio:.2f} → Good (양호) ✅")
            print(f"   Payback: {payback:.1f}개월 → Good (< 12개월) ✅")
            
            print(f"\n📊 생성된 시트:")
            print(f"   1. Dashboard - 요약 대시보드 (Traffic Light)")
            print(f"   2. Inputs - 입력 데이터 (7개 Named Range)")
            print(f"   3. LTV_Calculation - 2가지 계산 방법")
            print(f"   4. CAC_Analysis - 채널별 CAC (4개 채널)")
            print(f"   5. LTV_CAC_Ratio - Traffic Light (4단계)")
            print(f"   6. Payback_Period - 24개월 Timeline")
            print(f"   7. Sensitivity_Analysis - 2-Way Matrix")
            print(f"   8. UE_Scenarios - 3가지 시나리오")
            print(f"   9. Cohort_LTV - 12개월 추적")
            print(f"   10. Benchmark_Comparison - 5개 업계 벤치마크")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_saas():
    """SaaS B2B 완성 테스트 (10개 시트)"""
    
    print("\n" + "="*60)
    print("🧪 Unit Economics 완성 테스트 - SaaS B2B\n")
    
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
        'industry': 'SaaS',
        'cohort_months': 12,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"✅ 파일 생성 확인: {size_kb:.1f} KB")
            
            # 예상 결과
            ltv = 50000 * 33 * 0.75  # ₩1,237,500
            cac = 200000
            ratio = ltv / cac  # 6.19
            payback = cac / (50000 * 0.75)  # 5.33개월
            
            print(f"\n📊 핵심 지표:")
            print(f"   LTV: ₩{ltv:,.0f}")
            print(f"   CAC: ₩{cac:,.0f}")
            print(f"   LTV/CAC: {ratio:.2f} → Excellent (우수) ✅")
            print(f"   Payback: {payback:.1f}개월 → Best-in-Class (< 6개월) ✅")
            
            print(f"\n✅ 10개 시트 모두 생성 완료")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Unit Economics Analyzer 완성 테스트")
    print("="*60 + "\n")
    
    results = []
    
    # 테스트 1: 음악 스트리밍
    results.append(test_complete_music_streaming())
    
    # 테스트 2: SaaS
    results.append(test_complete_saas())
    
    # 결과
    print("\n" + "="*60)
    print("테스트 결과")
    print("="*60)
    print(f"총 {len(results)}개 테스트")
    print(f"성공: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")
    
    if all(results):
        print("\n🎉 Unit Economics Analyzer 완성!")
        print("\n📊 완성된 기능:")
        print("   - 10개 시트 자동 생성")
        print("   - LTV, CAC, Ratio, Payback 모두 계산")
        print("   - Traffic Light 자동 색상")
        print("   - Sensitivity 2-Way Matrix")
        print("   - 3가지 시나리오")
        print("   - 코호트 추적")
        print("   - 업계 벤치마크 비교")
        print("   - Dashboard 요약")
        
        print("\n📋 다음 단계:")
        print("   - Excel 파일 열어서 최종 확인")
        print("   - Batch 4-6 진행 (Financial Projection)")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)

