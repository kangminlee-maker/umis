#!/usr/bin/env python3
"""GS리테일 파싱 디버깅 - 실제 데이터 비교"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient
from dotenv import load_dotenv
import os

load_dotenv()

client = DARTClient(os.getenv('DART_API_KEY'))

# 원문 다운로드
xml = client.download_document('20240313001562', '11011')

# 섹션 찾기
pattern = r'28\.\s*판매비.*?관리비'
matches = list(re.finditer(pattern, xml, re.IGNORECASE))

print("="*70)
print("GS리테일 파싱 디버깅")
print("="*70)

print(f"\n'28. 판매비와관리비' 발견: {len(matches)}개")

if matches:
    m = matches[0]
    
    # 범위별로 테스트
    for range_size in [5000, 10000, 15000, 25000]:
        section = xml[m.start():m.start()+range_size]
        
        rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section, re.DOTALL)
        
        def extract_text(cell):
            text = re.sub(r'<[^>]+>', '', cell).strip()
            return text.replace('\xa0', ' ').replace('\u3000', ' ').strip()
        
        # "급여"가 포함된 행 수 카운트
        geupyeo_count = 0
        gamgasangak_count = 0
        
        for row in rows:
            cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
            
            if len(cells) >= 2:
                item_name = extract_text(cells[0])
                
                if '급여' in item_name and '및상여' in item_name:
                    geupyeo_count += 1
                
                if '감가상각' in item_name:
                    gamgasangak_count += 1
        
        print(f"\n범위 {range_size:,}자:")
        print(f"  테이블 행: {len(rows)}개")
        print(f"  '급여및상여' 발견: {geupyeo_count}번")
        print(f"  '감가상각' 발견: {gamgasangak_count}번")
        
        if geupyeo_count > 1 or gamgasangak_count > 1:
            print(f"  ⚠️ 중복 발견!")

print(f"\n{'='*70}")
print("결론:")
print("="*70)

print("""
범위가 클수록 중복 항목 증가
→ 다른 테이블이 범위 안에 포함됨
→ 같은 항목이 여러 번 파싱됨
→ 표준 계정 매칭 시 합산 → 2-3배!

해결책:
1. 범위를 더 줄이기 (5,000자?)
2. 또는 첫 번째 테이블만 (테이블 경계 감지)
3. 또는 중복 제거 (같은 항목명은 첫 번째만)
""")




