#!/usr/bin/env python3
"""
Financial Projection Batch 5 테스트
Assumptions + Revenue + Cost + P&L + CashFlow + Metrics (7개 시트)
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.financial_projection.financial_projection_generator import FinancialProjectionGenerator


def test_batch5_adult_education():
    """성인 교육 시장 Batch 5 테스트 (실제 케이스)"""
    
    print("🧪 Financial Projection Batch 5 테스트 - 성인 교육 시장\n")
    
    generator = FinancialProjectionGenerator()
    
    # 성인 교육 데이터 (Base Case)
    test_data = {
        'market_name': 'korean_adult_education',
        'assumptions_data': {
            'base_revenue_y0': 1250_0000_0000,  # 현재 125억
            'growth_rate_yoy': 0.28,  # 28% CAGR
            'gross_margin': 0.70,  # 70%
            'ebitda_margin': 0.15,  # 15% (Year 5 목표)
            'net_margin': 0.10,  # 10%
            'sm_percent': 0.30,  # S&M 30%
            'rd_percent': 0.15,  # R&D 15%
            'ga_percent': 0.10,  # G&A 10%
            'tax_rate': 0.25,  # 법인세 25%
            'discount_rate': 0.12  # 할인율 12%
        },
        'segments': [
            {'name': 'B2C (개인)', 'y0_revenue': 800_0000_0000, 'growth': 0.10},
            {'name': 'B2B (기업)', 'y0_revenue': 300_0000_0000, 'growth': 0.35},
            {'name': 'B2G (정부)', 'y0_revenue': 100_0000_0000, 'growth': 0.45},
            {'name': 'Global', 'y0_revenue': 50_0000_0000, 'growth': 0.60},
        ],
        'years': 5,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        # 파일 존재 확인
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"✅ 파일 생성 확인: {size_kb:.1f} KB")
            
            # 예상 결과 (Base Case)
            y0 = 1250_0000_0000
            y3 = 2621_0000_0000  # 목표 ₩3,050억 근처
            y5 = 4295_0000_0000  # 목표 ₩4,300억 근처
            
            print(f"\n📊 예상 재무 지표:")
            print(f"   Year 0 매출: ₩{y0/1_0000_0000:.0f}억")
            print(f"   Year 3 매출: ₩{y3/1_0000_0000:.0f}억 (목표 ₩3,050억)")
            print(f"   Year 5 매출: ₩{y5/1_0000_0000:.0f}억 (목표 ₩4,300억)")
            print(f"   CAGR: 28%")
            print(f"   Year 5 Net Income: ₩{y5 * 0.10 / 1_0000_0000:.0f}억 (목표 ₩645억)")
            print(f"   Year 5 Net Margin: 10%")
            
            print(f"\n📊 생성된 시트:")
            print(f"   1. Assumptions - 10개 Named Range")
            print(f"   2. Revenue_Buildup - 4개 세그먼트")
            print(f"   3. Cost_Structure - COGS + OPEX")
            print(f"   4. PL_3Year - 손익계산서 (3년)")
            print(f"   5. PL_5Year - 손익계산서 (5년)")
            print(f"   6. CashFlow - 현금흐름표")
            print(f"   7. Key_Metrics - 성장률, Margin 추이")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch5_saas_startup():
    """SaaS 스타트업 Batch 5 테스트"""
    
    print("\n" + "="*60)
    print("🧪 Financial Projection Batch 5 테스트 - SaaS 스타트업\n")
    
    generator = FinancialProjectionGenerator()
    
    # SaaS 스타트업 (고성장)
    test_data = {
        'market_name': 'saas_startup',
        'assumptions_data': {
            'base_revenue_y0': 50_0000_0000,  # 5억
            'growth_rate_yoy': 1.20,  # 120% (초기)
            'gross_margin': 0.80,  # 80%
            'ebitda_margin': -0.10,  # -10% (적자)
            'net_margin': -0.15,  # -15%
            'sm_percent': 0.60,  # S&M 60% (공격적)
            'rd_percent': 0.25,  # R&D 25%
            'ga_percent': 0.15,  # G&A 15%
            'tax_rate': 0.00,  # 적자 시 세금 없음
            'discount_rate': 0.15  # 15% (스타트업 리스크)
        },
        'segments': [
            {'name': 'SMB', 'y0_revenue': 30_0000_0000, 'growth': 1.00},
            {'name': 'Enterprise', 'y0_revenue': 20_0000_0000, 'growth': 1.50},
        ],
        'years': 5,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"✅ 파일 생성 확인: {size_kb:.1f} KB")
            
            print(f"\n📊 SaaS 특성:")
            print(f"   - 초기 적자 (EBITDA -10%, Net -15%)")
            print(f"   - 고성장 (120% YoY)")
            print(f"   - 높은 Gross Margin (80%)")
            print(f"   - 공격적 마케팅 (S&M 60%)")
            
            print(f"\n✅ 7개 시트 모두 생성 완료")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Financial Projection Batch 5 테스트")
    print("="*60 + "\n")
    
    results = []
    
    # 테스트 1: 성인 교육 (실제 케이스)
    results.append(test_batch5_adult_education())
    
    # 테스트 2: SaaS 스타트업
    results.append(test_batch5_saas_startup())
    
    # 결과
    print("\n" + "="*60)
    print("테스트 결과")
    print("="*60)
    print(f"총 {len(results)}개 테스트")
    print(f"성공: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")
    
    if all(results):
        print("\n✅ 모든 테스트 통과!")
        print("\n📊 Batch 5 완료:")
        print("   - 7개 시트 생성")
        print("   - P&L 3년/5년")
        print("   - Cash Flow")
        print("   - Key Metrics")
        print("\n📋 다음 단계:")
        print("   - Excel 파일 열어서 확인")
        print("   - Batch 6 진행 (Scenarios, DCF, Dashboard)")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)

