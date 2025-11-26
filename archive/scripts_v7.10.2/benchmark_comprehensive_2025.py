#!/usr/bin/env python3
"""
종합 LLM 벤치마크 (2025-11-21)
OpenAI + Claude 전체 라인업 테스트
- 접근 가능한 모델만 테스트
- Extended Thinking 모드 포함
- 품질, 가격, 속도 종합 평가
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


class ComprehensiveLLMBenchmark:
    """종합 LLM 벤치마크"""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.anthropic_client = anthropic.Anthropic()
        
        # 테스트할 모델 (접근 가능한 모델만)
        self.models = {
            # OpenAI - nano (초저가)
            'openai_nano': [
                'gpt-4.1-nano',
                'gpt-5-nano'
            ],
            # OpenAI - mini (저가)
            'openai_mini': [
                'gpt-4o-mini',
                'gpt-4.1-mini',
                'gpt-5-mini'
            ],
            # OpenAI - standard (일반)
            'openai_standard': [
                'gpt-4o',
                'gpt-4.1',
                'gpt-5',
                'gpt-5.1'
            ],
            # OpenAI - codex (코드 특화)
            'openai_codex': [
                'gpt-5-codex',
                'gpt-5.1-codex'
            ],
            # OpenAI - pro (최고급)
            'openai_pro': [
                'gpt-5-pro'
            ],
            # OpenAI - thinking (o 시리즈)
            'openai_thinking': [
                'o1',
                'o3',
                'o3-mini',
                'o4-mini'
            ],
            # OpenAI - thinking pro
            'openai_thinking_pro': [
                'o1-pro'
            ],
            # Claude - standard (접근 가능한 모델만)
            'claude_standard': [
                'claude-haiku-3.5',
                'claude-sonnet-3.7',
                'claude-sonnet-4',
                'claude-opus-4'
            ]
        }
        
        # 가격 정보 ($/1M 토큰) - 2025-11-21 기준
        self.pricing = {
            # OpenAI nano
            'gpt-4.1-nano': {'input': 0.10, 'output': 0.40},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            # OpenAI mini
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            # OpenAI standard
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4.1': {'input': 2.00, 'output': 8.00},
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5.1': {'input': 1.25, 'output': 10.00},
            # OpenAI codex
            'gpt-5-codex': {'input': 1.25, 'output': 10.00},
            'gpt-5.1-codex': {'input': 1.25, 'output': 10.00},
            # OpenAI pro
            'gpt-5-pro': {'input': 15.00, 'output': 120.00},
            # OpenAI thinking
            'o1': {'input': 15.00, 'output': 60.00},
            'o3': {'input': 2.00, 'output': 8.00},
            'o3-mini': {'input': 1.10, 'output': 4.40},
            'o4-mini': {'input': 1.10, 'output': 4.40},
            'o1-pro': {'input': 150.00, 'output': 600.00},
            # Claude standard (실제 가격)
            'claude-haiku-3.5': {'input': 0.80, 'output': 4.00},
            'claude-sonnet-3.7': {'input': 3.00, 'output': 15.00},
            'claude-sonnet-4': {'input': 3.00, 'output': 15.00},
            'claude-opus-4': {'input': 15.00, 'output': 75.00}
        }
        
        # Claude API 이름 매핑 (2025-11-21 업데이트)
        # 참조: https://platform.claude.com/docs/ko/about-claude/models/migrating-to-claude-4
        self.claude_api_names = {
            'claude-haiku-3.5': 'claude-3-5-haiku-20241022',
            'claude-sonnet-3.7': 'claude-3-7-sonnet-20250219',
            'claude-sonnet-4': 'claude-sonnet-4-20250514',
            'claude-sonnet-4.5': 'claude-sonnet-4-5-20250929',  # Claude 4.5 (최신)
            'claude-haiku-4.5': 'claude-haiku-4-5-20251001',    # Claude 4.5 (최신)
            'claude-opus-4': 'claude-opus-4-20250514',
            'claude-opus-4.1': 'claude-opus-4-1-20250805'       # Claude 4.1 (최신)
        }
        
        # Responses API를 사용해야 하는 모델들
        self.responses_api_models = [
            'gpt-5-codex',
            'gpt-5.1-codex',
            'gpt-5-pro',
            'o1-pro'
        ]
        
        self.results = []
    
    def get_test_scenarios(self) -> List[Dict]:
        """UMIS 5-Phase 테스트 시나리오 (Phase별 최적 파라미터 + JSON Schema 포함)"""
        return [
            {
                'id': 'phase0',
                'name': 'Phase 0: Literal',
                'phase': 0,
                'prompt': '''데이터에서 "한국 B2B SaaS ARPU" 값을 정확히 찾아 추출하세요.

주어진 데이터:
- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C SaaS ARPU: 70,000원

요구사항: B2B SaaS 값만 추출, confidence는 1.0으로 설정''',
                'expected': {'value': 200000, 'confidence': 1.0},
                'temperature': 0.0,
                'reasoning_effort': 'low',
                'json_schema': {
                    "name": "literal_extraction",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "추출된 ARPU 값"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 1.0, "maximum": 1.0}
                        },
                        "required": ["value", "unit", "confidence"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase1',
                'name': 'Phase 1: Direct RAG',
                'phase': 1,
                'prompt': '''RAG 검색 결과에서 코웨이의 월 렌탈료를 추출하세요.

RAG 결과:
코웨이 렌탈 사업 개요
- 월 평균 렌탈료: 33,000원
- 총 구독자 수: 720만명
- 주요 제품: 정수기, 공기청정기, 비데

요구사항: 월 렌탈료만 추출, confidence는 1.0으로 설정''',
                'expected': {'value': 33000},
                'temperature': 0.0,
                'reasoning_effort': 'low',
                'json_schema': {
                    "name": "rag_extraction",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "월 렌탈료"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 1.0, "maximum": 1.0}
                        },
                        "required": ["value", "unit", "confidence"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase2',
                'name': 'Phase 2: Calculation',
                'phase': 2,
                'prompt': '''주어진 공식과 값을 사용하여 LTV를 계산하세요.

공식: LTV = ARPU / Churn_Rate

주어진 값:
- ARPU = 80,000원
- Churn_Rate = 0.05

계산 과정:
1. 공식에 값 대입
2. 나눗셈 수행
3. 결과를 원 단위로 표현

요구사항: 정확한 계산 결과, confidence는 1.0으로 설정''',
                'expected': {'value': 1600000},
                'temperature': 0.0,
                'reasoning_effort': 'low',
                'json_schema': {
                    "name": "calculation",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "계산된 LTV"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 1.0, "maximum": 1.0}
                        },
                        "required": ["value", "unit", "confidence"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase3_template',
                'name': 'Phase 3: Guestimation (템플릿)',
                'phase': 3,
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
- confidence는 0.7~1.0 범위''',
                'expected': {'value_range': [50000, 150000], 'confidence_min': 0.7},
                'temperature': 0.3,
                'reasoning_effort': 'medium',
                'json_schema': {
                    "name": "guestimation_template",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "추정된 ARPU"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "reasoning": {"type": "string", "maxLength": 200, "description": "추정 근거 요약"}
                        },
                        "required": ["value", "unit", "confidence", "reasoning"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase3_no_template',
                'name': 'Phase 3: Guestimation (템플릿 없음)',
                'phase': 3,
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
- confidence는 0.6~0.9 범위 (템플릿 없으므로 낮음)''',
                'expected': {'value_range': [10000, 50000], 'confidence_min': 0.6},
                'temperature': 0.5,
                'reasoning_effort': 'medium',
                'json_schema': {
                    "name": "guestimation_free",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "추정된 월 구독료"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "reasoning": {"type": "string", "maxLength": 200, "description": "추정 논리"}
                        },
                        "required": ["value", "unit", "confidence", "reasoning"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase4_simple',
                'name': 'Phase 4: Simple Fermi',
                'phase': 4,
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
- decomposition: 주요 변수와 값을 JSON 객체로 표현
- reasoning: 추정 논리를 단계별로 요약 (300자 이내)
- confidence: 0.6~0.8 범위''',
                'expected': {'value_range': [1500, 4000], 'confidence_min': 0.6},
                'temperature': 0.7,
                'reasoning_effort': 'high',
                'json_schema': {
                    "name": "fermi_simple",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "추정된 학원 수"},
                            "unit": {"type": "string", "enum": ["개"]},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "reasoning": {"type": "string", "maxLength": 300, "description": "단계별 추정 논리"}
                        },
                        "required": ["value", "unit", "confidence", "reasoning"],
                        "additionalProperties": False
                    }
                }
            },
            {
                'id': 'phase4_complex',
                'name': 'Phase 4: Complex Fermi',
                'phase': 4,
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
   - 최소 2개 모델 사용, models 배열에 명시

요구사항:
- decomposition: 주요 변수를 구조화된 JSON으로
- models: 사용한 추정 모델 목록 (예: ["top_down", "bottom_up"])
- reasoning: 각 모델의 논리와 최종 값 선택 근거 (500자 이내)
- confidence: 0.5~0.8 범위 (복잡도로 인한 불확실성)''',
                'expected': {'value_range': [50000000000, 500000000000], 'confidence_min': 0.5},
                'temperature': 0.8,
                'reasoning_effort': 'high',
                'json_schema': {
                    "name": "fermi_complex",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": "추정된 연간 총 지출액"},
                            "unit": {"type": "string", "enum": ["원"]},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "models": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                                "description": "사용한 추정 모델 목록"
                            },
                            "reasoning": {"type": "string", "maxLength": 500, "description": "모델별 논리와 최종 선택 근거"}
                        },
                        "required": ["value", "unit", "confidence", "models", "reasoning"],
                        "additionalProperties": False
                    }
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
        """OpenAI API 호출 with retry (exponential backoff)"""
        return self.openai_client.chat.completions.create(**api_params)
    
    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=30,
        giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
    )
    def _call_openai_responses_with_retry(self, model: str, input_text: str) -> Any:
        """OpenAI Responses API 호출 with retry (exponential backoff)"""
        return self.openai_client.responses.create(
            model=model,
            input=input_text
        )
    
    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=30,
        giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
    )
    def _call_claude_with_retry(self, api_params: Dict) -> Any:
        """Claude API 호출 with retry (exponential backoff)"""
        return self.anthropic_client.messages.create(**api_params)
    
    def test_openai_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """OpenAI 모델 테스트 (Chat Completions 또는 Responses API)"""
        
        # Responses API 모델인지 확인
        if model in self.responses_api_models:
            return self.test_openai_responses_model(model, scenario)
        
        # 기존 Chat Completions API 로직
        start_time = time.time()
        
        try:
            # 모델 타입 구분
            is_o_series = model.startswith(('o1', 'o3', 'o4'))  # o1/o3/o4 시리즈
            is_gpt5 = model.startswith('gpt-5')  # gpt-5 시리즈
            is_reasoning_model = is_o_series or is_gpt5
            
            # 프롬프트 준비
            user_prompt = scenario['prompt']
            
            # reasoning 모델용 JSON 강조 추가
            if is_reasoning_model:
                user_prompt += "\n\n⚠️ 중요: 반드시 순수 JSON 형식으로만 응답하세요. 어떠한 설명이나 마크다운 없이 JSON 객체만 출력하세요."
            
            messages = [{"role": "user", "content": user_prompt}]
            if not is_reasoning_model:
                messages.insert(0, {"role": "system", "content": "시장 분석 전문가. JSON만 반환."})
            
            # API 호출 파라미터 구성
            api_params = {
                "model": model,
                "messages": messages
            }
            
            # Phase별 최적 파라미터 사용
            if is_reasoning_model:
                # reasoning_effort 사용 (Phase별 차별화)
                reasoning_effort = scenario.get('reasoning_effort', 'medium')
                api_params["reasoning_effort"] = reasoning_effort
                
                # GPT-5 전용: verbosity 추가 (JSON 응답이므로 low)
                if is_gpt5:
                    api_params["verbosity"] = "low"  # 간결한 JSON 응답
                
                # reasoning 모델은 response_format을 지원하지 않음!
                # JSON Schema도 사용 불가
            else:
                # temperature 사용 (Phase별 차별화)
                temperature = scenario.get('temperature', 0.2)
                
                # Claude 범위 초과 방지 (0~1)
                if 'claude' in model.lower():
                    temperature = min(temperature, 1.0)
                
                api_params["temperature"] = temperature
                
                # JSON Schema 적용 (structured outputs) - 일반 모델만
                json_schema = scenario.get('json_schema')
                if json_schema:
                    api_params["response_format"] = {
                        "type": "json_schema",
                        "json_schema": json_schema
                    }
                else:
                    # fallback: 일반 json_object
                    api_params["response_format"] = {"type": "json_object"}
            
            # API 호출 with retry
            response = self._call_openai_with_retry(api_params)
            
            elapsed = time.time() - start_time
            content = response.choices[0].message.content
            
            # JSON 추출 (강화된 파싱)
            import re
            
            try:
                # 1. 마크다운 코드 블록 제거
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                # 2. JSON 객체 추출 (정규식)
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            # 토큰 사용량 (reasoning_tokens 포함)
            tokens = {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens,
                'total': response.usage.total_tokens
            }
            
            # reasoning_tokens 추가 (reasoning 모델만)
            if hasattr(response.usage, 'completion_tokens_details'):
                details = response.usage.completion_tokens_details
                if hasattr(details, 'reasoning_tokens') and details.reasoning_tokens:
                    tokens['reasoning'] = details.reasoning_tokens
            
            cost = self._calculate_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)
            quality = self._evaluate_quality(parsed, scenario.get('expected', {}), scenario['phase'])
            
            # 사용된 파라미터 기록
            used_params = {}
            if is_reasoning_model:
                used_params['reasoning_effort'] = api_params.get('reasoning_effort')
                if is_gpt5:
                    used_params['verbosity'] = api_params.get('verbosity')
            else:
                used_params['temperature'] = api_params.get('temperature')
            
            return {
                'provider': 'openai',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'response': parsed,
                'quality_score': quality,
                'tokens': tokens,
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'parameters': used_params,  # 사용된 파라미터 기록
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            return {
                'provider': 'openai',
                'model': model,
                'scenario_id': scenario['id'],
                'error': str(e),
                'elapsed_seconds': round(time.time() - start_time, 2),
                'success': False
            }
    
    def test_openai_responses_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """OpenAI Responses API 전용 테스트 (codex, pro 모델)"""
        start_time = time.time()
        
        try:
            # 프롬프트 준비
            input_text = scenario['prompt']
            
            # JSON 형식 요청 추가
            input_text += "\n\n⚠️ 중요: 반드시 순수 JSON 형식으로만 응답하세요."
            
            # Responses API 호출 with retry
            response = self._call_openai_responses_with_retry(model, input_text)
            
            elapsed = time.time() - start_time
            
            # output_text 추출
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output'):
                content = response.output
            else:
                content = str(response)
            
            # JSON 추출 (강화된 파싱)
            import re
            
            try:
                # 1. 마크다운 코드 블록 제거
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                # 2. JSON 객체 추출 (정규식)
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            # 토큰 사용량 (Responses API는 다를 수 있음)
            tokens = {
                'input': getattr(response, 'input_tokens', 0),
                'output': getattr(response, 'output_tokens', 0),
                'total': getattr(response, 'total_tokens', 0)
            }
            
            # 토큰이 0이면 추정 (문자 수 기반)
            if tokens['total'] == 0:
                tokens['input'] = len(input_text) // 4  # 대략적 추정
                tokens['output'] = len(content) // 4
                tokens['total'] = tokens['input'] + tokens['output']
            
            cost = self._calculate_cost(model, tokens['input'], tokens['output'])
            quality = self._evaluate_quality(parsed, scenario.get('expected', {}), scenario['phase'])
            
            return {
                'provider': 'openai_responses',
                'api_type': 'responses',
                'model': model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'response': parsed,
                'quality_score': quality,
                'tokens': tokens,
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            return {
                'provider': 'openai_responses',
                'api_type': 'responses',
                'model': model,
                'scenario_id': scenario['id'],
                'error': str(e),
                'elapsed_seconds': round(time.time() - start_time, 2),
                'success': False
            }
    
    def test_claude_model(self, model: str, scenario: Dict) -> Dict[str, Any]:
        """Claude 모델 테스트"""
        start_time = time.time()
        
        try:
            api_model = self.claude_api_names.get(model, model)
            
            # Phase별 최적 temperature 사용 (Claude는 0~1 범위)
            temperature = scenario.get('temperature', 0.2)
            temperature = min(temperature, 1.0)  # Claude는 최대 1.0
            
            # API 호출 파라미터 구성
            api_params = {
                "model": api_model,
                "max_tokens": 2048,
                "temperature": temperature,
                "system": "시장 분석 전문가. JSON만 반환.",
                "messages": [{"role": "user", "content": scenario['prompt']}]
            }
            
            # API 호출 with retry
            response = self._call_claude_with_retry(api_params)
            
            elapsed = time.time() - start_time
            
            # refusal 중지 이유 처리 (Claude 4.5 요구사항)
            if response.stop_reason == "refusal":
                return {
                    'provider': 'claude',
                    'model': model,
                    'api_model': api_model,
                    'scenario_id': scenario['id'],
                    'scenario_name': scenario['name'],
                    'phase': scenario['phase'],
                    'error': 'Model refused to respond (safety/policy)',
                    'stop_reason': 'refusal',
                    'elapsed_seconds': round(elapsed, 2),
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
            
            content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            # JSON 추출 시도 (강화된 파싱)
            import re
            
            try:
                # 1. 코드 블록 내 JSON 추출
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                # 2. JSON 객체 추출 (정규식)
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            cost = self._calculate_cost(model, 
                                       response.usage.input_tokens,
                                       response.usage.output_tokens)
            quality = self._evaluate_quality(parsed, scenario.get('expected', {}), scenario['phase'])
            
            return {
                'provider': 'claude',
                'model': model,
                'api_model': api_model,
                'scenario_id': scenario['id'],
                'scenario_name': scenario['name'],
                'phase': scenario['phase'],
                'response': parsed,
                'quality_score': quality,
                'tokens': {
                    'input': response.usage.input_tokens,
                    'output': response.usage.output_tokens,
                    'total': response.usage.input_tokens + response.usage.output_tokens
                },
                'cost': cost,
                'elapsed_seconds': round(elapsed, 2),
                'parameters': {'temperature': temperature},  # 사용된 파라미터 기록
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        except Exception as e:
            return {
                'provider': 'claude',
                'model': model,
                'scenario_id': scenario['id'],
                'error': str(e),
                'elapsed_seconds': round(time.time() - start_time, 2),
                'success': False
            }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        if model not in self.pricing:
            return 0.0
        rates = self.pricing[model]
        return round((input_tokens / 1_000_000 * rates['input'] + 
                     output_tokens / 1_000_000 * rates['output']), 6)
    
    def _evaluate_quality(self, response: Dict, expected: Dict, phase: int = 0) -> Dict[str, Any]:
        """품질 평가 (Phase별 차별화, 0-100점)"""
        score = {
            'has_value': 'value' in response,
            'has_confidence': 'confidence' in response,
            'has_reasoning': 'reasoning' in response,
            'json_valid': 'parse_error' not in response,
            'value_in_range': False,
            'confidence_sufficient': False
        }
        
        # 값 범위 검증
        if score['has_value'] and 'value_range' in expected:
            value = response.get('value')
            if isinstance(value, (int, float)):
                min_val, max_val = expected['value_range']
                score['value_in_range'] = min_val <= value <= max_val
        elif score['has_value'] and 'value' in expected:
            score['value_in_range'] = response.get('value') == expected['value']
        
        # confidence 검증 (Phase별 차별화)
        if score['has_confidence']:
            if phase <= 2:  # Phase 0-2: 정확히 1.0이어야 함
                conf = response.get('confidence')
                score['confidence_sufficient'] = (conf == 1.0 or conf == 1)
            elif 'confidence_min' in expected:  # Phase 3-4: 최소값 이상
                score['confidence_sufficient'] = response.get('confidence', 0) >= expected['confidence_min']
        
        # Phase별 점수 체계
        total = 0
        
        if phase <= 2:  # Phase 0-2: 결정론적 작업
            # reasoning 불필요, 정확성 중시
            if score['json_valid']: total += 25        # JSON 파싱 성공
            if score['has_value']: total += 25         # value 필드 존재
            if score['has_confidence']: total += 20    # confidence 필드 존재
            if score['value_in_range']: total += 20    # 값이 정확함
            if score['confidence_sufficient']: total += 10  # confidence=1.0
        else:  # Phase 3-4: 추론 작업
            # reasoning 필수, 추론 품질 중시
            if score['json_valid']: total += 20        # JSON 파싱 성공
            if score['has_value']: total += 20         # value 필드 존재
            if score['has_confidence']: total += 15    # confidence 필드 존재
            if score['has_reasoning']: total += 15     # reasoning 필드 존재
            if score['value_in_range']: total += 20    # 값이 합리적 범위
            if score['confidence_sufficient']: total += 10  # confidence가 충분히 높음
        
        score['total_score'] = total
        score['phase'] = phase
        return score
    
    def run_benchmark(self, category_filter: Optional[List[str]] = None):
        """벤치마크 실행"""
        scenarios = self.get_test_scenarios()
        
        print(f"\n🚀 종합 LLM 벤치마크 시작")
        print(f"   시나리오: {len(scenarios)}개")
        
        # 필터링된 모델 카테고리
        test_categories = category_filter or list(self.models.keys())
        total_models = sum(len(self.models[cat]) for cat in test_categories if cat in self.models)
        print(f"   모델: {total_models}개")
        print()
        
        for scenario_idx, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*100}")
            print(f"시나리오 {scenario_idx}/{len(scenarios)}: {scenario['name']}")
            print(f"{'='*100}")
            
            for category in test_categories:
                if category not in self.models:
                    continue
                
                print(f"\n📦 {category}")
                models = self.models[category]
                
                for model in models:
                    try:
                        if 'claude' in category:
                            result = self.test_claude_model(model, scenario)
                        else:
                            result = self.test_openai_model(model, scenario)
                        
                        self.results.append(result)
                        self._print_result(result)
                        
                        # Rate limiting: 모델별 차별화된 대기 시간
                        if model.startswith(('o1', 'o3', 'o4')):  # thinking 모델
                            time.sleep(3)
                        elif 'claude' in category:  # Claude 모델
                            time.sleep(2)
                        else:  # 일반 모델
                            time.sleep(1.5)
                    
                    except Exception as e:
                        print(f"   ❌ {model}: {str(e)[:100]}")
                        self.results.append({
                            'model': model,
                            'scenario_id': scenario['id'],
                            'error': str(e),
                            'success': False
                        })
                        # 오류 발생 시 더 긴 대기
                        time.sleep(3)
        
        # 결과 저장
        output_file = f"benchmark_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_results(output_file)
        self.generate_report()
    
    def _print_result(self, result: Dict):
        """결과 출력"""
        if not result['success']:
            print(f"   ❌ {result['model']}: {result.get('error', '')[:80]}")
            return
        
        quality = result['quality_score']['total_score']
        
        print(f"   ✅ {result['model']}")
        print(f"      비용: ${result['cost']:.6f} | 시간: {result['elapsed_seconds']}초 | 품질: {quality}/100")
        
        if 'value' in result['response']:
            print(f"      답변: {result['response'].get('value')} {result['response'].get('unit', '')}")
    
    def save_results(self, filename: str):
        """결과 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.results),
                    'success_count': sum(1 for r in self.results if r['success'])
                },
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 결과 저장: {filename}")
    
    def generate_report(self):
        """리포트 생성"""
        success = [r for r in self.results if r['success']]
        
        print(f"\n{'='*100}")
        print("📊 종합 리포트")
        print(f"{'='*100}\n")
        print(f"총 테스트: {len(self.results)}개")
        print(f"성공: {len(success)}개 ({len(success)/len(self.results)*100:.1f}%)")
        
        # 모델별 평균
        from collections import defaultdict
        stats = defaultdict(lambda: {'costs': [], 'quality': [], 'times': []})
        
        for r in success:
            model = r['model']
            stats[model]['costs'].append(r['cost'])
            stats[model]['quality'].append(r['quality_score']['total_score'])
            stats[model]['times'].append(r['elapsed_seconds'])
        
        # 가성비 계산
        model_avg = []
        for model, data in stats.items():
            avg_cost = sum(data['costs']) / len(data['costs'])
            avg_quality = sum(data['quality']) / len(data['quality'])
            avg_time = sum(data['times']) / len(data['times'])
            efficiency = avg_quality / (avg_cost * 1000) if avg_cost > 0 else 0
            
            model_avg.append({
                'model': model,
                'avg_cost': avg_cost,
                'avg_quality': avg_quality,
                'avg_time': avg_time,
                'efficiency': efficiency,
                'count': len(data['costs'])
            })
        
        # 가성비 순
        model_avg.sort(key=lambda x: x['efficiency'], reverse=True)
        
        print(f"\n🏆 최고 가성비 TOP 10:")
        for idx, m in enumerate(model_avg[:10], 1):
            print(f"   {idx:2d}. {m['model']:30s} | 가성비: {m['efficiency']:7.1f} | 품질: {m['avg_quality']:5.1f} | 비용: ${m['avg_cost']:.6f}")


def main():
    """메인"""
    print("="*100)
    print("종합 LLM 벤치마크 (2025-11-21)")
    print("="*100)
    
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ API 키가 없습니다.")
        return
    
    print("\n✅ API 키 확인 완료")
    print("\n테스트 옵션:")
    print("1. 전체 모델 (느림, 비쌈, ~20-30분)")
    print("2. 핵심 모델만 (권장, ~10분)")
    print("3. nano/mini만 (빠름, 저렴, ~5분)")
    print("4. thinking 모델만 (중간, ~8분)")
    
    choice = input("\n선택 (1-4): ").strip()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    if choice == '2':
        categories = ['openai_mini', 'openai_standard', 'openai_thinking', 'claude_standard']
    elif choice == '3':
        categories = ['openai_nano', 'openai_mini']
    elif choice == '4':
        categories = ['openai_thinking', 'openai_thinking_pro']
    else:
        categories = None
    
    try:
        benchmark.run_benchmark(category_filter=categories)
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단됨")
        if benchmark.results:
            benchmark.save_results('benchmark_partial.json')
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()

