# 벤치마킹 스크립트 → Phase 0-4 적용 가능 패턴 분석

**날짜**: 2025-11-25  
**버전**: v7.8.1  
**대상 스크립트**: `scripts/benchmark_llm_models_2025.py`

---

## 📋 요약

벤치마킹 과정에서 도입한 **검증된 패턴**들을 실제 Phase 0-4 추정 과정에 적용하여, **안정성**, **정확성**, **효율성**을 높일 수 있습니다.

---

## 🎯 적용 가능한 핵심 패턴

### 1. **JSON 파싱 강화 (Robust Parsing)** ⭐ 우선순위 1

**벤치마크에서 발견한 패턴**:

```python:422:436:scripts/benchmark_llm_models_2025.py
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
```

**Phase 4에 이미 적용됨**:

```python:1268:1291:umis_rag/agents/estimator/phase4_fermi.py
            # 2. JSON 블록 추출 시도 (```json ... ```)
            content = llm_output
            
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
                logger.info(f"{'  ' * depth}        [Parser] JSON 블록 감지 (```json)")
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
                logger.info(f"{'  ' * depth}        [Parser] JSON 블록 감지 (```)")
            else:
                logger.info(f"{'  ' * depth}        [Parser] 코드 블록 없음, 전체 파싱 시도")
            
            # 3. JSON 파싱 시도
            try:
                data = json.loads(content)
                logger.info(f"{'  ' * depth}        [Parser] JSON 파싱 성공")
            except json.JSONDecodeError:
                # 4. YAML로 전체 파싱 시도 (Fallback)
                logger.info(f"{'  ' * depth}        [Parser] JSON 실패, YAML 시도")
                data = yaml.safe_load(llm_output)
```

**상태**: ✅ **이미 적용됨** (v7.8.1 Structural Fix에서 구현)

**개선 제안**:
- Phase 3의 `AIAugmentedEstimationSource`에서 External API 구현 시 동일한 패턴 적용
- 에러 핸들링 강화: `parse_error` 플래그를 Phase 4에서도 활용

---

### 2. **Retry 메커니즘 with Backoff** ⭐ 우선순위 2

**벤치마크 패턴**:

```python:367:376:scripts/benchmark_llm_models_2025.py
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
```

**적용 방법**:

Phase 4의 `_generate_llm_models`에 Retry 로직 추가:

```python
# umis_rag/agents/estimator/phase4_fermi.py

import backoff

class Phase4FermiDecomposition:
    
    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=30,
        giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower()
    )
    def _call_llm_with_retry(self, api_params: Dict) -> Any:
        """LLM API 호출 with retry"""
        model_config = self.model_config  # self에서 가져오기
        
        if model_config.api_type == 'responses':
            return self.llm_client.responses.create(**api_params)
        elif model_config.api_type == 'chat':
            return self.llm_client.chat.completions.create(**api_params)
        else:
            raise ValueError(f"Unsupported api_type: {model_config.api_type}")
    
    def _generate_llm_models(self, question, context, depth):
        # ... 기존 코드 ...
        
        # Retry 적용
        try:
            response = self._call_llm_with_retry(api_params)
        except Exception as e:
            logger.error(f"{'  ' * depth}      ❌ LLM 호출 실패 (재시도 소진): {e}")
            return []
```

**장점**:
- Rate Limit 에러 자동 재시도
- Timeout 에러 복원력 향상
- 지수 백오프로 API 부하 완화

**상태**: ⏳ **미적용**

**우선순위**: **Phase 3 External API 구현과 함께 적용 권장**

---

### 3. **API 타입별 분기 로직** ✅ 이미 적용됨

**벤치마크 패턴**:

```python:383:413:scripts/benchmark_llm_models_2025.py
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
```

**Phase 4에 이미 적용됨**:

`model_configs.yaml`에서 모델별 설정 관리:

```yaml:28:50:config/model_configs.yaml
  o1-mini:
    api_type: responses
    max_output_tokens: 16000
    reasoning_effort:
      support: true
      default: medium
    cost_per_1m_input: 1.10
    cost_per_1m_output: 4.40
  
  gpt-4o-mini:
    api_type: chat
    max_output_tokens: 16384
    temperature: 0.7
    cost_per_1m_input: 0.15
    cost_per_1m_output: 0.60
```

`ModelConfig.build_api_params()`에서 자동으로 적절한 파라미터 구성.

**상태**: ✅ **이미 적용됨** (Model Config System v7.8.0)

---

### 4. **품질 평가 시스템 (Quality Scoring)** ⭐ 우선순위 3

**벤치마크 패턴**:

```python:609:648:scripts/benchmark_llm_models_2025.py
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
```

**Phase 4 적용 방안**:

```python
# umis_rag/agents/estimator/phase4_fermi.py

class Phase4FermiDecomposition:
    
    def _evaluate_model_quality(self, model: FermiModel, llm_output: str) -> Dict[str, Any]:
        """
        생성된 모형의 품질 평가
        
        Returns:
            {
                'has_formula': bool,
                'has_variables': bool,
                'variable_count_reasonable': bool,  # 2-6개
                'formula_parsable': bool,
                'total_score': int (0-100)
            }
        """
        score = {
            'has_formula': bool(model.formula),
            'has_variables': len(model.variables) > 0,
            'variable_count_reasonable': 2 <= len(model.variables) <= 6,
            'formula_parsable': False,
            'all_variables_defined': False
        }
        
        # 수식 파싱 가능 여부
        try:
            # 간단한 검증: 변수명이 수식에 포함되는지
            formula = model.formula.lower()
            for var in model.variables.values():
                if var.name.lower() not in formula:
                    score['formula_parsable'] = False
                    break
            else:
                score['formula_parsable'] = True
        except:
            score['formula_parsable'] = False
        
        # 모든 변수가 정의되었는지
        score['all_variables_defined'] = all(
            var.available or var.need_estimate for var in model.variables.values()
        )
        
        # 총점 계산
        total_score = 0
        if score['has_formula']: total_score += 25
        if score['has_variables']: total_score += 25
        if score['variable_count_reasonable']: total_score += 20
        if score['formula_parsable']: total_score += 20
        if score['all_variables_defined']: total_score += 10
        
        score['total_score'] = total_score
        
        return score
    
    def _step2_generate_models(self, question, context, depth):
        # ... 기존 로직 ...
        
        models = self._generate_default_models(question, context, depth)
        
        # 품질 평가 추가
        for model in models:
            quality = self._evaluate_model_quality(model, "")
            logger.info(f"{'  ' * depth}        [Quality] {model.model_id}: {quality['total_score']}/100")
            
            # 품질 기준 미달 시 경고
            if quality['total_score'] < 60:
                logger.warning(f"{'  ' * depth}        ⚠️  낮은 품질: {model.model_id} ({quality['total_score']}/100)")
        
        return models
```

**장점**:
- 생성된 모형의 품질을 정량적으로 평가
- 품질 기준 미달 모형 조기 필터링
- 디버깅 및 개선 용이

**상태**: ⏳ **미적용**

---

### 5. **비용 추적 시스템 (Cost Tracking)** ⏳ 우선순위 4

**벤치마크 패턴**:

```python:599:607:scripts/benchmark_llm_models_2025.py
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        if model not in self.pricing:
            return 0.0
        
        rates = self.pricing[model]
        cost = (input_tokens / 1_000_000 * rates['input'] +
                output_tokens / 1_000_000 * rates['output'])
        return round(cost, 6)
```

**Phase 4 적용 방안**:

```python
# umis_rag/agents/estimator/phase4_fermi.py

class Phase4FermiDecomposition:
    
    def __init__(self, ...):
        # ... 기존 초기화 ...
        
        # 비용 추적
        self.cost_tracker = {
            'total_cost': 0.0,
            'api_calls': 0,
            'total_tokens': {'input': 0, 'output': 0}
        }
    
    def _track_cost(self, model_name: str, usage: Any):
        """비용 추적"""
        from umis_rag.core.model_configs import get_model_config
        
        model_config = get_model_config(model_name)
        
        input_tokens = usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else usage.input_tokens
        output_tokens = usage.completion_tokens if hasattr(usage, 'completion_tokens') else usage.output_tokens
        
        cost = (
            input_tokens / 1_000_000 * model_config.cost_per_1m_input +
            output_tokens / 1_000_000 * model_config.cost_per_1m_output
        )
        
        self.cost_tracker['total_cost'] += cost
        self.cost_tracker['api_calls'] += 1
        self.cost_tracker['total_tokens']['input'] += input_tokens
        self.cost_tracker['total_tokens']['output'] += output_tokens
        
        logger.info(f"[Cost] API 호출 비용: ${cost:.6f} (누적: ${self.cost_tracker['total_cost']:.6f})")
    
    def _generate_llm_models(self, question, context, depth):
        # ... API 호출 ...
        
        response = self.llm_client.chat.completions.create(**api_params)
        
        # 비용 추적
        self._track_cost(model_config.model_name, response.usage)
        
        # ... 나머지 로직 ...
    
    def get_cost_summary(self) -> Dict:
        """비용 요약 반환"""
        return {
            'total_cost_usd': round(self.cost_tracker['total_cost'], 6),
            'api_calls': self.cost_tracker['api_calls'],
            'total_tokens': self.cost_tracker['total_tokens'],
            'avg_cost_per_call': round(
                self.cost_tracker['total_cost'] / self.cost_tracker['api_calls'], 6
            ) if self.cost_tracker['api_calls'] > 0 else 0.0
        }
```

**장점**:
- 실시간 비용 모니터링
- API 호출 횟수 추적
- 비용 최적화 근거 데이터

**상태**: ⏳ **미적용**

---

### 6. **Rate Limiting 자동 대기** ⏳ 우선순위 5

**벤치마크 패턴**:

```python:121:140:scripts/benchmark_llm_models_2025.py
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
```

**Phase 4 적용 방안**:

```python
# umis_rag/agents/estimator/phase4_fermi.py

import time

class Phase4FermiDecomposition:
    
    def _apply_rate_limiting(self, model_name: str, is_error: bool = False):
        """Rate Limiting 자동 대기"""
        
        if is_error:
            # 에러 발생 시 3초 대기
            time.sleep(3)
            logger.info("[Rate Limit] 에러 후 3초 대기 완료")
            return
        
        # 모델 타입별 대기 시간
        if model_name.startswith('o1') or model_name.startswith('o3'):
            # Reasoning 모델: 3초
            time.sleep(3)
            logger.debug("[Rate Limit] Reasoning 모델 3초 대기 완료")
        elif model_name.startswith('gpt-5'):
            # GPT-5: 2초
            time.sleep(2)
            logger.debug("[Rate Limit] GPT-5 2초 대기 완료")
        else:
            # 일반 모델: 1.5초
            time.sleep(1.5)
            logger.debug("[Rate Limit] 일반 모델 1.5초 대기 완료")
    
    def _estimate_variable(self, var_name, question, parent_depth):
        # ... Phase 3 시도 ...
        
        try:
            phase3_result = self.phase3.estimate(question, context)
        except Exception as e:
            logger.error(f"Phase 3 실패: {e}")
            self._apply_rate_limiting(self.llm_mode, is_error=True)
        
        # ... Phase 4 재귀 ...
        
        if parent_depth + 1 < self.max_depth:
            try:
                recursive_result = self.estimate(question, depth=parent_depth + 1)
                
                # 성공 시 일반 대기
                self._apply_rate_limiting(self.llm_mode, is_error=False)
                
            except Exception as e:
                logger.error(f"재귀 실패: {e}")
                self._apply_rate_limiting(self.llm_mode, is_error=True)
```

**장점**:
- Rate Limit 에러 사전 방지
- API 공급자 정책 준수
- 안정적인 대용량 추정

**상태**: ⏳ **미적용**

---

## 📊 우선순위 정리

| 순위 | 패턴 | 상태 | 적용 대상 | 난이도 | 효과 |
|------|------|------|-----------|--------|------|
| 1 | JSON 파싱 강화 | ✅ 완료 | Phase 4 | 낮음 | 높음 |
| 2 | Retry 메커니즘 | ⏳ 미적용 | Phase 3, 4 | 중간 | 높음 |
| 3 | 품질 평가 시스템 | ⏳ 미적용 | Phase 4 | 중간 | 중간 |
| 4 | 비용 추적 | ⏳ 미적용 | Phase 3, 4 | 낮음 | 중간 |
| 5 | Rate Limiting | ⏳ 미적용 | Phase 3, 4 | 낮음 | 중간 |
| - | API 타입 분기 | ✅ 완료 | 전체 | - | - |

---

## 🚀 적용 로드맵

### Phase 1 (즉시): Phase 3 External API 구현

**작업**:
1. `AIAugmentedEstimationSource.collect()` External API 구현
2. JSON 파싱 강화 패턴 적용 (벤치마크와 동일)
3. Retry 메커니즘 통합

**예상 시간**: 2-3시간

---

### Phase 2 (단기): Phase 4 안정성 강화

**작업**:
1. Retry 메커니즘 추가
2. 품질 평가 시스템 통합
3. Phase 4 파싱 에러 디버깅 완료

**예상 시간**: 2-3시간

---

### Phase 3 (중기): 모니터링 및 최적화

**작업**:
1. 비용 추적 시스템 구축
2. Rate Limiting 자동화
3. 성능 메트릭 수집

**예상 시간**: 3-4시간

---

## 📝 추가 제안

### 1. **통합 파싱 유틸리티 함수**

벤치마크와 Phase 4에서 중복된 파싱 로직을 통합:

```python
# umis_rag/utils/llm_parsing.py

import json
import yaml
import re
from typing import Any, Optional, Dict

def parse_llm_response(
    content: str,
    prefer_format: str = 'json'  # 'json' or 'yaml'
) -> Optional[Dict[str, Any]]:
    """
    LLM 응답에서 구조화된 데이터 추출
    
    지원 형식:
    - ```json ... ```
    - ```yaml ... ```
    - ``` ... ``` (일반 코드 블록)
    - Raw JSON/YAML
    
    Returns:
        파싱된 Dict 또는 None
    """
    try:
        # 1. JSON 코드 블록 추출
        if '```json' in content:
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            content = content[json_start:json_end].strip()
            return json.loads(content)
        
        # 2. YAML 코드 블록 추출
        elif '```yaml' in content:
            yaml_start = content.find('```yaml') + 7
            yaml_end = content.find('```', yaml_start)
            content = content[yaml_start:yaml_end].strip()
            return yaml.safe_load(content)
        
        # 3. 일반 코드 블록
        elif '```' in content:
            block_start = content.find('```') + 3
            block_end = content.find('```', block_start)
            content = content[block_start:block_end].strip()
            
            # JSON 시도
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            
            # YAML 시도
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                pass
        
        # 4. Raw content 파싱
        if prefer_format == 'json':
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return yaml.safe_load(content)
        else:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                return json.loads(content)
    
    except Exception as e:
        return None
```

**사용**:

```python
# Phase 4
llm_output = response.choices[0].message.content
parsed = parse_llm_response(llm_output, prefer_format='yaml')

# Phase 3
llm_output = response.choices[0].message.content
parsed = parse_llm_response(llm_output, prefer_format='json')

# 벤치마크
content = response.choices[0].message.content
parsed = parse_llm_response(content, prefer_format='json')
```

---

### 2. **테스트 시나리오 재사용**

벤치마크의 Phase 0-4 시나리오를 **단위 테스트**로 활용:

```python
# tests/test_estimator_phases.py

import pytest
from umis_rag.agents.estimator import EstimatorRAG

class TestEstimatorPhases:
    
    @pytest.fixture
    def estimator(self):
        return EstimatorRAG(llm_mode='gpt-4o-mini')
    
    def test_phase0_literal_lookup(self, estimator):
        """Phase 0: Literal Lookup"""
        question = "한국 B2B SaaS 월 ARPU는?"
        
        # 프로젝트 데이터에 포함
        estimator.project_data = {
            'korea_b2b_saas_monthly_arpu': 200000
        }
        
        result = estimator.estimate(question)
        
        assert result['phase'] == 0
        assert result['value'] == 200000
        assert result['confidence'] >= 0.9
    
    def test_phase1_direct_rag(self, estimator):
        """Phase 1: Direct RAG"""
        question = "코웨이 렌탈 ARPU는?"
        
        result = estimator.estimate(question)
        
        assert result['phase'] in [1, 2]  # Phase 1 or 2
        assert 30000 <= result['value'] <= 35000
    
    # ... Phase 2, 3, 4 테스트 ...
```

---

## 🎯 최종 권장 사항

### 즉시 적용 (High Priority)

1. ✅ **JSON 파싱 강화** - 이미 완료
2. ⏳ **Phase 3 External API + Retry** - Phase 3 구현과 함께
3. ⏳ **통합 파싱 유틸리티** - 코드 중복 제거

### 단기 적용 (Medium Priority)

4. ⏳ **품질 평가 시스템** - Phase 4 모형 필터링
5. ⏳ **비용 추적 시스템** - 운영 최적화

### 장기 적용 (Low Priority)

6. ⏳ **Rate Limiting 자동화** - 대용량 추정 시
7. ⏳ **벤치마크 시나리오 → 단위 테스트** - 회귀 방지

---

**문서 종료**


