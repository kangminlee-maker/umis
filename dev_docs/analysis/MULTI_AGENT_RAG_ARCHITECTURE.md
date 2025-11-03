# UMIS Multi-Agent RAG 구현 계획

## ✅ 당신의 이해 (100% 정확!)

### 1. 저장: Single Collection

```
Collection: umis_knowledge_base (하나!)
├── Chunk 1: albert_baemin_structure (Albert 관점)
├── Chunk 2: steve_baemin_opportunity (Steve 관점)
├── Chunk 3: bill_baemin_metrics (Bill 관점)
├── Chunk 4: rachel_baemin_sources (Rachel 관점)
└── Chunk 5: stewart_baemin_validation (Stewart 관점)

공통 메타데이터:
  source_id="baemin_case" (모두 연결)
```

### 2. 조회: Agent별 Retrieval Layer

```python
SteveRetriever:
  → Filter: agent_view="steve"
  → 청킹 레벨: case (사례 완결성)
  → View: 기회/전략 중심

AlbertRetriever:
  → Filter: agent_view="albert"
  → 청킹 레벨: meso (구조 요소)
  → View: 구조/역학 중심

BillRetriever:
  → Filter: agent_view="bill"
  → 청킹 레벨: calculation (계산 블록)
  → View: 정량/계산 중심
```

### 3. Projection View

```
같은 source_id="baemin_case"를
각 agent가 다르게 봄:

Albert: "2010-2020 시장 구조 재편 과정"
Steve: "플랫폼 모델 실행 전략 및 CSF"
Bill: "MAU 1,000만, 점유율 60%, GMV 6조"
Rachel: "출처: Wikipedia (Medium), 공식발표 (High)"
Stewart: "등급 A, 4명 검증 완료"
```

---

## 📋 구현 로드맵

### Phase 1: 현재 (Prototype) ✅

```yaml
상태:
  ✅ Steve view만 구현
  ✅ Single collection (steve_knowledge_base)
  ✅ 기본 검색 작동
  
한계:
  ⚠️ 다른 agent 추가 불가
  ⚠️ 메타데이터 구조 단순
```

### Phase 2: Multi-View 전환 (권장 다음 단계)

```yaml
작업:
  1. 메타데이터 스키마 적용 (metadata_schema.py)
  2. 01_convert_yaml.py 확장
     - 같은 사례를 5개 관점으로 청킹
     - 통합 메타데이터 생성
  3. Collection 통합 (steve → umis_knowledge_base)
  4. Agent별 Retriever 클래스 구현

예상 시간: 2-3일
```

### Phase 3: Agentic RAG (최종 목표)

```yaml
작업:
  1. Steve가 자율적으로 다른 agent 호출
  2. Bill/Rachel Retriever 사용
  3. Cross-agent 협업 자동화
  4. Stewart 자동 검증

예상 시간: 1-2주
```

---

## 🔧 Phase 2 상세 구현

### 1. YAML → Multi-View Chunks

```python
# scripts/01_convert_yaml_multiview.py (신규)

def convert_baemin_case(case_data: dict) -> List[Chunk]:
    """
    배달의민족 사례를 5개 관점으로 청킹
    """
    chunks = []
    
    # Albert View (구조 중심)
    chunks.append({
        "chunk_id": "albert_baemin_market_structure",
        "content": extract_structure_view(case_data),
        "metadata": {
            # Core
            "source_id": "baemin_case",
            "domain": "case_study",
            
            # Albert-specific
            "agent_view": "albert",
            "albert_view_type": "structural",
            "albert_patterns": '["중개_플랫폼", "3면_시장"]',
            "albert_chunking_level": "meso",
            
            # Cross-reference
            "related_chunks": '["steve_baemin_opportunity", "bill_baemin_metrics"]'
        }
    })
    
    # Steve View (기회 중심)
    chunks.append({
        "chunk_id": "steve_baemin_platform_opportunity",
        "content": extract_opportunity_view(case_data),
        "metadata": {
            # Core
            "source_id": "baemin_case",
            "domain": "case_study",
            
            # Steve-specific
            "agent_view": "steve",
            "steve_view_type": "case_learning",
            "steve_pattern_id": "platform_business_model",
            "steve_csf": '["양측확보", "밀도전략", "30분배달"]',
            "steve_chunking_level": "case",
            
            # Cross-reference
            "related_chunks": '["albert_baemin_structure", "bill_baemin_metrics"]'
        }
    })
    
    # Bill View (정량 중심)
    # Rachel View (출처 중심)
    # Stewart View (검증 중심)
    # ... 동일 패턴
    
    return chunks
```

### 2. Agent별 Retriever 구현

```python
# umis_rag/retrievers/multi_agent.py (신규)

class BaseAgentRetriever:
    """모든 agent retriever의 기본 클래스"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.vectorstore = Chroma(
            collection_name="umis_knowledge_base",  # 통합!
            ...
        )
    
    def _base_filter(self) -> dict:
        """기본 필터 (agent_view)"""
        return {"agent_view": self.agent_name}
    
    def search(self, query: str, **kwargs):
        """기본 검색"""
        base_filter = self._base_filter()
        
        # 추가 필터 병합
        if "filter" in kwargs:
            combined_filter = {
                "$and": [
                    base_filter,
                    kwargs["filter"]
                ]
            }
        else:
            combined_filter = base_filter
        
        return self.vectorstore.similarity_search(
            query,
            filter=combined_filter,
            **kwargs
        )


class SteveRetriever(BaseAgentRetriever):
    """Steve 전용 Retriever"""
    
    def __init__(self):
        super().__init__("steve")
    
    def search_patterns(self, triggers: str):
        """트리거 → 패턴"""
        return self.search(
            triggers,
            filter={
                "steve_view_type": "opportunity",
                "steve_chunking_level": {"$in": ["pattern", "section"]}
            }
        )
    
    def search_cases(self, industry: str, pattern_id: str):
        """산업 → 사례"""
        return self.search(
            industry,
            filter={
                "steve_view_type": "case_learning",
                "steve_pattern_id": pattern_id,
                "steve_chunking_level": "case"
            }
        )


class BillRetriever(BaseAgentRetriever):
    """Bill 전용 Retriever"""
    
    def __init__(self):
        super().__init__("bill")
    
    def search_metric(self, metric_name: str):
        """메트릭 빠른 검색"""
        return self.search(
            metric_name,
            filter={
                "bill_has_numbers": True,
                "bill_chunking_level": "metric"
            }
        )
    
    def search_calculation(self, calc_type: str):
        """계산 과정 검색"""
        return self.search(
            calc_type,
            filter={
                "bill_chunking_level": "calculation"
            }
        )
```

### 3. Cross-Agent 협업

```python
# Steve가 Bill/Rachel을 호출하는 시나리오

class SteveAgent:
    def __init__(self):
        self.steve_retriever = SteveRetriever()
        self.bill_retriever = BillRetriever()
        self.rachel_retriever = RachelRetriever()
    
    def discover_opportunity(self, albert_observation: str):
        """기회 발굴 (자동 협업)"""
        
        # 1. 패턴 검색 (내 retriever)
        patterns = self.steve_retriever.search_patterns(
            albert_observation
        )
        
        # 2. 정량 데이터 요청 (Bill retriever)
        metrics = self.bill_retriever.search_metric(
            f"{patterns[0].metadata['steve_pattern_id']} 시장 규모"
        )
        
        # 3. 출처 확인 (Rachel retriever)
        sources = self.rachel_retriever.search_source(
            metrics[0].metadata["source_id"]
        )
        
        # 4. 가설 생성 (LLM)
        return self.generate_hypothesis(
            patterns, metrics, sources
        )
```

---

## 💡 청킹 레벨 결정 예시

### 배달의민족 사례 (1,500 토큰 원본)

```yaml
Albert 청킹:
  목표: 구조 패턴 파악
  레벨: meso (500-800 토큰)
  결과:
    - Chunk 1: 시장 구조 변화 (600 토큰)
    - Chunk 2: 경쟁 구도 재편 (500 토큰)
  이유: 구조 요소별로 분리해야 패턴 명확

Steve 청킹:
  목표: 사례 학습 (실행 전략)
  레벨: case (400-800 토큰)
  결과:
    - Chunk 1: 전체 사례 (800 토큰)
  이유: 전략은 완결성 중요 (쪼개면 의미 손실)

Bill 청킹:
  목표: 정량 지표 참조
  레벨: calculation (300-500 토큰)
  결과:
    - Chunk 1: 성장 지표 (350 토큰)
    - Chunk 2: 수익 계산 (400 토큰)
  이유: 계산 단위로 분리해야 재사용 쉬움

Rachel 청킹:
  목표: 출처별 신뢰도
  레벨: source (200-400 토큰)
  결과:
    - Chunk 1: SRC_001 Wikipedia (250 토큰)
    - Chunk 2: SRC_002 공식 발표 (200 토큰)
  이유: 출처별로 분리해야 검증 쉬움

Stewart 청킹:
  목표: 빠른 품질 확인
  레벨: summary (200-300 토큰)
  결과:
    - Chunk 1: 검증 요약 (200 토큰)
  이유: 요약만 있으면 충분
```

---

## 🚀 다음 작업 제안

현재 Steve 단일 view는 작동합니다. 

**옵션 A**: 지금 상태로 계속 (빠른 프로토타입)
- Steve만으로 기본 RAG 완성
- Jupyter 노트북으로 데모
- 개념 검증 완료

**옵션 B**: Multi-View로 전환 (완전한 설계)
- 메타데이터 스키마 적용
- 5개 agent view 생성
- 완벽한 아키텍처

어떤 방향으로 진행할까요?

저는 **옵션 A 먼저 → 검증 후 옵션 B**를 추천합니다! 
Steve 단독으로 작동하는 것을 먼저 완성하고, 
그 다음 확장하는 게 안전합니다.

현재 에러부터 수정하고 Steve를 완성할까요? 🎯
