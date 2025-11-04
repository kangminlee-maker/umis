#!/usr/bin/env python3
"""
모든 예제 파일 일괄 재생성 + 검증
컨텍스트 최소화 버전
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.market_sizing_generator import MarketSizingWorkbookGenerator
from umis_rag.deliverables.excel.unit_economics import UnitEconomicsGenerator
from umis_rag.deliverables.excel.financial_projection import FinancialProjectionGenerator
from umis_rag.deliverables.excel.golden_test_framework import GoldenTestRunner, GoldenTestSpec

# 출력 최소화
import os
os.environ['PYTHONUNBUFFERED'] = '1'

print("🚀 모든 예제 재생성 시작...", flush=True)

examples_dir = project_root / 'examples' / 'excel'
examples_dir.mkdir(parents=True, exist_ok=True)

results = {'generated': [], 'validated': []}

# 1. Market Sizing
try:
    gen = MarketSizingWorkbookGenerator()
    fp = gen.generate(
        market_name='piano_subscription_example',
        assumptions=[
            {'id': 'TAM_VALUE', 'category': 'TAM', 'description': '글로벌 악기', 'value': 100_000_000_000, 'unit': '원', 'data_type': '직접데이터', 'source': 'SRC_001', 'confidence': 'High'},
            {'id': 'FILTER_KOREA', 'category': '지역', 'description': '한국', 'value': 0.15, 'unit': '%', 'data_type': '직접데이터', 'source': 'SRC_002', 'confidence': 'High'},
            {'id': 'FILTER_PIANO', 'category': '제품', 'description': '피아노', 'value': 0.25, 'unit': '%', 'data_type': '추정치', 'source': 'EST_001', 'confidence': 'Medium'},
            {'id': 'SEG1_CUSTOMERS', 'category': '세그먼트1', 'description': '타겟', 'value': 100000, 'unit': '명', 'data_type': '추정치', 'source': 'EST_002', 'confidence': 'Medium'},
            {'id': 'SEG1_RATE', 'category': '세그먼트1', 'description': '전환율', 'value': 0.2, 'unit': '%', 'data_type': '추정치', 'source': 'EST_003', 'confidence': 'Medium'},
            {'id': 'SEG1_AOV', 'category': '세그먼트1', 'description': '구독료', 'value': 50000, 'unit': '원', 'data_type': '직접데이터', 'source': 'SRC_003', 'confidence': 'High'},
            {'id': 'SEG1_FREQ', 'category': '세그먼트1', 'description': '빈도', 'value': 12, 'unit': '회', 'data_type': '직접데이터', 'source': 'SRC_004', 'confidence': 'High'},
            {'id': 'PROXY_SIZE', 'category': 'Proxy', 'description': '유사시장', 'value': 50_000_000_000, 'unit': '원', 'data_type': '직접데이터', 'source': 'SRC_005', 'confidence': 'Medium'},
            {'id': 'PROXY_CORR', 'category': 'Proxy', 'description': '상관', 'value': 0.3, 'unit': '', 'data_type': '추정치', 'source': 'EST_004', 'confidence': 'Low'},
            {'id': 'PROXY_APP', 'category': 'Proxy', 'description': '적용', 'value': 0.5, 'unit': '%', 'data_type': '추정치', 'source': 'EST_005', 'confidence': 'Medium'},
            {'id': 'COMP1_REV', 'category': '경쟁사1', 'description': '매출', 'value': 10_000_000_000, 'unit': '원', 'data_type': '직접데이터', 'source': 'SRC_006', 'confidence': 'High'},
            {'id': 'COMP1_SHARE', 'category': '경쟁사1', 'description': '점유율', 'value': 0.4, 'unit': '%', 'data_type': '추정치', 'source': 'EST_006', 'confidence': 'Medium'},
        ],
        tam={'value': 100_000_000_000, 'definition': '글로벌 악기', 'source': 'TAM_VALUE', 'narrowing_steps': [
            {'dimension': '지역', 'ratio_source': 'FILTER_KOREA', 'description': '한국 15%'},
            {'dimension': '제품', 'ratio_source': 'FILTER_PIANO', 'description': '피아노 25%'},
        ]},
        segments=[{'name': '개인', 'target_customers': 'SEG1_CUSTOMERS', 'purchase_rate': 'SEG1_RATE', 'aov': 'SEG1_AOV', 'frequency': 'SEG1_FREQ'}],
        proxy_data={'proxy_market': 'PROXY_SIZE', 'correlation': 'PROXY_CORR', 'application_rate': 'PROXY_APP'},
        competitors=[{'company': '경쟁사A', 'revenue': 'COMP1_REV', 'market_share': 'COMP1_SHARE'}],
        output_dir=examples_dir
    )
    results['generated'].append(('Market Sizing', True))
    print("✅ Market Sizing 생성", flush=True)
except Exception as e:
    results['generated'].append(('Market Sizing', False))
    print(f"❌ Market Sizing 실패: {e}", flush=True)

# 2. Unit Economics
try:
    gen = UnitEconomicsGenerator()
    fp = gen.generate(
        market_name='music_streaming_example',
        inputs_data={'arpu': 9000, 'cac': 25000, 'gross_margin': 0.35, 'monthly_churn': 0.04, 'customer_lifetime': 25, 'sm_spend_monthly': 5000000, 'new_customers_monthly': 200},
        channels_data=[
            {'channel': '검색', 'spend': 2000000, 'customers': 80},
            {'channel': 'SNS', 'spend': 1500000, 'customers': 60},
            {'channel': '제휴', 'spend': 1000000, 'customers': 40},
            {'channel': '오프라인', 'spend': 500000, 'customers': 20},
        ],
        industry='Streaming',
        cohort_months=12,
        output_dir=examples_dir
    )
    results['generated'].append(('Unit Economics', True))
    print("✅ Unit Economics 생성", flush=True)
except Exception as e:
    results['generated'].append(('Unit Economics', False))
    print(f"❌ Unit Economics 실패: {e}", flush=True)

# 3. Financial Projection
try:
    gen = FinancialProjectionGenerator()
    fp = gen.generate(
        market_name='korean_adult_education_example',
        assumptions_data={'base_revenue_y0': 1250_0000_0000, 'growth_rate_yoy': 0.28, 'gross_margin': 0.70, 'ebitda_margin': 0.15, 'net_margin': 0.10, 'sm_percent': 0.30, 'rd_percent': 0.15, 'ga_percent': 0.10, 'tax_rate': 0.25, 'discount_rate': 0.12},
        segments=[
            {'name': 'B2C', 'y0_revenue': 800_0000_0000, 'growth': 0.10},
            {'name': 'B2B', 'y0_revenue': 300_0000_0000, 'growth': 0.35},
            {'name': 'B2G', 'y0_revenue': 100_0000_0000, 'growth': 0.45},
            {'name': 'Global', 'y0_revenue': 50_0000_0000, 'growth': 0.60},
        ],
        years=5,
        output_dir=examples_dir
    )
    results['generated'].append(('Financial Projection', True))
    print("✅ Financial Projection 생성", flush=True)
except Exception as e:
    results['generated'].append(('Financial Projection', False))
    print(f"❌ Financial Projection 실패: {e}", flush=True)

# Golden Test (CALCULATED 버전 필요하므로 생략, 별도 실행)
print("\n검증은 scripts/golden_test_all.py로 별도 실행", flush=True)

# 결과
print("\n" + "="*70)
print(f"생성 완료: {sum(1 for _, s in results['generated'] if s)}/3")
print("="*70)

sys.exit(0 if all(s for _, s in results['generated']) else 1)

