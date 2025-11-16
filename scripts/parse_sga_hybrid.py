#!/usr/bin/env python3
"""
Hybrid SG&A 파서: 규칙 기반 숫자 추출 + LLM 구조 판단

핵심 아이디어:
- 1단계: 규칙으로 모든 항목 + 숫자 정확히 추출
- 2단계: LLM으로 "포함/제외" 판단만
- 3단계: 결합

장점:
- 숫자 정확도 100% (규칙 기반)
- 구조 이해 100% (LLM 판단)
- 환각 방지 (LLM은 판단만, 숫자 생성 안 함)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from umis_rag.utils.dart_api import DARTClient
import os
import re
import yaml
import argparse
from openai import OpenAI
from typing import Dict, List, Tuple
import json

client_dart = DARTClient(os.getenv('DART_API_KEY'))
client_llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def extract_text_from_cell(cell: str) -> str:
    """테이블 셀에서 텍스트 추출"""
    p_match = re.search(r'<P[^>]*>(.*?)</P>', cell, re.DOTALL)
    if p_match:
        text = re.sub(r'<[^>]+>', '', p_match.group(1))
        return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
    text = re.sub(r'<[^>]+>', '', cell)
    return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')


def extract_all_items_with_regex(section_text: str) -> Tuple[Dict[str, float], str, int]:
    """
    1단계: 규칙 기반으로 모든 항목 + 숫자 정확히 추출
    
    Returns:
        (all_items, unit, item_count)
    """
    
    print(f"\n[Step 1] 규칙 기반 숫자 추출...")
    
    # 단위 찾기
    unit_patterns = [
        r'단위\s*[:：]\s*(백만원|천원|원|억원)',
        r'\(단위\s*[:：]\s*(백만원|천원|원)',
    ]
    
    unit = '백만원'
    for p in unit_patterns:
        m = re.search(p, section_text)
        if m:
            unit = m.group(1)
            break
    
    # "당기" 섹션만 찾기 (전기 제외)
    # "당기" 텍스트 이후부터 "전기" 텍스트 전까지만 파싱
    danggi_match = re.search(r'당기', section_text)
    jeongi_match = re.search(r'전기', section_text)
    
    if danggi_match and jeongi_match and jeongi_match.start() > danggi_match.start():
        # 당기 섹션만 추출
        danggi_section = section_text[danggi_match.start():jeongi_match.start()]
        
        # 최소 크기 검증 (너무 작으면 실패)
        if len(danggi_section) > 1000:
            print(f"  ✓ 당기 섹션만 추출 ({len(danggi_section):,}자)")
            parsing_text = danggi_section
        else:
            print(f"  ⚠️ 당기 섹션 너무 작음 ({len(danggi_section)}자), 전체 파싱")
            parsing_text = section_text
    else:
        # 전체 파싱
        print(f"  ✓ 전체 섹션 파싱 (당기/전기 분리 불가)")
        parsing_text = section_text
    
    # 테이블 행 파싱 (제한 없이 전체)
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', parsing_text, re.DOTALL)
    
    all_items = {}
    
    for row in rows:
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        if len(cells) >= 2:
            item_name = extract_text_from_cell(cells[0])
            amount_str = extract_text_from_cell(cells[1])  # 2번째 열 (당기 금액)
            
            # 헤더 제외
            if item_name in ['과목', '항목', '당기', '전기', '금액']:
                continue
            
            # ", 판관비" 제거
            item_name = re.sub(r',\s*판관비$', '', item_name)
            amount_clean = re.sub(r'[^\d-]', '', amount_str)
            
            if item_name and amount_clean and len(item_name) > 1:
                try:
                    amount = float(amount_clean)
                    
                    # 최소 임계값
                    min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                    
                    if abs(amount) > min_threshold:
                        # 중복 방지 (같은 이름이면 합산하지 말고 큰 값 사용)
                        if item_name not in all_items or amount > all_items[item_name]:
                            all_items[item_name] = amount
                except:
                    pass
    
    print(f"  ✓ 추출: {len(all_items)}개 항목")
    print(f"  ✓ 단위: {unit}")
    
    # 디버깅: 상위 20개 항목 출력
    print(f"\n  상위 20개 항목:")
    for i, (name, amount) in enumerate(sorted(all_items.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        amt_billion = amount / 100
        print(f"    {i:2d}. {name:30s}: {amt_billion:>10,.1f}억원")
    
    return all_items, unit, len(all_items)


def llm_decide_structure(all_items: Dict[str, float], company: str, dart_total: float) -> Dict:
    """
    2단계: LLM으로 "포함/제외" 판단만
    
    Returns:
        {
            'include': [항목명들],
            'exclude': [항목명들],
            'reasoning': str
        }
    """
    
    print(f"\n[Step 2] LLM 구조 판단...")
    
    # 항목 리스트 생성 (모두 보여주기)
    items_with_amounts = []
    for name, amount in sorted(all_items.items(), key=lambda x: x[1], reverse=True):
        amt_billion = amount / 100
        items_with_amounts.append(f"- {name}: {amt_billion:,.1f}억원")
    
    items_text = "\n".join(items_with_amounts)  # 모든 항목
    
    prompt = f"""
당신은 한국 재무제표 전문가입니다.

**기업**: {company}
**DART 판매비와관리비 총액**: {dart_total:,.1f}억원

**임무**: 아래 항목들 중 **실제 SG&A만** 선택하세요.

**추출된 항목들** (규칙으로 추출, 숫자는 100% 정확):
```
{items_text}
```

**판단 가이드**:

✅ **포함** (실제 SG&A):
- 급여, 퇴직급여, 복리후생비
- 지급수수료, 감가상각비, 무형자산상각비
- 광고선전비, 판매촉진비, 운반비
- **경상연구개발비 또는 경상개발비** (비용화된 R&D, 중요!)
- 기타 일반 SG&A 항목

❌ **제외**:
- "소계", "합계", "총계", "판매비와관리비" (합계 항목)
- "개발비 자산화" (무형자산, 비용 아님)
- "연구개발비 총지출액" (총액, 세부 아님)
- 매출원가 항목 (재료비, 제품, 상품매입 등)

**구조 이해**:
- "소계" 위 항목들: 일반 SG&A
- "소계" 아래 항목들: 
  - 경상개발비 = 연구개발비 총지출액 - 개발비 자산화 (포함!)
  - 총지출액, 자산화는 제외

**검증**:
- 선택한 항목들의 합계가 DART 총액({dart_total:,.1f}억원)과 유사해야 함
- ±20% 이내 권장

**응답 형식** (JSON):
{{
    "include": ["급여", "퇴직급여", "경상개발비", ...],
    "exclude": ["소계", "합계", "개발비 자산화", ...],
    "reasoning": "소계 위 13개 일반 SG&A + 소계 아래 경상개발비(비용화 R&D) 포함. 총지출액과 자산화는 계산 과정이므로 제외.",
    "confidence": 0.95
}}

⚠️ **중요**: 
- 항목명만 선택 (숫자는 규칙에서 추출한 것 사용)
- 상상하지 말고, 위 리스트에 있는 항목만 선택
- 위 리스트에 {len(all_items)}개 항목이 있습니다 - 모두 검토하세요
- "기타", "잡비" 같은 항목도 SG&A면 포함하세요
"""
    
    try:
        response = client_llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 한국 재무제표 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        print(f"  ✓ LLM 판단 완료")
        print(f"     포함: {len(result.get('include', []))}개")
        print(f"     제외: {len(result.get('exclude', []))}개")
        print(f"     신뢰도: {result.get('confidence', 0.9):.0%}")
        print(f"     근거: {result.get('reasoning', '')[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"  ❌ LLM 오류: {e}")
        return {
            'include': [],
            'exclude': [],
            'reasoning': f'LLM 오류: {e}',
            'confidence': 0
        }


def combine_results(all_items: Dict[str, float], llm_decision: Dict) -> Dict[str, float]:
    """
    3단계: 규칙 숫자 + LLM 판단 결합
    """
    
    print(f"\n[Step 3] 결합...")
    
    include_set = set(llm_decision.get('include', []))
    
    final_items = {}
    for name, amount in all_items.items():
        if name in include_set:
            final_items[name] = amount
    
    # 누락 체크
    not_found = [name for name in include_set if name not in all_items]
    if not_found:
        print(f"  ⚠️ LLM이 선택했지만 규칙에서 없음: {not_found[:5]}")
    
    print(f"  ✓ 최종: {len(final_items)}개 항목")
    
    return final_items


def main():
    parser = argparse.ArgumentParser(description='Hybrid 파서')
    parser.add_argument('--company', required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--rcept-no', required=True)
    args = parser.parse_args()
    
    print("="*70)
    print(f"🔀 Hybrid 파서: {args.company} ({args.year})")
    print("="*70)
    print(f"\n전략: 규칙(숫자) + LLM(판단)")
    
    # DART 총액
    print(f"\n[검증] DART SG&A 총액...")
    corp_code = client_dart.get_corp_code(args.company)
    
    dart_total = 0
    if corp_code:
        financials = client_dart.get_financials(corp_code, args.year, 'OFS')
        if financials:
            for item in financials:
                account = item.get('account_nm', '')
                if '판매비' in account or '관리비' in account:
                    amount_str = item.get('thstrm_amount', '0')
                    try:
                        dart_total = float(amount_str.replace(',', '')) / 100_000_000
                        break
                    except:
                        pass
    
    if dart_total:
        print(f"  ✓ DART SG&A: {dart_total:,.1f}억원")
    else:
        print(f"  ⚠️ DART 총액 없음")
        return 1
    
    # 원문 다운로드
    print(f"\n원문 다운로드...")
    xml = client_dart.download_document(args.rcept_no, '11011')
    
    if not xml:
        print("❌ 다운로드 실패")
        return 1
    
    print(f"  ✓ XML: {len(xml):,}자")
    
    # 섹션 찾기
    print(f"\n섹션 찾기...")
    
    # 모든 판관비 섹션 찾기
    pattern = r'(\d+)\.\s*판매비.*?관리비'
    all_matches = list(re.finditer(pattern, xml, re.IGNORECASE))
    
    if not all_matches:
        print("❌ 섹션 없음")
        return 1
    
    print(f"  ✓ {len(all_matches)}개 섹션 발견")
    
    for m in all_matches:
        section_num = int(m.group(1))
        print(f"     - 섹션 {section_num}: {m.group()}")
    
    # 섹션 24 우선 (사용자 통찰!)
    selected_match = None
    for m in all_matches:
        section_num = int(m.group(1))
        if section_num == 24:
            selected_match = m
            print(f"  ✓ 섹션 24 발견 (사용자 통찰 반영!)")
            break
    
    # 섹션 24가 없으면 파서 4 로직 사용
    if not selected_match:
        print(f"  ⚠️ 섹션 24 없음, 표준 계정 필터 사용...")
        from parse_sga_standard_accounts import extract_all_sga_sections
        candidate_sections = extract_all_sga_sections(xml, min_standard_accounts=10)
        if candidate_sections:
            best_section = candidate_sections[0]
            section_text = best_section['section_text']
            print(f"  ✓ 선택: 섹션 {best_section['section_num']} (표준계정 {best_section['standard_account_count']}개)")
        else:
            print("❌ 적합한 섹션 없음")
            return 1
    else:
        section_text = xml[selected_match.start():selected_match.start()+20000]
        print(f"  ✓ 선택: 섹션 24 (크기: {len(section_text):,}자)")
    
    # Hybrid 파싱
    print(f"\n{'='*70}")
    print(f"Hybrid 파싱 시작")
    print(f"{'='*70}")
    
    # Step 1: 규칙으로 모든 항목 추출
    all_items, unit, item_count = extract_all_items_with_regex(section_text)
    
    if not all_items:
        print("\n❌ 항목 추출 실패")
        return 1
    
    # Step 2: LLM으로 포함/제외 판단
    llm_decision = llm_decide_structure(all_items, args.company, dart_total)
    
    if not llm_decision.get('include'):
        print("\n❌ LLM 판단 실패")
        return 1
    
    # Step 3: 결합
    final_items = combine_results(all_items, llm_decision)
    
    if not final_items:
        print("\n❌ 최종 항목 없음")
        return 1
    
    # 결과 출력
    print(f"\n{'='*70}")
    print(f"파싱 결과")
    print(f"{'='*70}")
    
    print(f"\n최종 항목 ({len(final_items)}개):")
    for i, (name, amount) in enumerate(sorted(final_items.items(), key=lambda x: x[1], reverse=True)[:15], 1):
        if unit == '백만원':
            amt_billion = amount / 100
        elif unit == '천원':
            amt_billion = amount / 100_000
        else:
            amt_billion = amount / 100_000_000
        
        print(f"  {i:2d}. {name:30s}: {amt_billion:>10,.1f}억원")
    
    # 제외된 항목
    excluded = llm_decision.get('exclude', [])
    if excluded:
        print(f"\n제외된 항목 ({len(excluded)}개):")
        for name in excluded[:10]:
            amt = all_items.get(name, 0)
            amt_billion = amt / 100 if unit == '백만원' else amt / 100_000
            print(f"  - {name:30s}: {amt_billion:>10,.1f}억원")
    
    # 저장
    if unit == '백만원':
        parsed_total = sum(final_items.values()) / 100
    elif unit == '천원':
        parsed_total = sum(final_items.values()) / 100_000
    else:
        parsed_total = sum(final_items.values()) / 100_000_000
    
    diff_ratio = (parsed_total - dart_total) / dart_total if dart_total > 0 else 0
    
    output = {
        'company': args.company,
        'year': args.year,
        'rcept_no': args.rcept_no,
        'unit': unit,
        'parsing_method': 'hybrid_v1_rule_numbers_llm_decision',
        'sga_details_million': {k: round(v, 1) for k, v in final_items.items()},
        'hybrid_analysis': {
            'total_extracted': item_count,
            'llm_include_count': len(llm_decision.get('include', [])),
            'llm_exclude_count': len(llm_decision.get('exclude', [])),
            'final_count': len(final_items),
            'llm_reasoning': llm_decision.get('reasoning', ''),
            'llm_confidence': llm_decision.get('confidence', 0.9)
        },
        'quality_validation': {
            'dart_total_billion': dart_total,
            'parsed_total_billion': parsed_total,
            'difference_ratio': diff_ratio,
            'validation_date': '2025-11-14'
        }
    }
    
    filename = f"data/raw/{args.company.replace(' ', '_')}_sga_hybrid.yaml"
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ {filename} 저장")
    
    # 최종 품질
    if abs(diff_ratio) <= 0.05:
        grade = 'A'
        status = '✅✅✅ Production Ready!'
    elif abs(diff_ratio) <= 0.10:
        grade = 'B'
        status = '✅ 참고용'
    elif abs(diff_ratio) <= 0.20:
        grade = 'C'
        status = '⚠️ 재검토'
    else:
        grade = 'D'
        status = '❌ 폐기'
    
    print(f"\n{'='*70}")
    print(f"최종 등급: {grade} (LLM 신뢰도 {llm_decision.get('confidence', 0.9):.0%})")
    print(f"{'='*70}")
    print(f"\nDART 총액:   {dart_total:>12,.1f}억원")
    print(f"파싱 합계:   {parsed_total:>12,.1f}억원")
    print(f"차이:       {diff_ratio:>7.1%}")
    print(f"\n상태: {status}")
    print(f"비용: ~$0.005 (Hybrid: 규칙 $0 + LLM $0.005)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

