# UMIS 사용 방법 비교

## 🎯 3가지 사용 모드

---

## Mode 1: YAML Only (기존 방식)

### 사용 방법

```
Cursor 채팅에 첨부:
  @umis_guidelines_v6.2.yaml
  @umis_business_model_patterns_v6.2.yaml
  @umis_disruption_patterns_v6.2.yaml

메시지:
  "피아노 구독 서비스 시장 분석해줘"
```

### 장점

```yaml
✅ 간단: 파일 첨부만
✅ 즉시: 설정 불필요
✅ 투명: 모든 것이 YAML에
✅ 수정: YAML 편집으로 즉시 반영
```

### 단점

```yaml
❌ 토큰: 8,000+ 줄 (약 200K 토큰)
❌ 느림: 전체를 읽어야 함
❌ 비효율: 필요 없는 것도 읽음
❌ 검색: 순차 탐색 (느림)
```

### 언제 사용?

```
- 빠른 1회성 분석
- RAG 설정 안 됨
- 간단한 프로젝트
```

---

## Mode 2: YAML + RAG (Manual)

### 사용 방법

```
Cursor 채팅에 첨부:
  @umis_guidelines_v6.2.yaml (메인만!)

메시지:
  "피아노 구독 서비스 시장 분석해줘"

AI 작업 중:
  Albert: "트리거 발견: 높은 초기 비용"
  
  AI: "Python 실행 필요"
  → python scripts/query_rag.py "높은 초기 비용"
  → subscription_model 반환
  
  Steve: "subscription_model 적용..."
```

### 장점

```yaml
✅ 효율: 5,428줄만 (약 120K 토큰)
✅ 정확: RAG 의미 검색
✅ 학습: 과거 프로젝트 활용
✅ 품질: 고급 검증 (Graph)
```

### 단점

```yaml
⚠️ 수동: Python 스크립트 실행 필요
⚠️ 설정: RAG 인덱스 구축 필요
⚠️ 복잡: 두 시스템 관리
```

### 언제 사용?

```
- 반복 프로젝트
- 대용량 데이터
- 고품질 필요
- RAG 설정 완료됨
```

---

## Mode 3: YAML + RAG Tool (미래, 이상적!) ⭐

### 사용 방법

```
Cursor 채팅에 첨부:
  @umis_guidelines_v6.2_rag_enabled.yaml (1개만!)

메시지:
  "피아노 구독 서비스 시장 분석해줘"

AI가 자동으로:
  1. YAML 읽기
  2. Albert 작업
  3. 트리거 발견
  4. [Tool 자동 호출] search_patterns()
  5. [결과 통합] subscription_model
  6. Steve 분석 계속...
  
→ 사용자는 RAG 몰라도 됨! ✨
```

### 장점

```yaml
✅✅ 간단: YAML 1개만!
✅✅ 자동: RAG Tool 자동 사용
✅✅ 효율: 필요한 것만 검색
✅✅ 품질: RAG 고급 기능
✅✅ 투명: 기존 경험 유지
```

### 단점

```yaml
⚠️ 개발: MCP Tool API 필요 (1-2주)
⚠️ 설정: 백그라운드 RAG 서버
```

### 언제 사용?

```
- MCP Tool 개발 완료 후
- 모든 프로젝트 (기본값)
- 최상의 경험
```

---

## 📊 비교표

| 항목 | Mode 1 (YAML) | Mode 2 (Manual) | Mode 3 (Tool) |
|------|--------------|-----------------|---------------|
| **첨부 파일** | 3개 | 1개 | 1개 |
| **토큰 사용** | ~200K | ~120K | ~120K |
| **설정 필요** | 없음 | RAG 인덱스 | MCP Tool |
| **RAG 활용** | 없음 | 수동 | 자동 |
| **사용 난이도** | ⭐ 쉬움 | ⭐⭐⭐ 어려움 | ⭐ 쉬움 |
| **분석 품질** | ⭐⭐⭐ 기본 | ⭐⭐⭐⭐⭐ 최고 | ⭐⭐⭐⭐⭐ 최고 |
| **개발 상태** | ✅ 완료 | ✅ 완료 | 🔄 1-2주 필요 |

---

## 🎯 실전 시나리오: "피아노 구독 서비스"

### Mode 1 (YAML Only)

```
[사용자]
@umis_guidelines_v6.2.yaml
@umis_business_model_patterns_v6.2.yaml
@umis_disruption_patterns_v6.2.yaml

"피아노 구독 서비스 시장 분석해줘"

[AI]
(8,326줄 읽음... 30초)

Albert: "높은 초기 비용 관찰"
(YAML에서 subscription_model 찾음... 10초)

Steve: "subscription_model 적용"
(YAML에서 코웨이 사례 찾음... 10초)

결과: "코웨이와 유사한 구독 모델..."

토큰: ~200K
시간: ~50초
품질: ⭐⭐⭐
```

### Mode 2 (YAML + Manual RAG)

```
[사용자]
@umis_guidelines_v6.2.yaml

"피아노 구독 서비스 시장 분석해줘"

[AI]
(5,428줄 읽음... 15초)

Albert: "높은 초기 비용 관찰"

AI: "패턴 매칭 필요. Python 실행:"
```python
from umis_rag.agents.steve import create_steve_agent
steve = create_steve_agent()
results = steve.search_patterns("높은 초기 비용, 정기 사용")
```

(결과: subscription_model, 유사도 1.03)

Steve: "subscription_model 적용"

AI: "사례 검색 필요. Python 실행:"
```python
cases = steve.search_cases("정수기 렌탈", "subscription_model")
```

(결과: 코웨이, 넷플릭스, 멜론)

결과: "코웨이 정수기 렌탈 (100만원 → 월 3만원)과
       매우 유사한 구조..."

토큰: ~130K
시간: ~40초
품질: ⭐⭐⭐⭐⭐
```

### Mode 3 (YAML + RAG Tool) - 미래

```
[사용자]
@umis_guidelines_v6.2_rag_enabled.yaml

"피아노 구독 서비스 시장 분석해줘"

[AI]
(5,428줄 + RAG 힌트 읽음... 15초)

Albert: "높은 초기 비용 관찰"

AI: (내부적으로)
[Tool: search_patterns("높은 초기 비용")]
→ subscription_model

Steve: "subscription_model 적용"

AI: (내부적으로)
[Tool: search_cases("코웨이")]
→ 코웨이 사례

결과: "코웨이 정수기 렌탈..."

토큰: ~125K
시간: ~35초
품질: ⭐⭐⭐⭐⭐

사용자는 Mode 1과 동일한 경험!
하지만 Mode 2의 품질! ✨
```

---

## 💡 지금 당장 사용 가능한 방법

### 추천: Mode 2 (수동이지만 작동함!)

```bash
# 1. Cursor에 YAML 1개만 첨부
@umis_guidelines_v6.2.yaml

# 2. 분석 요청
"피아노 구독 서비스 시장 분석해줘"

# 3. AI가 패턴 매칭 필요하다고 하면
"다음 Python 코드 실행해줘:"

python -c "
from umis_rag.agents.steve import create_steve_agent
steve = create_steve_agent()
results = steve.search_patterns('높은 초기 비용, 정기 사용', top_k=2)

for i, (doc, score) in enumerate(results, 1):
    print(f'{i}. {doc.metadata[\"pattern_id\"]} (유사도: {score:.4f})')
    print(doc.page_content[:200])
    print()
"

# 4. 결과를 AI에게 붙여넣기
subscription_model이 매칭되었습니다:
  - 본질: 소유 → 이용 전환
  - 트리거: 높은 초기 비용, 정기 관리 필요
  - 사례: 코웨이 (100만원 → 월 3만원)

# 5. AI가 계속 분석
```

---

## 🚀 Migration Path (진화 경로)

### Phase 1: 현재 (Mode 1)

```yaml
현재 사용:
  - YAML 3개 첨부
  - 모든 것이 YAML에
  
유지:
  - 당분간 이 방식 사용 가능
  - 익숙하고 안정적
```

### Phase 2: Dual Mode (즉시 가능)

```yaml
선택 사용:
  - 간단한 분석: Mode 1 (YAML 3개)
  - 정밀 분석: Mode 2 (YAML 1개 + Python RAG)
  
비교:
  - 두 방식 품질 비교
  - RAG 가치 검증
  - 점진적 학습
```

### Phase 3: MCP Tool (1-2주 후)

```yaml
완성:
  - Mode 3 구현
  - YAML 1개만 첨부
  - RAG 자동 활용
  
경험:
  - Mode 1의 간단함
  - Mode 2의 품질
  - 최상의 통합! ✨
```

---

## 💡 실제 사용 예시

### 시나리오: Cursor에서 UMIS 사용

#### 현재 방식 (Mode 1)

```
1. 새 채팅 시작
2. 파일 첨부:
   - umis_guidelines_v6.2.yaml
   - umis_business_model_patterns_v6.2.yaml  
   - umis_disruption_patterns_v6.2.yaml

3. "피아노 구독 서비스 분석"

4. AI가 3개 파일 모두 읽고 분석

5. 결과 받음
```

#### 추천 방식 (Mode 2) - 지금 가능!

```
1. 새 채팅 시작
2. 파일 첨부:
   - umis_guidelines_v6.2.yaml (1개만!)

3. "피아노 구독 서비스 분석"

4. AI가 프로세스 시작
   - Albert: 트리거 발견
   - Steve: "패턴 매칭 필요"
   
5. AI: "RAG 검색 실행해주세요:"
   ```python
   # 터미널에서 실행
   python -c "..."
   ```

6. 결과를 채팅에 붙여넣기

7. AI가 결과 통합하여 계속 분석

8. 고품질 결과 받음
```

#### 미래 방식 (Mode 3) - MCP Tool 개발 후

```
1. 새 채팅 시작
2. 파일 첨부:
   - umis_guidelines_v6.2_rag_enabled.yaml

3. "피아노 구독 서비스 분석"

4. AI가 자동으로 모든 것 처리
   - YAML 읽기
   - RAG Tool 자동 호출
   - 통합 분석

5. 고품질 결과 받음

→ Mode 1처럼 간단!
→ Mode 2처럼 고품질!
```

---

## 🎯 당신에게 추천

### 지금 당장

**Option: Dual Mode (Mode 1 + Mode 2)**

```yaml
간단한 분석:
  - Mode 1 (YAML 3개)
  - 빠르게 시작
  
정밀 분석:
  - Mode 2 (YAML 1개 + RAG)
  - Python 스크립트 활용
  - 고품질

비교:
  - 두 방식으로 같은 프로젝트 분석
  - 품질 차이 체감
  - RAG 가치 검증
```

### 다음 2주

**개발: MCP Tool (Mode 3)**

```yaml
구현:
  Week 1: 기본 Tool 4개
    - search_patterns
    - search_cases
    - verify_data
    - check_validation
  
  Week 2: 고급 Tool 2개
    - detect_circular
    - check_goal_alignment

테스트:
  - Cursor 통합
  - E2E 시나리오
  - 사용자 경험 검증

완성:
  - YAML 1개만 첨부
  - RAG 자동 활용
  - 완벽한 통합!
```

---

## 📋 Quick Start (지금 바로 테스트!)

### Test 1: YAML Only

```bash
# Cursor 새 채팅
@umis_guidelines_v6.2.yaml
@umis_business_model_patterns_v6.2.yaml

"음악 스트리밍 구독 서비스 기회 분석"

→ 기본 품질 확인
```

### Test 2: YAML + RAG

```bash
# Terminal에서 RAG 준비 확인
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate
python -c "from umis_rag.agents.steve import create_steve_agent; print('✅ RAG 준비됨')"

# Cursor 새 채팅
@umis_guidelines_v6.2.yaml

"음악 스트리밍 구독 서비스 기회 분석"

# AI가 패턴 필요 시
→ Python 코드 실행
→ 결과 붙여넣기

→ 고품질 확인
```

### Test 3: 품질 비교

```
같은 프로젝트를 두 방식으로:
  - Test 1 결과 저장
  - Test 2 결과 저장
  - 비교:
    - 패턴 매칭 정확도
    - 사례 관련성
    - 분석 깊이
    - 소요 시간
```

---

## 🎯 결론

**당신의 고민 해결:**

```yaml
문제:
  "RAG가 독립 서비스로 가고 있다"
  "UMIS의 단순함을 잃고 있다"

해결:
  즉시 (Dual Mode):
    ✅ YAML 중심 유지
    ✅ RAG는 선택적
    ✅ 두 방식 비교 가능
  
  미래 (MCP Tool):
    ✅ YAML 1개만 첨부
    ✅ RAG 자동 활용
    ✅ 완벽한 통합
    ✅ 사용자는 기존 경험 유지
```

**UMIS의 단순함 + RAG의 강력함 = 완벽한 균형!** 🎯

Dual Mode로 먼저 테스트해보시겠어요?

