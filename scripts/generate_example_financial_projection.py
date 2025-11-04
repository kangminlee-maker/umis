#!/usr/bin/env python3
"""
Financial Projection 예제 파일 생성
모든 입력값이 채워진 완성된 샘플
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.financial_projection import FinancialProjectionGenerator


def generate_example_korean_adult_education():
    """
    성인 교육 시장 Financial Projection 예제
    
    실제 프로젝트 데이터 기반:
    - 현재 매출: ₩1,250억
    - 목표 Year 3: ₩3,050억
    - 목표 Year 5: ₩4,300억
    - CAGR: 28%
    - Gross Margin: 70%
    - 세그먼트: B2C, B2B, B2G, Global
    """
    
    print("\n" + "="*70)
    print("📊 Financial Projection 예제 생성")
    print("="*70 + "\n")
    
    print("💼 시장: 한국 성인 교육 시장")
    print("📈 목표: 5년 매출 ₩4,300억 (CAGR 28%)\n")
    
    generator = FinancialProjectionGenerator()
    
    # 실제 데이터로 완전히 채워진 입력값
    data = {
        'market_name': 'korean_adult_education_example',
        
        # Assumptions (완전히 채워진 가정)
        'assumptions_data': {
            'base_revenue_y0': 1250_0000_0000,  # ₩125억 (2024년 현재)
            
            # 성장률 (실제 Base Case 목표)
            'growth_rate_yoy': 0.28,  # 28% YoY (Base Case)
            
            # Margin 목표
            'gross_margin': 0.70,  # 70% (성인 교육 특성)
            'ebitda_margin': 0.15,  # 15% (Year 5 목표)
            'net_margin': 0.10,  # 10% (Year 5 목표)
            
            # OPEX 비율
            'sm_percent': 0.30,  # S&M 30% (마케팅 집약적)
            'rd_percent': 0.15,  # R&D 15% (콘텐츠 개발)
            'ga_percent': 0.10,  # G&A 10% (일반관리)
            
            # 기타
            'tax_rate': 0.25,  # 법인세 25%
            'discount_rate': 0.12  # 할인율 12% (교육 산업 리스크)
        },
        
        # Segments (4개 세그먼트, 각각 다른 성장률)
        'segments': [
            {
                'name': 'B2C (개인 학습자)',
                'y0_revenue': 800_0000_0000,  # ₩80억 (64%)
                'growth': 0.10  # 10% (안정적 성장)
            },
            {
                'name': 'B2B (기업 교육)',
                'y0_revenue': 300_0000_0000,  # ₩30억 (24%)
                'growth': 0.35  # 35% (고성장 엔진)
            },
            {
                'name': 'B2G (정부 사업)',
                'y0_revenue': 100_0000_0000,  # ₩10억 (8%)
                'growth': 0.45  # 45% (정부 디지털 전환 수혜)
            },
            {
                'name': 'Global (해외)',
                'y0_revenue': 50_0000_0000,  # ₩5억 (4%)
                'growth': 0.60  # 60% (초기 진출 단계)
            }
        ],
        
        'years': 5,
        
        # examples/ 폴더에 저장
        'output_dir': project_root / 'examples' / 'excel'
    }
    
    print("🚀 Excel 생성 중...\n")
    
    try:
        filepath = generator.generate(**data)
        
        print("\n" + "="*70)
        print("✅ 예제 파일 생성 완료!")
        print("="*70 + "\n")
        
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            
            print(f"📁 파일 위치: {filepath}")
            print(f"📏 파일 크기: {size_kb:.1f} KB\n")
            
            print("📊 포함된 내용:")
            print("   ✅ 11개 시트 (모든 입력값 채워짐)")
            print("   ✅ 4개 세그먼트 (B2C, B2B, B2G, Global)")
            print("   ✅ 5년 재무 예측 (Year 0 ~ Year 5)")
            print("   ✅ P&L 손익계산서 (3년, 5년)")
            print("   ✅ Cash Flow 현금흐름표")
            print("   ✅ Bear/Base/Bull 시나리오")
            print("   ✅ 손익분기 분석")
            print("   ✅ DCF 기업 가치 평가\n")
            
            # 예상 결과 계산
            y0 = 1250_0000_0000
            y1 = y0 * 1.28
            y3 = y0 * (1.28 ** 3)
            y5 = y0 * (1.28 ** 5)
            cagr = 0.28
            net_y5 = y5 * 0.10
            
            print("📈 핵심 재무 지표 (Excel에서 확인 가능):")
            print(f"   Year 0 (현재): ₩{y0/1_0000_0000:.0f}억")
            print(f"   Year 1: ₩{y1/1_0000_0000:.0f}억")
            print(f"   Year 3: ₩{y3/1_0000_0000:.0f}억 (목표 ₩3,050억)")
            print(f"   Year 5: ₩{y5/1_0000_0000:.0f}억 (목표 ₩4,300억)")
            print(f"   CAGR: {cagr*100:.0f}%")
            print(f"   Year 5 Net Income: ₩{net_y5/1_0000_0000:.0f}억\n")
            
            print("💡 사용 방법:")
            print("   1. Excel에서 파일 열기")
            print("   2. Dashboard 시트에서 핵심 지표 확인")
            print("   3. Assumptions 시트에서 가정 조정 (노란색 셀)")
            print("   4. P&L_5Year 시트에서 손익 추이 확인")
            print("   5. FP_Scenarios에서 Bear/Base/Bull 비교")
            print("   6. DCF_Valuation에서 기업 가치 확인\n")
            
            print("✨ 모든 함수가 살아있어서 가정 변경 시 자동 재계산됩니다!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_example_korean_adult_education()
    
    if success:
        print("\n" + "="*70)
        print("🎉 예제 파일 생성 완료!")
        print("="*70)
        sys.exit(0)
    else:
        sys.exit(1)

