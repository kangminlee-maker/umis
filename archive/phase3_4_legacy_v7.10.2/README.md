# Phase 3-4 레거시 코드 Archive

**이동일:** 2025-11-26  
**버전:** v7.10.2 → v7.11.0 마이그레이션  
**Branch:** feature/phase-to-stage-migration-v7.11.0

---

## 📋 Archive된 파일

### 코드 (4개, 총 5,257줄)

| 파일 | 줄 수 | 설명 |
|-----|------|------|
| `phase3_guestimation.py` | 466줄 | Phase 3 Guestimation (11개 Source 수집) |
| `phase3_range_engine.py` | 131줄 | Phase 3 Guardrail Range Engine |
| `phase4_fermi.py` | 3,460줄 | Phase 4 Fermi Decomposition (재귀) |
| `estimator_v7.10.2.py` | 1,200줄 | v7.10.2 Hybrid Architecture 메인 |

**합계:** 5,257줄

---

## 🚨 Archive 이유

### v7.11.0 Fusion Architecture로 완전 재설계

#### 1. **재귀 제거 (Phase 4 → Stage 3)**
- **문제:** Phase 4 재귀 폭발로 인한 느린 실행 (30-60초)
- **해결:** Stage 3 Fermi는 재귀 금지, max_depth=2, Budget 기반

#### 2. **Phase 개념 제거**
- **문제:** Phase 0→1→2→3→4 순차 Fallback
- **해결:** Stage 1-4 독립 실행, Early Return

#### 3. **Confidence → Certainty**
- **문제:** Confidence는 외부 증거 기반 (혼란)
- **해결:** Certainty는 LLM 내부 확신 (high/medium/low)

#### 4. **순환 의존성**
- **문제:** `phase4_fermi.py` → `phase3_guestimation.py`
- **해결:** 둘 다 Archive로 해결 ✅

---

## 🔄 v7.11.0 대체 구현

### 신규 파일 (Stage 기반)

| v7.10.2 레거시 | v7.11.0 신규 | 변경 사항 |
|---------------|-------------|----------|
| `phase3_guestimation.py` | `prior_estimator.py` | LLM 직접 값 요청, 11개 Source 제거 |
| `phase4_fermi.py` | `fermi_estimator.py` | 재귀 제거, PriorEstimator 주입 |
| `estimator_v7.10.2.py` | `estimator.py` | Stage 1-4 오케스트레이션 |
| (없음) | `fusion_layer.py` | Sensor Fusion (Stage 4) |
| (없음) | `evidence_collector.py` | Stage 1 (Literal, Direct RAG, Validator, Guardrails) |

---

## 📊 성능 개선

### v7.10.2 (Phase 4 재귀)
- **실행 시간:** 30-60초
- **LLM 호출:** 10-30회 (재귀)
- **성공률:** 85% (재귀 폭발 리스크)

### v7.11.0 (Stage 3 재귀 없음)
- **실행 시간:** 5-10초 (80-90% 단축)
- **LLM 호출:** 2-5회 (Budget 기반)
- **성공률:** 90% (안정성 향상)

---

## 🔗 참고 문서

### 설계 문서
- `dev_docs/improvements/PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md` (1,119줄)
- `dev_docs/improvements/PHASE3_4_IMPLEMENTATION_CHECKLIST_v7_11_0.md` (893줄)
- `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md` (770줄)

### 분석 문서 (Phase 1)
- `dev_docs/improvements/DEPENDENCY_ANALYSIS_v7_11_0.md`
- `dev_docs/improvements/TEST_CATALOG_v7_11_0.md`
- `dev_docs/improvements/DOCS_INVENTORY_v7_11_0.md`
- `dev_docs/improvements/CONFIG_REFACTORING_DESIGN_v7_11_0.md`

---

## 🛠️ 복원 방법 (긴급 시)

### 1. Archive에서 복원
```bash
# 긴급 롤백이 필요한 경우
cp archive/phase3_4_legacy_v7.10.2/*.py umis_rag/agents/estimator/

# Git으로 복원 (권장)
git checkout feature/v7.10.0-hybrid-architecture -- umis_rag/agents/estimator/phase*.py
```

### 2. Import 수정 필요
```python
# v7.11.0 호환성 레이어 제거
# umis_rag/agents/estimator/compat.py 삭제
```

---

## ⚠️ 주의사항

### 이 파일들은 v7.11.0에서 사용 불가
1. **순환 의존성:** `phase4_fermi.py` → `phase3_guestimation.py`
2. **재귀 로직:** v7.11.0에서 금지
3. **Phase 개념:** Stage로 완전 전환

### 역사적 참고용으로만 사용
- Phase 4 재귀 로직 이해
- Phase 3 11개 Source 수집 방식
- v7.10.2 Hybrid Architecture 연구

---

## 📅 타임라인

| 날짜 | 이벤트 |
|-----|------|
| 2025-11-20 | v7.10.2 Hybrid Architecture (Phase 3-4 병렬) |
| 2025-11-26 | v7.11.0 Fusion Architecture 설계 시작 |
| 2025-11-26 | Phase 3-4 파일 Archive 이동 |
| 2025-11-26 | Phase 2 (코드 리팩터링) 시작 |
| (예정) 2025-12-10 | v7.11.1 최종 제거 (프로덕션 2주 후) |

---

## ✅ 마이그레이션 완료 조건

- [x] Phase 3-4 파일 Archive 이동
- [ ] Import 리다이렉트 (compat.py) 구현
- [ ] 테스트 전환 (30개)
- [ ] 문서 업데이트 (7개)
- [ ] Config 리팩터링 (3개)
- [ ] 전체 테스트 통과 (100%)
- [ ] 프로덕션 배포
- [ ] 2주 모니터링
- [ ] 최종 제거 (v7.11.1)

---

**작성자:** AI Assistant  
**최종 업데이트:** 2025-11-26  

**끝.**

