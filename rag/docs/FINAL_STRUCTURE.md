# UMIS 프로젝트 최종 구조

**완료:** 2024-11-02  
**상태:** 기존 UMIS vs RAG 명확 분리 ✅

---

## 📁 최종 디렉토리 구조

```
umis-main/
│
├── 📚 UMIS Core (기존)
│   │
│   ├── 시작 문서
│   │   ├── START_HERE.md
│   │   ├── README.md
│   │   ├── CHANGELOG.md
│   │   └── IMPLEMENTATION_SUMMARY.md
│   │
│   ├── UMIS YAML (6개)
│   │   ├── umis_guidelines_v6.2.yaml
│   │   ├── umis_business_model_patterns_v6.2.yaml
│   │   ├── umis_disruption_patterns_v6.2.yaml
│   │   ├── umis_ai_guide_v6.2.yaml
│   │   ├── umis_deliverable_standards_v6.2.yaml
│   │   └── umis_examples_v6.2.yaml
│   │
│   ├── docs/
│   │   ├── UMIS_v6.2_Complete_Guide.md
│   │   ├── market_analysis/
│   │   └── ...
│   │
│   ├── archive/ (이전 버전)
│   ├── deliverable_specs/
│   └── umis_rag/ (Python 패키지)
│
└── 🤖 RAG (신규)
    └── rag/
        ├── README.md
        ├── quick_umis.sh (30초 시작)
        ├── Makefile
        ├── umis_rag_simple.py
        │
        ├── docs/ (26개)
        │   ├── INDEX.md
        │   ├── architecture/
        │   ├── planning/
        │   ├── guides/
        │   ├── analysis/
        │   └── 요약들
        │
        ├── code/
        │   └── scripts/
        │
        ├── config/
        │   ├── requirements.txt
        │   └── pyproject.toml
        │
        └── data/ → ../data/
```

---

## 🎯 역할 분리

### UMIS Core (루트)

```yaml
대상: UMIS 사용자
위치: umis-main/ (루트)
용도: 기존 YAML 기반 시장 분석

파일:
  • YAML 6개
  • docs/ (시장 분석 결과)
  • archive/ (이전 버전)

사용:
  Cursor에 YAML 첨부
  → 즉시 분석 시작
```

### RAG (rag/)

```yaml
대상: RAG 개발자/사용자
위치: rag/ 폴더
용도: 검색 증강, 패턴 라이브러리

파일:
  • docs/ (26개 설계/계획)
  • code/ (스크립트)
  • config/ (설정)

사용:
  cd rag/
  ./quick_umis.sh
  → IPython RAG 검색
```

---

## 🔗 연결

```yaml
RAG → UMIS:
  • ../umis_guidelines_v6.2.yaml 참조
  • ../data/ 공유 (심볼릭 링크)
  • from umis_rag import ... (Python)

UMIS → RAG:
  • 독립적 (RAG 없어도 작동)
  • 선택적 참조
```

---

## 📖 문서 위치

```
UMIS 문서:
  • docs/UMIS_v6.2_Complete_Guide.md
  • docs/UMIS v6.2 Executive Summary
  • CHANGELOG.md

RAG 문서:
  • rag/docs/INDEX.md (전체 인덱스)
  • rag/docs/architecture/ (설계)
  • rag/docs/planning/ (계획)
  • rag/docs/guides/ (가이드)
```

---

## 🚀 빠른 시작

### UMIS

```
Cursor:
  @umis_guidelines_v6.2.yaml
```

### RAG

```bash
cd rag/
./quick_umis.sh
```

---

**완벽하게 분리되었습니다!** 🎯
