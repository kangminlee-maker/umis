# Archive: benchmarks v7.10.2

**보관 일자**: 2025-11-26
**이유**: v7.11.0 Fusion Architecture - Phase 4 → Stage 3 Fermi로 대체

---

## 📁 구조

```
archive/benchmarks_v7.10.2/
├── phase4/ (Phase 4 벤치마크 전체)
│   ├── tests/ (49개 테스트)
│   ├── results/ (8개 JSON 결과)
│   ├── analysis/ (분석 문서 2개)
│   ├── scenarios.py
│   ├── common.py
│   └── README.md
├── MODEL_CONFIG_DESIGN.md
├── MODEL_CONFIG_TEST_RESULTS.md
├── PHASE4_IMPROVEMENT_PLAN.md
├── PHASE4_IMPROVEMENTS_SUMMARY.md
├── PHASE4_INTEGRATION_COMPLETE.md
├── PHASE4_INTEGRATION_FINAL.md
├── PHASE1_COMPLETION_REPORT.md
├── MIGRATION_PLAN.md
└── README.md (이 파일)
```

---

## 🎯 Phase 4 Architecture

### 구조
```
Phase 4: Fermi Decomposition (재귀적 분해)
  ├─ 재귀 깊이: max_depth=4
  ├─ 변수 탐색: 무제한
  └─ 실행 시간: 10-30초
```

### 주요 특징
- 재귀적 변수 분해
- 동적 깊이 제어
- PhaseConfig 기반 설정

---

## 🔄 v7.11.0 변경사항

### Architecture 변경
| 항목 | v7.10.2 Phase 4 | v7.11.0 Stage 3 |
|------|-----------------|-----------------|
| 구조 | Fermi Decomposition (재귀) | Fermi (재귀 없음) |
| 깊이 | max_depth=4 | max_depth=2 (고정) |
| 변수 추정 | 재귀 호출 | GenerativePrior (Stage 2) 호출 |
| 제어 | PhaseConfig | Budget |
| 속도 | 10-30초 | 3-5초 |

### 성능 개선
- **속도**: 3-10배 향상
- **예측 가능성**: 재귀 제거 → 실행 시간 명확
- **비용**: LLM 호출 50% 감소

---

## 📚 주요 문서

### Phase 4 구현
- `phase4/README.md` - Phase 4 전체 설명
- `PHASE4_INTEGRATION_COMPLETE.md` - 통합 완료 보고서
- `PHASE4_IMPROVEMENTS_SUMMARY.md` - 개선사항 요약

### Model Config
- `MODEL_CONFIG_DESIGN.md` - 설계
- `MODEL_CONFIG_TEST_RESULTS.md` - 테스트 결과

### 마이그레이션
- `MIGRATION_PLAN.md` - Phase 5 → Fusion 계획

---

## 🧪 테스트 (49개)

### Batch 테스트
- `batch1.py` - 5개 문제 (기본)
- `batch2.py` - 5개 문제 (중급)
- `batch3.py` - 5개 문제 (고급)
- `batch4.py` - 3개 문제 (중간 노력)
- `batch5.py` - 2개 문제 (낮은 노력)

### Extended 테스트
- `extended_10problems.py` - 10문제 Fermi (확장)

### Model 테스트
- `test_o1_mini.py` - O1-mini 모델
- `test_gpt51_*.py` - GPT-5.1 시리즈
- `test_responses_api_*.py` - Responses API
- 기타 18개 모델 테스트

### 통합 테스트
- `test_comprehensive_api.py` - API 통합
- `test_all_improvements.py` - 전체 개선사항

---

## ⚠️ 주의사항

### 이 벤치마크는 Archive입니다
- v7.11.0에서 더 이상 유효하지 않습니다
- 히스토리 참고용으로만 사용하세요
- 새 벤치마크는 `benchmarks/estimator/README.md` 참조

### v7.11.0 새 벤치마크
Stage 3 (Fermi) 벤치마크:
- 재귀 없음 검증
- Budget 제어 검증
- max_depth=2 검증
- GenerativePrior 통합 검증

---

## 📞 문의

**v7.11.0 관련**:
- 문서: `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md`
- GitHub Issues: https://github.com/kangminlee-maker/umis/issues

**Archive 복원**:
- Git history에서 복원 가능

---

**보관**: 2025-11-26
**Phase 4 Fermi → Stage 3 Fermi (Non-recursive)** 🎉
