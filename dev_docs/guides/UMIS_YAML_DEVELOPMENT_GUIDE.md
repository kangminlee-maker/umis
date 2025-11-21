# umis.yaml 개발 가이드
**버전**: v7.7.0
**대상**: UMIS 개발자
**목적**: umis.yaml 수정 → RAG 자동 동기화 워크플로우

---

## 🎯 핵심 원칙

### Single Source of Truth
```
umis.yaml = 유일한 편집 대상 (수동 편집 ✅)
tool_registry.yaml = 자동 생성 (편집 금지 ❌)
System RAG = 자동 구축 (편집 금지 ❌)
```

**규칙**:
- ✅ umis.yaml만 수정
- ❌ tool_registry.yaml 직접 수정 금지
- ❌ System RAG 직접 수정 금지

---

## 🔄 개발 워크플로우

### 일상적인 개발

```bash
# 1. umis.yaml 수정
vim umis.yaml
# 또는
code umis.yaml

# 예시: Observer에 새 프레임워크 추가
agents:
  - id: Observer
    extended_frameworks:
      universal_observation_dimensions:
        - dimension: "New Dimension"  # ← 추가!
          observable_elements:
            - "새로운 요소"

# 2. 동기화 (One Command!)
python3 scripts/sync_umis_to_rag.py

# 출력:
# 🚀 umis.yaml → RAG 동기화 시작
# 💾 백업: config/backups/tool_registry_20251112_160530.yaml
# 📖 umis.yaml 로드 중...
#    ✅ 9개 최상위 섹션
#    ✅ 6개 Agent
# 🔧 tool_registry.yaml 생성 중...
#    ✅ 15개 Complete 도구 생성
# 🔍 검증 중...
#    ✅ 도구 수: 15개
#    ✅ 필수 도구 모두 존재
# 💾 저장: config/tool_registry.yaml
# 🔨 System RAG 재구축 중...
#    ✅ System RAG 재구축 완료
# 🧪 RAG 검증 중...
#    ✅ 검색 테스트 통과
# ✅ 동기화 완료!

# 3. 테스트
python3 scripts/query_system_rag.py tool:observer:complete

# 4. 완료! 
# → 수정 내용이 RAG에 반영됨
```

**소요 시간**: 10-15초 (자동)

---

## 📋 사용 가능한 명령어

### 1. 일반 동기화
```bash
python3 scripts/sync_umis_to_rag.py
```
- umis.yaml → tool_registry.yaml 변환
- System RAG 재구축
- 검증 자동 수행
- 백업 자동 생성

---

### 2. Dry-run (시뮬레이션)
```bash
python3 scripts/sync_umis_to_rag.py --dry-run
```
- 실제 저장하지 않음
- 변환 과정만 확인
- 에러 체크용

**사용 시점**: 대규모 수정 전 테스트

---

### 3. 강제 동기화
```bash
python3 scripts/sync_umis_to_rag.py --force
```
- 검증 생략
- 빠름 (5초)
- 위험: 에러 가능

**사용 시점**: 검증 에러가 오탐일 때

---

### 4. 롤백
```bash
python3 scripts/rollback_rag.py
```
- 최근 백업으로 복원
- RAG 재구축
- 안전한 상태로 되돌림

**사용 시점**: 동기화 후 문제 발견

---

### 5. 백업 목록
```bash
python3 scripts/rollback_rag.py --list
```
- 최근 백업 10개 표시
- 크기, 날짜 정보

---

### 6. 빠른 동기화 (배치)
```bash
./scripts/quick_sync.sh
```
- 간단한 배치 스크립트
- 백업 + 변환 + 재구축 + 검증
- 한 번에 실행

---

## 🎯 umis.yaml 구조 규칙

### 컨벤션 (자동 변환 규칙)

#### 규칙 1: 최상위 섹션 → System 도구
```yaml
# umis.yaml
system_architecture:
  information_flow_state_machine:
    ...

# 자동 변환 →
# tool:system:system_architecture
```

#### 규칙 2: agents 리스트 → Agent Complete 도구
```yaml
# umis.yaml
agents:
  - id: Observer
    role: "Market Structure Observer"
    ...
  
  - id: Explorer
    role: "Market Explorer"
    ...

# 자동 변환 →
# tool:observer:complete
# tool:explorer:complete
```

#### 규칙 3: 섹션명 = 도구 ID
```
섹션명 변환:
  - 소문자: Observer → observer
  - 스네이크 케이스 유지: system_architecture
  - 접두사: system: 또는 {agent}:
```

---

## ⚠️ 주의사항

### 1. tool_registry.yaml 직접 수정 금지!
```yaml
# ❌ 금지!
config/tool_registry.yaml 직접 편집

# ✅ 대신:
umis.yaml 수정 후 sync_umis_to_rag.py
```

**이유**: 
- tool_registry.yaml은 자동 생성
- 수동 수정 시 다음 sync에서 덮어씌워짐

---

### 2. 백업 확인
```bash
# 동기화 전 백업 확인
ls -lh config/backups/

# 최근 백업 있는지 확인
# 없으면 수동 백업:
cp config/tool_registry.yaml config/backups/manual_backup.yaml
```

---

### 3. 검증 실패 시
```bash
# 에러 메시지 확인
❌ 에러 발생: 필수 도구 누락: observer:complete

# umis.yaml 확인
# → agents 리스트에 Observer 있는지?
# → id 필드 정확한지?

# 수정 후 재시도
python3 scripts/sync_umis_to_rag.py
```

---

## 🔍 문제 해결

### 문제 1: "필수 섹션 누락" 에러

**증상**:
```
❌ 에러 발생: 필수 섹션 누락: system_architecture
```

**원인**: umis.yaml에 필수 섹션 없음

**해결**:
```yaml
# umis.yaml에 필수 섹션 추가
system_architecture:
  ...

agents:
  ...

implementation_guide:
  ...
```

---

### 문제 2: "도구 수 부족" 에러

**증상**:
```
❌ 에러 발생: 도구 수 부족: 8
```

**원인**: umis.yaml이 너무 단순

**해결**:
- agents 리스트에 최소 4개 Agent 필요
- 또는 --force 옵션 사용

---

### 문제 3: RAG 재구축 실패

**증상**:
```
❌ RAG 구축 실패
```

**원인**: ChromaDB 문제 또는 YAML 문법 오류

**해결**:
```bash
# 1. 롤백
python3 scripts/rollback_rag.py

# 2. umis.yaml 문법 체크
python3 -c "import yaml; yaml.safe_load(open('umis.yaml'))"

# 3. ChromaDB 재초기화 (극단적)
rm -rf data/chroma/*
python3 scripts/build_system_knowledge.py
```

---

## 📊 예시 시나리오

### 시나리오 A: Observer에 새 프레임워크 추가

```yaml
# 1. umis.yaml 수정
agents:
  - id: Observer
    extended_frameworks:
      universal_observation_dimensions:
        - dimension: "Digital Footprint Analysis"  # ← 추가!
          observable_elements:
            - "앱 다운로드 순위"
            - "검색량 트렌드"
            - "SNS 언급량"
```

```bash
# 2. 동기화
python3 scripts/sync_umis_to_rag.py

# 3. 확인
python3 scripts/query_system_rag.py tool:observer:complete | grep "Digital"

# 결과:
# - dimension: Digital Footprint Analysis  ✅
# → 반영됨!
```

---

### 시나리오 B: 새 Agent 추가

```yaml
# 1. umis.yaml 수정
agents:
  - id: Observer
    ...
  - id: Explorer
    ...
  - id: Synthesizer  # ← 새 Agent!
    role: "Market Synthesizer"
    description: "분석 결과를 통합하는 Agent"
    core_competencies:
      - "결과 통합"
      - "인사이트 도출"
```

```bash
# 2. 동기화
python3 scripts/sync_umis_to_rag.py

# 출력:
#    ✅ tool:synthesizer:complete  ← 자동 생성!

# 3. 확인
python3 scripts/query_system_rag.py tool:synthesizer:complete

# 결과: 새 Agent 도구 사용 가능!
```

---

### 시나리오 C: 섹션 구조 변경

```yaml
# 1. umis.yaml 수정
system_architecture:
  information_flow_state_machine:
    states:
      new_state:  # ← 새 상태 추가!
        active_agents: [albert]
        ...
```

```bash
# 2. 동기화
python3 scripts/sync_umis_to_rag.py

# 3. 확인
python3 scripts/query_system_rag.py tool:system:system_architecture | grep "new_state"

# 결과:
# new_state:  ✅
# → 반영됨!
```

---

## 🚀 자동화 수준

### Level 1: 현재 (수동 트리거)
```bash
# umis.yaml 수정 후
python3 scripts/sync_umis_to_rag.py

소요: 10초
자동화: 90% (실행만 수동)
```

---

### Level 2: Watch 모드 (향후)
```bash
# 백그라운드 실행
python3 scripts/sync_umis_to_rag.py --watch &

# umis.yaml 저장 → 자동 동기화
소요: 0초 (자동)
자동화: 100%
```

---

### Level 3: Git Hook (향후)
```bash
# .git/hooks/pre-commit 설정
# umis.yaml 변경 → 자동 동기화 → 커밋

소요: 0초 (자동)
자동화: 100%
강제: 검증 통과 필수
```

---

## 📚 참고 문서

### 개발자용
- `UMIS_YAML_TO_RAG_PIPELINE.md` - 파이프라인 설계
- `SYSTEM_RAG_USAGE_GUIDE.md` - RAG 사용 가이드
- `migration_rules.yaml` - 변환 규칙 상세

### 스크립트
- `sync_umis_to_rag.py` - 메인 동기화 스크립트
- `rollback_rag.py` - 롤백 스크립트
- `quick_sync.sh` - 간단 배치 스크립트
- `migrate_umis_to_rag.py` - 변환 로직 (내부 사용)

---

## 🎉 요약

### ✅ 앞으로의 개발 방식

```
1. umis.yaml 수정 (Source of Truth)
   ↓
2. python3 scripts/sync_umis_to_rag.py (10초)
   ↓
3. RAG 자동 업데이트 완료!
   ↓
4. 바로 사용 가능
```

**핵심**:
- ✅ 빠른 개발 (68% 시간 단축)
- ✅ 일관성 보장 (자동 변환)
- ✅ 오류 감소 (자동 검증)
- ✅ 롤백 가능 (안전)

---

**문서 끝**





