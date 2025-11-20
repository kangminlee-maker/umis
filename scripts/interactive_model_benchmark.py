#!/usr/bin/env python3
"""
OpenAI 모델 인터랙티브 벤치마크
사용자가 각 응답을 평가하며 진행
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()


class InteractiveBenchmark:
    """
    인터랙티브 모델 벤치마크
    """
    
    def __init__(self):
        # API 키만 .env에서 로드, 모델은 직접 지정
        self.client = OpenAI()  # OPENAI_API_KEY 자동 로드
        
        # 테스트할 모델 (우선순위 순)
        self.models_to_test = [
            # Tier 1: 초저가 (최우선 테스트)
            'gpt-5-nano',
            'gpt-4.1-nano',
            'gpt-4o-mini',
            
            # Tier 2: 중급
            'gpt-5-mini',
            'gpt-4.1-mini',
            'gpt-4o',
            'gpt-4.1',
            
            # Tier 3: Thinking
            'o1-mini',
            'o3-mini',
            'o3'
        ]
        
        # 가격 정보
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
        
        self.results = []
    
    def get_test_scenarios(self) -> List[Dict]:
        """UMIS 테스트 시나리오"""
        return [
            {
                'id': 'SC-001',
                'name': 'Phase 0 (Literal - 확정 데이터 조회)',
                'phase': 0,
                'complexity': 'very_simple',
                'prompt': '''다음 데이터에서 "한국 B2B SaaS ARPU"를 찾아 반환하세요:

데이터:
- 미국 B2C SaaS ARPU: $50
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

JSON 형식으로만 답변:
{"value": 숫자, "unit": "원", "confidence": 1.0}''',
                'expected_answer': '200,000원',
                'evaluation_criteria': [
                    '정확한 값 (200,000)',
                    'JSON 형식 준수',
                    '빠른 응답 (<2초)'
                ]
            },
            
            {
                'id': 'SC-002',
                'name': 'Phase 2 (공식 계산)',
                'phase': 2,
                'complexity': 'simple',
                'prompt': '''다음 공식을 계산하세요:

LTV = ARPU / Churn_Rate

주어진 값:
- ARPU: 80,000원
- Churn_Rate: 0.05 (5%)

JSON 형식:
{"value": 숫자, "unit": "원", "formula": "ARPU / Churn_Rate", "confidence": 1.0}''',
                'expected_answer': '1,600,000원',
                'evaluation_criteria': [
                    '정확한 계산 (1,600,000)',
                    '공식 이해',
                    'JSON 형식'
                ]
            },
            
            {
                'id': 'SC-003',
                'name': 'Phase 3 (템플릿 있음 - 벤치마크 조정)',
                'phase': 3,
                'complexity': 'medium',
                'prompt': '''B2B SaaS 한국 시장 평균 ARPU를 추정하세요.

참고 예시:
질문: "B2B SaaS 미국 ARPU는?"
단계:
1. 글로벌 벤치마크: $100 (알려짐)
2. 결과: $100

이제 한국 시장을 같은 방식으로:

힌트:
- 글로벌 B2B SaaS ARPU: ~$100
- 한국 vs 글로벌 GDP per capita: 약 60%
- B2B vs B2C 배수: 약 3배

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.6-0.8, "reasoning": "한 문장 요약"}''',
                'expected_answer': '150,000-250,000원 (±30%)',
                'evaluation_criteria': [
                    '합리적 범위 (15-25만원)',
                    '논리적 근거 제시',
                    'Confidence 적절 (0.6-0.8)',
                    '단계별 계산'
                ]
            },
            
            {
                'id': 'SC-004',
                'name': 'Phase 3 (템플릿 없음 - 창의적 추정)',
                'phase': 3,
                'complexity': 'complex',
                'prompt': '''한국 성인 온라인 피아노 강좌의 월 구독료를 추정하세요.

고려 사항:
- 타겟: 성인 취미 학습자
- 경쟁사: 클래스101, 탈잉 등
- 사용자: 직장인, 30-40대
- 시장: 한국

단계별로 생각하고 JSON으로 답변:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "reasoning": "요약"}''',
                'expected_answer': '20,000-50,000원',
                'evaluation_criteria': [
                    '합리적 범위 (2-5만원)',
                    '시장 이해도',
                    '경쟁사 고려',
                    '논리적 근거'
                ]
            },
            
            {
                'id': 'SC-005',
                'name': 'Phase 4 (단순 Fermi - 템플릿 활용 가능)',
                'phase': 4,
                'complexity': 'complex',
                'prompt': '''서울의 피아노 학원 수를 추정하세요.

다음 접근을 고려하세요:
1. Top-down: 인구 기반 (서울 인구 1000만)
2. Bottom-up: 학생 수 기반 (초중고생 100만)

각 모형을 실행하고 평균을 구하세요.

JSON 형식:
{"value": 숫자, "models": [{"name": "모형1", "result": 값}, {"name": "모형2", "result": 값}], "confidence": 0.5-0.7, "reasoning": "요약"}''',
                'expected_answer': '2,000-3,500개',
                'evaluation_criteria': [
                    '합리적 범위 (2000-3500)',
                    '2개 이상 모형 사용',
                    '각 모형 논리 명확',
                    '검증 단계 포함'
                ]
            },
            
            {
                'id': 'SC-006',
                'name': 'Phase 4 (복잡 Fermi - 창의적 분해)',
                'phase': 4,
                'complexity': 'very_complex',
                'prompt': '''한국 성인 피아노 학습 시장의 연간 총 매출을 추정하세요.

고려할 요소:
- 학습자 수 (학원 + 온라인 + 개인교습)
- 각 채널별 가격
- 교재, 악기 구매 등 부가 지출

창의적으로 모형을 만들고, 여러 접근을 시도하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "models": [...], "confidence": 0.4-0.6, "reasoning_detail": "상세 근거"}''',
                'expected_answer': '1,000억-5,000억원',
                'evaluation_criteria': [
                    '창의적 모형 생성',
                    '다각도 접근 (3개 이상 모형)',
                    '변수 간 관계 이해',
                    '합리적 결과'
                ]
            }
        ]
    
    def test_single_scenario(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """
        단일 시나리오 테스트 (.env 설정 무시)
        """
        print(f"\n{'='*80}")
        print(f"📝 시나리오: {scenario['name']}")
        print(f"🤖 모델: {model}")
        print(f"{'='*80}\n")
        
        # 프롬프트 출력
        print("📋 프롬프트:")
        print("-" * 80)
        print(scenario['prompt'])
        print("-" * 80)
        print()
        
        # API 호출
        print(f"⏳ {model} 호출 중...\n")
        start_time = time.time()
        
        try:
            # 모델별 분기 (o1/o3/o4는 다른 파라미터)
            if model.startswith('o1') or model.startswith('o3') or model.startswith('o4'):
                # Thinking 모델 (system, temperature, response_format 미지원)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": scenario['prompt']}
                    ]
                )
            elif 'nano' in model or 'gpt-5' in model:
                # nano/gpt-5 모델 (temperature 기본값만 지원)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "당신은 시장 분석 전문가입니다. 항상 JSON 형식으로만 답변하세요."},
                        {"role": "user", "content": scenario['prompt']}
                    ],
                    response_format={"type": "json_object"}
                )
            else:
                # 일반 모델 (모든 파라미터 지원)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "당신은 시장 분석 전문가입니다. 항상 JSON 형식으로만 답변하세요."},
                        {"role": "user", "content": scenario['prompt']}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
            
            elapsed = time.time() - start_time
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {'raw_response': content, 'parse_error': True}
            
            # 비용 계산
            usage = response.usage
            cost = self._calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)
            
            # 응답 출력
            print("✅ 응답 받음")
            print(f"   비용: ${cost:.6f}")
            print(f"   시간: {elapsed:.2f}초")
            print(f"   토큰: {usage.total_tokens} ({usage.prompt_tokens}→{usage.completion_tokens})")
            print()
            print("📄 응답 내용:")
            print("-" * 80)
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            print("-" * 80)
            print()
            
            # 기대 답변 출력
            print("🎯 기대 답변:")
            print(f"   {scenario['expected_answer']}")
            print()
            
            # 평가 기준 출력
            print("📊 평가 기준:")
            for idx, criterion in enumerate(scenario['evaluation_criteria'], 1):
                print(f"   {idx}. {criterion}")
            print()
            
            # 사용자 평가 받기 (auto_mode에서는 건너뛰기)
            if hasattr(self, 'auto_mode') and self.auto_mode:
                quality_score = {'quality_score': None, 'auto_mode': True}
            else:
                quality_score = self._get_user_evaluation(scenario)
            
            # 결과 구성
            result = {
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'complexity': scenario['complexity'],
                'response': parsed,
                'expected': scenario['expected_answer'],
                'tokens': {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                },
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'user_evaluation': quality_score,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            return result
        
        except Exception as e:
            elapsed = time.time() - start_time
            
            print(f"❌ 오류 발생: {str(e)}")
            print()
            
            return {
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'error': str(e),
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'user_evaluation': {'quality': 0, 'reason': 'API 오류'}
            }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        if model not in self.pricing:
            return 0.0
        
        rates = self.pricing[model]
        cost = (input_tokens / 1_000_000 * rates['input'] +
                output_tokens / 1_000_000 * rates['output'])
        return round(cost, 8)
    
    def _get_user_evaluation(self, scenario: Dict) -> Dict[str, Any]:
        """
        사용자 평가 입력
        """
        print("="*80)
        print("👤 사용자 평가")
        print("="*80)
        print()
        
        # 품질 점수 (0-100)
        while True:
            try:
                quality_input = input("품질 점수 (0-100, Enter=건너뛰기): ").strip()
                
                if quality_input == '':
                    quality = None
                    break
                
                quality = int(quality_input)
                
                if 0 <= quality <= 100:
                    break
                else:
                    print("⚠️ 0-100 사이 값을 입력하세요.")
            except ValueError:
                print("⚠️ 숫자를 입력하세요.")
        
        # 세부 평가
        if quality is not None:
            print()
            print("세부 평가 (각 항목 y/n):")
            
            evaluations = {}
            for idx, criterion in enumerate(scenario['evaluation_criteria'], 1):
                while True:
                    answer = input(f"  {idx}. {criterion}? (y/n/Enter=skip): ").strip().lower()
                    if answer in ['y', 'n', '']:
                        evaluations[f'criterion_{idx}'] = answer if answer else 'skip'
                        break
            
            # 코멘트
            print()
            comment = input("코멘트 (선택, Enter=건너뛰기): ").strip()
            
            return {
                'quality_score': quality,
                'evaluations': evaluations,
                'comment': comment if comment else None,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'quality_score': None,
                'skipped': True,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_interactive_benchmark(
        self,
        models: List[str] = None,
        scenarios: List[str] = None,
        output_file: str = None,
        auto_mode: bool = False
    ):
        """
        인터랙티브 벤치마크 실행
        
        Args:
            models: 테스트할 모델 리스트 (None=전체)
            scenarios: 테스트할 시나리오 ID (None=전체)
            output_file: 결과 파일명
            auto_mode: 자동 모드 (확인 건너뛰기, 평가 건너뛰기)
        """
        print("="*80)
        print("🎯 OpenAI 모델 인터랙티브 벤치마크")
        print("="*80)
        print()
        
        # API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            return
        
        print(f"✅ API 키 확인: {api_key[:20]}...\n")
        
        # 테스트 대상
        test_models = models if models else self.models_to_test
        all_scenarios = self.get_test_scenarios()
        
        if scenarios:
            test_scenarios = [s for s in all_scenarios if s['id'] in scenarios]
        else:
            test_scenarios = all_scenarios
        
        print(f"테스트 모델: {len(test_models)}개")
        print(f"테스트 시나리오: {len(test_scenarios)}개")
        print(f"총 테스트 수: {len(test_models) * len(test_scenarios)}개")
        
        if auto_mode:
            print("⚡ 자동 모드: 평가 없이 응답만 수집")
        
        print()
        
        # 확인 (auto_mode에서는 건너뛰기)
        if not auto_mode:
            proceed = input("진행하시겠습니까? (y/n): ").strip().lower()
            if proceed != 'y':
                print("취소되었습니다.")
                return
        
        self.auto_mode = auto_mode
        
        # 테스트 진행
        total_tests = len(test_models) * len(test_scenarios)
        test_count = 0
        
        for model in test_models:
            print(f"\n{'#'*80}")
            print(f"# 모델: {model}")
            print(f"# 가격: ${self.pricing.get(model, {}).get('input', 0)}/1M 입력, ${self.pricing.get(model, {}).get('output', 0)}/1M 출력")
            print(f"{'#'*80}")
            
            for scenario in test_scenarios:
                test_count += 1
                print(f"\n진행: {test_count}/{total_tests}")
                
                result = self.test_single_scenario(model, scenario)
                self.results.append(result)
                
                # 중간 저장
                if test_count % 5 == 0:
                    self._save_intermediate()
                
                # 계속 진행 확인 (auto_mode에서는 건너뛰기)
                if test_count < total_tests and not self.auto_mode:
                    print()
                    cont = input("계속 진행? (y/Enter=yes, n=중단, s=저장 후 중단): ").strip().lower()
                    
                    if cont == 'n':
                        print("\n⚠️ 벤치마크 중단")
                        break
                    elif cont == 's':
                        print("\n⚠️ 저장 후 중단")
                        self.save_final_results(output_file)
                        return
                else:
                    cont = 'y'  # auto_mode에서는 항상 계속
            
            if test_count < total_tests and cont == 'n':
                break
        
        # 최종 결과 저장
        self.save_final_results(output_file)
        
        # 리포트 생성
        self.generate_report()
    
    def _save_intermediate(self):
        """중간 저장"""
        filename = f"benchmark_intermediate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 중간 저장: {filename}")
    
    def save_final_results(self, output_file: Optional[str] = None):
        """최종 결과 저장"""
        if output_file is None:
            output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.results),
                    'successful_tests': sum(1 for r in self.results if r['success'])
                },
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 최종 결과 저장: {output_file}")
        print(f"   총 {len(self.results)}개 테스트")
    
    def generate_report(self):
        """리포트 생성"""
        print(f"\n{'='*80}")
        print("📊 벤치마크 리포트")
        print(f"{'='*80}\n")
        
        # 기본 통계
        success_results = [r for r in self.results if r['success']]
        evaluated_results = [r for r in success_results if r.get('user_evaluation', {}).get('quality_score') is not None]
        
        print(f"총 테스트: {len(self.results)}개")
        print(f"성공: {len(success_results)}개")
        print(f"사용자 평가: {len(evaluated_results)}개")
        print()
        
        # Auto 모드일 때 기본 리포트
        if not evaluated_results:
            print("⚠️ 평가된 결과가 없습니다 (자동 모드)")
            print()
            print("응답 수집 완료!")
            print(f"결과 파일에서 각 모델의 응답을 확인하세요.")
            print()
            
            # 비용/시간 통계만 출력
            print(f"{'='*80}")
            print("모델별 비용/시간 통계")
            print(f"{'='*80}\n")
            
            model_stats = {}
            for result in success_results:
                model = result['model']
                if model not in model_stats:
                    model_stats[model] = {'costs': [], 'times': []}
                
                model_stats[model]['costs'].append(result['cost'])
                model_stats[model]['times'].append(result['elapsed_seconds'])
            
            print(f"{'모델':20s} | {'평균 비용':12s} | {'평균 시간':10s} | 테스트 수")
            print("-" * 70)
            
            for model, stats in model_stats.items():
                avg_cost = sum(stats['costs']) / len(stats['costs'])
                avg_time = sum(stats['times']) / len(stats['times'])
                
                print(f"{model:20s} | ${avg_cost:.6f}   | {avg_time:6.2f}초   | {len(stats['costs'])}개")
            
            return
        
        # 모델별 통계
        print(f"{'='*80}")
        print("모델별 성능 요약")
        print(f"{'='*80}\n")
        
        model_stats = {}
        for result in evaluated_results:
            model = result['model']
            
            if model not in model_stats:
                model_stats[model] = {
                    'quality_scores': [],
                    'costs': [],
                    'times': [],
                    'phases': {}
                }
            
            quality = result['user_evaluation']['quality_score']
            model_stats[model]['quality_scores'].append(quality)
            model_stats[model]['costs'].append(result['cost'])
            model_stats[model]['times'].append(result['elapsed_seconds'])
            
            phase = result.get('phase', 0)
            if phase not in model_stats[model]['phases']:
                model_stats[model]['phases'][phase] = []
            model_stats[model]['phases'][phase].append(quality)
        
        # 모델별 평균
        print(f"{'모델':20s} | {'평균 품질':10s} | {'평균 비용':12s} | {'평균 시간':10s} | 가성비")
        print("-" * 80)
        
        model_summaries = []
        for model, stats in model_stats.items():
            avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
            avg_cost = sum(stats['costs']) / len(stats['costs'])
            avg_time = sum(stats['times']) / len(stats['times'])
            
            # 가성비 = 품질 / 비용
            value_score = avg_quality / (avg_cost * 1000000) if avg_cost > 0 else 0
            
            model_summaries.append({
                'model': model,
                'avg_quality': avg_quality,
                'avg_cost': avg_cost,
                'avg_time': avg_time,
                'value_score': value_score,
                'test_count': len(stats['quality_scores'])
            })
            
            print(f"{model:20s} | {avg_quality:8.1f}점  | ${avg_cost:.6f}   | {avg_time:6.2f}초   | {value_score:8.0f}")
        
        # 가성비 TOP 3
        print(f"\n{'='*80}")
        print("🏆 가성비 TOP 3")
        print(f"{'='*80}\n")
        
        model_summaries.sort(key=lambda m: m['value_score'], reverse=True)
        
        for idx, summary in enumerate(model_summaries[:3], 1):
            print(f"{idx}위: {summary['model']}")
            print(f"   품질: {summary['avg_quality']:.1f}점")
            print(f"   비용: ${summary['avg_cost']:.6f}/작업")
            print(f"   시간: {summary['avg_time']:.2f}초")
            print(f"   가성비: {summary['value_score']:.0f}")
            print()
        
        # Phase별 분석
        print(f"{'='*80}")
        print("Phase별 성능 분석")
        print(f"{'='*80}\n")
        
        for model, stats in model_stats.items():
            if len(stats['phases']) > 1:
                print(f"{model}:")
                for phase, scores in sorted(stats['phases'].items()):
                    avg_score = sum(scores) / len(scores)
                    print(f"   Phase {phase}: {avg_score:.1f}점 ({len(scores)}개 테스트)")
                print()
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        if model not in self.pricing:
            return 0.0
        
        rates = self.pricing[model]
        cost = (input_tokens / 1_000_000 * rates['input'] +
                output_tokens / 1_000_000 * rates['output'])
        return cost


def quick_test_mode(auto: bool = False):
    """
    빠른 테스트 모드 (nano 모델만, 간단한 시나리오만)
    
    Args:
        auto: 자동 모드 (평가 없이 응답만 수집)
    """
    print("🚀 빠른 테스트 모드 (nano 모델 + Phase 0-3)")
    if auto:
        print("⚡ 자동 모드: 평가 건너뛰기, 응답만 수집")
    print()
    
    benchmark = InteractiveBenchmark()
    
    # nano 모델만
    test_models = ['gpt-5-nano', 'gpt-4.1-nano', 'gpt-4o-mini']
    
    # Phase 0-3만
    test_scenarios = ['SC-001', 'SC-002', 'SC-003']
    
    benchmark.run_interactive_benchmark(
        models=test_models,
        scenarios=test_scenarios,
        output_file='benchmark_nano_quick.json',
        auto_mode=auto
    )


def phase_by_phase_mode():
    """
    Phase별 테스트 모드
    """
    print("📊 Phase별 테스트 모드")
    print()
    print("테스트할 Phase를 선택하세요:")
    print("  0: Phase 0 (Literal)")
    print("  1: Phase 2 (계산)")
    print("  2: Phase 3 (템플릿 있음)")
    print("  3: Phase 3 (템플릿 없음)")
    print("  4: Phase 4 (단순)")
    print("  5: Phase 4 (복잡)")
    print()
    
    phase_choice = input("선택 (0-5): ").strip()
    
    scenario_map = {
        '0': ['SC-001'],
        '1': ['SC-002'],
        '2': ['SC-003'],
        '3': ['SC-004'],
        '4': ['SC-005'],
        '5': ['SC-006']
    }
    
    if phase_choice not in scenario_map:
        print("⚠️ 잘못된 선택입니다.")
        return
    
    # 모델 선택
    print()
    print("테스트할 모델을 선택하세요:")
    print("  1: nano 모델 (gpt-5-nano, gpt-4.1-nano, gpt-4o-mini)")
    print("  2: mini 모델 (gpt-5-mini, gpt-4.1-mini, gpt-4o-mini)")
    print("  3: standard 모델 (gpt-4o, gpt-4.1, gpt-5.1)")
    print("  4: thinking 모델 (o1-mini, o3-mini, o3)")
    print("  5: 전체")
    print()
    
    model_choice = input("선택 (1-5): ").strip()
    
    benchmark = InteractiveBenchmark()
    
    model_groups = {
        '1': benchmark.models['nano'],
        '2': benchmark.models['mini'],
        '3': benchmark.models['standard'],
        '4': benchmark.models['thinking'],
        '5': benchmark.models_to_test
    }
    
    if model_choice not in model_groups:
        print("⚠️ 잘못된 선택입니다.")
        return
    
    test_models = model_groups[model_choice]
    test_scenarios = scenario_map[phase_choice]
    
    print()
    print(f"✅ 테스트 구성:")
    print(f"   모델: {len(test_models)}개")
    print(f"   시나리오: {len(test_scenarios)}개")
    print(f"   총: {len(test_models) * len(test_scenarios)}개 테스트")
    print()
    
    benchmark.run_interactive_benchmark(
        models=test_models,
        scenarios=test_scenarios,
        output_file=f'benchmark_phase{phase_choice}.json'
    )


def main():
    """
    메인 메뉴
    """
    import sys
    
    # 커맨드라인 인자 확인
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'quick' or mode == '1':
            print("🚀 빠른 테스트 모드 (자동 실행)")
            print()
            quick_test_mode(auto=True)
            return
        elif mode == 'quick-interactive':
            print("🚀 빠른 테스트 모드 (인터랙티브)")
            print()
            quick_test_mode(auto=False)
            return
        elif mode == 'phase':
            phase_by_phase_mode()
            return
        elif mode == 'full':
            benchmark = InteractiveBenchmark()
            benchmark.run_interactive_benchmark()
            return
        else:
            print(f"⚠️ 알 수 없는 모드: {mode}")
            print("사용법: python interactive_model_benchmark.py [quick|phase|full]")
            return
    
    # 인터랙티브 모드
    print("="*80)
    print("OpenAI 모델 벤치마크 도구")
    print("="*80)
    print()
    print("모드를 선택하세요:")
    print("  1: 빠른 테스트 (nano 모델 + Phase 0-3, 9개 테스트)")
    print("  2: Phase별 테스트 (선택적)")
    print("  3: 전체 벤치마크 (모든 모델 + 모든 시나리오)")
    print()
    
    choice = input("선택 (1-3): ").strip()
    
    if choice == '1':
        quick_test_mode()
    elif choice == '2':
        phase_by_phase_mode()
    elif choice == '3':
        benchmark = InteractiveBenchmark()
        benchmark.run_interactive_benchmark()
    else:
        print("⚠️ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()

