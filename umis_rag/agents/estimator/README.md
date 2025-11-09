# Estimator Agent 구조

**v7.5.0** | 5,200줄, 14개 파일 | 다른 Agent의 8-17배 복잡도

---

## 왜 폴더로 분리?

다른 Agent: 295-659줄 (단일 파일)  
Estimator: 5,200줄 (모듈화 필수)

---

## 폴더 구조

```
estimator/
├── estimator.py       (337줄) - 메인 API
├── models.py          (518줄) - 데이터 모델
│
├── tier1.py           (320줄) - 규칙 (<0.5초)
├── tier2.py           (427줄) - 맥락 판단 (3-8초)
├── tier3.py         (1,463줄) - Fermi 분해 (10-30초)
│
├── judgment.py        (240줄) - 판단 로직
├── source_collector.py(232줄) - Source 수집
├── rag_searcher.py    (191줄) - RAG 검색
├── learning_writer.py (564줄) - 학습
│
└── sources/           (868줄)
    ├── physical.py    (254줄) - 물리 법칙
    ├── soft.py        (215줄) - 통계/법률
    └── value.py       (354줄) - 데이터/LLM/웹
```

---

## 3-Tier 아키텍처

| Tier | 속도 | 커버리지 | 방식 |
|------|------|---------|------|
| 1 | <0.5초 | 45%→95% | 규칙 매칭 (학습) |
| 2 | 3-8초 | 50%→5% | 11개 Source + 판단 |
| 3 | 10-30초 | 5%→0.5% | 재귀 분해 (12개 지표) |

진화: 사용↑ → Tier 1 규칙↑ → 속도 6-16배↑

---

## 사용

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("B2B SaaS Churn Rate는?")
# → EstimationResult(value, tier, reasoning_detail, confidence)
```

상세: `umis_core.yaml` (Line 608-693)
