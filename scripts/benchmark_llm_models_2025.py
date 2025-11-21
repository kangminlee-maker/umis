#!/usr/bin/env python3
"""
LLM 모델 성능 벤치마크 (2025-11-20 업데이트)
OpenAI + Anthropic 모델 종합 테스트
UMIS Estimator 5-Phase 추론 능력 평가
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
import anthropic
import backoff

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()


class LLMBenchmark2025:
    """
    LLM 모델 종합 벤치마크 (2025)
    """
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # 테스트할 모델 (2025-11-20 최신)
        self.models = {
            'openai_mini': [
                'gpt-4o-mini'
            ],
            'openai_standard': [
                'gpt-4o'
            ],
            'openai_thinking': [
                'o1-mini'
            ],
            'claude_haiku': [
                'claude-haiku-3.5'
            ],
            'claude_sonnet': [
                'claude-sonnet-3.5'
            ],
            'claude_opus': [
                'claude-opus-3'
            ]
        }
        
        # 가격 정보 ($/1M 토큰) - 2025-11-20 기준
        self.pricing = {
            # OpenAI (Standard Tier) - 현재 사용 가능한 모델
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'o1-mini': {'input': 1.10, 'output': 4.40},
            'o1': {'input': 15.00, 'output': 60.00},
            
            # Claude (Standard Tier) - 현재 사용 가능한 모델
            'claude-haiku-3.5': {'input': 0.80, 'output': 4.00},
            'claude-sonnet-3.5': {'input': 3.00, 'output': 15.00},
            'claude-opus-3': {'input': 15.00, 'output': 75.00}
        }
        
        # Claude API 이름 매핑 (2025-11-21 업데이트)
        self.model_api_names = {
            # Claude
            'claude-haiku-3.5': 'claude-3-5-haiku-20241022',
            'claude-sonnet-3.5': 'claude-3-5-sonnet-20241022',
            'claude-sonnet-3.7': 'claude-3-7-sonnet-20250219',
            'claude-sonnet-4': 'claude-sonnet-4-20250514',
            'claude-sonnet-4.5': 'claude-sonnet-4-5-20250929',
            'claude-haiku-4.5': 'claude-haiku-4-5-20251001',
            'claude-opus-3': 'claude-3-opus-20240229',
            'claude-opus-4': 'claude-opus-4-20250514',
            'claude-opus-4.1': 'claude-opus-4-1-20250805'
        }
        
        # 결과 저장
        self.results = []
    
    def run_full_benchmark(self, 
                          test_openai: bool = True,
                          test_claude: bool = True,
                          output_file: Optional[str] = None):
        """
        전체 벤치마크 실행
        """
        print("🚀 LLM 모델 벤치마크 시작 (2025-11-20)")
        print(f"   테스트 시나리오: {len(self.get_test_scenarios())}개")
        
        total_models = 0
        if test_openai:
            total_models += sum(len(models) for cat, models in self.models.items() if 'openai' in cat)
        if test_claude:
            total_models += sum(len(models) for cat, models in self.models.items() if 'claude' in cat)
        
        print(f"   테스트 모델: {total_models}개")
        print()
        
        scenarios = self.get_test_scenarios()
        
        for scenario_idx, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*100}")
            print(f"시나리오 {scenario_idx}/{len(scenarios)}: {scenario['name']}")
            print(f"{'='*100}")
            
            # OpenAI 모델 테스트
            if test_openai:
                for category, models in self.models.items():
                    if 'openai' not in category:
                        continue
                    
                    print(f"\n📦 {category}")
                    for model in models:
                        try:
                            result = self.test_openai_model(model, scenario)
                            self.results.append(result)
                            self._print_result(result)
                            
                            # Rate limiting: 더 긴 대기 시간 적용
                            if model.startswith('o'):  # thinking 모델은 더 긴 대기
                                time.sleep(3)
                            else:
                                time.sleep(1.5)
                        
                        except Exception as e:
                            print(f"   ❌ {model}: 오류 - {str(e)}")
                            self.results.append({
                                'provider': 'openai',
                                'model': model,
                                'scenario': scenario['name'],
                                'error': str(e),
                                'timestamp': datetime.now().isoformat(),
                                'success': False
                            })
                            # 오류 발생 시 더 긴 대기
                            time.sleep(3)
            
            # Claude 모델 테스트
            if test_claude:
                for category, models in self.models.items():
                    if 'claude' not in category:
                        continue
                    
                    print(f"\n📦 {category}")
                    for model in models:
                        try:
                            result = self.test_claude_model(model, scenario)
                            self.results.append(result)
                            self._print_result(result)
                            
                            # Rate limiting: Claude도 긴 대기 시간 적용
                            time.sleep(2)
                        
                        except Exception as e:
                            print(f"   ❌ {model}: 오류 - {str(e)}")
                            self.results.append({
                                'provider': 'claude',
                                'model': model,
                                'scenario': scenario['name'],
                                'error': str(e),
                                'timestamp': datetime.now().isoformat(),
                                'success': False
                            })
                            # 오류 발생 시 더 긴 대기
                            time.sleep(3)
        
        # 결과 저장
        self.save_results(output_file)
        
        # 분석 리포트 생성
        self.generate_report()
    
    def get_test_scenarios(self) -> List[Dict]:
        """
        UMIS Estimator 5-Phase 테스트 시나리오
        """
        return [
            {
                'id': 'phase0_literal',
                'name': 'Phase 0 (Literal Lookup)',
                'phase': 0,
                'category': 'simple',
                'prompt': '''다음 데이터에서 "한국 B2B SaaS 월 ARPU"를 찾아 반환하세요:

데이터:
- 미국 B2C SaaS ARPU: $50
- 한국 B2B SaaS 월 ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

JSON 형식으로 답변:
{"value": 숫자, "unit": "원", "confidence": 1.0, "source": "literal"}''',
                'expected': {
                    'value': 200000,
                    'unit': '원',
                    'confidence': 1.0
                }
            },
            
            {
                'id': 'phase1_direct_rag',
                'name': 'Phase 1 (Direct RAG)',
                'phase': 1,
                'category': 'simple',
                'prompt': '''다음은 RAG 검색 결과입니다. 코웨이 렌탈 ARPU를 추출하세요:

[검색 결과]
코웨이 2024년 렌탈 사업 실적:
- 월 렌탈료: 33,000원
- 구독자 수: 720만 명
- 렌탈 매출: 2.85조원

JSON 형식으로 답변:
{"value": 숫자, "unit": "원", "confidence": 1.0, "source": "rag"}''',
                'expected': {
                    'value': 33000,
                    'unit': '원',
                    'confidence': 1.0
                }
            },
            
            {
                'id': 'phase2_validator_search',
                'name': 'Phase 2 (Validator Search + Calculation)',
                'phase': 2,
                'category': 'simple',
                'prompt': '''다음 공식을 사용하여 LTV를 계산하세요:

공식: LTV = ARPU / Churn_Rate

주어진 값:
- ARPU: 80,000원
- Churn_Rate: 0.05 (월 5%)

JSON 형식으로 답변:
{"value": 숫자, "unit": "원", "formula": "ARPU/Churn", "confidence": 1.0}''',
                'expected': {
                    'value': 1600000,
                    'confidence': 1.0
                }
            },
            
            {
                'id': 'phase3_template',
                'name': 'Phase 3 (Guestimation - Template)',
                'phase': 3,
                'category': 'medium',
                'prompt': '''B2B SaaS 한국 시장 ARPU를 추정하세요.

참고 템플릿:
- 글로벌 B2B SaaS ARPU: $100
- 한국 GDP per capita: 글로벌 대비 60%
- B2B premium: B2C 대비 3배

추정 모형:
1. 글로벌 기준 조정: $100 × 0.6 = $60
2. B2B premium 적용: $60 × 3 = $180
3. 환율 적용: $180 × 1,300 = 234,000원
4. 반올림: 200,000원

이 템플릿을 따라 답변하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "reasoning": "한 문장", "models": ["model1"]}''',
                'expected': {
                    'value_range': [150000, 250000],
                    'confidence_min': 0.70
                }
            },
            
            {
                'id': 'phase3_no_template',
                'name': 'Phase 3 (Guestimation - No Template)',
                'phase': 3,
                'category': 'medium',
                'prompt': '''한국 온라인 성인 취미 교육 플랫폼의 월 구독료를 추정하세요.

고려 사항:
- 타겟: 직장인, 30-40대
- 경쟁사: 클래스101, 탈잉 등
- 콘텐츠: 악기, 미술, 요리 등

창의적으로 모형을 만들어 답변하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "reasoning": "요약", "models": ["model1", "model2"]}''',
                'expected': {
                    'value_range': [10000, 50000],
                    'confidence_min': 0.60
                }
            },
            
            {
                'id': 'phase4_simple_fermi',
                'name': 'Phase 4 (Simple Fermi Decomposition)',
                'phase': 4,
                'category': 'complex',
                'prompt': '''서울의 피아노 학원 수를 Fermi 분해로 추정하세요.

단계:
1. 어떤 변수가 필요한가?
2. 각 변수를 어떻게 구할까?
3. 어떤 모형을 사용할까?
4. 결과가 합리적인가?

JSON 형식:
{"value": 숫자, "unit": "개", "confidence": 0.0-1.0, "decomposition": {"var1": 값, "var2": 값}, "models": [...], "reasoning": "요약"}''',
                'expected': {
                    'value_range': [1500, 4000],
                    'confidence_min': 0.60
                }
            },
            
            {
                'id': 'phase4_complex_fermi',
                'name': 'Phase 4 (Complex Fermi - Multi-layer)',
                'phase': 4,
                'category': 'very_complex',
                'prompt': '''한국 성인 피아노 학습자의 연간 총 지출액을 추정하세요.

고려할 요소:
- 학습자 수 (어떻게 추정?)
- 학원비 (월 평균)
- 교재비 (연간)
- 악기 구매/렌탈 (비율)
- 기타 비용 (조율, 액세서리 등)

여러 모형을 시도하고, 재귀적으로 변수를 추정하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "decomposition": {...}, "models": [...], "recursive_estimates": {...}, "reasoning_detail": "상세 설명"}''',
                'expected': {
                    'value_range': [50000000000, 500000000000],  # 500억-5000억
                    'confidence_min': 0.50
                }
            },
            
            {
                'id': 'phase4_creative_synthesis',
                'name': 'Phase 4 (Creative Synthesis)',
                'phase': 4,
                'category': 'very_complex',
                'prompt': '''한국에서 "구독형 피아노 렌탈 + 온라인 레슨" 결합 서비스의 적정 월 구독료를 추정하세요.

고려 사항:
- 기존 피아노 렌탈비
- 기존 대면 레슨비
- 온라인 할인율
- 결합 할인
- WTP (지불 의향)
- 경쟁 대안

창의적으로 여러 접근을 시도하고, 최종 값에 수렴하세요.

JSON 형식:
{"value": 숫자, "unit": "원", "confidence": 0.0-1.0, "models": [...], "creative_approaches": [...], "final_reasoning": "종합 판단"}''',
                'expected': {
                    'value_range': [80000, 200000],
                    'confidence_min': 0.55
                }
            }
        ]
    
    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=30,
        giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
    )
    def _call_openai_with_retry(self, api_params: Dict) -> Any:
        """OpenAI API 호출 with retry"""
        return self.openai_client.chat.completions.create(**api_params)
    
    def test_openai_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """OpenAI 모델 테스트"""
        start_time = time.time()
        
        try:
            # 모델 타입 구분
            is_o_series = model.startswith(('o1', 'o3', 'o4'))  # o1/o3/o4 시리즈
            is_gpt5 = model.startswith('gpt-5')  # gpt-5 시리즈
            is_reasoning_model = is_o_series or is_gpt5
            
            messages = [{"role": "user", "content": scenario['prompt']}]
            
            if not is_reasoning_model:
                messages.insert(0, {
                    "role": "system",
                    "content": "당신은 시장 분석 전문가입니다. 항상 JSON 형식으로만 답변하세요."
                })
            
            # API 호출 파라미터 구성
            api_params = {
                "model": model,
                "messages": messages
            }
            
            # 파라미터 추가 (모델별 차별화)
            if is_reasoning_model:
                # o1/o3/o4: low/medium/high, gpt-5: minimal/low/medium/high
                if is_o_series:
                    api_params["reasoning_effort"] = "medium"  # o 시리즈 기본값
                else:  # gpt-5
                    api_params["reasoning_effort"] = "low"  # gpt-5 균형잡힌 설정
            else:
                # 일반 모델: temperature 사용
                api_params["temperature"] = 0.2
                api_params["response_format"] = {"type": "json_object"}
            
            # API 호출 with retry
            response = self._call_openai_with_retry(api_params)
            
            elapsed = time.time() - start_time
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # JSON 추출 시도 (```json ... ``` 블록 또는 일반 JSON)
            try:
                # 코드 블록 내 JSON 추출
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
                parsed = {'raw_response': content, 'parse_error': True}
            
            # 비용 계산
            usage = response.usage
            cost = self._calculate_cost(
                model,
                usage.prompt_tokens,
                usage.completion_tokens
            )
            
            # 품질 평가
            quality_score = self._evaluate_quality(parsed, scenario.get('expected', {}))
            
            return {
                'provider': 'openai',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'category': scenario['category'],
                'response': parsed,
                'expected': scenario.get('expected'),
                'quality_score': quality_score,
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
                'provider': 'openai',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'error': str(e),
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=30,
        giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
    )
    def _call_claude_with_retry(self, api_params: Dict) -> Any:
        """Claude API 호출 with retry"""
        return self.anthropic_client.messages.create(**api_params)
    
    def test_claude_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """Claude 모델 테스트"""
        start_time = time.time()
        
        try:
            # API 모델 이름 변환
            api_model = self.model_api_names.get(model, model)
            
            # API 호출 파라미터 구성
            api_params = {
                "model": api_model,
                "max_tokens": 2048,
                "temperature": 0.2,
                "system": "당신은 시장 분석 전문가입니다. 항상 JSON 형식으로만 답변하세요.",
                "messages": [
                    {"role": "user", "content": scenario['prompt']}
                ]
            }
            
            # API 호출 with retry
            response = self._call_claude_with_retry(api_params)
            
            elapsed = time.time() - start_time
            
            # refusal 중지 이유 처리 (Claude 4.5 요구사항)
            if response.stop_reason == "refusal":
                return {
                    'provider': 'claude',
                    'model': model,
                    'scenario_id': scenario['id'],
                    'scenario_name': scenario['name'],
                    'phase': scenario['phase'],
                    'category': scenario['category'],
                    'error': 'Model refused to respond (safety/policy)',
                    'stop_reason': 'refusal',
                    'elapsed_seconds': round(elapsed, 2),
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
            
            # 응답 파싱
            content = response.content[0].text
            
            # JSON 추출 시도 (```json ... ``` 블록 또는 일반 JSON)
            try:
                # 코드 블록 내 JSON 추출
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
                parsed = {'raw_response': content, 'parse_error': True}
            
            # 비용 계산
            cost = self._calculate_cost(
                model,
                response.usage.input_tokens,
                response.usage.output_tokens
            )
            
            # 품질 평가
            quality_score = self._evaluate_quality(parsed, scenario.get('expected', {}))
            
            return {
                'provider': 'claude',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'category': scenario['category'],
                'response': parsed,
                'expected': scenario.get('expected'),
                'quality_score': quality_score,
                'tokens': {
                    'input': response.usage.input_tokens,
                    'output': response.usage.output_tokens,
                    'total': response.usage.input_tokens + response.usage.output_tokens
                },
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                'provider': 'claude',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
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
    
    def _evaluate_quality(self, response: Dict, expected: Dict) -> Dict[str, Any]:
        """품질 평가"""
        score = {
            'has_value': 'value' in response,
            'has_confidence': 'confidence' in response,
            'has_reasoning': 'reasoning' in response or 'reasoning_detail' in response,
            'has_models': 'models' in response or 'decomposition' in response,
            'json_valid': 'parse_error' not in response,
            'value_in_range': False,
            'confidence_sufficient': False
        }
        
        # 값 범위 체크
        if score['has_value'] and 'value_range' in expected:
            value = response.get('value')
            if isinstance(value, (int, float)):
                min_val, max_val = expected['value_range']
                score['value_in_range'] = min_val <= value <= max_val
        elif score['has_value'] and 'value' in expected:
            score['value_in_range'] = response.get('value') == expected['value']
        
        # 신뢰도 체크
        if score['has_confidence'] and 'confidence_min' in expected:
            confidence = response.get('confidence', 0)
            score['confidence_sufficient'] = confidence >= expected['confidence_min']
        
        # 총점 계산 (0-100)
        total_score = 0
        if score['json_valid']: total_score += 20
        if score['has_value']: total_score += 20
        if score['has_confidence']: total_score += 15
        if score['has_reasoning']: total_score += 15
        if score['has_models']: total_score += 10
        if score['value_in_range']: total_score += 15
        if score['confidence_sufficient']: total_score += 5
        
        score['total_score'] = total_score
        
        return score
    
    def _print_result(self, result: Dict):
        """결과 출력"""
        if not result['success']:
            print(f"   ❌ {result['model']}: {result.get('error', 'Unknown error')}")
            return
        
        response = result['response']
        quality = result['quality_score']
        
        print(f"\n   ✅ {result['model']}")
        print(f"      비용: ${result['cost']:.6f}")
        print(f"      시간: {result['elapsed_seconds']}초")
        print(f"      토큰: {result['tokens']['total']} ({result['tokens']['input']}→{result['tokens']['output']})")
        print(f"      품질: {quality['total_score']}/100")
        
        if 'value' in response:
            print(f"      답변: {response.get('value')} {response.get('unit', '')}")
            print(f"      신뢰도: {response.get('confidence', 'N/A')}")
        
        if 'reasoning' in response:
            reasoning = response['reasoning'][:80]
            print(f"      근거: {reasoning}...")
    
    def save_results(self, output_file: Optional[str] = None):
        """결과 저장"""
        if output_file is None:
            output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.results),
                    'success_count': sum(1 for r in self.results if r['success']),
                    'pricing_date': '2025-11-20'
                },
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장: {output_file}")
        print(f"   총 {len(self.results)}개 테스트")
    
    def generate_report(self):
        """분석 리포트 생성"""
        print(f"\n{'='*100}")
        print("📊 벤치마크 리포트 (2025-11-20)")
        print(f"{'='*100}\n")
        
        # 성공/실패 통계
        success_results = [r for r in self.results if r['success']]
        total_count = len(self.results)
        success_count = len(success_results)
        
        print(f"총 테스트: {total_count}개")
        print(f"성공: {success_count}개 ({success_count/total_count*100:.1f}%)")
        print(f"실패: {total_count - success_count}개")
        
        # Phase별 성능
        print(f"\n{'='*100}")
        print("Phase별 최적 모델")
        print(f"{'='*100}\n")
        
        phases = {}
        for result in success_results:
            phase = result.get('phase', -1)
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(result)
        
        for phase in sorted(phases.keys()):
            results = phases[phase]
            print(f"\n🔹 Phase {phase}")
            
            # 품질 점수 순 정렬
            sorted_by_quality = sorted(results, key=lambda r: r['quality_score']['total_score'], reverse=True)
            
            print(f"   TOP 3 (품질 기준):")
            for idx, result in enumerate(sorted_by_quality[:3], 1):
                model = result['model']
                score = result['quality_score']['total_score']
                cost = result['cost']
                elapsed = result['elapsed_seconds']
                print(f"   {idx}위: {model:25s} | 품질: {score:3d}/100 | ${cost:.6f} | {elapsed:4.1f}초")
            
            # 비용 순 정렬
            sorted_by_cost = sorted(results, key=lambda r: r['cost'])
            
            print(f"\n   TOP 3 (비용 기준):")
            for idx, result in enumerate(sorted_by_cost[:3], 1):
                model = result['model']
                score = result['quality_score']['total_score']
                cost = result['cost']
                print(f"   {idx}위: {model:25s} | ${cost:.6f} | 품질: {score:3d}/100")
        
        # 모델별 평균 성능
        print(f"\n{'='*100}")
        print("모델별 종합 성능")
        print(f"{'='*100}\n")
        
        model_stats = {}
        for result in success_results:
            model = result['model']
            if model not in model_stats:
                model_stats[model] = {
                    'provider': result['provider'],
                    'costs': [],
                    'times': [],
                    'quality_scores': []
                }
            
            model_stats[model]['costs'].append(result['cost'])
            model_stats[model]['times'].append(result['elapsed_seconds'])
            model_stats[model]['quality_scores'].append(result['quality_score']['total_score'])
        
        # 평균 계산
        model_averages = []
        for model, stats in model_stats.items():
            if not stats['costs']:
                continue
            
            avg_cost = sum(stats['costs']) / len(stats['costs'])
            avg_time = sum(stats['times']) / len(stats['times'])
            avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
            
            # 가성비 점수 (품질/비용)
            cost_efficiency = avg_quality / (avg_cost * 1000) if avg_cost > 0 else 0
            
            model_averages.append({
                'model': model,
                'provider': stats['provider'],
                'avg_cost': avg_cost,
                'avg_time': avg_time,
                'avg_quality': avg_quality,
                'cost_efficiency': cost_efficiency,
                'test_count': len(stats['costs'])
            })
        
        # 가성비 순 정렬
        model_averages.sort(key=lambda m: m['cost_efficiency'], reverse=True)
        
        print(f"{'모델':30s} | {'제공사':10s} | {'평균 비용':12s} | {'평균 품질':10s} | {'가성비':10s} | {'테스트'}")
        print("-" * 100)
        
        for avg in model_averages:
            provider_emoji = "🔵" if avg['provider'] == 'openai' else "🟣"
            print(f"{provider_emoji} {avg['model']:27s} | {avg['provider']:10s} | ${avg['avg_cost']:.6f}   | {avg['avg_quality']:6.1f}/100 | {avg['cost_efficiency']:8.1f}   | {avg['test_count']}개")
        
        # 최종 권장
        print(f"\n{'='*100}")
        print("🏆 최종 권장 (UMIS용)")
        print(f"{'='*100}\n")
        
        print("💎 최고 가성비 TOP 5:")
        for idx, avg in enumerate(model_averages[:5], 1):
            provider_emoji = "🔵" if avg['provider'] == 'openai' else "🟣"
            print(f"   {idx}위: {provider_emoji} {avg['model']:25s} | 가성비: {avg['cost_efficiency']:6.1f} | 품질: {avg['avg_quality']:5.1f}/100 | 비용: ${avg['avg_cost']:.6f}")
        
        # 비용 기준
        print("\n💰 최저 비용 TOP 3:")
        sorted_by_cost = sorted(model_averages, key=lambda m: m['avg_cost'])
        for idx, avg in enumerate(sorted_by_cost[:3], 1):
            provider_emoji = "🔵" if avg['provider'] == 'openai' else "🟣"
            print(f"   {idx}위: {provider_emoji} {avg['model']:25s} ${avg['avg_cost']:.6f}/작업 | 품질: {avg['avg_quality']:5.1f}/100")
        
        # 품질 기준
        print("\n🎯 최고 품질 TOP 3:")
        sorted_by_quality = sorted(model_averages, key=lambda m: m['avg_quality'], reverse=True)
        for idx, avg in enumerate(sorted_by_quality[:3], 1):
            provider_emoji = "🔵" if avg['provider'] == 'openai' else "🟣"
            print(f"   {idx}위: {provider_emoji} {avg['model']:25s} {avg['avg_quality']:.1f}/100 | 비용: ${avg['avg_cost']:.6f}/작업")


def main():
    """메인 실행"""
    print("=" * 100)
    print("LLM 모델 벤치마크 (2025-11-20)")
    print("=" * 100)
    print()
    
    # API 키 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    test_openai = bool(openai_key)
    test_claude = bool(anthropic_key)
    
    if not test_openai and not test_claude:
        print("❌ API 키가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.")
        return
    
    if test_openai:
        print(f"✅ OpenAI API 키 확인됨")
    if test_claude:
        print(f"✅ Anthropic API 키 확인됨")
    print()
    
    # 사용자 선택
    print("테스트 옵션:")
    print("1. 전체 모델 테스트 (느림, 비쌈)")
    print("2. 핵심 모델만 테스트 (권장)")
    print("3. 커스텀 선택")
    
    choice = input("\n선택 (1-3): ").strip()
    
    benchmark = LLMBenchmark2025()
    
    if choice == '2':
        # 핵심 모델만 (실제 사용 가능한 모델)
        benchmark.models = {
            'openai_mini': ['gpt-4o-mini'],
            'openai_standard': ['gpt-4o'],
            'openai_thinking': ['o1-mini'],
            'claude_haiku': ['claude-haiku-3.5'],
            'claude_sonnet': ['claude-sonnet-3.5'],
            'claude_opus': ['claude-opus-3']
        }
    
    try:
        benchmark.run_full_benchmark(
            test_openai=test_openai,
            test_claude=test_claude
        )
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

