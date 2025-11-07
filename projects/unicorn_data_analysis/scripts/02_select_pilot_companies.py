#!/usr/bin/env python3
"""
파일럿 10개 유니콘 기업 선정

선정 기준:
1. 밸류에이션 Top (정보가 많을 확률 높음)
2. 상장 기업 우선 (공개 정보 많음)
3. 다양한 산업 분포
4. 한국 기업 포함 (로컬 정보 접근성)
"""

import json
from typing import List, Dict, Any


# 상장된 유니콘 (공개 정보 많음)
KNOWN_PUBLIC_COMPANIES = {
    "Stripe", "Databricks", "SpaceX", "Canva", "Revolut",
    "Instacart", "Klarna", "Nubank", "Rivian", "Epic Games",
    "Plaid Technologies", "Discord", "Figma", "Checkout.com",
    "배달의민족", "쿠팡", "당근마켓", "야놀자", "직방"
}

# 한국 기업 (정보 접근성 좋음)
KOREAN_COMPANIES = {
    "배달의민족", "쿠팡", "당근마켓", "야놀자", "직방", 
    "무신사", "토스", "비바리퍼블리카", "마켓컬리"
}


def select_pilot_companies(companies: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    파일럿 기업 선정
    """
    # 1. 밸류에이션 순 정렬
    sorted_companies = sorted(
        companies,
        key=lambda x: float(x['valuation']['amount_billion'].replace('$', '').replace(',', '')),
        reverse=True
    )
    
    # 2. Top 30에서 선별
    candidates = sorted_companies[:30]
    
    # 3. 선정 전략
    selected = []
    
    # 3-1. 한국 기업 우선 (2개)
    korean = [c for c in candidates if c['company'] in KOREAN_COMPANIES]
    selected.extend(korean[:2])
    
    # 3-2. 상장/유명 기업 (4개)
    public = [c for c in candidates 
              if c['company'] in KNOWN_PUBLIC_COMPANIES 
              and c not in selected]
    selected.extend(public[:4])
    
    # 3-3. 나머지는 밸류에이션 Top + 산업 다양성
    remaining = [c for c in candidates if c not in selected]
    
    # 산업 균형
    categories_selected = {c['category'] for c in selected}
    for candidate in remaining:
        if len(selected) >= top_n:
            break
        
        # 새로운 카테고리 우선
        if candidate['category'] not in categories_selected:
            selected.append(candidate)
            categories_selected.add(candidate['category'])
    
    # 아직 부족하면 Top 순서대로
    for candidate in remaining:
        if len(selected) >= top_n:
            break
        if candidate not in selected:
            selected.append(candidate)
    
    return selected[:top_n]


def calculate_data_richness_score(company: Dict) -> float:
    """
    데이터 풍부도 점수 (0-100)
    """
    score = 0
    
    # Business summary
    if company['business']['summary']:
        score += 20
    
    # Funding history
    funding_rounds = len(company.get('funding_history', []))
    score += min(funding_rounds * 5, 30)
    
    # Investors
    investors = len(company.get('select_investors', []))
    score += min(investors * 5, 30)
    
    # Details
    if company['business'].get('details'):
        score += 20
    
    return score


def main():
    print("="*80)
    print("🎯 파일럿 유니콘 기업 선정")
    print("="*80)
    print()
    
    # 데이터 로드
    with open('../unicorn_companies_rag_enhanced.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies = data['companies']
    print(f"📊 총 기업 수: {len(companies)}개")
    print()
    
    # 파일럿 선정
    print("🔍 파일럿 10개 선정 중...")
    pilot = select_pilot_companies(companies, top_n=10)
    
    print("✅ 선정 완료!")
    print()
    
    # 결과 출력
    print("="*80)
    print("🏆 파일럿 유니콘 10개")
    print("="*80)
    print()
    
    for i, company in enumerate(pilot, 1):
        valuation = company['valuation']['amount_billion']
        category = company['category']
        country = company['location']['country']
        pattern = company['business']['business_model']['pattern_type']
        funding = company['business']['growth_trajectory']['total_funding_usd_million']
        richness = calculate_data_richness_score(company)
        
        print(f"{i:2d}. {company['company']}")
        print(f"    💰 Valuation: {valuation}B")
        print(f"    🏭 Category: {category}")
        print(f"    🌍 Country: {country}")
        print(f"    📊 Pattern: {pattern}")
        print(f"    💵 Total Funding: ${funding:,.0f}M")
        print(f"    📈 Data Richness: {richness:.0f}/100")
        print(f"    🆔 Source ID: {company['rag_metadata']['source_id']}")
        print()
    
    # 저장
    output = {
        "metadata": {
            "selection_date": data['metadata']['last_updated'],
            "total_candidates": len(companies),
            "selected_count": len(pilot),
            "selection_criteria": [
                "밸류에이션 Top 30 내",
                "한국 기업 2개 포함",
                "상장/유명 기업 우선",
                "산업 다양성 고려"
            ]
        },
        "pilot_companies": pilot
    }
    
    output_file = '../pilot_companies.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("="*80)
    print(f"💾 저장 완료: {output_file}")
    print("="*80)
    print()
    
    # 통계
    print("📊 선정 통계:")
    print()
    
    countries = {}
    categories = {}
    patterns = {}
    
    for company in pilot:
        country = company['location']['country']
        category = company['category']
        pattern = company['business']['business_model']['pattern_type']
        
        countries[country] = countries.get(country, 0) + 1
        categories[category] = categories.get(category, 0) + 1
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    print("국가별:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {country}: {count}개")
    
    print()
    print("카테고리별:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count}개")
    
    print()
    print("패턴별:")
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {pattern}: {count}개")
    
    print()
    print("="*80)
    print("다음 단계:")
    print("="*80)
    print()
    print("1. pilot_companies.json 확인")
    print("2. 각 기업별 리서치 시작:")
    print("   - Problem/Solution")
    print("   - Revenue Model")
    print("   - Unit Economics (가능한 것만)")
    print("   - Critical Success Factors")
    print()
    print("3. 리서치 템플릿 사용:")
    print("   - scripts/03_research_template.md 참고")


if __name__ == "__main__":
    main()



