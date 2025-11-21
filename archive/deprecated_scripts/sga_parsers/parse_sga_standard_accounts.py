#!/usr/bin/env python3
"""
표준 계정 매칭 방식 SG&A 파서

핵심 아이디어 (사용자 제안):
- 17개 표준 SG&A 계정 정의
- 각 계정의 변형 표현 리스트
- 파싱된 항목을 표준 계정에 매칭
- 매칭된 것만 사용 → 품질 자동 향상!

특징:
- 매출원가, 금융, 투자 항목 자동 제외
- DART 총액과 실시간 비교
- 미상 비용 자동 계산
"""

import requests
import os
import re
import zipfile
import io
import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
DART_BASE_URL = "https://opendart.fss.or.kr/api"


# 표준 SG&A 계정 (16개) + 변형 표현
# ⚠️ 경상연구개발비 제외 (제조원가 포함 가능성)
STANDARD_SGA_ACCOUNTS = {
    '직원급여': {
        'variations': ['급여', '임금', '인건비', '봉급', '직원급여', '종업원급여', '급료'],
        'category': '인건비',
        'variable': False
    },
    '퇴직급여': {
        'variations': ['퇴직급여', '퇴직연금', '퇴직금', '퇴직비용'],
        'category': '인건비',
        'variable': False
    },
    '복리후생비': {
        'variations': ['복리후생비', '복리후생', '후생비'],
        'category': '인건비',
        'variable': False
    },
    # '경상연구개발비': 제외! (제조원가 포함 가능성)
    '세금과공과금': {
        'variations': ['세금과공과', '세금공과', '세금과공과금', '공과금'],
        'category': '세금',
        'variable': False
    },
    '유형자산감가상각비': {
        'variations': ['유형자산감가상각비', '유형자산상각비', '건물감가상각', '감가상각비'],
        'category': '감가상각',
        'variable': False
    },
    '지급임차료': {
        'variations': ['지급임차료', '임차료', '렌탈비', '리스료'],
        'category': '임차',
        'variable': False
    },
    '지급수수료': {
        'variations': ['지급수수료', '수수료', '전산수수료', '위탁수수료', '인건비성수수료', '용역비'],
        'category': '수수료',
        'variable': True  # 준변동비 (거래량 비례 가능)
    },
    '보험료': {
        'variations': ['보험료', '보험비'],
        'category': '보험',
        'variable': False
    },
    '운반비': {
        'variations': ['운반비', '운송비', '물류비', '배송비', '운반보관비', '운반및보관비'],
        'category': '물류',
        'variable': True  # 변동비
    },
    '광고선전비': {
        'variations': ['광고선전비', '광고비', '광고선전', '광고'],
        'category': '마케팅',
        'variable': True  # 변동비
    },
    '수도광열비': {
        'variations': ['수도광열비', '전기료', '수도요금', '가스비'],
        'category': '유틸리티',
        'variable': False
    },
    '판매촉진비': {
        'variations': ['판매촉진비', '판촉비', '프로모션비'],
        'category': '마케팅',
        'variable': True  # 변동비
    },
    '접대비': {
        'variations': ['접대비', '교제비', '회의비'],
        'category': '접대',
        'variable': False
    },
    '무형자산상각비': {
        'variations': ['무형자산상각비', '무형자산상각', '소프트웨어상각'],
        'category': '감가상각',
        'variable': False,
        'priority': 2  # 유형보다 먼저 매칭
    },
    '주식보상비용': {
        'variations': ['주식보상비용', '주식보상', '스톡옵션'],
        'category': '인건비',
        'variable': False
    },
    '사용권자산상각비': {
        'variations': ['사용권자산상각비', '사용권자산감가상각', '사용권상각'],
        'category': '감가상각',
        'variable': True,  # 준변동비 (가맹점 수 등)
        'priority': 1  # 가장 먼저 매칭
    },
    '투자부동산감가상각비': {
        'variations': ['투자부동산감가상각비', '투자부동산상각'],
        'category': '감가상각',
        'variable': False,
        'priority': 1
    },
}

# 추가 SG&A 항목 (위 16개 외)
ADDITIONAL_SGA = {
    'variations': [
        '여비교통비', '출장비', '교통비',
        '통신비',
        '소모품비', '사무용품비',
        '수선비', '유지보수비',
        '교육훈련비', '훈련비',
        '행사비', '이벤트비',
        '조사연구비', '시장조사비',
        '도서인쇄비',
        '포장비',
        '잡비',
        '장치장식비',  # GS리테일
        '품질관리비',  # SK하이닉스
    ]
}

# 강력 제외 키워드 (투자/처분/손상)
STRONG_EXCLUDE = [
    '투자주식', '관계기업', '종속기업', '공동기업',
    '처분이익', '처분손실', '처분손익',
    '손상차손', '손상차손환입', '손상차손환입',
    '평가이익', '평가손실', '평가손익',
    '대손상각비', '대손충당금',
]


def match_to_standard_account(item_name: str) -> Optional[str]:
    """
    파싱된 항목을 표준 계정에 매칭
    
    Returns:
        표준 계정명 or None (제외 항목은 None)
    """
    
    item_clean = item_name.replace(', 판관비', '').strip().lower()
    
    # 강력 제외 (투자/처분/손상)
    for exclude_keyword in STRONG_EXCLUDE:
        if exclude_keyword in item_name:
            return None  # 명시적 제외!
    
    # 우선순위 매칭 (구체적 → 일반적)
    # Priority 1: 사용권자산, 투자부동산 먼저
    # Priority 2: 무형자산
    # Priority 3: 유형자산 (감가상각비 일반)
    
    priority_accounts = []
    normal_accounts = []
    
    for standard_name, info in STANDARD_SGA_ACCOUNTS.items():
        priority = info.get('priority', 3)
        if priority < 3:
            priority_accounts.append((priority, standard_name, info))
        else:
            normal_accounts.append((standard_name, info))
    
    # 우선순위 정렬
    priority_accounts.sort(key=lambda x: x[0])
    
    # 우선순위 매칭
    for _, standard_name, info in priority_accounts:
        for variation in info['variations']:
            if variation in item_clean:
                return standard_name
    
    # 일반 매칭
    for standard_name, info in normal_accounts:
        for variation in info['variations']:
            if variation in item_clean:
                return standard_name
    
    # 추가 SG&A 항목
    for variation in ADDITIONAL_SGA['variations']:
        if variation in item_clean:
            return f"기타_{variation}"  # 원본 유지
    
    return None


def count_standard_accounts_in_section(section_text: str) -> int:
    """
    섹션에서 표준 계정이 몇 개 언급되는지 카운트
    
    Returns:
        표준 계정 언급 개수
    """
    section_lower = section_text.lower()
    matched_accounts = set()
    
    for standard_name, info in STANDARD_SGA_ACCOUNTS.items():
        for variation in info['variations']:
            if variation in section_lower:
                matched_accounts.add(standard_name)
                break  # 한 번만 카운트
    
    # 추가 SG&A 항목도 카운트
    for variation in ADDITIONAL_SGA['variations']:
        if variation in section_lower:
            matched_accounts.add(f'additional_{variation}')
    
    return len(matched_accounts)


def extract_all_sga_sections(xml: str, min_standard_accounts: int = 10) -> List[Dict]:
    """
    XML에서 모든 판관비 섹션 추출 및 필터링
    
    Args:
        xml: DART XML 원문
        min_standard_accounts: 최소 표준 계정 개수 (기본 10개 = 60%)
    
    Returns:
        List of {'section_text': str, 'section_num': int, 'start_pos': int, 
                 'standard_account_count': int, 'score': float}
    """
    patterns = [
        r'(\d+)\.\s*판매비.*?관리비',
        r'(\d+)\.\s*일반영업비용',
    ]
    
    candidate_sections = []
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, xml, re.IGNORECASE))
        
        for m in matches:
            section_num = int(m.group(1))
            section_text = xml[m.start():m.start()+10000]  # 10,000자
            
            # 표준 계정 개수 카운트
            standard_count = count_standard_accounts_in_section(section_text)
            
            # 최소 임계값 필터링
            if standard_count >= min_standard_accounts:
                score = 0
                
                # 표준 계정 개수 점수
                score += standard_count * 5
                
                # "연결" 체크 (규칙 기반!)
                title = m.group()
                if '연결' in title or '연결' in section_text[:500]:
                    score -= 50  # 큰 패널티
                
                # "당기" 체크
                if '당기' in section_text[:2000]:
                    score += 10
                
                candidate_sections.append({
                    'section_text': section_text,
                    'section_num': section_num,
                    'start_pos': m.start(),
                    'standard_account_count': standard_count,
                    'score': score,
                    'title': title
                })
    
    # 점수순 정렬
    candidate_sections.sort(key=lambda x: x['score'], reverse=True)
    
    return candidate_sections


def parse_with_standard_matching(xml: str) -> Tuple[Dict[str, float], str, Dict]:
    """
    표준 계정 매칭 방식으로 파싱
    
    Returns:
        (matched_items, unit, stats)
    """
    
    # 섹션 찾기 (새 로직: 표준 계정 10개 이상)
    candidate_sections = extract_all_sga_sections(xml, min_standard_accounts=10)
    
    if not candidate_sections:
        return {}, '백만원', {'error': 'No sections with 10+ standard accounts'}
    
    # 최고 점수 섹션 선택
    section = candidate_sections[0]['section_text']
    
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
    
    # 테이블 행 파싱
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section, re.DOTALL)
    
    def extract_text(cell):
        p_match = re.search(r'<P[^>]*>(.*?)</P>', cell, re.DOTALL)
        if p_match:
            text = re.sub(r'<[^>]+>', '', p_match.group(1))
            return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
        text = re.sub(r'<[^>]+>', '', cell)
        return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
    
    # 모든 항목 파싱 (매칭 전)
    all_items = {}
    
    for row in rows:
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        if len(cells) >= 2:
            item_name = extract_text(cells[0])
            amount_str = extract_text(cells[-1])
            
            item_name = re.sub(r',\s*판관비$', '', item_name)
            amount_clean = re.sub(r'[^\d-]', '', amount_str)
            
            if item_name and amount_clean and len(item_name) > 1:
                try:
                    amount = float(amount_clean)
                    min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                    if abs(amount) > min_threshold:
                        all_items[item_name] = amount
                except:
                    pass
    
    # 표준 계정 매칭
    matched = {}
    unmatched = {}
    
    for item, amount in all_items.items():
        standard_account = match_to_standard_account(item)
        
        if standard_account:
            # 같은 표준 계정에 여러 항목 매칭되면 합산
            if standard_account in matched:
                matched[standard_account] += amount
            else:
                matched[standard_account] = amount
        else:
            unmatched[item] = amount
    
    # 통계
    stats = {
        'total_parsed': len(all_items),
        'matched': len(matched),
        'unmatched': len(unmatched),
        'unmatched_items': list(unmatched.keys())
    }
    
    return matched, unit, stats


def main():
    parser = argparse.ArgumentParser(description='표준 계정 매칭 SG&A 파서')
    parser.add_argument('--company', required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--rcept-no', required=True)
    args = parser.parse_args()
    
    print("="*70)
    print(f"🎯 표준 계정 매칭 파서: {args.company} ({args.year})")
    print("="*70)
    print(f"\n전략: 17개 표준 SG&A 계정에 매칭")
    
    # corp_code
    from umis_rag.utils.dart_api import DARTClient
    client = DARTClient(DART_API_KEY)
    
    corp_code = client.get_corp_code(args.company)
    if not corp_code:
        print("❌ 기업 코드 없음")
        return 1
    
    # DART 총액
    print(f"\n[검증] DART SG&A 총액...")
    financials = client.get_financials(corp_code, args.year, fs_div='OFS')
    
    dart_sga_total = 0
    if financials:
        for item in financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amount_str = item.get('thstrm_amount', '0')
                try:
                    dart_sga_total = float(amount_str.replace(',', '')) / 100_000_000
                    break
                except:
                    pass
    
    if dart_sga_total:
        print(f"  ✓ DART SG&A: {dart_sga_total:,.1f}억원")
    else:
        print(f"  ⚠️ DART 총액 없음")
    
    # 원문 다운로드
    print(f"\n원문 파싱...")
    xml = client.download_document(args.rcept_no, '11011')
    
    if not xml:
        print("❌ 다운로드 실패")
        return 1
    
    # 표준 계정 매칭
    matched, unit, stats = parse_with_standard_matching(xml)
    
    print(f"  ✓ 전체 파싱: {stats['total_parsed']}개 항목")
    print(f"  ✓ 표준 매칭: {stats['matched']}개 계정")
    print(f"  ⚠️ 미매칭: {stats['unmatched']}개 항목")
    
    if stats['unmatched'] > 0:
        print(f"\n  미매칭 항목 (Top 5):")
        for item in stats['unmatched_items'][:5]:
            print(f"    - {item}")
    
    # 합계 비교
    print(f"\n[검증] 합계 비교...")
    
    if unit == '백만원':
        matched_total = sum(matched.values()) / 100
    elif unit == '천원':
        matched_total = sum(matched.values()) / 100_000
    else:
        matched_total = sum(matched.values()) / 100_000_000
    
    if dart_sga_total:
        diff = matched_total - dart_sga_total
        diff_ratio = diff / dart_sga_total
        
        print(f"  DART 총액:   {dart_sga_total:>12,.1f}억원")
        print(f"  매칭 합계:   {matched_total:>12,.1f}억원")
        print(f"  차이:       {diff:>12,.1f}억원 ({diff_ratio:>6.1%})")
        
        # 품질 평가
        if abs(diff_ratio) <= 0.05:
            grade = 'A'
            print(f"  ✅ 등급 A (오차 ±5%)")
        elif abs(diff_ratio) <= 0.10:
            grade = 'B'
            print(f"  ⚠️ 등급 B (오차 ±10%)")
        else:
            grade = 'C'
            print(f"  ❌ 등급 C (오차 >10%)")
        
        # 미상 비용
        if diff < 0:  # 부족
            unknown = abs(diff)
            unknown_ratio = unknown / dart_sga_total
            
            print(f"\n  미상 비용: {unknown:,.1f}억원 ({unknown_ratio:.1%})")
            
            if unknown_ratio > 0.20:
                print(f"  ❌ 미상 >20% - 신뢰도 낮음")
            elif unknown_ratio > 0.10:
                print(f"  ⚠️ 미상 10-20% - 주의")
            else:
                print(f"  ✅ 미상 <10% - 양호")
                
                # 미상 비용 추가
                if unit == '백만원':
                    matched['기타(미상)'] = unknown * 100
                elif unit == '천원':
                    matched['기타(미상)'] = unknown * 100_000
    else:
        grade = 'N/A'
    
    # 결과
    print(f"\n{'='*70}")
    print(f"✅ {len(matched)}개 표준 계정 (등급: {grade})")
    print(f"{'='*70}")
    
    print(f"\n표준 SG&A 계정:")
    for i, (account, amount) in enumerate(sorted(matched.items(), key=lambda x: x[1], reverse=True), 1):
        amt_billion = amount / 100 if unit == '백만원' else amount / 100_000 if unit == '천원' else amount / 100_000_000
        var_mark = "💰" if STANDARD_SGA_ACCOUNTS.get(account, {}).get('variable') else "🔒"
        print(f"{i:2d}. {var_mark} {account:25s}: {amt_billion:>10,.1f}억원")
    
    # 저장
    output = {
        'company': args.company,
        'year': args.year,
        'rcept_no': args.rcept_no,
        'unit': unit,
        'parsing_method': 'standard_account_matching',
        'standard_accounts': {k: round(v, 1) for k, v in matched.items()},
        'account_count': len(matched),
        'quality_validation': {
            'grade': grade,
            'confidence': 0.95 if grade == 'A' else 0.80 if grade == 'B' else 0.60,
            'dart_total_billion': dart_sga_total if dart_sga_total else 0,
            'matched_total_billion': matched_total if 'matched_total' in locals() else 0,
            'difference_ratio': diff_ratio if 'diff_ratio' in locals() else 0,
            'unknown_ratio': unknown_ratio if 'unknown_ratio' in locals() else 0,
            'matched_count': stats['matched'],
            'unmatched_count': stats['unmatched'],
            'validation_date': '2025-11-13'
        }
    }
    
    filename = f"data/raw/{args.company.replace(' ', '_')}_sga_standard.yaml"
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\n✅ {filename} 저장")
    print(f"\n품질:")
    print(f"  등급: {grade}")
    print(f"  매칭률: {stats['matched']}/{stats['total_parsed']} = {stats['matched']*100//stats['total_parsed']}%")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

