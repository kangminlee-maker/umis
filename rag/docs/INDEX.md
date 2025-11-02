# UMIS RAG 문서 인덱스

**버전:** 6.3.0-alpha  
**대상:** Cursor 사용자 (코딩 불필요)

---

## 🚀 즉시 시작

```
Cursor Composer (Cmd+I)

@umis_guidelines.yaml

"@Steve, 음악 스트리밍 구독 기회 분석해줘"
```

**그게 전부입니다!** 🎉

---

## 📚 필수 문서 (3개)

### 1. 빠른 시작
- **guides/01_CURSOR_QUICK_START.md** ⭐
  - 30초 시작
  - Cursor Composer 사용법

### 2. 상세 가이드
- **guides/02_CURSOR_WORKFLOW.md**
  - 실전 워크플로우
  - 데이터 추가 방법

### 3. 커스터마이징
- **guides/AGENT_CUSTOMIZATION.md**
  - agent_names.yaml 수정
  - Albert → Jane 등

---

## 📖 참고 문서 (선택)

### Architecture (설계)
- 4-Layer RAG 아키텍처
- 향후 구현 계획

### Planning (계획)
- Cursor 기반 개발 방법
- 12일 로드맵

### Analysis (분석)
- 설계 철학
- 기술 분석

### Summary (요약)
- 프로젝트 성과
- 개발 과정

---

## 🎯 v6.3.0-alpha 현황

### ✅ 구현됨 (현재 사용 가능!)

```yaml
Vector RAG:
  • 54개 검증된 패턴/사례
  • text-embedding-3-large
  • Explorer만 RAG 사용! ⭐

Cursor 통합:
  • .cursorrules 최적화 (148줄, 40% 압축)
  • UMIS 개념 최우선 로딩
  • Agent 모드 자동 실행
  • 초기 설치 자동 안내

Clean Design:
  • umis.yaml (name 필드 제거)
  • agent_names.yaml (단일 진실)
  • 완벽한 관심사 분리

Agent 커스터마이징:
  • agent_names.yaml
  • 양방향 매핑
  • Albert, Steve, Bill, ... (기본)
  → Jane, Alex, ... (커스텀)
```

### 📋 Architecture v2.0 (8개 개선안 설계 완료!)

```yaml
채택 (6개):
  1. Dual-Index (품질+일관성)
  2. Schema-Registry (필드 일관성)
  3. Routing YAML (가독성)
  4. Multi-Dimensional Confidence (질적+양적)
  7. Fail-Safe (안정성)
  8. System RAG (컨텍스트 95% 절감!) ⭐

설계만 (1개):
  6. Overlay Layer (팀 확장 시)

제외 (1개):
  5. RAE Index (오버엔지니어링)

문서:
  • architecture/COMPLETE_ARCHITECTURE_V2.md
  • architecture/umis_rag_architecture_v2.0.yaml
  • architecture/planning/IMPLEMENTATION_ROADMAP_V2.md
```

**로드맵:** `architecture/planning/IMPLEMENTATION_ROADMAP_V2.md` 참조

**상세:** architecture/, planning/ 참조

---

**시작:** guides/01_CURSOR_QUICK_START.md
