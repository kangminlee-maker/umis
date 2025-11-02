# Agent 변수명 변경 계획

**목표:** steve → explorer 등 변수명 통일  
**위험도:** 🟡 중간 (124개 항목)  
**권장:** 단계적 안전 마이그레이션

---

## 🔍 현재 상황

### 변경 완료 ✅

```yaml
문서 (.md):
  Albert → Observer ✅
  Steve → Explorer ✅
  Bill → Quantifier ✅
  Rachel → Validator ✅
  Stewart → Guardian ✅
  
  범위: 375개 항목
  상태: 완료!
```

### 변경 필요 ⚠️

```yaml
Python 코드:
  steve → explorer
  albert → observer
  bill → quantifier
  rachel → validator
  stewart → guardian
  
  범위: 124개 항목
  위치:
    • umis_rag/agents/steve.py
    • scripts/*.py
    • 변수명, 함수명, import
```

---

## ⚠️ 위험 요소

### 1. 파일명 변경

```python
Before:
  umis_rag/agents/steve.py
  
After:
  umis_rag/agents/explorer.py

위험:
  • import 경로 깨짐
  • 기존 import문 모두 수정 필요
```

### 2. 변수명 변경

```python
Before:
  steve = create_steve_agent()
  steve.search_patterns()

After:
  explorer = create_explorer_agent()
  explorer.search_patterns()

위험:
  • 124개 항목 변경
  • 누락 시 에러
```

### 3. 함수명 변경

```python
Before:
  def create_steve_agent():
  
After:
  def create_explorer_agent():

위험:
  • 호출하는 모든 곳 수정
```

---

## 🎯 안전한 방법 (추천!)

### Option 1: 별칭 추가 (가장 안전) ⭐⭐⭐⭐⭐

```python
# umis_rag/agents/__init__.py

from umis_rag.agents.steve import SteveRAG

# 별칭 추가 (하위 호환성)
ExplorerRAG = SteveRAG
create_explorer_agent = create_steve_agent

# 둘 다 작동!
steve = create_steve_agent()  # 기존 (작동 ✅)
explorer = create_explorer_agent()  # 새로운 (작동 ✅)
```

**장점:**
```yaml
✅ 안전: 기존 코드 그대로 작동
✅ 점진적: 새 코드는 explorer 사용
✅ 하위호환: 모두 지원
✅ 위험 없음: 0%
```

**단점:**
```yaml
⚠️ 이중 유지: 두 이름 공존
```

---

### Option 2: 점진적 마이그레이션 ⭐⭐⭐⭐

**3단계 안전 전환:**

#### Step 1: 새 파일 생성 (안전!)

```bash
# 새 파일 복사
cp umis_rag/agents/steve.py umis_rag/agents/explorer.py

# 내부 변수명 변경
sed -i 's/steve/explorer/g' umis_rag/agents/explorer.py
```

#### Step 2: 별칭 추가

```python
# umis_rag/agents/__init__.py

# 기존 (유지)
from umis_rag.agents.steve import create_steve_agent

# 새로운 (추가)
from umis_rag.agents.explorer import create_explorer_agent

# 둘 다 export
__all__ = ['create_steve_agent', 'create_explorer_agent']
```

#### Step 3: 점진적 교체

```python
# 새 코드는 explorer 사용
from umis_rag.agents import create_explorer_agent
explorer = create_explorer_agent()

# 기존 코드는 그대로 (나중에 천천히 변경)
from umis_rag.agents import create_steve_agent
steve = create_steve_agent()
```

**장점:**
```yaml
✅ 안전: 기존 동작 보장
✅ 유연: 천천히 전환
✅ 테스트: 각 단계 검증
```

---

### Option 3: 일괄 변경 (위험!) ⚠️⚠️⚠️

```bash
# 모든 파일 일괄 변경
find . -name "*.py" -exec sed -i '' \
  -e 's/steve/explorer/g' \
  -e 's/albert/observer/g' \
  -e 's/bill/quantifier/g' \
  {} +

# 파일명 변경
mv umis_rag/agents/steve.py umis_rag/agents/explorer.py
```

**위험:**
```yaml
❌ 한 번에 모든 것 변경
❌ 롤백 어려움
❌ 테스트 깨질 가능성 높음
❌ 디버깅 어려움
```

**언제 사용:**
```yaml
조건:
  • 완전한 테스트 커버리지
  • 백업 완료
  • 개발 초기 (지금!)
  
  → 지금은 프로토타입이니 가능하긴 함
```

---

## 💡 최종 추천: Hybrid 접근

### Phase 1: 문서만 (완료!) ✅

```yaml
상태: ✅ 이미 완료
  • .md 파일: Observer/Explorer/...
  • .cursorrules: Observer/Explorer/...
```

### Phase 2: 별칭 추가 (즉시 가능)

```python
# umis_rag/agents/__init__.py

"""Agent 별칭 지원"""

from umis_rag.agents.steve import (
    SteveRAG as ExplorerRAG,
    create_steve_agent as create_explorer_agent
)

# 기존 이름도 유지
from umis_rag.agents.steve import SteveRAG, create_steve_agent

__all__ = [
    # 새 이름 (권장)
    'ExplorerRAG',
    'create_explorer_agent',
    
    # 기존 이름 (하위호환)
    'SteveRAG', 
    'create_steve_agent'
]
```

**Cursor에서 사용:**
```python
# 둘 다 작동!
explorer = create_explorer_agent()  # 새로운 (권장)
steve = create_steve_agent()  # 기존 (호환)
```

### Phase 3: 점진적 교체 (나중에)

```yaml
시기: 향후 개발 시
방법: 새 기능은 explorer 사용
기존: steve 그대로 유지

→ 천천히 자연스럽게 전환
```

---

## 🎯 즉시 실행 (안전!)

### Cursor에게 요청:

```
"umis_rag/agents/__init__.py에 별칭을 추가해줘.

create_steve_agent의 별칭으로 create_explorer_agent를 만들고,
둘 다 export해줘.

기존 코드는 그대로 작동하면서
새 코드는 explorer를 쓸 수 있게"
```

**AI가 자동으로:**
```python
# 별칭 추가
ExplorerRAG = SteveRAG
create_explorer_agent = create_steve_agent

# export
__all__ = ['create_explorer_agent', 'create_steve_agent']
```

**결과:**
```yaml
✅ 안전: 기존 작동 보장
✅ 새로운: explorer 사용 가능
✅ 위험: 0%

→ 완벽! ✨
```

---

## 📋 권장 실행 순서

### 지금 (안전!)

```
Cursor Composer:

"별칭 추가해줘:
 - create_steve_agent → create_explorer_agent
 - SteveRAG → ExplorerRAG
 
 둘 다 작동하게!"
```

### 나중에 (선택)

```
천천히:
  • 새 기능: explorer 사용
  • 문서: explorer 표기
  • 기존: steve 유지
  
→ 자연스러운 전환
```

---

## 🎯 최종 추천

**별칭 추가 방식 (Option 1)**

```yaml
장점:
  ✅ 안전 100%
  ✅ 즉시 가능
  ✅ 하위호환
  ✅ Cursor 한 번 요청으로 끝

단점:
  ⚠️ 두 이름 공존 (괜찮음)

추천도: ⭐⭐⭐⭐⭐
```

**Cursor에게 지금 요청하시겠어요?** 

저가 별칭 추가 코드를 작성해드릴까요? 🚀
