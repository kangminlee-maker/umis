#!/usr/bin/env python3
"""
변동비/고정비 자동 분류

전략:
1. 비즈니스 모델 파악 (Observer 역할)
2. SG&A 항목별 특성 분석
3. 산업 벤치마크 참고 (BGF리테일 템플릿)
4. 변동비/준변동비/고정비 분류
5. 공헌이익(CM) 계산
"""

import yaml
from pathlib import Path
from typing import Dict, List

# SG&A 항목 분류 규칙 (산업 공통)
CLASSIFICATION_RULES = {
    # 고신뢰 고정비 (거의 항상)
    'fixed_high_confidence': {
        '급여': '고정비',
        '퇴직급여': '고정비',
        '복리후생비': '고정비',
        '감가상각비': '고정비',
        '유형자산상각비': '고정비',
        '무형자산상각비': '고정비',
        '임차료': '고정비',
        '수도광열비': '고정비',
        '세금과공과': '고정비',
        '접대비': '고정비',
        '회의비': '고정비',
        '통신비': '고정비',
        '소모품비': '고정비',
        '교육훈련비': '고정비',
        '여비교통비': '고정비',
    },
    
    # 변동비 (매출 비례)
    'variable': {
        '광고선전비': '변동비',  # 고객 모집
        '판매촉진비': '변동비',  # 매출 증대
        '운반비': '변동비',  # 거래량 비례
        '포장비': '변동비',
        '지급수수료': '준변동비',  # 비즈니스 모델에 따라 다름!
    },
    
    # 비즈니스 모델별 특수 (Observer 판단 필요)
    'business_specific': {
        '프랜차이즈 본부': {
            '지급수수료': '변동비',  # 가맹점 거래 비례
            '사용권자산상각비': '준변동비',  # 가맹점 수 비례
        },
        '제조업': {
            '경상연구개발비': '고정비',
            '서비스비': '변동비',
        },
        '플랫폼': {
            '서버비': '변동비',  # 트래픽 비례
            '마케팅비': '변동비',  # 고객 획득
        }
    }
}


def classify_sga_items(
    company_name: str,
    sga_items: Dict[str, float],
    business_model: str = 'general'
) -> Dict:
    """
    SG&A 항목을 변동비/고정비로 분류
    
    Args:
        company_name: 회사명
        sga_items: {항목명: 금액}
        business_model: 비즈니스 모델 ('프랜차이즈 본부', '제조업', '플랫폼', 'general')
    
    Returns:
        {
            'variable_costs': {...},
            'semi_variable_costs': {...},
            'fixed_costs': {...},
            'total_variable': float,
            'total_fixed': float
        }
    """
    
    variable = {}
    semi_variable = {}
    fixed = {}
    unclassified = {}
    
    for item, amount in sga_items.items():
        # 항목명 정리 (", 판관비" 제거)
        item_clean = item.replace(', 판관비', '').strip()
        
        classified = False
        
        # 1. 고신뢰 고정비 체크
        for pattern, cost_type in CLASSIFICATION_RULES['fixed_high_confidence'].items():
            if pattern in item_clean:
                fixed[item] = amount
                classified = True
                break
        
        if classified:
            continue
        
        # 2. 변동비 체크
        for pattern, cost_type in CLASSIFICATION_RULES['variable'].items():
            if pattern in item_clean:
                if cost_type == '변동비':
                    variable[item] = amount
                elif cost_type == '준변동비':
                    semi_variable[item] = amount
                classified = True
                break
        
        if classified:
            continue
        
        # 3. 비즈니스 모델별 특수 체크
        if business_model in CLASSIFICATION_RULES['business_specific']:
            special_rules = CLASSIFICATION_RULES['business_specific'][business_model]
            for pattern, cost_type in special_rules.items():
                if pattern in item_clean:
                    if cost_type == '변동비':
                        variable[item] = amount
                    elif cost_type == '준변동비':
                        semi_variable[item] = amount
                    else:
                        fixed[item] = amount
                    classified = True
                    break
        
        if not classified:
            unclassified[item] = amount
    
    return {
        'variable_costs': variable,
        'semi_variable_costs': semi_variable,
        'fixed_costs': fixed,
        'unclassified': unclassified,
        'total_variable': sum(variable.values()),
        'total_semi_variable': sum(semi_variable.values()),
        'total_fixed': sum(fixed.values()),
        'total_sga': sum(variable.values()) + sum(semi_variable.values()) + sum(fixed.values())
    }


def calculate_contribution_margin(
    revenue: float,
    cogs: float,
    variable_sga: float
) -> Dict:
    """
    공헌이익 계산
    
    공식:
        매출총이익 = 매출액 - 매출원가
        공헌이익 = 매출총이익 - 변동 SG&A
        공헌이익률 = 공헌이익 / 매출액
    
    Args:
        revenue: 매출액
        cogs: 매출원가 (100% 변동비)
        variable_sga: 변동 SG&A (준변동비 포함 권장)
    
    Returns:
        {
            'gross_profit': float,
            'gross_margin': float,
            'contribution_margin': float,
            'contribution_margin_ratio': float
        }
    """
    
    gross_profit = revenue - cogs
    gross_margin = gross_profit / revenue if revenue > 0 else 0
    
    contribution_margin = gross_profit - variable_sga
    cm_ratio = contribution_margin / revenue if revenue > 0 else 0
    
    return {
        'gross_profit': gross_profit,
        'gross_margin': round(gross_margin, 4),
        'contribution_margin': contribution_margin,
        'contribution_margin_ratio': round(cm_ratio, 4)
    }


def process_company_file(filepath: Path) -> Dict:
    """단일 회사 파일 처리"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    company = data.get('company', filepath.stem)
    
    print(f"\n{'='*70}")
    print(f"📊 {company} 변동비/고정비 분류")
    print(f"{'='*70}")
    
    # SG&A 데이터
    sga_data = data.get('sga_details_million', {})
    
    if not sga_data:
        print(f"  ⚠️ SG&A 데이터 없음")
        return None
    
    print(f"  SG&A 항목: {len(sga_data)}개")
    
    # 비즈니스 모델 추정
    industry = data.get('industry', '')
    if '편의점' in str(data) or '프랜차이즈' in str(data) or company in ['BGF리테일', 'GS리테일']:
        business_model = '프랜차이즈 본부'
    elif '전자' in company or '반도체' in company:
        business_model = '제조업'
    else:
        business_model = 'general'
    
    print(f"  비즈니스 모델: {business_model}")
    
    # 분류
    classification = classify_sga_items(company, sga_data, business_model)
    
    print(f"\n  변동비: {len(classification['variable_costs'])}개 = {classification['total_variable']/100:,.0f}억원")
    print(f"  준변동비: {len(classification['semi_variable_costs'])}개 = {classification['total_semi_variable']/100:,.0f}억원")
    print(f"  고정비: {len(classification['fixed_costs'])}개 = {classification['total_fixed']/100:,.0f}억원")
    
    if classification['unclassified']:
        print(f"  미분류: {len(classification['unclassified'])}개")
        for item in list(classification['unclassified'].keys())[:5]:
            print(f"    - {item}")
    
    return classification


def main():
    print("="*70)
    print("변동비/고정비 자동 분류 시스템")
    print("="*70)
    
    data_dir = Path("data/raw")
    sga_files = list(data_dir.glob("*_sga_complete.yaml"))
    
    print(f"\n대상 파일: {len(sga_files)}개")
    
    results = {}
    
    for filepath in sorted(sga_files):
        result = process_company_file(filepath)
        if result:
            company = filepath.stem.replace('_sga_complete', '')
            results[company] = result
    
    # 요약
    print(f"\n\n{'='*70}")
    print("전체 요약")
    print(f"{'='*70}")
    
    print(f"\n성공: {len(results)}개 기업")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

