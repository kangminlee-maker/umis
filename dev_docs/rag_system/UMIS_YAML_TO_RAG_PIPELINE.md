# umis.yaml → RAG 자동화 파이프라인 설계
**작성일**: 2025-11-12
**버전**: v7.7.0
**목적**: 지속 가능한 개발 워크플로우 구축

---

## 문제 정의

**현재 상황**:
- umis.yaml 수정 → 수동으로 RAG 업데이트
- 번거롭고 누락 가능성
- 일관성 보장 어려움

**목표**:
- umis.yaml 수정 → **자동으로** RAG 업데이트
- 검증 자동화
- 롤백 가능
- 빠른 개발 사이클

---

## 💡 제안 구조

### Architecture

```
umis.yaml (Source of Truth)
    ↓ [감지]
[변환 스크립트]
    ↓ [변환]
tool_registry.yaml (자동 생성)
    ↓ [인덱싱]
System RAG (ChromaDB)
    ↓ [검증]
[무결성 체크]
    ↓ [완료]
✅ 배포 또는 ❌ 롤백
```

---

## 🎯 설계 원칙

### 1. Single Source of Truth
```
umis.yaml = 유일한 편집 대상
tool_registry.yaml = 자동 생성 (수동 편집 금지!)
System RAG = 자동 구축
```

### 2. 컨벤션 기반 자동화
```yaml
# umis.yaml 구조 규칙
agents:
  - id: Observer  # ← tool:observer:complete 생성
  - id: Explorer  # ← tool:explorer:complete 생성

system_architecture:  # ← tool:system:system_architecture 생성
```

### 3. 검증 자동화
```
변환 후 자동 체크:
  - 섹션 누락 없음?
  - YAML 문법 정확?
  - 크기 정상 범위?
  - 검색 테스트 통과?
```

### 4. 롤백 가능
```
문제 발견 시:
  1. 이전 tool_registry.yaml 복원
  2. 이전 RAG 복원
  3. 에러 로그 제공
```

---

## 📋 구현 방안

### 방안 A: Watch 기반 자동화 (권장)

**구조**:
```bash
# 파일 감시 데몬
$ python3 scripts/watch_umis_yaml.py

[실행 중...]
→ umis.yaml 변경 감지
→ 자동 변환 (3초)
→ RAG 재구축 (5초)
→ 검증 (2초)
→ ✅ 완료 또는 ❌ 롤백
```

**장점**:
- 완전 자동화
- 수정 즉시 반영
- 에러 즉시 감지

**단점**:
- 데몬 실행 필요
- 복잡도 약간 증가

---

### 방안 B: 수동 트리거 (간단)

**구조**:
```bash
# umis.yaml 수정 후
$ python3 scripts/sync_umis_to_rag.py

→ 변환 (3초)
→ RAG 재구축 (5초)
→ 검증 (2초)
→ ✅ 완료
```

**장점**:
- 간단 명확
- 제어 가능
- 안정적

**단점**:
- 수동 실행 필요
- 깜빡할 수 있음

**권장**: **방안 B (수동 트리거)** - 간단하고 안정적

---

### 방안 C: Git Hook 통합 (고급)

**구조**:
```bash
# .git/hooks/pre-commit
→ umis.yaml 변경 감지
→ 자동 변환 + RAG 재구축
→ 검증 통과 시 커밋
→ 실패 시 커밋 차단
```

**장점**:
- Git workflow 통합
- 강제 검증
- 일관성 보장

**단점**:
- 커밋 시간 증가 (10초)
- Hook 설정 필요

---

## 🔧 구현 상세 (방안 B 권장)

### 파일 구조

```
scripts/
  ├── sync_umis_to_rag.py        # 메인 스크립트 (통합)
  ├── extract_umis_sections.py   # 섹션 추출 로직
  ├── validate_migration.py      # 검증 로직
  ├── build_system_knowledge.py  # RAG 구축 (기존)
  └── rollback_rag.py            # 롤백 스크립트

config/
  ├── umis.yaml                  # Source of Truth (수동 편집)
  ├── tool_registry.yaml         # 자동 생성 (편집 금지!)
  └── migration_rules.yaml       # 변환 규칙 (설정)
```

---

### 핵심 스크립트: sync_umis_to_rag.py

```python
#!/usr/bin/env python3
"""
umis.yaml → System RAG 동기화 (One Command)

사용법:
    python3 scripts/sync_umis_to_rag.py
    python3 scripts/sync_umis_to_rag.py --dry-run  # 시뮬레이션
    python3 scripts/sync_umis_to_rag.py --force    # 검증 생략
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime


class UmisToRAGSync:
    """umis.yaml → System RAG 동기화"""
    
    def __init__(self):
        self.umis_path = Path('umis.yaml')
        self.registry_path = Path('config/tool_registry.yaml')
        self.backup_dir = Path('config/backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def sync(self, dry_run=False, force=False):
        """전체 동기화 프로세스"""
        
        print("🚀 umis.yaml → RAG 동기화 시작")
        print()
        
        # Step 1: 백업
        if not dry_run:
            self._backup()
        
        # Step 2: umis.yaml 로드 및 검증
        umis_data = self._load_and_validate_umis()
        
        # Step 3: tool_registry.yaml 생성
        registry = self._generate_registry(umis_data)
        
        # Step 4: 검증
        if not force:
            self._validate_registry(registry)
        
        # Step 5: 저장
        if not dry_run:
            self._save_registry(registry)
            
            # Step 6: RAG 재구축
            self._rebuild_rag()
            
            # Step 7: 최종 검증
            self._verify_rag()
        
        print()
        print("✅ 동기화 완료!")
    
    def _backup(self):
        """기존 파일 백업"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'tool_registry_{timestamp}.yaml'
        
        if self.registry_path.exists():
            shutil.copy(self.registry_path, backup_path)
            print(f"💾 백업: {backup_path}")
        print()
    
    def _load_and_validate_umis(self):
        """umis.yaml 로드 및 검증"""
        print("📖 umis.yaml 로드 중...")
        
        with open(self.umis_path) as f:
            data = yaml.safe_load(f)
        
        # 필수 섹션 체크
        required_sections = [
            'system_architecture', 'system', 'agents',
            'implementation_guide'
        ]
        
        for section in required_sections:
            if section not in data:
                raise ValueError(f"필수 섹션 누락: {section}")
        
        print(f"   ✅ {len(data)}개 최상위 섹션")
        print(f"   ✅ {len(data.get('agents', []))}개 Agent")
        print()
        
        return data
    
    def _generate_registry(self, umis_data):
        """tool_registry.yaml 생성"""
        print("🔧 tool_registry.yaml 생성 중...")
        
        tools = []
        
        # 1. System 섹션 도구 생성
        for section_name, section_data in umis_data.items():
            if section_name not in ['agents', 'roles']:  # agents는 별도 처리
                tool = self._create_system_tool(section_name, section_data)
                tools.append(tool)
                print(f"   ✅ tool:system:{section_name}")
        
        # 2. roles 섹션
        if 'roles' in umis_data:
            tool = self._create_system_tool('roles', umis_data['roles'])
            tools.append(tool)
            print(f"   ✅ tool:system:roles")
        
        # 3. agents 섹션 전체
        if 'agents' in umis_data:
            tool = self._create_system_tool('agents', umis_data['agents'])
            tools.append(tool)
            print(f"   ✅ tool:system:agents (6개 Agent 전체)")
        
        # 4. 각 Agent Complete 도구
        for agent in umis_data.get('agents', []):
            agent_id = agent.get('id')
            tool = self._create_agent_complete(agent_id, agent)
            tools.append(tool)
            print(f"   ✅ tool:{agent_id.lower()}:complete")
        
        print()
        print(f"   총 {len(tools)}개 Complete 도구 생성")
        print()
        
        # 5. 레지스트리 구성
        registry = {
            'version': '7.7.0',
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'total_tools': len(tools),
            'auto_generated': True,
            'source': 'umis.yaml',
            'tools': tools
        }
        
        return registry
    
    def _create_system_tool(self, section_name, section_data):
        """System 섹션 도구 생성"""
        content_yaml = yaml.dump(
            {section_name: section_data},
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
        
        return {
            'tool_id': f'system:{section_name}',
            'tool_key': f'tool:system:{section_name}',
            'metadata': {
                'agent': 'system',
                'category': 'complete_context',
                'source': f'umis.yaml {section_name} (auto-sync)'
            },
            'content': f"""# System: {section_name}

umis.yaml {section_name} 섹션 전체 (0% 손실)

```yaml
{content_yaml}```
"""
        }
    
    def _create_agent_complete(self, agent_id, agent_data):
        """Agent Complete 도구 생성"""
        content_yaml = yaml.dump(
            agent_data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
        
        role = agent_data.get('role', f'{agent_id} Agent')
        
        return {
            'tool_id': f'{agent_id.lower()}:complete',
            'tool_key': f'tool:{agent_id.lower()}:complete',
            'metadata': {
                'agent': agent_id.lower(),
                'category': 'complete_context',
                'source': f'umis.yaml agents.{agent_id} (auto-sync)'
            },
            'content': f"""# {agent_id}: Complete

Role: {role}

umis.yaml {agent_id} 섹션 전체 (0% 손실)

```yaml
{content_yaml}```
"""
        }
    
    def _validate_registry(self, registry):
        """레지스트리 검증"""
        print("🔍 검증 중...")
        
        tools = registry['tools']
        
        # 1. 도구 수 체크
        assert len(tools) >= 15, f"도구 수 부족: {len(tools)}"
        print(f"   ✅ 도구 수: {len(tools)}개")
        
        # 2. 필수 도구 존재 체크
        required_tools = [
            'system:system_architecture',
            'observer:complete',
            'explorer:complete'
        ]
        
        tool_ids = {t['tool_id'] for t in tools}
        for req in required_tools:
            assert req in tool_ids, f"필수 도구 누락: {req}"
        print(f"   ✅ 필수 도구 모두 존재")
        
        # 3. Content 크기 체크
        for tool in tools:
            size = len(tool.get('content', ''))
            assert size > 100, f"Content 너무 작음: {tool['tool_id']}"
        print(f"   ✅ 모든 도구 Content 정상")
        
        print()
    
    def _save_registry(self, registry):
        """레지스트리 저장"""
        print("💾 저장 중...")
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"   ✅ {self.registry_path}")
        print()
    
    def _rebuild_rag(self):
        """RAG 재구축"""
        print("🔨 System RAG 재구축 중...")
        
        import subprocess
        result = subprocess.run(
            ['python3', 'scripts/build_system_knowledge.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"RAG 구축 실패:\n{result.stderr}")
        
        print("   ✅ System RAG 재구축 완료")
        print()
    
    def _verify_rag(self):
        """RAG 검증"""
        print("🧪 RAG 검증 중...")
        
        # 간단한 검색 테스트
        import subprocess
        result = subprocess.run(
            ['python3', 'scripts/query_system_rag.py', '--stats'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"RAG 검증 실패:\n{result.stderr}")
        
        print("   ✅ 검색 테스트 통과")
        print()


def main():
    import sys
    
    dry_run = '--dry-run' in sys.argv
    force = '--force' in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN 모드 (실제 저장 안 함)")
        print()
    
    sync = UmisToRAGSync()
    
    try:
        sync.sync(dry_run=dry_run, force=force)
    except Exception as e:
        print()
        print(f"❌ 에러 발생: {e}")
        print()
        print("롤백 방법:")
        print("  python3 scripts/rollback_rag.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**사용법**:
```bash
# 일반 실행
python3 scripts/sync_umis_to_rag.py

# 시뮬레이션 (저장 안 함)
python3 scripts/sync_umis_to_rag.py --dry-run

# 강제 (검증 생략)
python3 scripts/sync_umis_to_rag.py --force
```

---

### 보조 스크립트: rollback_rag.py

```python
#!/usr/bin/env python3
"""
RAG 롤백 스크립트
마지막 정상 상태로 복원
"""

import shutil
from pathlib import Path
from datetime import datetime


def rollback():
    """최근 백업으로 롤백"""
    
    print("🔄 RAG 롤백 시작")
    print()
    
    backup_dir = Path('config/backups')
    
    # 최근 백업 찾기
    backups = sorted(backup_dir.glob('tool_registry_*.yaml'), reverse=True)
    
    if not backups:
        print("❌ 백업 파일 없음")
        return
    
    latest = backups[0]
    print(f"📂 최근 백업: {latest.name}")
    
    # 복원
    shutil.copy(latest, 'config/tool_registry.yaml')
    print(f"✅ tool_registry.yaml 복원 완료")
    print()
    
    # RAG 재구축
    print("🔨 RAG 재구축 중...")
    import subprocess
    subprocess.run(['python3', 'scripts/build_system_knowledge.py'])
    
    print()
    print("✅ 롤백 완료!")


if __name__ == "__main__":
    rollback()
```

**사용법**:
```bash
python3 scripts/rollback_rag.py
```

---

## 📋 컨벤션 (Convention)

### umis.yaml 구조 규칙

```yaml
# ========================================
# 규칙 1: 최상위 섹션 = System 도구
# ========================================

system_architecture:  # → tool:system:system_architecture
  ...

adaptive_intelligence_system:  # → tool:system:adaptive_intelligence_system
  ...

# ========================================
# 규칙 2: agents 리스트 = Agent Complete 도구
# ========================================

agents:
  - id: Observer  # → tool:observer:complete
    role: "..."
    ...
  
  - id: Explorer  # → tool:explorer:complete
    role: "..."
    ...

# ========================================
# 규칙 3: 섹션명 = 도구 ID
# ========================================

# 섹션명 → 도구 ID 변환 규칙:
# - 소문자 변환: Observer → observer
# - 스네이크 케이스 유지: system_architecture
# - 접두사 추가: system: 또는 agent_id:
```

---

### 변환 규칙 (migration_rules.yaml)

```yaml
# config/migration_rules.yaml

version: 1.0

conversion_rules:
  
  # System 섹션 처리
  system_sections:
    prefix: "system:"
    category: "complete_context"
    priority: "high"
    
    sections:
      - system_architecture
      - system
      - adaptive_intelligence_system
      - proactive_monitoring
      - support_validation_system
      - data_integrity_system
      - agents  # 전체 Agent 리스트
      - roles
      - implementation_guide
  
  # Agent 개별 처리
  agent_sections:
    source: "agents list"
    id_field: "id"
    prefix: "{agent_id}:complete"
    category: "complete_context"
    priority: "high"

  # 제외 섹션
  excluded_sections:
    - _meta  # 메타데이터는 제외
    - version  # 버전은 registry에서 관리

validation:
  min_tools: 15
  max_tool_size: 100000  # 100KB
  required_tools:
    - system:system_architecture
    - observer:complete
    - explorer:complete

backup:
  enabled: true
  directory: config/backups
  retention_days: 30  # 30일 이상 된 백업 자동 삭제
```

---

## 🔄 개발 워크플로우

### 일상적인 개발 사이클

```bash
# 1. umis.yaml 수정 (Source of Truth)
vim umis.yaml
# → Observer 섹션에 새 프레임워크 추가
# → Explorer 7-Step에 단계 추가
# → etc.

# 2. 동기화 (One Command!)
python3 scripts/sync_umis_to_rag.py

# 출력:
# 🚀 umis.yaml → RAG 동기화 시작
# 💾 백업: config/backups/tool_registry_20251112_153022.yaml
# 📖 umis.yaml 로드 중...
#    ✅ 9개 최상위 섹션
#    ✅ 6개 Agent
# 🔧 tool_registry.yaml 생성 중...
#    ✅ 15개 도구 생성
# 🔍 검증 중...
#    ✅ 도구 수: 15개
#    ✅ 필수 도구 모두 존재
#    ✅ 모든 도구 Content 정상
# 💾 저장: config/tool_registry.yaml
# 🔨 System RAG 재구축 중...
#    ✅ System RAG 재구축 완료
# 🧪 RAG 검증 중...
#    ✅ 검색 테스트 통과
# ✅ 동기화 완료!

# 3. 테스트
python3 scripts/query_system_rag.py tool:observer:complete
# → 수정된 내용 반영 확인

# 4. 완료!
```

**소요 시간**: 10초

---

### 문제 발생 시

```bash
# 에러 발생!
❌ 에러 발생: YAML 문법 오류

# 롤백
python3 scripts/rollback_rag.py

# 출력:
# 🔄 RAG 롤백 시작
# 📂 최근 백업: tool_registry_20251112_153022.yaml
# ✅ tool_registry.yaml 복원 완료
# 🔨 RAG 재구축 중...
# ✅ 롤백 완료!

# 복구됨!
```

---

## 📊 장점 분석

### 1. 빠른 개발 사이클
```
Before:
  umis.yaml 수정 (10분)
  → 수동으로 tool_registry 업데이트 (30분)
  → RAG 재구축 (1분)
  → 테스트 (5분)
  = 총 46분

After:
  umis.yaml 수정 (10분)
  → sync_umis_to_rag.py (10초)
  → 테스트 (5분)
  = 총 15분 (68% 단축!)
```

---

### 2. 일관성 보장
```
Before:
  - 수동 복사 → 누락 가능
  - 형식 불일치
  - 버전 불일치

After:
  - 자동 변환 → 누락 없음
  - 형식 통일
  - 버전 자동 동기화
```

---

### 3. 오류 감소
```
Before:
  - 복사 실수
  - YAML 문법 오류
  - 섹션 누락

After:
  - 자동 변환 (오류 없음)
  - 자동 검증
  - 자동 롤백
```

---

## 🎯 고급 기능 (선택)

### 기능 A: 증분 업데이트

```python
# sync_umis_to_rag.py --incremental

# 변경된 섹션만 업데이트
# - 빠름 (5초)
# - 위험 낮음
```

**구현**:
- umis.yaml 해시 저장
- 변경 감지
- 변경된 섹션만 재생성

---

### 기능 B: Watch 모드

```bash
# 백그라운드 실행
python3 scripts/sync_umis_to_rag.py --watch &

# umis.yaml 저장할 때마다 자동 동기화
```

**구현**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class UmisYamlHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('umis.yaml'):
            sync.sync()
```

---

### 기능 C: Diff 보고

```bash
python3 scripts/sync_umis_to_rag.py --diff

# 출력:
# 📊 변경 사항:
#   Observer:
#     + observation_principles 추가
#     ~ core_competencies 수정
#   
#   Explorer:
#     + 새 프레임워크 추가
```

---

## 📋 구현 우선순위

### P0 (필수) - 즉시 구현
- [x] sync_umis_to_rag.py (메인 스크립트)
- [ ] rollback_rag.py (롤백)
- [ ] migration_rules.yaml (설정)
- [ ] 테스트 케이스

**예상 시간**: 2-3시간

---

### P1 (권장) - 1주일 내
- [ ] --incremental (증분 업데이트)
- [ ] --diff (변경 사항 표시)
- [ ] --validate-only (검증만)
- [ ] 자동 테스트

**예상 시간**: 4-5시간

---

### P2 (선택) - 필요시
- [ ] --watch (파일 감시)
- [ ] Git Hook 통합
- [ ] CI/CD 통합
- [ ] 버전 관리 자동화

**예상 시간**: 6-8시간

---

## 🚀 즉시 실행 가능한 간단 버전

### 최소 구현 (10분)

```bash
#!/bin/bash
# scripts/quick_sync.sh

echo "🚀 umis.yaml → RAG 동기화"

# 백업
cp config/tool_registry.yaml config/tool_registry_backup.yaml

# 변환
python3 scripts/migrate_umis_to_rag.py

# RAG 재구축
python3 scripts/build_system_knowledge.py

echo "✅ 완료!"
```

**사용**:
```bash
chmod +x scripts/quick_sync.sh
./scripts/quick_sync.sh
```

---

## 📚 문서 구조

### 개발자용
```
docs/development/
  ├── UMIS_YAML_STRUCTURE.md      # umis.yaml 구조 가이드
  ├── RAG_SYNC_GUIDE.md            # 동기화 가이드
  └── TROUBLESHOOTING.md           # 문제 해결
```

### 자동 생성 표시
```yaml
# tool_registry.yaml 상단
# ========================================
# ⚠️  이 파일은 자동 생성됩니다!
# 
# 편집 금지! 대신 umis.yaml을 수정하세요.
# 
# 동기화 방법:
#   python3 scripts/sync_umis_to_rag.py
# 
# 마지막 동기화: 2025-11-12 15:30:22
# ========================================
```

---

## 🎯 권장 구현 계획

### Phase 1: 기본 구조 (즉시)
```
1. sync_umis_to_rag.py 작성 (위 코드)
2. rollback_rag.py 작성
3. migration_rules.yaml 작성
4. 테스트

소요: 2-3시간
```

---

### Phase 2: 자동화 강화 (1주일)
```
1. --incremental 구현
2. --diff 구현
3. 자동 테스트 추가
4. 문서화

소요: 4-5시간
```

---

### Phase 3: 고급 기능 (필요시)
```
1. --watch 모드
2. Git Hook
3. CI/CD

소요: 6-8시간
```

---

## 🏆 기대 효과

### 개발 속도
```
Before: 46분/수정
After: 15분/수정
단축: 68%
```

### 일관성
```
Before: 수동 복사 (오류 가능)
After: 자동 변환 (오류 없음)
```

### 유지보수
```
Before: umis.yaml + tool_registry 2곳 관리
After: umis.yaml만 관리 (Single Source!)
```

---

## 📋 즉시 실행 가능한 TODO

- [ ] sync_umis_to_rag.py 구현 (위 코드 활용)
- [ ] rollback_rag.py 구현
- [ ] migration_rules.yaml 작성
- [ ] quick_sync.sh 작성 (간단 버전)
- [ ] 테스트 (3개 케이스)
- [ ] 문서화 (README.md 업데이트)

**예상 시간**: 2-3시간

---

**문서 끝**





