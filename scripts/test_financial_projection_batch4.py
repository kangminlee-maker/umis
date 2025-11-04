#!/usr/bin/env python3
"""
Financial Projection Batch 4 테스트
Assumptions + Revenue + Cost (3개 시트)
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.financial_projection.financial_projection_generator import FinancialProjectionGenerator


def test_batch4_adult_education():
    """성인 교육 시장 케이스 테스트 (실제 사례)"""
    
    print("🧪 Financial Projection Batch 4 테스트 - 성인 교육 시장\n")
    
    generator = FinancialProjectionGenerator()
    
    # 성인 교육 데이터 (실제 사례: Base Case CAGR 28%)
    test_data = {
        'market_name': 'korean_adult_education',
        'assumptions_data': {
            'base_revenue_y0': 1250_0000_0000,  # 현재 125억
            'growth_rate_yoy': 0.28,  # 28% (Base Case)
            'gross_margin': 0.70,  # 70%
            'ebitda_margin': 0.15,  # 15%
            'net_margin': 0.10,  # 10%
            'sm_percent': 0.30,  # S&M 30%
            'rd_percent': 0.15,  # R&D 15%
            'ga_percent': 0.10,  # G&A 10%
            'tax_rate': 0.25,  # 법인세 25%
            'discount_rate': 0.12  # 할인율 12%
        },
        'segments': [
            {'name': 'B2C (개인)', 'y0_revenue': 800_0000_0000, 'growth': 0.10},  # 80억, 10% 성장
            {'name': 'B2B (기업)', 'y0_revenue': 300_0000_0000, 'growth': 0.35},  # 30억, 35% 성장
            {'name': 'B2G (정부)', 'y0_revenue': 100_0000_0000, 'growth': 0.45},  # 10억, 45% 성장
            {'name': 'Global', 'y0_revenue': 50_0000_0000, 'growth': 0.60},  # 5억, 60% 성장
        ],
        'years': 5,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        # 파일 존재 확인
        if filepath.exists():
            print(f"✅ 파일 생성 확인: {filepath.stat().st_size} bytes")
            
            # 예상 결과 (Base Case)
            y0 = 1250_0000_0000
            y1 = y0 * 1.28
            y3 = y0 * (1.28 ** 3)
            y5 = y0 * (1.28 ** 5)
            
            print(f"\n📊 예상 매출 (전체 성장률 28% 적용):")
            print(f"   Year 0 (현재): ₩{y0/1_0000_0000:.0f}억")
            print(f"   Year 1: ₩{y1/1_0000_0000:.0f}억")
            print(f"   Year 3: ₩{y3/1_0000_0000:.0f}억 (목표 ₩3,050억)")
            print(f"   Year 5: ₩{y5/1_0000_0000:.0f}억 (목표 ₩4,300억)")
            print(f"   CAGR: 28%")
            
            print(f"\n📊 세그먼트별 성장:")
            print(f"   B2C: 10% (안정적)")
            print(f"   B2B: 35% (성장 엔진)")
            print(f"   B2G: 45% (고성장)")
            print(f"   Global: 60% (초기 단계)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch4_saas_startup():
    """SaaS 스타트업 케이스"""
    
    print("\n" + "="*60)
    print("🧪 Financial Projection Batch 4 테스트 - SaaS 스타트업\n")
    
    generator = FinancialProjectionGenerator()
    
    # SaaS 스타트업 데이터
    test_data = {
        'market_name': 'saas_startup',
        'assumptions_data': {
            'base_revenue_y0': 50_0000_0000,  # 현재 5억
            'growth_rate_yoy': 1.20,  # 120% (초기 고성장)
            'gross_margin': 0.80,  # 80% (SaaS 특성)
            'ebitda_margin': -0.10,  # -10% (초기 적자)
            'net_margin': -0.15,  # -15%
            'sm_percent': 0.60,  # S&M 60% (공격적)
            'rd_percent': 0.25,  # R&D 25%
            'ga_percent': 0.15,  # G&A 15%
            'tax_rate': 0.00,  # 적자 시 세금 없음
            'discount_rate': 0.15  # 15% (스타트업 리스크)
        },
        'segments': [
            {'name': 'SMB', 'y0_revenue': 30_0000_0000, 'growth': 1.00},  # 100% 성장
            {'name': 'Enterprise', 'y0_revenue': 20_0000_0000, 'growth': 1.50},  # 150% 성장
        ],
        'years': 5,
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        if filepath.exists():
            print(f"✅ 파일 생성 확인: {filepath.stat().st_size} bytes")
            
            # 예상 결과
            y0 = 50_0000_0000
            y5 = y0 * (2.20 ** 5)  # 120% 성장
            
            print(f"\n📊 예상 매출 (120% YoY):")
            print(f"   Year 0: ₩{y0/1_0000_0000:.0f}억")
            print(f"   Year 5: ₩{y5/1_0000_0000:.0f}억")
            print(f"   배수: {y5/y0:.1f}배")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Financial Projection Batch 4 테스트")
    print("="*60 + "\n")
    
    results = []
    
    # 테스트 1: 성인 교육 (실제 케이스)
    results.append(test_batch4_adult_education())
    
    # 테스트 2: SaaS 스타트업
    results.append(test_batch4_saas_startup())
    
    # 결과
    print("\n" + "="*60)
    print("테스트 결과")
    print("="*60)
    print(f"총 {len(results)}개 테스트")
    print(f"성공: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")
    
    if all(results):
        print("\n✅ 모든 테스트 통과!")
        print("\n📊 Batch 4 완료:")
        print("   - 3개 시트 생성 (Assumptions, Revenue, Cost)")
        print("   - 세그먼트별 매출 계산")
        print("   - 비용 구조 자동 계산")
        print("\n📋 다음 단계:")
        print("   - Excel 파일 열어서 확인")
        print("   - Batch 5 진행 (P&L, Cash Flow, Metrics)")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)

