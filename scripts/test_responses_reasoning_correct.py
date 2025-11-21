#!/usr/bin/env python3
"""
GPT-5 reasoning effort 옵션 테스트 (올바른 방법)
Responses API: reasoning={"effort": "..."} 형태 사용
Chat API: reasoning_effort="..." 형태 사용
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


def test_responses_api_reasoning_efforts():
    """Responses API - reasoning effort 옵션 테스트"""
    print("=" * 90)
    print("Responses API - reasoning effort 옵션 테스트")
    print("=" * 90)
    print()
    
    client = OpenAI()
    
    # 테스트 구성: (모델, effort, verbosity)
    test_configs = [
        # GPT-5.1 전체 조합
        ('gpt-5.1', 'none', 'low'),
        ('gpt-5.1', 'none', 'medium'),
        ('gpt-5.1', 'low', 'low'),
        ('gpt-5.1', 'low', 'medium'),
        ('gpt-5.1', 'medium', 'low'),
        ('gpt-5.1', 'medium', 'medium'),
        ('gpt-5.1', 'high', 'low'),
        ('gpt-5.1', 'high', 'medium'),
        
        # GPT-5 비교
        ('gpt-5', 'low', 'low'),
        ('gpt-5', 'medium', 'low'),
        
        # GPT-5-mini, nano
        ('gpt-5-mini', 'none', 'low'),
        ('gpt-5-mini', 'low', 'low'),
        ('gpt-5-nano', 'none', 'low'),
        ('gpt-5-nano', 'low', 'low'),
    ]
    
    prompt_text = '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

요구사항: 순수 JSON 형식으로만 응답하세요.
{"value": 숫자, "unit": "원", "confidence": 1.0}'''
    
    print(f"📋 테스트 구성: {len(test_configs)}개")
    print("   모델: gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano")
    print("   reasoning effort: none, low, medium, high")
    print("   verbosity: low, medium")
    print()
    
    results = []
    
    for model, effort, verbosity in test_configs:
        config_name = f"{model} (effort={effort}, verb={verbosity})"
        print(f"테스트: {config_name}")
        
        try:
            start = time.time()
            
            # Responses API 호출 (올바른 형태)
            response = client.responses.create(
                model=model,
                input=prompt_text,
                reasoning={"effort": effort},  # ← Dict 형태!
                text={"verbosity": verbosity}  # ← Dict 형태!
            )
            
            elapsed = time.time() - start
            
            # 응답 추출
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output'):
                content = response.output
            else:
                content = str(response)
            
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
                parsed = {'raw': content[:100], 'parse_error': True}
            
            # 토큰 정보
            tokens = {
                'input': getattr(response, 'input_tokens', 0),
                'output': getattr(response, 'output_tokens', 0),
            }
            
            # 토큰이 0이면 추정
            if tokens['input'] == 0:
                tokens['input'] = len(prompt_text) // 4
                tokens['output'] = len(content) // 4
            
            tokens['total'] = tokens['input'] + tokens['output']
            
            # 비용 계산
            pricing = {
                'gpt-5': {'input': 1.25, 'output': 10.00},
                'gpt-5.1': {'input': 1.25, 'output': 10.00},
                'gpt-5-mini': {'input': 0.25, 'output': 2.00},
                'gpt-5-nano': {'input': 0.05, 'output': 0.40}
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
                'verbosity': verbosity,
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
            print(f"      비용: ${cost:.6f} | 시간: {elapsed:.2f}초 | 품질: {quality}/100")
            
            time.sleep(2)
        
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 오류: {error_msg[:100]}")
            
            results.append({
                'model': model,
                'reasoning_effort': effort,
                'verbosity': verbosity,
                'config_name': config_name,
                'error': error_msg,
                'success': False
            })
            
            time.sleep(2)
        
        print()
    
    # 결과 분석
    analyze_results(results)
    
    # 저장
    output_file = f"benchmark_responses_reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'responses_api_reasoning_effort',
                'api': 'responses'
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장: {output_file}")
    print()
    print("🎉 테스트 완료!")


def analyze_results(results):
    """결과 분석"""
    print("=" * 90)
    print("📊 결과 분석")
    print("=" * 90)
    print()
    
    success = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개")
    print(f"실패: {len(failed)}개")
    print()
    
    if not success:
        print("❌ 성공한 테스트가 없습니다.")
        return
    
    # 모델별 그룹화
    from collections import defaultdict
    
    by_model = defaultdict(list)
    for r in success:
        by_model[r['model']].append(r)
    
    # 각 모델별 분석
    for model in sorted(by_model.keys()):
        model_results = by_model[model]
        
        print(f"{'='*90}")
        print(f"{model} - reasoning effort & verbosity 비교")
        print(f"{'='*90}")
        print()
        
        print(f"{'effort':<8} | {'verb':<8} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비':<10}")
        print("-" * 80)
        
        for r in sorted(model_results, 
                       key=lambda x: (['none', 'low', 'medium', 'high'].index(x['reasoning_effort']), 
                                     ['low', 'medium', 'high'].index(x['verbosity']))):
            effort = r['reasoning_effort']
            verb = r['verbosity']
            cost = r['cost']
            time_val = r['elapsed_seconds']
            quality = r['quality_score']
            efficiency = quality / (cost * 1000) if cost > 0 else 0
            
            marker = "⭐" if quality == 100 else "  "
            
            print(f"{marker}{effort:<8} | {verb:<8} | ${cost:<11.6f} | {time_val:<9.2f}초 | {quality:>6}/100 | {efficiency:>8.1f}")
        
        print()
        
        # 최적 옵션 찾기
        perfect = [r for r in model_results if r['quality_score'] == 100]
        
        if perfect:
            best = min(perfect, key=lambda r: r['cost'])
            print(f"💡 {model} 최적 옵션:")
            print(f"   ⭐ effort={best['reasoning_effort']}, verbosity={best['verbosity']}")
            print(f"      비용: ${best['cost']:.6f} | 시간: {best['elapsed_seconds']:.2f}초 | 품질: 100/100")
        else:
            best = max(model_results, key=lambda r: r['quality_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0)
            print(f"💡 {model} 최고 가성비:")
            print(f"   • effort={best['reasoning_effort']}, verbosity={best['verbosity']}")
            print(f"      비용: ${best['cost']:.6f} | 시간: {best['elapsed_seconds']:.2f}초 | 품질: {best['quality_score']}/100")
        
        print()


if __name__ == "__main__":
    test_responses_api_reasoning_efforts()

