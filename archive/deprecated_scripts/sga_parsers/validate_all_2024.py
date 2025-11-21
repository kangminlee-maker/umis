#!/usr/bin/env python3
"""
2024년 데이터 전체 품질 검증

개선된 파서로 재파싱 후 검증:
- 재고자산 제외
- 경상연구개발비 제외
- exclude_keywords 부분 문자열 체크
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient
import os
import yaml

client = DARTClient(os.getenv('DART_API_KEY'))

companies_2024 = [
    ('GS리테일', '20250312000991'),
    ('이마트', '20250318000688'),
    ('LG생활건강', '20250317000790'),
    ('SK하이닉스', '20250319000665'),
    ('유한양행', '20250312001137'),
    ('아모레퍼시픽', '20250317000429'),
    ('LG전자', '20250317001029'),
    ('CJ ENM', '20250319000884'),
    ('하이브', '20250321001187'),
]

print("="*70)
print("2024년 데이터 전체 재파싱 및 품질 검증")
print("="*70)

results = []

for company, rcept_no in companies_2024:
    print(f"\n{'='*70}")
    print(f"[{len(results)+1}/{len(companies_2024)}] {company}")
    print(f"{'='*70}")
    
    # 1. 재파싱 (최적화 파서 사용)
    try:
        result = subprocess.run(
            ['python3', 'scripts/parse_sga_optimized.py',
             '--company', company, '--year', '2024', '--rcept-no', rcept_no],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ❌ 파싱 실패")
            continue
        
        # 항목 수
        import re
        match = re.search(r'✅ (\d+)개 SG&A', result.stdout)
        item_count = int(match.group(1)) if match else 0
        
        print(f"  ✓ 파싱: {item_count}개 항목")
        
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        continue
    
    # 2. 품질 검증
    sga_file = Path(f'data/raw/{company}_sga_complete.yaml')
    
    if not sga_file.exists():
        continue
    
    with open(sga_file) as f:
        data = yaml.safe_load(f)
    
    sga = data.get('sga_details_million', {})
    unit = data.get('unit', '백만원')
    
    # 합계 계산
    if unit == '백만원':
        parsed_total = sum(sga.values()) / 100
    elif unit == '천원':
        parsed_total = sum(sga.values()) / 100_000
    else:
        parsed_total = sum(sga.values()) / 100_000_000
    
    # DART 총액
    corp_code = client.get_corp_code(company)
    
    if not corp_code:
        continue
    
    financials = client.get_financials(corp_code, 2024, 'OFS')
    
    dart_total = 0
    if financials:
        for item in financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amt_str = item.get('thstrm_amount', '0')
                try:
                    dart_total = float(amt_str.replace(',', '')) / 100_000_000
                    break
                except:
                    pass
    
    if dart_total == 0:
        print(f"  ⚠️ DART 총액 없음")
        continue
    
    # 오차 계산
    diff = parsed_total - dart_total
    diff_ratio = diff / dart_total
    
    # 등급
    if abs(diff_ratio) <= 0.05:
        grade = 'A'
        status = '✅✅✅'
    elif abs(diff_ratio) <= 0.10:
        grade = 'B'
        status = '✅'
    else:
        grade = 'C'
        status = '❌'
    
    print(f"\n  {status} 등급: {grade}")
    print(f"  DART: {dart_total:>10,.0f}억원")
    print(f"  파싱: {parsed_total:>10,.0f}억원")
    print(f"  오차: {diff_ratio:>7.1%}")
    
    results.append({
        'company': company,
        'grade': grade,
        'dart_total': dart_total,
        'parsed_total': parsed_total,
        'diff_ratio': diff_ratio,
        'item_count': item_count
    })

# 최종 요약
print(f"\n\n{'='*70}")
print("최종 품질 요약")
print(f"{'='*70}")

print(f"\n{'등급':<6} {'회사':<15} {'DART(억)':<12} {'파싱(억)':<12} {'오차':<10} {'항목'}")
print("-"*70)

for r in sorted(results, key=lambda x: x['diff_ratio']):
    status = '✅' if r['grade'] in ['A', 'B'] else '❌'
    print(f"{status} {r['grade']:<6} {r['company']:<15} {r['dart_total']:>10,.0f}  {r['parsed_total']:>10,.0f}  {r['diff_ratio']:>8.1%}  {r['item_count']:2d}개")

# 등급별 집계
grades = {}
for r in results:
    g = r['grade']
    grades[g] = grades.get(g, 0) + 1

print(f"\n등급별 분포:")
for g in ['A', 'B', 'C']:
    count = grades.get(g, 0)
    if count > 0:
        print(f"  {g}등급: {count}개")

print(f"\n총 {len(results)}개 기업 검증 완료")

