#!/usr/bin/env python3
"""
Clean SG&A 파일 생성

검증 시스템이 발견한 문제를 수정:
- 매출원가, 금융, 투자, 합계 항목 제거
- SG&A만 추출
- DART 총액과 비교
- 미상 비용 계산 및 추가
"""

import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# validate_sga_quality.py에서 가져오기
from validate_sga_quality import classify_account_type, validate_sga_parsing, DARTClient


def create_clean_sga_file(
    company_name: str,
    original_filepath: Path,
    dart_sga_total: float
):
    """Clean SG&A 파일 생성"""
    
    with open(original_filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    sga_items = data.get('sga_details_million', {})
    unit = data.get('unit', '백만원')
    
    # 검증 및 정리
    validation = validate_sga_parsing(company_name, sga_items, dart_sga_total, unit)
    
    # Clean SG&A만 사용
    clean_sga = validation['clean_sga']
    
    # 미상 비용 추가 (있으면)
    if validation['unknown_amount_billion'] > 0:
        unknown_ratio = validation['unknown_ratio']
        
        if unknown_ratio > 0.20:
            print(f"  ❌ 미상 비용 {unknown_ratio:.1%} (>20%) - 파일 생성 중단")
            return None
        else:
            # 미상 잡비용 추가
            if unit == '백만원':
                unknown_million = validation['unknown_amount_billion'] * 100
            elif unit == '천원':
                unknown_million = validation['unknown_amount_billion'] * 100_000
            else:
                unknown_million = validation['unknown_amount_billion'] * 100_000_000
            
            clean_sga['기타(미상)'] = unknown_million
            print(f"  ✅ 미상 잡비용 추가: {validation['unknown_amount_billion']:,.0f}억원 ({unknown_ratio:.1%})")
    
    # 데이터 업데이트
    data['sga_details_million'] = clean_sga
    data['sga_count'] = len(clean_sga)
    data['quality_validation'] = {
        'grade': validation['quality_grade'],
        'confidence': validation['confidence'],
        'dart_total_billion': validation['dart_total'],
        'parsed_total_billion': validation['parsed_total'],
        'difference_ratio': validation['difference_ratio'],
        'unknown_ratio': validation.get('unknown_ratio', 0),
        'validation_date': '2025-11-13'
    }
    
    # Clean 파일 저장
    clean_filepath = original_filepath.parent / f"{original_filepath.stem.replace('_sga_complete', '_sga_clean')}.yaml"
    
    with open(clean_filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print(f"  ✅ Clean 파일 저장: {clean_filepath.name}")
    
    return validation['quality_grade']


def main():
    print("="*70)
    print("Clean SG&A 파일 생성")
    print("="*70)
    
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    client = DARTClient(os.getenv('DART_API_KEY'))
    
    sga_files = list(Path('data/raw').glob('*_sga_complete.yaml'))
    
    results = []
    
    for filepath in sorted(sga_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        company = data.get('company', filepath.stem)
        year = data.get('year', 2023)
        
        # DART 총액 조회
        corp_code = client.get_corp_code(company)
        
        if not corp_code:
            continue
        
        financials = client.get_financials(corp_code, year, fs_div='OFS')
        
        if not financials:
            continue
        
        # SG&A 총액
        dart_sga = 0
        for item in financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amount_str = item.get('thstrm_amount', '0')
                try:
                    dart_sga = float(amount_str.replace(',', '')) / 100_000_000
                    break
                except:
                    pass
        
        if dart_sga == 0:
            continue
        
        # Clean 파일 생성
        grade = create_clean_sga_file(company, filepath, dart_sga)
        
        if grade:
            results.append((company, grade))
    
    print(f"\n{'='*70}")
    print(f"Clean 파일 생성 완료")
    print(f"{'='*70}")
    
    for company, grade in results:
        print(f"  {grade} - {company}")
    
    print(f"\n총 {len(results)}개 파일")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())




