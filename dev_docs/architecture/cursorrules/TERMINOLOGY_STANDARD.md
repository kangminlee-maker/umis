# UMIS 용어 표준화

**문제:** .cursorrules와 umis.yaml 용어 불일치

---

## 🔍 1. .cursorrules 약어/개념어

### 현재 사용

```yaml
# .cursorrules line 19
flow: Observer(observe)→Explorer(rag+hypothesize)→...

약어/개념어:
  • flow: 흐름
  • observe: 관찰
  • hypothesize: 가설화
  • calculate: 계산
  • verify: 검증
  • rag: RAG 검색
```

### 문제

```yaml
umis.yaml에 정의 없음!
  
  결과:
    • .cursorrules가 임의 용어 사용
    • umis.yaml과 불일치
    • 표준 없음
```

---

## 💡 해결: umis.yaml에 용어 정의

### 추가 필요 섹션

```yaml
# umis.yaml 최상단

_terminology:
  version: "7.0.0"
  purpose: "UMIS 표준 용어 정의"
  
  agent_actions:
    observe: "시장 구조 관찰 (Observer)"
    hypothesize: "기회 가설 생성 (Explorer)"
    calculate: "시장 규모 계산 (Quantifier)"
    verify: "데이터 검증 (Validator)"
    monitor: "프로세스 감시 (Guardian)"
    decide: "전략 결정 (Owner)"
  
  system_concepts:
    flow: "정보 흐름 (Agent 간 작업 순서)"
    rag: "RAG 자동 검색 (Explorer만)"
    discovery_sprint: "목표 명확화 프로세스"
    validation: "의무 검증 프로토콜"
  
  abbreviations:
    obs: Observer
    exp: Explorer
    qnt: Quantifier
    val: Validator
    grd: Guardian
```

**효과:**
```yaml
.cursorrules:
  flow: Observer(observe)→...
  
  → umis.yaml 참조
  → 표준 준수
  → 일관성 ✅
```

---

## 🔍 2. Patterns YAML 위치

### 현재 상태

```yaml
루트:
  • umis_business_model_patterns.yaml
  • umis_disruption_patterns.yaml
  
data/raw/:
  • umis_business_model_patterns.yaml (복사본)
  • umis_disruption_patterns.yaml (복사본)

→ 중복! ⚠️
```

### 당신의 제안

```yaml
제거: 루트
유지: data/raw/

이유:
  • 재현성 = data/raw/로 충분
  • Cursor가 자동으로 찾아서 수정
  • 루트 깔끔
```

**완전히 맞습니다!** ✅

---

## 💡 최종 구조

### 채택

```
umis-main/
├── 핵심 (간결!)
│   ├── umis.yaml (또는 모듈화)
│   ├── config/agent_names.yaml
│   ├── .cursorrules
│   └── ... (최소)
│
├── data/
│   ├── raw/ ⭐ RAG 소스!
│   │   ├── umis_business_model_patterns.yaml
│   │   ├── umis_disruption_patterns.yaml
│   │   └── umis_ai_guide.yaml (백업)
│   ├── chunks/
│   └── chroma/
│
└── ...
```

### 흐름

```yaml
사용자:
  Cursor: "코웨이 해지율 추가"

Cursor:
  1. data/raw/*.yaml 찾기 (자동)
  2. 해당 섹션 수정
  3. scripts/01_convert_yaml.py
  4. scripts/02_build_index.py
  5. "✅ 완료!"

사용자:
  루트 파일 몰라도 됨!
```

---

## 🎯 최종 결정

### 1. 용어 표준화

```yaml
채택:
  ✅ umis.yaml 최상단에 _terminology 섹션
  
내용:
  • agent_actions (observe, hypothesize, ...)
  • system_concepts (flow, rag, ...)
  • abbreviations (obs, exp, ...)

효과:
  .cursorrules ↔ umis.yaml 일관성
```

### 2. Patterns 위치

```yaml
채택:
  ✅ data/raw/만 유지
  ❌ 루트 제거

이유:
  • Cursor 자동 찾기
  • 재현성 충분
  • 루트 깔끔

삭제:
  • umis_business_model_patterns.yaml (루트)
  • umis_disruption_patterns.yaml (루트)
```

---

**당신의 두 지적이 모두 정확했습니다!** ✨

실행하시겠어요? 🚀

