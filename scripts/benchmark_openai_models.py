#!/usr/bin/env python3
"""
OpenAI 모델 성능 벤치마크 (UMIS 작업 기준)
각 모델을 실제 UMIS 작업으로 테스트하여 비용-성능 비교
"""

import os
import json
import time
from typing import Dict, List, Any
from datetime import datetime
from openai import OpenAI

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()


class OpenAIBenchmark:
    """
    OpenAI 모델 벤치마크
    """
    
    def __init__(self):
        self.client = OpenAI()
        
        # 테스트할 모델 (Standard Tier)
        self.models = {
            'nano': [
                'gpt-5-nano',
                'gpt-4.1-nano'
            ],
            'mini': [
                'gpt-4o-mini',
                'gpt-5-mini',
                'gpt-4.1-mini'
            ],
            'standard': [
                'gpt-4o',
                'gpt-4.1',
                'gpt-5.1'
            ],
            'thinking': [
                'o1-mini',
                'o3-mini',
                'o4-mini',
                'o3'
            ]
        }
        
        # 가격 정보 ($/1M 토큰)
        self.pricing = {
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            'gpt-4.1-nano': {'input': 0.10, 'output': 0.40},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4.1': {'input': 2.00, 'output': 8.00},
            'gpt-5.1': {'input': 1.25, 'output': 10.00},
            'o1-mini': {'input': 1.10, 'output': 4.40},
            'o3-mini': {'input': 1.10, 'output': 4.40},
            'o4-mini': {'input': 1.10, 'output': 4.40},
            'o3': {'input': 2.00, 'output': 8.00}
        }
        
        # 결과 저장
        self.results = []
    
    def run_full_benchmark(self, output_file: str = 'benchmark_results.json'):
        """
        전체 벤치마크 실행
        """
        print("🚀 OpenAI 모델 벤치마크 시작")
        print(f"   테스트 시나리오: {len(self.get_test_scenarios())}개")
        print(f"   테스트 모델: {sum(len(models) for models in self.models.values())}개")
        print()
        
        scenarios = self.get_test_scenarios()
        
        for scenario_idx, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*80}")
            print(f"시나리오 {scenario_idx}/{len(scenarios)}: {scenario['name']}")
            print(f"{'='*80}")
            
            # 각 모델 테스트
            for category, models in self.models.items():
                for model in models:
                    try:
                        result = self.test_model(model, scenario)
                        self.results.append(result)
                        
                        # 결과 출력
                        self._print_result(result)
                        
                        # Rate limit 방지
                        time.sleep(1)
                    
                    except Exception as e:
                        print(f"   ❌ {model}: 오류 - {str(e)}")
                        self.results.append({
                            'model': model,
                            'scenario': scenario['name'],
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
        
        # 결과 저장
        self.save_results(output_file)
        
        # 분석 리포트 생성
        self.generate_report()
    
    def get_test_scenarios(self) -> List[Dict]:
        """
        UMIS 테스트 시나리오
        """
        return [
            {
                'id': 'phase0',
                'name': 'Phase 0 (Literal)',
                'category': 'simple',
                'prompt': '''다음 데이터에서 "한국 B2B SaaS ARPU"를 찾아 반환하세요:

데이터:
- 미국 B2C SaaS ARPU: $50
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

JSON 형식으로 답변:
{"value": 숫자, "unit": "원", "confidence": 1.0}''',
                'expected': {
                    'value': 200000,
                    'unit': '원',
                    'confidence': 1.0
                }
            },
            
            {
                'id': 'phase2_calculation',
                'name': 'Phase 2 (계산)',
                'category': 'simple',
                'prompt': '''다음 공식을 계산하세요:

LTV = ARPU / Churn_Rate

주어진 값:
- ARPU: 80,000원
- Churn_Rate: 0.05

JSON 형식으로 답변:
{"value": 숫자, "formula": "공식", "confidence": 1.0}''',
                'expected': {
                    'value': 1600000,
                    'confidence': 1.0
                }
            },
            
            {
                'id': 'phase3_template',
                'name': 'Phase 3 (템플릿 있음)',
                'category': 'medium',
                'prompt': '''B2B SaaS 한국 시장 ARPU를 추정하세요.

참고 예시:
- 글로벌 B2B SaaS ARPU: $100
- 한국 GDP per capita: 글로벌 대비 60%
- B2B vs B2C 배수: 3배

모형:
1. 글로벌 기준 조정: $100 × 0.6 × 3 = $180
2. 환율 적용: $180 × 1,300 = 234,000원
3. 반올림: 200,000원

이제 같은 방식으로 답변하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "reasoning": "한 문장"}''',
                'expected': {
                    'value_range': [150000, 250000],
                    'confidence_min': 0.65
                }
            },
            
            {
                'id': 'phase3_no_template',
                'name': 'Phase 3 (템플릿 없음)',
                'category': 'complex',
                'prompt': '''한국 온라인 교육 플랫폼의 월 구독료를 추정하세요.

고려 사항:
- 타겟: 성인 취미 교육
- 경쟁사: 클래스101, 탈잉 등
- 사용자: 직장인, 30-40대

단계별로 생각하고 JSON으로 답변:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "reasoning": "요약"}''',
                'expected': {
                    'value_range': [10000, 50000],
                    'confidence_min': 0.60
                }
            },
            
            {
                'id': 'phase4_simple',
                'name': 'Phase 4 (단순 Fermi)',
                'category': 'complex',
                'prompt': '''서울의 피아노 학원 수를 추정하세요.

다음 단계로 생각하세요:
1. 어떤 변수가 필요한가?
2. 각 변수를 어떻게 구할까?
3. 어떤 모형을 사용할까?
4. 결과가 합리적인가?

JSON 형식:
{"value": 숫자, "models": [모형1결과, 모형2결과], "confidence": 0.0-1.0, "reasoning": "요약"}''',
                'expected': {
                    'value_range': [1500, 4000],
                    'confidence_min': 0.60
                }
            },
            
            {
                'id': 'phase4_complex',
                'name': 'Phase 4 (복잡 Fermi)',
                'category': 'very_complex',
                'prompt': '''한국 성인 피아노 학습자의 연간 총 지출액을 추정하세요.

고려할 요소:
- 학습자 수
- 학원비
- 교재비
- 악기 구매/렌탈
- 기타 비용

창의적으로 모형을 생성하고, 여러 접근을 시도한 후 답변하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "models": [...], "confidence": 0.0-1.0, "reasoning_detail": {...}}''',
                'expected': {
                    'value_range': [50000000000, 500000000000],  # 500억-5000억
                    'confidence_min': 0.50
                }
            }
        ]
    
    def test_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """
        단일 모델 테스트
        """
        start_time = time.time()
        
        try:
            # 모델 타입 구분
            is_o_series = model.startswith(('o1', 'o3', 'o4'))
            is_gpt5 = model.startswith('gpt-5')
            is_reasoning = is_o_series or is_gpt5
            
            # API 호출 (모델별 분기)
            if is_reasoning:
                # reasoning 모델 (system 메시지 미지원, reasoning_effort 사용)
                api_params = {
                    "model": model,
                    "messages": [{"role": "user", "content": scenario['prompt']}]
                }
                if is_o_series:
                    api_params["reasoning_effort"] = "medium"
                else:  # gpt-5
                    api_params["reasoning_effort"] = "low"
                
                response = self.client.chat.completions.create(**api_params)
            else:
                # 일반 모델
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "당신은 시장 분석 전문가입니다. JSON 형식으로만 답변하세요."},
                        {"role": "user", "content": scenario['prompt']}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
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
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트로 저장
                parsed = {'raw_response': content, 'parse_error': True}
            
            # 비용 계산
            usage = response.usage
            cost = self._calculate_cost(
                model,
                usage.prompt_tokens,
                usage.completion_tokens
            )
            
            # 결과 반환
            return {
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'category': scenario['category'],
                'response': parsed,
                'expected': scenario.get('expected'),
                'tokens': {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                },
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'error': str(e),
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        if model not in self.pricing:
            return 0.0
        
        rates = self.pricing[model]
        cost = (input_tokens / 1_000_000 * rates['input'] +
                output_tokens / 1_000_000 * rates['output'])
        return round(cost, 6)
    
    def _print_result(self, result: Dict):
        """결과 출력"""
        if not result['success']:
            print(f"   ❌ {result['model']}: {result['error']}")
            return
        
        response = result['response']
        
        print(f"\n   ✅ {result['model']}")
        print(f"      비용: ${result['cost']:.6f}")
        print(f"      시간: {result['elapsed_seconds']}초")
        print(f"      토큰: {result['tokens']['total']} ({result['tokens']['input']}→{result['tokens']['output']})")
        
        if 'value' in response:
            print(f"      답변: {response.get('value')} {response.get('unit', '')}")
            print(f"      신뢰도: {response.get('confidence', 'N/A')}")
        
        if 'reasoning' in response:
            print(f"      근거: {response['reasoning'][:100]}...")
    
    def save_results(self, output_file: str):
        """결과 저장"""
        output_path = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장: {output_path}")
        print(f"   총 {len(self.results)}개 테스트")
    
    def generate_report(self):
        """
        분석 리포트 생성
        """
        print(f"\n{'='*80}")
        print("📊 벤치마크 리포트")
        print(f"{'='*80}\n")
        
        # 성공/실패 통계
        success_count = sum(1 for r in self.results if r['success'])
        total_count = len(self.results)
        
        print(f"총 테스트: {total_count}개")
        print(f"성공: {success_count}개 ({success_count/total_count*100:.1f}%)")
        print(f"실패: {total_count - success_count}개")
        
        # 시나리오별 통계
        print(f"\n{'='*80}")
        print("시나리오별 성능")
        print(f"{'='*80}\n")
        
        scenarios = {}
        for result in self.results:
            if not result['success']:
                continue
            
            scenario = result['scenario_name']
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(result)
        
        for scenario_name, results in scenarios.items():
            print(f"\n📌 {scenario_name}")
            print(f"   테스트 모델: {len(results)}개\n")
            
            # 비용 순 정렬
            results_sorted = sorted(results, key=lambda r: r['cost'])
            
            for idx, result in enumerate(results_sorted[:5], 1):  # Top 5만
                model = result['model']
                cost = result['cost']
                elapsed = result['elapsed_seconds']
                
                # 응답 품질 (간단 평가)
                response = result.get('response', {})
                has_value = 'value' in response
                has_confidence = 'confidence' in response
                
                quality_score = "✅" if (has_value and has_confidence) else "⚠️"
                
                print(f"   {idx}위: {model:20s} | ${cost:.6f} | {elapsed:4.1f}초 | {quality_score}")
        
        # 모델별 평균 통계
        print(f"\n{'='*80}")
        print("모델별 평균 성능")
        print(f"{'='*80}\n")
        
        model_stats = {}
        for result in self.results:
            if not result['success']:
                continue
            
            model = result['model']
            if model not in model_stats:
                model_stats[model] = {
                    'costs': [],
                    'times': [],
                    'total_tokens': []
                }
            
            model_stats[model]['costs'].append(result['cost'])
            model_stats[model]['times'].append(result['elapsed_seconds'])
            model_stats[model]['total_tokens'].append(result['tokens']['total'])
        
        # 평균 계산 및 정렬
        model_averages = []
        for model, stats in model_stats.items():
            if not stats['costs']:
                continue
            
            avg_cost = sum(stats['costs']) / len(stats['costs'])
            avg_time = sum(stats['times']) / len(stats['times'])
            avg_tokens = sum(stats['total_tokens']) / len(stats['total_tokens'])
            
            model_averages.append({
                'model': model,
                'avg_cost': avg_cost,
                'avg_time': avg_time,
                'avg_tokens': avg_tokens,
                'test_count': len(stats['costs'])
            })
        
        # 비용 순 정렬
        model_averages.sort(key=lambda m: m['avg_cost'])
        
        print(f"{'모델':20s} | {'평균 비용':12s} | {'평균 시간':10s} | {'평균 토큰':10s} | 테스트 수")
        print("-" * 80)
        
        for avg in model_averages:
            print(f"{avg['model']:20s} | ${avg['avg_cost']:.6f}   | {avg['avg_time']:6.2f}초   | {avg['avg_tokens']:8.0f}   | {avg['test_count']}개")
        
        # 가성비 TOP 3
        print(f"\n{'='*80}")
        print("🏆 가성비 TOP 3 (비용/시간 기준)")
        print(f"{'='*80}\n")
        
        # 비용 기준
        print("💰 최저 비용:")
        for idx, avg in enumerate(model_averages[:3], 1):
            print(f"   {idx}위: {avg['model']:20s} ${avg['avg_cost']:.6f}/작업")
        
        # 속도 기준
        print("\n⚡ 최고 속도:")
        model_averages_speed = sorted(model_averages, key=lambda m: m['avg_time'])
        for idx, avg in enumerate(model_averages_speed[:3], 1):
            print(f"   {idx}위: {avg['model']:20s} {avg['avg_time']:.2f}초/작업")


def main():
    """
    메인 실행
    """
    print("=" * 80)
    print("OpenAI 모델 벤치마크 (UMIS 작업 기준)")
    print("=" * 80)
    print()
    
    # API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   .env 파일을 확인하세요.")
        return
    
    print(f"✅ API 키 확인됨: {api_key[:20]}...")
    print()
    
    # 벤치마크 실행
    benchmark = OpenAIBenchmark()
    
    try:
        benchmark.run_full_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다.")
        print(f"   현재까지 {len(benchmark.results)}개 테스트 완료")
        
        if benchmark.results:
            save = input("\n결과를 저장하시겠습니까? (y/n): ")
            if save.lower() == 'y':
                benchmark.save_results('benchmark_results_partial.json')
    
    print("\n🎉 벤치마크 완료!")


if __name__ == "__main__":
    main()




