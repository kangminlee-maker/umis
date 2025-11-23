#!/usr/bin/env python3
"""
Phase 4 Extended: 10개 추가 Fermi 문제 테스트
- 3개 모델: o1 (high), gpt-5.1 (medium), gpt-5.1 (high)
- 연결성 및 개념 점수 중심 평가
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..))
sys.path.insert(0, project_root)

from benchmarks.estimator.phase4.common import (
    get_model_config,
    build_api_params,
    call_model_api,
    get_improved_fewshot_prompt,
    evaluate_fermi_response
)

load_dotenv()


def get_extended_scenarios():
    """10개 추가 Fermi 추정 문제"""
    fewshot_example = get_improved_fewshot_prompt()
    
    return [
        {
            'id': 'extended_delivery_riders',
            'name': '한국 전체 배달 기사(라이더) 수',
            'expected_value': 400000,
            'expected_unit': '명',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 전체 배달 기사(라이더) 수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 배달 플랫폼 (배달의민족, 쿠팡이츠, 요기요 등)
- 전업 vs 부업 라이더 구분
- 시간대별 수요와 공급
- 지역별 밀도 차이

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 전체 배달 기사 수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 플랫폼 경제, 전업/부업, 지역별 밀도 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "명",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_chicken_delivery',
            'name': '한국 연간 치킨 배달 주문 건수',
            'expected_value': 1100000000,
            'expected_unit': '건',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 연간 치킨 배달 주문 건수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 한국 인구 및 가구 수
- 1인 가구 증가 트렌드
- 주중/주말 주문 패턴 차이
- 계절별 변동성

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 연간 치킨 배달 주문 건수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 1인 가구, 배달 문화, 주중/주말 차이 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "건",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_taxi_passengers',
            'name': '서울시 하루 평균 택시 승객 수',
            'expected_value': 1500000,
            'expected_unit': '명',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 서울시 하루 평균 택시 승객 수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 서울시 인구 및 유동 인구
- 교통 수단 분담률
- 시간대별 수요 (출퇴근, 심야)
- 대체 수단 (지하철, 버스, 카풀)

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 서울시 하루 평균 택시 승객 수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 대중교통 분담률, 시간대별 패턴 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "명",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_credit_card',
            'name': '한국 연간 신용카드 승인 건수',
            'expected_value': 30000000000,
            'expected_unit': '건',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 연간 신용카드 승인 건수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 신용카드 보유 인구
- 현금 대체율
- 온라인/오프라인 거래
- 소액 결제 증가 (간편결제)

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 연간 신용카드 승인 건수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 현금 대체율, 디지털 결제 증가 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "건",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_hospital_visits',
            'name': '한국 연간 병원 외래 진료 건수',
            'expected_value': 1700000000,
            'expected_unit': '건',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 연간 병원 외래 진료 건수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 전 국민 건강보험 가입
- 고령 인구 증가
- 만성질환 유병률
- 계절별 질병 (감기, 독감 등)

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 연간 병원 외래 진료 건수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 고령화, 만성질환, 의료 접근성 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "건",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_private_education',
            'name': '한국 초중고 학생 연간 사교육비 총액',
            'expected_value': 26000000000000,
            'expected_unit': '원',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 초중고 학생 연간 사교육비 총액을 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 초중고 학생 수
- 학년별 사교육 참여율
- 소득 분위별 지출 차이
- 과목별 (수학, 영어, 국어 등)

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 초중고 학생 연간 사교육비 총액"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 학년별 차이, 소득 격차, 지역 차이 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "원",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_jeonse_contracts',
            'name': '서울시 연간 전세 계약 건수',
            'expected_value': 400000,
            'expected_unit': '건',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 서울시 연간 전세 계약 건수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 서울시 전체 가구 수
- 전세 vs 월세 비중
- 전세 계약 주기 (보통 2년)
- 신혼/이직 등 이동 수요

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 서울시 연간 전세 계약 건수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 전세 비중, 이동 주기, 재계약률 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "건",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_ott_subscribers',
            'name': '한국 유료 OTT 구독자 수',
            'expected_value': 25000000,
            'expected_unit': '명',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 유료 OTT 구독자 수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 주요 OTT (넷플릭스, 티빙, 웨이브, 디즈니+ 등)
- 중복 구독 (1인이 여러 서비스)
- 세대별 이용률
- 가구당 계정 공유

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 유료 OTT 구독자 수"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 중복 구독, 세대별 차이, 계정 공유 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "명",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_coupang_boxes',
            'name': '쿠팡 일평균 배송 물량',
            'expected_value': 12000000,
            'expected_unit': '박스',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 쿠팡 일평균 배송 물량(박스 수)을 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 한국 이커머스 시장 규모
- 쿠팡 시장 점유율 (약 25-30%)
- 로켓배송 이용률
- 1인당 월평균 주문 횟수

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 쿠팡 일평균 배송 물량"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 시장 점유율, 로켓배송 비중, 주문 패턴 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "박스",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        },
        {
            'id': 'extended_disposable_cups',
            'name': '한국 연간 일회용 컵 사용량',
            'expected_value': 33000000000,
            'expected_unit': '개',
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 연간 일회용 컵 사용량을 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 카페 (스타벅스, 이디야 등)
- 편의점 음료
- 재사용 컵/텀블러 비율
- 계절별 변동 (여름 증가)

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 연간 일회용 컵 사용량"
3. 마지막 step의 "calculation"은 실제 사칙연산
4. 카페 판매, 재사용 비율, 계절 변동 등 개념 활용

JSON 형식 (엄격히 준수):
{{
    "value": 추정값 (숫자),
    "unit": "개",
    "confidence": 0.0-1.0,
    "method": "bottom-up" 또는 "top-down",
    "decomposition": [...]
}}'''
        }
    ]


def test_model_on_scenario(client, model_name, scenario, reasoning_effort):
    """단일 모델로 단일 시나리오 테스트"""
    
    try:
        start = time.time()
        
        # API 파라미터 생성
        api_type, api_params = build_api_params(
            model_name=model_name,
            prompt=scenario['prompt'],
            reasoning_effort=reasoning_effort
        )
        
        # API 호출
        response = call_model_api(client, api_type, api_params)
        
        elapsed = time.time() - start
        
        # 응답 추출
        if api_type == 'responses':
            if isinstance(response.output, list):
                for item in response.output:
                    if hasattr(item, 'role') and item.role == 'assistant':
                        if hasattr(item, 'content') and isinstance(item.content, list):
                            for content_item in item.content:
                                if hasattr(content_item, 'text'):
                                    output = content_item.text
                                    break
            else:
                output = response.output
        else:
            output = response.choices[0].message.content
        
        # JSON 파싱
        import json as json_lib
        import re
        
        clean_output = re.sub(r'```json\s*', '', output)
        clean_output = re.sub(r'```\s*$', '', clean_output)
        clean_output = clean_output.strip()
        
        parsed = json_lib.loads(clean_output)
        
        # 평가
        evaluation = evaluate_fermi_response(
            model_name=model_name,
            response=parsed,
            expected_value=scenario['expected_value'],
            problem_id=scenario['id']
        )
        
        return {
            'model': model_name,
            'problem': scenario['name'],
            'problem_id': scenario['id'],
            'expected_value': scenario['expected_value'],
            'reasoning_effort': reasoning_effort,
            'response': output,
            'elapsed': elapsed,
            **evaluation
        }
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return None


def run_extended_test():
    """10개 문제 × 3개 모델 테스트"""
    
    print("=" * 120)
    print("🚀 Phase 4 Extended: 10개 추가 Fermi 문제 테스트")
    print("=" * 120)
    print()
    print("📊 테스트 구성:")
    print("  • 문제 수: 10개")
    print("  • 모델: 3개 (o1, gpt-5.1 medium, gpt-5.1 high)")
    print("  • 총 테스트: 30개")
    print("  • 예상 시간: 30-40분")
    print()
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    scenarios = get_extended_scenarios()
    
    # 테스트할 모델 구성
    test_config = [
        {'model': 'o1', 'effort': 'high'},
        {'model': 'gpt-5.1', 'effort': 'medium'},
        {'model': 'gpt-5.1', 'effort': 'high'}
    ]
    
    all_results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print("\n" + "=" * 120)
        print(f"📋 문제 {i}/10: {scenario['name']}")
        print(f"   정답: {scenario['expected_value']:,} {scenario['expected_unit']}")
        print("=" * 120)
        
        for j, config in enumerate(test_config, 1):
            model_name = config['model']
            reasoning_effort = config['effort']
            
            print(f"\n🔄 모델 {j}/3: {model_name} (effort={reasoning_effort})")
            
            result = test_model_on_scenario(
                client=client,
                model_name=model_name,
                scenario=scenario,
                reasoning_effort=reasoning_effort
            )
            
            if result:
                all_results.append(result)
                
                print(f"   ✅ {result['value']:,} {result['unit']} | 총점: {result['total_score']:.1f}/110")
                print(f"      연결성: {result['calculation_connectivity']['score']:.1f}/50 | "
                      f"개념: {result['conceptual_coherence']['score']}/15 | "
                      f"시간: {result['elapsed']:.1f}초")
        
        # 문제별 순위
        problem_results = [r for r in all_results if r['problem'] == scenario['name']]
        if problem_results:
            print(f"\n📊 {scenario['name']} 순위:")
            sorted_results = sorted(problem_results, key=lambda x: x['total_score'], reverse=True)
            for rank, r in enumerate(sorted_results, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                print(f"  {medal}{rank}. {r['model']} ({r['reasoning_effort']}): {r['total_score']:.1f}/110")
    
    # 최종 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'phase4_extended_10problems_{timestamp}.json'
    
    # 모델별 평균 계산
    from collections import defaultdict
    by_model = defaultdict(list)
    for r in all_results:
        key = f"{r['model']}_{r['reasoning_effort']}"
        by_model[key].append(r)
    
    summary = []
    for model_key, results in by_model.items():
        if results:
            summary.append({
                'model': results[0]['model'],
                'effort': results[0]['reasoning_effort'],
                'avg_total': sum(r['total_score'] for r in results) / len(results),
                'avg_connectivity': sum(r['calculation_connectivity']['score'] for r in results) / len(results),
                'avg_concept': sum(r['conceptual_coherence']['score'] for r in results) / len(results),
                'avg_accuracy': sum(r['accuracy']['score'] for r in results) / len(results),
                'avg_time': sum(r['elapsed'] for r in results) / len(results),
                'count': len(results)
            })
    
    summary_sorted = sorted(summary, key=lambda x: x['avg_total'], reverse=True)
    
    # 최종 순위 출력
    print("\n" + "=" * 120)
    print("🏆 최종 순위 (10개 문제 평균)")
    print("=" * 120)
    print()
    
    print(f"{'순위':<4} | {'모델':<15} | {'Effort':<8} | {'평균 총점':<11} | {'연결성':<10} | {'개념':<9} | {'평균 시간':<12}")
    print("-" * 120)
    
    for rank, s in enumerate(summary_sorted, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"{medal}{rank:<3} | {s['model']:<15} | {s['effort']:<8} | {s['avg_total']:>9.1f}/110 | "
              f"{s['avg_connectivity']:>8.1f}/50 | {s['avg_concept']:>7.1f}/15 | {s['avg_time']:>9.1f}초")
    
    # 저장
    output_data = {
        'timestamp': timestamp,
        'test_name': 'Phase 4 Extended - 10 Additional Fermi Problems',
        'test_config': test_config,
        'scenarios': [
            {
                'id': s['id'],
                'name': s['name'],
                'expected_value': s['expected_value'],
                'expected_unit': s['expected_unit']
            }
            for s in scenarios
        ],
        'results': all_results,
        'summary': summary_sorted
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("\n🎉 전체 테스트 완료!")


if __name__ == '__main__':
    run_extended_test()

