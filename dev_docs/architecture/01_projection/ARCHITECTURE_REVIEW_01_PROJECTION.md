# 아키텍처 검토 #1: Projection-at-Retrieval

**질문:** 지연 투영(Lazy Projection) vs 사전 투영(Pre-Projection)?

---

## 🔍 현재 방식 (Pre-Projection)

### 저장 구조

```yaml
배달의민족 사례 → 6개 청크로 분리 저장:
  
  1. observer_baemin_structure (600 토큰)
     "시장 구조 변화 (파편화 → 집중화)..."
  
  2. explorer_baemin_opportunity (800 토큰)
     "플랫폼 비즈니스 모델 실행 전략..."
  
  3. quantifier_baemin_metrics (200 토큰)
     "MAU: 1,000만, 점유율: 60%..."
  
  4. quantifier_baemin_calculation (300 토큰)
     "GMV = MAU × 빈도 × 객단가..."
  
  5. validator_baemin_src001 (250 토큰)
     "SRC_001: Wikipedia..."
  
  6. guardian_baemin_validation (200 토큰)
     "등급 A, 검증 완료..."

총: 2,350 토큰 (6개 청크)
```

### 장점

```yaml
✅ 검색 빠름:
   • agent별 필터링만
   • 재투영 불필요
   • 즉시 사용 가능

✅ 청킹 최적화:
   • agent별 최적 크기
   • Observer: 600 토큰 (구조 요소)
   • Quantifier: 200 토큰 (숫자만)

✅ 간단:
   • 저장 = 검색
   • 로직 단순
```

### 단점

```yaml
❌ 저장 중복:
   • 같은 정보 6번 저장
   • 배달의민족: 2,350 토큰 → 실제 정보는 ~1,500 토큰
   • 중복률: ~56%

❌ 업데이트 복잡:
   • 해지율 추가 시
   • quantifier_baemin_metrics도 수정
   • explorer_baemin_opportunity도 수정
   • guardian_baemin_validation도 수정
   → 3곳 수정! (일관성 위험)

❌ 저장 공간:
   • 30개 사례 × 6-view × 평균 400 토큰
   = 72,000 토큰
   → 디스크: 약 200KB

❌ 벡터 DB 비용:
   • Pinecone 유료 전환 시
   • 청크 수 × 비용
   • 180개 vs 30개 = 6배 비용
```

---

## 💡 제안 방식 (Lazy Projection)

### 저장 구조

```yaml
배달의민족 사례 → 1개 정규화 청크:
  
  chunk_id: "baemin_case_canonical"
  content: """
    # 배달의민족 사례 (정규화)
    
    ## 시장 구조 (Observer)
    파편화 → 집중화, 3면 시장...
    
    ## 기회 전략 (Explorer)
    플랫폼 비즈니스 모델, 양측 확보...
    
    ## 정량 데이터 (Quantifier)
    MAU: 1,000만, 점유율: 60%
    계산: GMV = MAU × ...
    
    ## 출처 (Validator)
    SRC_001: Wikipedia...
    SRC_002: 공식 발표...
    
    ## 검증 (Guardian)
    등급 A, 4명 검증 완료...
  """
  
  metadata:
    source_id: "baemin_case"
    domain: "case_study"
    
    # 섹션 인덱스
    sections:
      observer: {start: 10, end: 25}
      explorer: {start: 27, end: 45}
      quantifier_metrics: {start: 47, end: 55}
      quantifier_calc: {start: 57, end: 65}
      validator: {start: 67, end: 80}
      guardian: {start: 82, end: 90}

총: 1,500 토큰 (1개 청크)
```

### 조회 시 (Lazy Projection)

```python
# Explorer가 검색
results = explorer_retriever.search("플랫폼 기회")

# 1. Vector 검색 (전체 청크 대상)
candidates = vector_search("플랫폼 기회", k=10)

# 2. 후처리: Explorer view 추출
for doc in candidates:
    sections = doc.metadata['sections']
    explorer_section = sections['explorer']
    
    # 해당 섹션만 추출
    doc.page_content = extract_section(
        doc.page_content,
        explorer_section['start'],
        explorer_section['end']
    )
    
    # Explorer 전용 메타데이터 추가
    doc.metadata = filter_for_explorer(doc.metadata)

return projected_docs
```

### 장점

```yaml
✅ 저장 효율:
   • 배달의민족: 1,500 토큰 (1개)
   • vs 2,350 토큰 (6개)
   • 절약: 36%

✅ 업데이트 단순:
   • 해지율 추가
   • 1곳만 수정!
   • 일관성 보장

✅ 확장성:
   • 새 Agent 추가
   • 청크 재생성 불필요
   • 섹션 인덱스만 추가

✅ 비용:
   • Pinecone: 30개 vs 180개
   • 6배 절감!
```

### 단점

```yaml
❌ 검색 복잡:
   • 후처리 필요
   • 섹션 추출 로직
   • 투영 오버헤드

❌ 청킹 제약:
   • 모든 Agent view를 한 청크에
   • 최대 크기 제한
   • Observer(600) + Explorer(800) + ... = 너무 클 수 있음

❌ 검색 품질:
   • Vector는 전체 청크 기준
   • Explorer 섹션만 매칭되어도
   • 전체 청크가 검색됨
   → 정확도 ↓?

❌ 복잡도:
   • 섹션 인덱스 관리
   • 추출 로직
   • 디버깅 어려움
```

---

## 🎯 Hybrid 접근 (최적!)

### 핵심 아이디어

```yaml
작은 청크: Pre-Projection
  • 사례, 메트릭 등 (< 500 토큰)
  • agent별로 분리 저장
  • 검색 빠름, 정확

큰 청크: Lazy Projection
  • 종합 리포트 등 (> 1,000 토큰)
  • 정규화 저장
  • 조회 시 투영
  • 저장 효율

기준:
  if chunk_size < 500:
      strategy = "pre_projection"
  else:
      strategy = "lazy_projection"
```

### 구현

```python
class HybridProjectionRAG:
    """
    크기 기반 Hybrid Projection
    """
    
    def store_chunk(self, canonical_data, agent_views):
        total_size = sum(len(v['content']) for v in agent_views.values())
        
        if total_size < 1500:  # 작은 경우
            # Pre-Projection: agent별 분리 저장
            for agent, view in agent_views.items():
                chunk = Document(
                    page_content=view['content'],
                    metadata={
                        'agent_view': agent,
                        'source_id': canonical_data['id'],
                        ...
                    }
                )
                self.vectorstore.add_documents([chunk])
        
        else:  # 큰 경우
            # Lazy Projection: 정규화 저장 + 섹션 인덱스
            combined = self._combine_views(agent_views)
            chunk = Document(
                page_content=combined['content'],
                metadata={
                    'source_id': canonical_data['id'],
                    'sections': combined['section_index'],
                    'projection_strategy': 'lazy'
                }
            )
            self.vectorstore.add_documents([chunk])
    
    def retrieve(self, query, agent_view):
        results = self.vectorstore.search(query)
        
        # 후처리
        projected = []
        for doc in results:
            if doc.metadata.get('projection_strategy') == 'lazy':
                # Lazy: 섹션 추출
                projected_doc = self._extract_section(doc, agent_view)
            else:
                # Pre: 그대로
                projected_doc = doc
            
            projected.append(projected_doc)
        
        return projected
```

---

## 📊 비교 분석

### 30개 사례 기준

| 방식 | 청크 수 | 토큰 수 | 검색 속도 | 업데이트 | 품질 |
|------|---------|---------|-----------|----------|------|
| **Pre** | 180 | 72,000 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Lazy** | 30 | 45,000 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Hybrid** | 90 | 55,000 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

```yaml
Pre-Projection:
  장점: 검색 빠름, 품질 우수
  단점: 중복, 업데이트 복잡
  
  적합: 작은 사례, 빠른 검색 필요

Lazy Projection:
  장점: 저장 효율, 업데이트 간단
  단점: 검색 느림, 품질 저하
  
  적합: 큰 리포트, 업데이트 빈번

Hybrid (추천!):
  장점: 균형잡힘
  단점: 구현 복잡
  
  적합: 대부분의 경우 ✨
```

---

## 💡 제 최종 추천

### 🎯 Phase별 적용

**Phase 1 (현재 v7.0.0):**
```yaml
방식: Pre-Projection만
이유:
  • 단순함 우선
  • 54개 청크 (작음)
  • 중복 허용 가능
  
  → 프로토타입에 적합! ✅
```

**Phase 2 (확장 시):**
```yaml
방식: Hybrid 전환
조건:
  • 청크 수 > 200개
  • 업데이트 빈번
  • 저장 비용 문제
  
  전환:
    • 작은 청크: Pre (유지)
    • 큰 리포트: Lazy (추가)
```

**Phase 3 (프로덕션):**
```yaml
방식: 완전 Hybrid
최적화:
  • 크기 기준 자동 선택
  • 섹션 인덱스 자동 생성
  • 투영 캐싱
```

---

## 🎯 결론

**당신의 제안이 정확합니다!**

```yaml
문제 인식:
  ✅ 저장 중복 (정확!)
  ✅ 업데이트 복잡성 (정확!)

해결책:
  ✅ Lazy Projection (타당!)
  
  하지만:
    지금은 Pre-Projection 유지
    이유: 단순함, 작은 규모
    
    향후: Hybrid 전환
    시기: 청크 > 200개
```

**추천:**
- 지금: Pre-Projection (단순)
- 설계: Lazy Projection 준비
- 전환: 필요 시점에

**다음 검토:** 2번 (Schema-Registry) 진행할까요? 🚀

