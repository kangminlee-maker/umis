# 11개 Source 통합 분석 (v7.7.0 → v7.8.0)

**날짜**: 2025-11-12  
**목적**: LLM + Web Source 통합 가능성 검토  
**결론**: 통합 권장 ✅

---

## 📋 현재 11개 Source 구조

### **Physical Constraints (3개)** - 절대 한계

| # | Source | 역할 | 구현 상태 | 정의 명확도 |
|---|--------|------|----------|------------|
| 1 | `SpacetimeConstraintSource` | 시공간 제약 (거리/속도/시간) | 🟡 Partial | ⚠️ 샘플만 |
| 2 | `ConservationLawSource` | 보존 법칙 (전체=부분합) | 🟡 Partial | ⚠️ 샘플만 |
| 3 | `MathematicalDefinitionSource` | 수학 정의 (비율, 백분율) | 🟡 Partial | ⚠️ 샘플만 |

**문제점**:
- 실제 구현: 샘플 데이터만 (하드코딩)
- TODO 주석 많음
- 실제 활용도: 낮음 (<5% 케이스)

### **Soft Constraints (3개)** - 범위 제시

| # | Source | 역할 | 구현 상태 | 정의 명확도 |
|---|--------|------|----------|------------|
| 4 | `LegalNormSource` | 법률/규범 (최저임금 등) | 🟡 Partial | ✅ 명확 |
| 5 | `StatisticalPatternSource` | 통계 패턴 (분포 정보) | 🟡 Partial | ⚠️ 샘플만 |
| 6 | `BehavioralInsightSource` | 행동경제학 | 🔴 TODO | ❌ 미구현 |

**문제점**:
- LegalNormSource: 하드코딩 (2개만)
- StatisticalPatternSource: 샘플 구현 ("TODO: RAG 검색")
- BehavioralInsightSource: 완전 미구현

### **Value Sources (5개)** - 구체적 값

| # | Source | 역할 | 구현 상태 | 정의 명확도 | 실제 활용 |
|---|--------|------|----------|------------|----------|
| 7 | `DefiniteDataSource` | 프로젝트 확정 데이터 | ✅ 완성 | ✅ 명확 | 높음 (Phase 0) |
| 8 | `LLMEstimationSource` | LLM 직접 추정 | 🔴 스킵 | ⚠️ 애매 | **없음** |
| 9 | `WebSearchSource` | 웹 검색 크롤링 | ✅ 완성 | ✅ 명확 | 중간 (Phase 3) |
| 10 | `RAGBenchmarkSource` | RAG 벤치마크 | ✅ 완성 | ✅ 명확 | 중간 (Phase 3) |
| 11 | `StatisticalValueSource` | 통계 분포값 | ✅ 완성 | ✅ 명확 | 낮음 (최후) |

**핵심 문제**:
- **LLMEstimationSource**: 현재 거의 사용 안 됨 (Native 모드에서 스킵)
- **WebSearchSource**: 복잡한 크롤링 구현했으나 역할은 "가이드라인"

---

## 🎯 통합 제안: LLM + Web → AI Augmented Estimation

### **통합 근거**

1. **역할 중복**
   - LLM: "간단한 사실 질문" → 값 추정
   - Web: "웹 검색" → 숫자 평균 → 가이드라인
   - → 둘 다 "외부에서 값 가져오기"

2. **현재 문제**
   - LLM: Native 모드에서 스킵 (interactive 필요)
   - Web: 크롤링 복잡도 과도

3. **자연스러운 통합**
   - AI에게: "값 추정 + 필요시 웹 검색"
   - Native: instruction 제공
   - External: LLM API 호출

### **통합 후 구조 (10개 Source)**

```python
# Physical (3개) - 변경 없음
1. SpacetimeConstraintSource
2. ConservationLawSource
3. MathematicalDefinitionSource

# Soft (3개) - 변경 없음
4. LegalNormSource
5. StatisticalPatternSource
6. BehavioralInsightSource

# Value (4개) ⭐ 5→4로 통합
7. DefiniteDataSource
8. AIAugmentedEstimationSource  # ⭐ LLM + Web 통합!
9. RAGBenchmarkSource
10. StatisticalValueSource
```

---

## 🔧 구체적 통합 방안

### **신규: AIAugmentedEstimationSource**

```python
# umis_rag/agents/estimator/sources/value.py

class AIAugmentedEstimationSource(ValueSourceBase):
    """
    AI 증강 추정 (v7.8.0)
    
    역할:
    -----
    - LLM에게 값 추정 요청
    - 필요시 웹 검색도 수행하도록 지시
    - Native: instruction 반환
    - External: API 호출
    - confidence 0.60-0.85
    """
    
    def __init__(self, llm_mode: str = "native"):
        self.llm_mode = llm_mode
        
        from umis_rag.core.config import settings
        self.web_search_enabled = settings.web_search_enabled
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """AI 증강 추정"""
        
        if self.llm_mode == "skip":
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Native 모드: instruction 반환
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.llm_mode == "native":
            logger.info(f"  [AI+Web] Native 모드: instruction 준비")
            
            instruction = self._build_native_instruction(question, context)
            
            # ValueEstimate 형식으로 반환 (특수 타입)
            return [ValueEstimate(
                source_type=SourceType.AI_AUGMENTED,
                value=0.0,  # placeholder
                confidence=0.0,  # AI가 결정
                reasoning="AI가 추정 + 웹 검색 수행 필요",
                source_detail="native_mode_instruction",
                raw_data={"instruction": instruction}
            )]
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # External 모드: API 호출
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        else:
            logger.info(f"  [AI+Web] External 모드: API 호출")
            
            # LLM API 호출 (웹 검색 포함 지시)
            result = self._llm_api_with_web_search(question, context)
            
            if result:
                return [ValueEstimate(
                    source_type=SourceType.AI_AUGMENTED,
                    value=result['value'],
                    confidence=result['confidence'],
                    reasoning=result['reasoning'],
                    source_detail=f"LLM + Web ({result['sources_count']}개 출처)",
                    raw_data=result
                )]
            
            return []
    
    def _build_native_instruction(
        self, 
        question: str, 
        context: Optional[Context]
    ) -> str:
        """
        Native 모드 instruction 생성
        
        AI에게 제공할 상세한 로직
        """
        
        instruction = f"""
# AI Augmented Estimation: {question}

당신의 임무:
1. 값 추정 시도 (지식 기반)
2. 불확실하면 웹 검색 수행
3. 검색 결과에서 숫자 추출
4. Consensus 계산
5. 결과 반환

## Step 1: 지식 기반 추정

질문: {question}
"""
        
        if context:
            instruction += f"맥락: domain={context.domain}, region={context.region}\n"
        
        instruction += """
먼저 당신의 지식으로 답변 시도:
- 확실하면 (confidence ≥ 0.8): 값 반환 후 종료
- 불확실하면 (confidence < 0.8): Step 2로

## Step 2: 웹 검색 수행

구글/네이버에서 검색:
- 검색어: "{question}"
"""
        
        if context and context.region:
            instruction += f"- 지역 추가: \"{context.region} {question}\"\n"
        
        instruction += """
상위 5-10개 결과 확인

## Step 3: 숫자 추출

각 결과에서:
1. 관련 숫자 찾기
2. 단위 확인 (명, 원, %, M, B, 조, 억)
3. 표준화 (예: 51.7M → 51,700,000)

예시:
- "인구 51.7M" → 51,700,000
- "GDP 2조원" → 2,000,000,000,000
- "성장률 5.2%" → 0.052

## Step 4: Consensus 계산

숫자들의 Consensus:
1. 이상치 제거 (평균±50% 벗어난 값)
2. 남은 숫자들의 평균 또는 중앙값
3. 일치 정도 평가

예시:
- 추출: [51.7M, 51.5M, 52.1M, 120M, 51.8M]
- 이상치 제거: 120M 제외
- 평균: 51.775M
- 일치도: 4/5 = 0.8 (높음)

## Step 5: 결과 반환

다음 형식으로 반환:

```json
{
    "value": 51775000,
    "confidence": 0.75,
    "reasoning": "웹 검색 4개 출처 평균 (1개 이상치 제거)",
    "sources_count": 4,
    "source_detail": "Google 검색 5개 결과",
    "web_searched": true
}
```

**Confidence 기준**:
- 5개 이상 일치: 0.80
- 3-4개 일치: 0.70
- 2개 일치: 0.60
- 1개만: 0.50
- LLM 지식만 (웹 검색 안 함): 0.65

**중요**: 
- 웹 검색은 선택적 (LLM이 불확실할 때만)
- 확실하면 지식만으로 답변 (더 빠름)
"""
        
        return instruction
    
    def _llm_api_with_web_search(
        self, 
        question: str, 
        context: Optional[Context]
    ) -> Optional[Dict]:
        """
        External 모드: LLM API 호출 + 웹 검색
        
        TODO: 실제 구현
        """
        # LangChain + Tavily/SerpAPI 사용
        # 또는 기존 크롤링 모듈 활용
        pass
```

### **통합 전후 비교**

#### **Before: 분리 (11개)**

```python
# source_collector.py
class SourceCollector:
    def __init__(self, llm_mode: str = "native"):
        # Value (5개)
        self.definite_data = DefiniteDataSource()
        self.llm = LLMEstimationSource(llm_mode)        # 거의 스킵
        self.web = WebSearchSource()                    # 복잡한 크롤링
        self.rag = RAGBenchmarkSource()
        self.statistical_value = StatisticalValueSource()
    
    def _collect_values_sequential(self, question, context):
        # 2. LLM
        estimates.extend(self.llm.collect(question, context))  # → 빈 리스트
        
        # 3. 웹 검색
        estimates.extend(self.web.collect(question, context))  # → 크롤링 실행
```

**문제**:
- LLM: Native 모드에서 스킵 (활용도 0%)
- Web: 복잡한 구현 (활용도: 가이드라인만)
- 역할 중복: 둘 다 "외부에서 값 가져오기"

#### **After: 통합 (10개)** ⭐

```python
# source_collector.py
class SourceCollector:
    def __init__(self, llm_mode: str = "native"):
        # Value (4개) ⭐ 5→4로 통합
        self.definite_data = DefiniteDataSource()
        self.ai_augmented = AIAugmentedEstimationSource(llm_mode)  # ⭐ 통합!
        self.rag = RAGBenchmarkSource()
        self.statistical_value = StatisticalValueSource()
    
    def _collect_values_sequential(self, question, context):
        # 2. AI 증강 추정 (LLM + Web 통합)
        estimates.extend(self.ai_augmented.collect(question, context))
        # → Native: instruction 반환
        # → External: LLM API + 웹 검색 자동 실행
```

**장점**:
- 역할 명확: "AI가 추정 (필요시 웹 검색)"
- Native 모드 활용도 ↑
- 코드 단순화

---

## 🔍 11개 Source 정의 명확도 검토

### ✅ **명확하게 정의된 Source (4개)**

1. **DefiniteDataSource** (Value)
   ```python
   # 역할: 프로젝트 데이터에서 확정값
   # 정의: ✅ 명확
   # 구현: ✅ 완성
   # 활용: 높음 (Phase 0)
   ```

2. **RAGBenchmarkSource** (Value)
   ```python
   # 역할: Quantifier 벤치마크 RAG 검색
   # 정의: ✅ 명확
   # 구현: ✅ 완성
   # 활용: 중간 (Phase 3)
   ```

3. **StatisticalValueSource** (Value)
   ```python
   # 역할: 통계 분포에서 대표값 (median/mean)
   # 정의: ✅ 명확
   # 구현: ✅ 완성
   # 활용: 낮음 (최후 수단)
   ```

4. **LegalNormSource** (Soft)
   ```python
   # 역할: 법률 규범 (최저임금, 근로시간)
   # 정의: ✅ 명확
   # 구현: 🟡 하드코딩 (2개만)
   # 활용: 낮음 (<1% 케이스)
   ```

### ⚠️ **부분적으로 정의된 Source (5개)**

5. **SpacetimeConstraintSource** (Physical)
   ```python
   # 역할: ✅ 명확 (시공간 제약)
   # 구현: 🟡 샘플만 (TODO 주석)
   # 활용: ⚠️ 거의 없음
   
   # 코드:
   def _check_travel_time(...):
       # TODO: 실제 구현
       return None  # ← 항상 None!
   ```

6. **ConservationLawSource** (Physical)
   ```python
   # 역할: ✅ 명확 (보존 법칙)
   # 구현: 🟡 샘플만
   # 활용: ⚠️ 거의 없음
   ```

7. **MathematicalDefinitionSource** (Physical)
   ```python
   # 역할: ✅ 명확 (수학 정의)
   # 구현: 🟡 샘플만
   # 활용: ⚠️ 거의 없음
   ```

8. **StatisticalPatternSource** (Soft)
   ```python
   # 역할: ✅ 명확 (통계 패턴)
   # 구현: 🟡 샘플만 (TODO: RAG 검색)
   # 활용: ⚠️ 중간
   
   # 코드:
   def collect(...):
       # TODO: 실제로는 RAG 검색 or DB 조회
       # 현재는 샘플 구현  ← 하드코딩!
   ```

9. **WebSearchSource** (Value)
   ```python
   # 역할: ⚠️ 애매 (가이드라인? 확정값?)
   # 구현: ✅ 완성 (크롤링)
   # 활용: 중간
   # 문제: 과도한 복잡도 (원래 목적: 가이드라인)
   ```

### ❌ **미구현 Source (2개)**

10. **BehavioralInsightSource** (Soft)
    ```python
    # 역할: ✅ 명확 (행동경제학)
    # 구현: ❌ TODO만
    # 활용: 없음
    
    # 코드:
    def collect(...):
        # TODO: 행동경제학 패턴
        return []  # ← 항상 빈 리스트!
    ```

11. **LLMEstimationSource** (Value)
    ```python
    # 역할: ⚠️ 애매 (간단한 사실? 추정?)
    # 구현: 🔴 스킵 (Native 모드)
    # 활용: 없음
    
    # 코드:
    def collect(...):
        # TODO: 실제 LLM 호출
        # 현재는 스킵
        logger.info("스킵 (Native Mode는 interactive 필요)")
        return []  # ← 항상 빈 리스트!
    ```

---

## 📊 Source별 활용도 분석

| Source | 구현도 | 활용도 | 역할 명확도 | 우선순위 |
|--------|--------|--------|------------|----------|
| DefiniteData | 100% | 높음 | ✅ | P0 (필수) |
| RAGBenchmark | 100% | 중간 | ✅ | P1 (중요) |
| StatisticalValue | 100% | 낮음 | ✅ | P2 (있으면 좋음) |
| LegalNorm | 30% | 낮음 | ✅ | P3 (선택) |
| **AIAugmented** | **0%** | **높을 것** | ⚠️ | **P1** |
| ~~LLM~~ | 10% | 없음 | ⚠️ | 삭제 |
| ~~Web~~ | 100% | 중간 | ⚠️ | 통합 |
| StatisticalPattern | 30% | 중간 | ✅ | P2 |
| Spacetime | 10% | 없음 | ✅ | P3 |
| Conservation | 10% | 없음 | ✅ | P3 |
| Mathematical | 10% | 없음 | ✅ | P3 |
| Behavioral | 0% | 없음 | ✅ | P3 |

**결론**:
- **실제 활용**: 4개만 (DefiniteData, RAG, Statistical, Web)
- **나머지 7개**: 미구현 또는 활용도 극히 낮음

---

## 🎯 권장 리팩토링

### **Option 1: 통합 + 정리 (권장)** ⭐

```python
# Physical (3개) → 1개로 통합 또는 제거
class PhysicalConstraintSource:
    """모든 물리 제약 통합"""
    
    def collect(self, question, context):
        # 시공간, 보존, 수학을 하나로
        # 또는 Native AI에게 위임
        return []  # 현재 활용도 낮아 제거 고려

# Soft (3개) → 1개로 통합
class SoftConstraintSource:
    """모든 Soft 제약 통합"""
    
    def collect(self, question, context):
        # 법률, 통계 패턴, 행동경제학
        # Native AI에게 위임
        return self._ai_instruction_for_constraints()

# Value (5개) → 4개로 통합
class SourceCollector:
    def __init__(self):
        # Value (4개만)
        self.definite_data = DefiniteDataSource()
        self.ai_augmented = AIAugmentedEstimationSource()  # LLM+Web
        self.rag_benchmark = RAGBenchmarkSource()
        self.statistical = StatisticalValueSource()
        
        # Physical → Native AI
        self.physical = None  # AI instruction
        
        # Soft → Native AI
        self.soft = None  # AI instruction
```

**결과**: 11개 → **4개 핵심 Source** (Physical/Soft는 AI instruction)

### **Option 2: 점진적 통합**

**Phase 1** (이번 주):
- LLM + Web 통합 → AIAugmentedEstimationSource

**Phase 2** (다음 주):
- Physical 3개 → Native AI instruction
- Soft 3개 → Native AI instruction

**Phase 3** (1개월):
- 실제 활용도 측정
- 불필요한 Source 제거

---

## 📝 구체적 구현 계획

### 1. AIAugmentedEstimationSource 생성

```python
# umis_rag/agents/estimator/sources/value.py

class AIAugmentedEstimationSource(ValueSourceBase):
    """
    AI 증강 추정 (LLM + Web 통합)
    
    Native 모드:
    - instruction 반환
    - AI가 추정 + 필요시 웹 검색
    
    External 모드:
    - LLM API 호출
    - 자동 웹 검색 (function calling)
    """
    # ... (위의 구현 참조)
```

### 2. SourceCollector 업데이트

```python
# umis_rag/agents/estimator/source_collector.py

class SourceCollector:
    def __init__(self, llm_mode: str = "native"):
        logger.info("[Source Collector] 초기화")
        
        # Physical (3개) → Native AI instruction
        self.physical_instruction = self._build_physical_instruction()
        
        # Soft (3개) → Native AI instruction  
        self.soft_instruction = self._build_soft_instruction()
        
        # Value (4개) ⭐
        self.definite_data = DefiniteDataSource()
        self.ai_augmented = AIAugmentedEstimationSource(llm_mode)
        self.rag = RAGBenchmarkSource()
        self.statistical_value = StatisticalValueSource()
        
        logger.info(f"  ✅ 4개 핵심 Source + AI instructions 준비")
```

### 3. models.py 업데이트

```python
# umis_rag/agents/estimator/models.py

class SourceType(Enum):
    # ... 기존
    AI_AUGMENTED = "ai_augmented"  # ⭐ 신규 (LLM + Web)
    # LLM = "llm"  # ← 삭제
    # WEB_SEARCH = "web_search"  # ← 삭제 (통합됨)
```

---

## ✅ 통합의 장점

1. **단순화**
   - 11개 → 4개 핵심 Source (Physical/Soft는 instruction)
   - 중복 제거 (LLM vs Web)

2. **Native 모드 활용도 ↑**
   - 현재: LLM Source 스킵
   - 통합 후: AI가 추정 + 웹 검색

3. **유지보수 ↓**
   - 크롤링 모듈 → instruction으로 대체
   - AI가 알아서 최적화

4. **철학 일관성**
   - UMIS Native 모드: AI 주도
   - Source도 AI instruction 중심

5. **유연성 ↑**
   - AI가 상황에 따라 웹 검색 여부 결정
   - 확실하면 지식만, 불확실하면 웹 검색

---

## 🚀 실행 계획

### **즉시 (이번 주)**

1. ✅ `AIAugmentedEstimationSource` 생성
2. ✅ `source_collector.py` 업데이트
3. ✅ `models.py` SourceType 추가
4. ✅ 테스트 스크립트 작성

**소요 시간**: 3-4시간

### **다음 주**

1. Physical/Soft → Native AI instruction 전환
2. 불필요한 Source 제거 또는 병합
3. 문서 업데이트

### **1개월 내**

1. 실제 활용도 측정
2. 최종 Source 구조 확정
3. v8.0.0 릴리스

---

## 📋 최종 Source 구조 (제안)

```yaml
# v7.8.0 최종 구조

Core Sources (4개):
  1. DefiniteDataSource      - 프로젝트 확정 데이터
  2. AIAugmentedEstimation   - AI 추정 + 웹 검색
  3. RAGBenchmarkSource      - RAG 벤치마크
  4. StatisticalValueSource  - 통계 분포값

AI Instructions (2개):
  5. Physical Constraints    - 시공간, 보존, 수학 (instruction)
  6. Soft Constraints        - 법률, 통계 패턴, 행동 (instruction)

총: 6개 (4개 코드 + 2개 instruction)
vs 기존: 11개

단순화: 45% (11→6)
```

---

## 💡 결론

1. **LLM + Web 통합 적극 권장** ✅
   - 역할 중복 제거
   - Native 모드 활용도 향상
   - 코드 단순화

2. **11개 Source 정의 상태**
   - ✅ 명확: 4개
   - ⚠️ 부분적: 5개 (샘플만)
   - ❌ 미구현: 2개 (스킵 또는 TODO)

3. **실제 활용도**
   - 높음: 3개 (DefiniteData, RAG, AI+Web)
   - 중간: 2개 (Statistical, Soft Pattern)
   - 낮음: 6개 (Physical 3개, Legal, Behavioral, LLM)

4. **권장 조치**
   - 즉시: LLM + Web 통합
   - 단기: Physical/Soft → AI instruction
   - 중기: 활용도 낮은 Source 제거/병합

**다음**: `AIAugmentedEstimationSource` 구현하시겠습니까?

