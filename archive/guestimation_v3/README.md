# Guestimation v3 Archive

**Deprecated**: 2025-11-20  
**Version**: v7.7.0 이전  
**Reason**: Estimator로 진화하면서 Tier 시스템 변경

---

## 📦 보관된 파일

### Tier 테스트 파일 (4개)
- `test_tier1_guestimation.py` - Tier 1 FastPath 테스트
- `test_tier2_guestimation.py` - Tier 2 Judgment 테스트
- `test_tier3_basic.py` - Tier 3 기본 동작 테스트
- `test_tier3_business_metrics.py` - Tier 3 비즈니스 지표 테스트

### Fermi & Learning 테스트 (3개)
- `test_fermi_model_search.py` - Fermi 모델 검색 테스트
- `test_learning_e2e.py` - E2E 학습 플로우 테스트
- `test_learning_writer.py` - Learning Writer 테스트

### Phase 테스트 (3개)
- `test_phase2_enhanced.py` - Phase 2 Enhanced 테스트
- `test_phase3_models.py` - Phase 3 모델 테스트
- `test_single_source_policy.py` - Single Source 정책 테스트

### 기타 (1개)
- `test_quantifier_v3.py` - Quantifier v3 통합 테스트
- `test_model_router.py` - 모델 라우터 테스트 (존재 시)

---

## 🔄 변경 사항

### v7.7.0에서 변경된 내용
- **Tier 1-3 시스템 → 5-Phase Architecture**
  - Phase 0: Direct (기본 계산)
  - Phase 1: Native (RAG만)
  - Phase 2: Validator Search (데이터 검색)
  - Phase 3: LLM Judgment (판단)
  - Phase 4: Fermi Decomposition (분해)

- **Guestimation → Estimator**
  - 통합된 EstimatorRAG 인터페이스
  - 자동 Phase 선택
  - 학습 시스템 개선

---

## 📚 참고 문서

### 새로운 시스템 (v7.7.0+)
- `umis_rag/agents/estimator/` - 새로운 Estimator 구현
- `docs/guides/ESTIMATOR_GUIDE.md` - Estimator 사용 가이드
- `dev_docs/estimator/` - Estimator 개발 문서

### 아키텍처 변경
- Tier 시스템 → Phase 시스템
- Built-in Rules → Canonical Store
- Learning Writer → 자동 학습

---

## ⚠️ 주의사항

이 파일들은 **동작하지 않을 수 있습니다**:
- 의존하는 코드가 변경됨
- 테스트 대상이 deprecated됨
- 참조 문서가 업데이트됨

**복구가 필요한 경우**:
1. 해당 파일만 scripts/로 복사
2. import 경로 수정 필요 가능성
3. 테스트 케이스 업데이트 필요 가능성

---

**Archive 날짜**: 2025-11-20  
**Last Update**: v7.7.0


