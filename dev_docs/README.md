# UMIS RAG Development Documentation

**목적**: UMIS RAG 시스템의 개발 히스토리 및 아키텍처 문서  
**상태**: 참조용 문서 (시스템 비의존)  
**버전**: v7.0.0 (RAG v3.0)

---

## 📌 중요

이 폴더는 **개발 문서만** 포함하며, 실제 UMIS 시스템과는 **독립적**입니다.

- **실제 RAG 코드**: `../umis_rag/` 패키지
- **RAG 스크립트**: `../scripts/` 폴더
- **이 폴더**: 개발 과정, 아키텍처 설계, 분석 문서

---

## 📁 구조 (플랫 디자인)

```
dev_docs/
├── README.md                 # 이 파일
├── INDEX.md                  # 전체 인덱스
│
├── architecture/             # RAG v3.0 아키텍처 설계
│   ├── 01_projection/        # Projection 메커니즘
│   ├── 02_schema_registry/   # Schema Registry
│   ├── 03_routing_yaml/      # Routing Policy
│   ├── 04_graph_confidence/  # Graph Confidence
│   ├── 05_rae_index/         # RAE Index
│   ├── 06_overlay_layer/     # Overlay Layer
│   ├── 07_fail_safe/         # Fail-Safe
│   ├── 08_system_rag/        # System RAG
│   ├── 09_id_lineage/        # ID & Lineage
│   ├── 10_anchor_hash/       # Anchor Hash
│   └── COMPLETE_ARCHITECTURE_V3.md
│
├── dev_history/              # 주차별 개발 히스토리
│   ├── week_2_dual_index/
│   ├── week_3_knowledge_graph/
│   ├── week_4_guardian/
│   └── phase_2_advanced/
│
├── analysis/                 # 시스템 분석 문서
│   ├── ADVANCED_RAG_CHALLENGES.md
│   ├── ARCHITECTURE_QA.md
│   ├── COMPREHENSIVE_AUDIT.md
│   ├── MULTI_AGENT_RAG_ARCHITECTURE.md
│   └── MEMORY_AUGMENTED_RAG_ANALYSIS.md
│
├── guides/                   # 개발 가이드
│   ├── 01_CURSOR_QUICK_START.md
│   ├── 02_CURSOR_WORKFLOW.md
│   ├── knowledge_graph_setup_20251103.md
│   ├── AGENT_CUSTOMIZATION.md
│   └── README_RAG.md
│
├── planning/                 # 계획 문서
│   └── (향후 계획 문서들)
│
└── summary/                  # 요약 문서
    ├── FINAL_STATUS_AND_NEXT_STEPS.md
    └── PROJECT_SUMMARY.md
```

---

## 🎯 주요 문서

### 1. 아키텍처 설계
- **[COMPLETE_ARCHITECTURE_V3.md](architecture/COMPLETE_ARCHITECTURE_V3.md)** - RAG v3.0 전체 설계
- **[umis_rag_architecture_v3.0.yaml](architecture/umis_rag_architecture_v3.0.yaml)** - 구조화된 스펙

### 2. 시스템 분석
- **[MULTI_AGENT_RAG_ARCHITECTURE.md](analysis/MULTI_AGENT_RAG_ARCHITECTURE.md)** - Multi-Agent RAG 아키텍처
- **[ADVANCED_RAG_CHALLENGES.md](analysis/ADVANCED_RAG_CHALLENGES.md)** - RAG 고급 과제
- **[ARCHITECTURE_QA.md](analysis/ARCHITECTURE_QA.md)** - 아키텍처 Q&A

### 3. 개발 히스토리
- **[DEVELOPMENT_TIMELINE.md](dev_history/DEVELOPMENT_TIMELINE.md)** - 전체 개발 타임라인
- **[week_3_knowledge_graph/](dev_history/week_3_knowledge_graph/)** - Knowledge Graph 개발
- **[week_4_guardian/](dev_history/week_4_guardian/)** - Guardian Memory 개발

### 4. 가이드
- **[01_CURSOR_QUICK_START.md](guides/01_CURSOR_QUICK_START.md)** - Cursor 빠른 시작
- **[knowledge_graph_setup_20251103.md](guides/knowledge_graph_setup_20251103.md)** - Knowledge Graph 설정
- **[README_RAG.md](guides/README_RAG.md)** - RAG 시스템 가이드

### 5. 요약
- **[FINAL_STATUS_AND_NEXT_STEPS.md](summary/FINAL_STATUS_AND_NEXT_STEPS.md)** - 최종 상태 및 다음 단계
- **[PROJECT_SUMMARY.md](summary/PROJECT_SUMMARY.md)** - 프로젝트 요약

---

## 🔗 실제 시스템 파일

RAG 시스템 사용/개발을 위해서는:

### 사용자
- **[../INSTALL.md](../INSTALL.md)** - 설치 가이드
- **[../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md)** - 전체 시스템 구조
- **[../umis.yaml](../umis.yaml)** - UMIS 가이드라인

### 개발자
- **[../umis_rag/](../umis_rag/)** - RAG 코드 패키지
- **[../scripts/](../scripts/)** - RAG 빌드/검색 스크립트
- **[../config/schema_registry.yaml](../config/schema_registry.yaml)** - RAG 스키마 정의

---

## 📚 활용 방법

### 새로운 기여자
1. [DEVELOPMENT_TIMELINE.md](dev_history/DEVELOPMENT_TIMELINE.md) - 개발 과정 이해
2. [COMPLETE_ARCHITECTURE_V3.md](architecture/COMPLETE_ARCHITECTURE_V3.md) - 아키텍처 학습
3. [../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md) - 현재 구조 파악

### 아키텍처 연구
- `architecture/` - 각 컴포넌트 설계 의사결정 과정
- Expert Feedback 문서들 - 전문가 피드백 및 반영

### 문제 해결
- `analysis/` - 다양한 분석 및 검토 문서
- 각 주차별 `COMPLETE.md` - 완료 항목 및 이슈

---

## 📝 파일 네이밍 규칙 (중요!)

### 날짜 포함 (필수)

**새로 작성하는 모든 분석/가이드 문서**에 날짜를 포함하세요:

```
feature_analysis_20251103.md
knowledge_graph_setup_20251103.md
performance_test_20251103.md
architecture_review_20251103.md
```

**형식**: `{주제}_{YYYYMMDD}.md`

**이유**:
- ✅ **최신 문서 즉시 식별** (과거 설계로 현재 개발하는 실수 방지)
- ✅ **과거 버전과 명확히 구분**
- ✅ **버전 추적 용이** (같은 주제의 시간별 진화 파악)

### 예외 (날짜 불필요)

```
README.md                         # 폴더 설명
INDEX.md                          # 인덱스
COMPLETE_ARCHITECTURE_V3.md       # 버전 번호(V3)로 충분
DEVELOPMENT_TIMELINE.md           # 타임라인 자체가 날짜 포함
```

### 기존 문서 (Legacy)

날짜가 없는 기존 문서들:
- 그대로 유지 (날짜 추가하면 git history 추적 어려움)
- 파일 내용에 작성일/최종 업데이트 명시 권장
- 새 버전 작성 시 날짜 포함

**예시**:
```
ADVANCED_RAG_CHALLENGES.md (기존)
  → 새 분석 작성 시: advanced_rag_challenges_v2_20251110.md
```

---

## ⚠️ 주의사항

### 이 폴더의 문서들은:
- ✅ 개발 히스토리 참조용
- ✅ 아키텍처 학습용
- ✅ 의사결정 과정 이해용

### 이 폴더의 문서들은 아님:
- ❌ 실제 시스템 동작과 무관
- ❌ 코드 실행에 필요하지 않음
- ❌ 일반 사용자가 읽을 필요 없음

---

## 🔄 업데이트

이 폴더는:
- 개발 과정 중 생성된 문서들의 아카이브
- 향후 v8.0, v9.0 개발 시 참조 자료
- RAG 시스템 진화 과정의 기록

**현재 버전**: v7.0.0 (RAG v3.0 기반)  
**구조 업데이트**: 2025-11-03 (플랫 디자인 적용)

---

**참고**: UMIS 사용 또는 개발을 시작하려면 이 폴더가 아닌 **루트의 [INSTALL.md](../INSTALL.md)** 또는 **[UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md)**를 참조하세요.
