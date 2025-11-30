# TOON Format 분석 - LLM 프롬프트 최적화

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**출처**: [TOON GitHub](https://github.com/toon-format/toon)

---

## 🎯 TOON이란?

**Token-Oriented Object Notation** - LLM 프롬프트를 위한 컴팩트하고 결정론적인 JSON 대체 포맷

### 핵심 특징

```yaml
설계 목적: LLM 토큰 효율성
대상: 프롬프트 데이터 직렬화
장점:
  - JSON 대비 토큰 수 감소
  - 인간 가독성 유지
  - 결정론적 출력
  - LLM 자연 파싱

적합:
  - Uniform 배열 (같은 필드, 원시값)
  - 프롬프트 컨텍스트
  - 테이블형 데이터

부적합:
  - 비균일 데이터
  - 깊은 중첩 구조
  - API 응답 (JSON이 표준)
```

---

## 📊 TOON vs JSON - 구문 비교

### 예시 1: 객체 배열 (UMIS 패턴 데이터)

**JSON**:
```json
{
  "items": [
    { "sku": "A1", "name": "Widget", "qty": 2, "price": 9.99 },
    { "sku": "B2", "name": "Gadget", "qty": 1, "price": 14.5 }
  ]
}
```

**TOON**:
```toon
items[2]{sku,name,qty,price}:
  A1,Widget,2,9.99
  B2,Gadget,1,14.5
```

**분석**:
```
JSON: 135 chars
TOON: 75 chars
감소: 44.4%

토큰 (GPT-4 tokenizer):
JSON: ~35 tokens
TOON: ~25 tokens
감소: 28.5%
```

---

### 예시 2: UMIS Explorer 패턴 (실제 데이터)

**JSON**:
```json
{
  "patterns": [
    {
      "id": "BM001",
      "name": "Subscription Model",
      "category": "Revenue Model",
      "triggers": ["High churn", "Predictable costs"]
    },
    {
      "id": "BM002",
      "name": "Freemium",
      "category": "Revenue Model",
      "triggers": ["Low barrier", "Viral growth"]
    }
  ]
}
```

**TOON**:
```toon
patterns[2]{id,name,category}:
  BM001,Subscription Model,Revenue Model
  BM002,Freemium,Revenue Model
triggers:
  - [2]: High churn,Predictable costs
  - [2]: Low barrier,Viral growth
```

**문제점**:
- TOON은 중첩된 배열(`triggers`)에서 list 모드로 전환
- Uniform하지 않은 데이터에서는 JSON과 비슷하거나 더 김

---

## 🔍 UMIS 적용 시나리오 분석

### ✅ TOON이 우수한 경우

#### 1. 벤치마크 데이터 (Quantifier)

**데이터 특성**:
- Uniform 테이블 구조
- 많은 행 (100개+)
- 원시값만
- LLM에게 전달

**JSON**:
```json
{
  "benchmarks": [
    {"industry": "SaaS", "metric": "CAC", "p50": 1200, "p90": 3500},
    {"industry": "SaaS", "metric": "LTV", "p50": 5000, "p90": 15000},
    {"industry": "E-commerce", "metric": "CAC", "p50": 50, "p90": 150}
  ]
}
```

**TOON**:
```toon
benchmarks[3]{industry,metric,p50,p90}:
  SaaS,CAC,1200,3500
  SaaS,LTV,5000,15000
  E-commerce,CAC,50,150
```

**효과**:
```
100개 벤치마크 기준:
JSON: ~2,500 tokens
TOON: ~1,500 tokens
감소: 40%

프롬프트 비용 절감:
- GPT-4: $0.03/1K tokens (input)
- 절감: $0.03/요청
- 1,000 요청: $30 절감
```

---

#### 2. Estimator Learned Rules

**데이터 특성**:
- 2,000개 규칙 (진화)
- Uniform 구조
- 프롬프트에 포함

**예시**:
```toon
rules[2000]{pattern,condition,value,confidence}:
  SaaS_CAC,ARR<1M,1500,0.85
  SaaS_LTV,Churn<5%,8000,0.90
  E-comm_CVR,Traffic>10K,2.5,0.75
  ...
```

**vs Protobuf**:
```
Protobuf: 더 작지만 (60% 감소)
  - LLM이 읽을 수 없음 (바이너리)
  - 프롬프트에 사용 불가

TOON: 적당히 작으면서 (40% 감소)
  - LLM이 직접 파싱 가능
  - 프롬프트에 삽입 가능
```

---

#### 3. 예제 데이터 (프롬프트)

**현재 (YAML)**:
```yaml
examples:
  - company: Netflix
    industry: Entertainment
    model: Subscription
    metrics:
      MRR: $1.2B
      Churn: 2.5%
  - company: Spotify
    industry: Music
    model: Freemium
    metrics:
      MRR: $800M
      Churn: 3.1%
```

**TOON**:
```toon
examples[2]{company,industry,model}:
  Netflix,Entertainment,Subscription
  Spotify,Music,Freemium
metrics:
  - MRR: 1.2B
    Churn: 2.5%
  - MRR: 800M
    Churn: 3.1%
```

**문제**: 중첩 구조에서 TOON의 장점 감소

---

### ❌ TOON이 부적합한 경우

#### 1. Agent 설정 (비균일)

**데이터**:
```yaml
agents:
  observer:
    name: Albert
    role: market_structure
    collections: [patterns, benchmarks]
  explorer:
    name: Steve
    role: opportunity_discovery
    collections: [patterns, cases, signals]
    rag_enabled: true
```

**문제**:
- 각 Agent마다 다른 필드
- 중첩된 객체
- TOON은 list 모드로 전환 → JSON과 비슷

---

#### 2. 비즈니스 모델 패턴 (복잡한 중첩)

**데이터**:
```yaml
pattern:
  id: BM001
  triggers: [signal1, signal2]
  examples:
    - company: X
      metrics: {...}
  validation:
    criteria: [...]
```

**문제**:
- 비균일 중첩
- 배열 안 객체 안 배열
- TOON의 강점 발휘 못함

---

## 📈 UMIS 적용 전략

### Tier 1: 프롬프트 데이터 (LLM Input)

```yaml
적용 대상:
  - 벤치마크 데이터 (100개+)
  - Estimator Rules (2,000개)
  - 예제 테이블
  - Discovery Sprint 결과

포맷 선택:
  개발: YAML (편집)
  프롬프트: TOON (LLM에게 전달)

변환 시점:
  - 런타임 (프롬프트 생성 시)
  - YAML → TOON → LLM
```

**구현**:
```python
from toon_format import encode  # Python 구현 필요

# 벤치마크 데이터
benchmarks = [
    {"industry": "SaaS", "metric": "CAC", "p50": 1200},
    {"industry": "SaaS", "metric": "LTV", "p50": 5000},
    # ... 100개
]

# TOON 인코딩
toon_data = encode(benchmarks)

# LLM 프롬프트에 삽입
prompt = f"""
Analyze the market using these benchmarks:

```toon
{toon_data}
```

Question: What is the typical CAC for SaaS?
"""
```

**효과**:
```
토큰 절감: 40%
프롬프트 비용: -40%
컨텍스트 윈도우: +67% 더 많은 데이터
```

---

### Tier 2: 설정 파일 (Storage)

```yaml
적용 대상:
  - 스키마 레지스트리 (비균일) ❌
  - Agent 설정 (비균일) ❌
  - 패턴 라이브러리 (복잡 중첩) ❌

권장: MessagePack / Protobuf
이유: TOON은 저장용이 아닌 프롬프트용
```

---

### Tier 3: API 응답 (Output)

```yaml
TOON 사용 불가:
  - API 표준은 JSON
  - 클라이언트 호환성
  - 생태계 도구

권장: JSON (표준)
```

---

## 🔬 벤치마크 (TOON vs 기존 포맷)

### 테스트: UMIS 벤치마크 100개

```python
# 데이터
benchmarks = [
    {"industry": "SaaS", "metric": "CAC", "p50": 1200, "p90": 3500, "count": 50},
    # ... 100개
]

# 포맷별 크기
import json, yaml, msgpack, toon_format

json_str = json.dumps({"benchmarks": benchmarks})
yaml_str = yaml.dump({"benchmarks": benchmarks})
msgpack_bin = msgpack.packb({"benchmarks": benchmarks})
toon_str = toon_format.encode({"benchmarks": benchmarks})

print(f"JSON:       {len(json_str)} chars")
print(f"YAML:       {len(yaml_str)} chars")
print(f"MessagePack:{len(msgpack_bin)} bytes")
print(f"TOON:       {len(toon_str)} chars")
```

**예상 결과** (100개 기준):
```
JSON:        8,500 chars  (~2,200 tokens)
YAML:        7,800 chars  (~2,000 tokens)
MessagePack: 3,200 bytes  (바이너리, LLM 불가)
TOON:        5,100 chars  (~1,300 tokens)

TOON 효과:
vs JSON: -40% 토큰
vs YAML: -35% 토큰
vs MessagePack: +59% 크기 BUT LLM 가독
```

---

## 💡 TOON의 독특한 가치

### 1. LLM 프롬프트 전용

```
다른 포맷들:
  MessagePack: 빠르지만 LLM 못 읽음
  Protobuf:    작지만 LLM 못 읽음
  JSON:        LLM 읽지만 verbose
  YAML:        LLM 읽지만 비효율

TOON:
  ✅ LLM이 자연스럽게 파싱
  ✅ 토큰 효율적
  ✅ 인간 가독성
  ✅ 구조 명시적 ([N], {fields})
```

---

### 2. 프롬프트 생성 (Output)

**시나리오**: LLM이 테이블 생성

**JSON 생성 (문제점)**:
```json
{
  "results": [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 2, "name": "Bob", "score": 87},
    ...
  ]
}
```

**문제**:
- 키 반복 (`"id":`, `"name":`, ...)
- LLM이 토큰 많이 생성
- 비용 증가

**TOON 생성**:
```toon
results[2]{id,name,score}:
  1,Alice,95
  2,Bob,87
```

**장점**:
- 키를 한 번만 생성
- 행만 반복 (토큰 절감)
- LLM 생성 비용 -40%

**프롬프트 예시**:
```
Return results in TOON format. Use this header:

results[N]{id,name,score}:

Then list rows with comma-separated values.
```

---

### 3. 양방향 최적화

```yaml
Input (LLM에게 전달):
  - YAML → TOON 변환
  - 프롬프트 토큰 -40%
  - 컨텍스트 절약

Output (LLM이 생성):
  - TOON 포맷 요청
  - 생성 토큰 -40%
  - 출력 비용 절약

총 효과:
  Input + Output 모두 절약!
```

---

## 🎯 UMIS 통합 권장사항

### Phase 1: 프롬프트 데이터만 (즉시)

```yaml
적용:
  - 벤치마크 데이터 → TOON
  - Estimator Rules → TOON
  - 예제 테이블 → TOON

구현:
  1. Python TOON 라이브러리 (개발 필요*)
  2. 프롬프트 빌더에 통합
  3. YAML → TOON 변환 함수

비용:
  - 개발: 1-2주
  - 라이브러리: 오픈소스 대기 중

효과:
  - 프롬프트 비용: -40%
  - 컨텍스트 용량: +67%
```

*현재 Python 구현은 개발 중 (공식 지원 예정)

---

### Phase 2: 하이브리드 전략 (1개월)

```yaml
저장 (Storage):
  설정: MessagePack (성능)
  패턴: MessagePack (성능)
  벤치마크: MessagePack (성능)

프롬프트 (LLM Input):
  벤치마크: TOON (토큰 효율)
  예제: TOON (토큰 효율)
  Rules: TOON (토큰 효율)

API (Output):
  클라이언트: JSON (표준)
```

**워크플로우**:
```
1. 원본: YAML (개발)
2. 빌드: YAML → MessagePack (저장)
3. 런타임: MessagePack → TOON (프롬프트)
4. LLM: TOON 읽기/생성
5. API: JSON (클라이언트)
```

---

## 🔧 구현 예시

### TOON Encoder for UMIS

```python
# umis_rag/utils/toon_encoder.py
from typing import List, Dict, Any

class UMISToonEncoder:
    """UMIS용 TOON 인코더 (Python 공식 라이브러리 대기)"""
    
    def encode_benchmarks(self, benchmarks: List[Dict]) -> str:
        """벤치마크를 TOON으로 인코딩"""
        if not benchmarks:
            return "benchmarks[0]:"
        
        # 필드 추출
        fields = list(benchmarks[0].keys())
        count = len(benchmarks)
        
        # 헤더
        header = f"benchmarks[{count}]{{{','.join(fields)}}}:\n"
        
        # 행
        rows = []
        for b in benchmarks:
            values = [self._format_value(b[f]) for f in fields]
            rows.append("  " + ",".join(values))
        
        return header + "\n".join(rows)
    
    def _format_value(self, value: Any) -> str:
        """값 포맷팅 (TOON 규칙)"""
        if isinstance(value, str):
            # 쉼표/줄바꿈 있으면 인용
            if ',' in value or '\n' in value:
                return f'"{value}"'
            return value
        elif isinstance(value, bool):
            return str(value).lower()
        elif value is None:
            return 'null'
        else:
            return str(value)

# 사용
encoder = UMISToonEncoder()

benchmarks = [
    {"industry": "SaaS", "metric": "CAC", "p50": 1200},
    {"industry": "SaaS", "metric": "LTV", "p50": 5000},
]

toon_str = encoder.encode_benchmarks(benchmarks)
print(toon_str)
# benchmarks[2]{industry,metric,p50}:
#   SaaS,CAC,1200
#   SaaS,LTV,5000
```

---

### 프롬프트 통합

```python
# umis_rag/agents/quantifier.py
from umis_rag.utils.toon_encoder import UMISToonEncoder

class QuantifierAgent:
    def __init__(self):
        self.toon = UMISToonEncoder()
    
    def build_prompt(self, industry: str, benchmarks: List[Dict]) -> str:
        """벤치마크를 TOON으로 인코딩하여 프롬프트 생성"""
        
        # TOON 인코딩
        toon_data = self.toon.encode_benchmarks(benchmarks)
        
        prompt = f"""
You are a market sizing expert. Analyze the {industry} industry.

Here are industry benchmarks in TOON format:

```toon
{toon_data}
```

Calculate the TAM using these benchmarks.
Return your calculations in TOON format with this header:
calculations[N]{{metric,method,value,confidence}}:
"""
        return prompt
```

---

## 📊 비교 요약표

| 포맷 | 크기 | 속도 | LLM 가독 | 프롬프트 적합 | 저장 적합 | API 적합 |
|------|------|------|----------|---------------|-----------|----------|
| **YAML** | 1.00x | 1.00x | ✅ | ⚠️ (verbose) | ✅ | ❌ |
| **JSON** | 1.05x | 0.30x | ✅ | ⚠️ (verbose) | ✅ | ✅ |
| **TOON** | **0.60x** | N/A* | ✅✅ | ✅✅ | ❌ | ❌ |
| **MessagePack** | 0.27x | 0.01x | ❌ | ❌ | ✅✅ | ❌ |
| **Protobuf** | 0.23x | 0.016x | ❌ | ❌ | ✅✅ | ⚠️ |

*TOON은 텍스트 포맷이므로 파싱 속도는 JSON과 비슷

---

## ⚠️ 제약사항

### 1. 구조적 제약

```yaml
적합:
  - Uniform 배열 (같은 필드)
  - 원시값 (문자열, 숫자, 불린)
  - 플랫한 테이블

부적합:
  - 비균일 객체
  - 깊은 중첩 (3단계+)
  - 복잡한 그래프 구조
```

---

### 2. 생태계 제약

```yaml
현재 상태 (2025-11):
  - TypeScript: 공식 지원 ✅
  - Python: 개발 중 ⚠️
  - 기타: 커뮤니티 구현

UMIS 영향:
  - Python 구현 필요
  - 자체 구현 또는 대기
  - 또는 TypeScript로 서비스
```

---

### 3. 용도 제약

```yaml
TOON은:
  ✅ 프롬프트 최적화 도구
  ❌ 범용 직렬화 포맷

JSON을 대체하지 않음:
  - API는 JSON 유지
  - 저장은 MessagePack/Protobuf
  - 프롬프트만 TOON
```

---

## 💰 비용 효과 분석

### 시나리오: 벤치마크 기반 시장 분석 (1,000회/월)

```yaml
프롬프트 구성:
  - 시스템 프롬프트: 500 tokens
  - 벤치마크 데이터: 100개
  - 사용자 쿼리: 50 tokens

JSON (현재):
  벤치마크: 2,200 tokens
  총: 2,750 tokens/요청
  비용: $0.0825/요청 (GPT-4)
  월 비용: $82.5

TOON:
  벤치마크: 1,300 tokens
  총: 1,850 tokens/요청
  비용: $0.0555/요청
  월 비용: $55.5

월 절감: $27 (-33%)
연 절감: $324
```

---

### 스케일 업 (10,000회/월)

```yaml
JSON: $825/월
TOON: $555/월

월 절감: $270
연 절감: $3,240
```

---

## ✅ 최종 권장사항

### TOON 채택 조건

```yaml
채택해야 하는 경우:
  ✅ Uniform 테이블 데이터가 많음
  ✅ LLM 프롬프트 비용이 높음
  ✅ 컨텍스트 윈도우가 부족
  ✅ Python 구현 개발 가능 또는 대기 가능

채택하지 말아야 하는 경우:
  ❌ 비균일 데이터가 대부분
  ❌ 프롬프트 비용이 낮음
  ❌ 즉시 프로덕션 필요 (Python 미지원)
  ❌ API/저장 용도
```

---

### UMIS 통합 전략

```yaml
단기 (관찰):
  - Python 공식 구현 릴리즈 대기
  - 벤치마크 데이터 TOON 시뮬레이션
  - 비용 절감 측정

중기 (3-6개월):
  - Python 구현 사용 가능 시
  - 벤치마크/Rules → TOON
  - 프롬프트 빌더 통합

장기 (선택):
  - LLM Output도 TOON 요청
  - 양방향 최적화
  - 총 비용 -40%
```

---

### 하이브리드 아키텍처 (최종)

```yaml
저장 (Disk/DB):
  설정: Protobuf (타입 안전)
  패턴: MessagePack (성능)
  벤치마크: MessagePack (성능)

프롬프트 (LLM):
  벤치마크: TOON (토큰 효율)
  예제: TOON (토큰 효율)
  Rules: TOON (토큰 효율)

API (External):
  응답: JSON (표준)

이유:
  - 각 용도에 최적 포맷
  - TOON은 프롬프트만
  - 총 효과 극대화
```

---

## 📚 참고 자료

- **TOON GitHub**: https://github.com/toon-format/toon
- **공식 사이트**: https://toonformat.dev
- **SPEC**: https://github.com/toon-format/toon/blob/main/SPEC.md
- **벤치마크**: https://github.com/toon-format/toon/tree/main/benchmarks

---

## 🎓 결론

TOON은 **LLM 프롬프트 최적화**라는 특정 목적에 최적화된 포맷입니다.

### UMIS에서의 위치

```
성능 최적화 (저장):
  MessagePack, Protobuf ✅

프롬프트 최적화 (LLM):
  TOON ✅✅

API 표준 (외부):
  JSON ✅
```

### 핵심 가치

1. **비용 절감**: 프롬프트 토큰 -40%
2. **용량 확장**: 컨텍스트에 +67% 더 많은 데이터
3. **양방향**: Input/Output 모두 최적화

### 채택 시기

- **지금**: Python 구현 대기 중 → 관찰
- **3-6개월**: Python 지원 시 → 도입
- **1년**: 성숙 후 → 전면 활용

---

**다음 단계**: Python TOON 구현 릴리즈 모니터링

