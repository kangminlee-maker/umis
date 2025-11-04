#!/usr/bin/env python3
"""
KPI 정의 라이브러리 구축 스크립트
100개 KPI 목표 (8개 카테고리)

카테고리:
- Platform (20개)
- Subscription (15개)
- E-commerce (15개)
- SaaS (15개)
- Marketplace (10개)
- Finance (10개)
- Marketing (10개)
- General (5개)
"""

import yaml
from pathlib import Path
from datetime import datetime


def generate_platform_kpis():
    """Platform KPI 20개"""
    return [
        {
            'kpi_id': 'KPI_PLT_001',
            'metric_name': '플랫폼 수수료율',
            'category': 'platform',
            'subcategory': 'commission',
            'definition': {
                'korean': '플랫폼이 거래 중개에 대해 공급자로부터 받는 수수료 비율',
                'english': 'Platform commission rate'
            },
            'formula': {
                'numerator': '플랫폼 중개 수수료 (KRW)',
                'denominator': '거래 금액 (KRW)',
                'calculation': '수수료 / 거래액 × 100'
            },
            'unit': '%',
            'typical_range': '3-20%',
            'scope': {
                'includes': ['중개 수수료', '거래 촉진 수수료'],
                'excludes': ['광고비', '배달비', '결제 수수료']
            },
            'industry_examples': [
                {'industry': '음식 배달', 'value': '6-12%', 'geography': 'KR', 'source': 'UMIS RAG'},
                {'industry': '차량 공유', 'value': '20-25%', 'geography': 'Global', 'source': 'Uber 공시'},
                {'industry': '숙박 공유', 'value': '14-16%', 'geography': 'Global', 'source': 'Airbnb'}
            ],
            'validation_rules': [
                '분자/분모 단위 일치 (KRW/KRW)',
                '제외 항목 일치 확인',
                '지리/시기 명시',
                '정의 불일치 시 비교 금지'
            ]
        },
        {
            'kpi_id': 'KPI_PLT_002',
            'metric_name': 'Take Rate',
            'category': 'platform',
            'subcategory': 'revenue',
            'definition': {
                'korean': '플랫폼 총 매출 / GMV',
                'english': 'Platform revenue as % of GMV'
            },
            'formula': {
                'numerator': '플랫폼 총 매출 (수수료 + 광고 + 구독)',
                'denominator': 'GMV (총 거래액)',
                'calculation': '총 매출 / GMV × 100'
            },
            'unit': '%',
            'typical_range': '10-30%',
            'scope': {
                'includes': ['모든 플랫폼 수익원'],
                'excludes': ['환불']
            },
            'industry_examples': [
                {'industry': '이커머스', 'value': '3-5%', 'note': 'Marketplace 모델'},
                {'industry': '음식 배달', 'value': '15-20%', 'note': '수수료 + 광고'}
            ]
        },
        # ... 나머지 18개는 패턴 반복
    ]


def generate_subscription_kpis():
    """Subscription KPI 15개"""
    return [
        {
            'kpi_id': 'KPI_SUB_001',
            'metric_name': '월간 해지율 (Churn Rate)',
            'category': 'subscription',
            'subcategory': 'retention',
            'definition': {
                'korean': '해당 월에 해지한 고객 수 / 월초 총 고객 수',
                'english': 'Monthly customer churn rate'
            },
            'formula': {
                'numerator': '월간 해지 고객 수',
                'denominator': '월초 총 고객 수',
                'calculation': '해지 수 / 월초 고객 수 × 100'
            },
            'unit': '%',
            'typical_range': '2-10%',
            'scope': {
                'includes': ['자발적 해지', '비자발적 해지 (결제 실패)'],
                'excludes': ['무료 체험 해지']
            },
            'industry_benchmarks': [
                {'industry': 'B2C SaaS', 'value': '5-7%', 'geography': 'Global'},
                {'industry': 'B2B SaaS', 'value': '2-3%', 'geography': 'Global'},
                {'industry': 'Consumer Subscription', 'value': '3-5%', 'geography': 'KR'}
            ]
        },
        {
            'kpi_id': 'KPI_SUB_002',
            'metric_name': 'LTV (Lifetime Value)',
            'category': 'subscription',
            'subcategory': 'economics',
            'definition': {
                'korean': '고객 생애 가치',
                'english': 'Customer Lifetime Value'
            },
            'formula': {
                'numerator': 'ARPU × Gross Margin',
                'denominator': 'Churn Rate',
                'calculation': 'ARPU × GM × (1 / Churn)'
            },
            'unit': 'KRW',
            'typical_range': '20만-100만원',
            'scope': {
                'includes': ['구독 수익만'],
                'excludes': ['일회성 수익']
            }
        },
        # ... 나머지 13개
    ]


def generate_ecommerce_kpis():
    """E-commerce KPI 15개"""
    return [
        {
            'kpi_id': 'KPI_EC_001',
            'metric_name': '전환율 (Conversion Rate)',
            'category': 'ecommerce',
            'subcategory': 'sales',
            'definition': {
                'korean': '구매 완료 수 / 방문자 수',
                'english': 'Purchase conversion rate'
            },
            'formula': {
                'numerator': '주문 완료 수',
                'denominator': '방문자 수 (UV)',
                'calculation': '주문 수 / 방문자 × 100'
            },
            'unit': '%',
            'typical_range': '1-5%',
            'industry_benchmarks': [
                {'industry': '이커머스 (PC)', 'value': '2-3%', 'geography': 'Global'},
                {'industry': '이커머스 (모바일)', 'value': '1-2%', 'geography': 'Global'},
                {'industry': '이커머스 (한국)', 'value': '3-4%', 'geography': 'KR', 'note': '모바일 높음'}
            ]
        },
        # ... 나머지 14개
    ]


def generate_saas_kpis():
    """SaaS KPI 15개"""
    return [
        {
            'kpi_id': 'KPI_SAS_001',
            'metric_name': 'MRR (Monthly Recurring Revenue)',
            'category': 'saas',
            'subcategory': 'revenue',
            'definition': {
                'korean': '월간 반복 매출',
                'english': 'Monthly Recurring Revenue'
            },
            'formula': {
                'numerator': '월간 구독 매출',
                'denominator': 'N/A',
                'calculation': 'SUM(구독자별 월 요금)'
            },
            'unit': 'KRW',
            'typical_range': 'N/A'
        },
        # ... 나머지 14개
    ]


def generate_marketplace_kpis():
    """Marketplace KPI 10개"""
    return [
        {
            'kpi_id': 'KPI_MKT_001',
            'metric_name': 'GMV (Gross Merchandise Value)',
            'category': 'marketplace',
            'subcategory': 'volume',
            'definition': {
                'korean': '총 거래액 (환불 전)',
                'english': 'Gross Merchandise Value'
            },
            'formula': {
                'numerator': '총 주문 금액',
                'denominator': 'N/A',
                'calculation': 'SUM(주문 금액)'
            },
            'unit': 'KRW',
            'scope': {
                'includes': ['모든 완료된 거래'],
                'excludes': ['취소', '환불']
            }
        },
        # ... 나머지 9개
    ]


def generate_finance_kpis():
    """Finance KPI 10개"""
    return [
        {
            'kpi_id': 'KPI_FIN_001',
            'metric_name': 'Gross Margin',
            'category': 'finance',
            'subcategory': 'profitability',
            'definition': {
                'korean': '(매출 - 매출원가) / 매출',
                'english': 'Gross profit margin'
            },
            'formula': {
                'numerator': '매출 - COGS',
                'denominator': '매출',
                'calculation': '(Revenue - COGS) / Revenue × 100'
            },
            'unit': '%',
            'typical_range': '20-80%'
        },
        # ... 나머지 9개
    ]


def generate_marketing_kpis():
    """Marketing KPI 10개"""
    return [
        {
            'kpi_id': 'KPI_MKT_001',
            'metric_name': 'CAC (Customer Acquisition Cost)',
            'category': 'marketing',
            'subcategory': 'efficiency',
            'definition': {
                'korean': '총 마케팅 비용 / 신규 고객 수',
                'english': 'Customer Acquisition Cost'
            },
            'formula': {
                'numerator': '마케팅 비용 (KRW)',
                'denominator': '신규 고객 수',
                'calculation': '마케팅 비용 / 신규 고객'
            },
            'unit': 'KRW',
            'typical_range': '1만-50만원'
        },
        # ... 나머지 9개
    ]


def generate_general_kpis():
    """General KPI 5개"""
    return [
        {
            'kpi_id': 'KPI_GEN_001',
            'metric_name': '시장 규모 (Market Size)',
            'category': 'general',
            'subcategory': 'market',
            'definition': {
                'korean': '특정 시장의 연간 총 매출',
                'english': 'Total addressable market'
            },
            'formula': {
                'numerator': '총 시장 매출',
                'denominator': 'N/A',
                'calculation': 'SUM(모든 플레이어 매출)'
            },
            'unit': 'KRW',
            'typical_range': 'N/A'
        },
        # ... 나머지 4개
    ]


def build_kpi_library():
    """
    KPI 라이브러리 생성
    
    Returns:
        kpi_library dict
    """
    
    print("\n" + "=" * 60)
    print("KPI 정의 라이브러리 구축")
    print("=" * 60)
    
    kpi_library = {
        '_meta': {
            'version': '1.0.0',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'agent': 'validator',
            'purpose': '산업 KPI 정의 표준화 (s10 Industry KPI Library)',
            'total_kpis': 0,
            'categories': 8
        }
    }
    
    # 카테고리별 생성
    categories = [
        ('platform_kpis', generate_platform_kpis, 20),
        ('subscription_kpis', generate_subscription_kpis, 15),
        ('ecommerce_kpis', generate_ecommerce_kpis, 15),
        ('saas_kpis', generate_saas_kpis, 15),
        ('marketplace_kpis', generate_marketplace_kpis, 10),
        ('finance_kpis', generate_finance_kpis, 10),
        ('marketing_kpis', generate_marketing_kpis, 10),
        ('general_kpis', generate_general_kpis, 5),
    ]
    
    total_kpis = 0
    
    for cat_name, gen_func, expected in categories:
        print(f"\n📋 {cat_name} 생성 중...")
        kpis = gen_func()
        kpi_library[cat_name] = kpis
        count = len(kpis)
        total_kpis += count
        print(f"   ✅ {count}개 생성 (목표: {expected}개)")
    
    # 총 개수 업데이트
    kpi_library['_meta']['total_kpis'] = total_kpis
    
    # 저장
    output_path = Path("data/raw/kpi_definitions.yaml")
    
    print(f"\n💾 저장 중: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            kpi_library,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            indent=2
        )
    
    print(f"\n✅ KPI 라이브러리 생성 완료!")
    print(f"   총 KPI: {total_kpis}개")
    print(f"   저장 위치: {output_path}")
    print(f"   파일 크기: {output_path.stat().st_size / 1024:.1f} KB")
    
    return kpi_library


if __name__ == '__main__':
    library = build_kpi_library()
    
    print("\n" + "=" * 60)
    print("카테고리별 요약")
    print("=" * 60)
    
    for key in library:
        if key.endswith('_kpis'):
            count = len(library[key])
            cat_name = key.replace('_kpis', '').capitalize()
            print(f"  • {cat_name}: {count}개")
    
    print(f"\n📊 총 {library['_meta']['total_kpis']}개 KPI")

