#!/usr/bin/env python3
"""
gpt-5-pro 문제 1 재테스트 (최적화된 max_output_tokens 48K)
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from phase4_common import (
    get_model_config,
    build_api_params,
    call_model_api,
    get_phase4_scenarios,
    evaluate_fermi_response
)

load_dotenv()


def test_gpt5_pro_problem1():
    """gpt-5-pro로 문제 1만 재테스트"""
    
    print("=" * 100)
    print("gpt-5-pro 문제 1 재테스트 (최적화된 max_output_tokens)")
    print("=" * 100)
    print()
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    scenarios = get_phase4_scenarios()
    
    # 문제 1만 테스트
    scenario = scenarios[0]  # Phase 4 - 한국 전체 사업자 수
    
    print(f"📋 문제: {scenario['name']}")
    print(f"   정답: {scenario['expected_value']:,} {scenario['expected_unit']}")
    print()
    
    model_name = 'gpt-5-pro'
    reasoning_effort = 'high'
    
    print(f"🔄 모델: {model_name} (effort={reasoning_effort})")
    print()
    
    try:
        start = time.time()
        
        # 최적화된 설정으로 API 파라미터 생성
        api_type, api_params = build_api_params(
            model_name=model_name,
            prompt=scenario['prompt'],
            reasoning_effort=reasoning_effort
        )
        
        # 모델 설정 출력
        config = get_model_config(model_name)
        print(f"🔧 {model_name} API 설정:")
        print(f"  - API 타입: {config['api_type']}")
        print(f"  - reasoning 지원: {config['reasoning_effort_support']}")
        print(f"  - reasoning.effort: {api_params.get('reasoning', {}).get('effort', 'N/A')}")
        print(f"  - max_output_tokens: {api_params.get('max_output_tokens', 'N/A')} (최적화: 272K → 48K)")
        print()
        
        print("⏳ API 호출 중...")
        
        # API 호출
        response = call_model_api(client, api_type, api_params)
        
        elapsed = time.time() - start
        
        # 응답 추출
        if api_type == 'responses':
            # response.output이 리스트인 경우 처리
            if isinstance(response.output, list):
                # 마지막 message의 content에서 텍스트 추출
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
        
        print(f"✅ 응답 완료! (소요: {elapsed:.1f}초)")
        print()
        
        # JSON 파싱
        import json as json_lib
        import re
        
        # JSON 추출 시도
        try:
            # 코드 블록 제거
            clean_output = re.sub(r'```json\s*', '', output)
            clean_output = re.sub(r'```\s*$', '', clean_output)
            clean_output = clean_output.strip()
            
            parsed = json_lib.loads(clean_output)
        except:
            print("⚠️ JSON 파싱 실패, 응답 일부 출력:")
            print(output[:500])
            print()
            raise
        
        # 평가
        evaluation = evaluate_fermi_response(
            model_name=model_name,
            response=parsed,
            expected_value=scenario['expected_value'],
            problem_id=scenario['id']
        )
        
        # 결과 출력
        print("=" * 100)
        print("📊 평가 결과")
        print("=" * 100)
        print()
        print(f"추정값: {evaluation['value']:,} {evaluation['unit']}")
        print(f"정답: {scenario['expected_value']:,} {scenario['expected_unit']}")
        print()
        print(f"총점: {evaluation['total_score']:.1f}/100")
        print(f"  - 정확도: {evaluation['accuracy']['score']}/25")
        print(f"  - 연결성: {evaluation['calculation_connectivity']['score']:.1f}/50")
        print(f"  - 분해: {evaluation['decomposition']['score']}/15")
        print(f"  - 개념: {evaluation['conceptual_coherence']['score']}/15")
        print(f"  - 논리: {evaluation['logic']['score']}/10")
        print()
        print(f"소요 시간: {elapsed:.1f}초")
        
        # 결과 저장
        result = {
            'model': model_name,
            'problem': scenario['name'],
            'problem_id': scenario['id'],
            'expected_value': scenario['expected_value'],
            'reasoning_effort': reasoning_effort,
            'max_output_tokens': api_params.get('max_output_tokens'),
            'elapsed': elapsed,
            'response': output,
            **evaluation
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'gpt5_pro_problem1_retest_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 결과 저장: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    test_gpt5_pro_problem1()

