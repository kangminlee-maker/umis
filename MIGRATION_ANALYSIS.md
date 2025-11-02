# Agent Name → ID 일괄 변경 분석

**목표:** steve → explorer 등 완전 통일  
**방법:** 백업 → 분석 → 일괄 변경

---

## 📊 현재 상황 파악

### 변경 필요 파일 (7개)

```yaml
1. umis_rag/agents/steve.py (핵심!)
   • class SteveRAG
   • create_steve_agent()
   → ExplorerRAG, create_explorer_agent()

2. scripts/01_convert_yaml.py
   • steve_bm_chunks
   • steve_dp_chunks
   → explorer_*

3. scripts/02_build_index.py
   • build_steve_index()
   • --agent steve
   → build_explorer_index(), --agent explorer

4. scripts/03_test_search.py
   • --agent steve
   → --agent explorer

5. scripts/query_rag.py
   • (주석에만 steve 언급)
   → explorer

6. scripts/dev_watcher.py
   • (주석에만)
   → explorer

7. umis_rag/core/metadata_schema.py
   • steve_view_type
   • SteveMetadata
   → explorer_*
```

---

## 🗑️ 삭제 가능 확인

### data/ 폴더

```yaml
data/chunks/
  • steve_business_models.jsonl
  • steve_disruption_patterns.jsonl
  
삭제 가능: ✅ Yes!
이유: YAML에서 재생성 가능 (2초)
```

```yaml
data/chroma/
  • steve_knowledge_base (벡터 DB)
  
삭제 가능: ✅ Yes!
이유: 청크에서 재구축 가능 (1분)
비용: $0.006 (재구축)
```

**결론:**
```yaml
✅ data/ 전체 삭제 후 재생성 권장!

이유:
  • 변수명 바뀌면 어차피 재구축 필요
  • YAML만 있으면 언제든 재생성
  • 깨끗한 시작
  
명령:
  rm -rf data/chunks/* data/chroma/*
  (나중에 재구축)
```

---

## ⚠️ ID 이름 검토

### 현재 ID (UMIS v6.2)

```yaml
Observer - 시장 구조 관찰
Explorer - 기회 발굴
Quantifier - 정량 분석
Validator - 데이터 검증
Guardian - 프로세스 감시
```

### 문제점 분석

```yaml
너무 Generic?
  Observer: ⚠️ 매우 일반적
  Explorer: ⚠️ 일반적
  Quantifier: ✅ 구체적
  Validator: ⚠️ 일반적  
  Guardian: ✅ 독특함

충돌 가능성:
  • 다른 시스템과 이름 충돌?
  • 확장 시 모호함?
  
예시:
  "Observer가 뭘 관찰하는가?"
  → 시장? 시스템? 사용자?
  
  "Explorer가 뭘 탐색하는가?"
  → 기회? 데이터? 옵션?
```

### 🎯 개선안 제안

#### Option A: Prefix 추가

```yaml
UMIS_Observer
UMIS_Explorer
UMIS_Quantifier
UMIS_Validator
UMIS_Guardian

장점:
  ✅ 명확: UMIS 전용임을 표시
  ✅ 충돌 방지: 다른 시스템과 구분
  ✅ 확장 용이: UMIS_* 네임스페이스

단점:
  ⚠️ 길어짐: UMIS_ 추가
```

#### Option B: 역할 명확화

```yaml
MarketObserver (시장 관찰자)
OpportunityExplorer (기회 탐색자)
MarketQuantifier (시장 정량화)
DataValidator (데이터 검증자)
ProcessGuardian (프로세스 수호자)

장점:
  ✅ 명확: 무엇을 하는지 명확
  ✅ 자연스러움: 영어로도 이해됨
  ✅ 확장 용이: 역할 분명

단점:
  ⚠️ 길어짐
  ⚠️ UMIS 표기 없음
```

#### Option C: 현재 유지

```yaml
Observer, Explorer, Quantifier, Validator, Guardian

장점:
  ✅ 짧음: 간결
  ✅ UMIS v6.2 표준: Guidelines와 일치
  ✅ 이미 정의됨: 변경 불필요

단점:
  ⚠️ Generic: 다소 일반적
  
평가:
  → UMIS 컨텍스트 내에서는 명확
  → 외부에서 import 시 애매할 수 있음
```

#### 🎯 최종 추천: Option A (UMIS Prefix)

```yaml
이유:
  1. 명확성: UMIS 전용임 명시
  2. 확장성: 향후 다른 도메인 추가 시
  3. 충돌 방지: 네임스페이스
  
실제 사용:
  from umis_rag.agents import UMIS_Explorer
  explorer = create_umis_explorer()
  
  → 명확하고 안전! ✅
```

---

## 📋 최종 제안

### 🎯 권장 방안

```yaml
1단계: 전체 백업
  git branch backup/before-rename
  git checkout -b refactor/agent-id-rename

2단계: ID 이름 결정
  Option A: UMIS_Observer, UMIS_Explorer, ...
  Option B: MarketObserver, OpportunityExplorer, ...
  Option C: Observer, Explorer, ... (현재)
  
  → 선택해주세요!

3단계: data/ 삭제
  rm -rf data/chunks/* data/chroma/*
  (재생성 예정)

4단계: 일괄 변경
  • 파일명: steve.py → explorer.py
  • 클래스명: SteveRAG → ExplorerRAG
  • 함수명: create_steve_agent → create_explorer_agent
  • 변수명: steve → explorer
  • 메타데이터: steve_view → explorer_view

5단계: 재구축
  python scripts/01_convert_yaml.py
  python scripts/02_build_index.py --agent explorer

6단계: 테스트
  python scripts/03_test_search.py --agent explorer
  python scripts/query_rag.py pattern "구독"

7단계: 커밋
  git commit -m "refactor: Rename agents to IDs"
  git push origin alpha
```

---

## 💡 ID 이름 최종 권장

### 🥇 UMIS Prefix 방식

```python
# umis_rag/agents/__init__.py

from .market_observer import UMIS_Observer, create_umis_observer
from .opportunity_explorer import UMIS_Explorer, create_umis_explorer
from .market_quantifier import UMIS_Quantifier, create_umis_quantifier
from .data_validator import UMIS_Validator, create_umis_validator
from .process_guardian import UMIS_Guardian, create_umis_guardian

__all__ = [
    'UMIS_Observer',
    'UMIS_Explorer',
    'UMIS_Quantifier',
    'UMIS_Validator',
    'UMIS_Guardian',
    'create_umis_observer',
    'create_umis_explorer',
    'create_umis_quantifier',
    'create_umis_validator',
    'create_umis_guardian',
]
```

**사용:**
```python
from umis_rag.agents import UMIS_Explorer

explorer = create_umis_explorer()
explorer.search_patterns("구독")

→ 명확하고 충돌 없음! ✅
```

**메타데이터:**
```python
metadata = {
    'agent_view': 'umis_explorer',  # 또는 'explorer'
    'umis_explorer_pattern_id': '...',
    # ...
}

→ 네임스페이스 명확! ✅
```

---

## 🎯 선택지

**어떤 ID를 선호하시나요?**

### A. UMIS Prefix (추천!)

```
UMIS_Observer, UMIS_Explorer, UMIS_Quantifier, UMIS_Validator, UMIS_Guardian
```

### B. 역할 명확화

```
MarketObserver, OpportunityExplorer, MarketQuantifier, DataValidator, ProcessGuardian
```

### C. 현재 유지

```
Observer, Explorer, Quantifier, Validator, Guardian
```

---

**선택해주시면 전체 백업 → 일괄 변경 진행하겠습니다!** 🚀

참고: data/ 삭제 후 재생성은 안전합니다 (YAML만 있으면 언제든 복구)
