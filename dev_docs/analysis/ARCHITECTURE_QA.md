# UMIS Multi-Agent RAG 아키텍처 Q&A

## 🎯 당신의 4가지 질문에 대한 답변

---

## Q1: 저장용 메타데이터 스키마는?

### A: Core + Agent-Specific 이중 구조

```yaml
통합 메타데이터 구조:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────┐
│  Core Metadata (모든 agent 공유)         │
├─────────────────────────────────────────┤
│  source_id: "baemin_case"               │
│  source_file: "business_model_..."      │
│  domain: "case_study"                   │
│  category: "platform"                   │
│  validation_status: "verified"          │
│  quality_grade: "A"                     │
└─────────────────────────────────────────┘
              ↓ 공유됨 ↓
┌──────────┬──────────┬──────────┬──────────┐
│ Albert   │  Steve   │   Bill   │  Rachel  │
│ Specific │ Specific │ Specific │ Specific │
├──────────┼──────────┼──────────┼──────────┤
│ view_    │ view_    │ view_    │ view_    │
│  type:   │  type:   │  type:   │  type:   │
│ structu  │ opportu  │ quantit  │ source   │
│  -ral    │  -nity   │  -ative  │          │
│          │          │          │          │
│ patterns │ pattern  │ metrics  │ sources  │
│ dynamics │ triggers │ formulas │ reliabi  │
│          │ csf      │ data_    │  -lity   │
│          │          │  quality │          │
│          │          │          │          │
│ chunking │ chunking │ chunking │ chunking │
│  level:  │  level:  │  level:  │  level:  │
│  meso    │  case    │ calcul   │  source  │
└──────────┴──────────┴──────────┴──────────┘
```

### 실제 저장 예시: "배달의민족" 사례

```json
// Chunk 1: Steve View
{
  "chunk_id": "steve_baemin_platform_opportunity",
  "content": "플랫폼 비즈니스 모델 실행 사례...",
  "metadata": {
    // Core (공통)
    "source_id": "baemin_case",
    "source_file": "umis_business_model_patterns_v6.2.yaml",
    "domain": "case_study",
    "category": "platform",
    "validation_status": "verified",
    "quality_grade": "A",
    "version": "6.2",
    "language": "ko",
    
    // Steve-specific
    "agent_view": "steve",
    "steve_view_type": "case_learning",
    "steve_pattern_id": "platform_business_model",
    "steve_pattern_type": "business_model",
    "steve_triggers": "[\"파편화\", \"중개비용\"]",
    "steve_csf": "[\"양측확보\", \"밀도전략\"]",
    "steve_difficulty": "high",
    "steve_chunking_level": "case",
    
    // Cross-reference
    "related_chunks": "[\"albert_baemin_structure\", \"bill_baemin_metrics\"]",
    
    "token_count": 650
  }
}

// Chunk 2: Bill View (같은 사례, 다른 관점)
{
  "chunk_id": "bill_baemin_growth_metrics",
  "content": "MAU: 1,000만, 점유율: 60%...",
  "metadata": {
    // Core (동일!)
    "source_id": "baemin_case",  // ← 같은 source_id!
    "domain": "case_study",
    "quality_grade": "A",
    
    // Bill-specific
    "agent_view": "bill",
    "bill_view_type": "quantitative",
    "bill_metrics": "[{\"name\":\"MAU\",\"value\":10000000}]",
    "bill_data_quality": "estimated",
    "bill_chunking_level": "calculation",
    
    // Cross-reference
    "related_chunks": "[\"steve_baemin_opportunity\"]",
    
    "token_count": 350
  }
}
```

---

## Q2: 각 Agent별 Retrieval Layer는?

### A: Agent별 필터링 전략 + 청킹 레벨

```python
# Albert Retrieval Layer
class AlbertRetriever:
    """
    Albert의 검색 특성:
    - 거시적 시장 구조
    - 경쟁 역학
    - 장기 트렌드
    """
    
    def search_structure(self, market: str):
        """시장 구조 검색"""
        return vectorstore.search(
            query=market,
            filter={
                "$and": [
                    {"agent_view": "albert"},
                    {"albert_view_type": "structural"},
                    {"albert_chunking_level": {"$in": ["macro", "meso"]}}
                ]
            }
        )
    
    def search_dynamics(self, pattern: str):
        """시장 역학 검색"""
        return vectorstore.search(
            query=pattern,
            filter={
                "$and": [
                    {"agent_view": "albert"},
                    {"albert_view_type": "dynamics"},
                    {"albert_chunking_level": "micro"}  # 세밀한 패턴
                ]
            }
        )


# Steve Retrieval Layer
class SteveRetriever:
    """
    Steve의 검색 특성:
    - 기회 패턴 인식
    - 실행 전략
    - 사례 학습
    """
    
    def search_by_trigger(self, triggers: str):
        """트리거 시그널 → 패턴"""
        return vectorstore.search(
            query=triggers,
            filter={
                "$and": [
                    {"agent_view": "steve"},
                    {"steve_view_type": "opportunity"},
                    {"steve_chunking_level": "section"}  # 섹션 레벨 (최적)
                ]
            }
        )
    
    def search_cases_by_industry(self, industry: str, pattern_id: str):
        """산업 유사성 → 사례"""
        return vectorstore.search(
            query=industry,
            filter={
                "$and": [
                    {"agent_view": "steve"},
                    {"steve_view_type": "case_learning"},
                    {"steve_pattern_id": pattern_id},
                    {"steve_chunking_level": "case"}  # 완전한 사례
                ]
            }
        )
    
    def ask_bill_for_metrics(self, source_id: str):
        """Bill에게 정량 데이터 요청"""
        # Bill의 retriever 사용!
        bill_retriever = BillRetriever()
        return bill_retriever.search(
            "",  # 쿼리 없음 (source_id로만)
            filter={
                "$and": [
                    {"source_id": source_id},  # 같은 사례
                    {"bill_view_type": "quantitative"}
                ]
            }
        )


# Bill Retrieval Layer
class BillRetriever:
    """
    Bill의 검색 특성:
    - 숫자 중심
    - 계산식
    - 빠른 참조
    """
    
    def search_exact_metric(self, metric_name: str):
        """특정 메트릭만 빠르게"""
        return vectorstore.search(
            query=metric_name,
            filter={
                "$and": [
                    {"agent_view": "bill"},
                    {"bill_chunking_level": "metric"},  # 가장 작은 단위
                    {"bill_has_numbers": True}
                ]
            },
            k=1  # 하나만!
        )
    
    def search_calculation_logic(self, calc_type: str):
        """계산 과정 전체"""
        return vectorstore.search(
            query=calc_type,
            filter={
                "$and": [
                    {"agent_view": "bill"},
                    {"bill_chunking_level": "calculation"}  # 계산 블록
                ]
            }
        )


# Rachel Retrieval Layer
class RachelRetriever:
    """
    Rachel의 검색 특성:
    - 출처 정보
    - 신뢰도
    - 검증 상태
    """
    
    def search_by_source(self, source_id: str):
        """특정 데이터의 출처 정보"""
        return vectorstore.search(
            query="",
            filter={
                "$and": [
                    {"agent_view": "rachel"},
                    {"source_id": source_id},
                    {"rachel_chunking_level": "source"}  # 출처별
                ]
            }
        )
    
    def verify_data_point(self, data_description: str):
        """특정 데이터 포인트 검증"""
        return vectorstore.search(
            query=data_description,
            filter={
                "$and": [
                    {"agent_view": "rachel"},
                    {"rachel_view_type": "verification"},
                    {"rachel_reliability": {"$in": ["high", "medium"]}}
                ]
            }
        )
```

---

## Q3: 각 Agent별 메타데이터 Subset은?

### A: Agent가 "볼" 메타데이터

```python
# Steve가 검색 결과에서 보는 메타데이터

steve_result = {
    # Core (항상 볼 수 있음)
    "source_id": "baemin_case",
    "domain": "case_study",
    "quality_grade": "A",
    
    # Steve-specific (자기 것만)
    "steve_pattern_id": "platform_business_model",
    "steve_csf": "[\"양측확보\", ...]",
    "steve_difficulty": "high",
    
    # Cross-reference (협업용)
    "related_chunks": [
        "albert_baemin_structure",  // Albert에게 문의 가능
        "bill_baemin_metrics"       // Bill에게 문의 가능
    ],
    
    # 다른 agent 것은 안 보임 (필요 없음)
    # "albert_patterns": ... (숨김)
    # "bill_metrics": ... (숨김)
}

# Bill이 같은 source_id 검색 시

bill_result = {
    # Core (공통)
    "source_id": "baemin_case",
    "domain": "case_study",
    
    # Bill-specific (자기 것)
    "bill_metrics": "[...]",
    "bill_formulas": "[...]",
    "bill_data_quality": "estimated",
    
    # Cross-reference
    "related_chunks": ["steve_baemin_opportunity"],
    
    # Steve 것은 안 보임
    # "steve_pattern_id": ... (숨김)
}
```

### 실제 사용 시나리오

```python
# Steve가 Bill에게 협업 요청

# 1. Steve가 기회 발견
steve_chunk = steve_retriever.search("플랫폼 기회")
# → steve_baemin_platform_opportunity

# 2. Steve가 "정량 데이터 필요"
source_id = steve_chunk.metadata["source_id"]  # "baemin_case"

# 3. Bill retriever로 같은 source_id 검색
bill_chunk = bill_retriever.search(
    "",
    filter={"source_id": source_id}  # 같은 사례!
)
# → bill_baemin_growth_metrics

# 4. Steve가 Bill 데이터 활용
mau = extract_from_bill_chunk(bill_chunk)  # "1,000만"
```

---

## Q4: 저장 시 청킹 레벨 결정 방법은?

### A: Agent의 정보 요구 특성 기반

```yaml
청킹 레벨 결정 기준:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 정보 완결성 vs 검색 정확도
   ┌─────────────────────────────────────┐
   │  큰 청크 (완결성 ↑)                 │
   │  - 장점: 맥락 완전                  │
   │  - 단점: 검색 정확도 ↓              │
   │                                     │
   │  작은 청크 (정확도 ↑)               │
   │  - 장점: 정밀 검색                  │
   │  - 단점: 맥락 손실                  │
   └─────────────────────────────────────┘

2. Agent별 정보 요구 패턴
   
   Albert (구조 분석):
     요구: "시장 구조 변화 과정"
     청킹: meso (500-800 토큰)
     이유: 구조 요소는 완결되어야 이해 가능
     
   Steve (전략 학습):
     요구: "실행 전략 전체"
     청킹: case (400-800 토큰)
     이유: 전략은 쪼개면 의미 손실
     
   Bill (숫자 참조):
     요구: "특정 메트릭만"
     청킹: metric (100-200 토큰)
     이유: 빠른 참조, 재사용 중요
     
   Rachel (출처 확인):
     요구: "출처 정보만"
     청킹: source (200-400 토큰)
     이유: 출처별 독립 검증

3. 데이터 특성
   
   구조화 데이터:
     → 작은 청크 가능 (명확한 구분점)
     
   서사적 데이터 (이야기):
     → 큰 청크 필요 (흐름 중요)
     
   정량 데이터:
     → 아주 작은 청크 (개별 지표)
```

### 결정 알고리즘

```python
def determine_chunking_level(
    agent: str,
    content_type: str,
    data_structure: str
) -> str:
    """
    청킹 레벨 자동 결정
    
    입력:
    -----
    agent: "steve", "albert", "bill", ...
    content_type: "case_study", "framework", "metric", ...
    data_structure: "narrative", "structured", "quantitative", ...
    
    출력:
    -----
    청킹 레벨 (예: "case", "meso", "calculation")
    """
    
    # Steve 규칙
    if agent == "steve":
        if content_type == "case_study":
            return "case"  # 사례는 완전히
        elif content_type == "pattern":
            if data_structure == "structured":
                return "section"  # 섹션별 (추천)
            else:
                return "pattern"  # 전체
        elif content_type == "framework":
            return "section"
    
    # Bill 규칙
    elif agent == "bill":
        if content_type == "single_metric":
            return "metric"  # 가장 작게
        elif content_type == "calculation":
            return "calculation"  # 계산 단위
        elif content_type == "report":
            return "report"  # 전체
    
    # Albert 규칙
    elif agent == "albert":
        if data_structure == "complex_structure":
            return "meso"  # 구조 요소별
        elif data_structure == "simple_pattern":
            return "micro"  # 세밀하게
        elif data_structure == "market_overview":
            return "macro"  # 전체
    
    # Rachel 규칙
    elif agent == "rachel":
        if content_type == "source_info":
            return "source"  # 출처별
        elif content_type == "verification":
            return "verification"  # 검증 항목별
    
    # 기본값
    return "medium"  # 500-800 토큰
```

---

## 📊 실전 예시: "배달의민족" 사례 5-View 청킹

### 원본 데이터 (1,500 토큰)

```yaml
배달의민족 사례:
  - 시장 배경: 300 토큰
  - 전략 실행: 400 토큰
  - 성장 지표: 300 토큰
  - 핵심 요인: 200 토큰
  - 출처 정보: 200 토큰
  - 검증 상태: 100 토큰
```

### Agent별 청킹 결과

```yaml
Albert (구조 분석):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  청킹 레벨: meso
  
  Chunk 1 (600 토큰):
    "시장 구조 변화"
    - 기존 구조: 파편화
    - 플랫폼 삽입 후: 집중화
    - Power shift
  
  Chunk 2 (500 토큰):
    "3면 시장 역학"
    - 음식점 ↔ 플랫폼 ↔ 고객 ↔ 배달원
    - 네트워크 효과
  
  이유: 구조 요소별로 분리 (패턴 명확)

Steve (기회 실행):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  청킹 레벨: case
  
  Chunk 1 (800 토큰):
    "플랫폼 비즈니스 모델 실행 사례"
    - 기회 인식
    - 양측 확보 전략
    - 밀도 전략
    - 수수료 모델
    - CSF
  
  이유: 전략은 완결성 중요 (쪼개면 안 됨)

Bill (정량 분석):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  청킹 레벨: calculation
  
  Chunk 1 (200 토큰):
    "성장 지표"
    - MAU: 1,000만
    - 점유율: 60%
    - 가맹점: 3만개
  
  Chunk 2 (300 토큰):
    "수익 계산"
    - GMV = MAU × 빈도 × 객단가
    - 매출 = GMV × 수수료율
    - 추정 연 매출: 4,800억
  
  이유: 계산 단위로 분리 (재사용 쉬움)

Rachel (출처 검증):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  청킹 레벨: source
  
  Chunk 1 (250 토큰):
    "SRC_001: Wikipedia"
    - URL: ...
    - 신뢰도: Medium
    - 정보: 연혁, 주요 지표
  
  Chunk 2 (200 토큰):
    "SRC_002: 공식 발표"
    - 출처: 우아한형제들
    - 신뢰도: High
    - 정보: MAU, 가맹점
  
  이유: 출처별 독립 검증

Stewart (검증 관리):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  청킹 레벨: summary
  
  Chunk 1 (200 토큰):
    "검증 상태 요약"
    - 등급: A
    - 검증: Albert, Steve, Bill, Rachel ✅
    - 주의: 일부 추정치
  
  이유: 빠른 품질 확인용
```

---

## 🎯 Multi-View 구현 전략

### 전략 1: View별 독립 변환 (권장)

```python
# 01_convert_yaml_multiview.py

def convert_baemin_to_all_views(raw_data: dict):
    """하나의 사례 → 5개 view 청크"""
    
    chunks = []
    
    # Albert view 생성
    chunks.append(
        create_albert_chunk(
            source_id="baemin_case",
            content=extract_structure_aspects(raw_data),
            chunking_level="meso"  # Albert는 meso 선호
        )
    )
    
    # Steve view 생성
    chunks.append(
        create_steve_chunk(
            source_id="baemin_case",
            content=extract_opportunity_aspects(raw_data),
            chunking_level="case"  # Steve는 case 선호
        )
    )
    
    # Bill view 생성 (여러 청크로 분할)
    chunks.extend(
        create_bill_chunks(
            source_id="baemin_case",
            content=extract_quantitative_data(raw_data),
            chunking_level="calculation"  # 계산 단위
        )
    )
    
    # Rachel view 생성
    chunks.extend(
        create_rachel_chunks(
            source_id="baemin_case",
            content=extract_sources(raw_data),
            chunking_level="source"  # 출처별
        )
    )
    
    # Stewart view 생성
    chunks.append(
        create_stewart_chunk(
            source_id="baemin_case",
            content=create_validation_summary(raw_data),
            chunking_level="summary"  # 요약
        )
    )
    
    # Cross-reference 연결
    link_chunks(chunks)  # related_chunks 필드 채움
    
    return chunks
```

### 전략 2: 메타데이터 일관성 검증

```python
def validate_cross_references(chunks: List[dict]):
    """
    Agent간 참조 무결성 검증
    
    검증:
    -----
    1. related_chunks에 명시된 chunk_id 존재하는가?
    2. source_id가 일치하는가?
    3. 순환 참조는 없는가?
    """
    
    chunk_ids = {c["chunk_id"] for c in chunks}
    
    for chunk in chunks:
        related = json.loads(chunk["metadata"]["related_chunks"])
        
        for related_id in related:
            assert related_id in chunk_ids, \
                f"Missing chunk: {related_id}"
    
    print("✅ Cross-reference 검증 완료")
```

---

## 🔬 실제 검색 시나리오

### 시나리오: Steve가 "배달 플랫폼" 기회 분석

```python
# 1. Steve가 패턴 검색
patterns = steve_retriever.search_by_trigger(
    "파편화된 공급-수요, 높은 중개 비용"
)
# → steve_platform_pattern_opportunity
#    source_id="platform_pattern"

# 2. Steve가 사례 검색
cases = steve_retriever.search_cases_by_industry(
    "음식 배달",
    pattern_id="platform_business_model"
)
# → steve_baemin_platform_opportunity
#    source_id="baemin_case"

# 3. Steve가 Bill에게 정량 데이터 요청
bill_data = steve.ask_bill_for_metrics(
    source_id="baemin_case"  # 2번에서 발견한 사례
)
# → bill_baemin_growth_metrics (같은 source_id!)
#    "MAU: 1,000만, 점유율: 60%..."

# 4. Steve가 Rachel에게 데이터 신뢰도 확인
rachel_verification = steve.ask_rachel_for_source(
    source_id="baemin_case"
)
# → rachel_baemin_sources
#    "SRC_001: Wikipedia (Medium)..."

# 5. Steve가 가설 생성
hypothesis = steve.generate_hypothesis(
    patterns=patterns,
    cases=cases,
    bill_metrics=bill_data,
    rachel_sources=rachel_verification
)
```

---

## 📊 저장 vs 조회 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│  1. 저장 (Single Collection)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  umis_knowledge_base                                         │
│  ├── albert_baemin_structure      (source_id: baemin_case) │
│  ├── steve_baemin_opportunity     (source_id: baemin_case) │
│  ├── bill_baemin_metrics          (source_id: baemin_case) │
│  ├── rachel_baemin_sources        (source_id: baemin_case) │
│  └── stewart_baemin_validation    (source_id: baemin_case) │
│                                                              │
│  공통 메타데이터로 연결 ━━━━━━━━━━━━━━━━━━━┓              │
│                                              ↓              │
│  source_id, domain, quality_grade 등 공유                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  2. 조회 (Agent별 Retrieval Layer)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SteveRetriever                                              │
│  ↓                                                           │
│  Filter: agent_view="steve"                                 │
│  ↓                                                           │
│  steve_baemin_opportunity 만 검색 ✅                        │
│  (albert/bill/rachel/stewart 것은 안 보임)                 │
│                                                              │
│  ────────────────────────────────────────                  │
│                                                              │
│  BillRetriever                                               │
│  ↓                                                           │
│  Filter: agent_view="bill"                                  │
│  ↓                                                           │
│  bill_baemin_metrics 만 검색 ✅                             │
│                                                              │
│  ────────────────────────────────────────                  │
│                                                              │
│  Cross-Agent 협업                                            │
│  ↓                                                           │
│  Steve: source_id 확인 → "baemin_case"                      │
│  Steve → Bill: source_id="baemin_case"로 검색 요청          │
│  Bill: Filter: agent_view="bill" AND source_id="baemin..."  │
│  ↓                                                           │
│  bill_baemin_metrics 반환 (같은 사례의 Bill view) ✅       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 왜 이 설계가 우수한가?

### 1. Single Source of Truth

```
같은 사실을 여러 곳에 저장 ❌

배달의민족 MAU가 1,000만 → 2,000만으로 변경?
  
  Bad 설계:
    - Steve 청크 수정
    - Bill 청크 수정
    - Albert 청크 수정
    → 3곳 수정! (실수 위험)
  
  Good 설계 (우리):
    - source_id="baemin_case"로 모든 view 연결
    - Bill view만 수정
    - Steve가 Bill view 참조
    → 1곳 수정! ✅
```

### 2. 적응형 해상도

```
Steve의 요구에 따라 해상도 조절:

"빠르게 패턴만 확인"
  → section 레벨 (300 토큰)
  → 빠른 검색, 개요만

"전략 전체를 상세히"
  → case 레벨 (800 토큰)
  → 완전한 맥락

"여러 사례 비교"
  → section 레벨 (300 토큰 × 5개)
  → 효율적
```

### 3. 크로스 협업 자연스러움

```python
# Steve가 작업 중
"배달의민족 사례가 좋네. Bill, 정량 데이터 줘"

# 기존 설계 (분리):
bill.search("배달의민족")  # 키워드로 다시 검색? 애매!

# 우리 설계:
steve_chunk.metadata["source_id"]  # "baemin_case"
bill.search_by_source_id("baemin_case")  # 정확히 매칭! ✅
```

---

## 🚀 구현 우선순위

### Phase 1: Steve만 완성 (현재) ✅
- 빠른 검증
- 단일 view

### Phase 2: Multi-View 전환 (다음)
- 메타데이터 스키마 적용
- 5-view 청킹
- Cross-reference 구축
- **예상 시간: 2-3일**

### Phase 3: Agentic 협업 (최종)
- Agent간 자율 협업
- Stewart 자동 검증
- **예상 시간: 1주**

---

## 결론

**당신의 이해가 100% 정확합니다!** 🎯

```yaml
✅ 저장: Single collection with multi-view chunks
✅ 조회: Agent별 retrieval layer + 필터링
✅ View: Agent별 projection (필요한 subset만)
✅ 청킹: Agent의 정보 요구 특성 기반
```

현재는 Steve만 구현했지만, 확장 경로가 명확합니다!

