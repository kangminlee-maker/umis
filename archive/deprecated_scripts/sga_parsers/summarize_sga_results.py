#!/usr/bin/env python3
"""완성된 SG&A 데이터 요약"""

import yaml
import glob
from pathlib import Path

print("="*70)
print("완성된 SG&A 벤치마크 요약")
print("="*70)

files = glob.glob('data/raw/*_sga_complete.yaml')

# (GS리테일 이제 정상 데이터!)

results = []

for filepath in sorted(files):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        company = data.get('company', Path(filepath).stem.replace('_sga_complete', ''))
        count = data.get('sga_count', len(data.get('sga_details_million', {})))
        unit = data.get('unit', '백만원')
        year = data.get('year', 2023)
        
        # 총액 계산
        details = data.get('sga_details_million', {})
        if details:
            # 단위 변환 (원 → 백만원)
            if unit == '원':
                total = sum(details.values()) / 1_000_000
            else:
                total = sum(details.values())
            
            total_billion = total / 100 if unit == '백만원' else total / 1_000_000_000
        else:
            total_billion = 0
        
        results.append({
            'company': company,
            'year': year,
            'count': count,
            'total_billion': total_billion,
            'filepath': filepath
        })
        
    except Exception as e:
        print(f"❌ {filepath}: {e}")

# 정렬 (항목 수 순)
results.sort(key=lambda x: x['count'], reverse=True)

print(f"\n완성된 기업: {len(results)}개\n")
print(f"{'순위':<4} {'기업명':<20} {'연도':<6} {'항목 수':<8} {'총액(억원)':<15} {'파일'}")
print("-"*90)

for i, r in enumerate(results, 1):
    print(f"{i:<4} {r['company']:<20} {r['year']:<6} {r['count']:<8} {r['total_billion']:>12,.0f}   {Path(r['filepath']).name}")

# 통계
total_items = sum(r['count'] for r in results)
avg_items = total_items / len(results) if results else 0

print(f"\n{'='*90}")
print(f"전체 통계:")
print(f"  - 완성 기업: {len(results)}개")
print(f"  - 총 항목: {total_items}개")
print(f"  - 평균 항목: {avg_items:.1f}개/기업")
print(f"  - 최다 항목: {results[0]['company']} ({results[0]['count']}개)")
print(f"  - 최소 항목: {results[-1]['company']} ({results[-1]['count']}개)")
print("="*90)

# 산업별 분류
industries = {
    '유통': ['BGF리테일', '이마트'],
    '전자/반도체': ['삼성전자', 'SK하이닉스'],
    '제약': ['유한양행'],
    '화장품': ['아모레퍼시픽', 'LG생활건강'],
    '엔터/미디어': ['CJ ENM'],
}

print(f"\n산업별 분류:")
for industry, companies in industries.items():
    matched = [r for r in results if r['company'] in companies]
    if matched:
        print(f"\n  {industry} ({len(matched)}개):")
        for r in matched:
            print(f"    - {r['company']}: {r['count']}개 항목")

