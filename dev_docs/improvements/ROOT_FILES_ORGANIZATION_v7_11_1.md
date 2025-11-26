# 루트 파일 정리 계획

## 📂 현재 루트 파일들

### 1. v7.11.1 관련 신규 문서
- CONTEXT_WINDOW_STRATEGY.md
- TASK_TOOLS_DECISION.md
- V7_11_1_COMPLETION_SUMMARY.md

### 2. v7.11.0 계획 문서
- UMIS_YAML_UPDATE_PLAN_v7_11_0.md

### 3. Core 설정 파일 (유지)
- umis.yaml (Source of Truth)
- umis_core.yaml (System RAG INDEX)
- umis_deliverable_standards.yaml
- umis_examples.yaml
- env.template
- requirements.txt
- docker-compose.yml
- .cursorrules
- README.md
- CHANGELOG.md
- VERSION.txt

---

## 🎯 이동 계획

### dev_docs/session_summaries/
- V7_11_1_COMPLETION_SUMMARY.md
  → dev_docs/session_summaries/V7_11_1_TASK_TOOLS_DECISION.md

### dev_docs/improvements/
- CONTEXT_WINDOW_STRATEGY.md
  → dev_docs/improvements/CONTEXT_WINDOW_STRATEGY_v7_11_1.md

- TASK_TOOLS_DECISION.md
  → dev_docs/improvements/TASK_TOOLS_DECISION_v7_11_1.md

### archive/planning/
- UMIS_YAML_UPDATE_PLAN_v7_11_0.md
  → archive/planning/UMIS_YAML_UPDATE_PLAN_v7_11_0.md

---

## 📋 Root 유지 파일 (8개)

필수 파일만 루트에 유지:
1. umis.yaml (Source of Truth)
2. umis_core.yaml (System RAG INDEX)
3. umis_deliverable_standards.yaml
4. umis_examples.yaml
5. README.md
6. CHANGELOG.md
7. VERSION.txt
8. .cursorrules

설정/환경:
- env.template
- requirements.txt
- docker-compose.yml
- .gitignore 등

---

**작성**: 2025-11-26
