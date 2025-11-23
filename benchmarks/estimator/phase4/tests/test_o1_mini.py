#!/usr/bin/env python3
"""
o1-mini 모델 테스트
Phase 0-4 전체 시나리오 테스트
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def test_o1_mini():
    """o1-mini 모델 전체 테스트"""
    
    client = OpenAI()
    
    # 7개 시나리오 (Phase 0-4)
    scenarios = [
        {
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
        },
        {
            'id': 'phase1_rag',
            'phase': 1,
            'name': 'Phase 1: Direct RAG (RAG 결과 파싱)',
            'prompt': '''RAG 검색 결과에서 코웨이의 월 렌탈료를 추출하세요.

RAG 결과:
코웨이 렌탈 사업 개요
- 월 평균 렌탈료: 33,000원
- 총 구독자 수: 720만명
- 주요 제품: 정수기, 공기청정기, 비데

요구사항: 월 렌탈료만 추출, confidence는 1.0으로 설정

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 1.0
}''',
            'expected': {'value': 33000, 'confidence': 1.0}
        },
        {
            'id': 'phase2_calculation',
            'phase': 2,
            'name': 'Phase 2: Calculation (수식 계산)',
            'prompt': '''주어진 공식과 값을 사용하여 LTV를 계산하세요.

공식: LTV = ARPU / Churn_Rate

주어진 값:
- ARPU = 80,000원
- Churn_Rate = 0.05

계산 과정:
1. 공식에 값 대입
2. 나눗셈 수행
3. 결과를 원 단위로 표현

요구사항: 정확한 계산 결과, confidence는 1.0으로 설정

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 1.0
}''',
            'expected': {'value': 1600000, 'confidence': 1.0}
        },
        {
            'id': 'phase3_template',
            'phase': 3,
            'name': 'Phase 3: Guestimation (템플릿 있음)',
            'prompt': '''주어진 템플릿을 참고하여 한국 B2B SaaS ARPU를 추정하세요.

참고 템플릿:
- 글로벌 평균 ARPU: $100
- 한국 시장 조정 계수: 0.6 (구매력, 시장 성숙도 고려)
- 환율: 1,300원/$
- 계산: $100 × 0.6 = $60 → 78,000원

작업:
1. 템플릿의 논리를 이해
2. 유사한 접근법 적용
3. 합리적인 범위 내에서 추정

제약:
- reasoning은 한 문장으로 요약
- confidence는 0.7~1.0 범위

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 0.7~1.0,
    "reasoning": "추정 근거 (200자 이내)"
}''',
            'expected': {'value_min': 50000, 'value_max': 150000, 'confidence_min': 0.7}
        },
        {
            'id': 'phase3_no_template',
            'phase': 3,
            'name': 'Phase 3: Guestimation (템플릿 없음)',
            'prompt': '''한국 온라인 성인 취미교육 플랫폼의 월 구독료를 추정하세요.

시장 정보:
- 타겟 고객: 직장인 30-40대
- 주요 경쟁사: 클래스101, 탈잉
- 서비스: 온라인 실시간/VOD 강의

고려사항:
1. 타겟 고객의 지불 능력
2. 경쟁사 가격대 (시장 조사 불가, 추정 필요)
3. 제공 가치 (편의성, 품질)
4. 구독 vs 단건 결제 모델

제약:
- reasoning은 추정 논리를 명확히 설명 (200자 이내)
- confidence는 0.6~0.9 범위 (템플릿 없으므로 낮음)

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 0.6~0.9,
    "reasoning": "추정 논리 (200자 이내)"
}''',
            'expected': {'value_min': 10000, 'value_max': 50000, 'confidence_min': 0.6}
        },
        {
            'id': 'phase4_simple',
            'phase': 4,
            'name': 'Phase 4: Simple Fermi',
            'prompt': '''Fermi 추정 기법을 사용하여 서울시 피아노 학원 수를 추정하세요.

단계별 접근:
1. 필요 변수 식별 (예: 인구, 학습률, 학원당 학생 수)
2. 각 변수 값 추정 (합리적 가정 기반)
3. 최종 계산 수행
4. 결과의 합리성 검증

변수 예시:
- 서울 인구
- 피아노 학습 인구 비율
- 학원당 평균 학생 수
- 온라인 vs 오프라인 비율

요구사항:
- reasoning: 추정 논리를 단계별로 요약 (300자 이내)
- confidence: 0.6~0.8 범위

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "개",
    "confidence": 0.6~0.8,
    "reasoning": "단계별 논리 (300자 이내)"
}''',
            'expected': {'value_min': 1500, 'value_max': 4000, 'confidence_min': 0.6}
        },
        {
            'id': 'phase4_complex',
            'phase': 4,
            'name': 'Phase 4: Complex Fermi',
            'prompt': '''다층 Fermi 추정으로 한국 성인 피아노 학습 시장의 연간 총 지출액을 계산하세요.

필수 구성요소:
1. 학습자 수 추정
   - 연령대별 학습 비율
   - 지역별 분포
   
2. 지출 항목별 추정
   - 학원비 (월평균 × 12개월)
   - 교재비 (연간)
   - 악기 구매/렌탈 (초기 + 유지)
   - 기타 비용 (조율, 악세서리 등)

3. 추정 모델
   - Top-down: 전체 시장에서 하향식
   - Bottom-up: 개인 지출에서 상향식
   - 최소 1개 모델 사용, models 배열에 명시

요구사항:
- models: 사용한 추정 모델 목록
- reasoning: 각 모델의 논리와 최종 값 선택 근거 (500자 이내)
- confidence: 0.5~0.8 범위 (복잡도로 인한 불확실성)

JSON 형식으로 응답:
{
    "value": 숫자,
    "unit": "원",
    "confidence": 0.5~0.8,
    "models": ["top_down" 또는 "bottom_up" 등],
    "reasoning": "모델별 논리 (500자 이내)"
}''',
            'expected': {'value_min': 50000000000, 'value_max': 500000000000, 'confidence_min': 0.5}
        }
    ]
    
    print("=" * 80)
    print("o1-mini 전체 시나리오 테스트")
    print("=" * 80)
    print()
    
    results = []
    total_cost = 0
    total_time = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/7] {scenario['name']}")
        print(f"Phase: {scenario['phase']}")
        print("-" * 80)
        
        try:
            # API 호출
            start_time = time.time()
            
            # o1-mini는 temperature 미지원
            response = client.chat.completions.create(
                model='o1-mini',
                messages=[
                    {"role": "user", "content": scenario['prompt']}
                ]
            )
            
            elapsed = time.time() - start_time
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # JSON 추출 시도
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
            
            # o1-mini 가격: $3/1M input, $12/1M output
            cost = (input_tokens * 3.00 / 1_000_000) + (output_tokens * 12.00 / 1_000_000)
            
            # 품질 평가
            quality = evaluate_quality(scenario, parsed)
            
            result = {
                'scenario_id': scenario['id'],
                'phase': scenario['phase'],
                'name': scenario['name'],
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
                print(f"   추정값: {parsed['value']:,}{parsed.get('unit', '')}")
            print()
            
            total_cost += cost
            total_time += elapsed
            
        except Exception as e:
            print(f"❌ 실패: {e}")
            print()
            
            result = {
                'scenario_id': scenario['id'],
                'phase': scenario['phase'],
                'name': scenario['name'],
                'success': False,
                'error': str(e),
                'quality_score': {'total_score': 0}
            }
        
        results.append(result)
        
        # Rate limiting
        if i < len(scenarios):
            time.sleep(2)
    
    # 요약
    print("=" * 80)
    print("테스트 완료 요약")
    print("=" * 80)
    print()
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(successful)}개")
    print(f"실패: {len(failed)}개")
    print()
    
    if successful:
        avg_quality = sum(r['quality_score']['total_score'] for r in successful) / len(successful)
        avg_time = total_time / len(successful)
        
        print(f"평균 품질: {avg_quality:.1f}/100")
        print(f"평균 시간: {avg_time:.2f}초")
        print(f"총 비용: ${total_cost:.6f}")
        print(f"1,000회 비용: ${total_cost * 1000 / len(successful):.2f}")
        print()
        
        # Phase별 결과
        print("Phase별 결과:")
        for phase in range(5):
            phase_results = [r for r in successful if r['phase'] == phase]
            if phase_results:
                phase_quality = sum(r['quality_score']['total_score'] for r in phase_results) / len(phase_results)
                phase_time = sum(r['time'] for r in phase_results) / len(phase_results)
                print(f"  Phase {phase}: 품질 {phase_quality:.1f}/100, 시간 {phase_time:.2f}초")
    
    # 결과 저장
    output = {
        'model': 'o1-mini',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'avg_quality': avg_quality if successful else 0,
            'avg_time': avg_time if successful else 0,
            'total_cost': total_cost,
            'cost_per_1000': total_cost * 1000 / len(successful) if successful else 0
        },
        'results': results
    }
    
    filename = f"benchmark_o1_mini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"결과 저장: {filename}")
    
    return output


def evaluate_quality(scenario, parsed):
    """품질 평가"""
    
    score = {
        'json_parse': 0,
        'has_value': 0,
        'has_confidence': 0,
        'value_accuracy': 0,
        'confidence_accuracy': 0,
        'has_reasoning': 0,
        'total_score': 0
    }
    
    # Phase 0-2: 결정론적
    if scenario['phase'] <= 2:
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
    
    # Phase 3-4: 추정
    else:
        # JSON 파싱 (20점)
        if 'parse_error' not in parsed:
            score['json_parse'] = 20
        
        # value 존재 (20점)
        if 'value' in parsed:
            score['has_value'] = 20
        
        # confidence 존재 (15점)
        if 'confidence' in parsed:
            score['has_confidence'] = 15
        
        # reasoning 존재 (15점)
        if 'reasoning' in parsed:
            score['has_reasoning'] = 15
        
        # value 범위 내 (20점)
        if 'value' in parsed:
            value = parsed['value']
            if scenario['expected']['value_min'] <= value <= scenario['expected']['value_max']:
                score['value_accuracy'] = 20
        
        # confidence 범위 내 (10점)
        if 'confidence' in parsed:
            conf = parsed['confidence']
            if conf >= scenario['expected']['confidence_min']:
                score['confidence_accuracy'] = 10
    
    score['total_score'] = sum(v for k, v in score.items() if k != 'total_score')
    
    return score


if __name__ == '__main__':
    test_o1_mini()
