#!/usr/bin/env python3
"""
모든 기업 2024년 사업보고서 일괄 재파싱

개선된 파서 사용:
- 내용 기반 섹션 선택
- COGS 체크
- 항목 개수 검증
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from umis_rag.utils.dart_api import DARTClient
import os

client = DARTClient(os.getenv('DART_API_KEY'))

# 재파싱 대상 (C등급 기업들)
COMPANIES = [
    ('이마트', '00872984'),
    ('LG생활건강', '00892134'),  # corp_code 확인 필요
    ('SK하이닉스', '00164779'),
    ('유한양행', '00102520'),
    ('아모레퍼시픽', '00154186'),
    ('LG전자', '00401731'),
    ('하이브', '01204056'),
    ('CJ ENM', '00166346'),
]

def main():
    print("="*70)
    print("2024년 사업보고서 일괄 재파싱")
    print("="*70)
    
    results = []

    for company_name, corp_code in COMPANIES:
        print(f"\n{'='*70}")
        print(f"[{len(results)+1}/{len(COMPANIES)}] {company_name}")
        print(f"{'='*70}")
        
        # 1. 2024년 사업보고서 검색
        print(f"\n2024년 사업보고서 검색...")
    
    reports = client.get_report_list(corp_code, 2024, report_type='A')
    
    rcept_no = None
    if reports:
        for r in reports:
            report_nm = r.get('report_nm', '')
            if '사업보고서' in report_nm and '정정' not in report_nm:
                rcept_no = r.get('rcept_no')
                print(f"  ✓ {report_nm}")
                print(f"  ✓ rcept_no: {rcept_no}")
                break
    
    if not rcept_no:
        print(f"  ❌ 2024년 사업보고서 없음")
        results.append({
            'company': company_name,
            'status': 'no_report',
            'rcept_no': None
        })
        continue
    
    # 2. 파싱
    print(f"\n파싱 중...")
    
    try:
        result = subprocess.run(
            [
                'python3', 'scripts/parse_sga_optimized.py',
                '--company', company_name,
                '--year', '2024',
                '--rcept-no', rcept_no
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # 항목 수 추출
            import re
            match = re.search(r'✅ (\d+)개 SG&A', result.stdout)
            item_count = int(match.group(1)) if match else 0
            
            print(f"  ✅ 성공: {item_count}개 항목")
            
            results.append({
                'company': company_name,
                'status': 'success',
                'rcept_no': rcept_no,
                'item_count': item_count
            })
        else:
            print(f"  ❌ 파싱 실패")
            results.append({
                'company': company_name,
                'status': 'parse_failed',
                'rcept_no': rcept_no
            })
    
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        results.append({
            'company': company_name,
            'status': 'error',
            'rcept_no': rcept_no
        })

# 요약
print(f"\n\n{'='*70}")
print("재파싱 결과")
print(f"{'='*70}")

success = [r for r in results if r['status'] == 'success']
failed = [r for r in results if r['status'] != 'success']

print(f"\n✅ 성공: {len(success)}/{len(results)}개")
for r in success:
    print(f"  - {r['company']}: {r['item_count']}개 항목")

if failed:
    print(f"\n❌ 실패: {len(failed)}개")
    for r in failed:
        print(f"  - {r['company']}: {r['status']}")

    print(f"\n다음 단계:")
    print(f"  1. 성공한 기업 품질 검증")
    print(f"  2. A/B 등급 달성 확인")
    print(f"  3. Unit Economics 계산")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

