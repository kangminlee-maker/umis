#!/usr/bin/env python3
"""
LLM 기반 SG&A 파서

기존 방식의 문제:
- 회사별 예외를 하드코딩 (LG전자, GS리테일, ...)
- 새로운 회사 나올 때마다 디버깅 필요
- 확장성 떨어짐

새로운 방식:
1. XML 다운로드
2. LLM에게 "판매비와관리비 섹션 찾아줘" 요청
3. LLM이 컨텍스트 기반으로 올바른 섹션 자동 선택
4. 테이블 파싱

장점:
- 제로 하드코딩
- 새로운 형식 자동 대응
- 사람처럼 판단
"""

import requests
import os
import re
import zipfile
import io
import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DART_BASE_URL = "https://opendart.fss.or.kr/api"

client = OpenAI(api_key=OPENAI_API_KEY)


def find_sga_section_with_llm(xml: str, company: str) -> dict:
    """
    LLM을 사용하여 SG&A 섹션을 찾음
    
    Returns:
        {
            'section_start': int,  # 섹션 시작 위치
            'section_title': str,  # 섹션 제목
            'confidence': float,   # 신뢰도
            'reasoning': str       # LLM의 판단 근거
        }
    """
    
    # 1. 후보 섹션들 찾기 (기존 regex)
    pattern = r'(\d+)\.\s*([^\n]{0,200})'
    matches = list(re.finditer(pattern, xml))
    
    # 판매비/관리비/영업비 관련 섹션만 필터
    candidates = []
    for m in matches:
        section_num = m.group(1)
        section_title = m.group(2)
        
        if any(keyword in section_title.lower() for keyword in 
               ['판매비', '관리비', '영업비', '일반영업', 'sga', 'operating']):
            
            # 섹션 주변 컨텍스트 (500자)
            context = xml[m.start():m.start()+500]
            
            candidates.append({
                'section_number': section_num,
                'section_title': section_title.strip(),
                'context': context,
                'position': m.start()
            })
    
    if not candidates:
        return None
    
    # 2. LLM에게 물어보기
    prompt = f"""
다음은 {company}의 DART 사업보고서 XML에서 찾은 "판매비와관리비" 관련 섹션 후보들입니다.

각 후보에 대해:
- section_number: 섹션 번호
- section_title: 섹션 제목
- context: 섹션 시작 부분 500자

당신의 임무:
1. 어느 섹션이 **실제 판매비와관리비의 세부 항목 테이블**인지 판단
2. 다음 기준으로 선택:
   - "당기" 또는 "공시금액" 키워드가 있는가?
   - 급여, 지급수수료, 감가상각비 등의 항목이 보이는가?
   - 단순히 정의나 설명이 아닌 실제 데이터 테이블인가?

후보 목록:
{yaml.dump(candidates, allow_unicode=True, default_flow_style=False)}

응답 형식 (JSON):
{{
    "selected_index": 0,  # 선택한 후보의 인덱스 (0부터 시작)
    "confidence": 0.95,   # 신뢰도 (0~1)
    "reasoning": "섹션 28은 '당기' 키워드와 함께 급여, 지급수수료 등의 항목이 명확히 보이며..."
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 한국 재무제표 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        selected_idx = result['selected_index']
        selected = candidates[selected_idx]
        
        return {
            'section_start': selected['position'],
            'section_title': selected['section_title'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning']
        }
        
    except Exception as e:
        print(f"  ⚠️ LLM 오류: {e}")
        # Fallback: "당기" 키워드가 있는 첫 번째 후보
        for c in candidates:
            if '당기' in c['context']:
                return {
                    'section_start': c['position'],
                    'section_title': c['section_title'],
                    'confidence': 0.7,
                    'reasoning': 'Fallback: "당기" 키워드 기반 선택'
                }
        
        # 최종 fallback
        return {
            'section_start': candidates[0]['position'],
            'section_title': candidates[0]['section_title'],
            'confidence': 0.5,
            'reasoning': 'Fallback: 첫 번째 후보 선택'
        }


def parse_sga_with_llm(company: str, year: int, rcept_no: str = None) -> dict:
    """
    LLM 기반 SG&A 파싱 (메인 함수)
    """
    
    print(f"\n{'='*70}")
    print(f"LLM 기반 SG&A 파싱: {company} ({year})")
    print(f"{'='*70}")
    
    # ... (기존 다운로드 로직과 동일)
    # 여기서는 핵심 차이점만 설명
    
    # 핵심 차이: LLM으로 섹션 찾기
    # section_info = find_sga_section_with_llm(xml, company)
    # 
    # if section_info:
    #     print(f"✅ LLM 선택: {section_info['section_title']}")
    #     print(f"   신뢰도: {section_info['confidence']:.1%}")
    #     print(f"   근거: {section_info['reasoning'][:100]}...")
    #     
    #     section = xml[section_info['section_start']:section_info['section_start']+25000]
    #     # ... 테이블 파싱
    
    pass


# 사용 예시
if __name__ == "__main__":
    print("""
    LLM 기반 SG&A 파서 - 개념 증명
    
    핵심 아이디어:
    1. 하드코딩된 규칙 제거
    2. LLM이 컨텍스트 기반으로 판단
    3. 새로운 형식 자동 대응
    
    구현 방법:
    - OpenAI API (gpt-4o-mini)
    - 후보 섹션을 LLM에게 제시
    - LLM이 가장 적합한 섹션 선택
    - 이유도 함께 반환 (설명 가능성)
    
    장점:
    - 제로 예외 처리
    - 확장성 높음
    - 사람처럼 판단
    
    비용:
    - 기업당 ~$0.01 (GPT-4o-mini)
    - 10개 기업 = $0.10
    
    다음 단계:
    1. 이 스크립트를 완성
    2. 기존 11개 기업으로 테스트
    3. 새로운 기업 100개로 확장성 검증
    """)




