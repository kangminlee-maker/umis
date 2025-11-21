#!/usr/bin/env python3
"""
확장 배치 SG&A 파싱

목표: Unit Economics 레퍼런스 데이터 구축
- 10-20개 주요 기업
- 다양한 산업
- A등급 목표 10개 이상
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient
import os

client = DARTClient(os.getenv('DART_API_KEY'))

# 확장 파싱 대상 기업
companies = [
    # 이미 완료 (A등급 5개)
    # {'name': 'SK하이닉스', 'year': 2024, 'status': '완료 (A등급 2.1%)'},
    # {'name': 'LG생활건강', 'year': 2024, 'status': '완료 (A등급 3.0%)'},
    # {'name': 'GS리테일', 'year': 2024, 'status': '완료 (A등급 4.1%)'},
    # {'name': '아모레퍼시픽', 'year': 2024, 'status': '완료 (A등급 4.1%)'},
    # {'name': 'LG전자', 'year': 2024, 'status': '완료 (A등급 4.6%)'},
    # {'name': '유한양행', 'year': 2024, 'status': '완료 (B등급 7.9%)'},
    
    # 세션 서머리 기업 (미완료)
    {'name': '하이브', 'year': 2024},
    {'name': 'CJ ENM', 'year': 2024},
    
    # 주요 대기업 (2024년)
    {'name': '삼성전자', 'year': 2024},
    {'name': '현대차', 'year': 2024},
    {'name': 'SK이노베이션', 'year': 2024},
    {'name': 'LG화학', 'year': 2024},
    {'name': 'POSCO홀딩스', 'year': 2024},
    {'name': '네이버', 'year': 2024},
    {'name': '카카오', 'year': 2024},
    
    # 유통/리테일
    {'name': '롯데쇼핑', 'year': 2024},
    {'name': '신세계', 'year': 2024},
    
    # 화장품/생활
    {'name': 'LG생활건강', 'year': 2023},  # 전년도 비교용
    
    # 제약/바이오
    {'name': '셀트리온', 'year': 2024},
    {'name': '삼성바이오로직스', 'year': 2024},
    
    # 금융/보험
    {'name': '삼성화재', 'year': 2024},
    {'name': 'KB금융', 'year': 2024},
]

print("="*70)
print("확장 배치 SG&A 파싱")
print(f"대상: {len(companies)}개 기업")
print("="*70)

results = []

for i, company_info in enumerate(companies, 1):
    company = company_info['name']
    year = company_info['year']
    
    print(f"\n{'='*70}")
    print(f"[{i}/{len(companies)}] {company} ({year})")
    print(f"{'='*70}")
    
    # corp_code 찾기
    corp_code = client.get_corp_code(company)
    if not corp_code:
        print(f"  ❌ corp_code 없음")
        results.append({'company': company, 'year': year, 'status': 'no_corp_code'})
        continue
    
    # 사업보고서 찾기
    reports = client.get_report_list(corp_code, year, 'A')
    
    rcept_no = None
    if reports:
        for r in reports:
            if '사업보고서' in r.get('report_nm', '') and '정정' not in r.get('report_nm', ''):
                rcept_no = r.get('rcept_no')
                print(f"  ✓ rcept_no: {rcept_no}")
                break
    
    if not rcept_no:
        print(f"  ❌ {year}년 사업보고서 없음")
        results.append({'company': company, 'year': year, 'status': 'no_report'})
        continue
    
    # 파싱 (optimized 먼저 시도)
    try:
        result = subprocess.run(
            ['python3', 'scripts/parse_sga_optimized.py',
             '--company', company, '--year', str(year), '--rcept-no', rcept_no],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # 등급 추출
            import re
            grade_match = re.search(r'최종 등급: ([ABCD])', result.stdout)
            grade = grade_match.group(1) if grade_match else '?'
            
            # 오차 추출
            diff_match = re.search(r'차이:\s+([-\d.]+)%', result.stdout)
            diff = diff_match.group(1) if diff_match else '?'
            
            print(f"  ✅ 등급: {grade} (오차: {diff}%)")
            
            results.append({
                'company': company,
                'year': year,
                'grade': grade,
                'diff': diff,
                'status': 'success'
            })
            
            # D등급이면 Hybrid 재시도
            if grade == 'D':
                print(f"  → D등급, Hybrid 재시도...")
                
                hybrid_result = subprocess.run(
                    ['python3', 'scripts/parse_sga_hybrid.py',
                     '--company', company, '--year', str(year), '--rcept-no', rcept_no],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if hybrid_result.returncode == 0:
                    grade_match = re.search(r'최종 등급: ([ABCD])', hybrid_result.stdout)
                    new_grade = grade_match.group(1) if grade_match else '?'
                    
                    diff_match = re.search(r'차이:\s+([-\d.]+)%', hybrid_result.stdout)
                    new_diff = diff_match.group(1) if diff_match else '?'
                    
                    if new_grade in ['A', 'B', 'C']:
                        print(f"  ✅ Hybrid 개선: {new_grade} (오차: {new_diff}%)")
                        results[-1].update({
                            'grade': new_grade,
                            'diff': new_diff,
                            'method': 'hybrid'
                        })
        else:
            print(f"  ❌ 파싱 실패")
            results.append({'company': company, 'year': year, 'status': 'parse_failed'})
            
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        results.append({'company': company, 'year': year, 'status': f'error: {e}'})

# 최종 요약
print(f"\n\n{'='*70}")
print("최종 결과 요약")
print(f"{'='*70}")

print(f"\n{'회사':<15} {'연도':<6} {'등급':<6} {'오차':<10} {'상태'}")
print("-"*70)

for r in results:
    company = r['company']
    year = r.get('year', '')
    grade = r.get('grade', '-')
    diff = r.get('diff', '-')
    status = r.get('status', '')
    
    if grade in ['A', 'B']:
        mark = '✅'
    elif grade == 'C':
        mark = '⚠️'
    elif grade == 'D':
        mark = '❌'
    else:
        mark = '  '
    
    print(f"{mark} {company:<15} {year:<6} {grade:<6} {diff:>8}%  {status}")

# 등급별 집계
grades = {}
for r in results:
    g = r.get('grade', 'N/A')
    grades[g] = grades.get(g, 0) + 1

print(f"\n등급별 분포:")
for g in ['A', 'B', 'C', 'D']:
    count = grades.get(g, 0)
    if count > 0:
        print(f"  {g}등급: {count}개")

print(f"\n총 {len(results)}개 기업 처리 완료")
print(f"A+B등급: {grades.get('A', 0) + grades.get('B', 0)}개")




