#!/usr/bin/env python3
"""GS리테일 2024년 사업보고서 검색"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from umis_rag.utils.dart_api import DARTClient
import os

client = DARTClient(os.getenv('DART_API_KEY'))

print("="*70)
print("GS리테일 2024년 사업보고서 검색")
print("="*70)

corp_code = '00140177'

# 2024년 사업보고서 = 2025년 3월 제출
reports = client.get_report_list(corp_code, 2024, report_type='A')

if reports:
    print(f"\n✓ {len(reports)}개 공시 발견\n")
    
    for r in reports:
        report_nm = r.get('report_nm', '')
        if '사업보고서' in report_nm:
            print(f"  📄 {report_nm}")
            print(f"     rcept_no: {r.get('rcept_no')}")
            print(f"     제출일: {r.get('rcept_dt')}")
            print()
else:
    print("\n❌ 공시 없음")




