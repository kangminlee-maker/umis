# UMIS Guestimation System v3.0 - Design Specification

**Document Version**: 1.0  
**Date**: 2025-11-06  
**Status**: Draft  
**Author**: UMIS Development Team

---

## 📋 Document Information

### Purpose
이 문서는 UMIS Guestimation System v3.0의 전체 설계를 정의합니다. v2.1의 근본적 한계를 해결하고, "Context-Aware Judgment" 시스템을 구현하기 위한 완전한 아키텍처 및 구현 가이드를 제공합니다.

### Scope
- **In Scope**: Guestimation System v3.0 전체 설계 (아키텍처, 컴포넌트, API, 데이터 모델)
- **Out of Scope**: Fermi Model Search 재설계 (기존 유지, 일부 수정만), RAG 시스템 변경

### Audience
- AI Developer (Cursor Agent)
- System Architect
- Future Maintainers

### References
- `SESSION_SUMMARY_20251106_FERMI_COMPLETE.md` - v2.1 완성 기록
- `CURRENT_STATUS.md` - 현재 시스템 상태
- `GUESTIMATION_FLOWCHART.md` - v2.1 플로우차트
- `umis_rag/utils/multilayer_guestimation.py` - v2.1 구현
- `umis_rag/utils/fermi_model_search.py` - Fermi 구현

---

## 🎯 Executive Summary

### Problem Statement

**v2.1의 근본적 문제**:
```yaml
현재 Multi-Layer Guestimation:
  구조: Sequential Fallback with Early Return
  동작: Layer 1 → Layer 2 → ... → 첫 성공 시 즉시 리턴
  
  문제점:
    ❌ "판단" 없음 (단순 if-else 체인)
    ❌ 정보 종합 없음 (첫 성공만 사용)
    ❌ 맥락 고려 없음
    ❌ 트레이드오프 평가 없음
```

**실제 필요**:
```yaml
진짜 판단 시스템:
  1. 맥락 파악: 질문 의도, 도메인, 세분화
  2. 정보 수집: 모든 관련 출처
  3. 증거 평가: 맥락에 비추어 각 증거 평가
  4. 종합 판단: 가중치 고려한 최종 판단
```

### Solution Overview

**v3.0 설계**:

```
Context-Aware Judgment System
  = 3-Tier Architecture + Judgment Components

3-Tier:
  Tier 1: Fast Path (90% 케이스, <1초, $0)
  Tier 2: Judgment Path (8% 케이스, 2-5초, $0.01-0.05)
  Tier 3: Fermi Recursion (2% 케이스, 10-30초, $0.1-1)

4 Core Components:
  1. ComplexityAnalyzer - 어느 Tier?
  2. ContextAnalyzer - 맥락 파악
  3. EvidenceCollector - 증거 수집
  4. JudgmentSynthesizer - 종합 판단
```

### Key Benefits

```yaml
기술적 개선:
  ✅ Sequential Fallback → Context-Aware Judgment
  ✅ 첫 성공만 사용 → 모든 증거 종합
  ✅ 맥락 무시 → 맥락 기반 평가
  ✅ 고정 전략 → 적응적 전략

성능 개선:
  ✅ 확실할 때 빠름 (Tier 1, 90%)
  ✅ 복잡할 때 정확 (Tier 2-3)
  ✅ 비용 최적화 (평균 <$0.01)

사용성 개선:
  ✅ 추론 투명성 (모든 증거 + 평가 과정)
  ✅ 신뢰도 정량화
  ✅ 불확실성 명시
```

### Migration Path

```yaml
v2.1 → v3.0:
  Phase 1: v3.0 구현 (병렬)
  Phase 2: 테스트 및 검증
  Phase 3: 점진적 마이그레이션
  Phase 4: v2.1 Deprecation
  
  하위 호환성: 
    - API 시그니처 유지
    - 설정 파일 호환
    - 기존 프로젝트 동작 보장
```

---

## 📐 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Estimation Entry Point                         │
│         estimate(question, context) → Result                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │   ComplexityAnalyzer              │
        │   analyze() → ComplexityResult    │
        └───────────┬───────────────────────┘
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
    ┌─────┐    ┌─────────┐  ┌──────────┐
    │Tier1│    │  Tier2  │  │  Tier3   │
    │Fast │    │Judgment │  │  Fermi   │
    └──┬──┘    └────┬────┘  └────┬─────┘
       │            │            │
       │       ┌────▼────┐       │
       │       │Context  │       │
       │       │Analyzer │       │
       │       └────┬────┘       │
       │            │            │
       │       ┌────▼────────┐   │
       │       │Evidence     │   │
       │       │Collector    │   │
       │       └────┬────────┘   │
       │            │            │
       │       ┌────▼────────┐   │
       │       │Judgment     │   │
       │       │Synthesizer  │   │
       │       └────┬────────┘   │
       │            │            │
       └────────────┼────────────┘
                    ▼
            ┌──────────────┐
            │ Final Result │
            └──────────────┘
```

### 1.2 Component Interaction

```
User Request
    ↓
[Entry Point]
    ↓
[ComplexityAnalyzer]
    ├→ score < 0.25 → [Tier 1 Fast]
    ├→ score < 0.60 → [Tier 2 Judgment]
    │                     ↓
    │                 [ContextAnalyzer]
    │                     ↓
    │                 [EvidenceCollector] (병렬 수집)
    │                     ↓
    │                 [JudgmentSynthesizer]
    │
    └→ score >= 0.60 → [Tier 3 Fermi]
                           ↓
                       [Fermi Model Search]
                           ↓
                       재귀: estimate() 호출
```

---

## 📦 2. Core Components Specification

### 2.1 ComplexityAnalyzer

**Responsibility**: 질문 복잡도 분석 및 Tier 추천

**Input**:
```python
question: str          # "한국 음식점 월평균 매출은?"
context: Context       # 맥락 정보 (optional)
```

**Output**:
```python
ComplexityResult:
    score: float                    # 0.0 ~ 1.0
    recommended_tier: int           # 1, 2, or 3
    strategy: str                   # "fast_path", "judgment", "fermi"
    signals: Dict[str, Any]         # 판단 근거
    reasoning: List[str]            # 추론 과정
```

**Algorithm**:
```python
score = (
    question_type_score * 0.30 +      # 질문 유형
    data_availability_score * 0.25 +  # 데이터 가용성
    variable_count_score * 0.25 +     # 예상 변수 개수
    domain_specificity_score * 0.20   # 도메인 특수성
)

if score < 0.25:
    tier = 1, strategy = "fast_path"
elif score < 0.60:
    tier = 2, strategy = "judgment_synthesis"
else:
    tier = 3, strategy = "fermi_decomposition"
```

**Detailed Scoring Logic**:

**Design Philosophy**: 

```yaml
문제: 하드코딩된 키워드 리스트는 확장성 없음
  - "피자 배달 시장", "유아용 장난감", "호텔 객실 회전율" 등 무한한 질문 가능
  - 키워드 리스트로 모든 경우 커버 불가능
  - 실제 세계는 너무 다양함

해결책: Hybrid Approach (규칙 + LLM + 임베딩)
  
  ┌─────────────────────────────────────────────────┐
  │ Layer 1: 빠른 패턴 체크 (90% 케이스)            │
  │   - 문법 구조 분석 (정규식)                     │
  │   - 특정 패턴 매칭 (시간, 복합 지표 등)         │
  │   - LLM 없이 0.001초                            │
  │   - Confidence >= 0.8 → 사용                    │
  └─────────────────┬───────────────────────────────┘
                    │ Confidence < 0.8
                    ▼
  ┌─────────────────────────────────────────────────┐
  │ Layer 2: LLM 분류 (10% 케이스)                  │
  │   - Native Mode: Cursor LLM ($0, 1-2초)        │
  │   - 간단한 프롬프트 (100-200 토큰)              │
  │   - JSON 응답                                    │
  │   - 캐싱 불필요 (비용 $0, 속도 충분)            │
  └─────────────────┬───────────────────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────────────────┐
  │ Layer 3: 임베딩 유사도 (특정 케이스)            │
  │   - 전문 용어 유사도 체크                       │
  │   - RAG 벤치마크 검색                           │
  │   - 프로젝트 데이터 매칭                        │
  └─────────────────────────────────────────────────┘

핵심 원칙:
  1. 확실할 땐 규칙 (빠름, 비용 없음)
  2. 불확실할 땐 LLM (정확함, Native Mode $0)
  3. 단순하게 유지 (캐싱 같은 불필요한 복잡도 제거)
  4. 임베딩 활용 (의미 기반 매칭)

캐싱 제거 이유:
  ❌ 복잡도 증가 (Redis/파일/메모리 구현 필요)
  ❌ 효익 미미 (Native Mode 비용 $0, 속도 1-2초 충분)
  ❌ 일관성 문제 (Stale data 가능성)
  ✅ YAGNI 원칙 (You Aren't Gonna Need It)
```

**4가지 점수 변수별 전략**:

```yaml
1. question_type_score:
   - 빠른 패턴: 문법 구조 (정규식)
   - 불확실 시: LLM 분류
   - 확장성: 무한한 질문 커버 가능

2. data_availability_score:
   - 프로젝트 데이터: 임베딩 유사도 매칭
   - 공개 데이터: LLM 판단
   - RAG: 벤치마크 검색
   - 확장성: 새로운 데이터 소스 자동 판단

3. variable_count_score:
   - LLM 분해 구조 분석
   - 휴리스틱 보조 (수식어 카운트)
   - 확장성: 복잡한 질문도 분해 가능

4. domain_specificity_score:
   - 임베딩: 전문 용어 유사도
   - LLM: 도메인 수준 판단
   - 확장성: 새로운 도메인 자동 인식
```

**Confidence Calculation (신뢰도 계산)**:

```yaml
핵심 질문: "이 패턴 매칭이 얼마나 확실한가?"

문제:
  - "음식점" 키워드 → simple_estimate
  - 하지만 얼마나 확실한가? 0.5? 0.8? 0.95?

해결책: Signal-based Confidence
  여러 신호를 종합하여 확률적으로 계산
```

**Confidence 계산 공식**:

```python
def _calculate_pattern_confidence(
    self,
    question: str,
    matched_pattern: str
) -> float:
    """
    패턴 매칭 신뢰도 계산
    
    여러 신호를 종합하여 0.0 ~ 1.0 반환
    """
    
    signals = []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Signal 1: 패턴 매칭 강도 (50%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    match_strength = self._calculate_match_strength(question, matched_pattern)
    signals.append(('match_strength', match_strength, 0.50))
    
    """
    예시:
      질문: "한국 인구는?"
      패턴: factual (정의 질문)
      
      체크:
        - 문법 패턴 정확히 일치: ".+는?$" ✅ (1.0)
        - "인구" 같은 사실 키워드 포함 ✅ (1.0)
        - 추정 키워드 없음 ("얼마", "몇") ✅ (1.0)
      
      match_strength = (1.0 + 1.0 + 1.0) / 3 = 1.0
    
    예시 2:
      질문: "음식점 매출은?"
      패턴: simple_estimate
      
      체크:
        - "매출" 키워드 ✅ (0.8)
        - 하지만 맥락 불명확 (0.6)
        - 수식어 적음 (0.7)
      
      match_strength = (0.8 + 0.6 + 0.7) / 3 = 0.70
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Signal 2: 반증 신호 (30%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    counter_signals = self._check_counter_signals(question, matched_pattern)
    signals.append(('counter_signals', 1.0 - counter_signals, 0.30))
    
    """
    반증 신호: 패턴과 모순되는 키워드
    
    예시:
      패턴: factual
      반증: "얼마", "몇", "예측" (추정/예측 키워드)
      
      질문: "한국 인구는 얼마?"
        → factual 패턴 매칭
        → 하지만 "얼마" 발견 (반증!)
        → counter_signals = 0.5
        → 신뢰도 하락
    
    예시 2:
      패턴: simple_estimate
      반증: "3년 후", "미래" (예측 키워드)
      
      질문: "3년 후 음식점 매출은?"
        → simple_estimate 매칭
        → "3년 후" 발견 (반증!)
        → counter_signals = 0.8
        → 신뢰도 크게 하락
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Signal 3: 구조 명확성 (20%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    structural_clarity = self._assess_structural_clarity(question)
    signals.append(('structural_clarity', structural_clarity, 0.20))
    
    """
    구조 명확성: 질문 구조가 얼마나 명확한가?
    
    명확:
      - "X는?" (단일 개념)
      - "A의 B는?" (명확한 관계)
    
    모호:
      - "X Y Z는?" (여러 개념)
      - 복합 문장
    
    예시:
      "한국 인구는?" → 0.95 (매우 명확)
      "음식점 평균 매출은?" → 0.80 (명확)
      "온라인 음식 배달 시장 성장률은?" → 0.60 (복잡)
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 종합 Confidence 계산
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    total_confidence = sum(
        signal_value * weight 
        for (name, signal_value, weight) in signals
    )
    
    return total_confidence


def _calculate_match_strength(self, question: str, pattern: str) -> float:
    """패턴 매칭 강도"""
    
    if pattern == 'factual':
        score = 0.0
        
        # 문법 매칭
        if re.match(r'.+(은|는)\??$', question):
            score += 0.4
        
        # 사실 키워드
        factual_keywords = ['인구', '면적', '수도', '시간']
        if any(kw in question for kw in factual_keywords):
            score += 0.4
        
        # 추정 키워드 없음
        estimate_keywords = ['얼마', '몇', '규모']
        if not any(kw in question for kw in estimate_keywords):
            score += 0.2
        
        return min(score, 1.0)
    
    elif pattern == 'simple_estimate':
        score = 0.0
        
        # 추정 키워드
        if any(kw in question for kw in ['평균', '대략', '얼마']):
            score += 0.3
        
        # 단순 지표
        if any(kw in question for kw in ['매출', '가격', '비용']):
            score += 0.4
        
        # 복잡 키워드 없음
        if not any(kw in question for kw in ['시장', '규모', 'TAM']):
            score += 0.3
        
        return min(score, 1.0)
    
    # ... 다른 패턴들

def _check_counter_signals(self, question: str, pattern: str) -> float:
    """반증 신호 체크 (0.0 = 반증 없음, 1.0 = 강한 반증)"""
    
    counter_patterns = {
        'factual': ['얼마', '몇', '규모', '예측'],
        'simple_estimate': ['3년 후', '미래', '시장 규모'],
        'complex_estimate': ['단순히', '그냥'],
        'prediction': ['과거', '현재']
    }
    
    if pattern in counter_patterns:
        counter_keywords = counter_patterns[pattern]
        matched_counters = [kw for kw in counter_keywords if kw in question]
        
        # 반증 강도
        counter_strength = len(matched_counters) * 0.3
        return min(counter_strength, 1.0)
    
    return 0.0

def _assess_structural_clarity(self, question: str) -> float:
    """구조 명확성"""
    
    # 길이 (짧을수록 명확)
    length_score = max(1.0 - len(question) / 50, 0.5)
    
    # 수식어 개수 (적을수록 명확)
    modifier_count = len(self._extract_modifiers(question))
    modifier_score = max(1.0 - modifier_count * 0.1, 0.5)
    
    # 복합 문장 (단일 문장이 명확)
    is_compound = ',' in question or '그리고' in question
    compound_score = 0.7 if is_compound else 1.0
    
    return (length_score + modifier_score + compound_score) / 3
```

**실제 계산 예시**:

```python
# 예제 1: "한국 인구는?"
pattern = 'factual'

match_strength:
  - 문법 매칭 ".+는?$": 0.4
  - "인구" 키워드: 0.4
  - 추정 키워드 없음: 0.2
  = 1.0

counter_signals:
  - 반증 키워드 없음
  = 0.0 → 1.0 (반전)

structural_clarity:
  - 길이 8자: 1.0
  - 수식어 1개 ("한국"): 0.9
  - 단일 문장: 1.0
  = 0.97

confidence = 1.0×0.5 + 1.0×0.3 + 0.97×0.2 = 0.994 ✅
→ 0.994 >= 0.95 → Tier 1 처리!


# 예제 2: "음식점 창업 예상 매출은?"
pattern = 'simple_estimate'

match_strength:
  - "매출" 키워드: 0.4
  - 복잡 키워드 없음: 0.3
  = 0.7

counter_signals:
  - "창업" (의사결정 맥락, 미묘함): 0.3
  = 0.7 (반전)

structural_clarity:
  - 길이 15자: 0.7
  - 수식어 2개 ("음식점", "창업"): 0.8
  - 단일 문장: 1.0
  = 0.83

confidence = 0.7×0.5 + 0.7×0.3 + 0.83×0.2 = 0.726
→ 0.726 < 0.95 → Tier 2로 넘김! ✅


# 예제 3: "3년 후 음식점 매출은?"
pattern = 'simple_estimate' (잘못된 매칭!)

match_strength:
  - "매출" 키워드: 0.4
  = 0.4 (낮음)

counter_signals:
  - "3년 후" (prediction 반증!): 0.8
  = 0.2 (반전, 낮음!)

structural_clarity:
  - 0.80

confidence = 0.4×0.5 + 0.2×0.3 + 0.8×0.2 = 0.42
→ 0.42 < 0.95 → Tier 2로 넘김! ✅
→ Tier 2에서 LLM이 'prediction' 정확히 판단
```

---

**1. question_type_score (30% 가중치)**

```python
def _classify_question_type(self, question: str) -> Tuple[str, float]:
    """
    질문 유형 분류 및 점수 계산
    
    Strategy:
      1. 빠른 패턴 체크 (문법 구조 기반)
      2. 불확실하면 LLM 분류 (Native Mode $0)
    
    Returns:
        (type_name, score): 유형과 점수 (0.0 ~ 1.0)
    
    Note: 캐싱 불필요
      - Native Mode 비용: $0
      - 응답 시간: 1-2초 (충분히 빠름)
      - 복잡도 증가 vs 효익 미미
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: 빠른 패턴 체크 (규칙 기반, LLM 없이)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pattern_result = self._check_question_patterns(question)
    
    if pattern_result['confidence'] >= 0.8:
        # 충분히 확실함 → 규칙 결과 사용
        return (pattern_result['type'], pattern_result['score'])
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: LLM 분류 (불확실한 경우)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    return self._classify_with_llm(question)


def _check_question_patterns(self, question: str) -> Dict:
    """
    문법 패턴 기반 빠른 체크 (LLM 없이)
    
    핵심 아이디어:
      - 키워드 매칭 ❌ → 문법 구조 분석 ✅
      - "무엇이 얼마인가?" 형태 분석
    """
    question_lower = question.lower()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Pattern 1: Factual (정의 질문)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # "X는?" "X란?" "X는 무엇?"
    if re.match(r'.+(은|는|이란|란)\??$', question_lower):
        # 하지만 "얼마", "몇" 있으면 추정 질문
        if not any(word in question_lower for word in ['얼마', '몇', '규모']):
            return {
                'type': 'factual',
                'score': 0.0,
                'confidence': 0.9,
                'reason': '정의 질문 패턴'
            }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Pattern 2: Prediction (시간 표현)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # "N년 후", "미래", "예측", "전망"
    time_future_patterns = [
        r'\d+년\s*후',
        r'\d+개월\s*후',
        r'미래',
        r'예측',
        r'전망',
    ]
    
    if any(re.search(pattern, question) for pattern in time_future_patterns):
        return {
            'type': 'prediction',
            'score': 0.9,
            'confidence': 0.95,
            'reason': '미래 시점 패턴'
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Pattern 3: Complex (복합 개념)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # "시장 규모", "TAM", "SAM", 전문 지표
    complex_patterns = [
        r'시장\s*(규모|크기)',
        r'TAM|SAM|SOM',
        r'unit\s*economics',
        r'LTV|CAC',
    ]
    
    if any(re.search(pattern, question, re.IGNORECASE) for pattern in complex_patterns):
        return {
            'type': 'complex_estimate',
            'score': 0.7,
            'confidence': 0.9,
            'reason': '복합 지표 패턴'
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Pattern 4: Simple vs Complex 구분
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 숫자 질문이지만 키워드 모호한 경우
    
    # "얼마", "몇" 있으면 숫자 질문
    if any(word in question_lower for word in ['얼마', '몇', '가격', '비용']):
        # 수식어 개수로 복잡도 판단
        modifier_count = len(re.findall(r'[가-힣]+\s+', question))
        
        if modifier_count >= 3:
            # 수식어 많음 → 복잡
            return {
                'type': 'complex_estimate',
                'score': 0.7,
                'confidence': 0.7,
                'reason': f'수식어 {modifier_count}개 (복잡)'
            }
        else:
            # 수식어 적음 → 단순
            return {
                'type': 'simple_estimate',
                'score': 0.3,
                'confidence': 0.7,
                'reason': f'수식어 {modifier_count}개 (단순)'
            }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 불확실 → LLM 필요
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    return {
        'type': 'simple_estimate',
        'score': 0.3,
        'confidence': 0.4,  # 낮은 신뢰도 → LLM 호출
        'reason': '패턴 불명확'
    }


def _classify_with_llm(self, question: str) -> Tuple[str, float]:
    """
    LLM을 사용한 질문 분류
    
    Native Mode 사용 시 비용 $0
    간단한 프롬프트로 빠르게 분류
    """
    
    prompt = f"""다음 질문을 4가지 유형 중 하나로 분류하세요.

질문: "{question}"

유형:
1. factual: 사실 확인 질문 (예: "한국 인구는?", "서울 면적은?")
2. simple_estimate: 단순 추정 (예: "카페 평균 가격은?", "음식점 고객수는?")
3. complex_estimate: 복잡한 추정 (예: "시장 규모는?", "LTV는?")
4. prediction: 미래 예측 (예: "3년 후 시장은?")

다음 JSON 형식으로만 답하세요:
{{"type": "...", "confidence": 0.0-1.0, "reason": "..."}}"""

    # LLM 호출 (Native Mode: Cursor LLM)
    response = self._call_llm(prompt, max_tokens=100)
    
    # JSON 파싱
    try:
        result = json.loads(response)
        
        # 점수 매핑
        score_mapping = {
            'factual': 0.0,
            'simple_estimate': 0.3,
            'complex_estimate': 0.7,
            'prediction': 0.9
        }
        
        return (result['type'], score_mapping[result['type']])
    
    except Exception as e:
        # LLM 실패 → 기본값
        logger.warning(f"LLM classification failed: {e}")
        return ('simple_estimate', 0.3)
```

**2. data_availability_score (25% 가중치)**

```python
def _check_data_availability(
    self, 
    question: str, 
    context: Optional[Context]
) -> float:
    """
    데이터 가용성 체크
    
    Strategy:
      1. 프로젝트 데이터 체크 (키워드 추출 + 유사도)
      2. 공개 데이터 가능성 판단 (LLM)
      3. RAG 벤치마크 체크 (임베딩 검색)
    
    Returns:
        score (0.0 ~ 1.0): 높을수록 데이터 없음 (복잡함)
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Check 1: 프로젝트 데이터 (가장 확실)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if context and context.project_data:
        # 키워드 추출 (NLP 기반)
        keywords = self._extract_keywords_nlp(question)
        
        # 유사도 기반 매칭 (임베딩)
        for key, value in context.project_data.items():
            similarity = self._calculate_similarity(question, key)
            if similarity >= 0.7:  # 70% 이상 유사
                return 0.0  # 데이터 있음!
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Check 2: 공개 데이터 가능성 (LLM 판단)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    public_data_availability = self._check_public_data_with_llm(question)
    
    if public_data_availability['available']:
        return public_data_availability['score']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Check 3: RAG 벤치마크 체크 (임베딩 검색)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    rag_similarity = self._check_rag_benchmarks(question)
    
    if rag_similarity >= 0.6:
        return 0.4  # RAG에 유사 데이터 있음
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Check 4: 완전히 새로운 질문
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    return 1.0


def _extract_keywords_nlp(self, question: str) -> List[str]:
    """NLP 기반 키워드 추출"""
    # 간단한 구현: 명사 추출
    # 실제로는 konlpy, spacy 등 사용 가능
    
    # 불용어 제거
    stopwords = {'은', '는', '이', '가', '를', '의', '에', '와', '과'}
    
    words = question.split()
    keywords = [w for w in words if w not in stopwords and len(w) >= 2]
    
    return keywords


def _check_public_data_with_llm(self, question: str) -> Dict:
    """LLM에게 공개 데이터 가능성 질문"""
    
    prompt = f"""다음 질문에 대해 공개 데이터를 찾을 수 있는지 판단하세요.

질문: "{question}"

다음을 판단하세요:
1. 공식 통계 (통계청, 정부 기관) 가능성
2. 산업 보고서 (리서치 기관) 가능성
3. 학술 논문/연구 가능성

JSON 형식으로 답하세요:
{{
  "available": true/false,
  "source_type": "official_stat" | "industry_report" | "academic" | "none",
  "score": 0.0-1.0,
  "reason": "..."
}}"""

    response = self._call_llm(prompt, max_tokens=150)
    
    try:
        result = json.loads(response)
        
        # 점수 매핑
        score_mapping = {
            'official_stat': 0.1,   # 매우 확실
            'industry_report': 0.3,  # 찾을 가능성
            'academic': 0.5,        # 계산 필요
            'none': 1.0             # 없음
        }
        
        return {
            'available': result['available'],
            'score': score_mapping.get(result['source_type'], 1.0),
            'reason': result['reason']
        }
    
    except Exception as e:
        # 실패 시 보수적 판단
        return {'available': False, 'score': 1.0}


def _check_rag_benchmarks(self, question: str) -> float:
    """RAG에서 유사 벤치마크 검색"""
    
    # 질문 임베딩
    question_embedding = self._get_embedding(question)
    
    # RAG 검색 (벤치마크 Collection)
    from umis_rag.agents.quantifier import QuantifierRAG
    
    quantifier = QuantifierRAG()
    results = quantifier.search_benchmarks(
        query_embedding=question_embedding,
        top_k=3
    )
    
    if not results:
        return 0.0
    
    # 최고 유사도 반환
    max_similarity = max(r['similarity'] for r in results)
    return max_similarity
```

**3. variable_count_score (25% 가중치)**

```python
def _estimate_variable_count(self, question: str) -> Tuple[int, float]:
    """
    예상 변수 개수 추정
    
    Strategy:
      1. 질문 분해 구조 분석 (LLM)
      2. 수식어/한정어 개수 카운트
      3. 종합 판단
    
    Returns:
        (count, score): 개수와 점수 (0.0 ~ 1.0)
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Method 1: LLM에게 분해 구조 질문
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    decomposition = self._ask_llm_decomposition(question)
    
    if decomposition['confidence'] >= 0.7:
        estimated_count = decomposition['variable_count']
    else:
        # LLM 불확실 → 휴리스틱 사용
        estimated_count = self._estimate_variables_heuristic(question)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Score 계산 (0.0 ~ 1.0)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if estimated_count == 0:
        score = 0.0
    elif estimated_count <= 2:
        score = 0.3
    elif estimated_count <= 5:
        score = 0.6
    else:
        score = 1.0
    
    return (estimated_count, score)


def _ask_llm_decomposition(self, question: str) -> Dict:
    """LLM에게 질문 분해 구조 질문"""
    
    prompt = f"""다음 질문을 답하려면 몇 개의 변수가 필요한지 분석하세요.

질문: "{question}"

예시:
- "한국 인구는?" → 0개 변수 (사실)
- "카페 평균 가격은?" → 1개 변수 (가격)
- "음식점 월매출은?" → 3개 변수 (고객수 × 객단가 × 방문빈도)
- "SaaS 시장 규모는?" → 5개 변수 (기업수 × 도입률 × ARPU × 세그먼트 × 지역)

JSON으로 답하세요:
{{
  "variable_count": 0-10,
  "decomposition": "분해 구조 설명",
  "confidence": 0.0-1.0
}}"""

    response = self._call_llm(prompt, max_tokens=200)
    
    try:
        result = json.loads(response)
        return result
    except:
        return {'variable_count': 3, 'confidence': 0.3}


def _estimate_variables_heuristic(self, question: str) -> int:
    """휴리스틱 기반 변수 개수 추정 (LLM 실패 시)"""
    
    estimated_count = 0
    
    # 곱셈 기호
    estimated_count += question.count('×') + question.count('*')
    
    # 수식어 개수 (NER)
    modifiers = self._extract_modifiers(question)
    estimated_count += len(modifiers) // 2
    
    # 기본값
    if estimated_count == 0:
        # 복잡도 단어로 추정
        if any(w in question for w in ['시장', '규모', 'TAM']):
            estimated_count = 4
        else:
            estimated_count = 1
    
    return estimated_count


def _extract_modifiers(self, question: str) -> List[str]:
    """수식어/한정어 추출"""
    
    # 패턴: "형용사 + 명사"
    # 예: "한국", "온라인", "B2B", "중소기업"
    
    # 간단한 구현: 특정 카테고리 키워드
    modifier_categories = {
        'region': ['한국', '미국', '서울', '글로벌', '아시아'],
        'channel': ['온라인', '오프라인', '모바일', '웹'],
        'target': ['B2B', 'B2C', 'B2G', '기업', '개인'],
        'size': ['대기업', '중소기업', '스타트업'],
        'model': ['구독', '일회성', '프리미엄', '무료'],
    }
    
    modifiers = []
    for category, keywords in modifier_categories.items():
        for keyword in keywords:
            if keyword in question:
                modifiers.append(keyword)
    
    return modifiers
```

**4. domain_specificity_score (20% 가중치)**

```python
def _assess_domain_specificity(self, question: str) -> Tuple[str, float]:
    """
    도메인 특수성 평가
    
    Strategy:
      1. 전문 용어 임베딩 유사도 체크
      2. LLM에게 도메인 판단 질문
      3. 종합 평가
    
    Returns:
        (domain_level, score): 수준과 점수 (0.0 ~ 1.0)
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Method 1: 전문 용어 임베딩 유사도
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    expert_similarity = self._check_expert_term_similarity(question)
    
    if expert_similarity >= 0.8:
        return ('expert', 1.0)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Method 2: LLM 판단
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    llm_assessment = self._assess_domain_with_llm(question)
    
    return (llm_assessment['level'], llm_assessment['score'])


def _check_expert_term_similarity(self, question: str) -> float:
    """전문 용어와의 임베딩 유사도 체크"""
    
    # 전문 용어 DB (임베딩 미리 계산)
    expert_terms = [
        'Churn', 'MRR', 'ARR', 'CAC Payback', 'Rule of 40',
        'Unit Economics', 'Cohort Analysis', 'EBITDA', 'Burn Rate'
    ]
    
    # 질문 임베딩
    q_embedding = self._get_embedding(question)
    
    # 각 전문 용어와 유사도 계산
    similarities = []
    for term in expert_terms:
        term_embedding = self._get_embedding(term)
        similarity = self._cosine_similarity(q_embedding, term_embedding)
        similarities.append(similarity)
    
    # 최대 유사도 반환
    return max(similarities) if similarities else 0.0


def _assess_domain_with_llm(self, question: str) -> Dict:
    """LLM에게 도메인 수준 판단 질문"""
    
    prompt = f"""다음 질문에 답하기 위해 필요한 지식 수준을 판단하세요.

질문: "{question}"

수준:
1. general: 일반 상식 (예: "인구", "면적", "날씨")
2. industry: 산업 지식 (예: "매출", "고객", "시장")
3. expert: 전문가 지식 (예: "Churn Rate", "Unit Economics", "EBITDA")

JSON으로 답하세요:
{{
  "level": "general" | "industry" | "expert",
  "score": 0.0-1.0,
  "domain": "구체적 도메인 (예: B2B_SaaS, E-commerce)",
  "reason": "..."
}}"""

    response = self._call_llm(prompt, max_tokens=150)
    
    try:
        result = json.loads(response)
        
        # 점수 매핑
        score_mapping = {
            'general': 0.0,
            'industry': 0.5,
            'expert': 1.0
        }
        
        return {
            'level': result['level'],
            'score': score_mapping.get(result['level'], 0.5),
            'domain': result.get('domain', 'Unknown'),
            'reason': result.get('reason', '')
        }
    
    except:
        # 실패 시 중간값
        return {'level': 'industry', 'score': 0.5}
```

**Complete Example**:

```python
def analyze(self, question: str, context: Optional[Context] = None) -> ComplexityResult:
    """완전한 복잡도 분석 예제"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예제 1: "한국 인구는?"
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    question = "한국 인구는?"
    
    # 1. 질문 유형: factual
    q_type, q_score = self._classify_question_type(question)
    # → ('factual', 0.0)
    
    # 2. 데이터 가용성: 공식 통계
    d_score = self._check_data_availability(question, context)
    # → 0.1 (통계청 데이터 있음)
    
    # 3. 변수 개수: 0개
    v_count, v_score = self._estimate_variable_count(question)
    # → (0, 0.0)
    
    # 4. 도메인 특수성: general
    domain, domain_score = self._assess_domain_specificity(question)
    # → ('general', 0.0)
    
    # 종합 점수
    total_score = (
        0.0 * 0.30 +   # question_type
        0.1 * 0.25 +   # data_availability
        0.0 * 0.25 +   # variable_count
        0.0 * 0.20     # domain_specificity
    ) = 0.025
    
    # 결과: 0.025 < 0.25 → Tier 1 ✅
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예제 2: "한국 음식점 월평균 매출은?"
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    question = "한국 음식점 월평균 매출은?"
    
    # 1. 질문 유형: simple_estimate
    # → ('simple_estimate', 0.3)
    
    # 2. 데이터 가용성: 산업 보고서 가능
    # → 0.3
    
    # 3. 변수 개수: 3개 (좌석 × 회전 × 객단가)
    # → (3, 0.6)
    
    # 4. 도메인 특수성: industry
    # → ('industry', 0.5)
    
    # 종합 점수
    total_score = (
        0.3 * 0.30 +   # 0.09
        0.3 * 0.25 +   # 0.075
        0.6 * 0.25 +   # 0.15
        0.5 * 0.20     # 0.10
    ) = 0.415
    
    # 결과: 0.25 < 0.415 < 0.60 → Tier 2 ✅
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예제 3: "한국 B2B SaaS 시장 규모는?"
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    question = "한국 B2B SaaS 시장 규모는?"
    
    # 1. 질문 유형: complex_estimate
    # → ('complex_estimate', 0.7)
    
    # 2. 데이터 가용성: 보고서 있지만 계산 필요
    # → 0.5
    
    # 3. 변수 개수: 5개 이상
    # → (5, 0.6)
    
    # 4. 도메인 특수성: industry
    # → ('industry', 0.5)
    
    # 종합 점수
    total_score = (
        0.7 * 0.30 +   # 0.21
        0.5 * 0.25 +   # 0.125
        0.6 * 0.25 +   # 0.15
        0.5 * 0.20     # 0.10
    ) = 0.585
    
    # 결과: 0.25 < 0.585 < 0.60 → Tier 2 (경계선)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예제 4: "3년 후 AI 시장 Unit Economics는?"
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    question = "3년 후 AI 시장 Unit Economics는?"
    
    # 1. 질문 유형: prediction
    # → ('prediction', 0.9)
    
    # 2. 데이터 가용성: 데이터 없음
    # → 1.0
    
    # 3. 변수 개수: 5개+
    # → (5, 1.0)
    
    # 4. 도메인 특수성: expert
    # → ('expert', 1.0)
    
    # 종합 점수
    total_score = (
        0.9 * 0.30 +   # 0.27
        1.0 * 0.25 +   # 0.25
        1.0 * 0.25 +   # 0.25
        1.0 * 0.20     # 0.20
    ) = 0.97
    
    # 결과: 0.97 >= 0.60 → Tier 3 ✅
    
    return ComplexityResult(
        score=total_score,
        recommended_tier=3,
        strategy="fermi_decomposition",
        signals={
            'question_type': ('prediction', 0.9),
            'data_availability': 1.0,
            'estimated_variables': (5, 1.0),
            'domain_specificity': ('expert', 1.0)
        },
        reasoning=[
            "질문 유형: prediction (점수 0.9)",
            "데이터 가용성: 없음 (점수 1.0)",
            "예상 변수: 5개 (점수 1.0)",
            "도메인 특수성: expert (점수 1.0)",
            "종합 점수: 0.97 → Tier 3 추천 (Fermi Decomposition)"
        ]
    )
```

---

### 2.2 ContextAnalyzer

**Responsibility**: 질문 맥락 파악 (의도, 도메인, 세분화 등)

**Input**:
```python
question: str              # 질문
external_context: Dict     # 외부 맥락 (Fermi 재귀 시 부모 정보)
```

**Output**:
```python
Context:
    intent: str                    # "get_value", "understand_market", etc.
    domain: str                    # "B2B_SaaS", "Consumer", etc.
    granularity: str               # "macro", "segment", "micro"
    spatiotemporal: Dict           # {region, time_period}
    parent_model: Optional[Model]  # Fermi 재귀 시 부모 모형
    variable_role: Optional[str]   # 변수 역할
    constraints: List[Constraint]  # 제약조건
    project_data: Dict             # 프로젝트 데이터
```

**Implementation Strategy**:

```yaml
Hybrid Approach (규칙 + LLM):

1. Intent 추론:
   규칙 (90%):
     - "창업", "고려" → make_decision
     - "분석", "이해" → understand_market
     - "vs", "비교" → compare
     - "예측", "년 후" → prediction
   
   LLM (10%):
     - 모호한 경우 LLM에게 질문
     - Native Mode $0

2. Domain 추론:
   규칙 (95%):
     - "SaaS", "구독" → B2B_SaaS
     - "음식점", "카페" → Food_Service
     - 키워드 매칭
   
   LLM (5%):
     - 새로운 산업/도메인
     - "피자 배달", "유아용 장난감" 등

3. Spatiotemporal 추출:
   규칙 (100%):
     - 정규식: "한국", "2024년", "3년 후"
     - NER (Named Entity Recognition)
   
   LLM: 불필요 (규칙으로 충분)

4. Granularity:
   규칙 (100%):
     - 수식어 개수 카운트
     - 0-1개: macro
     - 2-3개: segment
     - 4개+: micro
   
   LLM: 불필요
```

**Key Methods**:
```python
def _infer_intent(question: str) -> str:
    """
    의도 추론
    
    Strategy:
      1. 키워드 패턴 체크 (규칙)
      2. 모호하면 LLM
    """
    # 규칙 체크
    if any(word in question for word in ['창업', '고려', '시작']):
        return 'make_decision'
    
    if any(word in question for word in ['분석', '이해', '파악']):
        return 'understand_market'
    
    # ... 더 많은 규칙
    
    # 모호함 → LLM
    return _infer_intent_with_llm(question)

def _infer_domain(question: str) -> str:
    """
    도메인 추론
    
    Strategy:
      1. 키워드 매칭 (규칙)
      2. 없으면 LLM
    """
    # 규칙 체크
    domain_keywords = {
        'B2B_SaaS': ['SaaS', '구독', 'B2B', '클라우드'],
        'Food_Service': ['음식점', '카페', '레스토랑'],
        'E-commerce': ['커머스', '쇼핑몰', '온라인몰'],
        # ...
    }
    
    for domain, keywords in domain_keywords.items():
        if any(kw in question for kw in keywords):
            return domain
    
    # 새로운 도메인 → LLM
    return _infer_domain_with_llm(question)

def _extract_spatiotemporal(question: str) -> Dict:
    """
    시공간 추출
    
    Strategy:
      정규식만 사용 (LLM 불필요)
    """
    # 지역 추출
    region_patterns = {
        '한국': r'한국|대한민국|Korea',
        '서울': r'서울',
        '미국': r'미국|US|USA',
        # ...
    }
    
    # 시간 추출
    time_patterns = {
        'future': r'(\d+)년\s*후',
        'year': r'(\d{4})년',
        # ...
    }
    
    return {
        'region': extract_region(question, region_patterns),
        'time_period': extract_time(question, time_patterns)
    }

def _infer_granularity(question: str) -> str:
    """
    세분화 수준
    
    Strategy:
      수식어 개수만 카운트 (LLM 불필요)
    """
    modifiers = extract_modifiers(question)
    count = len(modifiers)
    
    if count <= 1:
        return 'macro'
    elif count <= 3:
        return 'segment'
    else:
        return 'micro'
```

**LLM 사용 비율**:
```yaml
Intent: 10% (대부분 규칙으로 커버)
Domain: 5% (새로운 산업만)
Spatiotemporal: 0% (정규식 충분)
Granularity: 0% (카운트만)

전체: ~5% LLM 사용
     95% 규칙 기반 (빠르고 비용 없음)
```

---

### 2.3 EvidenceCollector

**Responsibility**: 8개 Layer에서 증거 수집

**Input**:
```python
question: str
context: Context
layers: List[str]          # 수집할 Layer 리스트
mode: str = "parallel"     # "parallel" or "sequential"
```

**Output**:
```python
List[Evidence]:
    Evidence:
        success: bool
        value: Optional[float]
        confidence: float          # 0.0 ~ 1.0
        source: str                # Layer 이름
        source_detail: str         # 상세 출처
        reasoning: str             # 근거
        raw_data: Any              # 원본 데이터
        metadata: Dict             # 메타데이터
```

**8 Layers**:
```python
1. project_data      # 프로젝트 데이터
2. llm_direct        # LLM 직접 답변
3. web_search        # 웹 검색
4. law               # 물리/법률 법칙
5. behavioral        # 행동경제학
6. statistical       # 통계 패턴
7. rag_benchmark     # RAG 벤치마크
8. constraint        # 제약조건
```

**Key Features**:
- 병렬 수집 지원 (ThreadPoolExecutor)
- 실패 허용 (일부 Layer 실패해도 계속)
- 타임아웃 설정 (Layer별)

---

### 2.4 JudgmentSynthesizer

**Responsibility**: 여러 증거를 종합하여 최종 판단

**Input**:
```python
evidence_list: List[Evidence]
context: Context
```

**Output**:
```python
JudgmentResult:
    value: float                   # 최종 값
    confidence: float              # 신뢰도 (0.0 ~ 1.0)
    uncertainty: float             # 불확실성 (±%)
    strategy: str                  # 사용한 종합 전략
    all_evidence: List[Dict]       # 평가된 모든 증거
    reasoning: str                 # 판단 근거
    value_range: Optional[Tuple]   # 범위 (전략이 "range"일 때)
```

**Synthesis Strategies**:
```python
1. single_best:
   - 조건: 최고 가중치 ≥ 0.9 && 다른 증거와 차이 ≥ 0.3
   - 방법: 가장 좋은 증거 하나만 사용

2. weighted_average:
   - 조건: 여러 증거가 비슷한 가중치
   - 방법: 가중 평균

3. conservative:
   - 조건: context.intent == "make_decision"
   - 방법: 보수적 하한

4. range:
   - 조건: 증거들이 크게 다름
   - 방법: 범위 제시 (min ~ max)
```

**Evidence Evaluation**:
```python
EvaluationScore:
    relevance: float      # 맥락 적합도 (0.0 ~ 1.0)
    reliability: float    # 신뢰성 (0.0 ~ 1.0)
    recency: float        # 최신성 (0.0 ~ 1.0)
    overall: float        # 종합 가중치
    
overall = relevance * 0.5 + reliability * 0.3 + recency * 0.2
```

---

## 🔄 3. Tier Specifications

### 3.1 Tier 1: Fast Path

**Target**: 90% of cases
**Goal**: 확실한 답이 있을 때 즉시 리턴

**Flow**:
```
1. Check project_data (confidence ≥ 0.95)
   ↓ not found
2. Check physical/legal laws (confidence = 1.0)
   ↓ not applicable
3. Check simple factual LLM (confidence ≥ 0.9)
   ↓ not simple or low confidence
4. Return None → Go to Tier 2
```

**Performance**:
- Time: <1 second
- Cost: $0 ~ $0.001
- Confidence: ≥ 0.9

---

### 3.2 Tier 2: Judgment Path

**Target**: 8% of cases
**Goal**: 중간 복잡도, 여러 증거 종합

**Flow**:
```
1. ContextAnalyzer.analyze()
   ↓
2. Select relevant layers (3-5 layers)
   ↓
3. EvidenceCollector.collect(parallel=True)
   ↓
4. JudgmentSynthesizer.synthesize()
   ↓
5. If confidence ≥ 0.6: Return
   Else: Go to Tier 3
```

**Performance**:
- Time: 2-5 seconds
- Cost: $0.01 ~ $0.05
- Confidence: 0.6 ~ 0.9

---

### 3.3 Tier 3: Fermi Recursion

**Target**: 2% of cases
**Goal**: 매우 복잡, Decomposition 필요

**Flow**:
```
1. Check depth limit (max 4)
   ↓
2. Generate Fermi model (LLM)
   ↓
3. For each variable:
      - Create child context
      - Recursive call: estimate(variable, child_context, depth+1)
      - Result goes through Tier 1-2-3 again
   ↓
4. Calculate final value from model
   ↓
5. Propagate uncertainty
   ↓
6. Return result
```

**Recursion Escape**:
```python
if depth >= MAX_DEPTH:
    # Force judgment
    result = tier2_judgment_path(question, context)
    if result:
        return result
    else:
        # Last resort: constraint-based range
        return estimate_by_constraints(question, context)
```

**Performance**:
- Time: 10-30 seconds
- Cost: $0.1 ~ $1
- Confidence: 0.5 ~ 0.8

---

## 📊 4. Data Models

### 4.1 Core Data Classes

**ComplexityResult**:
```python
@dataclass
class ComplexityResult:
    """복잡도 분석 결과"""
    score: float                    # 0.0 ~ 1.0
    recommended_tier: int           # 1, 2, 3
    strategy: str                   # "fast_path" | "judgment" | "fermi"
    
    signals: Dict[str, Any]         # 판단 근거
    # {
    #   'question_type': ('simple_estimate', 0.3),
    #   'data_availability': 0.4,
    #   'estimated_variables': (3, 0.6),
    #   'domain_specificity': 0.5
    # }
    
    reasoning: List[str]            # 추론 과정
    # [
    #   "질문 유형: simple_estimate (점수 0.3)",
    #   "데이터 가용성: 중간 (점수 0.4)",
    #   "예상 변수: 3개 (점수 0.6)",
    #   "종합 점수: 0.45 → Tier 2 추천"
    # ]
    
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Context**:
```python
@dataclass
class Context:
    """질문 맥락"""
    intent: str                     # "get_value" | "understand_market" | "make_decision" | "compare" | "predict"
    domain: str                     # "B2B_SaaS" | "Consumer" | "FinTech" | "HealthTech" | "General"
    granularity: str                # "macro" | "segment" | "micro"
    
    spatiotemporal: Dict[str, str]  # {region: "한국", time_period: "2024"}
    
    # Fermi 재귀 관련
    parent_model: Optional['FermiModel'] = None
    variable_role: Optional[str] = None      # "ARPU", "customer_count" etc.
    
    # 제약조건
    constraints: List['Constraint'] = field(default_factory=list)
    
    # 프로젝트 데이터
    project_data: Dict[str, Any] = field(default_factory=dict)
    
    # 메타데이터
    depth: int = 0                  # 재귀 깊이
    parent_question: Optional[str] = None
```

**Evidence**:
```python
@dataclass
class Evidence:
    """증거 (하나의 Layer 결과)"""
    success: bool
    
    # 값
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None
    
    # 신뢰도
    confidence: float = 0.0         # Layer 자체 신뢰도
    
    # 출처
    source: str = ""                # "project_data" | "llm_direct" | "web_search" | ...
    source_detail: str = ""         # 상세 출처 ("통계청 2023년 데이터")
    
    # 근거
    reasoning: str = ""
    raw_data: Any = None            # 원본 데이터
    
    # 메타데이터
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

**EvaluationScore**:
```python
@dataclass
class EvaluationScore:
    """증거 평가 점수"""
    relevance: float                # 맥락 적합도 (0.0 ~ 1.0)
    reliability: float              # 신뢰성 (0.0 ~ 1.0)
    recency: float                  # 최신성 (0.0 ~ 1.0)
    overall: float                  # 종합 가중치
    
    details: Dict[str, Any] = field(default_factory=dict)
    # {
    #   'relevance_factors': {
    #       'region_match': 0.7,
    #       'time_match': 1.0,
    #       'granularity_match': 0.9
    #   },
    #   'reliability_factors': {
    #       'source_base': 0.7,
    #       'confidence_adjusted': 0.49
    #   }
    # }
```

**JudgmentResult**:
```python
@dataclass
class JudgmentResult:
    """판단 결과"""
    value: float                    # 최종 판단 값
    confidence: float               # 신뢰도 (0.0 ~ 1.0)
    uncertainty: float              # 불확실성 (±%)
    
    strategy: str                   # "single_best" | "weighted_average" | "conservative" | "range"
    
    all_evidence: List[Dict]        # 평가된 모든 증거
    # [
    #   {
    #       'evidence': Evidence(...),
    #       'evaluation': EvaluationScore(...),
    #       'weight': 0.8
    #   },
    #   ...
    # ]
    
    reasoning: str                  # 판단 근거
    value_range: Optional[Tuple[float, float]] = None  # 전략이 "range"일 때
    
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**EstimationResult** (최종 리턴):
```python
@dataclass
class EstimationResult:
    """최종 추정 결과"""
    question: str
    
    # 값
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None
    
    # 메타 정보
    tier: int = 0                   # 1, 2, 3
    source: str = ""                # "fast_path" | "judgment" | "fermi"
    confidence: float = 0.0
    uncertainty: float = 0.0
    
    # 추론 과정
    reasoning: str = ""
    logic_steps: List[str] = field(default_factory=list)
    
    # Tier 2 전용
    judgment_result: Optional[JudgmentResult] = None
    
    # Tier 3 전용
    fermi_model: Optional['FermiModel'] = None
    variable_results: Dict[str, 'EstimationResult'] = field(default_factory=dict)
    
    # 메타데이터
    complexity: Optional[ComplexityResult] = None
    context: Optional[Context] = None
    execution_time: float = 0.0     # seconds
    cost: float = 0.0               # dollars
    
    def is_successful(self) -> bool:
        return self.value is not None or self.value_range is not None
    
    def get_display_value(self) -> str:
        if self.value is not None:
            return f"{self.value:,.0f}"
        elif self.value_range:
            return f"{self.value_range[0]:,.0f} ~ {self.value_range[1]:,.0f}"
        return "추정 불가"
```

### 4.2 Constraint Models

```python
@dataclass
class Constraint:
    """제약조건"""
    type: str                       # "physical" | "legal" | "logical" | "temporal"
    description: str
    
    # 수치 제약
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    # 관계 제약
    relationship: Optional[str] = None  # "X < Y", "X + Y = Z"
    
    # 메타
    source: str = ""                # 제약의 출처
    confidence: float = 1.0         # 제약의 확실성
```

### 4.3 Configuration Models

```python
@dataclass
class Tier1Config:
    """Tier 1 설정"""
    enabled: bool = True
    
    min_confidence_project_data: float = 0.95
    min_confidence_law: float = 1.0
    min_confidence_llm_factual: float = 0.9
    
    timeout_seconds: float = 1.0

@dataclass
class Tier2Config:
    """Tier 2 설정"""
    enabled: bool = True
    
    min_confidence: float = 0.6
    min_evidence_count: int = 2
    max_evidence_count: int = 5
    
    collection_mode: str = "parallel"  # "parallel" | "sequential"
    timeout_seconds: float = 5.0
    
    synthesis_strategy: str = "auto"   # "auto" | "single_best" | "weighted_average" | ...

@dataclass
class Tier3Config:
    """Tier 3 설정"""
    enabled: bool = True
    
    max_depth: int = 4
    timeout_seconds: float = 30.0
    
    force_judgment_at_max_depth: bool = True

@dataclass
class GuestimationConfig:
    """전체 시스템 설정"""
    tier1: Tier1Config = field(default_factory=Tier1Config)
    tier2: Tier2Config = field(default_factory=Tier2Config)
    tier3: Tier3Config = field(default_factory=Tier3Config)
    
    # LLM 모드 (전역)
    llm_mode: str = "native"        # "native" | "external" | "skip"
    
    # 웹 검색 모드 (Guestimation 전용)
    web_search_mode: str = "native" # "native" | "external" | "skip"
    
    # 인터랙티브 모드
    interactive_mode: bool = False
    
    # 로깅
    verbose: bool = False
    log_all_evidence: bool = True
```

---

## 🔌 5. API Definitions

### 5.1 Main Entry Point

```python
def estimate(
    question: str,
    context: Optional[Union[Dict, Context]] = None,
    depth: int = 0,
    config: Optional[GuestimationConfig] = None
) -> EstimationResult:
    """
    메인 추정 함수
    
    Args:
        question: 추정 질문
            예: "한국 음식점 월평균 매출은?"
        
        context: 맥락 정보 (optional)
            - Dict: 자동으로 Context 객체로 변환
            - Context: 직접 제공
            - None: 빈 Context 생성
        
        depth: 재귀 깊이 (내부 사용, 일반 사용자는 0)
        
        config: 설정 오버라이드 (optional)
            - None: 전역 설정 사용 (multilayer_config.yaml + .env)
    
    Returns:
        EstimationResult: 추정 결과
    
    Example:
        >>> result = estimate("한국 음식점 월평균 매출은?")
        >>> print(f"값: {result.value:,.0f}원")
        >>> print(f"신뢰도: {result.confidence:.1%}")
        >>> print(f"Tier: {result.tier}")
        
        값: 2,700,000원
        신뢰도: 75.0%
        Tier: 2
    """
```

### 5.2 ComplexityAnalyzer API

```python
class ComplexityAnalyzer:
    def analyze(
        self, 
        question: str, 
        context: Optional[Context] = None
    ) -> ComplexityResult:
        """
        복잡도 분석
        
        Args:
            question: 질문
            context: 맥락 (optional)
        
        Returns:
            ComplexityResult
        """
    
    # Private methods (구현 참조용)
    def _classify_question_type(self, question: str) -> str:
        """질문 유형 분류"""
    
    def _check_data_availability(
        self, 
        question: str, 
        context: Optional[Context]
    ) -> float:
        """데이터 가용성 체크"""
    
    def _estimate_variable_count(self, question: str) -> int:
        """예상 변수 개수 추정"""
    
    def _assess_domain_specificity(self, question: str) -> float:
        """도메인 특수성 평가"""
```

### 5.3 ContextAnalyzer API

```python
class ContextAnalyzer:
    def analyze(
        self, 
        question: str, 
        external_context: Optional[Dict] = None
    ) -> Context:
        """
        맥락 분석
        
        Args:
            question: 질문
            external_context: 외부 맥락
                - project_data: Dict
                - parent_model: FermiModel
                - constraints: List[Constraint]
        
        Returns:
            Context
        """
    
    # Private methods
    def _parse_question(self, question: str) -> Dict:
        """질문 파싱"""
    
    def _infer_intent(self, question: str, parsed: Dict) -> str:
        """의도 추론"""
    
    def _infer_domain(self, question: str, parsed: Dict) -> str:
        """도메인 추론"""
    
    def _infer_granularity(self, question: str) -> str:
        """세분화 수준 추론"""
    
    def _extract_spatiotemporal(self, question: str) -> Dict:
        """시공간 맥락 추출"""
```

### 5.4 EvidenceCollector API

```python
class EvidenceCollector:
    def collect(
        self,
        question: str,
        context: Context,
        layers: Optional[List[str]] = None,
        mode: str = "parallel"
    ) -> List[Evidence]:
        """
        증거 수집
        
        Args:
            question: 질문
            context: 맥락
            layers: 수집할 Layer 리스트
                - None: 맥락에 따라 자동 선택
                - List: 지정된 Layer만
            mode: "parallel" or "sequential"
        
        Returns:
            List[Evidence]: 성공한 증거들
        """
    
    def select_relevant_layers(
        self,
        question: str,
        context: Context
    ) -> List[str]:
        """
        관련 Layer 자동 선택
        
        Returns:
            List[str]: ["llm_direct", "web_search", "rag_benchmark"]
        """
    
    # Layer methods
    def try_layer(
        self,
        layer_name: str,
        question: str,
        context: Context
    ) -> Evidence:
        """개별 Layer 시도"""
```

### 5.5 JudgmentSynthesizer API

```python
class JudgmentSynthesizer:
    def synthesize(
        self,
        evidence_list: List[Evidence],
        context: Context,
        strategy: str = "auto"
    ) -> JudgmentResult:
        """
        증거 종합 판단
        
        Args:
            evidence_list: 증거 리스트
            context: 맥락
            strategy: 종합 전략
                - "auto": 자동 선택
                - "single_best": 최고 증거만
                - "weighted_average": 가중 평균
                - "conservative": 보수적 하한
                - "range": 범위 제시
        
        Returns:
            JudgmentResult
        """
    
    def evaluate_evidence(
        self,
        evidence: Evidence,
        context: Context
    ) -> EvaluationScore:
        """개별 증거 평가"""
    
    def select_synthesis_strategy(
        self,
        evaluated_evidence: List[Dict],
        context: Context
    ) -> str:
        """종합 전략 자동 선택"""
```

### 5.6 Tier Functions

```python
def tier1_fast_path(
    question: str,
    context: Context,
    config: Tier1Config
) -> Optional[EstimationResult]:
    """Tier 1 실행"""

def tier2_judgment_path(
    question: str,
    context: Context,
    config: Tier2Config
) -> Optional[EstimationResult]:
    """Tier 2 실행"""

def tier3_fermi_recursion(
    question: str,
    context: Context,
    depth: int,
    config: Tier3Config
) -> EstimationResult:
    """Tier 3 실행"""
```

---

## 🛠️ 6. Implementation Guide

### 6.1 File Structure

```
umis_rag/
├── utils/
│   ├── guestimation_v3/              # 신규 폴더
│   │   ├── __init__.py
│   │   ├── core.py                   # 메인 Entry Point
│   │   ├── complexity.py             # ComplexityAnalyzer
│   │   ├── context.py                # ContextAnalyzer
│   │   ├── evidence.py               # EvidenceCollector
│   │   ├── judgment.py               # JudgmentSynthesizer
│   │   ├── tiers.py                  # Tier 1-2-3 Functions
│   │   ├── models.py                 # Data Models (All @dataclass)
│   │   ├── config.py                 # Configuration
│   │   └── layers/                   # Layer 구현 (재사용)
│   │       ├── __init__.py
│   │       ├── project_data.py
│   │       ├── llm_direct.py
│   │       ├── web_search.py
│   │       ├── law.py
│   │       ├── behavioral.py
│   │       ├── statistical.py
│   │       ├── rag_benchmark.py
│   │       └── constraint.py
│   │
│   ├── fermi_model_search.py         # 기존 (일부 수정)
│   ├── guestimation.py               # v2.1 (재사용 가능)
│   └── multilayer_guestimation.py    # v2.1 (Deprecated 예정)
│
config/
├── guestimation_v3_config.yaml       # 신규 설정 파일
└── multilayer_config.yaml            # v2.1 (호환 유지)
```

### 6.2 Implementation Phases

**Phase 1: Data Models & Config (Day 1)**

```yaml
파일: umis_rag/utils/guestimation_v3/models.py
작업:
  - ComplexityResult
  - Context
  - Evidence
  - EvaluationScore
  - JudgmentResult
  - EstimationResult
  - Constraint
  - All Config classes

예상: 300줄
```

**Phase 2: Core Components (Day 1-2)**

```yaml
파일: umis_rag/utils/guestimation_v3/complexity.py
클래스: ComplexityAnalyzer
메서드:
  - analyze()
  - _classify_question_type()
  - _check_data_availability()
  - _estimate_variable_count()
  - _assess_domain_specificity()
예상: 250줄

파일: umis_rag/utils/guestimation_v3/context.py
클래스: ContextAnalyzer
메서드:
  - analyze()
  - _parse_question()
  - _infer_intent()
  - _infer_domain()
  - _infer_granularity()
  - _extract_spatiotemporal()
  - _extract_parent_info()
예상: 300줄
```

**Phase 3: Evidence & Judgment (Day 2-3)**

```yaml
파일: umis_rag/utils/guestimation_v3/evidence.py
클래스: EvidenceCollector
메서드:
  - collect()
  - select_relevant_layers()
  - try_layer()
  - _collect_parallel()
  - _collect_sequential()
  - 8개 Layer 메서드 (기존 재사용)
예상: 400줄 (재사용 50%)

파일: umis_rag/utils/guestimation_v3/judgment.py
클래스: JudgmentSynthesizer
메서드:
  - synthesize()
  - evaluate_evidence()
  - select_synthesis_strategy()
  - _score_relevance()
  - _score_reliability()
  - _score_recency()
  - _calculate_uncertainty()
  - 4개 전략 메서드
예상: 350줄
```

**Phase 4: Tier Functions (Day 3-4)**

```yaml
파일: umis_rag/utils/guestimation_v3/tiers.py
함수:
  - tier1_fast_path()
  - tier2_judgment_path()
  - tier3_fermi_recursion()
예상: 300줄
```

**Phase 5: Main Entry & Integration (Day 4)**

```yaml
파일: umis_rag/utils/guestimation_v3/core.py
함수:
  - estimate() (메인 Entry Point)
클래스:
  - GuestimationSystemV3
예상: 200줄
```

**Phase 6: Fermi Integration (Day 5)**

```yaml
파일: umis_rag/utils/fermi_model_search.py (수정)
수정 내용:
  - fermi_estimate() → guestimation_v3.estimate() 호출
  - 변수 추정 로직 교체
  - 재귀 탈출 조건 개선
예상: 50줄 수정
```

**Phase 7: Testing & Debugging (Day 5-6)**

```yaml
파일: scripts/test_guestimation_v3.py
테스트:
  - Tier 1-2-3 각각
  - End-to-End
  - Fermi 통합
예상: 400줄
```

### 6.3 Code Reuse Strategy

**재사용 가능 (from v2.1)**:

```python
# umis_rag/utils/multilayer_guestimation.py에서 재사용

# Layer 구현들
def _try_project_data(question, context):
    # 200줄 → 그대로 재사용

def _try_law_based(question, context):
    # 150줄 → 그대로 재사용

def _try_behavioral(question, context, target_profile):
    # 180줄 → 그대로 재사용

def _try_statistical(question):
    # 120줄 → 그대로 재사용

def _try_constraint_boundary(question):
    # 100줄 → 그대로 재사용

# 총 750줄 재사용 가능!
```

**재작성 필요**:

```python
# Sequential Fallback 로직 → 완전 재작성
def estimate(question, ...):
    # v2.1: Layer 1 → 성공 시 즉시 리턴
    # v3.0: Complexity 분석 → Tier 선택 → ...
    
# 약 500줄 재작성
```

### 6.4 Implementation Priorities

**P0 (Must Have - MVP)**:
```yaml
1. ComplexityAnalyzer (기본 알고리즘)
2. ContextAnalyzer (기본 맥락)
3. EvidenceCollector (3개 Layer만: project_data, llm, law)
4. JudgmentSynthesizer (weighted_average 전략만)
5. Tier 1-2 구현
6. Main Entry Point
```

**P1 (Should Have - v3.0)**:
```yaml
1. 모든 Layer 구현 (8개)
2. 모든 종합 전략 (4개)
3. Tier 3 (Fermi 통합)
4. 고급 맥락 분석
```

**P2 (Nice to Have - v3.1+)**:
```yaml
1. 성능 최적화
2. 캐싱
3. 웹 UI
4. 학습 기능
```

### 6.5 Key Implementation Notes

**Note 1: LLM 호출 최소화**

```python
# 복잡도 분석에서 LLM 사용 최소화
class ComplexityAnalyzer:
    def analyze(self, question, context):
        # ❌ LLM에 "이 질문은 얼마나 복잡한가?" 물어보기
        # ✅ 규칙 기반 + 휴리스틱
        
        # 키워드 매칭
        if any(kw in question for kw in ['인구', '면적', '시간']):
            return simple
        
        # 변수 개수 추정 (LLM 없이)
        estimated_vars = question.count('×') + question.count('*')
        
        # ...
```

**Note 2: 병렬 처리 주의**

```python
# ThreadPoolExecutor 사용 시 타임아웃 필수
def _collect_parallel(self, question, context, layers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(
                self._try_layer_with_timeout,  # 타임아웃 래퍼!
                layer, question, context
            ): layer
            for layer in layers
        }
        
        # as_completed로 빠른 것부터 수집
        for future in concurrent.futures.as_completed(futures, timeout=10):
            # ...
```

**Note 3: 에러 핸들링**

```python
# 개별 Layer 실패는 허용
def try_layer(self, layer_name, question, context):
    try:
        return self._layer_methods[layer_name](question, context)
    except Exception as e:
        logger.warning(f"Layer {layer_name} failed: {e}")
        return Evidence(success=False, error=str(e))

# 하지만 모든 Layer 실패는 에러
def collect(self, ...):
    evidence_list = [...]
    
    if not evidence_list:
        raise NoEvidenceFoundError("모든 Layer 실패")
```

---

## ✅ 7. Testing Strategy

### 7.1 Unit Tests

**ComplexityAnalyzer Tests**:

```python
# scripts/test_complexity_analyzer.py

def test_simple_question():
    """간단한 사실 질문 → Tier 1"""
    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze("한국 인구는?")
    
    assert result.recommended_tier == 1
    assert result.strategy == "fast_path"
    assert result.score < 0.25

def test_moderate_question():
    """중간 복잡도 → Tier 2"""
    result = analyzer.analyze("한국 음식점 월평균 매출은?")
    
    assert result.recommended_tier == 2
    assert result.strategy == "judgment_synthesis"
    assert 0.25 <= result.score < 0.60

def test_complex_question():
    """복잡한 질문 → Tier 3"""
    result = analyzer.analyze("한국 클라우드 SaaS 시장 규모는?")
    
    assert result.recommended_tier == 3
    assert result.strategy == "fermi_decomposition"
    assert result.score >= 0.60
```

**ContextAnalyzer Tests**:

```python
def test_intent_inference():
    """의도 추론"""
    analyzer = ContextAnalyzer()
    
    # get_value
    context = analyzer.analyze("한국 인구는?")
    assert context.intent == "get_value"
    
    # make_decision
    context = analyzer.analyze("음식점 창업하려는데 예상 매출은?")
    assert context.intent == "make_decision"

def test_domain_inference():
    """도메인 추론"""
    context = analyzer.analyze("SaaS Churn Rate는?")
    assert context.domain == "B2B_SaaS"
    
    context = analyzer.analyze("커피숍 매출은?")
    assert context.domain == "Consumer"
```

**EvidenceCollector Tests**:

```python
def test_project_data_layer():
    """Layer 1: 프로젝트 데이터"""
    collector = EvidenceCollector()
    context = Context(
        project_data={'customer_count': 50000}
    )
    
    evidence = collector.try_layer("project_data", "고객수는?", context)
    
    assert evidence.success == True
    assert evidence.value == 50000
    assert evidence.confidence == 1.0

def test_parallel_collection():
    """병렬 수집"""
    evidence_list = collector.collect(
        question="한국 인구는?",
        context=Context(),
        layers=["llm_direct", "web_search"],
        mode="parallel"
    )
    
    assert len(evidence_list) >= 1
    # 병렬 실행 시간 < 순차 실행 시간
```

**JudgmentSynthesizer Tests**:

```python
def test_single_best_strategy():
    """단일 최고 증거 전략"""
    synthesizer = JudgmentSynthesizer()
    
    evidence_list = [
        Evidence(success=True, value=100, confidence=0.95),  # 최고!
        Evidence(success=True, value=120, confidence=0.6),
    ]
    
    result = synthesizer.synthesize(evidence_list, Context())
    
    assert result.strategy == "single_best"
    assert result.value == 100

def test_weighted_average_strategy():
    """가중 평균 전략"""
    evidence_list = [
        Evidence(success=True, value=100, confidence=0.7),
        Evidence(success=True, value=110, confidence=0.8),
        Evidence(success=True, value=90, confidence=0.6),
    ]
    
    result = synthesizer.synthesize(evidence_list, Context())
    
    assert result.strategy == "weighted_average"
    assert 95 <= result.value <= 110
```

### 7.2 Integration Tests

**Tier Tests**:

```python
# scripts/test_tiers.py

def test_tier1_fast_path():
    """Tier 1: Fast Path"""
    result = tier1_fast_path(
        question="하루는 몇 시간?",
        context=Context(),
        config=Tier1Config()
    )
    
    assert result is not None
    assert result.value == 24
    assert result.tier == 1
    assert result.source == "physical_law"

def test_tier2_judgment():
    """Tier 2: Judgment"""
    result = tier2_judgment_path(
        question="한국 음식점 월매출은?",
        context=Context(),
        config=Tier2Config()
    )
    
    assert result is not None
    assert result.tier == 2
    assert result.judgment_result is not None
    assert len(result.judgment_result.all_evidence) >= 2

def test_tier3_fermi():
    """Tier 3: Fermi"""
    result = tier3_fermi_recursion(
        question="한국 SaaS 시장 규모는?",
        context=Context(),
        depth=0,
        config=Tier3Config()
    )
    
    assert result.tier == 3
    assert result.fermi_model is not None
    assert len(result.variable_results) >= 2
```

### 7.3 End-to-End Tests

```python
# scripts/test_e2e_guestimation_v3.py

test_cases = [
    {
        'name': "간단한 사실",
        'question': "한국 인구는?",
        'expected_tier': 1,
        'expected_confidence': '>0.9'
    },
    {
        'name': "중간 복잡도",
        'question': "한국 음식점 월매출은?",
        'expected_tier': 2,
        'expected_confidence': '>0.6'
    },
    {
        'name': "Fermi 필요",
        'question': "한국 클라우드 SaaS 시장은?",
        'expected_tier': 3,
        'expected_confidence': '>0.5',
        'expected_model': True
    },
    {
        'name': "의사결정 맥락",
        'question': "음식점 창업 예상 매출은?",
        'expected_tier': 2,
        'expected_strategy': 'conservative'
    }
]

def test_all_cases():
    for case in test_cases:
        result = estimate(case['question'])
        
        assert result.tier == case['expected_tier']
        # ...
```

### 7.4 Performance Tests

```python
# scripts/test_performance_v3.py

def test_tier1_speed():
    """Tier 1은 1초 이내"""
    start = time.time()
    result = estimate("한국 인구는?")
    elapsed = time.time() - start
    
    assert elapsed < 1.0
    assert result.tier == 1

def test_tier2_speed():
    """Tier 2는 5초 이내"""
    start = time.time()
    result = estimate("음식점 월매출은?")
    elapsed = time.time() - start
    
    assert elapsed < 5.0
    assert result.tier == 2

def test_cost():
    """비용 추적"""
    result = estimate("SaaS 시장은?")
    
    # v3.0은 v2.1보다 비용 낮아야 함 (선택적 수집)
    assert result.cost < 0.1  # $0.1 이하
```

### 7.5 Regression Tests

```python
# v2.1 기존 동작 보장

def test_backward_compatibility():
    """기존 API 호환성"""
    # v2.1 방식도 여전히 작동
    from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation
    
    old_estimator = MultiLayerGuestimation()
    old_result = old_estimator.estimate("한국 인구는?")
    
    # v3.0
    new_result = estimate("한국 인구는?")
    
    # 결과 유사해야 함 (±10%)
    assert abs(old_result.value - new_result.value) / old_result.value < 0.1
```

---

## 🔄 8. Migration Plan

### 8.1 Migration Strategy

**전략: Incremental Migration (점진적 마이그레이션)**

```yaml
원칙:
  1. v2.1과 v3.0 병렬 운영 (1개월)
  2. 기존 API 호환성 유지
  3. Feature Flag로 제어
  4. 단계적 전환
```

### 8.2 Migration Phases

**Phase 1: v3.0 구현 (Week 1-2)**

```yaml
상태: v2.1 Active, v3.0 Development
작업:
  - v3.0 코드 구현
  - 단위 테스트
  - 통합 테스트
  - 문서 작성

브랜치: feature/guestimation-v3
```

**Phase 2: A/B 테스트 (Week 3)**

```yaml
상태: v2.1 Active (90%), v3.0 Beta (10%)

Feature Flag:
  # config/guestimation_v3_config.yaml
  enabled: false  # 기본값: v2.1 사용
  
  rollout:
    percentage: 10  # 10%만 v3.0
    whitelist:      # 특정 쿼리만 v3.0
      - "한국 인구는?"
      - "음식점 매출은?"

작업:
  - 10% 트래픽 v3.0 테스트
  - 성능 모니터링
  - 결과 비교
  - 버그 수정
```

**Phase 3: 점진적 확대 (Week 4)**

```yaml
상태: v2.1 Active (50%), v3.0 Beta (50%)

Feature Flag:
  enabled: true
  rollout:
    percentage: 50

작업:
  - 50% 트래픽 v3.0
  - 성능 확인
  - 비용 확인
  - 피드백 수집
```

**Phase 4: 완전 전환 (Week 5)**

```yaml
상태: v2.1 Deprecated, v3.0 Active (100%)

Feature Flag:
  enabled: true
  rollout:
    percentage: 100

작업:
  - 100% 트래픽 v3.0
  - v2.1 Deprecation 공지
  - 문서 업데이트
```

**Phase 5: v2.1 제거 (Week 6+)**

```yaml
상태: v3.0 Only

작업:
  - multilayer_guestimation.py → archive/
  - v2.1 관련 코드 제거
  - 테스트 정리
  - 최종 문서화
```

### 8.3 API Compatibility

**현재 API (v2.1)**:

```python
from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation

estimator = MultiLayerGuestimation(project_context={...})
result = estimator.estimate(
    question="...",
    target_profile=...,
    rag_candidates=...
)
```

**v3.0 API (하위 호환)**:

```python
# Option 1: 새로운 방식 (권장)
from umis_rag.utils.guestimation_v3 import estimate

result = estimate(
    question="...",
    context={
        'project_data': {...},
        'target_profile': ...,
    }
)

# Option 2: 기존 방식 (호환)
from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation

estimator = MultiLayerGuestimation()  # 내부적으로 v3.0 호출!
result = estimator.estimate("...")    # 동일한 인터페이스
```

### 8.4 Feature Flag Implementation

```python
# umis_rag/utils/guestimation_v3/config.py

@dataclass
class FeatureFlags:
    """Feature Flags"""
    v3_enabled: bool = False
    rollout_percentage: int = 0
    whitelist_questions: List[str] = field(default_factory=list)
    
    def should_use_v3(self, question: str) -> bool:
        """v3.0 사용 여부 판단"""
        if not self.v3_enabled:
            return False
        
        # Whitelist 체크
        if question in self.whitelist_questions:
            return True
        
        # 확률적 롤아웃
        import random
        return random.randint(1, 100) <= self.rollout_percentage

# 사용
def estimate_with_version_control(question, context):
    flags = load_feature_flags()
    
    if flags.should_use_v3(question):
        return estimate_v3(question, context)
    else:
        return estimate_v2(question, context)
```

### 8.5 Rollback Plan

```yaml
문제 발생 시:

Step 1: Feature Flag 즉시 비활성
  config/guestimation_v3_config.yaml:
    enabled: false
  
  효과: v2.1로 즉시 전환 (30초)

Step 2: 긴급 패치
  - 버그 수정
  - 핫픽스 배포
  
Step 3: 재시작
  - 10%부터 다시 시작
  - 검증 강화

조건:
  - 에러율 >5% → 즉시 롤백
  - 비용 >2배 → 롤백 고려
  - 성능 >2배 느림 → 롤백 고려
```

### 8.6 Monitoring & Metrics

```yaml
모니터링 지표:

성능:
  - 평균 응답 시간 (Tier별)
  - P95 응답 시간
  - 타임아웃 비율

품질:
  - 에러율
  - 신뢰도 분포
  - Tier 분포 (1:2:3 비율)

비용:
  - API 호출 수 (LLM, 웹)
  - 평균 비용/쿼리
  - 총 비용

정확도:
  - v2.1 vs v3.0 결과 차이
  - 사용자 피드백
  - 수동 검증 샘플
```

---

## 📚 9. References & Appendix

### 9.1 Related Documents

- `SESSION_SUMMARY_20251106_FERMI_COMPLETE.md` - v2.1 개발 기록
- `GUESTIMATION_FLOWCHART.md` - v2.1 플로우차트
- `MULTILAYER_IMPLEMENTATION_STATUS.md` - v2.1 구현 상태
- `FERMI_IMPLEMENTATION_STATUS.md` - Fermi 구현 상태

### 9.2 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-06 | Sequential Fallback → Context-Aware Judgment | v2.1은 "판단" 없음, 정보 종합 필요 |
| 2025-11-06 | 3-Tier Architecture | 확실할 땐 빠르게 (90%), 복잡할 땐 정확하게 |
| 2025-11-06 | 병렬 증거 수집 (Tier 2) | 모든 정보 활용, 시간 단축 |
| 2025-11-06 | Incremental Migration | 리스크 최소화, 검증 가능 |

### 9.3 Open Questions

```yaml
Q1: Tier 2에서 Layer 자동 선택 알고리즘?
  현재: 맥락 기반 휴리스틱
  개선: LLM이 선택? 학습 기반?

Q2: 종합 전략 자동 선택 알고리즘?
  현재: 규칙 기반
  개선: 강화학습?

Q3: 복잡도 점수 임계값 (0.25, 0.60)?
  현재: 경험적 설정
  개선: 데이터 기반 최적화?

Q4: Fermi 재귀와 Tier 시스템의 완전 통합?
  현재: Tier 3에서 Fermi 호출
  개선: 더 긴밀한 통합?
```

### 9.4 Future Work (v3.1+)

```yaml
캐싱:
  - 자주 묻는 질문 캐싱
  - 증거 캐싱 (TTL)
  - 비용 50% 절감 목표

학습:
  - 사용자 피드백 수집
  - 복잡도 분석 학습
  - 종합 전략 학습

UI:
  - 웹 인터페이스
  - 실시간 추론 과정 시각화
  - 증거 트리 표시

고급 기능:
  - 민감도 분석
  - What-if 시나리오
  - 자동 검증
```

---

## 📝 Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-06 | Initial draft - Complete specification | UMIS Dev Team |

---

**Document Complete**: All Sections (1-9) ✅  
**Status**: Ready for Review & Implementation  
**Next Step**: Begin Phase 1 Implementation

