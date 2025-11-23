#!/usr/bin/env python3
"""
GPT-5/5.1 Phase 0-4 고난이도 테스트
실제 UMIS Estimator 수준의 문항으로 모델 성능 검증
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# =====================================
# Phase 0-4 테스트 시나리오 (고난이도)
# =====================================

PHASE_SCENARIOS = {
    'phase_0': {
        'name': 'Phase 0: 복잡한 데이터 추출',
        'difficulty': 'Medium',
        'description': '여러 조건이 섞인 데이터에서 정확한 값 추출',
        'prompt': '''다음 시장 데이터에서 "한국 B2B SaaS 평균 ARPU (연간 구독)" 값을 추출하세요.

데이터:
- 한국 B2B SaaS 월간 구독 ARPU: 18,000원
- 한국 B2B SaaS 연간 구독 ARPU: 200,000원
- 한국 B2C SaaS 연간 구독 ARPU: 70,000원
- 일본 B2B SaaS 연간 구독 ARPU: ¥180,000
- 한국 B2B SaaS 평균 해지율: 8.5%
- 한국 B2B SaaS 평균 CAC: 450,000원

조건:
1. B2B만 추출 (B2C 제외)
2. 연간 구독만 추출 (월간 제외)
3. 한국만 추출 (일본 제외)
4. ARPU만 추출 (해지율, CAC 제외)

반드시 다음 JSON 형식으로만 응답하세요:
{"value": 200000, "unit": "원", "confidence": 1.0, "reasoning": "추출 근거"}''',
        'expected': {
            'value': 200000,
            'unit': '원',
            'confidence': 1.0
        }
    },
    
    'phase_1': {
        'name': 'Phase 1: 간단한 계산',
        'difficulty': 'Medium-High',
        'description': '주어진 값들로 간단한 산술 계산',
        'prompt': '''다음 데이터를 사용하여 "한국 B2B SaaS LTV"를 계산하세요.

주어진 데이터:
- 평균 ARPU (연간): 200,000원
- 평균 고객 유지 기간: 3.2년
- 연간 해지율: 8.5%

계산식:
LTV = ARPU × 평균 유지 기간
또는
LTV = ARPU / 해지율 (연간)

두 방법 중 하나를 선택하여 계산하세요.

반드시 다음 JSON 형식으로만 응답하세요:
{"value": <계산된_값>, "unit": "원", "confidence": <0.7-1.0>, "method": "사용한 계산식", "reasoning": "계산 과정"}''',
        'expected': {
            'value_range': [640000, 2352941],  # 두 방법의 결과 범위
            'unit': '원',
            'min_confidence': 0.7
        }
    },
    
    'phase_2': {
        'name': 'Phase 2: 지식 기반 추론',
        'difficulty': 'High',
        'description': 'Validator RAG 수준의 정의 및 벤치마크 활용',
        'prompt': '''다음 상황에서 "한국 B2B 협업 SaaS CAC"를 추정하세요.

상황:
- 산업: B2B 협업 도구 (Slack, Notion 유사)
- 시장: 한국
- 고객: 중소기업 (10-50명)
- 마케팅 채널: 디지털 마케팅 + Inside Sales

참고 정보 (활용 가능):
- 미국 B2B SaaS 평균 CAC: $1,200 (약 1,560,000원)
- 한국 SaaS CAC는 미국 대비 30-40% 수준
- B2B 협업 도구는 일반 SaaS 대비 CAC 20% 낮음 (바이럴 효과)
- 중소기업 타겟은 대기업 대비 CAC 40% 낮음

계산 과정:
1. 미국 기준값 선택
2. 한국 할인 적용
3. 협업 도구 할인 적용
4. 중소기업 할인 적용

반드시 다음 JSON 형식으로만 응답하세요:
{"value": <추정값>, "unit": "원", "confidence": <0.5-0.8>, "method": "계산 과정", "assumptions": ["가정1", "가정2"]}''',
        'expected': {
            'value_range': [200000, 500000],  # 합리적 범위
            'unit': '원',
            'min_confidence': 0.5
        }
    },
    
    'phase_3': {
        'name': 'Phase 3: 복잡한 시나리오 계산',
        'difficulty': 'High',
        'description': '여러 변수를 고려한 성장률 분석',
        'prompt': '''다음 데이터를 바탕으로 "3년 후 한국 B2B 협업 SaaS 시장 규모"를 계산하세요.

현재 시장 정보 (2025년):
- 현재 시장 규모: 500억원
- 현재 활성 기업 고객: 25,000개
- 평균 ARPU: 200만원/년

성장 요인:
1. 시장 성장률: 연 25% (팬데믹 이후 가속)
2. 고객 증가율: 연 20%
3. ARPU 증가율: 연 5% (기능 추가, 업셀링)

계산 과제:
- 단순 성장률 적용 vs 복합 성장 고려
- 3년 후 (2028년) 시장 규모 추정

반드시 다음 JSON 형식으로만 응답하세요:
{"value": <추정값>, "unit": "억원", "confidence": <0.6-0.9>, "method": "계산식", "breakdown": {"고객수": <값>, "ARPU": <값>}, "reasoning": "계산 근거"}''',
        'expected': {
            'value_range': [900, 1200],  # 억원 단위
            'unit': '억원',
            'min_confidence': 0.6
        }
    },
    
    'phase_4': {
        'name': 'Phase 4: Fermi 추정 (완전 미지의 값)',
        'difficulty': 'Very High',
        'description': '데이터 없이 순수 분해와 가정으로 추정',
        'prompt': '''데이터 없이 "한국 기업용 화상회의 솔루션 TAM (Total Addressable Market)"을 추정하세요.

제약 조건:
- 데이터는 주어지지 않음
- 순수 Fermi 분해 방식 사용
- Top-down 또는 Bottom-up 접근

추정 가이드 (선택 사항):
1. Top-down: 한국 전체 기업 수 → 잠재 고객 → 지불 의향 → 가격
2. Bottom-up: 평균 기업 규모 → 사용자 수 → 좌석당 가격 → 시장 침투율

필수 포함 요소:
- 명확한 분해 단계 (3단계 이상)
- 각 단계별 가정과 근거
- 최종 추정값과 신뢰 구간

반드시 다음 JSON 형식으로만 응답하세요:
{
    "value": <추정값>,
    "unit": "억원",
    "confidence": <0.3-0.7>,
    "method": "top-down 또는 bottom-up",
    "decomposition": [
        {"step": "단계1", "assumption": "가정", "value": <값>},
        {"step": "단계2", "assumption": "가정", "value": <값>}
    ],
    "reasoning": "전체 추정 논리",
    "confidence_range": {"min": <최소값>, "max": <최대값>}
}''',
        'expected': {
            'value_range': [500, 3000],  # 억원, 넓은 범위 허용
            'unit': '억원',
            'min_confidence': 0.3,
            'min_decomposition_steps': 3
        }
    }
}


def test_model_on_phase(client, model, api_type, phase_id, scenario, reasoning_config=None):
    """특정 Phase에서 모델 테스트"""
    
    prompt = scenario['prompt']
    
    try:
        start = time.time()
        
        if api_type == 'responses':
            # Responses API
            api_params = {
                "model": model,
                "input": prompt,
            }
            
            if reasoning_config:
                api_params["reasoning"] = reasoning_config.get("reasoning", {"effort": "low"})
                api_params["text"] = reasoning_config.get("text", {"verbosity": "low"})
            else:
                api_params["reasoning"] = {"effort": "medium"}
                api_params["text"] = {"verbosity": "low"}
            
            response = client.responses.create(**api_params)
            
            # 응답 추출
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output'):
                content = response.output
            else:
                content = str(response)
            
            # 토큰 정보
            tokens = {
                'input': getattr(response, 'input_tokens', len(prompt) // 4),
                'output': getattr(response, 'output_tokens', len(content) // 4),
            }
            tokens['total'] = tokens['input'] + tokens['output']
            
        else:
            # Chat API
            api_params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            }
            
            if reasoning_config and reasoning_config.get('reasoning_effort'):
                api_params["reasoning_effort"] = reasoning_config['reasoning_effort']
            
            response = client.chat.completions.create(**api_params)
            content = response.choices[0].message.content
            
            # 토큰 정보
            tokens = {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens,
                'total': response.usage.total_tokens
            }
            
            # reasoning_tokens 추가
            if hasattr(response.usage, 'completion_tokens_details'):
                details = response.usage.completion_tokens_details
                if hasattr(details, 'reasoning_tokens') and details.reasoning_tokens:
                    tokens['reasoning'] = details.reasoning_tokens
        
        elapsed = time.time() - start
        
        # JSON 파싱
        import re
        
        try:
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            parsed = json.loads(content)
        except Exception as e:
            parsed = {'raw': content[:200], 'parse_error': str(e)}
        
        # 비용 계산
        pricing = {
            'gpt-4.1-nano': {'input': 0.10, 'output': 0.40},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5.1': {'input': 1.25, 'output': 10.00}
        }
        
        rates = pricing.get(model, {'input': 1.25, 'output': 10.00})
        cost = (tokens['input'] / 1_000_000 * rates['input'] + 
               tokens['output'] / 1_000_000 * rates['output'])
        
        # 품질 평가 (Phase별 기준)
        quality_score = evaluate_phase_quality(phase_id, parsed, scenario['expected'])
        
        return {
            'success': True,
            'cost': cost,
            'elapsed_seconds': round(elapsed, 2),
            'quality_score': quality_score,
            'tokens': tokens,
            'response': parsed
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def evaluate_phase_quality(phase_id, response, expected):
    """Phase별 품질 평가 (100점 만점)"""
    
    if 'parse_error' in response:
        return 0
    
    score = 0
    
    # 기본 구조 (25점)
    if 'value' in response:
        score += 15
    if 'unit' in response:
        score += 5
    if 'confidence' in response:
        score += 5
    
    # Phase 0: 정확한 값 추출 (75점)
    if phase_id == 'phase_0':
        if response.get('value') == expected['value']:
            score += 50  # 정확한 값
        if response.get('unit') == expected['unit']:
            score += 15
        if response.get('confidence') == expected['confidence']:
            score += 10
    
    # Phase 1: 계산 정확도 (75점)
    elif phase_id == 'phase_1':
        value = response.get('value', 0)
        if expected['value_range'][0] <= value <= expected['value_range'][1]:
            score += 40  # 범위 내
        if response.get('unit') == expected['unit']:
            score += 15
        if 'method' in response:
            score += 10
        if 'reasoning' in response:
            score += 10
    
    # Phase 2: 추론 품질 (75점)
    elif phase_id == 'phase_2':
        value = response.get('value', 0)
        if expected['value_range'][0] <= value <= expected['value_range'][1]:
            score += 30
        if response.get('confidence', 0) >= expected['min_confidence']:
            score += 10
        if 'method' in response:
            score += 15
        if 'assumptions' in response and len(response.get('assumptions', [])) >= 2:
            score += 20
    
    # Phase 3: 시나리오 분석 (75점)
    elif phase_id == 'phase_3':
        value = response.get('value', 0)
        if expected['value_range'][0] <= value <= expected['value_range'][1]:
            score += 30
        if 'method' in response:
            score += 15
        if 'breakdown' in response:
            score += 15
        if 'reasoning' in response:
            score += 15
    
    # Phase 4: Fermi 분해 (75점)
    elif phase_id == 'phase_4':
        value = response.get('value', 0)
        if expected['value_range'][0] <= value <= expected['value_range'][1]:
            score += 20
        
        decomp = response.get('decomposition', [])
        if len(decomp) >= expected['min_decomposition_steps']:
            score += 25
        
        if 'method' in response:
            score += 10
        if 'reasoning' in response:
            score += 10
        if 'confidence_range' in response:
            score += 10
    
    return min(score, 100)


def run_comprehensive_test():
    """전체 테스트 실행"""
    print("=" * 120)
    print("GPT-5/5.1 Phase 0-4 고난이도 테스트")
    print("=" * 120)
    print()
    
    client = OpenAI()
    
    # 테스트 구성
    test_configs = [
        # Chat API 모델
        ('gpt-4.1-nano', 'chat', None),
        ('gpt-4o-mini', 'chat', None),
        ('gpt-4.1-mini', 'chat', None),
        
        # Responses API - 최적 구성
        ('gpt-5.1', 'responses', {
            'reasoning': {'effort': 'medium'},
            'text': {'verbosity': 'low'}
        }),
        
        # Chat API - reasoning effort
        ('gpt-5.1', 'chat', {'reasoning_effort': 'medium'}),
    ]
    
    results = []
    
    # Phase별 테스트
    for phase_id, scenario in PHASE_SCENARIOS.items():
        print(f"\n{'='*120}")
        print(f"🔬 {scenario['name']} (난이도: {scenario['difficulty']})")
        print(f"{'='*120}")
        print(f"📝 {scenario['description']}")
        print()
        
        phase_results = []
        
        for model, api_type, config in test_configs:
            config_name = f"{model} ({api_type})"
            print(f"  테스트: {config_name}")
            
            result = test_model_on_phase(client, model, api_type, phase_id, scenario, config)
            
            result['model'] = model
            result['api_type'] = api_type
            result['phase'] = phase_id
            result['config_name'] = config_name
            
            phase_results.append(result)
            
            if result['success']:
                print(f"    ✅ 성공: 품질 {result['quality_score']}/100, 비용 ${result['cost']:.6f}, 시간 {result['elapsed_seconds']}초")
            else:
                print(f"    ❌ 실패: {result['error'][:50]}")
            
            time.sleep(2)
        
        results.extend(phase_results)
        
        # Phase별 요약
        success_results = [r for r in phase_results if r['success']]
        if success_results:
            print(f"\n  📊 {phase_id} 요약:")
            print(f"  {'모델':<20} | {'품질':<8} | {'비용':<12} | {'시간'}")
            print(f"  {'-'*60}")
            
            for r in sorted(success_results, key=lambda x: x['quality_score'], reverse=True):
                marker = "🏆" if r['quality_score'] >= 90 else "⭐" if r['quality_score'] >= 70 else "  "
                print(f"  {marker}{r['config_name']:<18} | {r['quality_score']:>6}/100 | ${r['cost']:<11.6f} | {r['elapsed_seconds']}초")
    
    # 전체 분석
    print(f"\n{'='*120}")
    print("📊 전체 결과 분석")
    print(f"{'='*120}\n")
    
    success_results = [r for r in results if r['success']]
    
    # 모델별 평균 성능
    from collections import defaultdict
    
    by_model = defaultdict(list)
    for r in success_results:
        by_model[r['config_name']].append(r)
    
    print("🏆 모델별 종합 성능 (Phase 0-4 평균)\n")
    print(f"{'순위':<4} | {'모델':<25} | {'평균 품질':<10} | {'평균 비용':<12} | {'평균 시간':<10} | {'합계'}")
    print("-" * 120)
    
    model_stats = []
    for model_name, model_results in by_model.items():
        avg_quality = sum(r['quality_score'] for r in model_results) / len(model_results)
        avg_cost = sum(r['cost'] for r in model_results) / len(model_results)
        avg_time = sum(r['elapsed_seconds'] for r in model_results) / len(model_results)
        total_cost = sum(r['cost'] for r in model_results)
        
        model_stats.append({
            'name': model_name,
            'avg_quality': avg_quality,
            'avg_cost': avg_cost,
            'avg_time': avg_time,
            'total_cost': total_cost,
            'count': len(model_results)
        })
    
    model_stats.sort(key=lambda x: x['avg_quality'], reverse=True)
    
    for i, stat in enumerate(model_stats, 1):
        marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{marker}{i:<3} | {stat['name']:<25} | {stat['avg_quality']:>8.1f}/100 | ${stat['avg_cost']:<11.6f} | {stat['avg_time']:>8.2f}초 | ${stat['total_cost']:.6f}")
    
    # Phase별 최고 성능 모델
    print(f"\n\n🎯 Phase별 최고 성능 모델\n")
    
    for phase_id, scenario in PHASE_SCENARIOS.items():
        phase_results = [r for r in success_results if r['phase'] == phase_id]
        if phase_results:
            best = max(phase_results, key=lambda x: x['quality_score'])
            print(f"{scenario['name']}")
            print(f"  🏆 {best['config_name']}: {best['quality_score']}/100 (비용: ${best['cost']:.6f}, 시간: {best['elapsed_seconds']}초)")
    
    # 저장
    output_file = f"benchmark_phase_0_4_advanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'phase_0_4_advanced',
                'total_tests': len(results),
                'success_count': len(success_results),
                'phases': list(PHASE_SCENARIOS.keys())
            },
            'scenarios': PHASE_SCENARIOS,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ 결과 저장: {output_file}")
    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    run_comprehensive_test()


