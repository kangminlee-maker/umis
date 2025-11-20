"""
DART 재무제표 검증 모듈

핵심 기능:
- OFS/CFS 사전 검증
- XML 내 "판매비와관리비" 합계 항목 vs API 총액 비교
"""

from typing import Dict, Optional
import re
from .dart_api import DARTClient


def extract_sga_total_from_section(section_text: str) -> Optional[float]:
    """
    섹션에서 "판매비와관리비" 최종 합계 항목 추출
    
    우선순위:
    1. "합  계", "합 계", "합계" (가장 큰 금액)
    2. "판매비와관리비" 단독 (단, "기타", "일반" 등 수식어 없이)
    
    Returns:
        합계 금액 (억원) or None
    """
    
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', section_text, re.DOTALL)
    
    def extract_text(cell):
        p_match = re.search(r'<P[^>]*>(.*?)</P>', cell, re.DOTALL)
        if p_match:
            text = re.sub(r'<[^>]+>', '', p_match.group(1))
            return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
        text = re.sub(r'<[^>]+>', '', cell)
        return text.strip().replace('\xa0', ' ').replace('\u3000', ' ')
    
    # 단위 찾기
    unit = '백만원'
    unit_patterns = [
        r'단위\s*[:：]\s*(백만원|천원|원|억원)',
        r'\(단위\s*[:：]\s*(백만원|천원|원)',
    ]
    for p in unit_patterns:
        m = re.search(p, section_text)
        if m:
            unit = m.group(1)
            break
    
    candidates = []
    
    # 모든 합계/판관비 항목 수집
    for row in rows:
        cells = re.findall(r'<(?:TD|TH|TE)[^>]*>(.*?)</(?:TD|TH|TE)>', row, re.DOTALL)
        
        if len(cells) >= 2:
            item_name = extract_text(cells[0])
            amount_str = extract_text(cells[1])
            
            # 합계 항목 체크
            is_total = re.match(r'^(합|총|소)\s*계$', item_name.strip())
            
            # 판매비와관리비 체크 (수식어 없이 단독)
            is_sga_total = (
                item_name.strip() == '판매비와관리비' or
                item_name.strip() == '판매비와 관리비' or
                (item_name.strip().startswith('판매비') and item_name.strip().endswith('관리비') and len(item_name.strip()) < 15)
            )
            
            if is_total or is_sga_total:
                amount_clean = re.sub(r'[^\d-]', '', amount_str)
                
                if amount_clean:
                    try:
                        amount = float(amount_clean)
                        
                        # 단위 변환
                        if unit == '백만원':
                            amount_billion = amount / 100
                        elif unit == '천원':
                            amount_billion = amount / 100_000
                        else:
                            amount_billion = amount / 100_000_000
                        
                        candidates.append({
                            'name': item_name,
                            'amount': amount_billion,
                            'priority': 1 if is_total else 2  # 합계 우선
                        })
                    except:
                        pass
    
    if not candidates:
        return None
    
    # 우선순위 정렬: priority 낮은 것 우선, 같으면 금액 큰 것
    candidates.sort(key=lambda x: (x['priority'], -x['amount']))
    
    return candidates[0]['amount']


def validate_ofs_cfs(
    client: DARTClient,
    corp_code: str,
    year: int,
    xml_section_text: str
) -> Dict:
    """
    XML 섹션의 "판매비와관리비" 합계 vs API OFS/CFS 총액 비교
    
    프로세스:
    1. XML 섹션에서 "판매비와관리비" 합계 추출
    2. API OFS 총액 조회
    3. API CFS 총액 조회
    4. 정확히 일치하는지 비교 (±1%)
    5. 일치하는 쪽으로 판단
    
    Args:
        client: DARTClient 인스턴스
        corp_code: 기업 코드
        year: 사업연도
        xml_section_text: XML 섹션 텍스트
    
    Returns:
        {
            'is_ofs': bool,
            'is_cfs': bool,
            'ofs_total': float,
            'cfs_total': float,
            'xml_total': float,  # XML에서 추출한 합계
            'matched_type': 'OFS' or 'CFS' or 'UNKNOWN',
            'confidence': float,
            'message': str
        }
    """
    
    result = {
        'is_ofs': False,
        'is_cfs': False,
        'ofs_total': 0,
        'cfs_total': 0,
        'xml_total': 0,
        'matched_type': 'UNKNOWN',
        'confidence': 0,
        'message': ''
    }
    
    # 1. XML 섹션에서 "판매비와관리비" 합계 추출
    xml_total = extract_sga_total_from_section(xml_section_text)
    
    if not xml_total:
        result['message'] = 'XML 섹션에서 판매비와관리비 합계 항목을 찾을 수 없음'
        return result
    
    result['xml_total'] = xml_total
    
    # 2. API OFS 총액 조회
    ofs_financials = client.get_financials(corp_code, year, 'OFS', strict=False)
    
    if ofs_financials and not isinstance(ofs_financials, dict):
        for item in ofs_financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amount_str = item.get('thstrm_amount', '0')
                try:
                    result['ofs_total'] = float(amount_str.replace(',', '')) / 100_000_000
                    result['is_ofs'] = True
                    break
                except:
                    pass
    
    # 3. API CFS 총액 조회
    cfs_financials = client.get_financials(corp_code, year, 'CFS', strict=False)
    
    if cfs_financials and not isinstance(cfs_financials, dict):
        for item in cfs_financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amount_str = item.get('thstrm_amount', '0')
                try:
                    result['cfs_total'] = float(amount_str.replace(',', '')) / 100_000_000
                    result['is_cfs'] = True
                    break
                except:
                    pass
    
    # 4. XML 합계와 비교 (정확히 일치해야 함!)
    if not result['is_ofs'] and not result['is_cfs']:
        result['message'] = 'OFS/CFS 총액 모두 조회 실패'
        return result
    
    # 오차 계산 (±1% 이내여야 함)
    ofs_diff_ratio = abs(xml_total - result['ofs_total']) / result['ofs_total'] if result['is_ofs'] and result['ofs_total'] > 0 else 999
    cfs_diff_ratio = abs(xml_total - result['cfs_total']) / result['cfs_total'] if result['is_cfs'] and result['cfs_total'] > 0 else 999
    
    # 5. 판단 (정확히 일치하는 것 찾기)
    if ofs_diff_ratio <= 0.01:  # ±1% 이내
        result['matched_type'] = 'OFS'
        result['confidence'] = 1.0 - ofs_diff_ratio
        result['message'] = f'✅ 별도재무제표 (OFS) 확인 (오차 {ofs_diff_ratio*100:.2f}%)'
    elif cfs_diff_ratio <= 0.01:  # ±1% 이내
        result['matched_type'] = 'CFS'
        result['confidence'] = 1.0 - cfs_diff_ratio
        result['message'] = f'❌ 연결재무제표 (CFS) 감지 (오차 {cfs_diff_ratio*100:.2f}%) → 크롤링 필요'
    else:
        # 둘 다 정확히 일치하지 않음
        if ofs_diff_ratio < cfs_diff_ratio:
            result['matched_type'] = 'OFS'
            result['confidence'] = 1.0 - ofs_diff_ratio if ofs_diff_ratio < 1.0 else 0
            result['message'] = f'⚠️ OFS 추정 (오차 {ofs_diff_ratio*100:.1f}%, 부정확)'
        else:
            result['matched_type'] = 'CFS'
            result['confidence'] = 1.0 - cfs_diff_ratio if cfs_diff_ratio < 1.0 else 0
            result['message'] = f'❌ CFS 추정 (오차 {cfs_diff_ratio*100:.1f}%) → 크롤링 필요'
    
    return result


def print_ofs_cfs_validation(validation: Dict):
    """
    OFS/CFS 검증 결과 출력
    
    Returns:
        True: OFS 확인 (계속 진행)
        False: CFS 또는 불확실 (중단)
    """
    print(f"\n[OFS/CFS 사전 검증]")
    print("-"*70)
    
    print(f"  XML 합계:  {validation['xml_total']:>12,.1f}억원 (문서 내 '판매비와관리비' 항목)")
    
    if validation['is_ofs']:
        print(f"  API OFS:   {validation['ofs_total']:>12,.1f}억원 (별도재무제표)")
    
    if validation['is_cfs']:
        print(f"  API CFS:   {validation['cfs_total']:>12,.1f}억원 (연결재무제표)")
    
    print(f"\n  판단: {validation['matched_type']} (신뢰도 {validation['confidence']:.0%})")
    print(f"  {validation['message']}")
    
    if validation['matched_type'] == 'CFS':
        print(f"\n  ❌ 연결재무제표 감지 → 파싱 중단")
        print(f"  → DART 웹사이트에서 '재무제표 주석' 확인 필요")
        return False
    elif validation['matched_type'] == 'OFS' and validation['confidence'] > 0.95:
        print(f"  ✅ 별도재무제표 확인 (계속 진행)")
        return True
    else:
        print(f"  ⚠️ 불확실 (오차 > 1%) → 주의 필요")
        # 일단 진행하되 경고
        return True

