#!/usr/bin/env python3
"""
테스트되지 않은 모델 테스트
- o1-2024-12-17
- o1-pro-2025-03-19  
- o3-2025-04-16
- o3-mini-2025-01-31
- o4-mini-2025-04-16
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_test_scenario():
    """Phase 0 간단한 테스트 시나리오"""
    return {
        'id': 'phase0_literal',
        'phase': 0,
        'name': 'Phase 0: Literal (데이터 추출)',
        'prompt': '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

요구사항: B2B SaaS 값만 추출, confidence는 1.0으로 설정

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 1.0
}''',
        'expected': {'value': 200000, 'confidence': 1.0}
    }


def test_model(client, model_name, scenario):
    """단일 모델 테스트"""
    
    print(f"\n테스트: {model_name}")
    print("-" * 80)
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": scenario['prompt']}
            ]
        )
        
        elapsed = time.time() - start_time
        
        # 응답 파싱
        content = response.choices[0].message.content
        
        # JSON 추출
        try:
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            
            parsed = json.loads(content)
        except:
            parsed = {'raw': content, 'parse_error': True}
        
        # 비용 계산
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        
        # 모델별 가격 ($/1M 토큰)
        pricing = {
            'o1-2024-12-17': {'input': 15.00, 'output': 60.00},
            'o1-pro-2025-03-19': {'input': 150.00, 'output': 600.00},
            'o3-2025-04-16': {'input': 2.00, 'output': 8.00},
            'o3-mini-2025-01-31': {'input': 1.10, 'output': 4.40},
            'o4-mini-2025-04-16': {'input': 1.10, 'output': 4.40}
        }
        
        if model_name in pricing:
            cost = (input_tokens * pricing[model_name]['input'] / 1_000_000) + \
                   (output_tokens * pricing[model_name]['output'] / 1_000_000)
        else:
            cost = 0
        
        # 품질 평가
        quality = evaluate_quality(scenario, parsed)
        
        result = {
            'model': model_name,
            'success': True,
            'response': parsed,
            'quality_score': quality,
            'cost': cost,
            'time': elapsed,
            'tokens': {
                'input': input_tokens,
                'output': output_tokens,
                'total': input_tokens + output_tokens
            }
        }
        
        print(f"✅ 성공")
        print(f"   응답 시간: {elapsed:.2f}초")
        print(f"   토큰: {input_tokens} 입력 + {output_tokens} 출력 = {input_tokens + output_tokens} 총")
        print(f"   비용: ${cost:.6f}")
        print(f"   품질: {quality['total_score']}/100")
        if 'value' in parsed:
            print(f"   추정값: {parsed.get('value', 'N/A')}{parsed.get('unit', '')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        
        return {
            'model': model_name,
            'success': False,
            'error': str(e),
            'quality_score': {'total_score': 0}
        }


def evaluate_quality(scenario, parsed):
    """품질 평가"""
    
    score = {
        'json_parse': 0,
        'has_value': 0,
        'has_confidence': 0,
        'value_accuracy': 0,
        'confidence_accuracy': 0,
        'total_score': 0
    }
    
    # JSON 파싱 (25점)
    if 'parse_error' not in parsed:
        score['json_parse'] = 25
    
    # value 존재 (25점)
    if 'value' in parsed:
        score['has_value'] = 25
    
    # confidence 존재 (20점)
    if 'confidence' in parsed:
        score['has_confidence'] = 20
    
    # value 정확도 (20점)
    if 'value' in parsed and parsed['value'] == scenario['expected']['value']:
        score['value_accuracy'] = 20
    
    # confidence 정확도 (10점)
    if 'confidence' in parsed and parsed['confidence'] == scenario['expected']['confidence']:
        score['confidence_accuracy'] = 10
    
    score['total_score'] = sum(v for k, v in score.items() if k != 'total_score')
    
    return score


def main():
    """메인 실행"""
    
    client = OpenAI()
    scenario = get_test_scenario()
    
    # 테스트할 모델들
    models = [
        'o1-2024-12-17',
        'o1-pro-2025-03-19',
        'o3-2025-04-16',
        'o3-mini-2025-01-31',
        'o4-mini-2025-04-16'
    ]
    
    print("=" * 80)
    print("테스트되지 않은 모델 테스트 (Phase 0)")
    print("=" * 80)
    
    results = []
    total_cost = 0
    total_time = 0
    
    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] {model}")
        
        result = test_model(client, model, scenario)
        results.append(result)
        
        if result['success']:
            total_cost += result['cost']
            total_time += result['time']
        
        # Rate limiting
        if i < len(models):
            time.sleep(3)
    
    # 요약
    print("\n" + "=" * 80)
    print("테스트 완료 요약")
    print("=" * 80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"성공: {len(successful)}개")
    print(f"실패: {len(failed)}개")
    
    if successful:
        print(f"\n총 비용: ${total_cost:.6f}")
        print(f"총 시간: {total_time:.2f}초")
        
        print("\n모델별 결과:")
        for r in successful:
            print(f"  {r['model']:30} | 품질: {r['quality_score']['total_score']:3d}/100 | "
                  f"시간: {r['time']:5.2f}초 | 비용: ${r['cost']:.6f}")
    
    if failed:
        print("\n실패한 모델:")
        for r in failed:
            print(f"  {r['model']:30} | 에러: {r['error'][:60]}")
    
    # 결과 저장
    output = {
        'timestamp': datetime.now().isoformat(),
        'scenario': scenario['name'],
        'summary': {
            'total_tests': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_cost': total_cost,
            'total_time': total_time
        },
        'results': results
    }
    
    filename = f"benchmark_untested_models_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n결과 저장: {filename}")
    
    return output


if __name__ == '__main__':
    main()
