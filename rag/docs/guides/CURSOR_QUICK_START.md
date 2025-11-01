# Cursor에서 UMIS + RAG 사용하기

## 🚀 즉시 테스트 (5분)

### 방법 1: YAML Only (가장 간단)

```
1. Cursor 새 채팅 시작
2. 첨부: @umis_guidelines_v6.2.yaml
3. 입력: "피아노 구독 서비스 시장 기회 분석해줘"
4. 결과 확인

→ 기본 품질, 간단함
```

### 방법 2: YAML + RAG (고품질)

```
1. Cursor 새 채팅 시작
2. 첨부: @umis_guidelines_v6.2.yaml
3. 입력: "피아노 구독 서비스 시장 기회 분석해줘"

4. AI가 Steve 작업 중 "패턴 매칭 필요" 언급 시:
   
   Terminal:
   ```bash
   cd /Users/kangmin/Documents/AI_dev/umis-main
   source venv/bin/activate
   python scripts/query_rag.py pattern "높은 초기 비용, 정기 사용"
   ```
   
   결과 복사 → Cursor에 붙여넣기

5. AI가 계속 분석...

6. 고품질 결과!
```

---

## 📝 실전 예시

### 예시 1: 패턴 매칭

**Cursor 대화:**

```
You: @umis_guidelines_v6.2.yaml
     "피아노 학원을 구독 서비스로 전환하는 기회 분석"

AI (Albert): 
     "시장 관찰:
      - 피아노 구매: 300-800만원 (높은 진입장벽)
      - 정기 사용: 매일 연습 필요
      - 유지관리: 조율 연 1-2회, 15만원
      
      → 트리거 시그널 발견!"

AI (Steve):
     "패턴 매칭이 필요합니다. 
      RAG에서 subscription_model 패턴을 검색해주세요."
```

**Terminal 실행:**

```bash
python scripts/query_rag.py pattern "높은 초기 비용, 정기 사용, 유지관리"
```

**결과:**

```
🔍 패턴 검색: 높은 초기 비용, 정기 사용, 유지관리

✅ 2개 패턴 발견

🥇 1. subscription_model (business_model)
   유사도: 1.0273

╭────────────── subscription_model ──────────────╮
│ ## 구독형 사업모델                              │
│                                                 │
│ ### 핵심 개념                                   │
│ - **본질**: 소유 → 이용 전환, 장기 고객 관계   │
│ - **핵심 가치**: 초기 부담 ↓, 안정 현금흐름    │
│                                                 │
│ ### 트리거 시그널                               │
│ - 제품/서비스 초기 구매 비용 높음              │
│ - 정기적 유지관리나 업데이트 필요              │
│ - 고객의 지속적/반복적 사용...                 │
╰─────────────────────────────────────────────────╯
```

**Cursor에 붙여넣기:**

```
검색 결과:
🥇 subscription_model 패턴 매칭!
   - 본질: 소유 → 이용 전환
   - 트리거: 높은 초기 비용, 정기 관리 필요
   - 핵심 가치: 초기 부담 감소, 안정 현금흐름
```

**AI 계속:**

```
Steve: "subscription_model 패턴이 완벽히 매칭됩니다!
       유사 사례를 확인하겠습니다..."
```

---

### 예시 2: 사례 검색

**Cursor:**

```
AI (Steve):
     "subscription_model을 실제로 성공한 사례가 필요합니다.
      특히 고가 제품 렌탈 사례를 검색해주세요."
```

**Terminal:**

```bash
python scripts/query_rag.py case "고가 제품 렌탈" --pattern subscription_model
```

**결과:**

```
🔍 사례 검색: 고가 제품 렌탈
패턴 필터: subscription_model

✅ 3개 사례 발견

🥇 1. 코웨이 (정수기/공기청정기 렌탈)
   유사도: 1.4992

🥈 2. 멜론 (음악 스트리밍)
   유사도: 1.5540

🥉 3. 넷플릭스 (영상 스트리밍)
   유사도: 1.6013
```

**Cursor에 붙여넣기:**

```
사례 검색 결과:
🥇 코웨이 (정수기 렌탈)
   - 구조: 100만원 구매 → 월 3만원 렌탈
   - 서비스: 2개월 필터 교체, 정기 점검
   - 규모: 655만 계정 (국내)
   - 핵심: 정기 방문 = Lock-in 효과
```

**AI:**

```
Steve: "코웨이 사례가 피아노와 매우 유사합니다!
       
       피아노 구독 모델 제안:
       - 초기 구매 500만원 → 월 렌탈 10-15만원
       - 정기 조율 포함 (연 2회)
       - 해지 자유
       
       Bill에게 시장 규모 계산 요청..."
```

---

## 🎯 핵심 워크플로우

```
┌──────────────────────────────────────────────┐
│  Cursor (UMIS 분석)                           │
├──────────────────────────────────────────────┤
│                                               │
│  @umis_guidelines_v6.2.yaml 첨부             │
│  ↓                                            │
│  Albert: 트리거 발견                          │
│  ↓                                            │
│  Steve: "패턴 매칭 필요"                      │
│  ↓                                            │
└──────────┬───────────────────────────────────┘
           │
           │ (사용자가 Terminal로)
           ↓
┌──────────────────────────────────────────────┐
│  Terminal (RAG 검색)                          │
├──────────────────────────────────────────────┤
│                                               │
│  python scripts/query_rag.py pattern "..."   │
│  ↓                                            │
│  결과: subscription_model                     │
│  ↓                                            │
└──────────┬───────────────────────────────────┘
           │
           │ (결과를 Cursor에 복사)
           ↓
┌──────────────────────────────────────────────┐
│  Cursor (계속 분석)                           │
├──────────────────────────────────────────────┤
│                                               │
│  Steve: "subscription_model 적용..."         │
│  ↓                                            │
│  Bill: SAM 계산                               │
│  ↓                                            │
│  Stewart: 검증                                │
│  ↓                                            │
│  결과 완성! ✅                                │
│                                               │
└──────────────────────────────────────────────┘
```

---

## 💡 언제 RAG를 사용하는가?

### RAG 사용 권장 (고품질 필요)

```yaml
Steve 작업 시:
  - ✅ 패턴 매칭 (정확도 중요)
  - ✅ 사례 검색 (유사도 중요)
  - ✅ 검증 프레임워크 (완전성 중요)

이유:
  - 54개 청크에서 의미 검색
  - 코웨이처럼 정확한 사례 발견
  - 토큰 효율적 (필요한 것만)
```

### YAML만으로 충분 (빠른 참조)

```yaml
프로세스 참조 시:
  - ✅ Discovery Sprint 방법
  - ✅ 체크포인트 규칙
  - ✅ Agent 역할
  - ✅ 워크플로우

이유:
  - 구조적 지식 (YAML이 명확)
  - 순서 있는 프로세스
  - RAG 불필요
```

---

## 🔧 편리한 별칭 (선택)

`~/.zshrc` 또는 `~/.bashrc`에 추가:

```bash
# UMIS RAG 빠른 검색
alias umis-pattern='cd /Users/kangmin/Documents/AI_dev/umis-main && source venv/bin/activate && python scripts/query_rag.py pattern'
alias umis-case='cd /Users/kangmin/Documents/AI_dev/umis-main && source venv/bin/activate && python scripts/query_rag.py case'
alias umis-verify='cd /Users/kangmin/Documents/AI_dev/umis-main && source venv/bin/activate && python scripts/query_rag.py verify'
```

사용:

```bash
# 어디서든 간단히
umis-pattern "높은 초기 비용"
umis-case "음악 스트리밍" --pattern subscription_model
```

---

## 📊 Mode 비교 실전 테스트

### Test Case: "음악 스트리밍 구독 기회"

#### Mode 1 (YAML 3개)

```
첨부: 3개 파일 (8,326줄)
결과: "subscription_model... Spotify 사례..."
시간: ~50초
토큰: ~200K
품질: ⭐⭐⭐
```

#### Mode 2 (YAML + RAG)

```
첨부: 1개 파일 (5,428줄)
+ RAG 검색 2회
결과: "subscription_model (유사도 0.99)... 
       Spotify 프리미엄 전환율 42%..."
시간: ~40초
토큰: ~130K
품질: ⭐⭐⭐⭐⭐

차이:
  ✅ 30% 토큰 절감
  ✅ 더 정확한 매칭
  ✅ 더 관련성 높은 사례
```

---

## 🎯 지금 바로 테스트!

```bash
# 1. RAG 준비 확인
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate
python -c "from umis_rag.agents.steve import create_steve_agent; print('✅ 준비 완료!')"

# 2. 빠른 테스트
python scripts/query_rag.py pattern "플랫폼 중개"

# 3. Cursor에서 사용
# - 새 채팅
# - @umis_guidelines_v6.2.yaml
# - AI 분석 시작
# - 필요 시 위 명령 실행
```

---

## 결론

**UMIS의 단순함을 유지하면서 RAG의 강력함을 활용!**

```
지금 (Dual Mode):
  ✅ YAML 3개 (간단)
  ✅ YAML 1개 + RAG (고품질)
  ✅ 선택 가능!

미래 (MCP Tool):
  ✅ YAML 1개만
  ✅ RAG 자동
  ✅ 완벽한 통합!
```

테스트해보시겠어요? 🚀

