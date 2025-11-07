#!/usr/bin/env python3
"""
SEC API 단순화 버전 - 정확한 연도별 데이터

핵심 개선:
- end 날짜로 연도 추출 (fy 대신)
- 중복 데이터 제거
- 간단하고 명확한 로직
"""

import requests
import json
import time
from collections import defaultdict

HEADERS = {'User-Agent': 'UMIS Research kangmin@umis.com'}
BASE_URL = "https://data.sec.gov"

# 상장 유니콘 CIK
COMPANIES = {
    "Rivian": "0001874178",
    "Instacart": "0001939542",
}


def get_annual_metrics(cik: str, company_name: str) -> dict:
    """
    연도별 재무 지표 추출 (end 날짜 기준)
    """
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None
        
        facts = response.json()
        us_gaap = facts.get('facts', {}).get('us-gaap', {})
        
    except:
        return None
    
    # 연도별 데이터 저장
    by_year = defaultdict(dict)
    
    # 추출할 필드들
    metrics = {
        'RevenueFromContractWithCustomerExcludingAssessedTax': 'revenue',
        'GrossProfit': 'gross_profit',
        'OperatingIncomeLoss': 'operating_income',
        'NetIncomeLoss': 'net_income',
        'CostOfRevenue': 'cost_of_revenue',
        'CashAndCashEquivalentsAtCarryingValue': 'cash',
    }
    
    for field, metric_name in metrics.items():
        if field not in us_gaap:
            continue
        
        usd_data = us_gaap[field].get('units', {}).get('USD', [])
        
        for item in usd_data:
            # 10-K + FY만
            if item.get('form') != '10-K' or item.get('fp') != 'FY':
                continue
            
            # end 날짜에서 연도 추출
            end_date = item.get('end', '')
            if not end_date:
                continue
            
            year = int(end_date[:4])
            filed = item.get('filed', '')
            value = item.get('val', 0)
            
            # 같은 연도는 가장 최근 filing 사용
            if metric_name not in by_year[year] or filed > by_year[year].get(f'{metric_name}_filed', ''):
                by_year[year][metric_name] = value
                by_year[year][f'{metric_name}_filed'] = filed
                by_year[year]['end_date'] = end_date
    
    # Margin 계산
    for year, data in by_year.items():
        rev = data.get('revenue', 0)
        if rev > 0:
            if 'gross_profit' in data:
                data['gross_margin_pct'] = (data['gross_profit'] / rev) * 100
            if 'operating_income' in data:
                data['operating_margin_pct'] = (data['operating_income'] / rev) * 100
            if 'net_income' in data:
                data['net_margin_pct'] = (data['net_income'] / rev) * 100
    
    return by_year


def main():
    print("="*80)
    print("🏛️ SEC API - 단순화 & 정확한 버전")
    print("="*80)
    print()
    
    all_results = {}
    
    for company, cik in COMPANIES.items():
        print(f"\n📊 {company} (CIK: {cik})")
        print("-"*80)
        
        data = get_annual_metrics(cik, company)
        
        if not data:
            print(f"❌ 데이터 없음")
            continue
        
        # 최근 3년
        years = sorted(data.keys(), reverse=True)[:3]
        
        print()
        for year in years:
            d = data[year]
            print(f"📅 {year} (End: {d.get('end_date', 'N/A')})")
            
            if 'revenue' in d:
                print(f"   Revenue:          ${d['revenue']/1e6:>9,.1f}M")
            if 'gross_profit' in d:
                margin = d.get('gross_margin_pct', 0)
                print(f"   Gross Profit:     ${d['gross_profit']/1e6:>9,.1f}M  ({margin:>6.1f}%)")
            if 'operating_income' in d:
                margin = d.get('operating_margin_pct', 0)
                print(f"   Operating Income: ${d['operating_income']/1e6:>9,.1f}M  ({margin:>6.1f}%)")
            if 'net_income' in d:
                margin = d.get('net_margin_pct', 0)
                print(f"   Net Income:       ${d['net_income']/1e6:>9,.1f}M  ({margin:>6.1f}%)")
            if 'cash' in d:
                print(f"   Cash:             ${d['cash']/1e6:>9,.1f}M")
            print()
        
        # Performance Metrics 형식으로 변환
        result = {
            "company": company,
            "cik": cik,
            "data_source": "SEC EDGAR API (Simplified & Accurate)",
            "retrieved_at": time.strftime("%Y-%m-%d"),
            "performance_metrics": {
                "financial": {
                    "revenue": {},
                    "gross_profit": {},
                    "operating_profit": {},
                    "net_income": {},
                    "gross_margin": data[years[0]].get('gross_margin_pct'),
                    "operating_margin": data[years[0]].get('operating_margin_pct'),
                    "net_margin": data[years[0]].get('net_margin_pct'),
                    "cash_and_equivalents": data[years[0]].get('cash', 0) / 1e6 if 'cash' in data[years[0]] else None,
                }
            }
        }
        
        # 연도별 데이터 입력
        for i, year in enumerate(years, 1):
            key = f"year_{i}"
            d = data[year]
            
            if 'revenue' in d:
                result["performance_metrics"]["financial"]["revenue"][key] = {
                    "year": year,
                    "amount_usd_million": round(d['revenue'] / 1e6, 1),
                    "source": f"SEC 10-K {year}, end {d.get('end_date')}"
                }
            
            if 'gross_profit' in d:
                result["performance_metrics"]["financial"]["gross_profit"][key] = {
                    "year": year,
                    "amount_usd_million": round(d['gross_profit'] / 1e6, 1),
                    "source": f"SEC 10-K {year}"
                }
            
            if 'operating_income' in d:
                result["performance_metrics"]["financial"]["operating_profit"][key] = {
                    "year": year,
                    "amount_usd_million": round(d['operating_income'] / 1e6, 1),
                    "source": f"SEC 10-K {year}"
                }
            
            if 'net_income' in d:
                result["performance_metrics"]["financial"]["net_income"][key] = {
                    "year": year,
                    "amount_usd_million": round(d['net_income'] / 1e6, 1),
                    "source": f"SEC 10-K {year}"
                }
        
        all_results[company] = result
        
        # 저장
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        output_file = os.path.join(project_dir, 'research', f'SEC_{company}_final.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 저장: SEC_{company}_final.json")
        
        # Rate limit
        time.sleep(0.5)
    
    print()
    print("="*80)
    print("✅ 모든 작업 완료!")
    print("="*80)


if __name__ == "__main__":
    main()



