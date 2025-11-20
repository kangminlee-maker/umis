#!/usr/bin/env python3
"""
Phase 3 전용 모델 테스트
gpt-5-mini, gpt-4.1-mini 등 중급 모델 성능 확인
"""

import os
import json
import time
from typing import Dict, Any
from datetime import datetime
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


class Phase3ModelTest:
    """
    Phase 3 중급 작업 전용 모델 테스트
    """
    
    def __init__(self):
        self.client = OpenAI()
        
        # 테스트 대상: nano와 standard 사이 모델들
        self.models = [
            'gpt-4o-mini',      # 기준 (검증됨)
            'gpt-5-mini',       # NEW
            'gpt-4.1-mini',     # NEW
            'gpt-4o',           # 비교용
            'gpt-4.1'           # NEW
        ]
        
        # 가격 정보
        self.pricing = {
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4.1': {'input': 2.00, 'output': 8.00}
        }
        
        self.results = []
    
    def get_phase3_scenarios(self):
        """
        Phase 3 시나리오 (개선된 프롬프트)
        """
        return [
            {
                'id': 'P3-001',
                'name': 'Phase 3 (템플릿 있음) - 개선된 프롬프트',
                'complexity': 'medium',
                'prompt': '''B2B SaaS 한국 시장 평균 ARPU를 추정하세요.

참고 예시:
질문: "B2B SaaS 글로벌 ARPU는?"
답: $100

이제 한국 시장을 추정하세요.

단계별 계산:
1. 글로벌 벤치마크: $100
2. 한국 조정: $100 × 0.6 = $60 (GDP per capita 비율)
3. B2B 배수 적용: $60 × 3 = $180 (B2B는 B2C의 3배)
4. 환율 적용: $180 × 1,300 = 234,000원
5. 반올림: 200,000원

위 단계를 따라 계산하세요.

JSON 형식:
{
  "value": 숫자,
  "unit": "원",
  "confidence": 0.65-0.75,
  "step1_global": 값,
  "step2_korea": 값,
  "step3_b2b": 값,
  "step4_krw": 값,
  "reasoning": "한 문장 요약"
}''',
                'expected_answer': '180,000-240,000원',
                'correct_range': (180000, 240000)
            },
            
            {
                'id': 'P3-002',
                'name': 'Phase 3 (템플릿 없음) - 창의적 추정',
                'complexity': 'complex',
                'prompt': '''한국 온라인 교육 플랫폼의 성인 취미 강좌 월 구독료를 추정하세요.

고려 사항:
- 타겟: 성인 취미 학습자 (직장인 30-40대)
- 경쟁사: 클래스101, 탈잉, 프립
- 시장: 한국
- 콘텐츠: 피아노, 그림, 요리 등 취미 강좌

단계별로 생각하세요:
1. 경쟁사 가격 조사 (알려진 정보 활용)
2. 타겟 고객 지불 의향
3. 콘텐츠 가치
4. 시장 포지셔닝

JSON 형식:
{
  "value": 숫자,
  "unit": "원",
  "confidence": 0.60-0.75,
  "competitive_analysis": "경쟁사 분석",
  "reasoning": "종합 판단"
}''',
                'expected_answer': '20,000-50,000원',
                'correct_range': (20000, 50000)
            },
            
            {
                'id': 'P3-003',
                'name': 'Phase 3 (벤치마크 조정) - 다른 도메인',
                'complexity': 'medium',
                'prompt': '''한국 B2C 커피 배달 앱의 건당 배달비를 추정하세요.

참고 데이터:
- 글로벌 음식 배달 평균 배달비: $3-5
- 한국 물가 수준: 글로벌 대비 70%
- 커피는 음식보다 간편: 0.8배

단계별 계산:
1. 글로벌 중간값: $4
2. 한국 조정: $4 × 0.7 = $2.8
3. 커피 특성: $2.8 × 0.8 = $2.24
4. 환율: $2.24 × 1,300 = 2,912원
5. 반올림: 3,000원

위 논리를 따라 답변하세요.

JSON 형식:
{
  "value": 숫자,
  "unit": "원",
  "confidence": 0.70,
  "reasoning": "계산 과정 요약"
}''',
                'expected_answer': '2,500-3,500원',
                'correct_range': (2500, 3500)
            }
        ]
    
    def test_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """단일 모델 테스트"""
        print(f"\n{'='*80}")
        print(f"🤖 모델: {model}")
        print(f"📝 시나리오: {scenario['name']}")
        print(f"{'='*80}\n")
        
        print(f"⏳ {model} 호출 중...")
        start_time = time.time()
        
        try:
            # API 호출
            if model.startswith('o1') or model.startswith('o3'):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": scenario['prompt']}]
                )
            elif 'gpt-5' in model:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "당신은 시장 분석 전문가입니다. JSON 형식으로만 답변하세요."},
                        {"role": "user", "content": scenario['prompt']}
                    ],
                    response_format={"type": "json_object"}
                )
            else:
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
            
            # 파싱
            content = response.choices[0].message.content
            try:
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            # 비용
            usage = response.usage
            cost = self._calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)
            
            # 정확도 자동 평가
            auto_eval = self._auto_evaluate(parsed, scenario)
            
            # 결과 출력
            print(f"\n✅ 응답 받음")
            print(f"   비용: ${cost:.6f}")
            print(f"   시간: {elapsed:.2f}초")
            print(f"   토큰: {usage.total_tokens} ({usage.prompt_tokens}→{usage.completion_tokens})")
            print()
            print("📄 응답:")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            print()
            print(f"🎯 기대: {scenario['expected_answer']}")
            print(f"📊 자동 평가: {auto_eval['accuracy']} ({auto_eval['reason']})")
            print()
            
            return {
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'response': parsed,
                'expected': scenario['expected_answer'],
                'auto_evaluation': auto_eval,
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'tokens': {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                },
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n❌ 오류: {str(e)}")
            
            return {
                'model': model,
                'scenario_id': scenario['id'],
                'error': str(e),
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        rates = self.pricing.get(model, {'input': 0, 'output': 0})
        cost = (input_tokens / 1_000_000 * rates['input'] +
                output_tokens / 1_000_000 * rates['output'])
        return cost
    
    def _auto_evaluate(self, response: Dict, scenario: Dict) -> Dict[str, Any]:
        """자동 평가 (범위 확인)"""
        if 'parse_error' in response:
            return {'accuracy': 'JSON 파싱 실패', 'score': 0, 'reason': 'JSON 형식 오류'}
        
        value = response.get('value')
        if value is None:
            return {'accuracy': '값 없음', 'score': 0, 'reason': '응답에 value 없음'}
        
        # 범위 확인
        min_val, max_val = scenario['correct_range']
        
        if min_val <= value <= max_val:
            return {'accuracy': '✅ 범위 내', 'score': 100, 'reason': f'{min_val:,}-{max_val:,}원 범위 내'}
        elif min_val * 0.7 <= value <= max_val * 1.3:
            deviation = abs(value - (min_val + max_val) / 2) / ((min_val + max_val) / 2) * 100
            return {'accuracy': '⚠️ 허용 범위', 'score': 80, 'reason': f'±30% 내, 편차 {deviation:.0f}%'}
        else:
            deviation = abs(value - (min_val + max_val) / 2) / ((min_val + max_val) / 2) * 100
            return {'accuracy': '❌ 범위 벗어남', 'score': 50, 'reason': f'편차 {deviation:.0f}%'}
    
    def run_test(self):
        """전체 테스트 실행"""
        print("="*80)
        print("Phase 3 중급 모델 테스트")
        print("="*80)
        print()
        
        scenarios = self.get_phase3_scenarios()
        
        print(f"테스트 모델: {len(self.models)}개")
        for idx, model in enumerate(self.models, 1):
            rates = self.pricing[model]
            cost_per_task = (rates['input'] * 1000 / 1_000_000 + rates['output'] * 500 / 1_000_000)
            print(f"  {idx}. {model:20s} - ${cost_per_task:.6f}/작업")
        
        print(f"\n테스트 시나리오: {len(scenarios)}개")
        for idx, sc in enumerate(scenarios, 1):
            print(f"  {idx}. {sc['name']}")
        
        print(f"\n총 테스트: {len(self.models) * len(scenarios)}개")
        print()
        
        # 진행
        total = len(self.models) * len(scenarios)
        count = 0
        
        for model in self.models:
            print(f"\n{'#'*80}")
            print(f"# 모델: {model}")
            print(f"{'#'*80}")
            
            for scenario in scenarios:
                count += 1
                print(f"\n[{count}/{total}] 진행 중...")
                
                result = self.test_model(model, scenario)
                self.results.append(result)
                
                time.sleep(0.5)  # Rate limit 방지
        
        # 저장
        output_file = f'benchmark_phase3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.results),
                    'successful': sum(1 for r in self.results if r['success'])
                },
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장: {output_file}")
        
        # 리포트
        self.generate_report()
    
    def generate_report(self):
        """리포트 생성"""
        print(f"\n{'='*80}")
        print("📊 Phase 3 모델 성능 리포트")
        print(f"{'='*80}\n")
        
        success_results = [r for r in self.results if r['success']]
        
        # 모델별 통계
        model_stats = {}
        for result in success_results:
            model = result['model']
            
            if model not in model_stats:
                model_stats[model] = {
                    'costs': [],
                    'times': [],
                    'scores': [],
                    'correct_count': 0,
                    'total_count': 0
                }
            
            model_stats[model]['costs'].append(result['cost'])
            model_stats[model]['times'].append(result['elapsed_seconds'])
            
            auto_eval = result.get('auto_evaluation', {})
            score = auto_eval.get('score', 0)
            model_stats[model]['scores'].append(score)
            model_stats[model]['total_count'] += 1
            
            if score == 100:
                model_stats[model]['correct_count'] += 1
        
        # 테이블 출력
        print(f"{'모델':20s} | {'정확도':10s} | {'평균 비용':12s} | {'평균 시간':10s} | {'평균 점수':10s} | 가성비")
        print("-" * 95)
        
        summaries = []
        for model, stats in model_stats.items():
            accuracy = stats['correct_count'] / stats['total_count'] * 100
            avg_cost = sum(stats['costs']) / len(stats['costs'])
            avg_time = sum(stats['times']) / len(stats['times'])
            avg_score = sum(stats['scores']) / len(stats['scores'])
            
            value_score = avg_score / (avg_cost * 1_000_000) if avg_cost > 0 else 0
            
            summaries.append({
                'model': model,
                'accuracy': accuracy,
                'avg_cost': avg_cost,
                'avg_time': avg_time,
                'avg_score': avg_score,
                'value_score': value_score
            })
            
            print(f"{model:20s} | {accuracy:7.0f}%   | ${avg_cost:.6f}   | {avg_time:7.2f}초   | {avg_score:7.0f}점   | {value_score:8.0f}")
        
        # 가성비 순 정렬
        summaries.sort(key=lambda s: s['value_score'], reverse=True)
        
        print(f"\n{'='*80}")
        print("🏆 Phase 3 가성비 랭킹")
        print(f"{'='*80}\n")
        
        for idx, summary in enumerate(summaries, 1):
            print(f"{idx}위: {summary['model']}")
            print(f"   정확도: {summary['accuracy']:.0f}%")
            print(f"   평균 점수: {summary['avg_score']:.0f}점")
            print(f"   비용: ${summary['avg_cost']:.6f}/작업")
            print(f"   시간: {summary['avg_time']:.2f}초")
            print(f"   가성비: {summary['value_score']:.0f}")
            print()
        
        # 추천
        print(f"{'='*80}")
        print("💡 추천")
        print(f"{'='*80}\n")
        
        best = summaries[0]
        
        print(f"Phase 3 (템플릿 있음) 최적 모델:")
        print(f"  → {best['model']}")
        print(f"     품질: {best['avg_score']:.0f}점")
        print(f"     비용: ${best['avg_cost']:.6f}")
        print(f"     가성비: {best['value_score']:.0f}")
        print()
        
        # GPT-4o-mini와 비교
        mini_stats = next((s for s in summaries if s['model'] == 'gpt-4o-mini'), None)
        
        if mini_stats and best['model'] != 'gpt-4o-mini':
            print(f"vs GPT-4o-mini:")
            print(f"  품질: {best['avg_score']:.0f} vs {mini_stats['avg_score']:.0f} ({best['avg_score'] - mini_stats['avg_score']:+.0f}점)")
            print(f"  비용: ${best['avg_cost']:.6f} vs ${mini_stats['avg_cost']:.6f}")
            
            if best['avg_cost'] < mini_stats['avg_cost']:
                saving = (1 - best['avg_cost'] / mini_stats['avg_cost']) * 100
                print(f"  절감: {saving:.0f}%")
            else:
                increase = (best['avg_cost'] / mini_stats['avg_cost'] - 1) * 100
                print(f"  추가 비용: +{increase:.0f}%")


def main():
    """메인 실행"""
    tester = Phase3ModelTest()
    tester.run_test()


if __name__ == "__main__":
    main()




