#!/usr/bin/env python3
"""
Unit Economics 예제 파일 생성
모든 입력값이 채워진 완성된 샘플
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.unit_economics import UnitEconomicsGenerator


def generate_example_music_streaming():
    """
    음악 스트리밍 Unit Economics 예제
    
    실제 프로젝트 데이터 기반:
    - ARPU: ₩9,000/월
    - CAC: ₩25,000
    - LTV: ₩78,750
    - LTV/CAC: 3.15 (Good)
    - Payback: 7.9개월
    """
    
    print("\n" + "="*70)
    print("📊 Unit Economics 예제 생성")
    print("="*70 + "\n")
    
    print("🎵 시장: 음악 스트리밍 구독 서비스")
    print("📈 목표: LTV/CAC > 3.0, Payback < 12개월\n")
    
    generator = UnitEconomicsGenerator()
    
    # 실제 데이터로 완전히 채워진 입력값
    data = {
        'market_name': 'music_streaming_example',
        
        # Inputs (실제 음악 스트리밍 데이터)
        'inputs_data': {
            'arpu': 9000,  # ₩9,000/월 (Spotify, Melon 평균)
            'cac': 25000,  # ₩25,000 (마케팅 비용)
            'gross_margin': 0.35,  # 35% (라이선스료 제외 후)
            'monthly_churn': 0.04,  # 4%/월 (업계 평균)
            'customer_lifetime': 25,  # 25개월 (1/0.04)
            'sm_spend_monthly': 5000000,  # ₩500만/월 (S&M 지출)
            'new_customers_monthly': 200  # 200명/월 (신규 획득)
        },
        
        # 채널별 CAC 데이터
        'channels_data': [
            {
                'channel': '검색 광고 (네이버, Google)',
                'spend': 2000000,  # ₩200만
                'customers': 80  # 80명
            },
            {
                'channel': 'SNS 광고 (Instagram, Facebook)',
                'spend': 1500000,  # ₩150만
                'customers': 60  # 60명
            },
            {
                'channel': '제휴 마케팅 (블로그, 유튜버)',
                'spend': 1000000,  # ₩100만
                'customers': 40  # 40명
            },
            {
                'channel': '오프라인 이벤트',
                'spend': 500000,  # ₩50만
                'customers': 20  # 20명
            }
        ],
        
        'industry': 'Streaming',  # 업계 벤치마크
        'cohort_months': 12,  # 12개월 코호트 추적
        
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
            print("   ✅ 10개 시트 (모든 입력값 채워짐)")
            print("   ✅ 4개 마케팅 채널 CAC 분석")
            print("   ✅ LTV 2가지 계산 방법")
            print("   ✅ LTV/CAC Ratio (Traffic Light)")
            print("   ✅ 24개월 Payback Timeline")
            print("   ✅ 2-Way Sensitivity Matrix")
            print("   ✅ Conservative/Base/Optimistic 시나리오")
            print("   ✅ 12개월 Cohort 추적")
            print("   ✅ 업계 벤치마크 비교\n")
            
            # 예상 결과 계산
            arpu = 9000
            lifetime = 25
            margin = 0.35
            ltv = arpu * lifetime * margin
            cac = 25000
            ratio = ltv / cac
            payback = cac / (arpu * margin)
            
            print("📈 핵심 Unit Economics 지표 (Excel에서 확인 가능):")
            print(f"   ARPU: ₩{arpu:,}/월")
            print(f"   CAC: ₩{cac:,}")
            print(f"   LTV: ₩{ltv:,.0f}")
            print(f"   LTV/CAC: {ratio:.2f} → Good (양호) ✅")
            print(f"   Payback: {payback:.1f}개월 → Good (< 12개월) ✅")
            print(f"   평가: 건강한 비즈니스 모델\n")
            
            print("💡 사용 방법:")
            print("   1. Excel에서 파일 열기")
            print("   2. Dashboard 시트에서 LTV/CAC 비율 확인 (Traffic Light)")
            print("   3. Inputs 시트에서 가정 조정 (노란색 셀)")
            print("   4. LTV_CAC_Ratio 시트에서 색상 변화 확인")
            print("   5. Sensitivity_Analysis에서 가장 중요한 변수 확인")
            print("   6. UE_Scenarios에서 최악/최선 시나리오 확인\n")
            
            print("✨ 모든 함수가 살아있어서 가정 변경 시 자동 재계산됩니다!")
            print("🎨 Traffic Light가 자동으로 색상 변경됩니다!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_example_music_streaming()
    
    if success:
        print("\n" + "="*70)
        print("🎉 예제 파일 생성 완료!")
        print("="*70)
        sys.exit(0)
    else:
        sys.exit(1)

