#!/usr/bin/env python3
"""
여러 기업의 SG&A 섹션 패턴을 수집하여 AI 학습용 데이터 생성

목적:
- 하드코딩 대신 데이터 기반 패턴 학습
- LLM을 활용한 자동 규칙 생성
"""

import requests
import os
import re
import zipfile
import io
from dotenv import load_dotenv
import json

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
DART_BASE_URL = "https://opendart.fss.or.kr/api"

# 이미 성공한 기업들의 rcept_no
SAMPLES = [
    {'company': 'BGF리테일', 'rcept_no': '20240327000690', 'year': 2023},
    {'company': '이마트', 'rcept_no': '20240320001504', 'year': 2023},
    {'company': '삼성전자', 'rcept_no': '20240312000736', 'year': 2023},
    {'company': 'LG전자', 'rcept_no': '20240318000755', 'year': 2023},
    {'company': 'GS리테일', 'rcept_no': '20240313001562', 'year': 2023},
    {'company': '유한양행', 'rcept_no': '20240329001184', 'year': 2023},
    {'company': '아모레퍼시픽', 'rcept_no': '20240329001043', 'year': 2023},
    {'company': 'LG생활건강', 'rcept_no': '20240329000851', 'year': 2023},
    {'company': 'CJ ENM', 'rcept_no': '20240329000596', 'year': 2023},
    {'company': 'SK하이닉스', 'rcept_no': '20240329000403', 'year': 2023},
    {'company': '하이브', 'rcept_no': '20250321001187', 'year': 2024},
]

def extract_sga_section_metadata(xml: str, company: str) -> dict:
    """
    SG&A 섹션의 메타데이터 추출
    - 섹션 제목들
    - 테이블 구조
    - 컬럼 헤더
    - 특수 패턴
    """
    
    # 1. 모든 섹션 번호 + 제목 찾기 (판매비, 영업비, 관리비 관련)
    patterns = [
        r'(\d+)\.\s*([^<\n]*(?:판매비|관리비|영업비|일반영업)[^<\n]*)',
        r'(\d+)\.\s*([^<\n]*(?:SG&A|Operating)[^<\n]*)',
    ]
    
    sections_found = []
    for pattern in patterns:
        matches = re.finditer(pattern, xml, re.IGNORECASE)
        for m in matches:
            section_num = m.group(1)
            section_title = m.group(2).strip()
            
            # 섹션 주변 텍스트 (2000자)
            preview = xml[m.start():m.start()+2000]
            
            # "당기" 키워드 확인
            has_danggi = '당기' in preview
            
            # 테이블 구조 확인
            rows = re.findall(r'<TR[^>]*>(.*?)</TR>', preview, re.DOTALL)
            
            # 컬럼 헤더 추출 (첫 3개 행)
            headers = []
            for row in rows[:3]:
                cells = re.findall(r'<(?:TD|TE)[^>]*>(.*?)</(?:TD|TE)>', row, re.DOTALL)
                row_texts = []
                for cell in cells[:5]:  # 첫 5개 컬럼만
                    text = re.sub(r'<[^>]+>', '', cell).strip()
                    text = text.replace('\xa0', '').replace('\u3000', '')
                    if text:
                        row_texts.append(text)
                if row_texts:
                    headers.append(row_texts)
            
            sections_found.append({
                'section_number': section_num,
                'section_title': section_title,
                'has_danggi': has_danggi,
                'row_count': len(rows),
                'headers': headers,
                'position': m.start()
            })
    
    return {
        'company': company,
        'total_sections': len(sections_found),
        'sections': sections_found
    }


def main():
    print("="*70)
    print("SG&A 섹션 패턴 수집 (AI 학습용)")
    print("="*70)
    
    all_patterns = []
    
    for sample in SAMPLES:
        company = sample['company']
        rcept_no = sample['rcept_no']
        year = sample['year']
        
        print(f"\n[{len(all_patterns)+1}/{len(SAMPLES)}] {company} ({year})")
        
        try:
            # 원문 다운로드
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
            
            # 메타데이터 추출
            metadata = extract_sga_section_metadata(xml, company)
            all_patterns.append(metadata)
            
            # 요약 출력
            print(f"  ✓ {metadata['total_sections']}개 섹션 발견")
            for sec in metadata['sections'][:3]:  # 처음 3개만
                print(f"    - {sec['section_number']}. {sec['section_title'][:50]}")
                print(f"      당기: {sec['has_danggi']}, 행: {sec['row_count']}")
            
        except Exception as e:
            print(f"  ✗ 오류: {e}")
    
    # JSON 저장
    output_file = 'data/raw/sga_patterns_for_llm.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_patterns, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ {len(all_patterns)}개 기업 패턴 수집 완료!")
    print(f"파일: {output_file}")
    print(f"\n다음 단계:")
    print(f"  1. LLM에게 이 JSON 파일 제공")
    print(f"  2. 패턴 규칙 자동 생성 요청")
    print(f"  3. Robust 파서 코드 생성")
    print("="*70)
    
    # 패턴 요약
    print("\n패턴 요약:")
    
    all_titles = []
    for p in all_patterns:
        for sec in p['sections']:
            title = sec['section_title']
            if any(kw in title for kw in ['판매비', '관리비', '영업비', '일반영업']):
                all_titles.append(title)
    
    # 유니크 제목들
    unique_titles = list(set(all_titles))
    unique_titles.sort()
    
    print(f"\n발견된 고유 섹션 제목 ({len(unique_titles)}개):")
    for i, title in enumerate(unique_titles, 1):
        print(f"  {i}. {title}")
    
    return all_patterns


if __name__ == "__main__":
    patterns = main()




