# UMIS RAG 사용 가이드

**버전:** v7.0.0  
**날짜:** 2025-11-02  
**대상:** Cursor 사용자

---

## 📚 문서 목록

### 01_CURSOR_QUICK_START.md ⭐ 시작!

**5분 빠른 시작**

```yaml
내용:
  • 즉시 사용 (2분)
  • Agent 역할
  • RAG 자동 활용
  • Agent 커스터마이징

사용자:
  처음 사용하는 사람
```

---

### 02_CURSOR_WORKFLOW.md

**상세 워크플로우**

```yaml
내용:
  • 시장 분석 전체 흐름
  • 데이터 추가 방법
  • RAG 재구축
  • 단축 명령

사용자:
  Workflow 이해 필요한 사람
```

---

### AGENT_CUSTOMIZATION.md

**Agent 이름 커스터마이징**

```yaml
내용:
  • agent_names.yaml 수정
  • Albert → Jane 등
  • 양방향 매핑
  • 예시

사용자:
  Agent 이름 바꾸고 싶은 사람
```

---

### README_RAG.md

**RAG 기술 설명**

```yaml
내용:
  • RAG란?
  • Vector DB
  • Embedding
  • 검색 원리

사용자:
  기술적 배경 궁금한 사람
```

---

## 🚀 빠른 시작

**처음 사용:**
1. `01_CURSOR_QUICK_START.md` 읽기
2. Cursor (Cmd+I) 열기
3. `@umis.yaml` 첨부
4. `"@Steve, 시장 분석해줘"`

**끝!** ✨

---

## 🎯 최신 변경사항 (2025-11-02)

```yaml
파일명 변경:
  umis_guidelines.yaml → umis.yaml ✨
  
사용:
  Before: @umis_guidelines.yaml
  After: @umis.yaml (간결!)

.cursorrules:
  • 148줄 압축 (40% ↓)
  • UMIS 개념 최우선
  • Agent ID 사용

Agent 구조:
  • id: Observer, Explorer, ... (시스템)
  • name: Albert, Steve, ... (agent_names.yaml)
  • Clean Design (name 필드 제거)
```

---

**상위 문서:**
- ../../START_HERE.md (프로젝트 시작)
- ../architecture/COMPLETE_ARCHITECTURE_V2.md (전체 아키텍처)

