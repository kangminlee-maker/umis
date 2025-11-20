# Source 재설계 제안서 (v7.8.0)

**날짜**: 2025-11-12  
**목적**: 11개 Source → 정교한 4개 Source + AI instruction  
**상태**: 구현 전 검토 단계

---

## 🎯 핵심 개선 사항

### 1. **AIAugmentedEstimationSource** (LLM + Web 통합)
- LLM 지식 우선 → 불확실하면 웹 검색
- Native: instruction / External: API 호출

### 2. **Physical Constraints** (개념 기반 상한/하한)
- 추정 대상 대비 **개념적으로 명백한** 상한/하한
- 너무 넓은 범위 방지 (의미 있는 제약)

### 3. **Soft Constraints** (통계적 접근)
- 법률/규범 위반 확률 고려
- 처벌 수위 → 준수율 추정

---

## 📐 Physical Constraints 재설계

### **현재 문제**

```python
# 현재: 샘플 데이터만, 실제 활용 거의 없음
class SpacetimeConstraintSource:
    def collect(self, question, context):
        # TODO: 실제 구현
        return None  # 항상 None!
```

### **개선안: 개념 기반 Boundary**

```python
class PhysicalConstraintSource:
    """
    물리적 제약 (개념 기반)
    
    원칙:
    -----
    - 추정 대상의 개념을 분석
    - 개념적으로 명백한 상한/하한 도출
    - 범위가 너무 넓으면 제공 안 함 (무의미)
    
    예시:
    -----
    질문: "한국 인구는?"
    개념: count (개수)
    상한: 8,000,000,000 (세계 인구, 너무 넓음 → 제공 안 함)
    하한: 0 (무의미)
    → Boundary 제공 안 함 ✅
    
    질문: "서울 1인당 소득은?"
    개념: income_per_capita
    상한: 1,000,000,000원 (개념적 최대, 현실적)
    하한: 9,860원 (최저임금 × 연간)
    범위: 약 100,000배 (너무 넓음)
    → Boundary 제공 안 함 ✅
    
    질문: "SaaS Churn Rate는?"
    개념: rate (비율)
    상한: 1.0 (100%, 모두 이탈)
    하한: 0.0 (0%, 아무도 안 이탈)
    범위: 명확하고 의미 있음
    → Boundary 제공 ✅
    
    질문: "한국 담배 판매량은?"
    개념: daily_consumption
    상한: 성인 인구 × 3갑/일 (헤비 스모커 최대)
        = 40,000,000 × 3 = 120,000,000갑/일
    하한: 0
    추정치: 87,671,233갑/일
    → 상한이 추정치 대비 40% 차이 (의미 있음) ✅
    ```

### **구현 로직**

```python
class PhysicalConstraintSource:
    """개념 기반 물리 제약"""
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """
        개념적으로 명백한 상한/하한 추출
        
        프로세스:
        1. 질문에서 개념 타입 추출 (count, rate, size, income)
        2. 개념별 상한/하한 규칙 적용
        3. 범위 의미 있는지 검증 (너무 넓으면 제공 안 함)
        """
        
        # Step 1: 개념 타입 추출
        concept_type = self._extract_concept_type(question)
        
        if not concept_type:
            return []  # 개념 파악 불가
        
        # Step 2: 개념별 Boundary 생성
        boundary = self._create_boundary_for_concept(
            concept_type=concept_type,
            question=question,
            context=context
        )
        
        if not boundary:
            return []
        
        # Step 3: 범위 의미성 검증
        if self._is_range_too_wide(boundary):
            logger.info(f"  [Physical] 범위 너무 넓음 → 제공 안 함")
            return []
        
        logger.info(f"  [Physical] Boundary: [{boundary.lower_bound}, {boundary.upper_bound}]")
        return [boundary]
    
    def _extract_concept_type(self, question: str) -> Optional[str]:
        """
        개념 타입 추출
        
        Returns:
            "count"        - 개수 (인구, 고객 수)
            "rate"         - 비율 (Churn, 전환율)
            "size"         - 크기 (시장 규모, 면적)
            "income"       - 소득 (ARPU, 임금)
            "duration"     - 기간 (LTV, Payback)
            "consumption"  - 소비량 (판매량, 사용량)
            None           - 파악 불가
        """
        
        # Rate (비율)
        rate_keywords = ['률', 'rate', 'churn', '전환', '점유율', '성장률', '%']
        if any(kw in question.lower() for kw in rate_keywords):
            return "rate"
        
        # Count (개수)
        count_keywords = ['수', '개수', '인구', '고객 수', '사용자 수', '명']
        if any(kw in question.lower() for kw in count_keywords):
            return "count"
        
        # Income (소득)
        income_keywords = ['arpu', '임금', '소득', '수익', '매출']
        if any(kw in question.lower() for kw in income_keywords):
            return "income"
        
        # Consumption (소비량)
        consumption_keywords = ['판매량', '소비량', '사용량', '구매량']
        if any(kw in question.lower() for kw in consumption_keywords):
            return "consumption"
        
        # Duration (기간)
        duration_keywords = ['ltv', 'lifetime', 'payback', '기간']
        if any(kw in question.lower() for kw in duration_keywords):
            return "duration"
        
        # Size (크기)
        size_keywords = ['규모', '면적', '크기', 'tam', 'sam']
        if any(kw in question.lower() for kw in size_keywords):
            return "size"
        
        return None
    
    def _create_boundary_for_concept(
        self,
        concept_type: str,
        question: str,
        context: Optional[Context]
    ) -> Optional[Boundary]:
        """
        개념별 Boundary 생성
        
        원칙: 개념적으로 명백한 상한/하한만
        """
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Rate (비율): 0.0 ~ 1.0
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "rate":
            return Boundary(
                source_type=SourceType.PHYSICAL,
                lower_bound=0.0,
                upper_bound=1.0,
                confidence=1.0,
                reasoning="비율의 수학적 범위 (0-100%)",
                constraint_type="mathematical_definition"
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Duration (기간): 0 ~ 매우 큰 값
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "duration":
            # LTV, Payback 등은 상한 설정 어려움
            # 하한만 명확 (0)
            
            # 단, Payback은 현실적 상한 있음
            if "payback" in question.lower():
                return Boundary(
                    source_type=SourceType.PHYSICAL,
                    lower_bound=0.0,
                    upper_bound=120.0,  # 10년 (월 단위)
                    confidence=0.90,
                    reasoning="Payback > 10년은 비현실적",
                    constraint_type="practical_limit"
                )
            
            return None  # LTV 등은 상한 설정 어려움
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Consumption (소비량): 개념 기반 상한
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "consumption":
            # 맥락에서 추출
            if "담배" in question and "한국" in question:
                # 성인 인구 기반 상한
                adult_population = 40_000_000  # 한국 성인
                max_per_person = 3  # 갑/일 (헤비 스모커 최대)
                
                upper = adult_population * max_per_person
                
                return Boundary(
                    source_type=SourceType.PHYSICAL,
                    lower_bound=0.0,
                    upper_bound=upper,
                    confidence=0.85,
                    reasoning=f"한국 성인 {adult_population:,}명 × 최대 3갑/일",
                    constraint_type="per_capita_limit"
                )
            
            # 일반적인 소비량: 인구 기반
            return self._consumption_boundary_from_population(question, context)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Count, Size, Income: 일반적으로 상한 설정 어려움
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        return None
    
    def _is_range_too_wide(self, boundary: Boundary) -> bool:
        """
        범위가 너무 넓은지 검증
        
        기준: upper/lower > 10,000 이면 무의미
        """
        
        if boundary.lower_bound <= 0:
            return True  # 하한이 0이면 범위 무한대
        
        ratio = boundary.upper_bound / boundary.lower_bound
        
        if ratio > 10_000:
            logger.debug(f"    범위 비율: {ratio:,.0f}배 (너무 넓음)")
            return True
        
        return False
    
    def _consumption_boundary_from_population(
        self,
        question: str,
        context: Optional[Context]
    ) -> Optional[Boundary]:
        """
        인구 기반 소비량 상한 추정
        
        Native 모드: AI instruction
        """
        
        if context and context.region:
            # AI에게 인구 기반 상한 계산 요청
            instruction = f"""
            질문: {question}
            지역: {context.region}
            
            다음 계산으로 상한 추정:
            1. {context.region} 인구 파악
            2. 1인당 최대 소비량 추정 (현실적 최대)
            3. 총 상한 = 인구 × 1인당 최대
            
            결과 반환:
            {{
                "upper_bound": 계산된 상한,
                "reasoning": "계산 근거",
                "confidence": 0.80
            }}
            """
            
            # Native 모드에서는 instruction 반환
            return Boundary(
                source_type=SourceType.PHYSICAL,
                lower_bound=0.0,
                upper_bound=0.0,  # AI가 계산
                confidence=0.0,   # AI가 결정
                reasoning="AI가 인구 기반 상한 계산 필요",
                raw_data={"instruction": instruction}
            )
        
        return None
```

---

## 🧮 Soft Constraints 재설계

### **현재 문제**

```python
# 현재: 범위만 제공, 활용도 낮음
class LegalNormSource:
    def collect(self, question, context):
        return SoftGuide(
            suggested_range=(9860, 15000),  # 최저임금 범위
            typical_value=9860
        )
        # → 실제 활용: 거의 없음
```

### **개선안: Knock-out 제약 (명백한 위반 감지)**

**핵심 통찰**:
- Soft라는 이름과 달리 **명백한 제약**들임
  - 법률: 대부분 지킴 (사회 유지 조건)
  - 통계패턴: 자연법칙 수준
  - 행동경제학: 인간본능
- 역할: **명백한 위반 값 제거** (Knock-out Gate)
- 준수율 계산 불필요 (복잡도만 증가)

```python
class SoftConstraintSource:
    """
    Soft Constraints (Knock-out Gate)
    
    원칙:
    -----
    - "Soft"라는 이름이지만 실제로는 명백한 제약
    - 법률: 사회 유지 조건 (대부분 지킴)
    - 통계패턴: 자연법칙 수준
    - 행동경제학: 인간본능
    
    역할:
    -----
    - 명백하게 위반된 값 감지 → Knock-out
    - 준수율 계산 불필요 (복잡도만 증가)
    - 임계값 기반 간단한 체크
    
    예시:
    -----
    질문: "한국 소상공인 평균 시급은?"
    추정값: 5,000원
    
    법률: 최저임금 9,860원
    임계값: 최저임금의 70% = 6,902원
    
    5,000 < 6,902 → 명백한 위반! ❌
    → Knock-out: "명백히 비현실적 (최저임금 미달)"
    
    ---
    
    질문: "한국 소상공인 평균 시급은?"
    추정값: 11,000원
    
    11,000 > 6,902 → 통과 ✅
    → 법률 제약 위반 아님
    """
    
    def __init__(self):
        # 법률 규범 DB (Knock-out 임계값)
        self.legal_norms = {
            '최저임금': {
                'legal_value': 9860,
                'direction': 'minimum',  # 최소값
                'tolerance': 0.70,  # 70% 미만이면 knock-out
                'reasoning': '최저임금의 70% 미만은 명백한 위반 (사회 유지 불가)'
            },
            
            '주당근로시간': {
                'legal_value': 52,
                'direction': 'maximum',  # 최대값
                'tolerance': 1.30,  # 130% 초과면 knock-out
                'reasoning': '법정 최대의 130% 초과는 명백한 위반'
            },
            
            '성인 흡연율': {
                'statistical_range': (0.15, 0.45),  # 15-45%
                'tolerance_lower': 0.05,  # 5% 미만 비현실적
                'tolerance_upper': 0.60,  # 60% 초과 비현실적
                'reasoning': '자연법칙 수준 (인간 행동 패턴)'
            }
        }
    
    def validate(self, question: str, estimated_value: float) -> Optional[str]:
        """
        추정값이 명백하게 위반하는지 체크
        
        Args:
            question: 질문
            estimated_value: 추정값
        
        Returns:
            None: 통과 ✅
            str: Knock-out 사유 ❌
        """
        
        # 키워드 매칭
        for norm_key, norm_data in self.legal_norms.items():
            if norm_key in question:
                
                # 최소값 제약
                if norm_data.get('direction') == 'minimum':
                    threshold = norm_data['legal_value'] * norm_data['tolerance']
                    
                    if estimated_value < threshold:
                        return (
                            f"❌ Knock-out: {estimated_value:,.0f} < {threshold:,.0f} "
                            f"({norm_data['reasoning']})"
                        )
                
                # 최대값 제약
                elif norm_data.get('direction') == 'maximum':
                    threshold = norm_data['legal_value'] * norm_data['tolerance']
                    
                    if estimated_value > threshold:
                        return (
                            f"❌ Knock-out: {estimated_value:,.0f} > {threshold:,.0f} "
                            f"({norm_data['reasoning']})"
                        )
                
                # 범위 제약
                elif 'statistical_range' in norm_data:
                    lower = norm_data['tolerance_lower']
                    upper = norm_data['tolerance_upper']
                    
                    if estimated_value < lower or estimated_value > upper:
                        return (
                            f"❌ Knock-out: {estimated_value:.2f} 범위 벗어남 "
                            f"[{lower}, {upper}] ({norm_data['reasoning']})"
                        )
        
        return None  # 통과 ✅
```

**예시**:

```
질문: "한국 소상공인 평균 시급은?"
추정값: 5,000원

법률: 최저임금 9,860원
임계값: 9,860 × 0.70 = 6,902원

체크: 5,000 < 6,902 → ❌ Knock-out
사유: "명백한 위반 (최저임금의 70% 미달)"

→ 이 추정값은 폐기!

---

질문: "한국 소상공인 평균 시급은?"
추정값: 11,000원

체크: 11,000 > 6,902 → ✅ 통과
→ 법률 제약 만족, 추정값 유효
```

---

## 🤖 AIAugmentedEstimationSource 상세 설계

### **Native 모드 Instruction**

```python
def _build_native_instruction(self, question: str, context: Optional[Context]) -> str:
    """
    AI에게 제공할 상세 로직
    """
    
    domain_info = f"도메인: {context.domain}" if context and context.domain else ""
    region_info = f"지역: {context.region}" if context and context.region else ""
    
    instruction = f"""
# AI Augmented Estimation

질문: {question}
{domain_info}
{region_info}

---

## 임무

당신은 값을 추정해야 합니다. 다음 프로세스를 따르세요:

### Step 1: 지식 기반 추정

먼저 당신의 지식(학습 데이터)으로 답변을 시도하세요.

**자가 평가**:
- 확신도가 **80% 이상**이면: 즉시 값 반환 (Step 2 스킵)
- 확신도가 **80% 미만**이면: Step 2로 진행

**반환 형식 (확신도 ≥ 80%)**:
```json
{{
    "value": 추정값,
    "confidence": 0.80-0.90,
    "reasoning": "지식 기반 추정 (출처: ...)",
    "web_searched": false
}}
```

---

### Step 2: 웹 검색 수행 (확신도 < 80%인 경우)

구글 또는 네이버에서 검색을 수행하세요.

**검색어 최적화**:
```
기본: "{question}"
"""
    
    if context:
        if context.region:
            instruction += f'\n지역 추가: "{context.region} {question}"'
        if context.time_period:
            instruction += f'\n시점 추가: "{question} {context.time_period}"'
    
    instruction += """

통계 키워드 추가: "statistics", "통계", "데이터"
```

**검색 범위**:
- 상위 **5-10개** 결과 확인
- 신뢰할 수 있는 출처 우선 (정부, 통계청, 위키피디아, 학술)

---

### Step 3: 숫자 추출

각 검색 결과에서 관련 숫자를 찾으세요.

**추출 대상**:
- 제목에 있는 숫자
- 본문 첫 2-3단락의 숫자
- 표/차트의 숫자

**단위 변환**:
```
영어 단위:
- 51.7M → 51,700,000
- 2.3B → 2,300,000,000
- 850K → 850,000

한국어 단위:
- 5170만 → 51,700,000
- 2조 3000억 → 2,300,000,000,000
- 85만 → 850,000

비율:
- 5.2% → 0.052
- 6-8% → 0.07 (중간값)
```

**관련성 확인**:
- 질문과 관련 있는 숫자만 추출
- 예: "인구" 질문에 "GDP" 숫자는 제외

---

### Step 4: Consensus 계산

추출된 숫자들의 합의값을 계산하세요.

**이상치 제거**:
1. 모든 숫자의 중앙값(median) 계산
2. 중앙값의 ±50% 범위 벗어난 값 제거
3. 남은 숫자들로 평균 계산

**예시**:
```
추출: [51.7M, 51.5M, 52.1M, 120M, 51.8M]
       ↓
중앙값: 51.8M
±50% 범위: [25.9M, 77.7M]
       ↓
이상치: 120M (범위 벗어남) → 제거
       ↓
평균: (51.7 + 51.5 + 52.1 + 51.8) / 4 = 51.775M
```

**Confidence 계산**:
```
일치 출처 개수:
- 5개 이상: 0.80
- 4개: 0.75
- 3개: 0.70
- 2개: 0.65
- 1개만: 0.55

추가 보너스:
- 신뢰 출처 (정부, 통계청): +0.05
- 최신 데이터 (2024): +0.03
```

---

### Step 5: 결과 반환

최종 결과를 다음 형식으로 반환하세요:

```json
{{
    "value": 51775000,
    "confidence": 0.75,
    "reasoning": "웹 검색 4개 출처 평균 (Wikipedia, 통계청, 네이버 지식백과, CIA Factbook). 1개 이상치(120M) 제거.",
    "sources_count": 4,
    "source_detail": "Google 검색 5개 결과",
    "web_searched": true,
    "extracted_numbers": [
        {{"value": 51700000, "source": "Wikipedia"}},
        {{"value": 51500000, "source": "통계청"}},
        {{"value": 52100000, "source": "네이버"}},
        {{"value": 51800000, "source": "CIA"}}
    ]
}}
```

**반환 규칙**:
- `value`: 최종 추정값 (숫자)
- `confidence`: 0.55-0.90 (신뢰도)
- `reasoning`: 상세 근거 (어떻게 계산했는지)
- `sources_count`: 사용한 출처 개수
- `web_searched`: true (웹 검색 수행) / false (지식만)

---

## 🎯 요약

**임무**: 
1. 지식으로 먼저 추정 (빠름)
2. 불확실하면 웹 검색 (정확함)
3. 여러 출처 종합 (신뢰도 높임)
4. 결과 반환

**핵심**: 
- **선택적 웹 검색** (필요할 때만)
- **Consensus 알고리즘** (여러 출처 평균)
- **명확한 근거 제시**
"""
    
    return instruction

def _llm_api_with_web_search(self, question: str, context: Optional[Context]) -> Optional[Dict]:
    """
    External 모드: LLM API 호출
    
    구현 방안:
    1. LangChain + Tavily/SerpAPI (웹 검색 자동)
    2. Function Calling (GPT-4가 직접 웹 검색)
    3. 또는 기존 크롤링 모듈 재활용
    """
    
    # TODO: LangChain Tool 사용
    # from langchain.agents import create_openai_tools_agent
    # from langchain_community.tools.tavily_search import TavilySearchResults
    
    pass
```

---

## 📋 구현 순서

### **Phase 1: AIAugmentedEstimationSource** (우선순위 1)

**파일**: `umis_rag/agents/estimator/sources/value.py`

```python
# 1. AIAugmentedEstimationSource 클래스 추가 (200줄)
# 2. LLMEstimationSource 제거 또는 deprecated
# 3. WebSearchSource → 선택적 기능으로 전환
```

**소요**: 2-3시간

### **Phase 2: SourceCollector 업데이트** (우선순위 2)

**파일**: `umis_rag/agents/estimator/source_collector.py`

```python
# 1. __init__에서 통합
#    self.llm 삭제
#    self.web 삭제
#    self.ai_augmented 추가
#
# 2. _collect_values_sequential 업데이트
#    LLM, Web 부분을 ai_augmented로 대체
```

**소요**: 1시간

### **Phase 3: Physical Constraints 재설계** (우선순위 3)

**파일**: `umis_rag/agents/estimator/sources/physical.py`

```python
# 1. 3개 클래스 → 1개로 통합
# 2. 개념 기반 Boundary 로직 구현
# 3. 범위 의미성 검증 추가
```

**소요**: 3-4시간

### **Phase 4: Soft Constraints 재설계** (우선순위 4)

**파일**: `umis_rag/agents/estimator/sources/soft.py`

```python
# 1. 3개 클래스 → 1개로 통합
# 2. Knock-out 임계값 설정
# 3. validate() 메서드 구현
```

**소요**: 2-3시간 (단순화)

### **Phase 5: 테스트 및 문서** (우선순위 5)

**파일**: `scripts/test_source_consolidation.py` (신규)

```python
# 1. 통합 전후 비교 테스트
# 2. 성능 벤치마크
# 3. 문서 업데이트
```

**소요**: 2시간

**총 소요**: 12-15시간 (1-2일)

---

## 🎯 검토 포인트

### 1. AIAugmented Instruction 충분한가?

- ✅ Step 1-5 명확
- ✅ 웹 검색 선택적
- ✅ 숫자 추출 로직 상세
- ✅ Consensus 알고리즘 명확

### 2. Physical Constraints 개념 기반 접근

- ✅ 개념 타입 추출 (rate, count, income, etc)
- ✅ 개념별 상한/하한 규칙
- ✅ 범위 의미성 검증 (너무 넓으면 제외)
- ❓ 충분한 케이스 커버? → 테스트 필요

### 3. Soft Constraints Knock-out Gate

- ✅ 명백한 위반 감지 (임계값 기반)
- ✅ 간단한 로직 (70% 규칙)
- ✅ 추가 데이터 불필요
- ✅ "Soft"지만 실제로는 명백한 제약

---

## ❓ 확인 사항

1. **AIAugmented instruction 충분한가요?**
   - Step이 너무 많거나 복잡하지 않은지?
   - AI가 이해하고 실행하기 충분한지?

2. **Physical Constraints 개념 접근이 맞나요?**
   - "개념적으로 명백한 상한/하한"의 정의가 명확한지?
   - 예시가 충분한지?

3. **Soft Constraints 준수율 모형이 합리적인가요?**
   - Rational Crime 모형 적용이 적절한지?
   - 준수율 계산 공식이 현실적인지?

4. **우선순위가 맞나요?**
   - Phase 1 (AIAugmented) 먼저?
   - 아니면 Physical/Soft 먼저?

**피드백 주시면 바로 구현하겠습니다!** 🚀

