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
        'market_name': 'test_market',
        'assumptions': [
            {
                'id': 'ASM_001',
                'category': '인구',
                'description': '타겟 고객 수',
                'value': 10000,
                'unit': '명',
                'data_type': '직접데이터',
                'source': 'SRC_001',
                'confidence': 'High'
            }
        ],
        'tam': {'value': 1000000000000, 'definition': '전체 시장'},
        'segments': [],
        'proxy_data': {},
        'competitors': [],
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

