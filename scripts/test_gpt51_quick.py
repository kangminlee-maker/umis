#!/usr/bin/env python3
"""
GPT-5.1 핵심 옵션만 빠르게 테스트
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


def quick_test_gpt51():
    """GPT-5.1 핵심 옵션만 빠른 테스트"""
    print("=" * 80)
    print("GPT-5.1 핵심 옵션 빠른 테스트")
    print("=" * 80)
    print()
    
    client = OpenAI()
    
    # 핵심 구성만: (API, reasoning_effort, verbosity)
    test_configs = [
        ('responses', 'none', 'low'),
        ('responses', 'low', 'low'),
        ('responses', 'medium', 'low'),
        ('responses', 'high', 'low'),
    ]
    
    prompt = '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

JSON 형식: {"value": 200000, "unit": "원", "confidence": 1.0}'''
    
    print(f"📋 테스트: gpt-5.1 (Responses API)")
    print(f"   구성: {len(test_configs)}개 (effort × verbosity)")
    print(f"   예상 시간: ~30초")
    print()
    
    results = []
    
    for api_type, effort, verbosity in test_configs:
        config_name = f"gpt-5.1 (effort={effort}, verb={verbosity})"
        print(f"테스트: {config_name}")
        
        try:
            start = time.time()
            
            response = client.responses.create(
                model='gpt-5.1',
                input=prompt,
                reasoning={"effort": effort},
                text={"verbosity": verbosity}
            )
            
            elapsed = time.time() - start
            
            # 응답 추출
            if hasattr(response, 'output_text'):
                content = response.output_text
            else:
                content = str(response)
            
            # JSON 파싱
            import re
            try:
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                parsed = json.loads(content)
            except:
                parsed = {'raw': content[:100], 'parse_error': True}
            
            # 토큰 추정
            tokens = {
                'input': len(prompt) // 4,
                'output': len(str(content)) // 4
            }
            tokens['total'] = tokens['input'] + tokens['output']
            
            # 비용
            cost = (tokens['input'] / 1_000_000 * 1.25 + 
                   tokens['output'] / 1_000_000 * 10.00)
            
            # 품질
            quality = 0
            if 'parse_error' not in parsed: quality += 25
            if 'value' in parsed: quality += 25
            if 'confidence' in parsed: quality += 20
            if parsed.get('value') == 200000: quality += 20
            if parsed.get('confidence') in [1.0, 1]: quality += 10
            
            result = {
                'api_type': api_type,
                'reasoning_effort': effort,
                'verbosity': verbosity,
                'config_name': config_name,
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'quality_score': quality,
                'tokens': tokens,
                'success': True
            }
            
            results.append(result)
            
            print(f"   ✅ ${cost:.6f} | {elapsed:.2f}초 | 품질: {quality}/100")
            time.sleep(1.5)
        
        except Exception as e:
            print(f"   ❌ {str(e)[:80]}")
            results.append({
                'reasoning_effort': effort,
                'verbosity': verbosity,
                'error': str(e),
                'success': False
            })
            time.sleep(1.5)
    
    # 결과
    print()
    print("=" * 80)
    print("📊 결과")
    print("=" * 80)
    print()
    
    success = [r for r in results if r.get('success', False)]
    
    if success:
        success.sort(key=lambda r: r['cost'])
        
        print(f"{'effort':<10} | {'verbosity':<10} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비'}")
        print("-" * 80)
        
        for r in success:
            efficiency = r['quality_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0
            marker = "⭐" if r['quality_score'] == 100 else "  "
            print(f"{marker}{r['reasoning_effort']:<9} | {r['verbosity']:<10} | ${r['cost']:<11.6f} | "
                  f"{r['elapsed_seconds']:<9.2f}초 | {r['quality_score']:>6}/100 | {efficiency:>8.1f}")
        
        # 100점 모델
        perfect = [r for r in success if r['quality_score'] == 100]
        if perfect:
            best = min(perfect, key=lambda r: r['cost'])
            print()
            print(f"💎 100점 최적 구성: effort={best['reasoning_effort']}, verbosity={best['verbosity']}")
            print(f"   비용: ${best['cost']:.6f}, 시간: {best['elapsed_seconds']:.2f}초")
    
    # 저장
    output_file = f"benchmark_gpt51_quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'results': results}, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ 저장: {output_file}")
    print()
    print("🎉 완료!")


if __name__ == "__main__":
    quick_test_gpt51()

