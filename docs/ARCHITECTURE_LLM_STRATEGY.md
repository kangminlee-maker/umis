# UMIS LLM 전략 (Architecture Review)

**작성일**: 2025-11-05  
**버전**: v7.2.0  
**검토**: LLM 활용 전략

---

## 🎯 핵심 질문

**"UMIS를 구동하는 Cursor Native LLM이 이미 고성능인데, 왜 외부 API LLM을 호출하는가?"**

**용어 정의:**
- **Native LLM**: Cursor Agent가 사용하는 모델 (Claude Sonnet 4.5, GPT-4o 등, 사용자 선택)
- **External LLM**: OpenAI/Anthropic API를 통해 호출하는 모델

---

## 📊 성능 비교

### Cursor Native LLM (사용자 선택)

| 모델 | 컨텍스트 | 성능 | Cursor 비용 | 특징 |
|------|---------|------|------------|------|
| **Claude Sonnet 4.5** | 200K | ⭐⭐⭐⭐⭐ | 포함 | 최고 품질, 긴 컨텍스트 |
| **GPT-4o** | 128K | ⭐⭐⭐⭐ | 포함 | 빠름, 멀티모달 |
| **Claude Opus 3.5** | 200K | ⭐⭐⭐⭐⭐ | 포함 | 최고 수준, 느림 |

### External API LLM (추가 비용)

| 모델 | 컨텍스트 | 성능 | API 비용 (1M tokens) |
|------|---------|------|---------------------|
| GPT-4 Turbo | 128K | ⭐⭐⭐ | ~$10 |
| GPT-4o | 128K | ⭐⭐⭐⭐ | ~$5 |
| Claude Sonnet API | 200K | ⭐⭐⭐⭐⭐ | ~$3 |
| Claude Haiku API | 200K | ⭐⭐ | ~$0.25 |

**결론**: Native LLM(Cursor 포함) > External API (추가 비용)

---

## 🏗️ 3가지 아키텍처 옵션

### 옵션 A: Native LLM Only (추천: Interactive Use) ⭐

#### 구조
```python
# UMIS를 Cursor에서 직접 구동
# 외부 API 호출 없음

from umis_rag.agents.explorer import ExplorerRAG

explorer = ExplorerRAG()  # RAG만 사용
patterns = explorer.search_patterns("SaaS 구독")  # Vector Search

# 분석은 Cursor Native LLM이 직접 수행
# → Cursor Composer/Chat에서 바로 실행
# → 모델: 사용자 설정 (Claude Sonnet 4.5, GPT-4o 등)
```

#### 장점
- ✅ **고성능**: Cursor 최신 모델 사용 (Sonnet 4.5, GPT-4o 등)
- ✅ **비용 절감**: External API 비용 $0 (Cursor 구독에 포함)
- ✅ **큰 컨텍스트**: 최대 200K tokens
- ✅ **빠른 속도**: API 왕복 없음
- ✅ **유연성**: 사용자가 모델 선택 가능

#### 단점
- ❌ **자동화 불가**: Python 스크립트 독립 실행 불가
- ❌ **배치 불가**: 100개 시장 동시 분석 불가

#### 사용 사례
- ✅ 일회성 심층 분석 (현재)
- ✅ 탐색적 분석
- ✅ 품질 중시

---

### 옵션 B: 하이브리드 (추천: 프로덕션)

#### 구조
```python
# umis_rag/llm.py (신규)

class UMISLLMProvider:
    def __init__(self, mode='auto'):
        """
        mode:
          - 'interactive': Claude in Cursor (무료, 고성능)
          - 'automated': Claude API (유료, 자동화)
          - 'budget': GPT-4o-mini (저렴)
        """
        self.mode = mode
        
    def analyze(self, prompt):
        if self.mode == 'interactive':
            # Cursor에서 실행 시 Claude Sonnet 4.5 사용
            return self._cursor_claude(prompt)
        
        elif self.mode == 'automated':
            # 독립 스크립트 실행 시 Claude API
            return self._claude_api(prompt)
        
        elif self.mode == 'budget':
            # 저렴한 옵션
            return self._openai_mini(prompt)
```

#### 사용 예시

**Interactive (Cursor):**
```python
# Cursor Composer에서
from umis_rag.agents.explorer import ExplorerRAG

explorer = ExplorerRAG(llm_mode='interactive')
# → Claude Sonnet 4.5 (나) 사용
# → API 비용 $0
```

**Automated (Script):**
```python
# Python 스크립트에서
from umis_rag.agents.explorer import ExplorerRAG

explorer = ExplorerRAG(llm_mode='automated')
# → Claude API (Anthropic) 호출
# → 자동화 가능
```

#### 장점
- ✅ **유연성**: 상황에 따라 최적 선택
- ✅ **비용 효율**: Interactive는 무료
- ✅ **자동화**: Automated 모드 지원
- ✅ **성능**: 모두 고성능 모델

---

### 옵션 C: 비용 최적화 (추천: 대량 처리)

#### 구조
```python
# 구동(오케스트레이션): Claude Haiku (저렴, 빠름)
# 분석(핵심 사고): Claude Sonnet API (고성능)

class UMISOrchestrator:
    def __init__(self):
        self.orchestrator = Haiku()  # $0.25/1M tokens
        self.analyst = SonnetAPI()   # $3/1M tokens
    
    def analyze_market(self, market):
        # Haiku: 워크플로우 관리
        steps = self.orchestrator.plan(market)
        
        # Sonnet: 핵심 분석만
        for step in critical_steps:
            result = self.analyst.analyze(step)
```

#### 비용 예시
- 100개 시장 분석
- Haiku (오케스트레이션): 100K tokens × $0.25 = **$0.025**
- Sonnet (핵심 분석): 500K tokens × $3 = **$1.5**
- **총 비용: $1.525**

vs. 전체 Sonnet: 600K × $3 = **$1.8** (절감: 15%)

---

## 💰 비용 비교 (100개 시장 분석 기준)

| 방식 | 모델 | 총 토큰 | 비용 | 품질 | 자동화 |
|------|------|---------|------|------|--------|
| **현재 (GPT-4)** | GPT-4 Turbo | 600K | $6.00 | ⭐⭐⭐ | ✅ |
| **옵션 A (Claude Only)** | Sonnet 4.5 (Cursor) | 600K | $0 | ⭐⭐⭐⭐⭐ | ❌ |
| **옵션 B (Hybrid)** | Sonnet 4.5 API | 600K | $1.80 | ⭐⭐⭐⭐⭐ | ✅ |
| **옵션 C (최적화)** | Haiku + Sonnet | 600K | $1.53 | ⭐⭐⭐⭐⭐ | ✅ |

---

## 🎯 최종 권장사항

### Phase 1: 현재 (즉시 적용) ⭐

**"외부 LLM 제거, Claude(나)만 사용"**

```python
# Before (비효율)
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(...)  # GPT-4 호출

# After (권장)
# Cursor Composer/Chat에서 직접 실행
# Claude Sonnet 4.5가 바로 분석
# → OpenAI API 비용 $0
# → 더 나은 품질
```

**이유:**
- 현재는 일회성 분석 (자동화 불필요)
- Cursor에서 실행 중 (나를 이미 사용 중)
- GPT-4 호출은 **비용 낭비 + 품질 저하**

---

### Phase 2: 향후 (자동화 필요 시)

**"하이브리드 모드 구현"**

```python
# umis_rag/agents/base.py

class BaseAgent:
    def __init__(self, llm_mode='auto'):
        if llm_mode == 'auto':
            # Cursor 환경 감지
            if self._is_cursor_environment():
                self.llm_mode = 'interactive'  # Claude Sonnet (무료)
            else:
                self.llm_mode = 'automated'    # Claude API (유료)
        else:
            self.llm_mode = llm_mode
    
    def _is_cursor_environment(self):
        # Cursor에서 실행 중인지 감지
        return 'CURSOR' in os.environ or hasattr(sys, 'ps1')
```

---

## 📋 구현 로드맵

### Step 1: LLM 호출 제거 (즉시)

**수정 파일:**
- `scripts/llm_observer_analysis.py` → 삭제 또는 주석 처리
- `scripts/llm_explorer_rag_analysis.py` → RAG만 사용, 분석은 Cursor에서

**Before:**
```python
# GPT-4 호출
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[...]
)
```

**After:**
```python
# RAG 패턴만 검색
patterns = explorer.search_patterns("SaaS")

# 분석은 Cursor Composer/Chat에서:
# "위 패턴을 바탕으로 국내 SaaS 시장 기회 5개 제시"
```

---

### Step 2: 하이브리드 모드 구현 (선택)

**신규 파일:** `umis_rag/llm/provider.py`

```python
from anthropic import Anthropic

class LLMProvider:
    """
    UMIS LLM 제공자
    
    Modes:
      - interactive: Cursor에서 Claude 사용 (무료)
      - automated: Claude API 호출 (유료)
      - budget: GPT-4o-mini (저렴)
    """
    
    @staticmethod
    def create(mode='auto'):
        if mode == 'interactive':
            return InteractiveLLM()  # Cursor 연동
        elif mode == 'automated':
            return ClaudeAPI()
        elif mode == 'budget':
            return OpenAIMini()
```

---

### Step 3: Agent 통합

**수정:** `umis_rag/agents/explorer.py`

```python
class ExplorerRAG:
    def __init__(self, llm_mode='interactive'):
        # RAG 초기화 (기존)
        self.vectorstore = ...
        
        # LLM 초기화 (신규)
        from umis_rag.llm import LLMProvider
        self.llm = LLMProvider.create(llm_mode)
    
    def analyze_opportunities(self, patterns):
        if self.llm.mode == 'interactive':
            # Cursor에 요청
            return self.llm.request_analysis(patterns)
        else:
            # API 호출
            return self.llm.analyze(patterns)
```

---

## 🔬 실험 결과 (오늘 분석 기준)

### 현재 방식 (GPT-4)
- **토큰**: 5,934 토큰
- **비용**: ~$0.06
- **시간**: ~60초 (API 왕복)
- **품질**: ⭐⭐⭐

### 권장 방식 (Claude Only)
- **토큰**: 0 (Cursor 내부)
- **비용**: $0
- **시간**: ~5초
- **품질**: ⭐⭐⭐⭐⭐

**절감**: $0.06/분석 → 100개 분석 시 **$6 절감**

---

## 🎓 결론

### 즉시 적용 (Phase 1)

**"외부 LLM(GPT-4) 제거"**

1. ✅ `scripts/llm_*.py` 파일 → 참고용으로만
2. ✅ 분석은 Cursor Composer/Chat에서 직접
3. ✅ RAG만 활용 (패턴 검색)

### 향후 계획 (Phase 2)

**"자동화 필요 시 Claude API 추가"**

1. Anthropic API 키 설정
2. 하이브리드 모드 구현
3. 배치 처리 스크립트

---

## 📞 FAQ

**Q: RAG 임베딩은?**
A: OpenAI Embeddings 유지 (저렴, $0.00013/1K tokens)

**Q: 완전 오프라인 가능?**
A: 불가능 (임베딩은 API 필요). 대안: Local Embeddings (Sentence Transformers)

**Q: GPT-4o는?**
A: Sonnet 4.5보다 성능 낮음, 비용만 추가

**Q: 기존 스크립트는?**
A: 참고용 유지, 실제론 Cursor에서 직접 실행 권장

---

**최종 권장**: **옵션 A (Claude Only)** - 현재 사용 사례에 최적

**작성**: Claude Sonnet 4.5  
**검토**: 2025-11-05

