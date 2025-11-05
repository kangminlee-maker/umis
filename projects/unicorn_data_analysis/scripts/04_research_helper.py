#!/usr/bin/env python3
"""
리서치 헬퍼 - 검색 쿼리 자동 생성 및 리서치 진행 지원

작성일: 2025-11-04
목적: 파일럿 리서치 효율화
"""

import json
import webbrowser
from typing import Dict, List


# ========================================
# 검색 쿼리 템플릿
# ========================================

SEARCH_QUERIES = {
    "revenue_financial": [
        '"{company}" revenue "$" billion million 2023 2024',
        '"{company}" annual revenue growth rate financial performance',
        '"{company}" profitability operating margin EBITDA',
    ],
    
    "operational_metrics": [
        '"{company}" MAU million users 2024 statistics',
        '"{company}" announces XX million customers subscribers',
        '"{company}" GMV gross merchandise value',
        '"{company}" ARR annual recurring revenue',
    ],
    
    "business_model": [
        '"{company}" business model how does make money',
        '"{company}" revenue model pricing strategy',
        '"{company}" fee structure commission rate',
    ],
    
    "problem_solution": [
        '"{company}" problem solving value proposition',
        '"{company}" why customers choose competitive advantage',
        '"{company}" founder story startup journey',
    ],
    
    "competitive": [
        '"{company}" vs {competitor} market share comparison',
        '"{company}" competitive advantage moat network effects',
        '"{company}" differentiation unique features',
    ],
}


SITE_SPECIFIC_QUERIES = {
    "techcrunch": 'site:techcrunch.com "{company}" revenue OR funding OR metrics',
    "bloomberg": 'site:bloomberg.com "{company}" financial OR revenue',
    "wsj": 'site:wsj.com "{company}" valuation OR financial',
    "theinformation": 'site:theinformation.com "{company}"',
    "sec": '"{company}" site:sec.gov 10-K OR S-1',
}


# ========================================
# URL 생성
# ========================================

def generate_google_search_url(query: str) -> str:
    """
    Google 검색 URL 생성
    """
    import urllib.parse
    encoded = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded}"


def generate_crunchbase_url(company_name: str) -> str:
    """
    Crunchbase 프로필 URL 생성
    """
    import urllib.parse
    slug = company_name.lower().replace(' ', '-').replace('.', '')
    return f"https://www.crunchbase.com/organization/{slug}"


def generate_sec_search_url(company_name: str) -> str:
    """
    SEC EDGAR 검색 URL 생성
    """
    import urllib.parse
    encoded = urllib.parse.quote(company_name)
    return f"https://www.sec.gov/cgi-bin/browse-edgar?company={encoded}&action=getcompany"


# ========================================
# 리서치 가이드 생성
# ========================================

def generate_research_guide(company: Dict) -> Dict:
    """
    개별 기업의 리서치 가이드 생성
    """
    company_name = company['company']
    category = company['category']
    country = company['location']['country']
    
    # 경쟁사 추론
    competitors = {
        "Stripe": ["PayPal", "Square", "Adyen", "Checkout.com"],
        "SpaceX": ["Blue Origin", "Rocket Lab", "Virgin Galactic"],
        "Databricks": ["Snowflake", "Google BigQuery", "Amazon Redshift"],
        "Klarna": ["Affirm", "Afterpay", "PayPal Credit"],
        "Instacart": ["DoorDash", "Uber Eats", "Amazon Fresh"],
    }
    
    competitor_list = competitors.get(company_name, [])
    
    # 검색 쿼리 생성
    queries = {}
    for category, templates in SEARCH_QUERIES.items():
        queries[category] = []
        for template in templates:
            query = template.replace("{company}", company_name)
            if "{competitor}" in template and competitor_list:
                query = query.replace("{competitor}", competitor_list[0])
            queries[category].append({
                "query": query,
                "url": generate_google_search_url(query)
            })
    
    # 사이트별 쿼리
    site_queries = {}
    for site, template in SITE_SPECIFIC_QUERIES.items():
        query = template.replace("{company}", company_name)
        site_queries[site] = {
            "query": query,
            "url": generate_google_search_url(query)
        }
    
    # 직접 URL
    direct_urls = {
        "crunchbase": generate_crunchbase_url(company_name),
        "sec": generate_sec_search_url(company_name),
        "google_company": generate_google_search_url(f'"{company_name}" official website'),
    }
    
    return {
        "company": company_name,
        "category": category,
        "country": country,
        "competitors": competitor_list,
        "search_queries": queries,
        "site_specific": site_queries,
        "direct_urls": direct_urls,
    }


# ========================================
# 리서치 체크리스트 생성
# ========================================

def create_research_checklist(company_name: str) -> str:
    """
    리서치 체크리스트 Markdown 생성
    """
    checklist = f"""# ✅ {company_name} 리서치 체크리스트

## Phase 1: 기본 정보 수집 (10분)

- [ ] Crunchbase 프로필 확인
- [ ] 공식 웹사이트 방문
- [ ] 최신 뉴스 확인 (Google News)
- [ ] 상장 여부 확인 (SEC 검색)

## Phase 2: 재무 정보 (20-30분)

### 상장사인 경우:
- [ ] SEC EDGAR에서 최신 10-K 다운로드
- [ ] Revenue (3년) 추출
- [ ] Operating Profit (3년) 추출
- [ ] Key Metrics 확인 (MD&A 섹션)
- [ ] 소스: 10-K, Page ___

### 비상장인 경우:
- [ ] TechCrunch 펀딩 기사 검색
- [ ] Bloomberg/WSJ 분석 기사
- [ ] 공식 발표에서 언급된 지표 확인
- [ ] The Information 기사 (유료 시)

## Phase 3: 운영 지표 (15-20분)

- [ ] Users/MAU 공식 발표 확인
- [ ] GMV/ARR 발표 확인
- [ ] 컨퍼런스 발표 자료 검색
- [ ] CEO 인터뷰에서 언급된 지표

## Phase 4: 비즈니스 분석 (20-30분)

- [ ] Problem/Solution 정리
- [ ] Revenue Model 확인
- [ ] Competitive Advantage 분석 (3-5개)
- [ ] Critical Success Factors 도출 (3-5개)

## Phase 5: 검증 & 문서화 (10분)

- [ ] 모든 소스 URL 기록
- [ ] 신뢰도 평가 (⭐⭐⭐⭐⭐)
- [ ] Quality Grade 부여 (A/B/C/D)
- [ ] JSON 업데이트 준비

---

**예상 총 소요시간:** 75-110분
**목표 Quality Grade:** A 또는 B
"""
    return checklist


# ========================================
# Main - 리서치 가이드 출력
# ========================================

def main():
    """
    파일럿 10개 기업의 리서치 가이드 생성
    """
    import os
    
    # 파일 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # 파일럿 데이터 로드
    pilot_file = os.path.join(project_dir, 'pilot_companies.json')
    with open(pilot_file, 'r', encoding='utf-8') as f:
        pilot = json.load(f)
    
    companies = pilot['pilot_companies']
    
    print("="*80)
    print("🔍 리서치 헬퍼 - 검색 쿼리 자동 생성")
    print("="*80)
    print()
    
    # 리서치 가이드 폴더 생성
    research_dir = os.path.join(project_dir, 'research')
    os.makedirs(research_dir, exist_ok=True)
    
    print(f"📁 리서치 가이드 폴더: {research_dir}")
    print()
    
    # 각 기업별 가이드 생성
    for i, company in enumerate(companies, 1):
        company_name = company['company']
        
        print(f"{i}. {company_name} 리서치 가이드 생성 중...")
        
        # 리서치 가이드 생성
        guide = generate_research_guide(company)
        
        # 체크리스트 생성
        checklist = create_research_checklist(company_name)
        
        # 파일명 안전하게 만들기
        safe_name = company_name.replace('/', '_').replace(' ', '_')
        
        # JSON 가이드 저장
        guide_file = os.path.join(research_dir, f"{i:02d}_{safe_name}_guide.json")
        with open(guide_file, 'w', encoding='utf-8') as f:
            json.dump(guide, f, ensure_ascii=False, indent=2)
        
        # 체크리스트 저장
        checklist_file = os.path.join(research_dir, f"{i:02d}_{safe_name}_checklist.md")
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print(f"   ✅ {guide_file}")
        print(f"   ✅ {checklist_file}")
    
    print()
    print("="*80)
    print("✅ 리서치 가이드 생성 완료!")
    print("="*80)
    print()
    
    # 첫 번째 기업 샘플 출력
    print("📝 샘플: Stripe 리서치 가이드")
    print("="*80)
    print()
    
    stripe_guide = generate_research_guide(companies[0])
    
    print("🔍 Revenue & Financial 검색 쿼리:")
    for q in stripe_guide['search_queries']['revenue_financial'][:2]:
        print(f"   - {q['query']}")
    
    print()
    print("📊 Operational Metrics 검색 쿼리:")
    for q in stripe_guide['search_queries']['operational_metrics'][:2]:
        print(f"   - {q['query']}")
    
    print()
    print("🌐 직접 접근 URL:")
    for name, url in stripe_guide['direct_urls'].items():
        print(f"   - {name}: {url}")
    
    print()
    print("="*80)
    print("💡 사용 방법:")
    print("="*80)
    print()
    print("1. research/ 폴더의 가이드 파일 열기")
    print("2. JSON 파일에서 검색 쿼리 복사")
    print("3. URL 클릭하여 자동으로 검색 실행")
    print("4. 체크리스트 따라가며 정보 수집")
    print("5. 리서치 템플릿에 정보 입력")


if __name__ == "__main__":
    main()

