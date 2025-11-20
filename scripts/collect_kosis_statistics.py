#!/usr/bin/env python3
"""
KOSIS (통계청) API를 사용한 산업별 마진율 자동 수집

통계청 기업경영분석 데이터를 자동으로 수집하여
산업별 평균 마진율 벤치마크 생성

사용:
    python scripts/collect_kosis_statistics.py
    
    # 특정 산업만
    python scripts/collect_kosis_statistics.py --industry "음식점업"

API Key 발급:
    https://kosis.kr/openapi/index/index.jsp
    무료, 승인 필요 (1-2일)
    .env 파일에 KOSIS_API_KEY 설정

v7.9.0 (Gap #2 실제 데이터)
"""

import requests
import yaml
import os
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# KOSIS API Key
KOSIS_API_KEY = os.getenv('KOSIS_API_KEY')

if not KOSIS_API_KEY or KOSIS_API_KEY == 'your-kosis-api-key-here':
    print("⚠️ KOSIS_API_KEY가 설정되지 않았습니다!")
    print("\n설정 방법:")
    print("1. https://kosis.kr/openapi/index/index.jsp 접속")
    print("2. OpenAPI 신청 (무료, 승인 1-2일)")
    print("3. .env 파일에 설정:")
    print("   - 일반: KOSIS_API_KEY=발급받은키")
    print("   - '=' 포함 시: KOSIS_API_KEY=\"abc=def=xyz\"")
    print("   ⚠️ Key에 '=' 문자 있으면 반드시 따옴표로 감싸기!")
    print("\n대안: 수동 수집 가이드 제공")
    KOSIS_API_KEY = None

# KOSIS API Base URL
KOSIS_BASE_URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do"


# ========================================
# 한국 주요 산업 (KSIC 분류)
# ========================================

TARGET_INDUSTRIES = {
    "음식점업": {
        "ksic_code": "56",
        "ksic_name": "음식점 및 주점업",
        "kosis_table_id": "DT_1K52C01",  # 확인 필요
        "priority": 1,
        "business_type": "offline"
    },
    "소매업": {
        "ksic_code": "47",
        "ksic_name": "소매업 (자동차 제외)",
        "kosis_table_id": "DT_1K52C01",
        "priority": 1,
        "business_type": "offline"
    },
    "미용업": {
        "ksic_code": "96",
        "ksic_name": "미용, 욕탕 및 유사 서비스업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 1,
        "business_type": "offline"
    },
    "보건업": {
        "ksic_code": "86",
        "ksic_name": "보건업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 1,
        "business_type": "offline"
    },
    "교육서비스업": {
        "ksic_code": "85",
        "ksic_name": "교육 서비스업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 1,
        "business_type": "offline"
    },
    "숙박업": {
        "ksic_code": "55",
        "ksic_name": "숙박업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 2,
        "business_type": "offline"
    },
    "스포츠_오락업": {
        "ksic_code": "91",
        "ksic_name": "스포츠 및 오락 관련 서비스업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 2,
        "business_type": "offline",
        "note": "헬스장, PC방 포함"
    },
    "제조업": {
        "ksic_code": "10-33",
        "ksic_name": "제조업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 2,
        "business_type": "mixed"
    },
    "건설업": {
        "ksic_code": "41-42",
        "ksic_name": "건설업",
        "kosis_table_id": "DT_1K52C01",
        "priority": 3,
        "business_type": "offline"
    }
}


def get_kosis_data(industry_info: Dict) -> Optional[Dict]:
    """
    KOSIS API로 산업별 재무비율 조회
    
    Args:
        industry_info: 산업 정보 dict
    
    Returns:
        재무비율 데이터 또는 None
    """
    
    if not KOSIS_API_KEY:
        return None
    
    # ⚠️ 실제 KOSIS API 파라미터는 확인 필요
    # 아래는 예시 구조
    
    params = {
        'method': 'getList',
        'apiKey': KOSIS_API_KEY,
        'itmId': 'ALL',  # 항목
        'objL1': industry_info.get('ksic_code'),  # KSIC 코드
        'format': 'json',
        'jsonVD': 'Y'
    }
    
    try:
        response = requests.get(KOSIS_BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # ⚠️ 실제 응답 구조 확인 필요
        return data
        
    except Exception as e:
        print(f"  ✗ KOSIS API 오류: {e}")
        return None


def create_manual_collection_guide(industry_name: str, industry_info: Dict) -> Dict:
    """
    수동 수집 가이드 생성 (API 없을 때)
    
    Args:
        industry_name: 산업명
        industry_info: 산업 정보
    
    Returns:
        수동 수집 가이드 dict
    """
    
    return {
        'benchmark_id': f"KR_KOSTAT_{industry_name.upper()}_001_MANUAL",
        'industry': industry_name,
        'sub_category': '전체',
        'business_model': '평균',
        'region': '한국',
        
        'margins': {
            'gross_margin': {'value': 'MANUAL_CHECK_NEEDED'},
            'operating_margin': {'value': 'MANUAL_CHECK_NEEDED'}
        },
        
        'data_source': {
            'type': 'to_be_verified',
            'source': '통계청 기업경영분석',
            
            'manual_collection_guide': f"""
[사용자 수동 확인 필요]

1. 통계청 KOSIS 접속:
   https://kosis.kr

2. 검색:
   "기업경영분석" → "산업별 재무비율"

3. 산업 선택:
   KSIC: {industry_info['ksic_code']} ({industry_info['ksic_name']})

4. 확인 항목:
   - 매출총이익률: ??%
   - 영업이익률: ??%
   - 표본 기업 수: ??개

5. 이 파일 업데이트:
   margins:
     gross_margin: {{value: 0.XXX}}
     operating_margin: {{value: 0.XXX}}
   sample_size: XXXXX
   reliability: "verified"
""",
            
            'collection_date': 'PENDING',
            'kosis_url': 'https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1K52C01'
        },
        
        'reliability': 'pending_manual_verification',
        'sample_size': None,
        'year': 2024,
        
        'notes': f"""
⚠️ 수동 수집 필요
- 통계청 KOSIS 직접 확인
- KSIC {industry_info['ksic_code']} ({industry_info['ksic_name']})
- 확인 후 실제 값으로 업데이트
"""
    }


def collect_kosis_industries(industries: Dict = None) -> List[Dict]:
    """
    KOSIS 산업별 데이터 수집 (API 또는 수동 가이드)
    
    Args:
        industries: 수집할 산업 dict
    
    Returns:
        수집된/수동가이드 benchmarks
    """
    
    if industries is None:
        industries = TARGET_INDUSTRIES
    
    benchmarks = []
    
    print("\n" + "="*60)
    print("KOSIS 통계청 산업별 마진율 수집")
    print("="*60)
    print(f"대상 산업: {len(industries)}개")
    print(f"API Key: {'설정됨' if KOSIS_API_KEY else '❌ 없음 (수동 가이드 생성)'}")
    
    for idx, (industry_name, industry_info) in enumerate(industries.items(), 1):
        print(f"\n[{idx}/{len(industries)}] {industry_name}")
        print(f"  KSIC: {industry_info['ksic_code']} - {industry_info['ksic_name']}")
        
        if KOSIS_API_KEY:
            # API로 시도
            print("  API 조회 시도...")
            data = get_kosis_data(industry_info)
            
            if data:
                # ⚠️ 실제 파싱 로직 구현 필요
                print("  ✓ API 조회 성공 (파싱 로직 필요)")
                # TODO: 실제 데이터 파싱
            else:
                print("  ✗ API 조회 실패 → 수동 가이드 생성")
                benchmark = create_manual_collection_guide(industry_name, industry_info)
                benchmarks.append(benchmark)
        else:
            # API 없으면 수동 가이드
            print("  수동 수집 가이드 생성...")
            benchmark = create_manual_collection_guide(industry_name, industry_info)
            benchmarks.append(benchmark)
            print("  ✓ 수동 가이드 생성 완료")
    
    return benchmarks


def main():
    """메인 함수"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="KOSIS 통계청 데이터 수집 (API 또는 수동 가이드)"
    )
    parser.add_argument(
        '--industry',
        help='특정 산업만 (예: "음식점업")'
    )
    parser.add_argument(
        '--output',
        help='출력 파일명'
    )
    
    args = parser.parse_args()
    
    # 수집 대상
    if args.industry:
        if args.industry in TARGET_INDUSTRIES:
            industries = {args.industry: TARGET_INDUSTRIES[args.industry]}
        else:
            print(f"❌ {args.industry}는 대상 산업에 없습니다")
            print(f"가능한 산업: {', '.join(TARGET_INDUSTRIES.keys())}")
            return 1
    else:
        industries = TARGET_INDUSTRIES
    
    # 데이터 수집 (또는 수동 가이드)
    benchmarks = collect_kosis_industries(industries)
    
    # YAML 저장
    output_file = args.output or (project_root / "data" / "raw" / "kosis_manual_guides.yaml")
    save_to_yaml(benchmarks, output_file)
    
    # 결과
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    
    if KOSIS_API_KEY:
        print("✓ API로 수집 시도")
    else:
        print("✓ 수동 수집 가이드 생성")
        print("\n다음 단계:")
        print("  1. kosis_manual_guides.yaml 확인")
        print("  2. 가이드대로 KOSIS 웹사이트 접속")
        print("  3. 실제 값 확인 후 업데이트")
    
    return 0


def save_to_yaml(benchmarks: List[Dict], output_file: str):
    """YAML 저장"""
    
    output = {
        'version': '2.0',
        'created': datetime.now().strftime('%Y-%m-%d'),
        'source': 'KOSIS 통계청' + (' API' if KOSIS_API_KEY else ' 수동 가이드'),
        'total_items': len(benchmarks),
        
        'collection_info': {
            'method': 'API 자동' if KOSIS_API_KEY else '수동 가이드',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'collected' if KOSIS_API_KEY else 'pending_manual'
        },
        
        'benchmarks': benchmarks
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ 저장: {output_file}")


if __name__ == "__main__":
    sys.exit(main())

