# UMIS v7.7.0 시작하기

**버전:** 7.7.0 (6-Agent + 5-Phase + Web 크롤링, 100% 커버리지)  
**날짜:** 2025-11-12  
**대상:** Cursor 사용자

---

## ⚡ 30초 빠른 시작

```
Cursor Composer (Cmd+I):

umis.yaml 첨부

"@Steve, 음악 스트리밍 구독 서비스 시장 기회 분석해줘"
"@Fermi, SaaS LTV는?"  ⭐ 5-Phase + Web Search!
"@Fermi, 한국 인구는?"  ⭐ Validator 우선 검색!
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
Estimator (Fermi) → 값 추정 (3-Tier, 12개 지표) ⭐ 신규!

v7.6.2: 5-Phase + Web Search 완전 작동!
```

---

## ⭐ v7.7.0 신규 기능

```yaml
✅ Web Search 페이지 크롤링 (v7.7.0)
   - 정보량: 553자 → 20,538자 (3,614% 증가)
   - 숫자 추출: 4개 → 41개 (10배 증가)
   - 자동 fallback (실패 시 snippet 사용)

✅ Native 모드 진짜 구현
   - Explorer: RAG만 → Cursor LLM 분석
   - 비용 $0 (API 호출 없음)

✅ 5-Phase 명확화 (Phase 0-4)
   - Phase: Estimator 전체 단계
   - Step: Phase 4 내부 단계
   - 혼란 완전 제거

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

## 🚀 사용 흐름 (v7.6.2)

```
1. Cursor (Cmd+I)
2. umis.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Explorer RAG 자동 검색
→ subscription_model 발견
→ Spotify, Netflix 사례 학습
→ 가설 생성

4. "@Fermi, LTV는?"  ⭐ 신규!

→ Tier 1 체크 → 없음
→ Tier 2 시도 → 복잡
→ Tier 3 실행 (재귀 분해)
→ 템플릿: ltv = arpu / churn_rate
→ 재귀 추정 → Backtracking
→ 결과: 1,600,000원

→ 100% 답변 가능! ✨
```

---

## 📖 더 알아보기

**시작:**
- [README.md](../README.md) - UMIS v7.6.2 소개
- [SETUP.md](SETUP.md) - 초기 설정 (5분)

**가이드:**
- [UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md) - 전체 아키텍처
- [CURRENT_STATUS.md](../CURRENT_STATUS.md) - v7.6.2 현황

**Release Notes:**
- [CHANGELOG.md](../CHANGELOG.md) - v7.6.2 변경사항
- [CHANGELOG.md](../CHANGELOG.md) - 전체 버전 이력

---

## 🔗 링크

- **GitHub:** [kangminlee-maker/umis](https://github.com/kangminlee-maker/umis)
- **Issues:** [umis/issues](https://github.com/kangminlee-maker/umis/issues)

---

**UMIS Team • 2025**
