#!/usr/bin/env python3
"""
국내 공연시장 주요 플레이어 매출 검증 스크립트
DART API를 활용한 실제 재무 데이터 확인
"""

import os
import sys
from pathlib import Path

# UMIS 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.dart_api import DARTClient
from dotenv import load_dotenv

# .env 로드
load_dotenv()

def main():
    """주요 엔터테인먼트 기업 재무 데이터 검증"""
    
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print("❌ DART_API_KEY가 설정되지 않았습니다.")
        return
    
    client = DARTClient(api_key)
    
    # 검증 대상 기업 (상장사만)
    companies = [
        "하이브",
        "SM",
        "YG엔터테인먼트",
        "JYP Ent.",
        "CJ ENM",
        "쇼박스",
        "NEW",  # 신시컴퍼니
    ]
    
    print("\n" + "="*80)
    print("📊 국내 엔터테인먼트 기업 실제 재무 데이터 검증 (DART 공시)")
    print("="*80 + "\n")
    
    results = []
    
    for company_name in companies:
        print(f"\n🔍 검색: {company_name}")
        print("-" * 60)
        
        try:
            # 1. 기업 코드 조회
            corp_code = client.get_corp_code(company_name)
            if not corp_code:
                print(f"  ❌ 기업 코드를 찾을 수 없습니다: {company_name}")
                continue
            
            print(f"  ✅ 기업 코드: {corp_code}")
            
            # 2. 2023년 재무제표 조회 (개별재무제표 우선)
            financials_2023 = client.get_financials(corp_code, 2023, fs_div='OFS')
            
            if not financials_2023:
                print(f"  ⚠️  2023년 개별재무제표 없음, 연결재무제표 시도...")
                financials_2023 = client.get_financials(corp_code, 2023, fs_div='CFS')
            
            # 3. 2022년 재무제표 조회 (성장률 계산용)
            financials_2022 = client.get_financials(corp_code, 2022, fs_div='OFS')
            if not financials_2022:
                financials_2022 = client.get_financials(corp_code, 2022, fs_div='CFS')
            
            # 4. 주요 재무 지표 추출
            if financials_2023:
                revenue_2023 = financials_2023.get('매출액', 0)
                revenue_2022 = financials_2022.get('매출액', 0) if financials_2022 else 0
                operating_income = financials_2023.get('영업이익', 0)
                
                # 억 단위로 변환
                revenue_2023_billion = revenue_2023 / 100_000_000
                revenue_2022_billion = revenue_2022 / 100_000_000
                operating_income_billion = operating_income / 100_000_000
                
                # 성장률 계산
                growth_rate = 0
                if revenue_2022 > 0:
                    growth_rate = ((revenue_2023 - revenue_2022) / revenue_2022) * 100
                
                # 영업이익률 계산
                operating_margin = 0
                if revenue_2023 > 0:
                    operating_margin = (operating_income / revenue_2023) * 100
                
                print(f"\n  📈 재무 데이터 (2023년):")
                print(f"     - 매출액: {revenue_2023_billion:,.0f}억원")
                if revenue_2022 > 0:
                    print(f"     - 전년 매출: {revenue_2022_billion:,.0f}억원")
                    print(f"     - YoY 성장률: {growth_rate:+.1f}%")
                print(f"     - 영업이익: {operating_income_billion:,.0f}억원")
                print(f"     - 영업이익률: {operating_margin:.1f}%")
                
                results.append({
                    'company': company_name,
                    'revenue_2023': revenue_2023_billion,
                    'revenue_2022': revenue_2022_billion,
                    'growth_rate': growth_rate,
                    'operating_income': operating_income_billion,
                    'operating_margin': operating_margin
                })
            else:
                print(f"  ❌ 재무제표를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"  ❌ 오류 발생: {str(e)}")
    
    # 5. 종합 결과 출력
    print("\n\n" + "="*80)
    print("📊 검증 결과 요약")
    print("="*80 + "\n")
    
    if results:
        print(f"{'기업명':<15} {'2023 매출':>12} {'2022 매출':>12} {'성장률':>10} {'영업이익':>12} {'이익률':>8}")
        print("-" * 80)
        
        total_revenue = 0
        for r in results:
            print(f"{r['company']:<15} {r['revenue_2023']:>10,.0f}억 {r['revenue_2022']:>10,.0f}억 "
                  f"{r['growth_rate']:>8.1f}% {r['operating_income']:>10,.0f}억 {r['operating_margin']:>6.1f}%")
            total_revenue += r['revenue_2023']
        
        print("-" * 80)
        print(f"{'합계':<15} {total_revenue:>10,.0f}억")
        
        print("\n⚠️  중요 사항:")
        print("  - 위 매출액은 '전체 매출'이며, '공연 부문만'의 매출이 아닙니다.")
        print("  - 음반, 매니지먼트, 콘텐츠, MD 등 모든 사업부문이 포함되어 있습니다.")
        print("  - 공연 부문 매출만 추출하려면 사업보고서 세그먼트 정보가 필요합니다.")
        print("  - 대부분 기업은 세그먼트별 매출을 상세 공개하지 않습니다.")
    else:
        print("  ❌ 검증 가능한 데이터가 없습니다.")
    
    print("\n")

if __name__ == "__main__":
    main()
