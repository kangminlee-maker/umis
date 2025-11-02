# RAG 문서 검토 (Cursor Composer 중심)

## 🎯 대상 사용자

**코딩 못 하는 UMIS 사용자**
- Cursor Composer만 사용
- Agent 모드 활용
- 대화로 모든 것

## 📋 문서 분류

### ✅ 필수 (Cursor 사용자용)

**guides/**
  ✅ CURSOR_ONLY_WORKFLOW.md - 핵심 가이드!
  ✅ CURSOR_QUICK_START.md - 빠른 시작
  ⚠️ README_RAG.md - 업데이트 필요
  
**architecture/**
  ✅ COMPLETE_RAG_ARCHITECTURE.md - 이해용 (선택)
  ✅ umis_rag_architecture_v1.1_enhanced.yaml - 참조용 (선택)
  
**planning/**
  ✅ DETAILED_TASK_LIST.md - 12일 계획 (향후 개발용)
  ⚠️ IMPLEMENTATION_PLAN.md - 통합 가능
  
**요약/**
  ✅ PROJECT_SUMMARY.md - 성과 요약
  ✅ FINAL_SUMMARY.md - 최종 정리

### ⚠️ 개발자용 (삭제 후보)

**guides/**
  ❌ SIMPLEST_WORKFLOW.md - IPython (개발자용)
  ❌ LIGHTEST_SETUP.md - Python 코드 (개발자용)
  ❌ QUICK_START.md - Jupyter (개발자용)
  ❌ SETUP_GUIDE.md - 터미널 명령 (개발자용)
  ⚠️ USAGE_COMPARISON.md - 일부만 필요
  
**planning/**
  ❌ DEPLOYMENT_STRATEGY.md - Hot-Reload (개발자용)
  ❌ USER_DEVELOPER_WORKFLOW.md - 개발자용
  ❌ DEVELOPMENT_WORKFLOW.md - 개발자용
  ❌ IMPLEMENTATION_ROADMAP.md - 중복

### 🔄 통폐합 필요

**planning/ → 하나로 통합**
  - DETAILED_TASK_LIST.md (유지)
  - IMPLEMENTATION_PLAN.md (통합)
  
**guides/ → Cursor 중심 3개만**
  1. CURSOR_ONLY_WORKFLOW.md (메인!)
  2. CURSOR_QUICK_START.md (빠른 시작)
  3. README_RAG.md (개요, 업데이트)

## 📊 최종 구조 제안

```
rag/docs/
├── INDEX.md (업데이트)
├── README.md (Cursor 중심)
│
├── guides/ (3개만)
│   ├── 01_CURSOR_QUICK_START.md
│   ├── 02_CURSOR_WORKFLOW.md
│   └── 03_ADVANCED_TIPS.md
│
├── architecture/ (참조용)
│   ├── COMPLETE_ARCHITECTURE.md
│   └── specs.yaml
│
├── planning/ (1개)
│   └── IMPLEMENTATION_PLAN.md (통합)
│
└── summary/ (요약)
    ├── PROJECT_SUMMARY.md
    └── WHATS_NEXT.md

→ 10개 핵심 문서만!
```

