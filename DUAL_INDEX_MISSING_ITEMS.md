# Dual-Index 미구현 항목 분석

**날짜:** 2024-11-03  
**확인:** Chroma Collections 실제 확인 완료

---

## 📊 현재 Chroma 상태

```yaml
실제 Collections:
  ✅ explorer_knowledge_base: 354개 (기존 Vector RAG)
  ✅ goal_memory: 5개 (Week 4)
  ✅ rae_index: 4개 (개선사항)
  ✅ query_memory: 15개 (Week 4)

미생성 Collections:
  ❌ canonical_index: 없음
  ❌ projected_index: 없음

결론:
  Dual-Index 코드만 존재, 실제 데이터 미생성
```

---

## ❌ 미구현 항목 (3개)

### 1. Canonical Index 데이터 생성 ❌

```yaml
현재 상태:
  빌더: ✅ build_canonical_index.py (220줄)
  데이터: ❌ Collection 없음
  사용: ❌ 미사용

필요한 작업:
  
  실행:
    python scripts/build_canonical_index.py
  
  예상 결과:
    • canonical_index Collection 생성
    • 13개 CAN-xxx 청크
    • anchor_path + content_hash
    • Lineage 정보
  
  API 사용:
    • OpenAI Embeddings (13개 호출)
    • 비용: ~$0.01

소요: 30분 (API 대기 포함)
우선순위: P0 (핵심)
```

### 2. Projected Index 데이터 생성 ❌

```yaml
현재 상태:
  빌더: ✅ build_projected_index.py (129줄)
  데이터: ❌ Collection 없음
  사용: ❌ 미사용

필요한 작업:
  
  선행:
    Canonical Index 생성 먼저 필요
  
  실행:
    python scripts/build_projected_index.py
  
  예상 결과:
    • projected_index Collection 생성
    • ~65개 PRJ-xxx 청크 (13 × 5 agents)
    • TTL 메타데이터
    • Agent별 분리
  
  API 사용:
    • Embeddings (65개 호출)
    • LLM 판단 (~6회, 10%)
    • 비용: ~$0.05

소요: 30분 (API 대기 포함)
우선순위: P0 (핵심)
```

### 3. TTL 실제 동작 ❌

```yaml
현재 상태:
  메타데이터: ✅ 정의됨 (hybrid_projector.py)
  동작 로직: ❌ 없음
  
  정의된 필드:
    • strategy: 'on_demand'
    • cache_ttl_hours: 24
    • last_materialized_at: timestamp
    • access_count: 0

필요한 구현:
  
  파일 (신규):
    umis_rag/projection/ttl_manager.py (200줄)
  
  기능:
    1. check_expiration(projected_id)
       • last_materialized_at + 24시간 체크
       • 만료 여부 반환
    
    2. should_regenerate(projected_id)
       • TTL 만료 or 데이터 없음
       • 재생성 필요 여부
    
    3. regenerate_on_demand(canonical_id, agent)
       • Canonical → Projected 즉시 투영
       • 새 PRJ-xxx 생성
    
    4. cleanup_expired()
       • 만료된 Projected 청크 삭제
       • 저장 공간 확보
    
    5. update_access_count(projected_id)
       • 검색 시 access_count++
       • 고빈도 → persist_profile 설정
  
  통합:
    • Explorer 검색 시 TTL 체크
    • 만료 시 자동 재생성
    • 주기적 cleanup (선택)

소요: 3시간
우선순위: P0 (비용 절감)
효과: 저장 비용 관리, 최신 유지
```

---

## 🎯 구현 순서 (총 4시간)

### Step 1: Canonical Index 생성 (30분) ⭐⭐⭐⭐⭐

```bash
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate
python scripts/build_canonical_index.py
```

**효과:**
- CAN-xxx 13개 생성
- anchor_path + content_hash 적용
- Dual-Index 기반 마련

### Step 2: Projected Index 생성 (30분) ⭐⭐⭐⭐⭐

```bash
python scripts/build_projected_index.py
```

**효과:**
- PRJ-xxx ~65개 생성
- Agent별 분리
- Dual-Index 활성화 (75%)

### Step 3: Explorer 통합 (30분) ⭐⭐⭐⭐

```python
# umis_rag/agents/explorer.py 수정
# use_projected=True로 변경하여 projected_index 사용
```

**효과:**
- Explorer가 Dual-Index 사용
- 품질 vs 일관성 개선

### Step 4: TTL Manager 구현 (3시간) ⭐⭐⭐

```python
# umis_rag/projection/ttl_manager.py 신규 작성
# 만료 체크, 재생성, cleanup 로직
```

**효과:**
- 저장 비용 절감
- 자동 캐시 관리
- 완전한 Dual-Index (100%)

---

## 💡 즉시 실행 권장

```yaml
최소 구현 (1시간):
  Step 1 + Step 2
  → Dual-Index 데이터 생성
  → 75% 완성, 즉시 사용 가능

완전 구현 (4시간):
  Step 1 + Step 2 + Step 3 + Step 4
  → Dual-Index 100% 완성
  → TTL 자동 관리

권장:
  최소한 Step 1+2는 즉시 실행! (1시간)
  → Dual-Index 활성화의 핵심
```

---

Dual-Index 데이터를 지금 생성하시겠어요? (1시간 소요)

**Yes: Canonical + Projected Index 생성하자** (권장!)  
**No: TTL Manager부터 구현하자**  
**Skip: 현재 상태 유지** (explorer_knowledge_base 사용)
