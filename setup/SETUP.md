# UMIS v7.11.0 초기 설정

**버전**: v7.11.0 (6-Agent + 4-Stage Fusion + LLM Abstraction)  
**업데이트**: 2025-11-26

**대상:** 처음 사용하는 사용자  
**소요:** 5분

---

## 🤖 AI 자동 설치 (권장)

Cursor나 AI Assistant를 사용 중이라면:

```
"UMIS 설치해줘" 또는 "@setup"
```

AI가 자동으로:
1. `setup.py` 실행
2. 패키지 설치
3. .env 파일 생성
4. RAG 인덱스 빌드
5. 완료 확인

**AI 가이드**: `AI_SETUP_GUIDE.md` 참조

---

## 💻 수동 설치

또는 아래 단계를 직접 실행:

---

## 1️⃣ Repository Clone

```bash
git clone -b alpha https://github.com/kangminlee-maker/umis
cd umis
```

---

## 2️⃣ OpenAI API 키 설정

### .env 파일 생성

```bash
# env.template을 .env로 복사
cp env.template .env
```

### API 키 입력

```
.env 파일 열기 (Cursor 또는 텍스트 편집기)

OPENAI_API_KEY=your-api-key-here
→ 자신의 OpenAI API 키로 변경!
```

**API 키 받기:**
- https://platform.openai.com/api-keys
- Sign up → Create API Key
- 복사 → .env에 붙여넣기

**자세한 가이드:** `ENV_SETUP_GUIDE.md`

---

## 3️⃣ Vector DB 생성

**옵션 A: Cursor로 (추천!)**

```
Cursor (Cmd+I):

"RAG 인덱스를 구축해줘"

→ AI가 자동 실행!
```

**옵션 B: 터미널로**

```bash
python scripts/02_build_index.py --agent explorer
```

**소요:** 1분  
**비용:** $0.006

---

## 4️⃣ 즉시 사용!

```
Cursor Composer (Cmd+I):

umis.yaml 첨부

"@Steve, 음악 스트리밍 구독 서비스 시장 분석해줘"
```

**끝!** 🎉

---

## 💡 파일 설명

### 사용자가 수정하는 파일

```
✅ config/agent_names.yaml
   → Agent 이름 커스터마이징
   
✅ umis.yaml 등
   → 데이터 추가 (Cursor가 도움)
```

### Cursor가 사용하는 파일

```
📂 scripts/
   → RAG 검색 스크립트
   → Cursor Agent 모드가 자동 실행
   → 사용자는 건드리지 않음

📂 umis_rag/
   → Python 패키지
   → scripts/에서 사용
   → 사용자는 건드리지 않음

📄 .cursorrules
   → Cursor 자동화 규칙
   → Git 포함 (모든 사용자 동일)
```

### 개인 파일 (.gitignore)

```
❌ .env
   → OpenAI API 키 (개인)
   → Git 제외
   
❌ docs/market_analysis/
   → 개인 분석 결과물
   → Git 제외

❌ data/chroma/
   → Vector DB (재생성 가능)
   → Git 제외 (2.4MB)
```

---

## 🎯 요약

**최소 설정:**
1. API 키 (.env) - 30초
2. 인덱스 구축 - 1분

**총:** 2분

**사용:** Cursor (Cmd+I)만!

