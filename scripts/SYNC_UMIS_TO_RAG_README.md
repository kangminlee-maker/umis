# sync_umis_to_rag.py 사용 가이드

**버전**: v7.11.1  
**업데이트**: 2025-11-26

---

## 📋 목적

`umis.yaml`의 변경 사항을 자동으로 `tool_registry.yaml`과 System RAG에 동기화합니다.

## 🎯 생성되는 도구

### 총 15개 (v7.11.1)

```yaml
System 도구 (9개):
  - tool:system:system_architecture
  - tool:system:system
  - tool:system:adaptive_intelligence_system
  - tool:system:proactive_monitoring
  - tool:system:support_validation_system
  - tool:system:data_integrity_system
  - tool:system:roles
  - tool:system:implementation_guide
  - tool:system:agents (전체 Agent)

Complete 도구 (6개):
  - tool:observer:complete
  - tool:explorer:complete
  - tool:quantifier:complete
  - tool:validator:complete
  - tool:guardian:complete
  - tool:estimator:complete
```

**Note**: Task 도구는 v7.11.1에서 제거됨 (`CONTEXT_WINDOW_STRATEGY.md` 참조)

---

## 🚀 사용법

### 1. 일반 실행

```bash
python3 scripts/sync_umis_to_rag.py
```

**동작**:
1. `config/tool_registry.yaml` 백업
2. `umis.yaml` 로드 및 검증
3. 15개 도구 생성
4. `tool_registry.yaml` 저장
5. System RAG 재구축 (`build_system_knowledge.py`)
6. 검증 테스트

### 2. Dry-run (시뮬레이션)

```bash
python3 scripts/sync_umis_to_rag.py --dry-run
```

**동작**:
- 실제 저장하지 않고 시뮬레이션만
- 생성될 도구 목록 확인
- 검증 체크

### 3. 강제 실행 (검증 생략)

```bash
python3 scripts/sync_umis_to_rag.py --force
```

**주의**: 검증을 건너뛰므로 신중히 사용

---

## 📊 프로세스

```
┌─────────────────┐
│ 1. umis.yaml    │
│    변경         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 2. 백업         │
│  (자동)         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 3. 도구 생성    │
│  (15개)         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 4. 검증         │
│  (자동)         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 5. 저장         │
│  tool_registry  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 6. RAG 재구축   │
│  (자동)         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 7. 검증         │
│  (자동)         │
└────────┬────────┘
         │
         ↓
       완료!
```

---

## ✅ 검증 항목

1. **도구 수**: 최소 10개 이상
2. **필수 도구**: system:system_architecture, observer:complete, explorer:complete
3. **Content 크기**: 각 도구 최소 100자 이상

---

## 🔧 백업

### 자동 백업

모든 실행 시 `config/backups/` 폴더에 자동 백업:

```
config/backups/tool_registry_20251126_103045.yaml
```

### 수동 롤백

```bash
cp config/backups/tool_registry_YYYYMMDD_HHMMSS.yaml config/tool_registry.yaml
python3 scripts/build_system_knowledge.py
```

---

## 🐛 트러블슈팅

### 에러: "필수 섹션 누락"

**원인**: `umis.yaml`에 `system_architecture` 또는 `agents` 섹션이 없음

**해결**: `umis.yaml` 구조 확인

### 에러: "도구 수 부족"

**원인**: 생성된 도구가 10개 미만

**해결**: `umis.yaml`의 `agents` 섹션 확인

### 에러: "RAG 구축 실패"

**원인**: `build_system_knowledge.py` 실행 실패

**해결**:
```bash
python3 scripts/build_system_knowledge.py
```

### 에러: "검색 테스트 통과 실패"

**원인**: System RAG Collection 문제

**해결**:
```bash
# Collection 재구축
python3 scripts/build_system_knowledge.py

# 검증
python3 scripts/query_system_rag.py --stats
```

---

## 📝 예시 출력

```
🚀 umis.yaml → RAG 동기화 시작

💾 백업: config/backups/tool_registry_20251126_103045.yaml

📖 umis.yaml 로드 중...
   ✅ 9개 최상위 섹션
   ✅ 6개 Agent

🔧 tool_registry.yaml 생성 중...
   ✅ tool:system:system_architecture
   ✅ tool:system:system
   ...
   ✅ tool:estimator:complete

   총 15개 도구 생성 (System + Complete)
   - System 도구: 9개
   - Complete 도구: 6개

🔍 검증 중...
   ✅ 도구 수: 15개
   ✅ 필수 도구 모두 존재
   ✅ 모든 도구 Content 정상

💾 저장 중...
   ✅ config/tool_registry.yaml

🔨 System RAG 재구축 중...
   ✅ System RAG 재구축 완료

🧪 RAG 검증 중...
   ✅ 검색 테스트 통과

✅ 동기화 완료!

================================================================================
다음 단계:
  1. python3 scripts/query_system_rag.py --list (도구 목록 확인)
  2. python3 scripts/query_system_rag.py tool:observer:complete (테스트)
================================================================================
```

---

## 🔗 관련 문서

- **CONTEXT_WINDOW_STRATEGY.md**: Task 도구 제거 결정 근거
- **TASK_TOOLS_DECISION.md**: v7.11.1 결정 요약
- **docs/guides/SYSTEM_RAG_GUIDE.md**: System RAG 사용 가이드

---

**작성**: 2025-11-26  
**버전**: v7.11.1
