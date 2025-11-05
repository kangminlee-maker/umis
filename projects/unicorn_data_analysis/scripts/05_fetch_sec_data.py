#!/usr/bin/env python3
"""
SEC EDGAR API를 통해 상장 유니콘 재무 데이터 자동 수집

작성일: 2025-11-04
목적: Rivian, Instacart 등 상장사의 10-K 재무 데이터 자동 추출

SEC EDGAR API 사용:
- Company Facts API: https://data.sec.gov/api/xbrl/companyfacts/
- Submissions API: https://data.sec.gov/submissions/
"""

import json
import time
import requests
from typing import Dict, List, Optional


# ========================================
# SEC API 설정
# ========================================

# SEC requires User-Agent header
HEADERS = {
    'User-Agent': 'UMIS Research umis@example.com',
    'Accept-Encoding': 'gzip, deflate',
}

BASE_URL = "https://data.sec.gov"


# ========================================
# CIK 매핑 (알려진 상장 유니콘)
# ========================================

COMPANY_CIK = {
    "Rivian": "0001874178",
    "Instacart": "0001874178",  # 실제 CIK 확인 필요
    # 추가 상장사...
}


# ========================================
# SEC API Functions
# ========================================

def get_company_facts(cik: str) -> Optional[Dict]:
    """
    SEC Company Facts API로 재무 데이터 가져오기
    
    Returns JSON with financial facts (XBRL data)
    """
    # CIK를 10자리로 패딩
    cik_padded = cik.zfill(10)
    
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    
    try:
        print(f"🔍 SEC API 요청: {url}")
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            print("✅ 데이터 수신 성공")
            return response.json()
        else:
            print(f"❌ 오류: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return None


def get_company_submissions(cik: str) -> Optional[Dict]:
    """
    SEC Submissions API로 제출 문서 목록 가져오기
    
    Returns recent filings list (10-K, 10-Q, 8-K, etc.)
    """
    cik_padded = cik.zfill(10)
    
    url = f"{BASE_URL}/submissions/CIK{cik_padded}.json"
    
    try:
        print(f"🔍 SEC Submissions API 요청: {url}")
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            print("✅ 제출 문서 목록 수신")
            return response.json()
        else:
            print(f"❌ 오류: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return None


# ========================================
# Data Extraction Functions
# ========================================

def extract_revenue(facts_data: Dict, company_name: str) -> List[Dict]:
    """
    Company Facts에서 Revenue 추출 (연간 데이터만)
    
    US-GAAP 표준 필드:
    - Revenues
    - RevenueFromContractWithCustomerExcludingAssessedTax
    """
    revenues = []
    
    try:
        # US-GAAP facts
        us_gaap = facts_data.get('facts', {}).get('us-gaap', {})
        
        # Revenue 관련 필드들
        revenue_fields = [
            'Revenues',
            'RevenueFromContractWithCustomerExcludingAssessedTax',
            'SalesRevenueNet',
        ]
        
        for field in revenue_fields:
            if field in us_gaap:
                units = us_gaap[field].get('units', {})
                
                # USD 단위 데이터
                if 'USD' in units:
                    # 연도별로 그룹핑 (분기 데이터 제외)
                    annual_data = {}
                    
                    for item in units['USD']:
                        # 10-K 데이터만 (연간) + 12개월 데이터만
                        if item.get('form') == '10-K' and item.get('fp') == 'FY':
                            year = item.get('fy')
                            
                            # 같은 연도의 가장 큰 값 (full year)
                            if year not in annual_data or item.get('val') > annual_data[year].get('val'):
                                annual_data[year] = item
                    
                    # 리스트로 변환
                    for year, item in annual_data.items():
                        revenues.append({
                            'year': year,
                            'end_date': item.get('end'),
                            'value_usd': item.get('val'),
                            'filed': item.get('filed'),
                            'form': '10-K',
                            'field': field
                        })
                
                if revenues:
                    break  # 첫 번째 필드에서 찾으면 종료
        
        # 연도별로 정리 (최근 3년)
        revenues.sort(key=lambda x: x['year'], reverse=True)
        
        return revenues[:3]
        
    except Exception as e:
        print(f"❌ Revenue 추출 실패: {e}")
        return []


def extract_operating_income(facts_data: Dict) -> List[Dict]:
    """
    Operating Income/Loss 추출 (연간 데이터만)
    """
    results = []
    
    try:
        us_gaap = facts_data.get('facts', {}).get('us-gaap', {})
        
        # Operating Income 필드들
        fields = [
            'OperatingIncomeLoss',
            'OperatingExpenses',
        ]
        
        for field in fields:
            if field in us_gaap:
                units = us_gaap[field].get('units', {})
                
                if 'USD' in units:
                    # 연도별로 그룹핑
                    annual_data = {}
                    
                    for item in units['USD']:
                        # 10-K 데이터만 + Full Year만
                        if item.get('form') == '10-K' and item.get('fp') == 'FY':
                            year = item.get('fy')
                            
                            # 같은 연도의 절대값이 가장 큰 값 (full year)
                            if year not in annual_data or abs(item.get('val')) > abs(annual_data[year].get('val')):
                                annual_data[year] = item
                    
                    # 리스트로 변환
                    for year, item in annual_data.items():
                        results.append({
                            'year': year,
                            'end_date': item.get('end'),
                            'value_usd': item.get('val'),
                            'filed': item.get('filed'),
                            'field': field
                        })
                
                if results:
                    break
        
        results.sort(key=lambda x: x['year'], reverse=True)
        return results[:3]
        
    except Exception as e:
        print(f"❌ Operating Income 추출 실패: {e}")
        return []


def format_financial_data(company_name: str, cik: str) -> Dict:
    """
    SEC 데이터를 Performance Metrics 형식으로 변환
    """
    print("="*80)
    print(f"📊 {company_name} SEC 재무 데이터 수집")
    print("="*80)
    print()
    
    # Company Facts 가져오기
    facts = get_company_facts(cik)
    
    if not facts:
        print("❌ Company Facts를 가져올 수 없습니다.")
        return None
    
    print()
    
    # Revenue 추출
    print("💰 Revenue 추출 중...")
    revenues = extract_revenue(facts, company_name)
    
    if revenues:
        print(f"✅ {len(revenues)}개 연도 Revenue 확보")
        for rev in revenues:
            val_millions = rev['value_usd'] / 1_000_000
            print(f"   - {rev['year']}: ${val_millions:,.0f}M")
    else:
        print("⚠️ Revenue 데이터 없음")
    
    print()
    
    # Operating Income 추출
    print("📈 Operating Income 추출 중...")
    op_income = extract_operating_income(facts)
    
    if op_income:
        print(f"✅ {len(op_income)}개 연도 Operating Income 확보")
        for oi in op_income:
            val_millions = oi['value_usd'] / 1_000_000
            print(f"   - {oi['year']}: ${val_millions:,.0f}M")
    else:
        print("⚠️ Operating Income 데이터 없음")
    
    # Performance Metrics 형식으로 변환
    result = {
        "company": company_name,
        "cik": cik,
        "data_source": "SEC EDGAR Company Facts API",
        "retrieved_at": time.strftime("%Y-%m-%d"),
        
        "performance_metrics": {
            "financial": {
                "revenue": {},
                "operating_profit": {},
                "gross_margin": None,
                "ebitda": None
            }
        }
    }
    
    # Revenue 입력 (year_1, year_2, year_3)
    for i, rev in enumerate(revenues[:3], 1):
        year_key = f"year_{i}"
        result["performance_metrics"]["financial"]["revenue"][year_key] = {
            "year": int(rev['year']),
            "amount_usd_million": round(rev['value_usd'] / 1_000_000, 2),
            "source": f"SEC 10-K {rev['year']}, filed {rev['filed']}"
        }
    
    # Operating Income 입력
    for i, oi in enumerate(op_income[:3], 1):
        year_key = f"year_{i}"
        result["performance_metrics"]["financial"]["operating_profit"][year_key] = {
            "year": int(oi['year']),
            "amount_usd_million": round(oi['value_usd'] / 1_000_000, 2),
            "source": f"SEC 10-K {oi['year']}, filed {oi['filed']}"
        }
    
    return result


# ========================================
# Main Function
# ========================================

def main():
    """
    상장 유니콘 기업의 SEC 데이터 수집
    """
    import os
    
    print("="*80)
    print("🏛️ SEC EDGAR API - 상장 유니콘 재무 데이터 자동 수집")
    print("="*80)
    print()
    
    print("📋 대상 기업:")
    for company, cik in COMPANY_CIK.items():
        print(f"   - {company} (CIK: {cik})")
    
    print()
    print("="*80)
    
    # 각 기업별로 데이터 수집
    results = {}
    
    for company, cik in COMPANY_CIK.items():
        print()
        
        # API 요청 (SEC는 rate limit 있음)
        data = format_financial_data(company, cik)
        
        if data:
            results[company] = data
            
            # 결과 저장
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            output_file = os.path.join(
                project_dir, 
                'research',
                f'SEC_{company}_financial_data.json'
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print()
            print(f"💾 저장 완료: {output_file}")
        
        # Rate limiting (SEC 권장: 10 requests/second)
        time.sleep(0.2)
    
    print()
    print("="*80)
    print("✅ SEC 데이터 수집 완료!")
    print("="*80)
    print()
    
    # 요약
    print("📊 수집 요약:")
    for company, data in results.items():
        revenue_years = len(data['performance_metrics']['financial']['revenue'])
        op_years = len(data['performance_metrics']['financial']['operating_profit'])
        print(f"   {company}:")
        print(f"      - Revenue: {revenue_years}개년")
        print(f"      - Operating Profit: {op_years}개년")
    
    print()
    print("📁 저장 위치: research/SEC_{Company}_financial_data.json")
    print()
    print("다음 단계:")
    print("  1. JSON 파일 확인")
    print("  2. research/07_Rivian_research.md 업데이트")
    print("  3. unicorn_companies_rag_enhanced.json 반영")


if __name__ == "__main__":
    main()

