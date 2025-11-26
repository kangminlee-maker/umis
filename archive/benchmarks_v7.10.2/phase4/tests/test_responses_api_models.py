#!/usr/bin/env python3
"""
Responses API 전용 모델 테스트
- o1-pro
- o1-pro-2025-03-19

중요: o1-mini는 2025년 4월에 deprecated, 10월 27일 shutdown됨!
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def test_responses_api_model(client, model_name):
    """Responses API 모델 테스트"""
    
    print(f"\n테스트: {model_name}")
    print("-" * 80)
    
    try:
        start_time = time.time()
        
        # Responses API 사용
        response = client.responses.create(
            model=model_name,
            input='''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

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
            reasoning={"effort": "low"},  # Phase 0는 낮은 추론 필요
            background=False  # 동기 처리
        )
        
        elapsed = time.time() - start_time
        
        # 응답 파싱
        content = response.output_text
        
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
        
        # Usage 정보 (Responses API는 다를 수 있음)
        usage_info = {}
        if hasattr(response, 'usage'):
            usage_info = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'reasoning_tokens': getattr(response.usage, 'reasoning_tokens', 0),
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            # 비용 계산 (o1-pro: $150/$600)
            cost = (usage_info['input_tokens'] * 150.00 / 1_000_000) + \
                   (usage_info['output_tokens'] * 600.00 / 1_000_000)
        else:
            # Usage 정보 없으면 추정
            usage_info = {
                'input_tokens': 0,
                'output_tokens': 0,
                'reasoning_tokens': 0,
                'total_tokens': 0
            }
            cost = 0
        
        # 품질 평가
        quality = evaluate_quality(parsed)
        
        result = {
            'model': model_name,
            'api_type': 'responses',
            'success': True,
            'response': parsed,
            'quality_score': quality,
            'cost': cost,
            'time': elapsed,
            'tokens': usage_info
        }
        
        print(f"✅ Responses API 성공")
        print(f"   응답 시간: {elapsed:.2f}초")
        if usage_info['total_tokens'] > 0:
            print(f"   토큰: {usage_info['input_tokens']} 입력 + "
                  f"{usage_info['output_tokens']} 출력 = "
                  f"{usage_info['total_tokens']} 총")
            if usage_info['reasoning_tokens'] > 0:
                print(f"   Reasoning: {usage_info['reasoning_tokens']} 토큰")
            print(f"   비용: ${cost:.6f}")
        print(f"   품질: {quality['total_score']}/100")
        if 'value' in parsed:
            print(f"   추정값: {parsed.get('value', 'N/A')}{parsed.get('unit', '')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        
        return {
            'model': model_name,
            'api_type': 'responses',
            'success': False,
            'error': str(e),
            'quality_score': {'total_score': 0}
        }


def evaluate_quality(parsed):
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
    if 'value' in parsed and parsed['value'] == 200000:
        score['value_accuracy'] = 20
    
    # confidence 정확도 (10점)
    if 'confidence' in parsed and parsed['confidence'] == 1.0:
        score['confidence_accuracy'] = 10
    
    score['total_score'] = sum(v for k, v in score.items() if k != 'total_score')
    
    return score


def main():
    """메인 실행"""
    
    client = OpenAI()
    
    print("=" * 80)
    print("Responses API 전용 모델 테스트 (Phase 0)")
    print("=" * 80)
    print()
    print("ℹ️  참고: o1-mini는 2025년 4월 deprecated, 10월 27일 shutdown")
    print("         o4-mini로 대체되었습니다.")
    print()
    
    # 테스트할 모델들
    models = [
        'o1-pro',           # 기본 o1-pro
        'o1-pro-2025-03-19', # 버전 특화
    ]
    
    results = []
    total_cost = 0
    total_time = 0
    
    for i, model in enumerate(models, 1):
        print(f"[{i}/{len(models)}] {model}")
        
        result = test_responses_api_model(client, model)
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
    
    # o1-mini 관련 안내
    print("\n" + "=" * 80)
    print("⚠️  o1-mini 상태")
    print("=" * 80)
    print("""
o1-mini는 2025년 4월에 deprecated되고, 10월 27일에 완전히 shutdown되었습니다.

대체 모델:
  1. o4-mini ⭐⭐⭐⭐⭐ (권장)
     - 가격: $1.10/$4.40 (o1-mini와 동일)
     - 성능: 향상됨
     - Phase 0 테스트: 1.66초, 100/100 품질
  
  2. o3-mini ⭐⭐⭐⭐⭐ (권장)
     - 가격: $1.10/$4.40 (동일)
     - Phase 0 테스트: 2.90초, 100/100 품질
     - 안정적

권장 사항:
  - o1-mini 대신 o4-mini 또는 o3-mini 사용
  - UMIS Phase 4에는 o3-mini-2025-01-31 권장 ($0.87/1,000회)
    """)
    
    # 결과 저장
    output = {
        'timestamp': datetime.now().isoformat(),
        'api_type': 'responses',
        'summary': {
            'total_tests': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_cost': total_cost,
            'total_time': total_time
        },
        'results': results
    }
    
    filename = f"benchmark_responses_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n결과 저장: {filename}")
    
    return output


if __name__ == '__main__':
    main()
