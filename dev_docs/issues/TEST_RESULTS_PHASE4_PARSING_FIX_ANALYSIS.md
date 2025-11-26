# Phase 4 Parsing Fix 테스트 결과 분석

**버전**: v7.8.1  
**날짜**: 2025-11-25  
**담당**: Estimator Phase 3 & Phase 4 검증

---

## 📋 요약

Phase 4 LLM 응답 파싱 버그에 대한 **Structural Fix**를 적용한 후, `test_phase4_parsing_fix.py`를 실행하여 검증했습니다. 그러나 테스트 과정에서 여러 가지 새로운 문제들이 발견되었습니다.

### 발견된 주요 문제

1. **Phase 3 "Judgment failed (no evidence)" 반복 발생** ⚠️
   - 많은 변수에 대해 Phase 3가 증거를 찾지 못하고 실패
   - 모든 변수 추정이 Phase 4로 넘어가는 상황

2. **Phase 4 LLM 응답 파싱 에러: `unhashable type: 'dict'`** ❌
   - `_parse_llm_models` 메서드에서 `yaml.safe_load` fallback 실행 중 발생
   - 재귀 추정 과정에서 발생 (변수 `p_C` 추정 중)

3. **수식 실행 경고: "허용되지 않는 문자"** ⚠️
   - Phase 4에서 생성된 수식에 허용되지 않은 문자가 포함됨
   - 예: `N_arrivals / T_obs`

4. **순환 의존성 경고** ⚠️
   - 재귀 호출 중 순환 감지: `'General에서 C는 얼마인가?'`, `'General에서 D는 얼마인가?'`
   - 추정 프로세스가 중단됨

---

## 🔍 상세 분석

### 1. Phase 3 "Judgment failed (no evidence)" 반복

#### 관찰 내용

로그에서 다음과 같은 패턴이 **반복적으로** 발생:

```log
INFO     | umis_rag.agents.estimator.source_collector:collect_all:128 -   Physical: 0개 제약
INFO     | umis_rag.agents.estimator.sources.value:collect:124 -   [AI+Web] External API 모드 (TODO: API 호출)
INFO     | umis_rag.agents.estimator.source_collector:collect_all:138 -   Value: 0개 추정
INFO     | umis_rag.agents.estimator.source_collector:collect_all:144 -   Soft: 0개 가이드
WARNING  | umis_rag.agents.estimator.judgment:synthesize:74 - [Judgment] 증거 없음
WARNING  | umis_rag.agents.estimator.phase3_guestimation:estimate:145 -   판단 실패 (증거 없음)
```

#### 근본 원인

**`AIAugmentedEstimationSource` (value.py)의 External API 미구현**

```python:110:126:umis_rag/agents/estimator/sources/value.py
            logger.info(f"  [AI+Web] Cursor AI: instruction 생성 (Phase 3 스킵)")
            
            instruction = self._build_native_instruction(question, context)
            
            # v7.8.1: Cursor AI에서는 빈 리스트 반환
            # 이유: value=0.0은 False로 평가되어 판단 실패 발생
            # instruction은 Phase 4에서만 사용
            logger.info(f"  [AI+Web] Cursor AI: Phase 3에서 사용 불가 → 빈 값 반환")
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # External API: API 호출 (TODO)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        else:  # External API
            logger.info(f"  [AI+Web] External API 모드 (TODO: API 호출)")
            # TODO: LangChain + Tavily/SerpAPI
            return []
```

- **현재 상태**: External API 모드 (`gpt-4o-mini`)에서는 항상 빈 리스트 `[]` 반환
- **결과**: Phase 3에서 어떠한 값 추정도 수집되지 않음 (`Value: 0개 추정`)
- **후속 영향**:
  - `JudgmentSynthesizer`에서 증거가 없어 `'value': None` 반환
  - `phase3_guestimation.py`에서 `if judgment['value'] is None:` 조건 충족 → 판단 실패
  - 모든 변수가 Phase 4로 넘어가게 됨

#### 영향

- **Phase 3 무력화**: Phase 3가 설계 목적대로 작동하지 않음 (LLM 지식 + 웹 검색 조합)
- **Phase 4 과부하**: 모든 변수를 Phase 4가 Fermi 분해해야 함 → 성능 저하
- **테스트 목적 왜곡**: Phase 4 파싱 버그를 테스트하려 했으나, Phase 3 문제로 인해 테스트가 제대로 진행되지 않음

---

### 2. Phase 4 LLM 응답 파싱 에러 (`unhashable type: 'dict'`)

#### 관찰 내용

```log
ERROR | umis_rag.agents.estimator.phase4_fermi:_parse_llm_models:1332 - ❌ LLM 응답 파싱 실패: unhashable type: 'dict'
```

- **발생 시점**: 재귀 추정 중 (`General에서 p_C는 얼마인가?`)
- **발생 위치**: `phase4_fermi.py:_parse_llm_models:1332` (Line 1332)

#### 코드 확인

```python:1240:1334:umis_rag/agents/estimator/phase4_fermi.py
    def _parse_llm_models(
        self,
        llm_output: str,
        depth: int
    ) -> List[FermiModel]:
        """
        LLM 응답 파싱 (YAML/JSON 지원)
        
        v7.8.1: JSON 추출 로직 강화 (벤치마크 패턴 적용)
        
        Args:
            llm_output: LLM 응답
            depth: 깊이
        
        Returns:
            FermiModel 리스트
        """
        try:
            # 1. YAML 블록 추출 시도 (```yaml ... ```)
            yaml_match = re.search(r'```yaml\n(.*?)\n```', llm_output, re.DOTALL)
            
            if yaml_match:
                yaml_str = yaml_match.group(1)
                logger.info(f"{'  ' * depth}        [Parser] YAML 블록 감지")
                
                # YAML 파싱
                data = yaml.safe_load(yaml_str)
            else:
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
            
            # 데이터 검증
            if not data or 'models' not in data:
                logger.warning(f"{'  ' * depth}        ⚠️  파싱 실패 (models 키 없음)")
                logger.debug(f"{'  ' * depth}        응답 미리보기: {llm_output[:200]}...")
                return []
            
            # FermiModel 변환
            models = []
            for model_data in data['models']:
                # 변수 파싱
                variables = {}
                for var_data in model_data.get('variables', []):
                    var_name = var_data.get('name', 'unknown')
                    var_available = var_data.get('available', False)
                    
                    variables[var_name] = FermiVariable(
                        name=var_name,
                        available=var_available,
                        need_estimate=not var_available,
                        source="llm_generated" if var_available else ""
                    )
                
                # FermiModel 생성
                model = FermiModel(
                    model_id=model_data.get('id', f"LLM_MODEL_{len(models)+1}"),
                    name="LLM 생성 모형",
                    formula=model_data.get('formula', ''),
                    description=model_data.get('description', ''),
                    variables=variables,
                    total_variables=len(variables),
                    unknown_count=sum(1 for v in variables.values() if not v.available)
                )
                
                models.append(model)
            
            logger.info(f"{'  ' * depth}        [Parser] 파싱 완료: {len(models)}개 모형")
            return models
        
        except Exception as e:
            logger.error(f"{'  ' * depth}        ❌ LLM 응답 파싱 실패: {e}")
            logger.debug(f"{'  ' * depth}        응답 미리보기: {llm_output[:300]}...")
            return []
```

#### 근본 원인 추정

**Line 1291: `data = yaml.safe_load(llm_output)`에서 `unhashable type: 'dict'` 발생**

`yaml.safe_load()`가 Python 딕셔너리를 반환하는 것이 일반적이지만, `unhashable type: 'dict'` 에러는 **dict가 dict의 key로 사용될 때** 발생합니다.

**가능한 원인**:

1. **LLM 응답 형식 문제**: LLM이 YAML이 아닌 다른 형식(예: Markdown + Code)을 반환했을 가능성
   - `llm_output`이 여러 코드 블록을 포함하거나, 중첩된 구조일 수 있음
   
2. **파싱 로직 문제**: 
   - JSON 파싱 실패 후, `llm_output` 전체를 `yaml.safe_load`에 전달
   - `llm_output`에 Markdown, 주석, 또는 비정형 텍스트가 포함되어 있을 경우, YAML 파싱 실패 가능
   
3. **변수 변환 로직 문제**:
   - Line 1304~1313: `var_data`를 처리하는 과정에서 `dict`를 hashable key로 사용하려 했을 가능성
   - 예: `variables[var_name] = FermiVariable(...)` 에서 `var_name`이 dict일 경우

#### 필요한 조치

1. **디버깅 정보 추가**:
   - 에러 발생 시 `llm_output` 전체를 로깅
   - `data` 변수의 타입과 내용 확인
   
2. **파싱 로직 강화**:
   - `yaml.safe_load` fallback 전에 `llm_output`의 유효성 검증
   - 예외 처리 개선 (특정 에러 타입별 로깅)
   
3. **LLM 프롬프트 개선**:
   - LLM에게 더 명확한 응답 형식 지시 (YAML 또는 JSON만 반환하도록)

---

### 3. 수식 실행 경고: "허용되지 않는 문자"

#### 관찰 내용

```log
WARNING | umis_rag.agents.estimator.phase4_fermi:_execute_formula_simple:1959 - ⚠️ 수식에 허용되지 않는 문자: N_arrivals / T_obs
```

- **발생 메서드**: `_execute_formula_simple` (Line 1959)
- **문제 수식**: `N_arrivals / T_obs`

#### 근본 원인

**Phase 4에서 LLM이 생성한 수식의 변수명 검증 실패**

- **변수명**: `N_arrivals`, `T_obs`
- **예상 원인**: `_execute_formula_simple` 메서드가 허용하는 변수명 패턴에 **언더스코어 `_`가 포함된 변수명**이 포함되지 않았을 가능성

#### 영향

- Phase 4에서 생성된 모형이 실행되지 못함
- 수식 실행 실패 → 추정 실패

#### 필요한 조치

1. **`_execute_formula_simple` 메서드 확인**:
   - 허용되는 변수명 패턴 확인 (정규표현식)
   - 언더스코어 `_`를 포함한 변수명 허용 여부 확인
   
2. **변수명 정규화**:
   - LLM이 생성한 변수명을 검증 및 정규화하는 로직 추가
   - 허용되지 않는 문자 자동 치환 또는 제거

3. **LLM 프롬프트 개선**:
   - 변수명 규칙을 명확히 제시 (예: `[a-zA-Z_][a-zA-Z0-9_]*`)

---

### 4. 순환 의존성 경고

#### 관찰 내용

```log
WARNING | umis_rag.agents.estimator.phase4_fermi:_detect_circular:1868 - 순환 감지: 'General에서 C는 얼마인가?'
WARNING | umis_rag.agents.estimator.phase4_fermi:estimate:565 - ⚠️ 순환 의존성 감지 (A→B→A) → 중단
```

- **발생 메서드**: `_detect_circular` (Line 1868), `estimate` (Line 565)
- **순환 경로**: 예를 들어, `C` 추정 → `D` 필요 → `C` 필요 (순환)

#### 근본 원인

**재귀 추정 중 순환 참조 발생**

1. **LLM 모형 생성 문제**:
   - LLM이 `C`를 추정하기 위한 모형에서 `D`가 필요하다고 판단
   - `D`를 추정하기 위한 모형에서 다시 `C`가 필요하다고 판단
   - 순환 참조 발생

2. **Backtracking 실패**:
   - Phase 4는 순환을 감지하면 중단하지만, 다른 모형을 시도하는 backtracking이 제대로 작동하지 않을 수 있음

#### 영향

- 순환 감지 시 해당 변수 추정이 **중단**됨
- 해당 모형이 실행되지 못하고, 다음 모형으로 넘어가야 하지만, 결국 모든 모형이 실패할 가능성

#### 필요한 조치

1. **순환 감지 로직 확인**:
   - `_detect_circular` 메서드가 정확히 작동하는지 확인
   - 순환 감지 후 처리 로직 (backtracking) 검증

2. **LLM 프롬프트 개선**:
   - LLM에게 순환 참조를 피하도록 명시적으로 지시
   - 예: "Do not create circular dependencies. Ensure each variable depends only on more fundamental variables."

3. **모형 평가 강화**:
   - 모형 생성 단계에서 순환 가능성을 사전 평가
   - 순환 가능성이 높은 모형의 점수를 낮춤

---

## 🎯 종합 진단

### 현재 상황

1. **Phase 3 완전 무력화**: External API 미구현으로 Phase 3가 작동하지 않음
2. **Phase 4 과부하**: 모든 변수가 Phase 4로 넘어가면서 복잡도 증가
3. **파싱 에러 발생**: `unhashable type: 'dict'` 에러로 일부 재귀 추정 실패
4. **수식 실행 실패**: 변수명 검증 문제로 수식 실행 불가
5. **순환 의존성**: 재귀 추정 중 순환 참조 발생, 추정 중단

### 테스트 목적 달성 여부

| 목적 | 상태 | 비고 |
|------|------|------|
| Phase 4 파싱 버그 수정 검증 | ⚠️ 부분 달성 | Structural Fix는 적용되었으나, Phase 3 문제로 충분한 테스트 불가 |
| 다양한 LLM 응답 형식 처리 | ❌ 실패 | `unhashable type: 'dict'` 에러 발생 |
| Phase 3 → Phase 4 워크플로우 검증 | ❌ 실패 | Phase 3가 작동하지 않음 |

---

## 📌 우선순위별 해결 과제

### 우선순위 1 (Blocker): Phase 3 External API 구현

**문제**: `AIAugmentedEstimationSource`에서 External API 호출이 구현되지 않음

**해결**:

1. **Phase 3 Native 모드 로직 재사용**:
   - `_build_native_instruction` 메서드의 출력을 External API 프롬프트로 사용
   
2. **External LLM 호출 구현**:
   ```python
   else:  # External API
       logger.info(f"  [AI+Web] External API 모드 (LLM 호출)")
       
       # Instruction 생성
       instruction = self._build_native_instruction(question, context)
       
       # LLM API 호출
       from umis_rag.core.model_configs import get_model_config
       model_config = get_model_config(self.llm_mode)
       api_params = model_config.build_api_params(instruction)
       
       # API 호출 (api_type에 따라 분기)
       if model_config.api_type == 'responses':
           response = self.llm_client.responses.create(**api_params)
           llm_output = response.output_text
       elif model_config.api_type == 'chat':
           response = self.llm_client.chat.completions.create(**api_params)
           llm_output = response.choices[0].message.content
       
       # JSON 파싱
       # TODO: JSON 형식으로 응답을 파싱하여 ValueEstimate 리스트 생성
       
       return value_estimates
   ```

3. **웹 검색 통합 (선택적)**:
   - Tavily 또는 SerpAPI를 활용하여 웹 검색 결과를 추가

**예상 소요 시간**: 2-3시간

---

### 우선순위 2 (Critical): Phase 4 파싱 에러 디버깅

**문제**: `unhashable type: 'dict'` 에러

**해결**:

1. **로깅 강화**:
   ```python
   except Exception as e:
       logger.error(f"{'  ' * depth}        ❌ LLM 응답 파싱 실패: {e}")
       logger.error(f"{'  ' * depth}        응답 전체:\n{llm_output}")
       logger.error(f"{'  ' * depth}        data 타입: {type(data)}")
       if isinstance(data, dict):
           logger.error(f"{'  ' * depth}        data 키: {data.keys()}")
       return []
   ```

2. **원인 파악 후 수정**:
   - `llm_output` 내용 확인
   - `yaml.safe_load` 결과 검증
   - 변수 변환 로직 검증

**예상 소요 시간**: 1-2시간

---

### 우선순위 3 (Important): 수식 실행 문제 해결

**문제**: "허용되지 않는 문자" 경고

**해결**:

1. **`_execute_formula_simple` 메서드 확인**:
   - 허용되는 변수명 패턴 확인
   
2. **변수명 검증 로직 개선**:
   - 언더스코어 허용
   - 정규표현식 업데이트: `[a-zA-Z_][a-zA-Z0-9_]*`

**예상 소요 시간**: 30분 - 1시간

---

### 우선순위 4 (Medium): 순환 의존성 처리 개선

**문제**: 재귀 추정 중 순환 참조 발생

**해결**:

1. **LLM 프롬프트 개선**:
   - 순환 참조 방지 명시
   
2. **Backtracking 로직 강화**:
   - 순환 감지 시 다른 모형으로 자동 전환

**예상 소요 시간**: 1-2시간

---

## 📝 결론

### 현재 상태

- **Structural Fix 적용**: ✅ 완료
- **테스트 실행**: ✅ 완료
- **주요 블로커 발견**: ✅ Phase 3 External API 미구현

### 다음 단계

1. **Phase 3 External API 구현** (최우선)
2. **Phase 4 파싱 에러 디버깅**
3. **수식 실행 문제 해결**
4. **순환 의존성 처리 개선**

### 추가 제안

- **통합 테스트 개선**:
  - Phase 3와 Phase 4를 개별적으로 테스트할 수 있는 단위 테스트 작성
  - Mock 데이터를 활용하여 각 컴포넌트를 독립적으로 검증
  
- **로깅 개선**:
  - 에러 발생 시 더 상세한 컨텍스트 정보 제공
  - LLM 응답 원문을 로그 파일에 저장

---

**문서 종료**





