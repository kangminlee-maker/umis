#!/usr/bin/env python3
"""
SG&A 파서 v2.0 - 품질 검증 내장

개선사항:
1. 계정 타입 자동 분류 (SG&A vs COGS vs 금융 등)
2. DART 총액과 실시간 비교
3. 미상 비용 자동 추가
4. 품질 등급 자동 평가 (A/B/C)
5. 신뢰도 메타데이터 포함

사용:
    python scripts/parse_sga_v2_validated.py --company "삼성전자" --year 2023
"""

import requests
import os
import re
import zipfile
import io
import time
import yaml
import argparse
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
DART_BASE_URL = "https://opendart.fss.or.kr/api"


# 계정 타입 분류 키워드
ACCOUNT_CLASSIFIERS = {
    'exclude_cogs': [
        '매입', '원재료', '재료비', '저장품', '재공품', '제품의 변동',
        '외주가공비', '제조', '생산',
    ],
    'exclude_financial': [
        '금융수익', '금융비용', '금융손익', '순금융',
        '이자수익', '이자비용', '배당금',
        '외환차익', '외환차손', '외환차이',
        '파생상품',
    ],
    'exclude_investment': [
        '투자주식', '관계기업', '공동기업', '종속기업',
        '평가손실', '평가이익', '손상차손', '손상차손환입',
        '처분이익', '처분손실',
    ],
    'exclude_summary': [
        '합계', '총계', '소계', '총액', 'Total',
        '순이익', '당기순이익', '영업이익', '포괄손익',
        '세전', '법인세', '차감',
        '성격별', '기능별',
    ],
    'exclude_others': [
        '주식수', '주당', 'EPS', '가중평균',
        '기초', '기말', '증감',
    ]
}


def should_exclude_item(item_name: str) -> Tuple[bool, str]:
    """항목 제외 여부 판단"""
    
    for category, keywords in ACCOUNT_CLASSIFIERS.items():
        for keyword in keywords:
            if keyword in item_name:
                return True, category.replace('exclude_', '')
    
    return False, 'sga'


def get_corp_code(company_name: str) -> Optional[str]:
    """기업 코드 조회 (기존 로직)"""
    
    known_codes = {
        'BGF리테일': '01263022', '하이브': '01204056', '이마트': '00872984',
        'GS리테일': '00140177', '삼성전자': '00126380', 'LG전자': '00401731',
    }
    
    if company_name in known_codes:
        return known_codes[company_name]
    
    # corpCode.xml 검색
    url = f"{DART_BASE_URL}/corpCode.xml"
    response = requests.get(url, params={'crtfc_key': DART_API_KEY}, timeout=30)
    
    import xml.etree.ElementTree as ET
    
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    xml_data = zip_file.read('CORPCODE.xml')
    root = ET.fromstring(xml_data)
    
    # 정확한 매칭 우선
    for corp in root.findall('list'):
        name = corp.findtext('corp_name', '')
        if name == company_name:
            return corp.findtext('corp_code', '')
    
    # 상장사 우선
    candidates = []
    for corp in root.findall('list'):
        name = corp.findtext('corp_name', '')
        if company_name in name:
            code = corp.findtext('corp_code', '')
            stock_code = corp.findtext('stock_code', '')
            has_stock = stock_code and stock_code.strip()
            candidates.append((name, code, has_stock))
    
    if candidates:
        listed = [c for c in candidates if c[2]]
        if listed:
            return listed[0][1]
        return candidates[0][1]
    
    return None


def get_dart_sga_total(corp_code: str, year: int) -> Optional[float]:
    """DART 재무제표에서 SG&A 총액 조회"""
    
    url = f"{DART_BASE_URL}/fnlttSinglAcntAll.json"
    params = {
        'crtfc_key': DART_API_KEY,
        'corp_code': corp_code,
        'bsns_year': str(year),
        'reprt_code': '11011',
        'fs_div': 'OFS'
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get('status') != '000':
        return None
    
    # SG&A 총액 추출
    for item in data.get('list', []):
        account = item.get('account_nm', '')
        if '판매비' in account or '관리비' in account:
            amount_str = item.get('thstrm_amount', '0')
            try:
                # 원 → 억원
                return float(amount_str.replace(',', '')) / 100_000_000
            except:
                pass
    
    return None


def download_and_parse_sga(rcept_no: str) -> Tuple[Dict[str, float], str]:
    """원문 다운로드 및 파싱 (기존 로직)"""
    
    # document.xml 다운로드
    url = f"{DART_BASE_URL}/document.xml"
    params = {
        'crtfc_key': DART_API_KEY,
        'rcept_no': rcept_no,
        'reprt_code': '11011'
    }
    
    response = requests.get(url, params=params, timeout=60)
    
    # ZIP 압축 해제
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    xml_filename = zip_file.namelist()[0]
    xml_bytes = zip_file.read(xml_filename)
    xml = xml_bytes.decode('utf-8', errors='ignore')
    
    # 섹션 찾기 (직접 패턴)
    patterns = [
        r'(\d+)\.\s*판매비.*?관리비',
        r'(\d+)\.\s*일반영업비용',
    ]
    
    section = None
    for pattern in patterns:
        matches = list(re.finditer(pattern, xml, re.IGNORECASE))
        
        if matches:
            # 개별재무제표 우선
            for m in matches:
                if '연결' not in m.group():
                    preview = xml[m.start():m.start()+2000]
                    if '당기' in preview:
                        section = xml[m.start():m.start()+25000]
                        break
            
            if section:
                break
    
    if not section:
        return {}, '백만원'
    
    # 단위
    unit_patterns = [
        r'단위\s*[:：]\s*(백만원|천원|원|억원)',
        r'\(단위\s*[:：]\s*(백만원|천원|원)',
    ]
    
    unit = '백만원'
    for p in unit_patterns:
        m = re.search(p, section)
        if m:
            unit = m.group(1)
            break
    
    # 테이블 행
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section, re.DOTALL)
    
    # 항목 추출
    items = {}
    
    def extract_text(cell):
        p_match = re.search(r'<P[^>]*>(.*?)</P>', cell, re.DOTALL)
        if p_match:
            text = re.sub(r'<[^>]+>', '', p_match.group(1))
            return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
        text = re.sub(r'<[^>]+>', '', cell)
        return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
    
    for row in rows:
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        if len(cells) >= 2:
            item_name = extract_text(cells[0])
            amount_str = extract_text(cells[-1])
            
            # 정리
            item_name = re.sub(r',\s*판관비$', '', item_name)
            amount_clean = re.sub(r'[^\d-]', '', amount_str)
            
            if item_name and amount_clean and len(item_name) > 1:
                try:
                    amount = float(amount_clean)
                    
                    min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                    
                    if abs(amount) > min_threshold:
                        # 제외 여부 체크 (품질 검증!)
                        should_exclude, reason = should_exclude_item(item_name)
                        
                        if not should_exclude:
                            items[item_name] = amount
                except:
                    pass
    
    return items, unit


def main():
    parser = argparse.ArgumentParser(description='SG&A 파서 v2.0 (품질 검증 내장)')
    parser.add_argument('--company', required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--rcept-no', help='rcept_no 직접 입력')
    args = parser.parse_args()
    
    print("="*70)
    print(f"🔍 SG&A 파서 v2.0 (검증 내장): {args.company} ({args.year})")
    print("="*70)
    
    # 1. 기업 코드
    corp_code = get_corp_code(args.company)
    if not corp_code:
        print("❌ 기업 코드 없음")
        return 1
    
    print(f"\n✓ corp_code: {corp_code}")
    
    # 2. DART SG&A 총액 (검증용!)
    print(f"\n[품질 검증] DART SG&A 총액 조회...")
    dart_sga_total = get_dart_sga_total(corp_code, args.year)
    
    if dart_sga_total:
        print(f"  ✓ DART SG&A: {dart_sga_total:,.1f}억원 (검증 기준)")
    else:
        print(f"  ⚠️ DART 총액 없음 (검증 불가)")
    
    # 3. rcept_no 찾기 (기존 로직 생략 - 직접 입력만)
    if not args.rcept_no:
        print("❌ --rcept-no 필수")
        return 1
    
    # 4. 원문 다운로드 및 파싱
    print(f"\n원문 파싱...")
    items, unit = download_and_parse_sga(args.rcept_no)
    
    if not items:
        print("❌ 파싱 실패")
        return 1
    
    print(f"  ✓ {len(items)}개 항목 (필터링 적용)")
    print(f"  ✓ 단위: {unit}")
    
    # 5. 품질 검증
    print(f"\n[품질 검증] 합계 비교...")
    
    if unit == '백만원':
        parsed_total = sum(items.values()) / 100
    elif unit == '천원':
        parsed_total = sum(items.values()) / 100_000
    else:
        parsed_total = sum(items.values()) / 100_000_000
    
    if dart_sga_total:
        diff = parsed_total - dart_sga_total
        diff_ratio = diff / dart_sga_total
        
        print(f"  DART 총액:   {dart_sga_total:>12,.1f}억원")
        print(f"  파싱 합계:   {parsed_total:>12,.1f}억원")
        print(f"  차이:       {diff:>12,.1f}억원 ({diff_ratio:>6.1%})")
        
        # 품질 등급 평가
        if abs(diff_ratio) <= 0.05:
            quality_grade = 'A'
            print(f"  ✅ 등급 A (오차 ±5% 이내)")
        elif abs(diff_ratio) <= 0.10:
            quality_grade = 'B'
            print(f"  ⚠️ 등급 B (오차 ±10% 이내)")
        else:
            quality_grade = 'C'
            print(f"  ❌ 등급 C (오차 >10%)")
        
        # 미상 비용 처리
        unknown_amount = 0
        unknown_ratio = 0
        
        if diff < 0:  # 부족
            unknown_amount = abs(diff)
            unknown_ratio = unknown_amount / dart_sga_total
            
            if unknown_ratio > 0.20:
                print(f"  ❌ 미상 비용 {unknown_ratio:.1%} (>20%) - 재파싱 필요")
                quality_grade = 'C'
            elif unknown_ratio > 0.10:
                print(f"  ⚠️ 미상 비용 {unknown_ratio:.1%} (10-20%)")
                if quality_grade == 'A':
                    quality_grade = 'B'
                
                # 미상 비용 추가
                if unit == '백만원':
                    items['기타(미상)'] = unknown_amount * 100
                elif unit == '천원':
                    items['기타(미상)'] = unknown_amount * 100_000
                else:
                    items['기타(미상)'] = unknown_amount * 100_000_000
                
                print(f"  ✅ 미상 잡비용 추가: {unknown_amount:,.1f}억원")
            else:
                print(f"  ✅ 미상 비용 {unknown_ratio:.1%} (<10%) - 양호")
                
                # 미상 비용 추가
                if unit == '백만원':
                    items['기타(미상)'] = unknown_amount * 100
                elif unit == '천원':
                    items['기타(미상)'] = unknown_amount * 100_000
                
                print(f"  ✅ 미상 잡비용 추가: {unknown_amount:,.1f}억원")
        
        elif diff > 0:  # 과다
            print(f"  ❌ 과다 파싱 {diff_ratio:.1%}")
            print(f"  원인: 매출원가/금융/투자 항목 혼입 가능성")
            quality_grade = 'C'
    
    else:
        quality_grade = 'N/A'
        unknown_amount = 0
        unknown_ratio = 0
    
    # 6. 결과 출력
    print(f"\n{'='*70}")
    print(f"✅ {len(items)}개 SG&A 항목 (등급: {quality_grade})")
    print(f"{'='*70}")
    
    sorted_items = sorted(items.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print(f"\nTop 15:")
    for i, (name, amt) in enumerate(sorted_items[:15], 1):
        amt_billion = amt / 100 if unit == '백만원' else amt / 100_000 if unit == '천원' else amt / 100_000_000
        print(f"{i:2d}. {name:45s}: {amt:>15,.0f} {unit} ({amt_billion:>10,.1f}억)")
    
    # 7. 저장
    output = {
        'company': args.company,
        'year': args.year,
        'rcept_no': args.rcept_no,
        'unit': unit,
        'sga_details_million': {k: round(v, 1) for k, v in items.items()},
        'sga_count': len(items),
        'quality_validation': {
            'grade': quality_grade,
            'confidence': 0.95 if quality_grade == 'A' else 0.80 if quality_grade == 'B' else 0.60,
            'dart_total_billion': dart_sga_total if dart_sga_total else 0,
            'parsed_total_billion': parsed_total if 'parsed_total' in locals() else 0,
            'difference_ratio': diff_ratio if 'diff_ratio' in locals() else 0,
            'unknown_amount_billion': unknown_amount,
            'unknown_ratio': unknown_ratio,
            'validation_date': '2025-11-13',
            'parser_version': 'v2.0_validated'
        }
    }
    
    filename = f"data/raw/{args.company.replace(' ', '_')}_sga_v2.yaml"
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\n✅ {filename} 저장")
    print(f"\n품질 메타데이터:")
    print(f"  등급: {quality_grade}")
    print(f"  신뢰도: {output['quality_validation']['confidence']:.0%}")
    if unknown_ratio > 0:
        print(f"  미상 비용: {unknown_ratio:.1%}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

