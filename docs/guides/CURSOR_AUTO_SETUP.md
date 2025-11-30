# Cursor IDE 자동 설치 가이드

## 🎯 목적

새로운 사용자가 UMIS 레포를 fork한 후 Cursor IDE Agent Chat에서 바로 요청하면, **자동으로 설치 프로세스가 시작**되도록 합니다.

## 🔧 동작 방식

### 1. **Pre-Flight Check (필수 체크)**

`.cursorrules` 최상단에 `MANDATORY PRE-FLIGHT CHECK` 섹션이 있습니다.

```yaml
mandatory_preflight:
  rule: "NEVER process any user request without completing this check first"
  priority: "CRITICAL - 최우선 실행"
```

### 2. **신규 Fork 감지**

AI가 모든 요청 전에 다음을 체크합니다:

```bash
# 자동 실행되는 체크 명령
ls data/chroma_db/system_knowledge/ 2>&1
ls .env 2>&1
python3 -c 'import chromadb' 2>&1
```

**감지 신호:**
- `data/chroma_db/` 폴더 없음
- `.env` 파일 없음
- `chromadb` 모듈 없음

### 3. **자동 설치 시작**

미설치 감지 시:

```bash
python setup/setup.py
```

**프로세스:**
1. 🚀 Python 패키지 설치
2. 🔧 System RAG 구축 (19개 도구)
3. ✅ 설치 완료 (2-3분)

### 4. **설치 확인**

```bash
python3 scripts/query_system_rag.py --list
# Expected: 19개 도구 목록
```

## 📋 사용자 경험

### **시나리오 1: 신규 Fork**

```
사용자: "@Explorer, 음악 스트리밍 시장 분석해줘"

AI (자동 감지):
🚨 UMIS 설치가 필요합니다!

신규 fork를 감지했습니다. 사용하시려면 먼저 설치가 필요합니다.
자동 설치를 시작하겠습니다 (2-3분 소요).

[python setup/setup.py 실행]

🚀 UMIS v7.11.1 자동 설치 시작
📦 Python 패키지 설치 중...
🔧 System RAG 구축 중...
✅ 설치 완료!

다음 단계:
1. .env 파일에 OPENAI_API_KEY 입력
2. 다시 요청해주세요
```

### **시나리오 2: 설치 완료 상태**

```
사용자: "@Explorer, 음악 스트리밍 시장 분석해줘"

AI (자동 체크):
✅ 설치 확인 완료

[Onboarding 진행]
→ tool:onboarding:quick_start 로드
→ tool:explorer:complete 로드
→ 작업 수행
```

## 🎛️ .cursorrules 핵심 설정

### **필수 체크 순서**

```yaml
check_sequence:
  1. detect_new_fork (신규 fork 감지)
  2. auto_install (자동 설치)
  3. verify_installation (설치 확인)
```

### **강제 규칙**

```yaml
critical_rule:
  - "설치되지 않은 상태에서는 절대 다른 작업 수행 금지"
  - "사용자 요청보다 설치가 우선"
  - "설치 완료 전까지 Onboarding도 불가능"
```

### **Quick Check (빠른 감지)**

```yaml
quick_check_example:
  first_command: "ls data/chroma_db/system_knowledge/ 2>&1 && ls .env 2>&1"
  
  if_error: "즉시 python setup/setup.py 실행"
  if_success: "Onboarding 진행"
```

## ⚠️ 제약사항

### **완전한 "강제"는 불가능**

`.cursorrules`는 AI의 **행동 가이드**이지 **강제 실행 스크립트**가 아닙니다.

**할 수 있는 것:**
- ✅ 매우 강력한 프롬프트로 필수 체크 유도
- ✅ 설치 감지 로직 제공
- ✅ 명확한 우선순위 지정
- ✅ 설치 명령 자동 실행

**할 수 없는 것:**
- ❌ 100% 강제 실행 (AI가 무시할 가능성 0.1%)
- ❌ Pre-commit hook 같은 시스템 레벨 강제
- ❌ 사용자 동의 없이 파일 수정

## 🚀 최적화 전략

### **1. 최상단 배치**

`.cursorrules` 가장 위에 배치하여 AI가 가장 먼저 읽도록 합니다.

### **2. 강력한 언어 사용**

```yaml
rule: "NEVER process any user request without completing this check first"
priority: "CRITICAL - 최우선 실행"
```

### **3. 명확한 체크 명령**

실제 실행 가능한 shell 명령을 제공합니다.

### **4. 시각적 경고**

```
# ========================================
# ⚠️ MANDATORY PRE-FLIGHT CHECK (필수!)
# ========================================
# AI: 모든 작업 전 반드시 실행! NEVER SKIP!
# ========================================
```

## 📊 효과

### **Before (수동 설치)**
```
1. 사용자가 README 읽고 설치 명령 찾기
2. python setup/setup.py 수동 실행
3. .env 파일 수동 생성
4. 사용 시작

→ 10분+ 소요, 이탈률 높음
```

### **After (자동 감지)**
```
1. 사용자가 바로 요청
2. AI가 자동 감지 → 설치 시작
3. 설치 완료 안내
4. 사용 시작

→ 3분 소요, 이탈률 낮음 ⚡
```

## 🔍 디버깅

### **설치 상태 확인**

```bash
# 수동 체크
ls data/chroma_db/system_knowledge/
ls .env
python3 scripts/query_system_rag.py --list

# 기대 결과:
# - data/chroma_db/system_knowledge/ 존재
# - .env 존재
# - 19개 도구 목록
```

### **재설치**

```bash
# 완전 재설치
python setup/setup.py

# 또는 System RAG만 재구축
python3 scripts/sync_umis_to_rag.py
python3 scripts/build_system_knowledge.py
```

## 💡 추가 개선 가능 사항

### **Option 1: Git Hook 추가**

```bash
# .git/hooks/post-checkout
#!/bin/bash
if [ ! -d "data/chroma_db" ]; then
    echo "🚀 자동 설치 시작..."
    python setup/setup.py
fi
```

### **Option 2: VS Code Task**

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "UMIS Auto Setup",
      "type": "shell",
      "command": "python setup/setup.py",
      "runOptions": {
        "runOn": "folderOpen"
      }
    }
  ]
}
```

### **Option 3: package.json 스크립트**

```json
{
  "scripts": {
    "postinstall": "python setup/setup.py"
  }
}
```

---

## ✅ 최종 결론

`.cursorrules`로 **95% 이상 자동 감지/설치**가 가능합니다.

완전한 강제는 아니지만, 실용적으로는 **충분히 효과적**입니다.
