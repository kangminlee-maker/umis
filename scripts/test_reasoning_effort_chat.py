#!/usr/bin/env python3
"""
GPT-5 reasoning_effort 옵션 테스트 (Chat API)
동일 모델에 다양한 reasoning_effort 적용
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def test_reasoning_effort_chat_api():
    """Chat API에서 reasoning_effort 옵션별 테스트"""
    print("=" * 80)
    print("GPT-5 reasoning_effort 옵션 테스트 (Chat API)")
    print("=" * 80)
    print()
    
    client = OpenAI()
    
    # 테스트 구성
    test_configs = [
        # GPT-5 시리즈 (reasoning 모델)
        ('gpt-5', 'low'),
        ('gpt-5', 'medium'),
        ('gpt-5', 'high'),
        ('gpt-5.1', 'low'),
        ('gpt-5.1', 'medium'),
        ('gpt-5.1', 'high'),
        # O 시리즈도 테스트
        ('o1', 'low'),
        ('o1', 'medium'),
        ('o1', 'high'),
    ]
    
    # Phase 0 프롬프트
    prompt = '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

요구사항: B2B SaaS 값만 추출, confidence는 1.0으로 설정

⚠️ 중요: 반드시 순수 JSON 형식으로만 응답하세요.'''
    
    print(f"📋 테스트 구성: {len(test_configs)}개")
    print("   모델: gpt-5, gpt-5.1, o1")
    print("   reasoning_effort: low, medium, high")
    print()
    
    results = []
    
    for model, effort in test_configs:
        config_name = f"{model} (effort={effort})"
        print(f"테스트: {config_name}")
        
        try:
            start = time.time()
            
            # Chat API 호출 (reasoning 모델은 system 메시지 없음)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                reasoning_effort=effort
            )
            
            elapsed = time.time() - start
            content = response.choices[0].message.content
            
            # JSON 파싱
            import json
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
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            # 토큰 및 비용
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
            
            # 가격 정보 ($/1M 토큰)
            pricing = {
                'gpt-5': {'input': 1.25, 'output': 10.00},
                'gpt-5.1': {'input': 1.25, 'output': 10.00},
                'o1': {'input': 15.00, 'output': 60.00}
            }
            
            rates = pricing.get(model, {'input': 0, 'output': 0})
            cost = (tokens['input'] / 1_000_000 * rates['input'] + 
                   tokens['output'] / 1_000_000 * rates['output'])
            
            # 품질 평가
            has_value = 'value' in parsed
            correct_value = parsed.get('value') == 200000 if has_value else False
            has_confidence = 'confidence' in parsed
            correct_confidence = parsed.get('confidence') == 1.0 if has_confidence else False
            json_valid = 'parse_error' not in parsed
            
            quality = 0
            if json_valid: quality += 25
            if has_value: quality += 25
            if has_confidence: quality += 20
            if correct_value: quality += 20
            if correct_confidence: quality += 10
            
            result = {
                'model': model,
                'reasoning_effort': effort,
                'config_name': config_name,
                'cost': cost,
                'elapsed_seconds': elapsed,
                'quality_score': quality,
                'tokens': tokens,
                'response': parsed,
                'success': True
            }
            
            results.append(result)
            
            print(f"   ✅ 성공!")
            print(f"      비용: ${cost:.6f}")
            print(f"      시간: {elapsed:.2f}초")
            print(f"      품질: {quality}/100")
            if 'reasoning' in tokens:
                print(f"      Reasoning 토큰: {tokens['reasoning']}")
            
            time.sleep(2)
        
        except Exception as e:
            print(f"   ❌ 오류: {str(e)[:100]}")
            results.append({
                'model': model,
                'reasoning_effort': effort,
                'config_name': config_name,
                'error': str(e),
                'success': False
            })
            time.sleep(2)
        
        print()
    
    # 결과 분석
    print("=" * 80)
    print("📊 결과 분석")
    print("=" * 80)
    print()
    
    success = [r for r in results if r.get('success', False)]
    
    if success:
        print(f"총 테스트: {len(results)}개")
        print(f"성공: {len(success)}개")
        print()
        
        # 모델별 그룹화
        from collections import defaultdict
        
        by_model = defaultdict(list)
        for r in success:
            by_model[r['model']].append(r)
        
        for model in ['gpt-5', 'gpt-5.1', 'o1']:
            if model not in by_model:
                continue
            
            print(f"{'='*80}")
            print(f"{model} - reasoning_effort별 비교")
            print(f"{'='*80}")
            print()
            
            model_results = by_model[model]
            
            print(f"{'effort':<10} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비':<10} | {'토큰'}")
            print("-" * 85)
            
            for r in sorted(model_results, key=lambda x: ['low', 'medium', 'high'].index(x['reasoning_effort'])):
                effort = r['reasoning_effort']
                cost = r['cost']
                time_val = r['elapsed_seconds']
                quality = r['quality_score']
                efficiency = quality / (cost * 1000) if cost > 0 else 0
                total_tokens = r['tokens']['total']
                reasoning_tokens = r['tokens'].get('reasoning', 0)
                
                token_info = f"{total_tokens} (R:{reasoning_tokens})" if reasoning_tokens > 0 else str(total_tokens)
                
                print(f"{effort:<10} | ${cost:<11.6f} | {time_val:<9.2f}초 | {quality:>6}/100 | {efficiency:>8.1f} | {token_info}")
            
            print()
            
            # 최적 옵션 추천
            best_efficiency = max(model_results, key=lambda r: r['quality_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0)
            best_quality = max(model_results, key=lambda r: r['quality_score'])
            fastest = min(model_results, key=lambda r: r['elapsed_seconds'])
            cheapest = min(model_results, key=lambda r: r['cost'])
            
            print(f"💡 {model} 권장 옵션:")
            print(f"   - 최고 가성비: {best_efficiency['reasoning_effort']} (가성비 {best_efficiency['quality_score'] / (best_efficiency['cost'] * 1000):.1f})")
            print(f"   - 최고 품질: {best_quality['reasoning_effort']} ({best_quality['quality_score']}/100)")
            print(f"   - 가장 빠름: {fastest['reasoning_effort']} ({fastest['elapsed_seconds']:.2f}초)")
            print(f"   - 가장 저렴: {cheapest['reasoning_effort']} (${cheapest['cost']:.6f})")
            print()
    
    # 저장
    import json
    from datetime import datetime
    
    output_file = f"benchmark_reasoning_effort_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'reasoning_effort_comparison',
                'api': 'chat_completions'
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장: {output_file}")
    print()
    print("🎉 테스트 완료!")


if __name__ == "__main__":
    test_reasoning_effort_chat_api()


