# Deprecated 파일 목록

**작성일**: 2025-11-07  
**이유**: Guestimation v3.0으로 대체  
**조치**: archive/guestimation_v1_v2/ 이동

---

## 📋 이동할 파일

### 코어 모듈 (3개)

```
umis_rag/utils/multilayer_guestimation.py (1,030줄)
  - Multi-Layer v2.1
  - 문제: Sequential Fallback (판단 없음)
  - 대체: guestimation_v3/tier2.py

umis_rag/utils/guestimation.py (415줄)
  - Guestimation v1.0
  - 비교 가능성 검증
  - 대체: guestimation_v3/sources/value.py (RAGBenchmarkSource)

umis_rag/core/multilayer_config.py
  - Multi-Layer v2.1 설정 로더
  - 대체: Tier2Config, Tier1Config
```

### 설정 파일 (1개)

```
config/multilayer_config.yaml
  - Multi-Layer v2.1 설정
  - 대체: 필요 없음 (코드에 내장)
```

### 테스트 파일 (4개)

```
scripts/test_multilayer_guestimation.py
  - Multi-Layer v2.1 테스트
  - 대체: test_tier2_guestimation.py

scripts/test_quantifier_multilayer.py
  - Quantifier + Multi-Layer 통합
  - 대체: test_tier2_guestimation.py

scripts/test_guestimation_integration.py
  - Guestimation v1.0 통합
  - 대체: test_learning_e2e.py

scripts/test_hybrid_guestimation.py
  - Guardian 자동 전환 (multilayer 의존)
  - 대체: 필요 시 v3.0으로 재작성
```

### 문서 파일 (6개)

```
FERMI_TO_MULTILAYER_EVOLUTION.md
  - Fermi → Multi-Layer 진화 과정
  - 대체: GUESTIMATION_V3_DESIGN.yaml (Phase 1)

MULTILAYER_IMPLEMENTATION_STATUS.md
  - Multi-Layer v2.1 구현 상태
  - 대체: PHASE_5_COMPLETE.md

MULTILAYER_COMPLETE_REPORT.md
  - Multi-Layer v2.1 완료 보고
  - 대체: GUESTIMATION_V3_SESSION_COMPLETE.md

docs/MULTILAYER_USAGE_EXAMPLES.md
  - Multi-Layer 사용 예시
  - 대체: PHASE_5_IMPLEMENTATION_GUIDE.md

docs/MULTILAYER_GUESTIMATION_GUIDE.md
  - Multi-Layer 가이드
  - 대체: guestimation_v3 코드 주석

docs/GUESTIMATION_MULTILAYER_SPEC.md
  - Multi-Layer 스펙
  - 대체: GUESTIMATION_V3_DESIGN.yaml
```

---

## 📊 요약

```yaml
총 파일: 14개

코어 모듈 (3개):
  - multilayer_guestimation.py (v2.1)
  - guestimation.py (v1.0)
  - multilayer_config.py (v2.1 설정)

설정 (1개):
  - multilayer_config.yaml

테스트 (4개):
  - test_multilayer_guestimation.py
  - test_quantifier_multilayer.py
  - test_guestimation_integration.py
  - test_hybrid_guestimation.py

문서 (6개):
  - FERMI_TO_MULTILAYER_EVOLUTION.md
  - MULTILAYER_IMPLEMENTATION_STATUS.md
  - MULTILAYER_COMPLETE_REPORT.md
  - docs/MULTILAYER_USAGE_EXAMPLES.md
  - docs/MULTILAYER_GUESTIMATION_GUIDE.md
  - docs/GUESTIMATION_MULTILAYER_SPEC.md

이동 위치:
  archive/guestimation_v1_v2/
```

---

## ✅ v3.0 대체 매핑

```yaml
v2.1 MultiLayerGuestimation:
  → v3.0 Tier2JudgmentPath
  문제 해결: Sequential → Judgment 기반

v1.0 GuestimationEngine:
  → v3.0 RAGBenchmarkSource
  개선: 비교 가능성 → 종합 판단

multilayer_config:
  → Tier1Config, Tier2Config
  개선: 하드코딩 제거

테스트:
  → test_tier1_guestimation.py
  → test_tier2_guestimation.py
  → test_learning_writer.py
  → test_learning_e2e.py
```

---

## 🚀 다음 조치

```bash
# 1. archive 디렉토리 생성
mkdir -p archive/guestimation_v1_v2/utils
mkdir -p archive/guestimation_v1_v2/core
mkdir -p archive/guestimation_v1_v2/config
mkdir -p archive/guestimation_v1_v2/scripts

# 2. 파일 이동
git mv umis_rag/utils/multilayer_guestimation.py archive/guestimation_v1_v2/utils/
git mv umis_rag/utils/guestimation.py archive/guestimation_v1_v2/utils/
git mv umis_rag/core/multilayer_config.py archive/guestimation_v1_v2/core/
git mv config/multilayer_config.yaml archive/guestimation_v1_v2/config/
git mv scripts/test_multilayer_guestimation.py archive/guestimation_v1_v2/scripts/
git mv scripts/test_quantifier_multilayer.py archive/guestimation_v1_v2/scripts/
git mv scripts/test_guestimation_integration.py archive/guestimation_v1_v2/scripts/
git mv scripts/test_hybrid_guestimation.py archive/guestimation_v1_v2/scripts/

# 3. README 생성
touch archive/guestimation_v1_v2/README.md

# 4. 커밋
git commit -m "archive: Guestimation v1.0/v2.1 → v3.0으로 대체"
```

---

**대체 버전**: Guestimation v3.0 (3-Tier Architecture)  
**이동 준비**: ✅ 완료

