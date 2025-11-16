#!/usr/bin/env python3
"""
SG&A 데이터를 완전한 Economics 분석으로 확장

입력: *_sga_complete.yaml (SG&A 항목만)
출력: *_economics_complete.yaml (BGF 템플릿 형식)

프로세스:
1. DART API로 재무제표 기본 정보 수집
2. 비즈니스 모델 파악
3. SG&A 변동비/고정비 분류
4. 공헌이익 계산
5. BGF 템플릿 형식으로 저장
"""

import yaml
from pathlib import Path
from typing import Dict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient


# 비즈니스 모델별 분류 규칙
BUSINESS_MODELS = {
    'GS리테일': '프랜차이즈 본부',
    '이마트': '대형마트 (직영)',
    '삼성전자': '전자제조',
    'LG전자': '전자제조',
    'SK하이닉스': '반도체제조',
    '유한양행': '제약제조',
    '아모레퍼시픽': '화장품제조',
    'LG생활건강': '화장품제조',
    'CJ ENM': '엔터/미디어',
    '하이브': '엔터/음악',
}

# 비즈니스 모델별 SG&A 변동비 패턴
VARIABLE_PATTERNS = {
    '프랜차이즈 본부': {
        'variable': ['광고선전비', '판매촉진비', '운반비'],
        'semi_variable': ['지급수수료', '사용권자산상각'],  # 가맹점/거래량 비례
    },
    '대형마트 (직영)': {
        'variable': ['광고선전비', '판매촉진비', '운반비'],
        'semi_variable': ['지급수수료'],  # 카드 수수료
    },
    '전자제조': {
        'variable': ['광고선전비', '판매촉진비', '운반비', '서비스비'],
        'semi_variable': ['지급수수료'],
    },
    '반도체제조': {
        'variable': ['운반비'],
        'semi_variable': ['지급수수료'],
    },
    '제약제조': {
        'variable': ['광고선전비', '판매촉진비', '운반비'],
        'semi_variable': ['지급수수료'],
    },
    '화장품제조': {
        'variable': ['광고선전비', '판매촉진비', '운반비'],
        'semi_variable': ['지급수수료'],
    },
    '엔터/미디어': {
        'variable': ['광고선전비', '운반비'],
        'semi_variable': ['지급수수료'],
    },
    '엔터/음악': {
        'variable': ['광고선전비', '운반비'],
        'semi_variable': ['지급수수료'],
    },
}


def get_financials_from_dart(company_name: str, year: int, corp_code: str = None) -> Dict:
    """DART API로 재무제표 기본 정보 가져오기"""
    
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        api_key = os.getenv('DART_API_KEY')
        client = DARTClient(api_key)
        
        # corp_code가 없으면 검색
        if not corp_code:
            corp_code = client.get_corp_code(company_name)
        
        if not corp_code:
            return None
        
        # 재무제표 조회 (OFS 우선)
        financials = client.get_financials(corp_code, year, fs_div='OFS')
        
        if not financials:
            # OFS 없으면 CFS
            financials = client.get_financials(corp_code, year, fs_div='CFS')
            fs_div = 'CFS'
        else:
            fs_div = 'OFS'
        
        if not financials:
            return None
        
        # 주요 계정 추출
        revenue = 0
        cogs = 0
        sga = 0
        operating_profit = 0
        
        for item in financials:
            account = item.get('account_nm', '')
            amount_str = item.get('thstrm_amount', '0')
            
            try:
                amount = float(amount_str.replace(',', ''))
            except:
                amount = 0
            
            if '매출액' in account and '매출원가' not in account:
                revenue = amount
            elif '매출원가' in account:
                cogs = amount
            elif '판매비' in account or '관리비' in account:
                sga = amount
            elif '영업이익' in account:
                operating_profit = amount
        
        if revenue > 0:
            return {
                'revenue': revenue / 100_000_000,  # 억원
                'cogs': cogs / 100_000_000,
                'sga_total': sga / 100_000_000,
                'operating_profit': operating_profit / 100_000_000,
                'gross_profit': (revenue - cogs) / 100_000_000,
                'gross_margin': (revenue - cogs) / revenue if revenue > 0 else 0,
                'operating_margin': operating_profit / revenue if revenue > 0 else 0,
                'fs_div': fs_div
            }
        
    except Exception as e:
        print(f"  ⚠️ DART API 오류: {e}")
    
    return None


def classify_sga_by_business_model(
    sga_items: Dict[str, float],
    business_model: str
) -> Dict:
    """비즈니스 모델별 SG&A 분류"""
    
    patterns = VARIABLE_PATTERNS.get(business_model, VARIABLE_PATTERNS['프랜차이즈 본부'])
    
    variable = {}
    semi_variable = {}
    fixed = {}
    
    for item, amount in sga_items.items():
        item_clean = item.replace(', 판관비', '').strip()
        
        classified = False
        
        # 변동비 체크
        for pattern in patterns.get('variable', []):
            if pattern in item_clean:
                variable[item] = amount
                classified = True
                break
        
        if classified:
            continue
        
        # 준변동비 체크
        for pattern in patterns.get('semi_variable', []):
            if pattern in item_clean:
                semi_variable[item] = amount
                classified = True
                break
        
        if classified:
            continue
        
        # 고정비 (기본)
        # 급여, 퇴직급여, 복리후생비, 감가상각비, 임차료 등
        fixed_keywords = ['급여', '퇴직', '복리후생', '감가상각', '상각비', '임차료', 
                         '수도광열', '세금과공과', '접대비', '여비', '통신비', '소모품',
                         '교육', '회의', '수선', '보험']
        
        for keyword in fixed_keywords:
            if keyword in item_clean:
                fixed[item] = amount
                classified = True
                break
        
        if not classified:
            # 기타 항목은 일단 고정비로
            if amount > 0:  # 금액이 있으면
                fixed[item] = amount
    
    return {
        'variable': variable,
        'semi_variable': semi_variable,
        'fixed': fixed
    }


def create_economics_yaml(company_name: str, sga_filepath: Path) -> Dict:
    """SG&A 파일을 Economics 완전 분석으로 확장"""
    
    print(f"\n{'='*70}")
    print(f"📊 {company_name} Economics 분석")
    print(f"{'='*70}")
    
    # 기존 SG&A 데이터 로드
    with open(sga_filepath, 'r', encoding='utf-8') as f:
        sga_data = yaml.safe_load(f)
    
    company = sga_data.get('company', company_name)
    year = sga_data.get('year', 2023)
    rcept_no = sga_data.get('rcept_no')
    unit = sga_data.get('unit', '백만원')
    sga_items = sga_data.get('sga_details_million', {})
    
    print(f"  SG&A 항목: {len(sga_items)}개")
    
    # DART API로 재무제표 수집
    print(f"  DART API 재무제표 조회...")
    
    financials = get_financials_from_dart(company, year)
    
    if not financials:
        print(f"  ⚠️ 재무제표 조회 실패")
        return None
    
    print(f"  ✅ 재무제표 조회 성공 ({financials['fs_div']})")
    print(f"     매출액: {financials['revenue']:,.0f}억원")
    print(f"     매출총이익률: {financials['gross_margin']:.1%}")
    
    # 비즈니스 모델 파악
    business_model = BUSINESS_MODELS.get(company, 'general')
    print(f"  비즈니스 모델: {business_model}")
    
    # SG&A 항목 단위 변환 (백만원 → 억원)
    sga_items_billion = {}
    
    if unit == '백만원':
        sga_items_billion = {k: v / 100 for k, v in sga_items.items()}
    elif unit == '천원':
        sga_items_billion = {k: v / 1000 for k, v in sga_items.items()}
    elif unit == '원':
        sga_items_billion = {k: v / 100_000_000 for k, v in sga_items.items()}
    else:
        sga_items_billion = sga_items
    
    # SG&A 분류
    classification = classify_sga_by_business_model(sga_items_billion, business_model)
    
    total_variable = sum(classification['variable'].values())
    total_semi = sum(classification['semi_variable'].values())
    total_fixed = sum(classification['fixed'].values())
    
    print(f"\n  SG&A 분류:")
    print(f"    변동비: {len(classification['variable'])}개 = {total_variable:,.0f}억원")
    print(f"    준변동비: {len(classification['semi_variable'])}개 = {total_semi:,.0f}억원")
    print(f"    고정비: {len(classification['fixed'])}개 = {total_fixed:,.0f}억원")
    
    # 공헌이익 계산
    gross_profit = financials['gross_profit']
    variable_sga = total_variable + total_semi  # 준변동비도 변동비로 간주
    
    contribution_margin = gross_profit - variable_sga
    cm_ratio = contribution_margin / financials['revenue']
    
    print(f"\n  공헌이익:")
    print(f"    매출총이익: {gross_profit:,.0f}억원 ({financials['gross_margin']:.1%})")
    print(f"    - 변동 SG&A: {variable_sga:,.0f}억원")
    print(f"    = 공헌이익: {contribution_margin:,.0f}억원 ({cm_ratio:.1%}) ⭐")
    
    # 완전한 YAML 생성 (BGF 템플릿 형식)
    economics_data = {
        'version': '1.0_economics',
        'created': '2025-11-13',
        'status': 'complete_with_classification',
        
        'company_info': {
            'company_name': company,
            'industry': business_model,
            'region': '한국',
            'year': year,
        },
        
        'financial_statement_info': {
            'year': year,
            'report_type': '사업보고서',
            'rcept_no': rcept_no,
            'fs_type': f'{"개별" if financials["fs_div"] == "OFS" else "연결"}재무제표 ({financials["fs_div"]})',
            'fs_div': financials['fs_div'],
        },
        
        'income_statement': {
            'key_accounts_billion': {
                'revenue': round(financials['revenue'], 1),
                'cogs': round(financials['cogs'], 1),
                'gross_profit': round(financials['gross_profit'], 1),
                'sga_total': round(financials['sga_total'], 1),
                'operating_profit': round(financials['operating_profit'], 1),
            },
            'ratios': {
                'cogs_ratio': round(financials['cogs'] / financials['revenue'], 4),
                'gross_margin': round(financials['gross_margin'], 4),
                'sga_ratio': round(financials['sga_total'] / financials['revenue'], 4),
                'operating_margin': round(financials['operating_margin'], 4),
            }
        },
        
        'sga_details': {
            'total_billion': round(sum(sga_items_billion.values()), 1),
            'count': len(sga_items_billion),
            'unit_original': unit,
            'details_billion': {k: round(v, 1) for k, v in sorted(sga_items_billion.items(), key=lambda x: x[1], reverse=True)},
        },
        
        'cost_classification': {
            'variable_costs_billion': {k: round(v, 1) for k, v in sorted(classification['variable'].items(), key=lambda x: x[1], reverse=True)},
            'semi_variable_costs_billion': {k: round(v, 1) for k, v in sorted(classification['semi_variable'].items(), key=lambda x: x[1], reverse=True)},
            'fixed_costs_billion': {k: round(v, 1) for k, v in sorted(classification['fixed'].items(), key=lambda x: x[1], reverse=True)[:10]},  # Top 10만
            
            'totals': {
                'variable': round(total_variable, 1),
                'semi_variable': round(total_semi, 1),
                'fixed': round(total_fixed, 1),
            }
        },
        
        'unit_economics': {
            'gross_profit_billion': round(gross_profit, 1),
            'gross_margin': round(financials['gross_margin'], 4),
            
            'variable_sga_billion': round(variable_sga, 1),
            'variable_sga_ratio': round(variable_sga / financials['revenue'], 4),
            
            'contribution_margin_billion': round(contribution_margin, 1),
            'contribution_margin_ratio': round(cm_ratio, 4),
            
            'fixed_sga_billion': round(total_fixed, 1),
            'fixed_sga_ratio': round(total_fixed / financials['revenue'], 4),
            
            'operating_profit_billion': round(financials['operating_profit'], 1),
            'operating_margin': round(financials['operating_margin'], 4),
            
            'analysis': {
                'cm_vs_om': f"공헌이익 {cm_ratio:.1%} > 영업이익 {financials['operating_margin']:.1%}",
                'variable_intensity': round((financials['cogs'] + variable_sga) / financials['revenue'], 4),
                'business_model': business_model,
                'health': 'healthy' if cm_ratio > 0.05 else 'weak'
            }
        }
    }
    
    return economics_data


def main():
    print("="*70)
    print("10개 기업 Economics 완전 분석")
    print("="*70)
    
    data_dir = Path("data/raw")
    sga_files = list(data_dir.glob("*_sga_complete.yaml"))
    
    # BGF리테일은 이미 완전 템플릿 있으므로 제외
    sga_files = [f for f in sga_files if 'BGF' not in f.name]
    
    print(f"\n대상: {len(sga_files)}개 기업")
    
    success_count = 0
    
    for filepath in sorted(sga_files):
        company_name = filepath.stem.replace('_sga_complete', '')
        
        economics = create_economics_yaml(company_name, filepath)
        
        if economics:
            # 저장
            output_path = data_dir / f"{company_name}_economics_complete.yaml"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(economics, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            print(f"  ✅ 저장: {output_path.name}")
            success_count += 1
        else:
            print(f"  ❌ 실패")
    
    print(f"\n{'='*70}")
    print(f"완료: {success_count}/{len(sga_files)}개 기업")
    print(f"{'='*70}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

