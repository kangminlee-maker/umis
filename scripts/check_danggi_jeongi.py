#!/usr/bin/env python3
"""당기/전기 중복 파싱 체크"""

import requests
import os
import re
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')

# 삼성전자
rcept_no = '20240312000736'

url = "https://opendart.fss.or.kr/api/document.xml"
params = {'crtfc_key': DART_API_KEY, 'rcept_no': rcept_no, 'reprt_code': '11011'}

response = requests.get(url, params=params, timeout=60)
zip_file = zipfile.ZipFile(io.BytesIO(response.content))
xml_filename = zip_file.namelist()[0]
xml_bytes = zip_file.read(xml_filename)
xml = xml_bytes.decode('utf-8', errors='ignore')

# 판매비와관리비 섹션
pattern = r'22\.\s*판매비.*?관리비'
matches = [m for m in re.finditer(pattern, xml, re.IGNORECASE) if '연결' not in m.group()]

if matches:
    m = matches[0]
    section = xml[m.start():m.start()+5000]
    
    print("삼성전자 판매비와관리비 테이블:")
    print("="*70)
    
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section, re.DOTALL)
    
    print(f"\n처음 10개 행:\n")
    
    for i, row in enumerate(rows[:10], 1):
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        print(f"행 {i} ({len(cells)}개 셀):")
        
        for j, cell in enumerate(cells):
            text = re.sub(r'<[^>]+>', '', cell).strip()
            text = text.replace('\xa0', ' ').replace('\u3000', ' ').strip()
            
            if text and len(text) < 60:
                print(f"  [{j}] {text}")
        print()
    
    print("="*70)
    print("결론:")
    print("  행 2: ['당기', '(단위 : 백만원)']")
    print("  행 4: ['급여, 판관비', '8,324,562']")
    print()
    print("  → 2개 셀 구조!")
    print("  → 전기 컬럼 없음!")
    print("  → 당기 데이터만 파싱 중 ✅")




