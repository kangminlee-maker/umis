#!/usr/bin/env python3
"""
gpt-5.1 Responses API Phase 4 문제 해결 테스트
다양한 reasoning effort & verbosity 조합으로 테스트
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


# Phase 4 프롬프트
PHASE_4_PROMPT = '''데이터 없이 "한국 기업용 화상회의 솔루션 TAM (Total Addressable Market)"을 추정하세요.

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
        {"step": "단계2", "assumption": "가정", "value": <값>},
        {"step": "단계3", "assumption": "가정", "value": <값>}
    ],
    "reasoning": "전체 추정 논리",
    "confidence_range": {"min": <최소값>, "max": <최대값>}
}'''


def test_responses_config(client, effort, verbosity):
    """특정 설정으로 Responses API 테스트"""
    
    config_name = f"effort={effort}, verbosity={verbosity}"
    print(f"\n테스트: {config_name}")
    
    try:
        start = time.time()
        
        api_params = {
            "model": "gpt-5.1",
            "input": PHASE_4_PROMPT,
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
        
        elapsed = time.time() - start
        
        # 토큰 정보
        tokens = {
            'input': getattr(response, 'input_tokens', len(PHASE_4_PROMPT) // 4),
            'output': getattr(response, 'output_tokens', len(content) // 4),
        }
        tokens['total'] = tokens['input'] + tokens['output']
        
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
            parsed = {'raw': content[:500], 'parse_error': str(e)}
        
        # 비용 계산
        cost = (tokens['input'] / 1_000_000 * 1.25 + 
               tokens['output'] / 1_000_000 * 10.00)
        
        # 품질 평가
        score = 0
        
        # 기본 구조 (25점)
        if 'value' in parsed and parsed['value']:
            score += 15
        if 'unit' in parsed and parsed['unit']:
            score += 5
        if 'confidence' in parsed and parsed['confidence']:
            score += 5
        
        # Phase 4 특화 평가 (75점)
        value = parsed.get('value', 0)
        if 500 <= value <= 3000:
            score += 20
        
        decomp = parsed.get('decomposition', [])
        if isinstance(decomp, list) and len(decomp) >= 3:
            score += 25
            print(f"  ✅ decomposition: {len(decomp)}단계")
        else:
            print(f"  ❌ decomposition: {decomp}")
        
        if 'method' in parsed and parsed['method']:
            score += 10
        if 'reasoning' in parsed and parsed['reasoning']:
            score += 10
        if 'confidence_range' in parsed and parsed['confidence_range']:
            score += 10
        
        print(f"  품질: {score}/100")
        print(f"  비용: ${cost:.6f}")
        print(f"  시간: {elapsed:.2f}초")
        print(f"  토큰: {tokens['total']}")
        
        if score >= 70:
            print(f"  ✅ 성공!")
        else:
            print(f"  ⚠️ 품질 미달")
        
        return {
            'config': config_name,
            'effort': effort,
            'verbosity': verbosity,
            'quality_score': score,
            'cost': cost,
            'elapsed_seconds': round(elapsed, 2),
            'tokens': tokens,
            'response': parsed,
            'success': True
        }
        
    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:100]}")
        return {
            'config': config_name,
            'effort': effort,
            'verbosity': verbosity,
            'error': str(e),
            'success': False
        }


def run_test():
    """전체 테스트 실행"""
    print("=" * 100)
    print("gpt-5.1 Responses API Phase 4 문제 해결 테스트")
    print("=" * 100)
    
    client = OpenAI()
    
    # 다양한 조합 테스트
    test_configs = [
        # 원래 설정
        ('medium', 'low'),
        
        # verbosity 높이기
        ('medium', 'medium'),
        ('medium', 'high'),
        
        # effort 높이기
        ('high', 'low'),
        ('high', 'medium'),
        ('high', 'high'),
        
        # effort 낮추기
        ('low', 'medium'),
        ('low', 'high'),
        
        # 둘 다 최대
        ('none', 'high'),
    ]
    
    results = []
    
    for effort, verbosity in test_configs:
        result = test_responses_config(client, effort, verbosity)
        results.append(result)
        time.sleep(2)
    
    # 결과 분석
    print("\n" + "=" * 100)
    print("📊 결과 분석")
    print("=" * 100)
    print()
    
    success_results = [r for r in results if r.get('success', False)]
    
    if success_results:
        print("🏆 품질 순위\n")
        print(f"{'순위':<4} | {'구성':<30} | {'품질':<10} | {'비용':<12} | {'시간'}")
        print("-" * 80)
        
        success_results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        for i, r in enumerate(success_results, 1):
            marker = "⭐" if r['quality_score'] >= 70 else "  "
            print(f"{marker}{i:<3} | {r['config']:<30} | {r['quality_score']:>8}/100 | ${r['cost']:<11.6f} | {r['elapsed_seconds']}초")
        
        # 70점 이상 모델
        good_results = [r for r in success_results if r['quality_score'] >= 70]
        
        if good_results:
            print(f"\n\n💎 품질 70점 이상 달성 구성 ({len(good_results)}개)\n")
            
            for r in good_results:
                print(f"✅ {r['config']}")
                print(f"   - 품질: {r['quality_score']}/100")
                print(f"   - 비용: ${r['cost']:.6f}")
                print(f"   - 시간: {r['elapsed_seconds']}초")
                
                if 'decomposition' in r['response']:
                    decomp = r['response']['decomposition']
                    if isinstance(decomp, list):
                        print(f"   - 분해 단계: {len(decomp)}단계")
                print()
        else:
            print("\n\n⚠️ 70점 이상 달성한 구성 없음!")
            print("gpt-5.1 Responses API는 Phase 4에 부적합한 것으로 판단됩니다.")
    
    # 저장
    output_file = f"test_gpt5_phase4_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'gpt5_phase4_responses_fix',
                'total_tests': len(results),
                'success_count': len(success_results)
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    run_test()


