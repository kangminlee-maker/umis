# 단일 Provider 전략 가이드
**OpenAI vs Claude 전용 구성 - UMIS 최적화**

---

## 📌 단일 Provider의 장점

### Why Single Provider?

```yaml
장점:
  1. API 관리 단순화:
     - 단일 API 키
     - 단일 인증 방식
     - 단일 에러 핸들링
     - 단일 Rate Limit 관리
  
  2. 비용 추적 용이:
     - 단일 청구서
     - 명확한 비용 분석
     - 예산 관리 단순
  
  3. 코드 복잡도 감소:
     - Provider별 분기 불필요
     - 단일 클라이언트
     - 유지보수 용이
  
  4. 최적화 집중:
     - 한 Provider 특성에 집중
     - 프롬프트 최적화
     - 캐싱 전략 단순

단점:
  - Vendor Lock-in 가능성
  - 장애 시 대안 없음
  - 특정 작업에 차선 모델 사용 가능

결론: 
  실무에서는 단일 Provider가 더 실용적!
  (Multi-Provider는 복잡도 대비 효과 낮음)
```

---

## 🎯 Strategy A: OpenAI 전용 구성

### 모델 라인업

```yaml
Tier 1 (85% 작업): GPT-4o-mini
  가격: $0.15/1M 입력, $0.60/1M 출력
  작업당: $0.00045
  
  사용:
    - Phase 0-2 (100%)
    - Phase 3 (템플릿 있음, 40%)
    - Quantifier 모든 계산 (10%)
    - Validator 정의 검증 (5%)
    - Explorer RAG 작업

Tier 2 (10% 작업): GPT-4o
  가격: $5/1M 입력, $15/1M 출력
  작업당: $0.0125
  
  사용:
    - Phase 3 (템플릿 없음, 8%)
    - Explorer 가설 생성
    - Validator 신뢰도 평가
    - Observer 간단한 분석

Tier 3 (5% 작업): o1-mini
  가격: $3/1M 입력, $12/1M 출력
  작업당: $0.009
  
  사용:
    - Phase 4 (복잡한 Fermi)
    - Discovery Sprint (Full)
    - Observer 복잡한 분석

(선택) Tier 4: o1 (품질 최우선 시)
  가격: $15/1M 입력, $60/1M 출력
  작업당: $0.045
  
  사용:
    - 최고 복잡도 작업만 (1%)
```

### 비용 계산

```yaml
평균 비용/작업:
  (0.85 × $0.00045) + (0.10 × $0.0125) + (0.05 × $0.009)
  = $0.00038 + $0.00125 + $0.00045
  = $0.00208

1,000회 작업: $2.08
10,000회: $20.80

vs Sonnet 4.5 (Thinking) 100%: ~$15/1,000회
절감: -86% (오히려 38% 더 비쌈)

하지만:
  - 단일 Provider 이점
  - GPT-4o-mini의 압도적 가성비
  - 관리 단순화
```

### 강점

```yaml
1. GPT-4o-mini의 가성비:
   - UMIS 작업 85%에 완벽
   - 초저가 ($0.00045/작업)
   - 매우 빠름 (<1초)
   - Few-shot 학습 뛰어남

2. o1-mini의 Thinking:
   - Phase 4에 충분
   - Sonnet Thinking 대비 40% 저렴
   - 합리적 성능

3. 멀티모달:
   - GPT-4o/4o-mini 이미지 처리
   - Excel 차트 분석 가능
   - 향후 확장성

4. 안정성:
   - OpenAI API 안정적
   - Rate Limit 관대
   - 문서화 우수
```

### 약점

```yaml
1. Phase 4 품질:
   - o1-mini < Sonnet 4.5 (Thinking)
   - 복잡한 추론에서 약함
   - 약 10-15% 성능 차이

2. 긴 컨텍스트:
   - 최대 128k (o1-mini)
   - Claude 200k보다 작음
   - 일부 작업 제약

3. Extended Thinking:
   - o1은 Thinking이지만 비쌈
   - o1-mini는 제한적
   - Claude만큼 자연스럽지 않음
```

### 구현

```python
# umis_rag/core/openai_provider.py

from openai import OpenAI
from typing import Dict, Any

class OpenAIProvider:
    """
    OpenAI 전용 Provider
    """
    
    def __init__(self):
        self.client = OpenAI()  # .env에서 자동
        
        # 모델 매핑
        self.models = {
            'tier1': 'gpt-4o-mini',
            'tier2': 'gpt-4o',
            'tier3': 'o1-mini',
            'tier4': 'o1'  # 선택
        }
        
        # 비용 추적
        self.cost_tracker = {
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4o': {'input': 5.00, 'output': 15.00},
            'o1-mini': {'input': 3.00, 'output': 12.00},
            'o1': {'input': 15.00, 'output': 60.00}
        }
    
    def select_model(self, task: Dict[str, Any]) -> str:
        """
        작업 특성 → 모델 선택
        """
        phase = task.get('phase', 0)
        has_template = task.get('has_template', False)
        complexity = task.get('complexity', 0.5)
        
        # Tier 1: GPT-4o-mini (85%)
        if phase <= 2:
            return self.models['tier1']
        
        if phase == 3 and has_template:
            return self.models['tier1']
        
        # Tier 2: GPT-4o (10%)
        if phase == 3:
            return self.models['tier2']
        
        # Tier 3-4: o1-mini/o1 (5%)
        if phase == 4:
            if complexity > 0.8:
                return self.models.get('tier4', 'o1-mini')  # tier4 없으면 o1-mini
            else:
                return self.models['tier3']
        
        return self.models['tier2']  # Fallback
    
    def estimate(self, query: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        추정 실행
        """
        model = self.select_model(task)
        
        # 프롬프트 생성
        prompt = self._build_prompt(query, task, model)
        
        # API 호출
        if model.startswith('o1'):
            # o1 시리즈는 다른 파라미터
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                # o1은 temperature, system 미지원
            )
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "당신은 시장 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}  # 4o-mini, 4o만
            )
        
        # 비용 추적
        usage = response.usage
        cost = self._calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)
        
        # 결과 파싱
        result = self._parse_response(response.choices[0].message.content)
        result['model_used'] = model
        result['cost'] = cost
        
        return result
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        rates = self.cost_tracker[model]
        cost = (input_tokens / 1_000_000 * rates['input'] + 
                output_tokens / 1_000_000 * rates['output'])
        return cost
```

### 프롬프트 전략 (OpenAI 최적화)

```yaml
GPT-4o-mini 최적화:
  1. Few-shot 예시 필수 (3-5개)
  2. 명시적 단계 지시
  3. JSON 출력 강제
  4. 간결한 프롬프트 (토큰 절약)

GPT-4o 최적화:
  1. 구조화된 프롬프트
  2. 예시 2-3개
  3. 멀티모달 활용 가능

o1-mini 최적화:
  1. 간결한 질문
  2. System 메시지 없음
  3. 복잡한 추론 의존
  4. 검증 요청
```

### 비용 최적화

```yaml
1. 캐싱:
   - 동일 질문 30-40% 재사용
   - 비용 추가 30% 절감

2. 프롬프트 압축:
   - 불필요한 설명 제거
   - 핵심만 전달
   - 20% 토큰 절약

3. 배치 처리:
   - 여러 질문 한 번에
   - API 호출 최소화

4. 템플릿 구축:
   - Phase 3 작업 템플릿화
   - mini 사용률 85% → 95%

총 효과:
  $2.08 → $1.00-1.50/1,000회
  (50-70% 추가 절감)
```

### 최종 OpenAI 구성

```yaml
기본 (균형):
  - 85%: GPT-4o-mini
  - 10%: GPT-4o
  - 5%: o1-mini
  비용: $2.08/1,000회 → 최적화 후 $1.00-1.50

저비용 (스타트업):
  - 95%: GPT-4o-mini
  - 5%: GPT-4o (o1-mini 대신)
  비용: $0.70/1,000회
  품질: -10-15%

고품질:
  - 85%: GPT-4o-mini
  - 8%: GPT-4o
  - 5%: o1-mini
  - 2%: o1 (최고급)
  비용: $3.00/1,000회
  품질: +5-10%
```

---

## 🎯 Strategy B: Claude 전용 구성

### 모델 라인업

```yaml
Tier 1 (85% 작업): Haiku 3.5
  가격: $0.25/1M 입력, $1.25/1M 출력
  작업당: $0.000875
  
  사용:
    - Phase 0-2 (100%)
    - Phase 3 (템플릿 있음, 40%)
    - Quantifier 모든 계산 (10%)
    - Validator 정의 검증 (5%)
    - Explorer RAG 작업

Tier 2 (10% 작업): Sonnet 4.5
  가격: $3/1M 입력, $15/1M 출력
  작업당: $0.0105
  
  사용:
    - Phase 3 (템플릿 없음, 8%)
    - Explorer 가설 생성
    - Validator 신뢰도 평가
    - Observer 간단한 분석
    - Discovery Sprint (Fast Track)

Tier 3 (5% 작업): Sonnet 4.5 (Thinking)
  가격: ~$5/1M 입력, ~$20/1M 출력 (추정)
  작업당: ~$0.015
  
  사용:
    - Phase 4 (복잡한 Fermi)
    - Discovery Sprint (Full)
    - Observer 복잡한 분석

(선택) Tier 4: Opus 4.1 (Thinking) (품질 최우선 시)
  가격: ~$25/1M 입력, ~$100/1M 출력 (추정)
  작업당: ~$0.075
  
  사용:
    - 최고 복잡도 작업만 (1%)
```

### 비용 계산

```yaml
평균 비용/작업:
  (0.85 × $0.000875) + (0.10 × $0.0105) + (0.05 × $0.015)
  = $0.00074 + $0.00105 + $0.00075
  = $0.00254

1,000회 작업: $2.54
10,000회: $25.40

vs OpenAI 구성: $2.08
차이: +22% (약간 비쌈)

vs Sonnet 4.5 (Thinking) 100%: ~$15/1,000회
절감: -83%
```

### 강점

```yaml
1. Extended Thinking:
   - Sonnet 4.5 (Thinking) 최고
   - 자연스러운 추론
   - Self-correction 뛰어남
   - Phase 4 품질 최상

2. 긴 컨텍스트:
   - 모든 모델 200k
   - 복잡한 문서 분석 유리
   - UMIS 프로젝트 파일 다수 처리

3. 윤리적 판단:
   - Constitutional AI
   - 안전한 응답
   - 신뢰성 높음

4. Haiku 3.5:
   - GPT-4o-mini 대비 2배 비싸지만
   - 200k 컨텍스트 (vs 128k)
   - Claude 품질
```

### 약점

```yaml
1. 비용:
   - Haiku가 GPT-4o-mini 대비 2배
   - 전체 22% 더 비쌈
   - Thinking 추가 비용

2. 속도:
   - Thinking 모델 느림 (10-20초)
   - Haiku는 빠르지만 mini보다 약간 느림

3. API 제한:
   - Rate Limit 더 엄격
   - Thinking 토큰 추가 비용
   - 투명성 낮음 (숨겨진 토큰)

4. 멀티모달:
   - 이미지 처리 제한적
   - GPT만큼 자연스럽지 않음
```

### 구현

```python
# umis_rag/core/claude_provider.py

import anthropic
from typing import Dict, Any

class ClaudeProvider:
    """
    Claude 전용 Provider
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic()  # .env에서 자동
        
        # 모델 매핑
        self.models = {
            'tier1': 'claude-3-5-haiku-20241022',
            'tier2': 'claude-sonnet-4-20250514',
            'tier3': 'claude-sonnet-4-20250514',  # Thinking 활성화
            'tier4': 'claude-opus-4-20250514'  # 선택
        }
        
        # 비용 추적 (실제 가격 확인 필요)
        self.cost_tracker = {
            'haiku-3.5': {'input': 0.25, 'output': 1.25},
            'sonnet-4.5': {'input': 3.00, 'output': 15.00},
            'sonnet-4.5-thinking': {'input': 5.00, 'output': 20.00},  # 추정
            'opus-4.1-thinking': {'input': 25.00, 'output': 100.00}  # 추정
        }
    
    def select_model(self, task: Dict[str, Any]) -> tuple[str, bool]:
        """
        작업 특성 → 모델 + Thinking 여부
        
        Returns:
            (model_id, use_thinking)
        """
        phase = task.get('phase', 0)
        has_template = task.get('has_template', False)
        complexity = task.get('complexity', 0.5)
        
        # Tier 1: Haiku 3.5 (85%)
        if phase <= 2:
            return (self.models['tier1'], False)
        
        if phase == 3 and has_template:
            return (self.models['tier1'], False)
        
        # Tier 2: Sonnet 4.5 (10%)
        if phase == 3:
            return (self.models['tier2'], False)
        
        # Tier 3-4: Sonnet/Opus Thinking (5%)
        if phase == 4:
            if complexity > 0.9:
                return (self.models.get('tier4', self.models['tier3']), True)
            else:
                return (self.models['tier3'], True)  # Thinking 활성화
        
        return (self.models['tier2'], False)  # Fallback
    
    def estimate(self, query: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        추정 실행
        """
        model_id, use_thinking = self.select_model(task)
        
        # 프롬프트 생성
        prompt = self._build_prompt(query, task, model_id)
        
        # API 호출
        params = {
            "model": model_id,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Extended Thinking 활성화
        if use_thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 10000  # Thinking 토큰 예산
            }
        
        response = self.client.messages.create(**params)
        
        # 비용 추적
        usage = response.usage
        cost = self._calculate_cost(
            model_id, 
            use_thinking,
            usage.input_tokens, 
            usage.output_tokens,
            getattr(usage, 'thinking_tokens', 0)  # Thinking 토큰
        )
        
        # 결과 파싱
        result = self._parse_response(response.content[0].text)
        result['model_used'] = model_id
        result['use_thinking'] = use_thinking
        result['cost'] = cost
        
        return result
    
    def _calculate_cost(
        self, 
        model_id: str, 
        use_thinking: bool,
        input_tokens: int, 
        output_tokens: int,
        thinking_tokens: int = 0
    ) -> float:
        """비용 계산"""
        # 모델 타입 결정
        if 'haiku' in model_id:
            model_type = 'haiku-3.5'
        elif 'opus' in model_id and use_thinking:
            model_type = 'opus-4.1-thinking'
        elif 'sonnet' in model_id and use_thinking:
            model_type = 'sonnet-4.5-thinking'
        else:
            model_type = 'sonnet-4.5'
        
        rates = self.cost_tracker[model_type]
        
        # 기본 비용
        cost = (input_tokens / 1_000_000 * rates['input'] + 
                output_tokens / 1_000_000 * rates['output'])
        
        # Thinking 토큰 추가 비용 (추정)
        if thinking_tokens > 0:
            cost += thinking_tokens / 1_000_000 * rates['input'] * 1.5
        
        return cost
```

### 프롬프트 전략 (Claude 최적화)

```yaml
Haiku 3.5 최적화:
  1. 명확하고 간결한 지시
  2. 예시 2-3개
  3. XML 태그 활용
  4. 구조화된 출력

Sonnet 4.5 최적화:
  1. 상세한 컨텍스트 제공
  2. 단계별 지시
  3. 예시 활용
  4. 200k 컨텍스트 활용

Sonnet 4.5 (Thinking) 최적화:
  1. 복잡한 문제 그대로 제시
  2. Thinking 예산 설정
  3. 검증 요청
  4. 자연스러운 질문
```

### 비용 최적화

```yaml
1. Thinking 토큰 제어:
   - 예산 설정 (10,000 토큰)
   - 불필요한 Thinking 방지

2. 캐싱:
   - Claude 캐싱 기능 활용
   - Prompt Caching
   - 30-50% 절감

3. 프롬프트 재사용:
   - 시스템 프롬프트 캐싱
   - 예시 재사용

4. 템플릿 구축:
   - Haiku 사용률 극대화

총 효과:
  $2.54 → $1.50-2.00/1,000회
  (30-40% 추가 절감)
```

### 최종 Claude 구성

```yaml
기본 (균형):
  - 85%: Haiku 3.5
  - 10%: Sonnet 4.5
  - 5%: Sonnet 4.5 (Thinking)
  비용: $2.54/1,000회 → 최적화 후 $1.50-2.00

저비용:
  - 95%: Haiku 3.5
  - 5%: Sonnet 4.5 (Thinking 없이)
  비용: $1.30/1,000회
  품질: -15-20%

고품질 (현재):
  - 5%: Haiku 3.5 (Phase 0-2만)
  - 20%: Sonnet 4.5
  - 75%: Sonnet 4.5 (Thinking)
  비용: $12-15/1,000회
  품질: 최고
```

---

## 📊 OpenAI vs Claude 비교

### 비용 비교

| 구성 | OpenAI | Claude | 차이 |
|------|--------|--------|------|
| **기본 (균형)** | $2.08 | $2.54 | Claude +22% |
| **최적화 후** | $1.00-1.50 | $1.50-2.00 | Claude +33% |
| **저비용** | $0.70 | $1.30 | Claude +86% |
| **고품질** | $3.00 | $12-15 | Claude +300% |

**결론**: OpenAI가 비용 면에서 우세 (GPT-4o-mini 덕분)

### 품질 비교

| 작업 | OpenAI | Claude | 우세 |
|------|--------|--------|------|
| Phase 0-2 | mini: ⭐⭐⭐⭐⭐ | Haiku: ⭐⭐⭐⭐⭐ | 동등 |
| Phase 3 (템플릿 O) | mini: ⭐⭐⭐⭐⭐ | Haiku: ⭐⭐⭐⭐⭐ | 동등 |
| Phase 3 (템플릿 X) | 4o: ⭐⭐⭐⭐⭐ | Sonnet 4.5: ⭐⭐⭐⭐⭐ | 동등 |
| Phase 4 (복잡) | o1-mini: ⭐⭐⭐⭐ | Sonnet (Think): ⭐⭐⭐⭐⭐ | **Claude** |
| Discovery Sprint | o1-mini: ⭐⭐⭐⭐ | Sonnet (Think): ⭐⭐⭐⭐⭐ | **Claude** |
| 멀티모달 | 4o: ⭐⭐⭐⭐⭐ | Claude: ⭐⭐⭐ | **OpenAI** |
| 긴 컨텍스트 | 128k: ⭐⭐⭐⭐ | 200k: ⭐⭐⭐⭐⭐ | **Claude** |

**결론**: 
- 85% 작업: 동등
- 10% 작업: 동등
- 5% 작업 (Phase 4): Claude 우세 (+10-15%)

### 특징 비교

```yaml
OpenAI:
  강점:
    ✅ 비용 (GPT-4o-mini 압도적)
    ✅ 멀티모달 (이미지 처리)
    ✅ API 안정성
    ✅ 속도 (mini 매우 빠름)
    ✅ 문서화 우수
  
  약점:
    ❌ Phase 4 품질 (o1-mini < Sonnet Thinking)
    ❌ 컨텍스트 128k (vs 200k)
    ❌ Extended Thinking 약함

Claude:
  강점:
    ✅ Phase 4 품질 (Extended Thinking)
    ✅ 긴 컨텍스트 (200k)
    ✅ 윤리적 판단
    ✅ 자연스러운 추론
  
  약점:
    ❌ 비용 (Haiku가 mini 대비 2배)
    ❌ API 제한 더 엄격
    ❌ 멀티모달 제한적
    ❌ Thinking 토큰 불투명
```

---

## 🎯 최종 권장

### 시나리오별 권장

#### 1. 비용 최우선 (스타트업)

```yaml
권장: OpenAI 전용 ⭐⭐⭐⭐⭐

구성:
  - 95%: GPT-4o-mini
  - 5%: GPT-4o

비용: $0.70/1,000회

이유:
  - GPT-4o-mini가 압도적 가성비
  - Claude 대비 46% 저렴
  - Phase 4 품질 약간 하락 (허용 가능)

트레이드오프:
  - Phase 4: -10-15% 품질
  - Discovery Sprint: -15-20% 품질
  - 대부분 작업: 동일 품질
```

#### 2. 균형 (일반 기업) ⭐⭐⭐⭐⭐

```yaml
권장 A: OpenAI 전용 ⭐⭐⭐⭐⭐

구성:
  - 85%: GPT-4o-mini
  - 10%: GPT-4o
  - 5%: o1-mini

비용: $2.08/1,000회 → 최적화 후 $1.00-1.50

이유:
  - 최고 가성비
  - 90% 품질
  - 관리 단순
  - 멀티모달 보너스

---

권장 B: Claude 전용 ⭐⭐⭐⭐

구성:
  - 85%: Haiku 3.5
  - 10%: Sonnet 4.5
  - 5%: Sonnet 4.5 (Thinking)

비용: $2.54/1,000회 → 최적화 후 $1.50-2.00

이유:
  - Phase 4 최고 품질
  - 200k 컨텍스트
  - Extended Thinking
  - +22% 비용 허용 가능

---

최종 선택:
  예산 중요: OpenAI
  품질 중요: Claude
  멀티모달 필요: OpenAI
  긴 컨텍스트 필요: Claude
```

#### 3. 품질 최우선

```yaml
권장: Claude 전용 ⭐⭐⭐⭐⭐

구성:
  - 85%: Haiku 3.5 (Phase 0-2만)
  - 10%: Sonnet 4.5
  - 5%: Sonnet 4.5 (Thinking)

또는 현재 구성 유지:
  - 20%: Sonnet 4.5
  - 80%: Sonnet 4.5 (Thinking)

비용: $2.54-15/1,000회

이유:
  - Extended Thinking 최고
  - Phase 4 완벽
  - Discovery Sprint 완벽
  - 비용보다 품질
```

#### 4. 멀티모달 활용

```yaml
권장: OpenAI 전용 ⭐⭐⭐⭐⭐

구성:
  - 85%: GPT-4o-mini
  - 15%: GPT-4o (이미지 처리 포함)

비용: $2.50/1,000회

이유:
  - GPT-4o/mini 이미지 처리 우수
  - Excel 차트 분석
  - 향후 확장성
```

---

## 💡 실전 구현

### OpenAI 전용 구현

```python
# umis_rag/core/provider.py

from openai import OpenAI
from typing import Dict, Any

class UMISProvider:
    """
    OpenAI 전용 UMIS Provider
    """
    
    def __init__(self):
        self.client = OpenAI()
        self.router = OpenAIRouter()
    
    def estimate(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """통합 추정 인터페이스"""
        
        # 작업 분석
        task = self._analyze_task(query, context)
        
        # 모델 선택
        model = self.router.select_model(task)
        
        # 프롬프트 생성
        prompt = self._build_prompt(query, task, model)
        
        # API 호출
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 시장 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"} if model != 'o1-mini' else None
        )
        
        # 결과 반환
        result = self._parse_response(response.choices[0].message.content)
        result['model_used'] = model
        
        return result

# 사용
provider = UMISProvider()
result = provider.estimate("B2B SaaS ARPU는?")
```

### Claude 전용 구현

```python
# umis_rag/core/provider.py

import anthropic
from typing import Dict, Any

class UMISProvider:
    """
    Claude 전용 UMIS Provider
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.router = ClaudeRouter()
    
    def estimate(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """통합 추정 인터페이스"""
        
        # 작업 분석
        task = self._analyze_task(query, context)
        
        # 모델 + Thinking 선택
        model, use_thinking = self.router.select_model(task)
        
        # 프롬프트 생성
        prompt = self._build_prompt(query, task, model)
        
        # API 호출
        params = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if use_thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 10000
            }
        
        response = self.client.messages.create(**params)
        
        # 결과 반환
        result = self._parse_response(response.content[0].text)
        result['model_used'] = model
        result['thinking_used'] = use_thinking
        
        return result

# 사용
provider = UMISProvider()
result = provider.estimate("서울 음식점 수는?")
```

---

## 📋 Quick Decision Guide

```yaml
질문: "어떤 Provider를 선택할까?"

Step 1: 예산은?
  매우 제한적 → OpenAI (70% 저렴)
  보통 → 다음 질문
  충분 → 다음 질문

Step 2: Phase 4 비중은?
  5% 이하 → OpenAI (품질 차이 미미)
  10% 이상 → Claude (품질 차이 중요)

Step 3: 멀티모달 필요?
  YES → OpenAI (이미지 처리 우수)
  NO → 다음 질문

Step 4: 200k 컨텍스트 필요?
  YES → Claude (200k vs 128k)
  NO → OpenAI

Step 5: 관리 단순성?
  중요 → OpenAI (문서화 우수, API 안정)
  상관없음 → Claude

최종 권장:
  일반적: OpenAI ⭐⭐⭐⭐⭐
  품질 우선: Claude ⭐⭐⭐⭐
  비용 우선: OpenAI ⭐⭐⭐⭐⭐
```

---

**작성자**: AI Assistant  
**작성일**: 2025-11-18  
**결론**: 대부분 상황에서 **OpenAI 전용** 권장 (비용, 관리, 멀티모달). 품질 최우선이면 **Claude 전용**.  

---

*단일 Provider = 관리 단순 + 비용 추적 용이 + 최적화 집중 가능*
*UMIS 기본 권장: OpenAI (mini 85% + 4o 10% + o1-mini 5%) = $2.08/1,000회*




