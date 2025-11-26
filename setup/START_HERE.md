# UMIS v7.11.0 시작하기

**버전:** 7.11.0 (6-Agent + 4-Stage Fusion + LLM Abstraction)  
**날짜:** 2025-11-26  
**대상:** Cursor 사용자

---

## ⚡ 30초 빠른 시작

```
Cursor Composer (Cmd+I):

umis.yaml 첨부

"@Steve, 음악 스트리밍 구독 서비스 시장 기회 분석해줘"
"@Estimator, SaaS LTV는?"  ⭐ 4-Stage Fusion!
"@Estimator, 한국 인구는?"  ⭐ Validator 우선 검색!
```

**끝!** 🎉

---

## 🤖 UMIS 6-Agent 시스템

```
Observer (Albert) → 시장 구조 분석
Explorer (Steve) → 기회 발굴 (RAG!)
Quantifier (Bill) → 정량 분석 + Excel
Validator (Rachel) → 데이터 검증 + 교차 검증
Guardian (Stewart) → 프로세스 감시 (Meta-RAG)
Estimator (Fermi) → 값 추정 (4-Stage Fusion, 12개 지표) ⭐

v7.11.0: 4-Stage Fusion + LLM Abstraction 완성!
```

---

## ⭐ v7.11.0 신규 기능

```yaml
✅ 4-Stage Fusion Architecture (v7.11.0)
   - Phase 0-4 → Stage 1-4 통합
   - Stage 1: Evidence Collection (확정 데이터, <1초)
   - Stage 2: Generative Prior (LLM 직접 추정, ~3초)
   - Stage 3: Structural Explanation (Fermi 분해, max_depth=2)
   - Stage 4: Fusion & Validation (융합, <1초)
   - 재귀 제거 → 예측 가능한 실행 시간

✅ LLM Complete Abstraction
   - LLMProvider 인터페이스 (DIP, SRP, OCP, ISP)
   - Cursor vs External 모드 완전 추상화
   - 비즈니스 로직에서 llm_mode 분기 61개 제거
   - Clean Architecture 100% 적용

✅ Budget 기반 탐색
   - max_llm_calls, max_runtime, budget_mode
   - 예측 가능한 비용 및 실행 시간
   - 표준 모드 (3-5초), 고속 모드 (1-2초), 정밀 모드 (5-10초)

✅ 100% 커버리지 유지
```

---

## 📦 설치

```bash
git clone https://github.com/kangminlee-maker/umis.git
cd umis
```

**초기 설정:** [SETUP.md](SETUP.md) 참고 (5분)

---

## 📁 프로젝트 구조

```
umis/
├── 핵심 YAML
│   ├── umis.yaml ⭐ (메인 가이드라인)
│   ├── umis_deliverable_standards.yaml (산출물 표준)
│   ├── umis_examples.yaml (예제)
│   └── config/agent_names.yaml (커스터마이징)
│
├── RAG 데이터
│   └── data/
│       ├── raw/ (원본 YAML)
│       │   ├── umis_business_model_patterns.yaml (31 패턴)
│       │   └── umis_disruption_patterns.yaml (23 패턴)
│       ├── chunks/ (청크 JSONL)
│       └── chroma/ (벡터 DB, 54개 문서)
│
├── RAG 시스템
│   ├── scripts/ (RAG 빌드/검색)
│   ├── umis_rag/ (Python 패키지)
│   └── notebooks/ (프로토타입)
│
├── 문서
│   ├── docs/ (UMIS v6.2 가이드)
│   └── rag/docs/ (RAG 아키텍처 65개)
│
└── 설정
    ├── .cursorrules (UMIS 자동화 규칙)
    ├── env.template (API 키)
    └── SETUP.md (초기 설정)
```

---

## 🚀 사용 흐름 (v7.11.0)

```
1. Cursor (Cmd+I)
2. umis.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Explorer RAG 자동 검색
→ subscription_model 발견
→ Spotify, Netflix 사례 학습
→ 가설 생성

4. "@Estimator, LTV는?"  ⭐ 4-Stage Fusion!

→ Stage 1 (Evidence): 확정 데이터 검색 (<1초)
→ Stage 1 없음 → Stage 2 (Prior): LLM 직접 추정 (~3초)
→ certainty == low → Stage 3 (Fermi): 구조적 분해 (max_depth=2)
   - Formula: ltv = arpu / churn_rate
   - 변수 추정: arpu, churn_rate (Stage 2 사용)
   - 계산 수행
→ Stage 4 (Fusion): 모든 Stage 결과 가중 합성 (<1초)
→ 결과: 1,600,000원

→ 100% 답변 가능! ✨
```

---

## 📖 더 알아보기

**시작:**
- [README.md](../README.md) - UMIS v7.11.0 소개
- [SETUP.md](SETUP.md) - 초기 설정 (5분)

**가이드:**
- [UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md) - 전체 아키텍처
- [LLM_COMPLETE_ABSTRACTION_SUMMARY_v7_11_0.md](../dev_docs/improvements/LLM_COMPLETE_ABSTRACTION_SUMMARY_v7_11_0.md) - LLM 추상화

**Release Notes:**
- [CHANGELOG.md](../CHANGELOG.md) - v7.11.0 변경사항
- [CHANGELOG.md](../CHANGELOG.md) - 전체 버전 이력

---

## 🔗 링크

- **GitHub:** [kangminlee-maker/umis](https://github.com/kangminlee-maker/umis)
- **Issues:** [umis/issues](https://github.com/kangminlee-maker/umis/issues)

---

**UMIS Team • 2025**
