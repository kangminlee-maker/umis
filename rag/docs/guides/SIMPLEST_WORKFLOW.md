# 가장 가볍고 간단한 UMIS RAG 환경

## 🎯 3가지 옵션 (가벼운 순)

---

## 🥇 Option 1: IPython + %autoreload (최고 추천!)

### 특징

```yaml
가장 가벼움: ⭐⭐⭐⭐⭐
사용 = 개발: ⭐⭐⭐⭐⭐
즉시 반영: ⭐⭐⭐⭐⭐ (2초!)
복잡도: ⭐ (매우 간단)
```

### 사용법

```bash
# 1. IPython 시작
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate
ipython

# 2. 자동 리로드 설정 (한 번만)
%load_ext autoreload
%autoreload 2
```

```python
# 3. UMIS RAG 로드
from umis_rag.agents.steve import create_steve_agent

steve = create_steve_agent()
print("✅ Steve 준비!")

# 4. 검색
results = steve.search_patterns("높은 초기 비용")
print(results[0][0].page_content[:200])

# 5. YAML 수정 (VS Code에서)
# umis_business_model_patterns_v6.2.yaml 열기
# 코웨이 섹션에 데이터 추가
# Ctrl+S

# 6. 즉시 반영! (자동!)
# 다시 검색
results = steve.search_patterns("코웨이")
# → 방금 추가한 데이터 보임! ✨

# 7. 코드도 수정 가능
# umis_rag/agents/steve.py 수정
# Ctrl+S
# → 자동 리로드!
# → 즉시 사용 가능!
```

### 워크플로우

```
Terminal (IPython):          VS Code:
━━━━━━━━━━━━━━━━━━━━━━━    ━━━━━━━━━━━━━━━━━━━━━━━
steve = create_steve_agent()  
                            
검색 실행                   
→ 결과 확인                 
                            
"해지율 데이터 필요"         YAML 열기
                            churn_rate 추가
                            Ctrl+S
                            
                            (2초 대기)
                            
검색 재실행                  
→ 새 데이터 보임! ✅         
                            
"메서드 추가 필요"           steve.py 열기
                            메서드 추가
                            Ctrl+S
                            
새 메서드 사용               
→ 즉시 작동! ✅             

→ 완벽한 피드백 루프! ⚡
```

### 장점

```yaml
✅ 즉시 반영: YAML/코드 수정 → 2초 → 사용 가능
✅ 상태 유지: 변수, 객체 유지됨
✅ 실험 용이: 즉시 테스트
✅ 가벼움: 추가 설정 없음
✅ 익숙함: Python REPL
```

### 단점

```yaml
⚠️ UI 없음: 터미널만
⚠️ 히스토리: 수동 관리
```

---

## 🥈 Option 2: VS Code Interactive Python (.py with # %%)

### 특징

```yaml
가벼움: ⭐⭐⭐⭐
사용 = 개발: ⭐⭐⭐⭐⭐
즉시 반영: ⭐⭐⭐⭐
복잡도: ⭐⭐
```

### 파일 생성

```python
# umis_playground.py

# %% 설정
from umis_rag.agents.steve import create_steve_agent

steve = create_steve_agent()

# %% 패턴 검색
query = "높은 초기 비용, 정기 사용"
results = steve.search_patterns(query, top_k=2)

for i, (doc, score) in enumerate(results, 1):
    print(f"{i}. {doc.metadata['pattern_id']} ({score:.4f})")

# %% 사례 검색
cases = steve.search_cases("정수기 렌탈", "subscription_model")

for i, (doc, score) in enumerate(cases, 1):
    print(f"{i}. {doc.metadata['company']} ({score:.4f})")

# %% 실험 (자유롭게 추가)
# YAML 수정 → 이 셀 재실행 → 즉시 반영!
```

### 사용법

```
VS Code:
  1. umis_playground.py 열기
  2. 셀 실행: Shift+Enter
  3. 결과 즉시 확인
  
  4. YAML 수정 (다른 탭)
  5. 셀 재실행 → 반영!
  
  6. 코드 수정
  7. 셀 재실행 → 반영!

→ 모든 것이 VS Code 안에! ✨
```

### 장점

```yaml
✅ VS Code 통합: 하나의 환경
✅ 셀 실행: Jupyter처럼
✅ Git 친화적: .py 파일
✅ 디버깅: VS Code 디버거
```

---

## 🥉 Option 3: Streamlit (가장 예쁨)

### 특징

```yaml
가벼움: ⭐⭐⭐
사용 = 개발: ⭐⭐⭐⭐
즉시 반영: ⭐⭐⭐⭐⭐ (자동!)
복잡도: ⭐⭐⭐
```

### 파일 생성

```python
# umis_app.py

import streamlit as st
from umis_rag.agents.steve import create_steve_agent

st.title("🚀 UMIS RAG Playground")

# 사이드바: 설정
with st.sidebar:
    st.header("설정")
    agent = st.selectbox("Agent", ["Steve", "Albert", "Bill"])
    top_k = st.slider("결과 수", 1, 10, 3)

# Steve 초기화
steve = create_steve_agent()

# 검색
query = st.text_input("🔍 검색", placeholder="높은 초기 비용...")

if query:
    with st.spinner("검색 중..."):
        results = steve.search_patterns(query, top_k=top_k)
    
    st.success(f"✅ {len(results)}개 발견!")
    
    for i, (doc, score) in enumerate(results, 1):
        with st.expander(f"{i}. {doc.metadata['pattern_id']} ({score:.4f})"):
            st.write(doc.page_content[:500])
            st.json(doc.metadata)
```

### 사용법

```bash
# 1. Streamlit 설치
pip install streamlit

# 2. 실행
streamlit run umis_app.py

# 3. 브라우저 자동 오픈
# http://localhost:8501

# 4. YAML 수정
# VS Code에서 YAML 수정
# Ctrl+S

# 5. 자동 리로드!
# Streamlit이 변경 감지
# "Rerun" 버튼 클릭 또는 자동
# → 즉시 반영! ✨
```

### 장점

```yaml
✅ UI: 예쁨
✅ 자동 리로드: 파일 감지
✅ 대화형: 즉시 피드백
✅ 공유 가능: URL 공유
```

### 단점

```yaml
❌ 무거움: Streamlit 의존성
❌ 브라우저: 별도 창
```

---

## 🎯 최종 추천: IPython + autoreload

### 왜?

```yaml
가장 가벼움:
  - 추가 설치: 없음 (IPython은 기본)
  - 파일: 없음 (기존 코드만)
  - 설정: 2줄

즉시 반영:
  - YAML 수정 → 자동 리로드
  - Python 코드 수정 → 자동 리로드
  - 2초 만에 반영!

사용 = 개발:
  - 같은 환경
  - 같은 인터페이스
  - 완벽한 피드백 루프

IPython 강력함:
  - 히스토리 (↑↓)
  - 자동완성 (Tab)
  - 매직 명령어 (%timeit, %debug)
  - 결과 저장 (_1, _2, ...)
```

---

## 🚀 추천 워크플로우 (IPython)

### 초기 설정 (한 번만)

```bash
# 1. IPython 설정 파일 생성
mkdir -p ~/.ipython/profile_default/startup

# 2. 자동 설정 추가
cat > ~/.ipython/profile_default/startup/00-umis.py << 'EOF'
# UMIS RAG 자동 설정
import sys
from pathlib import Path

# 프로젝트 루트
umis_root = Path.home() / "Documents/AI_dev/umis-main"
if umis_root.exists():
    import os
    os.chdir(umis_root)
    sys.path.insert(0, str(umis_root))
    
    # 자동 리로드
    %load_ext autoreload
    %autoreload 2
    
    print(f"✅ UMIS 환경 ({umis_root})")
    print("💡 from umis_rag.agents.steve import create_steve_agent")
EOF

# 3. 별칭 추가 (~/.zshrc)
echo 'alias umis="cd ~/Documents/AI_dev/umis-main && source venv/bin/activate && ipython"' >> ~/.zshrc
source ~/.zshrc
```

### 매일 사용

```bash
# 어디서든
$ umis

# 자동으로:
# - UMIS 디렉토리로 이동
# - venv 활성화
# - IPython 시작
# - autoreload 설정됨

✅ UMIS 환경 (/Users/kangmin/Documents/AI_dev/umis-main)
💡 from umis_rag.agents.steve import create_steve_agent

In [1]:
```

### 실제 사용

```python
# Steve 생성
In [1]: from umis_rag.agents.steve import create_steve_agent

In [2]: steve = create_steve_agent()
✅ Steve 준비!

# 검색
In [3]: r = steve.search_patterns("구독")

In [4]: r[0][0].metadata['pattern_id']
Out[4]: 'subscription_model'

# (VS Code에서 YAML 수정)
# (Ctrl+S)
# (2초 대기 - autoreload)

# 재검색 (자동 반영!)
In [5]: r = steve.search_patterns("구독")

In [6]: r[0][0].page_content[:100]
Out[6]: '... 방금 추가한 내용 ...'  # ✅ 반영됨!

# 편리한 기능
In [7]: %timeit steve.search_patterns("플랫폼")
# → 성능 측정

In [8]: result = _  # 마지막 결과 저장
```

---

## 💡 더 간단한 버전: 단일 파일

### 초간단 버전

```python
# quick_search.py

from umis_rag.agents.steve import create_steve_agent

def search(query):
    steve = create_steve_agent()
    results = steve.search_patterns(query, top_k=3)
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. {doc.metadata['pattern_id']} ({score:.4f})")
        print(f"   {doc.page_content[:150]}...\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        search(" ".join(sys.argv[1:]))
    else:
        print("사용: python quick_search.py 검색어")
```

### 사용

```bash
# 검색
python quick_search.py 플랫폼 비즈니스

# YAML 수정
# VS Code에서 수정

# 재검색
python quick_search.py 플랫폼 비즈니스
# → 즉시 반영!

→ 가장 간단! ✨
```

---

## 🎯 최종 추천 비교

| 방법 | 가벼움 | 즉시반영 | 대화형 | 설정 | 추천 |
|------|--------|----------|--------|------|------|
| **IPython** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 1분 | 🥇 최고! |
| VS Code Cell | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 0분 | 🥈 좋음 |
| Streamlit | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 5분 | 🥉 예쁨 |
| 단일 파일 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | 0분 | 간단 |
| make dev | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | 5분 | 자동화 |

---

## 🏆 가장 가벼운 설정: IPython

### 전체 설정 (3분)

```bash
# 1. 별칭 추가
echo 'alias umis="cd ~/Documents/AI_dev/umis-main && source venv/bin/activate && ipython"' >> ~/.zshrc
source ~/.zshrc

# 2. IPython 프로필
mkdir -p ~/.ipython/profile_default/startup
cat > ~/.ipython/profile_default/startup/00-umis.py << 'EOF'
import sys, os
from pathlib import Path

umis = Path.home() / "Documents/AI_dev/umis-main"
if umis.exists():
    os.chdir(umis)
    sys.path.insert(0, str(umis))
    
    %load_ext autoreload
    %autoreload 2
    
    print("✅ UMIS 환경")
EOF

# 3. 끝!
```

### 사용 (매일)

```bash
# 어디서든
$ umis

# IPython 시작
✅ UMIS 환경

In [1]: from umis_rag.agents.steve import create_steve_agent
In [2]: steve = create_steve_agent()
In [3]: steve.search_patterns("구독")

# (YAML 수정)
# (자동 리로드)
# (재실행)

In [4]: steve.search_patterns("구독")
# → 변경 반영! ✅
```

---

## 🔄 피드백 루프 비교

### 기존 (복잡)

```
발견: "데이터 추가 필요"
  ↓
VS Code: YAML 수정
  ↓
Terminal: make dev (실행 중)
  ↓ (2초 대기)
Watcher: 자동 업데이트
  ↓
Cursor: 새 채팅 시작
  ↓
AI: 분석
  ↓
확인

총 시간: ~2분
단계: 6단계
```

### IPython (간단!)

```
발견: "데이터 추가 필요"
  ↓
VS Code: YAML 수정 + Ctrl+S
  ↓ (2초 자동 리로드)
IPython: 재실행 (↑ Enter)
  ↓
확인

총 시간: ~5초
단계: 2단계

→ 20배 빠름! ⚡
```

---

## 💡 실전 예시

### 시나리오: "코웨이 해지율 추가"

#### IPython 방식

```python
# IPython에서
In [1]: steve = create_steve_agent()

In [2]: r = steve.search_cases("정수기")
In [3]: r[0][0].page_content
# "... 코웨이 ... (해지율 없음)"

# 발견: 해지율 필요!

# VS Code (다른 모니터)
# umis_business_model_patterns_v6.2.yaml
# 찾기: 코웨이
# 추가:
#   churn_rate: "3-5% (업계 평균)"
# Ctrl+S

# (2초 대기 - autoreload)

# IPython에서 즉시
In [4]: r = steve.search_cases("정수기")
In [5]: r[0][0].page_content
# "... 코웨이 ... churn_rate: 3-5% ..."
# ✅ 반영됨!

# 즉시 사용
In [6]: "코웨이 해지율 3-5%로 피아노도 유사 예상"

→ 5초 만에 발견 → 수정 → 사용! ⚡
```

---

## 🎯 최종 추천

### 가장 가볍고 간단한 환경:

**IPython + autoreload**

```yaml
설정: 3분 (한 번만)
사용: `umis` 명령 하나
피드백: 5초 (발견 → 수정 → 반영)
복잡도: 최소
강력함: 최대
```

### 설치

```bash
# 1. 별칭 설정
echo 'alias umis="cd ~/Documents/AI_dev/umis-main && source venv/bin/activate && ipython"' >> ~/.zshrc
source ~/.zshrc

# 2. 사용
umis

# 끝!
```

---

## 📊 비교 요약

```
복잡한 환경 (기존):
  - make dev (Watcher)
  - Cursor (AI 분석)
  - Terminal (스크립트)
  - VS Code (수정)
  → 4개 도구
  
간단한 환경 (추천):
  - IPython (검색 + 실험)
  - VS Code (수정)
  → 2개 도구
  
가장 간단:
  - IPython만!
  - 검색, 수정, 재실행 모두 IPython
  → 1개 도구!
```

---

## 결론

**IPython + autoreload = 완벽한 인라인 어셈블러!**

```
✅ 가장 가벼움
✅ 가장 간단함
✅ 가장 빠른 피드백 (5초)
✅ 즉시 시작 가능

→ 지금 바로:
   $ umis
```

설정하시겠어요? 🚀

