# Tier 3 수정 핵심 요약

---

## 🎯 3가지 핵심 문제

### 1. Config 누락 ✅ 해결됨
```python
# Before: AttributeError
model=self.config.llm_model

# After: settings 사용
model=settings.llm_model
```

### 2. Phase 1 데이터 수집 부족 ⏳ 구현 필요
```python
# Before: 프로젝트 데이터만
available = {'distance': 325}

# After: 5개 출처 통합
available = {
    'distance': 325,          # 프로젝트
    'ktx_speed': 130,         # RAG
    'population': 51000000    # Tier 2
}
```

### 3. LLM 변수 재검색 ⏳ 구현 필요
```python
# Phase 2b: LLM이 제안한 변수 재검색
LLM: "speed 필요" 
  → RAG 재검색: "speed" 
  → 발견: ktx_speed=130
  → Unknown 0개 (재귀 불필요)
```

---

## 🔧 구현 순서

### Phase 1: 데이터 수집 확장

```python
def _phase1_scan(...):
    available = {}
    
    # Step 0: 부모 데이터 (재귀 시)
    # Step 1: 프로젝트 데이터 (최우선)
    # Step 2: RAG 검색 ⭐ 신규
    # Step 3: Tier 2 Source ⭐ 신규
    # Step 4: Context 상수 ⭐ 신규
    
    return {'available': available}
```

**필요 메서드**:
- `_search_rag_benchmarks()` - RAG 벤치마크
- `_query_tier2_sources()` - Tier 2 통계
- `_extract_context_constants()` - 상수

---

### Phase 2b: 반복 개선

```python
def _phase2b_refine_with_data_search(models, ...):
    """LLM 제안 변수 재검색 (최대 2회)"""
    
    for iteration in range(2):
        # 1. Unknown 변수 추출
        unknown_vars = [...]
        
        # 2. 재검색
        newly_found = {}
        for var in unknown_vars:
            data = self._search_for_variable(var)
            if data:
                newly_found[var] = data
        
        # 3. 업데이트
        if not newly_found:
            break
        
        update_models(models, newly_found)
    
    return models
```

**효율성**:
- 반복 2회: 90%+ 커버
- 검색 3-5회 vs 재귀 12-20회
- 절감: 60-75%

---

## 📊 Before vs After

### Before
```
Phase 1: distance=325
Phase 2: LLM → speed 필요
Phase 3: speed 재귀 → Tier 2 → Tier 3...
  → 느림, 비효율
```

### After
```
Phase 1: distance=325, ktx_speed=130 (RAG)
Phase 2: LLM → 둘 다 사용
Phase 3: Unknown 0개
  → 빠름, 효율적
```

---

## ✅ 체크리스트

- [x] Config - settings 통합
- [x] 문서 업데이트
- [ ] Phase 1 RAG 검색
- [ ] Phase 1 Tier 2 조회
- [ ] Phase 1 Context 상수
- [ ] Phase 2b 반복 개선
- [ ] 테스트

---

**상세 문서**:
- `TIER3_ITERATIVE_REFINEMENT.md` - 반복 개선 설계
- `TIER3_FIX_IMPLEMENTATION_PLAN.md` - 구현 계획
- `TIER3_LLM_PROMPT_ANALYSIS.md` - 프롬프트 분석





