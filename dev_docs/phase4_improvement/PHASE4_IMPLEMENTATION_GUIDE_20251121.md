# Phase 4 Few-shot 개선 구현 요약

**작성일**: 2025-11-21  
**목적**: Few-shot 예시를 Phase 4에 실제 적용  
**작업량**: 약 1-2시간 예상

---

## 🎯 적용할 개선 사항

### 1. Few-shot 예시 추가

**파일**: `umis_rag/agents/estimator/phase4_fermi.py`  
**메서드**: `_build_llm_prompt()` (라인 1240)

**현재 프롬프트**:
```python
prompt = f"""질문: {question}

가용한 데이터:
{available_str}

임무:
1. 이 질문에 답하기 위한 계산 모형을 3-5개 제시하세요.
...
```

**개선 후 프롬프트**:
```python
prompt = f"""먼저 올바른 Fermi 분해 예시를 보여드리겠습니다:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
예시: 서울시 택시 수

{{
    "value": 70000,
    "unit": "대",
    "decomposition": [
        {{
            "step": "1. 서울 인구",
            "value": 10000000,
            "calculation": "약 1000만명",
            "reasoning": "서울시 통계청 기준 약 1000만명"
        }},
        {{
            "step": "2. 1인당 연간 택시 이용",
            "value": 20,
            "calculation": "월 1-2회 × 12",
            "reasoning": "대중교통 중심이므로 택시는 보조 수단"
        }},
        {{
            "step": "3. 연간 총 이용",
            "value": 200000000,
            "calculation": "step1 × step2 = 10000000 × 20",
            "reasoning": "전체 인구의 택시 이용을 합산"
        }},
        {{
            "step": "4. 택시당 연간 운행",
            "value": 3000,
            "calculation": "일 10회 × 300일",
            "reasoning": "2교대 운행 가정"
        }},
        {{
            "step": "5. 필요 대수",
            "value": 66667,
            "calculation": "step3 / step4 = 200000000 / 3000",
            "reasoning": "총 이용을 택시당 운행으로 나눔"
        }}
    ],
    "final_calculation": "step3 / step4 = 66667 ≈ 70000",
    "calculation_verification": "1000만 × 20 / 3000 = 66667 ✓"
}}

핵심 규칙:
1. ⭐ 각 step의 value는 이전 step들로부터 명확히 계산
2. ⭐ calculation에 "step1 × step2" 같은 명시적 수식
3. ⭐ reasoning에 해당 값을 사용한 합리적 근거
4. ⭐ final_calculation은 step들의 value를 조합
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이제 실제 문제:

질문: {question}

가용한 데이터:
{available_str}

⚠️ 중요: 위 예시처럼 각 단계의 값이 최종값으로 명확히 계산되어야 합니다!
⚠️ 핵심: 각 가정에 대한 합리적인 근거를 반드시 제시해야 합니다!

임무:
1. 이 질문에 답하기 위한 분해를 제시하세요.
2. 각 단계에 calculation과 reasoning을 모두 포함하세요.
3. 가용한 데이터를 최대한 활용하세요.
...
```

---

## 📊 예상 효과

### Before (현재)
```
LLM 응답:
{
    "models": [
        {"formula": "result = A × B × C"}
    ]
}

문제:
- 계산 연결성 부족
- Reasoning 없음
```

### After (Few-shot)
```
LLM 응답:
{
    "decomposition": [
        {
            "step": "1. 변수",
            "value": 100,
            "calculation": "step1 × 0.5",
            "reasoning": "업계 평균 50%"
        }
    ],
    "final_calculation": "step1 × step2 = ..."
}

개선:
- ✅ 계산 연결성 145% 향상
- ✅ Reasoning 포함
- ✅ 검증 가능
```

---

## 🚀 구현 계획

### Step 1: Few-shot 예시 추가 (30분)

**위치**: `_build_llm_prompt()` 메서드

**작업**:
1. Few-shot 예시 문자열 작성
2. 프롬프트 앞부분에 추가
3. 핵심 규칙 강조

### Step 2: 계산 검증 메서드 추가 (30분)

**새 메서드**: `_verify_calculation_connectivity()`

```python
def _verify_calculation_connectivity(self, decomposition: List[Dict], final_value: float) -> Dict:
    """
    분해 값들이 최종값으로 올바르게 계산되는지 자동 검증
    
    Returns:
        {
            'verified': bool,
            'method': str,
            'calculated_value': float,
            'error': float,
            'score': int  # 0-25점
        }
    """
    # 다양한 조합 시도 (마지막 값, 합계, 곱셈 등)
    # 가장 오차가 작은 방법 선택
    # 10% 이내면 통과
```

### Step 3: Config 수정 (10분)

**파일**: `umis_rag/agents/estimator/models.py`

```python
@dataclass
class Phase4Config:
    max_depth: int = 4
    max_variables: int = 10
    
    # v7.7.1+ Few-shot 설정
    use_fewshot: bool = True
    verify_calculation: bool = True
    
    # 품질 기준
    min_calculation_score: int = 15
```

### Step 4: 테스트 (20분)

**테스트 케이스**:
1. 간단한 문제 (한국 사업자 수)
2. 계산 연결성 점수 확인
3. Reasoning 존재 확인

---

## 📁 수정할 파일

1. ✅ `umis_rag/agents/estimator/phase4_fermi.py`
   - `_build_llm_prompt()`: Few-shot 추가
   - `_verify_calculation_connectivity()`: 새 메서드

2. ✅ `umis_rag/agents/estimator/models.py`
   - `Phase4Config`: Few-shot 옵션 추가

3. ✅ `tests/test_phase4_fewshot.py` (새 파일)
   - Few-shot 효과 검증 테스트

---

## ⚠️ 주의사항

### 1. 기존 코드 호환성

- Native Mode는 그대로 유지
- External Mode (LLM API)만 Few-shot 추가
- 기존 테스트 통과 필수

### 2. 프롬프트 크기

- Few-shot 예시: 약 500토큰
- 총 프롬프트: 약 800-1000토큰
- gpt-5.1: 문제없음

### 3. 성능 영향

- 응답 시간: +1-2초 (무시 가능)
- 비용: +20% (Few-shot 포함)
- 품질 향상: +145% ⭐

---

## 🎯 성공 기준

### 테스트 통과 기준

1. ✅ 계산 연결성 점수: 40/50 이상
2. ✅ Reasoning 존재율: 80% 이상
3. ✅ 기존 테스트: 모두 통과

### 예상 성능

```
Before:
- 계산 연결성: 18-30/40
- Reasoning: 0%

After:
- 계산 연결성: 40-50/50 (+145%)
- Reasoning: 80-100%
```

---

## 📋 구현 체크리스트

- [ ] Few-shot 예시 작성
- [ ] `_build_llm_prompt()` 수정
- [ ] `_verify_calculation_connectivity()` 추가
- [ ] `Phase4Config` 수정
- [ ] 기존 테스트 실행 및 통과 확인
- [ ] 새 테스트 작성 및 실행
- [ ] 문서 업데이트

---

**다음 단계**: `_build_llm_prompt()` 메서드 수정부터 시작!

**예상 완료 시각**: 약 1-2시간 후

**예상 효과**: 계산 연결성 145% 향상, Reasoning 100% 포함

