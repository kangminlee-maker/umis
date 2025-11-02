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
  • .cursorrules 자동화
  • Agent 모드 자동 실행
  • 대화만! 코딩 불필요!

Agent 커스터마이징:
  • agent_names.yaml
  • 양방향 매핑
  • Albert, Steve, Bill, ... (기본)
  → Jane, Alex, ... (커스텀)
```

### 📋 향후 계획 (미구현)

```yaml
Knowledge Graph (Layer 3):
  • 패턴 조합 자동 발견
  
Guardian 감시 (Layer 4):
  • 순환 패턴 감지
  • 목표 정렬 모니터링

Multi-Agent (Layer 1 확장):
  • 6-Agent modular RAG
  • Observer/Quantifier/Validator/Guardian RAG

Meta-RAG (Layer 2):
  • 품질 자동 평가
```

**주의:** architecture/, planning/ 문서는 **향후 계획**입니다!

**상세:** architecture/, planning/ 참조

---

**시작:** guides/01_CURSOR_QUICK_START.md
