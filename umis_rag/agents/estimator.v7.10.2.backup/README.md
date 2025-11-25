# Estimator Agent 구조

**v7.7.0** | 5,200줄, 14개 파일 | 다른 Agent의 8-17배 복잡도

---

## 왜 폴더로 분리?

다른 Agent: 295-659줄 (단일 파일)  
Estimator: 5,200줄 (모듈화 필수)

---

## 폴더 구조

```
estimator/
├── estimator.py       (520줄) - 메인 API (5-Phase)
├── models.py          (518줄) - 데이터 모델
│
├── tier1.py           (320줄) - Phase 1 구현 (<0.5초)
├── tier2.py           (650줄) - Phase 3 구현 (3-8초)
├── tier3.py         (2,500줄) - Phase 4 구현 (10-30초, Step 1-4)
│
├── judgment.py        (240줄) - 판단 로직
├── source_collector.py(232줄) - Source 수집
├── rag_searcher.py    (191줄) - RAG 검색
├── learning_writer.py (564줄) - 학습 시스템
├── boundary_validator.py - Boundary 검증
│
└── sources/           (868줄)
    ├── physical.py    (254줄) - 물리 법칙
    ├── soft.py        (215줄) - 통계/법률
    └── value.py       (354줄) - 데이터/LLM/웹
```

---

## 5-Phase Architecture (v7.7.0)

### 용어 정의
- **Tier**: 구현 파일명만 (tier1.py, tier2.py, tier3.py)
- **Phase**: Estimator 전체 프로세스 단계 (0-4)
- **Step**: Phase 4 (Fermi) 내부 세부 단계 (1-4)

### 전체 구조

| Phase | 속도 | 커버리지 | 방식 | 파일 |
|-------|------|---------|------|------|
| 0 | <0.1초 | 10% | 프로젝트 데이터 | estimator.py |
| 1 | <0.5초 | 5%→40% | 학습 규칙 (Direct RAG) | tier1.py |
| 2 | <1초 | 85%→50% | Validator 검색 | estimator.py |
| 3 | 3-8초 | 2-5% | 11개 Source (Guestimation) | tier2.py |
| 4 | 10-30초 | 3%→1% | Fermi 분해 (Step 1-4) | tier3.py |

### Phase 4 내부 (Step 1-4)

```
Phase 4: Fermi Decomposition (tier3.py)
  ├─ Step 1: 초기 스캔 (Bottom-up)
  ├─ Step 2: 모형 생성 (Top-down, 3-5개)
  ├─ Step 3: 실행 가능성 체크 (재귀)
  └─ Step 4: 모형 실행 (Backtracking)
```

진화: 사용↑ → Phase 1 규칙↑ → 속도 6-16배↑

---

## 사용

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("B2B SaaS Churn Rate는?")
# → EstimationResult(value, phase, reasoning_detail, confidence)
```

상세: `umis_core.yaml` (Line 609-743)

---

## v7.7.0 변경사항

### Native 모드 구현
- Explorer Native/External 분기 구현
- LLMProvider 클래스 추가
- 비용 $0 (Cursor LLM 직접 사용)

### 용어 명확화
- ❌ Deprecated: 3-Tier Architecture
- ✅ Current: 5-Phase Architecture
- ✅ Fermi 내부: Step 1-4
- ✅ Phase/Step 혼란 해결
