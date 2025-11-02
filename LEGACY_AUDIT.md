# 레거시 내용 전체 감사

## 🔍 실제 서비스 vs 문서

### ✅ 실제 구현됨 (v6.3.0-alpha)

```yaml
구현:
  ✅ Vector RAG (54 chunks)
  ✅ Explorer agent (pattern/case search)
  ✅ .cursorrules (자동화)
  ✅ agent_names.yaml (커스터마이징)
  ✅ Cursor Composer 통합

사용 방법:
  Cmd+I
  @umis_guidelines_v6.2.yaml
  "@Steve, 분석해줘"
```

### ❌ 문서에만 있음 (미구현, 제거 필요!)

```yaml
레거시 1: 개발 환경
  ❌ Hot-Reload (make dev)
  ❌ dev_watcher.py
  ❌ Makefile 명령어
  ❌ IPython + autoreload
  ❌ 터미널 명령
  ❌ pip install, venv 설정

레거시 2: 사용 모드
  ❌ Mode 1, 2, 3 비교
  ❌ YAML Only vs YAML+RAG
  ❌ Dual Mode
  ❌ 3가지 Track

레거시 3: 배포 관련
  ❌ build_release.py
  ❌ 배포 패키지 생성
  ❌ Index-Included vs Slim
  ❌ Local vs Shared RAG

레거시 4: 미구현 기능
  ❌ Knowledge Graph (계획만)
  ❌ Guardian 순환 감지 (계획만)
  ❌ 목표 정렬 (계획만)
  ❌ Modular 6-View (계획만)
  ❌ Meta-RAG (계획만)
  ❌ Memory-Augmented RAG (계획만)

레거시 5: 개발 도구
  ❌ quick_umis.sh
  ❌ umis_rag_simple.py
  ❌ pytest, 테스트
  ❌ 성능 벤치마크

레거시 6: 구현 계획
  ❌ 12일 Task List
  ❌ Day별 체크리스트
  ❌ 시간 추정
  ❌ 우선순위 P0-P4
```

---

## 📋 제거/수정 작업 리스트

### Category 1: 개발 환경 언급 제거

**파일:**
- README.md
- START_HERE.md
- rag/docs/guides/README_RAG.md
- rag/docs/PROJECT_SUMMARY.md
- rag/docs/FINAL_SUMMARY.md

**제거 내용:**
- Hot-Reload 섹션
- make 명령어
- 터미널 명령
- IPython 사용법
- 환경 설정 가이드

---

### Category 2: 미구현 기능 표시

**파일:**
- rag/docs/architecture/COMPLETE_RAG_ARCHITECTURE.md
- rag/docs/planning/*
- rag/docs/analysis/*

**수정:**
- 4-Layer → "Layer 1만 구현, 나머지 계획"
- 12일 계획 → "향후 개발 로드맵"
- Guardian 감시 → "계획 중"

---

### Category 3: 사용 모드 단순화

**파일:**
- README.md
- START_HERE.md

**변경:**
- "3가지 모드" → 제거
- "Dual Mode" → 제거
- "YAML Only vs RAG" → 단순화

**유지:**
- Cursor Composer만!

---

### Category 4: 배포 관련 제거

**파일:**
- rag/docs/planning/*
- rag/docs/guides/*

**제거:**
- build_release.py 언급
- 배포 패키지
- Local/Shared RAG 비교

---

### Category 5: 파일 삭제/백업

**제거 후보:**
- rag/quick_umis.sh (개발자용)
- rag/umis_rag_simple.py (개발자용)
- rag/Makefile (개발자용)
- scripts/dev_watcher.py (미사용)
- scripts/build_release.py (미사용)

**백업:**
- rag/docs/planning/*_DEV_ONLY.md.backup → 삭제
- rag/docs/migration/* → 보관 (참조용)

---

## 🎯 최종 목표

### 문서 내용

```yaml
현재 (혼란):
  "make dev로..."
  "IPython에서..."
  "3가지 모드 중..."
  "12일 개발 계획..."

목표 (명확):
  "Cursor Composer (Cmd+I)"
  "@Steve, 분석해줘"
  "대화만! 코딩 불필요!"
```

### 파일 구조

```yaml
현재 (복잡):
  루트: 개발 도구들 (Makefile, quick_umis.sh, ...)
  rag/docs/: 구현 계획들

목표 (단순):
  루트: YAML + agent_names.yaml
  rag/docs/: 사용 가이드만
```

---

## 📊 예상 작업

```yaml
파일 수정: 10+개
파일 삭제: 5+개
라인 제거: 1,000+줄

소요: 30분
방식: 자동 스크립트 + 수동 검토
```

---

**실행할까요?**

