#!/usr/bin/env python3
"""모든 기업 2024년 일괄 재파싱"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient
import os

client = DARTClient(os.getenv('DART_API_KEY'))

# 재파싱 대상
companies = [
    '이마트',
    'LG생활건강', 
    'SK하이닉스',
    '유한양행',
    '아모레퍼시픽',
    'LG전자',
    '하이브',
    'CJ ENM',
]

print("="*70)
print("2024년 사업보고서 일괄 재파싱")
print("="*70)

results = []

for company in companies:
    print(f"\n{'='*70}")
    print(f"[{len(results)+1}/{len(companies)}] {company}")
    print(f"{'='*70}")
    
    # corp_code 찾기
    corp_code = client.get_corp_code(company)
    if not corp_code:
        print(f"  ❌ corp_code 없음")
        continue
    
    # 2024년 사업보고서 찾기
    reports = client.get_report_list(corp_code, 2024, 'A')
    
    rcept_no = None
    if reports:
        for r in reports:
            if '사업보고서' in r.get('report_nm', '') and '정정' not in r.get('report_nm', ''):
                rcept_no = r.get('rcept_no')
                print(f"  ✓ rcept_no: {rcept_no}")
                break
    
    if not rcept_no:
        print(f"  ❌ 2024년 사업보고서 없음")
        continue
    
    # 파싱 (최적화 파서 사용)
    try:
        result = subprocess.run(
            ['python3', 'scripts/parse_sga_optimized.py',
             '--company', company, '--year', '2024', '--rcept-no', rcept_no],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            import re
            match = re.search(r'✅ (\d+)개 SG&A', result.stdout)
            count = int(match.group(1)) if match else 0
            print(f"  ✅ {count}개 항목")
            results.append({'company': company, 'count': count, 'status': 'ok'})
        else:
            print(f"  ❌ 실패")
            results.append({'company': company, 'status': 'failed'})
    except Exception as e:
        print(f"  ❌ {e}")

print(f"\n{'='*70}")
print(f"성공: {len([r for r in results if r.get('status') == 'ok'])}/{len(results)}개")
print("="*70)

for r in results:
    if r.get('status') == 'ok':
        print(f"  ✅ {r['company']}: {r['count']}개")

