#!/usr/bin/env python3
"""
SEC API 일괄 수집 - 유니콘 상장사 10-20개

작성일: 2025-11-04
목적: 유니콘 리스트 중 상장사를 찾아 SEC API로 일괄 수집
"""

import json
import time
import requests
from collections import defaultdict

HEADERS = {'User-Agent': 'UMIS Research kangmin@umis.com'}
BASE_URL = "https://data.sec.gov"


# ========================================
# 상장 유니콘 CIK 매핑 (직접 확인한 것들)
# ========================================

UNICORN_PUBLIC_CIK = {
    # 파일럿
    "Rivian": "0001874178",
    "Instacart": "0001939542",  # Maplebear Inc
    
    # 추가 상장사 (CIK 검증 완료)
    "Coinbase": "0001679788",
    "DoorDash": "0001792789",
    "Affirm": "0001820953",  # ✅ 수정됨! (이전: 1783879)
    "Robinhood": "0001783879",  # ✅ 정확함
    "Snowflake": "0001640147",
    "Unity": "0001810806",
    "Roblox": "0001315098",
    "Palantir": "0001321655",
    "Asana": "0001477720",
    "C3.ai": "0001699150",
    "Coupang": "0001834584",
    
    # CIK 확인 필요
    "Grab": None,  # GRAB
    "GitLab": None,  # GTLB  
    "HashiCorp": None,  # HCP
    "UiPath": None,  # PATH
    "monday.com": None,  # MNDY
    "SentinelOne": None,  # S
    "Sea Limited": None,  # SE
}


def get_annual_metrics(cik: str, company_name: str) -> dict:
    """
    연도별 재무 지표 추출 (개선된 버전)
    """
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        
        facts = response.json()
        us_gaap = facts.get('facts', {}).get('us-gaap', {})
        
    except Exception as e:
        print(f"  ❌ API 오류: {e}")
        return None
    
    # 연도별 데이터 저장
    by_year = defaultdict(dict)
    
    # 추출할 필드들
    metrics = {
        'RevenueFromContractWithCustomerExcludingAssessedTax': 'revenue',
        'Revenues': 'revenue',  # 대체 필드
        'GrossProfit': 'gross_profit',
        'OperatingIncomeLoss': 'operating_income',
        'NetIncomeLoss': 'net_income',
        'CostOfRevenue': 'cost_of_revenue',
        'CashAndCashEquivalentsAtCarryingValue': 'cash',
    }
    
    for field, metric_name in metrics.items():
        if field not in us_gaap:
            continue
        
        # Revenue는 첫 번째 필드만
        if metric_name == 'revenue' and any('revenue' in by_year[y] for y in by_year):
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
    for year, d in by_year.items():
        rev = d.get('revenue', 0)
        if rev > 0:
            if 'gross_profit' in d:
                d['gross_margin_pct'] = (d['gross_profit'] / rev) * 100
            if 'operating_income' in d:
                d['operating_margin_pct'] = (d['operating_income'] / rev) * 100
            if 'net_income' in d:
                d['net_margin_pct'] = (d['net_income'] / rev) * 100
    
    return by_year


def main():
    print("="*80)
    print("🏛️ SEC API 일괄 수집 - 상장 유니콘")
    print("="*80)
    print()
    
    # CIK가 있는 회사만 처리
    to_process = {k: v for k, v in UNICORN_PUBLIC_CIK.items() if v is not None}
    
    print(f"📊 처리 대상: {len(to_process)}개 상장사")
    print()
    
    for name in to_process.keys():
        print(f"  - {name}")
    
    print()
    print("="*80)
    
    results = {}
    success_count = 0
    
    for company_name, cik in to_process.items():
        print(f"\n📊 {company_name} (CIK: {cik})")
        print("-"*80)
        
        # 재무 데이터 수집
        yearly_data = get_annual_metrics(cik, company_name)
        
        if not yearly_data:
            print("  ❌ 데이터 수집 실패")
            continue
        
        # 최근 3년
        years = sorted(yearly_data.keys(), reverse=True)[:3]
        
        if not years:
            print("  ❌ 데이터 없음")
            continue
        
        print(f"  ✅ {len(years)}개년 데이터 수집")
        
        # 간단히 출력
        for year in years:
            d = yearly_data[year]
            if 'revenue' in d:
                rev = d['revenue'] / 1e6
                print(f"    {year}: Revenue ${rev:>8,.0f}M", end='')
                
                if 'net_income' in d:
                    ni = d['net_income'] / 1e6
                    margin = d.get('net_margin_pct', 0)
                    print(f" | Net ${ni:>8,.0f}M ({margin:>6.1f}%)")
                else:
                    print()
        
        # Performance Metrics 형식으로 변환
        result = {
            "company": company_name,
            "cik": cik,
            "data_source": "SEC EDGAR API",
            "retrieved_at": time.strftime("%Y-%m-%d"),
            "performance_metrics": {
                "financial": {
                    "revenue": {},
                    "operating_profit": {},
                    "gross_profit": {},
                    "net_income": {},
                    "gross_margin": yearly_data[years[0]].get('gross_margin_pct'),
                    "operating_margin": yearly_data[years[0]].get('operating_margin_pct'),
                    "net_margin": yearly_data[years[0]].get('net_margin_pct'),
                    "cash_and_equivalents": yearly_data[years[0]].get('cash', 0) / 1e6 if 'cash' in yearly_data[years[0]] else None,
                }
            }
        }
        
        # 연도별 데이터 입력
        for i, year in enumerate(years, 1):
            key = f"year_{i}"
            d = yearly_data[year]
            
            for metric in ['revenue', 'gross_profit', 'operating_income', 'net_income']:
                if metric in d:
                    field_name = metric if metric != 'operating_income' else 'operating_profit'
                    result["performance_metrics"]["financial"][field_name][key] = {
                        "year": year,
                        "amount_usd_million": round(d[metric] / 1e6, 1),
                        "source": f"SEC 10-K {year}"
                    }
        
        results[company_name] = result
        success_count += 1
        
        # 저장
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        output_file = os.path.join(project_dir, 'research', f"SEC_{company_name}_final.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Rate limit
        time.sleep(0.2)
    
    print()
    print("="*80)
    print(f"✅ 수집 완료: {success_count}/{len(to_process)}개")
    print("="*80)
    print()
    
    # 요약 저장
    summary = {
        "collection_date": time.strftime("%Y-%m-%d"),
        "total_companies": len(to_process),
        "success_count": success_count,
        "companies": list(results.keys()),
        "failed": [k for k in to_process.keys() if k not in results]
    }
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    summary_file = os.path.join(project_dir, 'research', 'SEC_batch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("📊 요약:")
    print(f"  성공: {success_count}개")
    print(f"  실패: {len(summary['failed'])}개")
    if summary['failed']:
        print(f"  실패 목록: {', '.join(summary['failed'])}")
    
    print()
    print("💾 결과 저장:")
    print(f"  research/SEC_{{Company}}_final.json (각 기업별)")
    print(f"  research/SEC_batch_summary.json (요약)")


if __name__ == "__main__":
    main()

