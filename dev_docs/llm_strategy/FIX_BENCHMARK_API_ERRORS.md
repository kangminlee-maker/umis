# LLM 벤치마크 API 에러 수정 리포트 (v2.0)

**날짜**: 2025-11-21  
**버전**: 2.0 (reasoning_effort 매개변수 추가)  
**이슈**: 
1. OpenAI GPT-5 temperature 에러
2. Claude-4 응답 파싱 실패
3. reasoning_effort 매개변수 미적용

---

## 업데이트 (v2.0)

### 추가된 내용
- ✅ **reasoning_effort 매개변수 적용**
  - o 시리즈: low/medium/high
  - gpt-5 시리즈: minimal/low/medium/high
- ✅ **reasoning_tokens 캡처**
- ✅ **모델별 최적 설정**

자세한 내용은 [REASONING_EFFORT_IMPLEMENTATION.md](./REASONING_EFFORT_IMPLEMENTATION.md) 참조

---

## 1. 문제 진단

### 1.1 GPT-5 Temperature 에러
```
❌ gpt-5-mini: Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not...
```

**원인**: GPT-5 계열 모델(gpt-5, gpt-5-mini, gpt-5-nano, gpt-5.1 등)은 `temperature` 파라미터를 지원하지 않음

**영향 모델**:
- gpt-5-nano
- gpt-5-mini
- gpt-5
- gpt-5.1
- gpt-5-codex
- gpt-5.1-codex
- gpt-5-pro

### 1.2 Claude-4 응답 파싱 실패
```
claude-sonnet-3.7: 품질: 0/100
claude-sonnet-4: 품질: 0/100
claude-opus-4: 품질: 0/100
```

**원인**: 
1. Claude가 JSON을 코드 블록(```json ... ```)으로 감싸서 반환
2. 기존 파싱 로직이 일반 JSON만 처리
3. 결과적으로 parse_error 발생 → 품질 평가 0점

---

## 2. 해결 방법

### 2.1 GPT-5 Temperature 처리

**Before**:
```python
is_thinking = model.startswith('o1') or model.startswith('o3') or model.startswith('o4')

response = self.openai_client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.2 if not is_thinking else None,
    response_format={"type": "json_object"} if not is_thinking else None
)
```

**After**:
```python
# temperature 미지원 모델: o1/o3/o4 시리즈, gpt-5 시리즈
no_temperature = (model.startswith('o1') or model.startswith('o3') or 
                model.startswith('o4') or model.startswith('gpt-5'))

messages = [{"role": "user", "content": scenario['prompt']}]
if not no_temperature:
    messages.insert(0, {"role": "system", "content": "시장 분석 전문가. JSON만 반환."})

# API 호출 파라미터 구성
api_params = {
    "model": model,
    "messages": messages
}

# temperature 지원 모델만 추가
if not no_temperature:
    api_params["temperature"] = 0.2
    api_params["response_format"] = {"type": "json_object"}

response = self.openai_client.chat.completions.create(**api_params)
```

**핵심 변경점**:
1. `gpt-5` 시리즈를 `no_temperature` 체크에 추가
2. `temperature=None` 대신 파라미터 자체를 제거 (API에 전달하지 않음)
3. 조건부 파라미터 구성으로 깔끔한 코드

### 2.2 Claude JSON 파싱 강화

**Before**:
```python
content = response.content[0].text

try:
    parsed = json.loads(content)
except:
    parsed = {'raw': content, 'parse_error': True}
```

**After**:
```python
content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])

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
except:
    parsed = {'raw': content, 'parse_error': True}
```

**핵심 변경점**:
1. 마크다운 코드 블록(```json ... ```) 감지 및 추출
2. 일반 코드 블록(``` ... ```) 지원
3. 추출 후 trim() 적용하여 공백 제거
4. 순수 JSON도 기존처럼 정상 처리

---

## 3. 수정된 스크립트

✅ **benchmark_comprehensive_2025.py**
- GPT-5 temperature 처리 수정
- Claude JSON 파싱 강화

✅ **benchmark_llm_models_2025.py**
- GPT-5 temperature 처리 수정
- OpenAI JSON 파싱 강화
- Claude JSON 파싱 강화

✅ **benchmark_final_2025.py**
- GPT-5 temperature 처리 수정
- OpenAI JSON 파싱 강화
- Claude JSON 파싱 강화

✅ **benchmark_openai_models.py**
- GPT-5 temperature 처리 수정
- JSON 파싱 강화

✅ **interactive_model_benchmark.py**
- JSON 파싱 강화 (이미 GPT-5 처리는 되어 있었음)

---

## 4. 검증 방법

### 4.1 GPT-5 모델 테스트
```bash
# 단일 모델 테스트
python3 scripts/interactive_model_benchmark.py
# → 옵션 1 선택 (nano 모델)
# → gpt-5-nano 테스트

# 전체 벤치마크
python3 scripts/benchmark_comprehensive_2025.py
# → 옵션 1 선택 (전체 모델)
```

**기대 결과**:
- ❌ `Error code: 400 - temperature` 에러 없음
- ✅ 정상 응답 수신
- ✅ 비용, 품질 점수 산출

### 4.2 Claude-4 모델 테스트
```bash
python3 scripts/benchmark_comprehensive_2025.py
# → 옵션 2 선택 (핵심 모델)
```

**기대 결과**:
- ✅ claude-sonnet-4: 품질 > 0점
- ✅ claude-opus-4: 품질 > 0점
- ✅ JSON 파싱 성공
- ✅ 응답 내용 정상 추출

---

## 5. 성능 예상

### Before (에러 발생)
```
총 테스트: 105개
성공: 91개 (86.7%)  ← GPT-5 모델 14개 실패

claude-sonnet-3.7: 품질 0/100  ← 파싱 실패
claude-sonnet-4: 품질 0/100    ← 파싱 실패
claude-opus-4: 품질 0/100      ← 파싱 실패
```

### After (수정 후)
```
총 테스트: 105개
성공: 105개 (100%)  ← 모든 모델 성공

claude-sonnet-3.7: 품질 75-100/100  ← 정상
claude-sonnet-4: 품질 75-100/100    ← 정상
claude-opus-4: 품질 75-100/100      ← 정상
```

---

## 6. 추가 고려사항

### 6.1 향후 모델 추가 시
새로운 temperature 미지원 모델이 나올 경우:

```python
# 리스트로 관리하는 방식도 고려
NO_TEMP_MODELS = ['gpt-5', 'o1', 'o3', 'o4']

no_temperature = any(model.startswith(prefix) for prefix in NO_TEMP_MODELS)
```

### 6.2 Claude API 이름 매핑 확인
Claude-4 API 이름이 올바른지 주기적 검증:

```python
self.claude_api_names = {
    'claude-haiku-3.5': 'claude-3-5-haiku-20241022',
    'claude-sonnet-3.7': 'claude-3-7-sonnet-20250219',
    'claude-sonnet-4': 'claude-sonnet-4-20250514',    # ← 확인 필요
    'claude-opus-4': 'claude-opus-4-20250514'          # ← 확인 필요
}
```

Anthropic 공식 문서: https://docs.anthropic.com/en/docs/about-claude/models

### 6.3 JSON 파싱 추가 개선
더 견고한 파싱:

```python
# 정규표현식 사용
import re
json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
if json_match:
    content = json_match.group(1).strip()
```

---

## 7. 요약

✅ **GPT-5 에러**: `temperature` 파라미터 제거로 해결  
✅ **Claude-4 0점**: JSON 코드 블록 파싱 추가로 해결  
✅ **5개 스크립트**: 모두 수정 완료  
✅ **Linting**: 에러 없음  

**다음 단계**: 실제 벤치마크 실행하여 수정 검증

---

## 8. 참고 자료

- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [Anthropic Claude 4 Migration Guide](https://docs.anthropic.com/ko/docs/about-claude/models/migrating-to-claude-4)
- [UMIS LLM 벤치마크 전략](./COMPLETE_LLM_MODEL_COMPARISON.md)

