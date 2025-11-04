#!/usr/bin/env python3
"""
Market Sizing 예제 파일 생성
모든 입력값이 채워진 완성된 샘플
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.market_sizing_generator import MarketSizingWorkbookGenerator


def generate_example_piano_subscription():
    """
    피아노 구독 서비스 Market Sizing 예제
    
    실제 프로젝트 스타일 데이터:
    - TAM: ₩1,000억 (글로벌 악기 시장)
    - 지역 축소: 한국 15%
    - 제품 축소: 피아노만 25%
    - SAM: 4가지 방법으로 계산
    """
    
    print("\n" + "="*70)
    print("📊 Market Sizing 예제 생성")
    print("="*70 + "\n")
    
    print("🎹 시장: 피아노 구독 서비스")
    print("📈 목표: SAM 계산 (4-Method Convergence)\n")
    
    generator = MarketSizingWorkbookGenerator()
    
    # 완전히 채워진 입력 데이터
    data = {
        'market_name': 'piano_subscription_example',
        
        # Assumptions (12개)
        'assumptions': [
            # TAM
            {'id': 'TAM_VALUE', 'category': 'TAM', 'description': '글로벌 악기 시장',
             'value': 1000_0000_0000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_001', 'confidence': 'High'},
            
            # Top-Down Narrowing
            {'id': 'FILTER_KOREA', 'category': '지역', 'description': '한국 비중',
             'value': 0.15, 'unit': '%', 'data_type': '직접데이터',
             'source': 'SRC_002', 'confidence': 'High'},
            
            {'id': 'FILTER_PIANO', 'category': '제품', 'description': '피아노 비중',
             'value': 0.25, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_001', 'confidence': 'Medium'},
            
            # Bottom-Up Segment
            {'id': 'SEG1_CUSTOMERS', 'category': '세그먼트1', 'description': '타겟 고객 수',
             'value': 100000, 'unit': '명', 'data_type': '추정치',
             'source': 'EST_002', 'confidence': 'Medium'},
            
            {'id': 'SEG1_RATE', 'category': '세그먼트1', 'description': '구독 전환율',
             'value': 0.2, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_003', 'confidence': 'Medium'},
            
            {'id': 'SEG1_AOV', 'category': '세그먼트1', 'description': '월 구독료',
             'value': 50000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_003', 'confidence': 'High'},
            
            {'id': 'SEG1_FREQ', 'category': '세그먼트1', 'description': '연간 결제',
             'value': 12, 'unit': '회', 'data_type': '직접데이터',
             'source': 'SRC_004', 'confidence': 'High'},
            
            # Proxy Data
            {'id': 'PROXY_SIZE', 'category': 'Proxy', 'description': '유사 시장 규모',
             'value': 500_0000_0000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_005', 'confidence': 'Medium'},
            
            {'id': 'PROXY_CORR', 'category': 'Proxy', 'description': '상관계수',
             'value': 0.3, 'unit': '', 'data_type': '추정치',
             'source': 'EST_004', 'confidence': 'Low'},
            
            {'id': 'PROXY_APP', 'category': 'Proxy', 'description': '적용 비율',
             'value': 0.5, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_005', 'confidence': 'Medium'},
            
            # Competitor
            {'id': 'COMP1_REV', 'category': '경쟁사1', 'description': '경쟁사A 매출',
             'value': 100_0000_0000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_006', 'confidence': 'High'},
            
            {'id': 'COMP1_SHARE', 'category': '경쟁사1', 'description': '시장 점유율',
             'value': 0.4, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_006', 'confidence': 'Medium'},
        ],
        
        # TAM Definition
        'tam': {
            'value': 1000_0000_0000,
            'definition': '글로벌 악기 시장',
            'source': 'TAM_VALUE',
            'narrowing_steps': [
                {'dimension': '지역', 'ratio_source': 'FILTER_KOREA', 'description': '한국 비중 15%'},
                {'dimension': '제품', 'ratio_source': 'FILTER_PIANO', 'description': '피아노만 25%'},
            ]
        },
        
        # Bottom-Up Segments
        'segments': [
            {
                'name': '개인 구독',
                'target_customers': 'SEG1_CUSTOMERS',
                'purchase_rate': 'SEG1_RATE',
                'aov': 'SEG1_AOV',
                'frequency': 'SEG1_FREQ'
            }
        ],
        
        # Proxy Data
        'proxy_data': {
            'proxy_market': 'PROXY_SIZE',
            'correlation': 'PROXY_CORR',
            'application_rate': 'PROXY_APP'
        },
        
        # Competitors
        'competitors': [
            {
                'company': '경쟁사A',
                'revenue': 'COMP1_REV',
                'market_share': 'COMP1_SHARE'
            }
        ],
        
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
            print("   ✅ Summary 대시보드")
            print("   ✅ Assumptions (12개 가정)")
            print("   ✅ Estimation_Details (6개 추정치)")
            print("   ✅ Method 1: Top-Down (TAM → SAM)")
            print("   ✅ Method 2: Bottom-Up (세그먼트 합산)")
            print("   ✅ Method 3: Proxy (유사 시장)")
            print("   ✅ Method 4: Competitor Revenue (경쟁사 역산)")
            print("   ✅ Convergence Analysis (±30%)")
            print("   ✅ Scenarios (Best/Base/Worst)")
            print("   ✅ Validation Log\n")
            
            # 예상 SAM 계산
            tam = 1000_0000_0000
            sam_topdown = tam * 0.15 * 0.25  # ₩37.5억
            
            print("📈 핵심 지표 (Excel에서 확인 가능):")
            print(f"   TAM: ₩{tam/1_0000_0000:.0f}억")
            print(f"   SAM (Top-Down): ₩{sam_topdown/1_0000_0000:.1f}억")
            print(f"   Convergence: 4가지 방법 비교")
            print(f"   목표: ±30% 수렴\n")
            
            print("💡 사용 방법:")
            print("   1. Excel에서 파일 열기")
            print("   2. Summary 시트에서 핵심 지표 확인")
            print("   3. Assumptions 시트에서 가정 조정 (노란색 셀)")
            print("   4. Method_1_TopDown ~ Method_4 시트에서 각 계산 확인")
            print("   5. Convergence_Analysis에서 수렴 여부 확인 (±30%)")
            print("   6. Scenarios에서 Best/Base/Worst 비교\n")
            
            print("✨ 모든 함수가 살아있어서 가정 변경 시 자동 재계산됩니다!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_example_piano_subscription()
    
    if success:
        print("\n" + "="*70)
        print("🎉 예제 파일 생성 완료!")
        print("="*70)
        sys.exit(0)
    else:
        sys.exit(1)

