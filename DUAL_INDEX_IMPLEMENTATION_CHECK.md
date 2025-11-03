# Dual-Index 구현 현황 상세 체크

**날짜:** 2024-11-03  
**목적:** Dual-Index Modular RAG 미구현 항목 확인

---

## 📊 구현 현황 요약

```yaml
전체 완성도: 75%

구현됨 (75%):
  ✅ Canonical Index 빌더 (100%)
  ✅ Projected Index 빌더 (100%)
  ✅ Hybrid Projection 로직 (100%)
  ✅ Learning Loop (100%)
  ✅ schema_registry.yaml (100%)
  🟡 TTL 메타데이터 (50% - 정의만)

미구현 (25%):
  ❌ TTL 실제 동작 (0%)
     - 만료 체크
     - 자동 재생성
     - 캐시 관리
  
  ❌ 실제 데이터 생성 (0%)
     - Canonical Index 데이터 없음
     - Projected Index 데이터 없음
```

---

## 📦 상세 구현 현황

### 1. Canonical Index ✅/❌

```yaml
빌더 코드: ✅ 완성
  파일: scripts/build_canonical_index.py (220줄)
  
  기능:
    ✅ YAML 파일 로드
    ✅ CAN-xxxxxxxx ID 생성
    ✅ anchor_path + content_hash
    ✅ sections 추출
    ✅ Lineage 생성
    ✅ Chroma 저장 로직

실제 데이터: ❌ 미생성
  확인:
    $ ls data/chroma/
    → canonical_index Collection 없음
  
  이유:
    빌더 코드는 있지만 실행하지 않음
  
  실행 명령:
    python scripts/build_canonical_index.py

완성도: 코드 100%, 데이터 0%
```

### 2. Projected Index ✅/❌

```yaml
빌더 코드: ✅ 완성
  파일: scripts/build_projected_index.py (129줄)
  
  기능:
    ✅ Canonical → Projected 변환
    ✅ HybridProjector 사용
    ✅ PRJ-xxxxxxxx ID 생성
    ✅ Agent별 분리
    ✅ Chroma 저장 로직

실제 데이터: ❌ 미생성
  확인:
    $ ls data/chroma/
    → projected_index Collection 없음
  
  이유:
    Canonical Index 선행 필요
  
  실행 순서:
    1. build_canonical_index.py
    2. build_projected_index.py

완성도: 코드 100%, 데이터 0%
```

### 3. Hybrid Projection ✅

```yaml
로직: ✅ 완성
  파일: umis_rag/projection/hybrid_projector.py (211줄)
  
  기능:
    ✅ 규칙 기반 투영 (90%)
    ✅ LLM 판단 (10%)
    ✅ LLM 로그 저장
    ✅ Projected 청크 생성
    ✅ TTL 메타데이터 포함

완성도: 100%
```

### 4. Learning Loop ✅

```yaml
로직: ✅ 완성
  파일: umis_rag/learning/rule_learner.py (300줄)
  
  기능:
    ✅ 로그 분석
    ✅ 패턴 추출
    ✅ 규칙 생성
    ✅ YAML 출력

완성도: 100%
```

### 5. TTL (Time-To-Live) 🟡/❌

```yaml
메타데이터 정의: ✅ 완성
  위치: hybrid_projector.py (160-167줄)
  
  내용:
    materialization:
      strategy: 'on_demand'
      cache_ttl_hours: 24
      persist_profile: None
      last_materialized_at: timestamp
      access_count: 0

실제 동작: ❌ 미구현

필요한 기능:
  ❌ TTL 만료 체크 로직
     • last_materialized_at + 24시간 비교
     • 만료 시 삭제 또는 재생성
  
  ❌ 온디맨드 재생성
     • 검색 시 없으면 즉시 생성
     • Canonical → Projected 자동 투영
  
  ❌ 캐시 관리
     • access_count 증가
     • 고빈도 → persist_profile 설정

미구현 파일:
  ❌ umis_rag/projection/ttl_manager.py

완성도: 메타데이터 100%, 동작 0%
```

---

## ❌ 미구현 항목 상세

### TTL 실제 동작 (0%)

```yaml
현재:
  • TTL 메타데이터만 저장됨
  • 실제 만료 체크 없음
  • 자동 재생성 없음

필요한 구현:
  
  1. TTLManager 클래스
     파일: umis_rag/projection/ttl_manager.py
     
     기능:
       • check_expiration(projected_id)
       • should_regenerate(projected_id)
       • regenerate_on_demand(canonical_id, agent)
       • cleanup_expired()
       • update_access_count(projected_id)
  
  2. 통합
     • Explorer 검색 시 TTL 체크
     • 만료된 청크 자동 재생성
     • 주기적 cleanup (cron)
  
  3. 설정
     runtime_config.yaml에 추가:
       ttl:
         enabled: true
         check_on_search: true
         auto_cleanup: true
         cleanup_interval_hours: 6

소요 예상: 3시간

효과:
  • 저장 비용 절감
  • 최신 데이터 유지
  • 자동 관리
```

### Canonical/Projected Index 실제 데이터 (0%)

```yaml
현재:
  • 빌더 코드는 존재
  • 실행하지 않음
  • Chroma에 Collection 없음

확인:
  $ cd data/chroma
  $ ls -la
  → canonical_index/ 폴더 없음
  → projected_index/ 폴더 없음

원인:
  • Week 2에서 코드만 작성
  • 실제 실행은 안 함

필요한 작업:
  
  1. Canonical Index 생성
     명령: python scripts/build_canonical_index.py
     소요: OpenAI API 사용 (Embedding)
     결과: ~13개 CAN-xxx 청크
  
  2. Projected Index 생성
     명령: python scripts/build_projected_index.py
     소요: 추가 Embedding + LLM 판단
     결과: ~65개 PRJ-xxx 청크 (13 × 5 agents)
  
  3. Learning Loop 실행
     명령: python scripts/learn_projection_rules.py
     결과: learned_projection_rules.yaml

소요 예상: 1시간 (API 호출 시간 포함)

효과:
  • Dual-Index 완전 활성화
  • 품질 vs 일관성 Trade-off 실현
```

---

## 🎯 구현 우선순위

### Phase A: 데이터 생성 (1시간) ⭐⭐⭐⭐⭐

```yaml
작업:
  1. Canonical Index 생성
     python scripts/build_canonical_index.py
  
  2. Projected Index 생성
     python scripts/build_projected_index.py
  
  3. 검증
     • canonical_index Collection 확인
     • projected_index Collection 확인
     • 청크 수 확인

소요: 1시간
필요성: 높음 (Dual-Index 활성화)
효과: 즉시 사용 가능

권장: ✅ 즉시 실행!
```

### Phase B: TTL 동작 구현 (3시간) ⭐⭐⭐

```yaml
작업:
  1. TTLManager 클래스 (2시간)
     umis_rag/projection/ttl_manager.py
     
     기능:
       • check_expiration()
       • regenerate_on_demand()
       • cleanup_expired()
       • update_access_count()
  
  2. Explorer 통합 (30분)
     • 검색 시 TTL 체크
     • 만료 시 재생성
  
  3. 테스트 (30분)
     • TTL 만료 시뮬레이션
     • 재생성 확인

소요: 3시간
필요성: 중간 (비용 절감)
효과: 저장 비용 관리

권장: 📋 선택 (Phase A 후)
```

### Phase C: 최적화 (선택)

```yaml
작업:
  • 고빈도 청크 프로파일링
  • persist_profile 자동 설정
  • 캐시 전략 고도화

소요: 2시간
필요성: 낮음
효과: 세밀한 비용 관리

권장: ⏸️ 향후
```

---

## 💡 즉시 실행 가능한 명령어

### Dual-Index 데이터 생성

```bash
# 1. Canonical Index 생성
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate
python scripts/build_canonical_index.py

# 예상 결과:
#   ✅ canonical_index Collection 생성
#   📊 Documents: 13개
#   🔑 ID: CAN-xxxxxxxx

# 2. Projected Index 생성
python scripts/build_projected_index.py

# 예상 결과:
#   ✅ projected_index Collection 생성
#   📊 Documents: 65개
#   🔑 ID: PRJ-xxxxxxxx
#   ⏰ TTL: 24시간

# 3. 검증
python -c "
import chromadb
client = chromadb.PersistentClient('data/chroma')
print('Collections:', [c.name for c in client.list_collections()])
"

# 예상 출력:
#   Collections: ['explorer_knowledge_base', 'canonical_index', 'projected_index', ...]
```

---

## 📊 구현 후 예상 상태

### Before (현재)

```yaml
Dual-Index:
  코드: ✅ 100%
  데이터: ❌ 0%
  TTL 동작: ❌ 0%
  
  완성도: 33%

사용:
  Explorer → explorer_knowledge_base (기존)
  Dual-Index 미사용
```

### After (Phase A 완료)

```yaml
Dual-Index:
  코드: ✅ 100%
  데이터: ✅ 100%
  TTL 동작: 🟡 메타만
  
  완성도: 75%

사용:
  Explorer → canonical_index / projected_index
  Dual-Index 활성화
  품질 vs 일관성 개선
```

### After (Phase A + B 완료)

```yaml
Dual-Index:
  코드: ✅ 100%
  데이터: ✅ 100%
  TTL 동작: ✅ 100%
  
  완성도: 100%

사용:
  자동 캐시 관리
  비용 최적화
  온디맨드 재생성
```

---

## 🎯 권장사항

### 즉시 실행 (1시간)

```yaml
Phase A: 데이터 생성

명령:
  python scripts/build_canonical_index.py
  python scripts/build_projected_index.py

효과:
  ✅ Dual-Index 활성화 (33% → 75%)
  ✅ Canonical/Projected 분리 실현
  ✅ 품질 vs 일관성 개선

필요성: ⭐⭐⭐⭐⭐
권장: 즉시!
```

### 선택 구현 (3시간)

```yaml
Phase B: TTL 동작

파일:
  umis_rag/projection/ttl_manager.py (신규, 200줄)

효과:
  ✅ 저장 비용 절감
  ✅ 자동 캐시 관리
  ✅ 온디맨드 재생성

필요성: ⭐⭐⭐
권장: Phase A 후 선택
```

---

## 📋 체크리스트

```yaml
Dual-Index 완성을 위한 체크리스트:

✅ 코드 구현:
  ✅ build_canonical_index.py
  ✅ build_projected_index.py
  ✅ hybrid_projector.py
  ✅ schema_registry.yaml
  ✅ projection_rules.yaml
  ✅ Learning Loop

❌ 데이터 생성:
  ❌ Canonical Index Collection
  ❌ Projected Index Collection
  ❌ 실제 CAN-xxx 청크
  ❌ 실제 PRJ-xxx 청크

🟡 TTL 구현:
  ✅ TTL 메타데이터 정의
  ❌ TTL 만료 체크 로직
  ❌ 온디맨드 재생성 로직
  ❌ 캐시 관리 로직
```

---

**작성:** UMIS Team  
**날짜:** 2024-11-03  
**권장:** Phase A 데이터 생성 즉시 실행!


