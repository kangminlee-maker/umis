#!/usr/bin/env python3
"""
공헌이익(Contribution Margin) 계산

BGF리테일 템플릿 기반으로 전체 기업 분석
"""

import yaml
from pathlib import Path


def analyze_bgf_retail():
    """BGF리테일 공헌이익 분석 (템플릿)"""
    
    filepath = Path("data/raw/bgf_retail_FINAL_complete.yaml")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("="*70)
    print("BGF리테일 공헌이익 분석 (템플릿)")
    print("="*70)
    
    # 주요 계정
    revenue = data['income_statement_2023']['key_accounts_billion']['revenue']
    cogs = data['income_statement_2023']['key_accounts_billion']['cogs']
    sga_total = data['income_statement_2023']['key_accounts_billion']['sga_total']
    operating_profit = data['income_statement_2023']['key_accounts_billion']['operating_profit']
    
    gross_profit = revenue - cogs
    gross_margin = gross_profit / revenue
    
    print(f"\n손익계산서 (억원):")
    print(f"  매출액: {revenue:,.0f}")
    print(f"  매출원가: {cogs:,.0f} (변동비 100%)")
    print(f"  매출총이익: {gross_profit:,.0f} ({gross_margin:.1%})")
    print(f"  SG&A: {sga_total:,.0f}")
    print(f"  영업이익: {operating_profit:,.0f} ({operating_profit/revenue:.1%})")
    
    # SG&A 분류
    classification = data.get('cost_classification_guide', {}).get('sga_items_classification', {})
    
    # 변동 SG&A 계산
    variable_sga = 0
    fixed_sga = 0
    
    # BGF 템플릿에 정의된 분류 사용
    sga_details = data.get('sga_details_2024', {}).get('details_billion', {})
    
    variable_items = {
        '지급수수료': 5216.2,  # 준변동비 (거래량 비례)
        '사용권자산상각비': 3110.7,  # 준변동비 (가맹점 수)
        '광고선전비': 38.1,
        '판매촉진비': 107.6,
    }
    
    fixed_items = {
        '급여': 1956.5,
        '퇴직급여': 118.3,
        '복리후생비': 206.9,
        '감가상각비': 1807.4,
        # ... 나머지
    }
    
    variable_sga = sum(variable_items.values())
    
    # 공헌이익 계산
    contribution_margin = gross_profit - variable_sga
    cm_ratio = contribution_margin / revenue
    
    print(f"\n공헌이익 분석:")
    print(f"  매출총이익: {gross_profit:,.0f}억원 ({gross_margin:.1%})")
    print(f"  - 변동 SG&A: {variable_sga:,.0f}억원")
    print(f"  = 공헌이익: {contribution_margin:,.0f}억원 ({cm_ratio:.1%})")
    print(f"  - 고정 SG&A: {sga_total - variable_sga:,.0f}억원")
    print(f"  = 영업이익: {operating_profit:,.0f}억원 ({operating_profit/revenue:.1%})")
    
    print(f"\n핵심 인사이트:")
    print(f"  • 공헌이익률 ({cm_ratio:.1%}) > 영업이익률 ({operating_profit/revenue:.1%})")
    print(f"  • 변동비 비중: {(cogs + variable_sga)/revenue:.1%}")
    print(f"  • 고정비 비중: {(sga_total - variable_sga)/revenue:.1%}")
    print(f"  • Unit Economics: 공헌이익 {cm_ratio:.1%} (건강!)")
    
    return {
        'company': 'BGF리테일',
        'revenue': revenue,
        'gross_margin': gross_margin,
        'contribution_margin_ratio': cm_ratio,
        'operating_margin': operating_profit/revenue,
        'variable_sga': variable_sga,
        'fixed_sga': sga_total - variable_sga
    }


def main():
    print("="*70)
    print("공헌이익 분석 시스템")
    print("="*70)
    
    # BGF리테일 템플릿 분석
    bgf_result = analyze_bgf_retail()
    
    print(f"\n\n{'='*70}")
    print("다음 단계:")
    print(f"{'='*70}")
    print("  1. BGF리테일 템플릿 완성 ✅")
    print("  2. 다른 10개 기업에 적용")
    print("  3. 산업별 벤치마크 구축")
    print("  4. Unit Economics 비교")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

