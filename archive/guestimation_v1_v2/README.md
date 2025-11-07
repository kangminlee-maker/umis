# Guestimation v1.0 / v2.1 Archive

**Archive Date**: 2025-11-07  
**Reason**: Guestimation v3.0으로 대체  
**Status**: Deprecated

---

## 📦 포함된 파일

### Core Modules (3개)

```
utils/multilayer_guestimation.py (1,030줄)
  - Multi-Layer Guestimation v2.1
  - 작성: 2025-11-05
  - 8개 Layer Sequential Fallback

utils/guestimation.py (415줄)
  - Guestimation Engine v1.0
  - 작성: 2025-11-04
  - 비교 가능성 검증

core/multilayer_config.py
  - Multi-Layer 설정 로더
  - 의존: config/multilayer_config.yaml
```

### Config (1개)

```
config/multilayer_config.yaml
  - Multi-Layer v2.1 설정
  - 8개 Layer 정의
```

### Tests (4개)

```
scripts/test_multilayer_guestimation.py
  - Multi-Layer v2.1 테스트

scripts/test_quantifier_multilayer.py
  - Quantifier + Multi-Layer 통합 테스트

scripts/test_guestimation_integration.py
  - Guestimation v1.0 통합 테스트

scripts/test_hybrid_guestimation.py
  - Guardian 자동 전환 로직
```

---

## 🔄 v3.0 대체 매핑

### Multi-Layer v2.1 → v3.0

```yaml
Before (v2.1):
  - 8개 Layer Sequential Fallback
  - 첫 성공만 사용
  - 판단 없음
  - 정보 종합 없음

After (v3.0):
  - 3-Tier Architecture
  - 모든 증거 수집 → 종합 판단
  - Context-Aware Judgment
  - 학습하는 시스템

대체 파일:
  multilayer_guestimation.py → guestimation_v3/tier2.py
```

### Guestimation v1.0 → v3.0

```yaml
Before (v1.0):
  - 비교 가능성 검증 중심
  - BenchmarkCandidate 매칭
  - 단순 벤치마크 비교

After (v3.0):
  - 11개 Source 통합
  - RAG Benchmark (Source #10)
  - 증거 평가 + 종합 판단

대체 파일:
  guestimation.py → guestimation_v3/sources/value.py
```

### Config → Code

```yaml
Before (v2.1):
  - multilayer_config.yaml 의존
  - 외부 설정 파일 필요

After (v3.0):
  - Config 클래스 내장
  - Tier1Config, Tier2Config
  - 설정 파일 불필요
```

---

## 📜 변경 이력

### v2.1 (2025-11-05)

**문제 발견**:
- Sequential Fallback (첫 성공만 사용)
- 판단 없음 (검색만)
- 정보 종합 없음
- Context 고려 없음

**결정**: v3.0 설계 시작

### v3.0 (2025-11-07)

**설계 완성**:
- 3-Tier Architecture
- 11개 Source (3 Category)
- Context-Aware Judgment
- 학습하는 시스템

**구현 완료**:
- MVP 작동 ✅
- Phase 5 학습 시스템 ✅
- E2E 테스트 통과 ✅

---

## 🔧 복원 방법 (필요 시)

```bash
# Archive에서 복원
git mv archive/guestimation_v1_v2/utils/multilayer_guestimation.py umis_rag/utils/
git mv archive/guestimation_v1_v2/config/multilayer_config.yaml config/

# 주의: v3.0과 동시 사용 불가!
```

---

## 📚 참고 문서

- **v3.0 설계**: `GUESTIMATION_V3_DESIGN.yaml` (3,474줄)
- **설계 세션**: `SESSION_SUMMARY_20251107_GUESTIMATION_V3_DESIGN.md`
- **Phase 5 완료**: `PHASE_5_COMPLETE.md`
- **v2.1 문제 분석**: `GUESTIMATION_V3_DESIGN.yaml` (Phase 1)

---

**Archive 이유**: v3.0이 v1.0/v2.1의 근본적 문제를 해결  
**권장**: v3.0 사용  
**복원**: 필요 시 가능하나 비권장

