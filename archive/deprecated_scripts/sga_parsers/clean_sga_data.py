#!/usr/bin/env python3
"""
SG&A 데이터 정리

문제: 합계, 순이익, 금융비용 등 SG&A가 아닌 항목 포함
해결: 강화된 필터로 정리
"""

import yaml
from pathlib import Path

# 제외할 키워드 (강화!)
EXCLUDE_KEYWORDS = [
    # 기본
    '합계', '계', '소계', '총액', 'Total', '총계',
    
    # 손익계산서 항목
    '순이익', '당기순이익', '법인세비용', '세전이익', '영업이익', '포괄손익',
    '매출', '매출액', '매출원가', '매출총이익',
    
    # 금융 항목
    '금융수익', '금융비용', '금융손익', '순금융',
    '이자수익', '이자비용',
    '배당금수익', '외환차익', '외환차손',
    '파생상품',
    
    # 투자 관련
    '투자주식', '관계기업', '공동기업', '종속기업',
    '평가손실', '평가이익', '손상차손', '손상차손환입',
    '처분이익', '처분손실',
    
    # 기타 제외
    '법인세', '조정', '기타의',
    '주식수', '주당', 'EPS',
    
    # 성격별 분류 (손익계산서 섹션)
    '성격별', '기능별',
]


def clean_sga_items(sga_items: dict) -> dict:
    """SG&A 항목에서 문제 항목 제거"""
    
    cleaned = {}
    removed = {}
    
    for item, amount in sga_items.items():
        # 제외 여부 판단
        should_exclude = False
        
        for keyword in EXCLUDE_KEYWORDS:
            if keyword in item:
                should_exclude = True
                removed[item] = amount
                break
        
        if not should_exclude:
            cleaned[item] = amount
    
    return cleaned, removed


def clean_company_file(filepath: Path):
    """단일 기업 파일 정리"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    company = data.get('company', filepath.stem)
    original_items = data.get('sga_details_million', {})
    
    print(f"\n{'='*70}")
    print(f"📋 {company} 데이터 정리")
    print(f"{'='*70}")
    
    print(f"  원본 항목: {len(original_items)}개")
    
    # 정리
    cleaned, removed = clean_sga_items(original_items)
    
    print(f"  제거 항목: {len(removed)}개")
    if removed:
        for item in list(removed.keys())[:5]:
            print(f"    - {item}")
        if len(removed) > 5:
            print(f"    ... ({len(removed) - 5}개 더)")
    
    print(f"  정리 후: {len(cleaned)}개")
    
    # 데이터 업데이트
    data['sga_details_million'] = cleaned
    data['sga_count'] = len(cleaned)
    
    # 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print(f"  ✅ 저장 완료")
    
    return len(cleaned), len(removed)


def main():
    print("="*70)
    print("SG&A 데이터 정리")
    print("="*70)
    
    problem_files = [
        'data/raw/CJ_ENM_sga_complete.yaml',
        'data/raw/유한양행_sga_complete.yaml',
        'data/raw/SK하이닉스_sga_complete.yaml',
        'data/raw/LG생활건강_sga_complete.yaml',
    ]
    
    results = []
    
    for filepath_str in problem_files:
        filepath = Path(filepath_str)
        if filepath.exists():
            cleaned_count, removed_count = clean_company_file(filepath)
            results.append((filepath.stem, cleaned_count, removed_count))
    
    print(f"\n{'='*70}")
    print(f"정리 완료")
    print(f"{'='*70}")
    
    for company, cleaned, removed in results:
        print(f"\n{company}:")
        print(f"  정리 후: {cleaned}개 (제거: {removed}개)")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())




