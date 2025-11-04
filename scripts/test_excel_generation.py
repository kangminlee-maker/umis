#!/usr/bin/env python3
"""
Excel 생성 테스트
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.market_sizing_generator import MarketSizingWorkbookGenerator


def test_basic_generation():
    """기본 생성 테스트"""
    
    print("🧪 Excel 생성 테스트\n")
    
    generator = MarketSizingWorkbookGenerator()
    
    # 테스트 데이터
    test_data = {
        'market_name': 'piano_subscription',
        'assumptions': [
            # TAM
            {'id': 'TAM_VALUE', 'category': 'TAM', 'description': '글로벌 악기 시장', 
             'value': 1000000000000, 'unit': '원', 'data_type': '직접데이터', 
             'source': 'SRC_001', 'confidence': 'High'},
            
            # Narrowing
            {'id': 'FILTER_KOREA', 'category': '지역', 'description': '한국 비중',
             'value': 0.15, 'unit': '%', 'data_type': '직접데이터',
             'source': 'SRC_002', 'confidence': 'High'},
            
            {'id': 'FILTER_PIANO', 'category': '제품', 'description': '피아노만',
             'value': 0.25, 'unit': '%', 'data_type': '직접데이터',
             'source': 'SRC_003', 'confidence': 'Medium'},
            
            # Bottom-Up
            {'id': 'SEG1_CUSTOMERS', 'category': '세그먼트1', 'description': '타겟 고객',
             'value': 100000, 'unit': '명', 'data_type': '추정치',
             'source': 'EST_001', 'confidence': 'Medium'},
            
            {'id': 'SEG1_RATE', 'category': '세그먼트1', 'description': '구매율',
             'value': 0.2, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_002', 'confidence': 'Medium'},
            
            {'id': 'SEG1_AOV', 'category': '세그먼트1', 'description': '객단가',
             'value': 50000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_004', 'confidence': 'High'},
            
            {'id': 'SEG1_FREQ', 'category': '세그먼트1', 'description': '연간 구매',
             'value': 2, 'unit': '회', 'data_type': '추정치',
             'source': 'EST_003', 'confidence': 'Medium'},
            
            # Proxy
            {'id': 'PROXY_SIZE', 'category': 'Proxy', 'description': '유사 시장 규모',
             'value': 500000000000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_005', 'confidence': 'Medium'},
            
            {'id': 'PROXY_CORR', 'category': 'Proxy', 'description': '상관계수',
             'value': 0.3, 'unit': '', 'data_type': '추정치',
             'source': 'EST_004', 'confidence': 'Low'},
            
            {'id': 'PROXY_APP', 'category': 'Proxy', 'description': '적용 비율',
             'value': 0.5, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_005', 'confidence': 'Medium'},
            
            # Competitor
            {'id': 'COMP1_REV', 'category': '경쟁사1', 'description': '경쟁사A 매출',
             'value': 100000000000, 'unit': '원', 'data_type': '직접데이터',
             'source': 'SRC_006', 'confidence': 'High'},
            
            {'id': 'COMP1_SHARE', 'category': '경쟁사1', 'description': '시장 점유율',
             'value': 0.4, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_006', 'confidence': 'Medium'},
        ],
        'tam': {
            'value': 1000000000000,
            'definition': '글로벌 악기 시장',
            'source': 'TAM_VALUE',
            'narrowing_steps': [
                {'dimension': '지역', 'ratio_source': 'FILTER_KOREA', 'description': '한국 비중 15%'},
                {'dimension': '제품', 'ratio_source': 'FILTER_PIANO', 'description': '피아노만 25%'},
            ]
        },
        'segments': [
            {
                'name': '개인 구독',
                'target_customers': 'SEG1_CUSTOMERS',
                'purchase_rate': 'SEG1_RATE',
                'aov': 'SEG1_AOV',
                'frequency': 'SEG1_FREQ'
            }
        ],
        'proxy_data': {
            'proxy_market': 'PROXY_SIZE',
            'correlation': 'PROXY_CORR',
            'application_rate': 'PROXY_APP'
        },
        'competitors': [
            {
                'company': '경쟁사A',
                'revenue': 'COMP1_REV',
                'market_share': 'COMP1_SHARE'
            }
        ],
        'output_dir': Path('test_output')
    }
    
    try:
        filepath = generator.generate(**test_data)
        print(f"\n✅ 테스트 성공: {filepath}")
        
        # 파일 존재 확인
        if filepath.exists():
            print(f"✅ 파일 생성 확인: {filepath.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_generation()
    sys.exit(0 if success else 1)

