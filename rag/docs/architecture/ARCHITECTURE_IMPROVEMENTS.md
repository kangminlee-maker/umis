# 아키텍처 개선 제안 분석

**날짜:** 2025-11-02  
**목적:** 7가지 구조 개선안 검토 및 우선순위

---

## 1️⃣ Projection-at-Retrieval 병행 (지연 투영)

### 제안

```yaml
현재 (Pre-Projection):
  저장:
    - albert_baemin_structure (Observer view)
    - explorer_baemin_opportunity (Explorer view)
    - quantifier_baemin_metrics (Quantifier view)
    → 1개 사례 = 6개 청크 (중복!)

제안 (Lazy Projection):
  저장:
    - baemin_case (정규화, 1개만!)
    
  조회:
    Observer.search() → observer_view 필터 적용
    Explorer.search() → explorer_view 필터 적용
    → 조회 시 투영!
```

### 장단점

**Pre-Projection (현재):**
```yaml
장점:
  ✅ 검색 빠름: 이미 투영됨
  ✅ 캐시 효과: 반복 조회 빠름
  ✅ 단순함: 저장=조회

단점:
  ❌ 저장 중복: N배 (Agent 수만큼)
  ❌ 동기화: 원본 변경 시 N개 업데이트
  ❌ 디스크: N배 공간
```

**Lazy Projection:**
```yaml
장점:
  ✅ 저장 효율: 1배만
  ✅ 일관성: 단일 소스
  ✅ 유연성: 투영 로직 변경 쉬움

단점:
  ❌ 조회 느림: 매번 투영 계산
  ❌ 복잡도: 투영 로직 필요
  ❌ CPU: 반복 계산
```

### 🎯 제 판단

**Hybrid 접근 추천!**

```python
class HybridStorage:
    """
    자주 쓰는 것: Pre-Projection (캐시)
    가끔 쓰는 것: Lazy Projection (동적)
    """
    
    def search(self, agent, query):
        # 1. Pre-Projection 캐시 확인
        cached = self.cache.get(f"{agent}_{query}")
        if cached:
            return cached  # 빠름!
        
        # 2. Lazy Projection (캐시 미스)
        canonical = self.db.search(query)
        projected = self.project(canonical, agent)
        
        # 3. 자주 쓰는 것 캐싱
        if self.is_hot(query):
            self.cache.set(f"{agent}_{query}", projected)
        
        return projected
```

**이유:**
- 저장: 1배 (Canonical)
- 조회: 빠름 (Hot 쿼리 캐싱)
- 최적: 공간 + 속도 균형

**우선순위:** 🟡 P2 (최적화, 당장 필요 없음)

---

## 2️⃣ Schema-Registry & Contract-Test

### 제안

```yaml
문제:
  metadata_schema.py 변경 → 기존 청크 호환 깨짐
  
해결:
  1. Schema-Registry:
     schema_v1.json (v6.3.0-alpha)
     schema_v2.json (향후)
     
  2. Contract-Test:
     pytest로 스키마 준수 검증
```

### 구현

```python
# schema_registry.py

SCHEMAS = {
    "v1": {
        "core": {
            "source_id": str,
            "agent_view": str,
            "domain": str,
        },
        "explorer": {
            "explorer_pattern_id": str,
            "explorer_csf": str,
        }
    },
    "v2": {
        # 향후 확장
    }
}

# contract_test.py

def test_chunk_schema_compliance():
    """모든 청크가 스키마 준수하는지"""
    chunks = load_all_chunks()
    
    for chunk in chunks:
        schema_version = chunk.metadata.get("schema_version", "v1")
        schema = SCHEMAS[schema_version]
        
        assert validate(chunk.metadata, schema)
```

### 🎯 제 판단

**매우 중요! 🔴 P0**

**이유:**
```yaml
필요성:
  ✅ 호환성: 스키마 변경 시 기존 데이터 보호
  ✅ 검증: 자동으로 오류 발견
  ✅ 진화: 안전하게 스키마 확장

복잡도:
  • Schema-Registry: 1일
  • Contract-Test: 1일
  
  → 간단하면서 효과 큼!

즉시 구현:
  1. schema_registry.py (스키마 정의)
  2. pytest 추가 (테스트)
  3. metadata에 schema_version 추가
```

**우선순위:** 🔴 P0 (필수! 지금 구현 권장)

---

## 3️⃣ Routing/Policy YAML 외부화

### 제안

```yaml
# rag_policy.yaml

routing:
  explorer:
    trigger:
      - "패턴 매칭 필요"
      - "트리거 시그널 발견"
    
    search_sequence:
      - layer: "vector"
        filter: {pattern_type: "business_model"}
      
      - layer: "graph"
        expand: "COMBINES_WITH"
      
      - layer: "vector"
        filter: {chunk_type: "success_case"}
    
    fallback:
      - use: "yaml_only"
```

### 장단점

**코드 (현재):**
```python
# 하드코딩
if "패턴 매칭" in query:
    vector_search()
    graph_expand()
    case_search()
```

```yaml
장점:
  ✅ 빠름: 컴파일됨
  ✅ 타입 안전: IDE 지원

단점:
  ❌ 변경 어려움: 코드 수정 필요
  ❌ 이해 어려움: 코드 읽어야
```

**YAML (제안):**
```yaml
장점:
  ✅ 수정 쉬움: YAML 편집만
  ✅ 이해 쉬움: 선언적
  ✅ 실험 용이: 정책 A/B 테스트

단점:
  ❌ 파싱 필요: 런타임 오버헤드
  ❌ 타입 안전성 낮음: 오타 위험
  ❌ 복잡한 로직: YAML로 표현 한계
```

### 🎯 제 판단

**좋은 아이디어! 🟡 P1 (중요)**

**접근:**
```yaml
Hybrid:
  간단한 정책: YAML
  복잡한 로직: Python (plugin)

예시:
  rag_policy.yaml:
    explorer:
      search_layers: [vector, graph, vector]
      filter_preset: "business_opportunity"
  
  코드:
    policy = load_yaml("rag_policy.yaml")
    for layer in policy['explorer']['search_layers']:
        execute(layer)
```

**이점:**
```yaml
✅ Cursor 사용자가 직접 정책 수정 가능!
✅ 실험 용이
✅ 이해 쉬움
```

**우선순위:** 🟡 P1 (구현 권장, 2-3일)

---

## 4️⃣ Graph Provenance & Confidence

### 제안

```yaml
현재:
  (platform)-[:COMBINES_WITH {
    synergy: "충성도 + 수익"
  }]->(subscription)

제안:
  (platform)-[:COMBINES_WITH {
    synergy: "충성도 + 수익",
    provenance: "Amazon Prime 사례",
    confidence: 0.8,
    evidence: ["SRC_001", "SRC_002"]
  }]->(subscription)
```

### 대안들

**Option A: Confidence Score (숫자)**
```yaml
장점:
  ✅ 정량: 0.8 > 0.6 비교 가능
  ✅ 가중: Guardian이 가중 평균

단점:
  ❌ 모호: 0.8의 의미?
  ❌ 주관적: 누가 정하나?
```

**Option B: Yes/No (Boolean)**
```yaml
장점:
  ✅ 명확: verified = true/false
  ✅ 단순: 판단 쉬움

단점:
  ❌ 이진: 회색지대 표현 못함
```

**Option C: Tier 시스템 (추천!) ⭐**
```yaml
tier:
  gold: "검증됨, 3개 이상 사례"
  silver: "검증됨, 1-2개 사례"
  bronze: "추정, 이론적"
  experimental: "실험적"

예시:
  (platform)-[:COMBINES_WITH {
    tier: "gold",
    evidence: ["Amazon Prime", "Netflix", "Spotify"],
    verified_by: "guardian",
    verified_date: "2025-11-02"
  }]->(subscription)
```

**장점:**
```yaml
✅ 명확: 등급으로 이해
✅ 실용: Guardian이 tier 기반 판단
✅ 확장: tier 추가 가능
✅ 자기 설명: gold = 신뢰
```

### 🎯 제 판단

**Tier 시스템 강력 추천! 🔴 P0**

**이유:**
```yaml
필수성:
  ✅ 신뢰성: Knowledge Graph 품질 핵심
  ✅ Guardian: 평가 시 tier 활용
  ✅ 사용자: 신뢰도 이해 쉬움

구현:
  • tier 필드 추가: 1시간
  • Guardian 통합: 2시간
  
  → 간단하면서 효과 큼!
```

**우선순위:** 🔴 P0 (필수! Knowledge Graph 구현 시 함께)

---

## 5️⃣ RAE 인덱스 승격 (평가 메모리)

### 현재 vs 제안

**현재:**
```python
# 매번 LLM 호출
evaluation = llm.invoke(f"이 가설 평가: {hypothesis}")
```

**제안:**
```python
# 1. 유사 과거 평가 검색
similar_past = rae_index.search(hypothesis)

if similar_past and similar_past[0].score > 0.9:
    # 재사용!
    return similar_past[0].metadata['grade']

# 2. 새로운 케이스만 LLM
evaluation = llm.invoke(...)
rae_index.add(hypothesis, evaluation)  # 저장
```

### 비용 분석

```yaml
시나리오: 100개 가설 평가

현재 (LLM 매번):
  • LLM 호출: 100회
  • 비용: 100 × $0.01 = $1.00
  • 시간: 100 × 2초 = 200초

RAE Index:
  • LLM 호출: 30회 (70% 재사용)
  • 비용: 30 × $0.01 = $0.30
  • 시간: 30 × 2초 + 70 × 0.1초 = 67초
  
  절감: 70% 비용, 66% 시간!
```

### 🎯 제 판단

**매우 실용적! 🔴 P0**

**이유:**
```yaml
효과:
  ✅ 비용: 70% 절감
  ✅ 속도: 66% 단축
  ✅ 일관성: 유사 케이스 동일 평가

구현:
  • rae_index 컬렉션: 1시간
  • Guardian 통합: 2시간
  
  → 간단하면서 ROI 최고!

즉시 효과:
  프로젝트 많을수록 효과 ↑
```

**우선순위:** 🔴 P0 (필수! Guardian 구현 시 함께)

---

## 6️⃣ Overlay 레이어 (Core/Team/Personal)

### 제안 구조

```yaml
Core (UMIS 공식):
  umis_guidelines.yaml
  umis_business_model_patterns.yaml
  → Git 관리, 모두 공유

Team (팀 표준):
  team_patterns.yaml (팀 발견 패턴)
  team_cases.yaml (팀 프로젝트)
  → 팀 저장소

Personal (개인 실험):
  my_experiments.yaml
  my_notes.yaml
  → 로컬만, Git ignore
```

### 충돌 해결

```yaml
우선순위:
  Personal > Team > Core
  
검색:
  1. Personal RAG 검색
  2. 없으면 Team RAG
  3. 없으면 Core RAG
  
추가:
  Personal에서 검증 → Team으로 승격
  Team에서 검증 → Core로 승격
```

### 🎯 제 판단

**좋은 아이디어! 🟡 P1**

**이유:**
```yaml
필요성:
  ✅ 실험: 개인 실험 안전
  ✅ 협업: 팀 지식 공유
  ✅ 표준: 공식 패턴 보호

복잡도:
  • 3-tier 구조: 3일
  • 우선순위 로직: 1일
  
  → 중간 복잡도

시기:
  팀 사용 시작 전에 필요
  지금은 개인만 사용 → 나중에
```

**우선순위:** 🟡 P1 (팀 사용 시작 전)

---

## 7️⃣ Fail-Safe 런타임 모드

### 제안

```yaml
# config.yaml

runtime_mode: hybrid  # yaml_only / hybrid / rag_only

fail_safe:
  vector_rag:
    enabled: true
    fallback: "yaml_only"
    timeout: 5s
  
  knowledge_graph:
    enabled: true
    fallback: "skip_layer"
  
  guardian_monitoring:
    enabled: true
    fallback: "warning_only"
```

### Circuit Breaker

```python
class FailSafeRAG:
    """
    레이어별 독립 비활성화
    """
    
    def search_with_failsafe(self, query):
        try:
            # Layer 1: Vector
            result = self.vector_rag.search(query)
        except Exception as e:
            logger.error(f"Vector RAG 실패: {e}")
            
            if config.fallback == "yaml_only":
                return self.yaml_search(query)
            else:
                raise
        
        try:
            # Layer 3: Graph
            result = self.graph.expand(result)
        except Exception:
            # Graph 실패해도 Vector 결과 반환
            logger.warning("Graph 건너뜀")
        
        return result
```

### 🎯 제 판단

**필수! 🔴 P0**

**이유:**
```yaml
안정성:
  ✅ 부분 실패 허용
  ✅ 전체 시스템 다운 방지
  ✅ 점진적 복구

실용성:
  ✅ OpenAI API 다운 → YAML로
  ✅ Neo4j 다운 → Vector만
  ✅ 프로덕션 필수

구현:
  • Mode toggle: 1시간
  • Circuit breaker: 2시간
  
  → 간단하면서 안정성 ↑
```

**우선순위:** 🔴 P0 (즉시 구현!)

---

## 3️⃣ Routing/Policy YAML 외부화

(위에서 분석했지만 재평가)

### 🎯 제 판단

**매우 좋음! 🟡 P1**

**Cursor 사용자 핵심!**
```yaml
이유:
  ✅ Cursor 사용자가 정책 직접 수정
  ✅ 코드 몰라도 됨
  ✅ 실험 쉬움

구현:
  rag_policy.yaml:
    explorer:
      when: "패턴 매칭 필요"
      layers: [vector, graph]
      timeout: 5s
```

**우선순위:** 🟡 P1 (Cursor 사용자 경험 핵심)

---

## 🎯 우선순위 최종 정리

### 🔴 P0 - 즉시 구현 (필수!)

```yaml
1. Fail-Safe 런타임 모드 ⭐ 최우선!
   이유: 안정성, 프로덕션 필수
   시간: 3시간
   효과: 시스템 다운 방지

2. Schema-Registry & Contract-Test
   이유: 호환성, 진화 가능성
   시간: 2일
   효과: 안전한 확장

3. RAE 인덱스 승격
   이유: 비용 70% 절감, 속도 66% 향상
   시간: 3시간
   효과: ROI 최고

4. Graph Tier 시스템
   이유: Knowledge Graph 품질 핵심
   시간: 3시간
   효과: 신뢰도 관리
```

**총 소요: 3일**

---

### 🟡 P1 - 권장 (중요)

```yaml
5. Routing/Policy YAML 외부화
   이유: Cursor 사용자 경험
   시간: 2일
   효과: 사용자 직접 정책 수정

6. Overlay 레이어 (Core/Team/Personal)
   이유: 팀 협업
   시간: 4일
   효과: 충돌 방지, 실험 안전
```

**총 소요: 6일**

---

### 🟢 P2 - 최적화 (선택)

```yaml
7. Lazy Projection 병행
   이유: 저장 공간 절약
   시간: 3일
   효과: 공간 효율
   
   → 당장 필요 없음 (데이터 적음)
```

---

## 💡 최종 추천 실행 순서

### Week 1 (P0 - 3일)

```
Day 1: Fail-Safe 모드
  • config.yaml (모드 토글)
  • Circuit breaker
  • Fallback 로직
  
  → 시스템 안정성 확보! ⭐

Day 2: Schema-Registry
  • schema_registry.py
  • pytest 추가
  • schema_version 필드
  
  → 호환성 보장!

Day 3: RAE Index + Graph Tier
  • rae_index 컬렉션
  • Guardian 통합
  • Graph tier 시스템
  
  → 비용 절감 + 품질 향상!
```

**3일 후:**
```yaml
달성:
  ✅ 안정성 (Fail-Safe)
  ✅ 호환성 (Schema)
  ✅ 효율성 (RAE)
  ✅ 품질 (Tier)
  
  → 프로덕션 레디! 🎯
```

---

### Week 2 (P1 - 선택)

```
Day 4-5: Routing YAML
  • rag_policy.yaml
  • Policy 엔진
  
Day 6-9: Overlay 레이어
  • Core/Team/Personal 구조
  • 우선순위 로직
```

---

## 🎯 즉시 시작 추천

**1, 2, 3, 4번을 먼저!**

```yaml
이유:
  1. Fail-Safe: 안정성 (프로덕션 필수)
  2. Schema: 호환성 (확장 필수)
  3. RAE: 효율성 (비용 절감)
  4. Tier: 품질 (Graph 필수)

→ 모두 P0! 3일이면 완성!

5, 6번:
  Cursor 사용자 경험 + 팀 협업
  → P1, 나중에
```

---

## 결론

**당신의 제안이 모두 훌륭합니다!**

```yaml
즉시 (P0):
  1. Fail-Safe ⭐ 최우선!
  3. RAE Index
  2. Schema-Registry
  4. Graph Tier

나중 (P1):
  3. Routing YAML
  6. Overlay 레이어

선택 (P2):
  1. Lazy Projection
```

**P0 4개를 먼저 구현하시겠어요?** 🚀

3일이면 프로덕션 레디 시스템 완성입니다!

