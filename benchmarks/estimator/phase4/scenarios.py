"""
Phase 4 Fermi Estimation Scenarios

3개 핵심 문제 + 10개 확장 문제
"""

def get_phase4_scenarios():
    """Phase 4 시나리오 반환 (common.py의 함수 참조용)"""
    from benchmarks.estimator.phase4.common import get_phase4_scenarios as _get_scenarios
    return _get_scenarios()


def get_extended_scenarios():
    """확장 10문제 시나리오"""
    from benchmarks.estimator.phase4.common import get_extended_scenarios as _get_extended
    return _get_extended()


# 시나리오 설명
CORE_PROBLEMS = {
    'phase4_korean_businesses': {
        'question': '한국 전체 사업자 수',
        'expected_value': 8200000,
        'difficulty': 'medium',
        'domain': 'business'
    },
    'phase4_seoul_population': {
        'question': '서울시 인구',
        'expected_value': 9500000,
        'difficulty': 'easy',
        'domain': 'demographics'
    },
    'phase4_coffee_shops': {
        'question': '한국 커피 전문점 수',
        'expected_value': 100000,
        'difficulty': 'medium',
        'domain': 'retail'
    }
}

EXTENDED_PROBLEMS = {
    'delivery_drivers': {
        'question': '한국 배달 기사 수',
        'expected_value': 400000,
        'difficulty': 'medium',
        'domain': 'logistics'
    },
    'chicken_delivery': {
        'question': '한국 연간 치킨 배달 건수',
        'expected_value': 600000000,
        'difficulty': 'hard',
        'domain': 'food_service'
    },
    'taxi_passengers': {
        'question': '서울 하루 택시 승객 수',
        'expected_value': 1500000,
        'difficulty': 'medium',
        'domain': 'transportation'
    },
    # ... 나머지 7개 문제
}

