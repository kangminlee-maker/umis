#!/usr/bin/env python3
"""
GPT-5 reasoning effort 옵션 테스트 (올바른 Responses API 사용법)
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


def test_gpt5_reasoning_options():
    """GPT-5 reasoning effort 옵션 전체 테스트"""
    print("=" * 100)
    print("GPT-5 reasoning effort 옵션 종합 테스트")
    print("=" * 100)
    print()
    
    client = OpenAI()
    
    # 테스트 구성: (모델, API, reasoning_effort, verbosity)
    test_configs = [
        # GPT-5.1 (Responses API) - 전체 옵션
        ('gpt-5.1', 'responses', 'none', 'low'),
        ('gpt-5.1', 'responses', 'none', 'medium'),
        ('gpt-5.1', 'responses', 'none', 'high'),
        ('gpt-5.1', 'responses', 'low', 'low'),
        ('gpt-5.1', 'responses', 'low', 'medium'),
        ('gpt-5.1', 'responses', 'medium', 'low'),
        ('gpt-5.1', 'responses', 'high', 'low'),
        
        # GPT-5 (Responses API)
        ('gpt-5', 'responses', 'low', 'low'),
        ('gpt-5', 'responses', 'medium', 'low'),
        ('gpt-5', 'responses', 'high', 'low'),
        
        # GPT-5.1 (Chat API) - 비교용
        ('gpt-5.1', 'chat', 'none', None),
        ('gpt-5.1', 'chat', 'low', None),
        ('gpt-5.1', 'chat', 'medium', None),
        ('gpt-5.1', 'chat', 'high', None),
    ]
    
    # Phase 0 프롬프트
    prompt = '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

요구사항: B2B SaaS 값만 추출, confidence는 1.0으로 설정

반드시 다음 JSON 형식으로만 응답하세요:
{"value": 200000, "unit": "원", "confidence": 1.0}'''
    
    print(f"📋 테스트 구성: {len(test_configs)}개")
    print("   모델: gpt-5, gpt-5.1")
    print("   API: Responses, Chat")
    print("   reasoning effort: none, low, medium, high")
    print("   verbosity: low, medium, high")
    print()
    
    results = []
    
    for model, api_type, effort, verbosity in test_configs:
        if api_type == 'responses':
            config_name = f"{model} (Responses, effort={effort}, verb={verbosity})"
        else:
            config_name = f"{model} (Chat, effort={effort})"
        
        print(f"테스트: {config_name}")
        
        try:
            start = time.time()
            
            if api_type == 'responses':
                # Responses API - 올바른 파라미터 구조
                api_params = {
                    "model": model,
                    "input": prompt,
                    "reasoning": {"effort": effort},
                    "text": {"verbosity": verbosity}
                }
                
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
                    'input': getattr(response, 'input_tokens', 0),
                    'output': getattr(response, 'output_tokens', 0),
                }
                
                if tokens['input'] == 0:
                    tokens['input'] = len(prompt) // 4
                    tokens['output'] = len(content) // 4
                
                tokens['total'] = tokens['input'] + tokens['output']
                
            else:
                # Chat API
                api_params = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "reasoning_effort": effort
                }
                
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
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            # 비용 계산
            pricing = {
                'gpt-5': {'input': 1.25, 'output': 10.00},
                'gpt-5.1': {'input': 1.25, 'output': 10.00}
            }
            
            rates = pricing.get(model, {'input': 0, 'output': 0})
            cost = (tokens['input'] / 1_000_000 * rates['input'] + 
                   tokens['output'] / 1_000_000 * rates['output'])
            
            # 품질 평가
            has_value = 'value' in parsed
            correct_value = parsed.get('value') == 200000 if has_value else False
            has_confidence = 'confidence' in parsed
            correct_confidence = parsed.get('confidence') in [1.0, 1] if has_confidence else False
            json_valid = 'parse_error' not in parsed
            
            quality = 0
            if json_valid: quality += 25
            if has_value: quality += 25
            if has_confidence: quality += 20
            if correct_value: quality += 20
            if correct_confidence: quality += 10
            
            result = {
                'model': model,
                'api_type': api_type,
                'reasoning_effort': effort,
                'verbosity': verbosity,
                'config_name': config_name,
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
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
                'api_type': api_type,
                'reasoning_effort': effort,
                'verbosity': verbosity,
                'config_name': config_name,
                'error': str(e),
                'success': False
            })
            time.sleep(2)
        
        print()
    
    # 결과 분석
    print("=" * 100)
    print("📊 결과 분석")
    print("=" * 100)
    print()
    
    success = [r for r in results if r.get('success', False)]
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개")
    print(f"실패: {len(results) - len(success)}개")
    print()
    
    if success:
        # 모델별 그룹화
        from collections import defaultdict
        
        # API별로 분리
        by_api = defaultdict(list)
        for r in success:
            key = f"{r['model']} ({r['api_type']})"
            by_api[key].append(r)
        
        for group_key in sorted(by_api.keys()):
            group_results = by_api[group_key]
            
            print(f"{'='*100}")
            print(f"{group_key}")
            print(f"{'='*100}")
            print()
            
            print(f"{'effort':<10} | {'verbosity':<10} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비':<10} | {'토큰'}")
            print("-" * 100)
            
            for r in sorted(group_results, key=lambda x: (x['reasoning_effort'], x.get('verbosity', '') or '')):
                effort = r['reasoning_effort']
                verb = r.get('verbosity') or 'N/A'
                cost = r['cost']
                time_val = r['elapsed_seconds']
                quality = r['quality_score']
                efficiency = quality / (cost * 1000) if cost > 0 else 0
                
                token_info = f"{r['tokens']['total']}"
                if 'reasoning' in r['tokens']:
                    token_info += f" (R:{r['tokens']['reasoning']})"
                
                marker = "⭐" if quality == 100 else "  "
                
                print(f"{marker}{effort:<9} | {verb:<10} | ${cost:<11.6f} | {time_val:<9.2f}초 | {quality:>6}/100 | {efficiency:>8.1f} | {token_info}")
            
            print()
            
            # 100점 모델 찾기
            perfect = [r for r in group_results if r['quality_score'] == 100]
            if perfect:
                best = min(perfect, key=lambda r: r['cost'])
                print(f"💎 100점 최적 구성:")
                print(f"   - effort={best['reasoning_effort']}, verbosity={best.get('verbosity', 'N/A')}")
                print(f"   - 비용: ${best['cost']:.6f}, 시간: {best['elapsed_seconds']:.2f}초")
                print()
    
    # 100점 모델 종합 비교
    perfect_all = [r for r in success if r['quality_score'] == 100]
    
    if perfect_all:
        print("=" * 100)
        print("🏆 품질 100점 달성 구성 전체 비교")
        print("=" * 100)
        print()
        
        perfect_all.sort(key=lambda r: r['cost'])
        
        print(f"{'순위':<4} | {'구성':<50} | {'비용':<12} | {'시간':<10} | {'가성비'}")
        print("-" * 100)
        
        for i, r in enumerate(perfect_all, 1):
            efficiency = 100 / (r['cost'] * 1000)
            marker = "⭐" if i <= 3 else "  "
            print(f"{marker}{i:<3} | {r['config_name']:<50} | ${r['cost']:<11.6f} | {r['elapsed_seconds']:<9.2f}초 | {efficiency:>8.1f}")
    
    # 저장
    output_file = f"benchmark_reasoning_effort_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'reasoning_effort_comparison',
                'total_tests': len(results),
                'success_count': len(success)
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ 결과 저장: {output_file}")
    print()
    print("🎉 테스트 완료!")


if __name__ == "__main__":
    test_gpt5_reasoning_options()

