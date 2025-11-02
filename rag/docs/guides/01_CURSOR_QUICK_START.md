# Cursor로 UMIS RAG 즉시 시작하기

**대상:** 코딩 못 하는 UMIS 사용자  
**도구:** Cursor Composer만!  
**시간:** 30초

---

## ⚡ 30초 빠른 시작

### Step 1: Cursor Composer 열기

```
Cmd+I (Mac) 또는 Ctrl+I (Windows)
```

### Step 2: UMIS 분석 시작

```
@umis_guidelines_v6.2.yaml를 첨부하고:

"피아노 구독 서비스 시장 기회를 분석해줘"
```

### Step 3: AI가 자동으로

```
Observer (Observer): 시장 관찰...
  → 트리거 발견: "높은 초기 비용, 정기 사용"

Explorer (Explorer): 패턴 매칭 필요
  → [Agent 자동 실행] RAG 검색
  → subscription_model 발견!
  
Explorer: 코웨이 사례 참고하여 가설 생성...
  "피아노 구독 서비스 (월 10-15만원)..."
```

**끝!** 그게 전부입니다! 🎉

---

## 🎯 RAG가 자동으로 활용됨

### .cursorrules 자동화

**이미 설정되어 있습니다:**

```yaml
Explorer가 패턴 필요 시:
  → 자동으로 RAG 검색
  → 결과를 분석에 통합
  
데이터 추가 필요 시:
  → YAML 자동 수정
  → RAG 자동 재구축
  → 즉시 반영
```

**사용자는 대화만 하면 됩니다!** ✨

---

## 📝 자주 쓰는 명령어

### RAG 검색

```
"subscription_model 패턴을 RAG에서 검색해줘"
```

### 데이터 추가

```
"코웨이 사례에 해지율 3-5% 추가해줘"

→ AI가 자동으로:
  1. YAML 열기
  2. 위치 찾기
  3. 추가
  4. 저장
  5. RAG 재구축
  6. "✅ 완료!"
```

### RAG 재구축

```
"RAG 인덱스를 재구축해줘"

→ AI가 자동으로:
  scripts/01_convert_yaml.py
  scripts/02_build_index.py
  → "✅ 완료!"
```

### 통계 확인

```
"RAG 인덱스 통계를 보여줘"

→ Collection: umis_knowledge_base
   Documents: 54개
```

---

## 🎨 Cursor Composer 팁

### Multi-file 편집

```
"코웨이, Netflix, Spotify에 모두 전환율 데이터 추가해"

→ AI가 3개 파일 동시 수정!
→ 한 번에 재구축!
→ 효율적! ✨
```

### 컨텍스트 유지

```
분석 중:
  "이 데이터 추가"  ← 무엇인지 AI가 알고 있음
  "여기에 사례 추가"  ← 어디인지 AI가 알고 있음
  
→ 자연스러운 대화! 🎯
```

---

## 🏆 완벽한 워크플로우

```
1. Cmd+I (Composer)
2. @umis_guidelines_v6.2.yaml
3. "시장 분석해줘"
4. AI 자동 분석 (RAG 활용)
5. "데이터 추가해"
6. AI 자동 처리
7. 즉시 사용!

→ 모든 것이 대화! ✨
```

---

**다음:** `02_CURSOR_WORKFLOW.md`에서 상세 워크플로우 확인

