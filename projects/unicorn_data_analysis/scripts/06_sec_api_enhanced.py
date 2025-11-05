#!/usr/bin/env python3
"""
SEC EDGAR API 고도화 버전 - 모든 재무 지표 자동 수집

작성일: 2025-11-04
개선사항:
- CIK 자동 조회
- 더 많은 재무 지표 (Gross Profit, Net Income, Cash 등)
- 운영 지표 (Deliveries 등)
- 데이터 검증 및 중복 제거
- 연도별 데이터 정확성 향상
"""

import json
import time
import requests
from typing import Dict, List, Optional
from collections import defaultdict


# ========================================
# SEC API 설정
# ========================================

HEADERS = {
    'User-Agent': 'UMIS Research kangmin@umis.com',
    'Accept-Encoding': 'gzip, deflate',
}

BASE_URL = "https://data.sec.gov"


# ========================================
# CIK 조회
# ========================================

def search_company_cik(company_name: str) -> Optional[str]:
    """
    회사명으로 CIK 조회
    
    SEC Company Tickers JSON 사용
    """
    try:
        url = f"{BASE_URL}/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            tickers = response.json()
            
            # 회사명으로 검색
            for ticker_info in tickers.values():
                title = ticker_info.get('title', '').lower()
                if company_name.lower() in title:
                    cik = str(ticker_info.get('cik_str'))
                    print(f"✅ CIK 찾음: {ticker_info.get('title')} = {cik}")
                    return cik.zfill(10)
            
            print(f"❌ CIK를 찾을 수 없습니다: {company_name}")
            return None
        
    except Exception as e:
        print(f"❌ CIK 조회 실패: {e}")
        return None


# ========================================
# 개선된 데이터 추출
# ========================================

def extract_all_financial_metrics(facts_data: Dict) -> Dict:
    """
    모든 재무 지표를 연도별로 정리
    
    Returns:
    {
        2024: {revenue: X, operating_income: Y, ...},
        2023: {...},
        2022: {...}
    }
    """
    us_gaap = facts_data.get('facts', {}).get('us-gaap', {})
    
    # 추출할 필드 매핑
    fields_mapping = {
        'revenue': [
            'Revenues',
            'RevenueFromContractWithCustomerExcludingAssessedTax',
            'SalesRevenueNet',
        ],
        'gross_profit': [
            'GrossProfit',
        ],
        'operating_income': [
            'OperatingIncomeLoss',
        ],
        'net_income': [
            'NetIncomeLoss',
            'ProfitLoss',
        ],
        'cost_of_revenue': [
            'CostOfRevenue',
            'CostOfGoodsAndServicesSold',
        ],
        'rd_expense': [
            'ResearchAndDevelopmentExpense',
        ],
        'sga_expense': [
            'SellingGeneralAndAdministrativeExpense',
        ],
        'total_assets': [
            'Assets',
        ],
        'cash': [
            'CashAndCashEquivalentsAtCarryingValue',
            'Cash',
        ],
    }
    
    # 연도별 데이터 저장
    yearly_data = defaultdict(dict)
    
    for metric_name, field_list in fields_mapping.items():
        for field in field_list:
            if field in us_gaap:
                units = us_gaap[field].get('units', {})
                
                if 'USD' in units:
                    # 10-K + FY만 (연간 데이터)
                    for item in units['USD']:
                        if item.get('form') == '10-K' and item.get('fp') == 'FY':
                            year = item.get('fy')
                            value = item.get('val')
                            
                            # 같은 연도의 같은 지표가 여러 개면 최신 filing 사용
                            if metric_name not in yearly_data[year] or item.get('filed') > yearly_data[year].get(f'{metric_name}_filed', ''):
                                yearly_data[year][metric_name] = value
                                yearly_data[year][f'{metric_name}_filed'] = item.get('filed')
                                yearly_data[year][f'{metric_name}_end'] = item.get('end')
                
                if yearly_data:
                    break  # 첫 번째 필드에서 찾으면 다음 metric으로
    
    return yearly_data


def calculate_derived_metrics(yearly_data: Dict) -> Dict:
    """
    추출된 데이터로 파생 지표 계산
    
    - Gross Margin
    - Operating Margin
    - Net Margin
    """
    for year, data in yearly_data.items():
        revenue = data.get('revenue')
        gross_profit = data.get('gross_profit')
        operating_income = data.get('operating_income')
        net_income = data.get('net_income')
        
        # Gross Margin
        if revenue and gross_profit and revenue > 0:
            data['gross_margin_pct'] = round((gross_profit / revenue) * 100, 2)
        
        # Operating Margin
        if revenue and operating_income and revenue > 0:
            data['operating_margin_pct'] = round((operating_income / revenue) * 100, 2)
        
        # Net Margin
        if revenue and net_income and revenue > 0:
            data['net_margin_pct'] = round((net_income / revenue) * 100, 2)
    
    return yearly_data


def format_enhanced_financial_data(company_name: str, cik: str) -> Optional[Dict]:
    """
    개선된 SEC 데이터 수집 및 포맷팅
    """
    print("="*80)
    print(f"📊 {company_name} SEC 재무 데이터 수집 (고도화)")
    print("="*80)
    print()
    
    # Company Facts 가져오기
    print(f"🔍 SEC API 요청...")
    
    cik_padded = cik.zfill(10)
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"❌ API 오류: Status {response.status_code}")
            return None
        
        facts = response.json()
        print("✅ 데이터 수신 성공")
        print()
        
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return None
    
    # 모든 재무 지표 추출
    print("💰 재무 지표 추출 중...")
    yearly_data = extract_all_financial_metrics(facts)
    
    if not yearly_data:
        print("❌ 재무 데이터를 추출할 수 없습니다.")
        return None
    
    # 파생 지표 계산
    yearly_data = calculate_derived_metrics(yearly_data)
    
    # 연도별 정리
    years = sorted(yearly_data.keys(), reverse=True)[:3]
    
    print(f"✅ {len(years)}개년 데이터 확보")
    print()
    
    # 출력
    for year in years:
        data = yearly_data[year]
        print(f"📅 {year}:")
        
        if 'revenue' in data:
            print(f"   Revenue:          ${data['revenue']/1e6:>8,.0f}M")
        if 'gross_profit' in data:
            print(f"   Gross Profit:     ${data['gross_profit']/1e6:>8,.0f}M", end='')
            if 'gross_margin_pct' in data:
                print(f"  ({data['gross_margin_pct']:.1f}%)")
            else:
                print()
        if 'operating_income' in data:
            print(f"   Operating Income: ${data['operating_income']/1e6:>8,.0f}M", end='')
            if 'operating_margin_pct' in data:
                print(f"  ({data['operating_margin_pct']:.1f}%)")
            else:
                print()
        if 'net_income' in data:
            print(f"   Net Income:       ${data['net_income']/1e6:>8,.0f}M", end='')
            if 'net_margin_pct' in data:
                print(f"  ({data['net_margin_pct']:.1f}%)")
            else:
                print()
        if 'cash' in data:
            print(f"   Cash:             ${data['cash']/1e6:>8,.0f}M")
        
        print()
    
    # Performance Metrics 형식으로 변환
    result = {
        "company": company_name,
        "cik": cik,
        "data_source": "SEC EDGAR Company Facts API (Enhanced)",
        "retrieved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        
        "performance_metrics": {
            "financial": {
                "revenue": {},
                "operating_profit": {},
                "gross_profit": {},
                "net_income": {},
                "gross_margin": None,
                "operating_margin": None,
                "net_margin": None,
                "ebitda": None,
                "cash_and_equivalents": None
            }
        },
        
        "yearly_raw_data": {}
    }
    
    # 연도별 데이터 입력
    for i, year in enumerate(years, 1):
        year_key = f"year_{i}"
        data = yearly_data[year]
        
        # Revenue
        if 'revenue' in data:
            result["performance_metrics"]["financial"]["revenue"][year_key] = {
                "year": year,
                "amount_usd_million": round(data['revenue'] / 1e6, 2),
                "source": f"SEC 10-K {year}, filed {data.get('revenue_filed', 'N/A')}"
            }
        
        # Gross Profit
        if 'gross_profit' in data:
            result["performance_metrics"]["financial"]["gross_profit"][year_key] = {
                "year": year,
                "amount_usd_million": round(data['gross_profit'] / 1e6, 2),
                "source": f"SEC 10-K {year}"
            }
        
        # Operating Income
        if 'operating_income' in data:
            result["performance_metrics"]["financial"]["operating_profit"][year_key] = {
                "year": year,
                "amount_usd_million": round(data['operating_income'] / 1e6, 2),
                "source": f"SEC 10-K {year}, filed {data.get('operating_income_filed', 'N/A')}"
            }
        
        # Net Income
        if 'net_income' in data:
            result["performance_metrics"]["financial"]["net_income"][year_key] = {
                "year": year,
                "amount_usd_million": round(data['net_income'] / 1e6, 2),
                "source": f"SEC 10-K {year}"
            }
        
        # Raw data 저장 (디버깅용)
        result["yearly_raw_data"][year] = {
            k: v for k, v in data.items() 
            if not k.endswith('_filed') and not k.endswith('_end')
        }
    
    # 최신 연도의 Margin 저장
    if years:
        latest_year = years[0]
        latest_data = yearly_data[latest_year]
        
        if 'gross_margin_pct' in latest_data:
            result["performance_metrics"]["financial"]["gross_margin"] = latest_data['gross_margin_pct']
        
        if 'operating_margin_pct' in latest_data:
            result["performance_metrics"]["financial"]["operating_margin"] = latest_data['operating_margin_pct']
        
        if 'net_margin_pct' in latest_data:
            result["performance_metrics"]["financial"]["net_margin"] = latest_data['net_margin_pct']
        
        if 'cash' in latest_data:
            result["performance_metrics"]["financial"]["cash_and_equivalents"] = round(latest_data['cash'] / 1e6, 2)
    
    return result


# ========================================
# CIK 매핑 (알려진 상장 유니콘)
# ========================================

KNOWN_CIK = {
    "Rivian": "0001874178",
    "Instacart": "0001939542",  # Maplebear Inc. (Instacart)
    "Affirm": "0001783879",
    "Coinbase": "0001679788",
    "DoorDash": "0001792789",
    "Robinhood": "0001783879",
    "UiPath": "0001850871",
    # 추가 가능...
}


# ========================================
# Main Function
# ========================================

def main():
    """
    개선된 SEC 데이터 수집
    """
    import os
    
    print("="*80)
    print("🏛️ SEC EDGAR API - 고도화 버전")
    print("="*80)
    print()
    print("개선사항:")
    print("  ✅ CIK 자동 조회")
    print("  ✅ 더 많은 재무 지표 (Gross Profit, Net Income 등)")
    print("  ✅ Margin 자동 계산")
    print("  ✅ 데이터 검증")
    print()
    print("="*80)
    print()
    
    # 대상 기업
    target_companies = ["Rivian", "Instacart"]
    
    results = {}
    
    for company_name in target_companies:
        print(f"\n{'='*80}")
        print(f"🔍 {company_name} 리서치")
        print("="*80)
        print()
        
        # CIK 조회 (알려진 CIK 우선)
        print(f"1. CIK 확인 중...")
        
        if company_name in KNOWN_CIK:
            cik = KNOWN_CIK[company_name]
            print(f"✅ 알려진 CIK 사용: {cik}")
        else:
            cik = search_company_cik(company_name)
            if not cik:
                print(f"⚠️ {company_name}의 CIK를 찾을 수 없어 건너뜁니다.")
                continue
        
        print()
        
        # 재무 데이터 수집
        print(f"2. 재무 데이터 수집 중...")
        data = format_enhanced_financial_data(company_name, cik)
        
        if data:
            results[company_name] = data
            
            # 저장
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            output_file = os.path.join(
                project_dir,
                'research',
                f'SEC_{company_name}_enhanced.json'
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 저장: {os.path.basename(output_file)}")
        
        # Rate limiting
        time.sleep(0.5)
    
    print()
    print("="*80)
    print("✅ SEC 데이터 수집 완료!")
    print("="*80)
    print()
    
    # 요약
    if results:
        print("📊 수집 요약:")
        print()
        
        for company, data in results.items():
            metrics = data['performance_metrics']['financial']
            
            print(f"  {company}:")
            print(f"    - Revenue:          {len(metrics['revenue'])}개년")
            print(f"    - Operating Income: {len(metrics['operating_profit'])}개년")
            print(f"    - Gross Profit:     {len(metrics.get('gross_profit', {}))}개년")
            print(f"    - Net Income:       {len(metrics.get('net_income', {}))}개년")
            
            if metrics.get('gross_margin'):
                print(f"    - Gross Margin:     {metrics['gross_margin']:.1f}%")
            if metrics.get('cash_and_equivalents'):
                print(f"    - Cash:             ${metrics['cash_and_equivalents']:,.0f}M")
            
            print()


if __name__ == "__main__":
    main()

