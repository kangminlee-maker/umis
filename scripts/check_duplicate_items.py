#!/usr/bin/env python3
"""같은 항목명 중복 파싱 체크"""

import requests
import os
import re
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')

rcept_no = '20240312000736'  # 삼성전자

url = "https://opendart.fss.or.kr/api/document.xml"
params = {'crtfc_key': DART_API_KEY, 'rcept_no': rcept_no, 'reprt_code': '11011'}

response = requests.get(url, params=params, timeout=60)
zip_file = zipfile.ZipFile(io.BytesIO(response.content))
xml_filename = zip_file.namelist()[0]
xml_bytes = zip_file.read(xml_filename)
xml = xml_bytes.decode('utf-8', errors='ignore')

# 개별 판매비와관리비
pattern = r'22\.\s*판매비.*?관리비'
matches = [m for m in re.finditer(pattern, xml, re.IGNORECASE) if '연결' not in m.group()]

if matches:
    m = matches[0]
    section = xml[m.start():m.start()+15000]
    
    print("="*70)
    print("중복 항목 체크")
    print("="*70)
    
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section, re.DOTALL)
    
    def extract_text(cell):
        text = re.sub(r'<[^>]+>', '', cell).strip()
        return text.replace('\xa0', ' ').replace('\u3000', ' ').strip()
    
    # 모든 항목명 수집
    item_names = []
    
    for row in rows:
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        if len(cells) >= 2:
            item_name = extract_text(cells[0])
            amount_str = extract_text(cells[-1])
            
            # 숫자가 있는 행만
            if item_name and re.search(r'\d', amount_str):
                item_name_clean = item_name.replace(', 판관비', '').strip()
                
                if len(item_name_clean) > 1 and item_name_clean not in ['당기', '전기', '과목', '금액']:
                    item_names.append(item_name_clean)
    
    print(f"\n파싱된 항목: {len(item_names)}개")
    
    # 중복 체크
    from collections import Counter
    counts = Counter(item_names)
    
    duplicates = {k: v for k, v in counts.items() if v > 1}
    
    if duplicates:
        print(f"\n⚠️ 중복 항목 발견: {len(duplicates)}개")
        for item, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {item:40s}: {count}번")
        
        print(f"\n결론: 같은 항목명이 여러 번 파싱됨!")
        print(f"  → 표준 계정 매칭 시 합산됨")
        print(f"  → 합계가 커지는 원인!")
    else:
        print(f"\n✅ 중복 없음")
        print(f"  모든 항목이 unique")

EOF




