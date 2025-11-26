# Archive: dev_docs v7.10.2 and Below

**보관 일자**: 2025-11-26
**이유**: v7.11.0 Fusion Architecture 마이그레이션 완료

---

## 📁 구조

```
archive/dev_docs_v7.10.2_and_below/
├── improvements/
│   ├── v7_8_x/     (6개 문서)
│   ├── v7_9_x/     (7개 문서)
│   └── v7_10_x/    (14개 문서)
└── README.md
```

---

## 📊 버전별 히스토리

### v7.8.x (2024 Q4)
**주요 특징**:
- Native/External 모드 통합
- Model Config 시스템 도입
- Phase 4 테스트 개선

**문서 (6개)**:
- NATIVE_EXTERNAL_LEGACY_REMOVAL_v7_8_1.md
- NATIVE_EXTERNAL_LEGACY_REMOVAL_COMPLETE_v7_8_1.md
- PHASE_0_4_TEST_RESULTS_v7_8_1.md
- PHASE_3_4_IMPROVEMENTS_v7_8_1.md
- SOURCE_TYPE_FIX_v7_8_1.md
- V7_8_1_LEGACY_REMOVAL_COMPLETE_SUMMARY.md

### v7.9.0 (2025 Q1)
**주요 특징**:
- Phase 0-2 완료
- Production Quality Roadmap
- Phase 3 계획

**문서 (7개)**:
- PHASE_0_COMPLETE_v7_9_0.md
- PHASE_1_COMPLETE_v7_9_0.md
- PHASE_2_COMPLETE_v7_9_0.md
- PHASE_2_PROGRESS_v7_9_0.md
- PHASE_3_PLAN_v7_9_0.md
- PRODUCTION_QUALITY_ROADMAP_v7_9_0.md
- PRODUCTION_QUALITY_ROADMAP_COMPLETE_v7_9_0.md ⭐

### v7.10.x (2025 Q1-Q2)
**주요 특징**:
- Hybrid Architecture 실험
- Phase 0-4 Redesign
- Benchmark 패턴 분석

**문서 (14개)**:
- BENCHMARK_PATTERNS_FOR_PHASE_0_4.md
- FEEDBACK_REVIEW_v7_10_0.md
- HYBRID_ARCHITECTURE_EXPLAINED.md
- HYBRID_ARCHITECTURE_SUMMARY_v7_10_0.md
- PHASE_0_4_FINAL_SYNTHESIS_v7_10_0.md
- PHASE_0_4_REDESIGN_ANALYSIS_v7_10_0.md
- PHASE0_TASK1_COMPLETED.md
- PHASE0_TASK2_COMPLETED.md
- WEEK1_COMPLETE_v7_10_0.md
- WEEK1_SUMMARY_v7_10_0.md
- WEEK2_FINAL_STATUS_v7_10_0.md
- WEEK2_PROGRESS_v7_10_0.md
- YAML_REVIEW_v7_10_0.md
- estimator_work_domain_v7_10_0.yaml

---

## 🔄 v7.11.0 변경사항

### Architecture 변경
| 항목 | v7.10.2 | v7.11.0 |
|------|---------|---------|
| 구조 | Phase 0-4 (5단계) | Stage 1-4 (4단계) |
| 재귀 | Phase 4 (max_depth=4) | 없음 (max_depth=2) |
| 제어 | PhaseConfig | Budget |
| 확신도 | confidence (0.0-1.0) | certainty (high/medium/low) |

### 성능 개선
- **속도**: 3-10배 향상 (10-30초 → 3-5초)
- **비용**: LLM 호출 50% 감소
- **예측 가능성**: 재귀 제거로 실행 시간 명확

### 용어 개선
- `phase` → `source` (추정 소스)
- `confidence` → `certainty` (LLM 확신도)
- `PhaseConfig` → `Budget` (자원 제어)

---

## 📚 현재 버전 문서

**v7.11.0 핵심 문서**:
- `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md` ⭐ 최종 보고서
- `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md`
- `docs/api/ESTIMATOR_API_v7_11_0.md`
- `docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md`

---

## ⚠️ 주의사항

### 이 문서들은 Archive입니다
- v7.11.0에서 **더 이상 유효하지 않습니다**
- 히스토리 참고용으로만 사용하세요
- 새 기능 구현 시 v7.11.0 문서를 참조하세요

### 하위 호환성
- `umis_rag/agents/estimator/compat.py`를 통해 Phase 3-4 API 지원
- `DeprecationWarning` 발생
- 향후 제거 예정 (프로덕션 배포 후 1-2주)

---

## 📞 문의

**v7.11.0 관련 질문**:
- 문서: `dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md`
- GitHub Issues: https://github.com/kangminlee-maker/umis/issues

**Archive 복원 필요 시**:
- Git history에서 복원 가능
- Commit: `[문서 정리 커밋 해시]`

---

**보관**: 2025-11-26
**v7.11.0 마이그레이션 완료 기념** 🎉
