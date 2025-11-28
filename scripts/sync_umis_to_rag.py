#!/usr/bin/env python3
"""
umis.yaml → System RAG 동기화 (One Command)

버전: v7.11.1
업데이트: 2025-11-26
변경사항:
  - Complete 도구만 생성 (Task 도구 제거)
  - 총 15개 도구 (System 9 + Complete 6)
  - v7.11.1 4-Stage Fusion Architecture

사용법:
    python3 scripts/sync_umis_to_rag.py              # 일반 실행
    python3 scripts/sync_umis_to_rag.py --dry-run    # 시뮬레이션
    python3 scripts/sync_umis_to_rag.py --force      # 검증 생략
"""

import yaml
import shutil
import subprocess
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
        else:
            print("🔍 DRY RUN: 실제 저장하지 않음")
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
        required_sections = ['system_architecture', 'agents']
        
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
        
        # 0. Onboarding 도구 생성 (신규!)
        if 'ai_onboarding' in umis_data:
            onboarding_tools = self._create_onboarding_tools(umis_data['ai_onboarding'])
            tools.extend(onboarding_tools)
            print(f"   ✅ {len(onboarding_tools)}개 Onboarding 도구")
        
        # 1. System 섹션 도구 생성
        system_sections = [k for k in umis_data.keys() 
                           if k not in ['agents', 'ai_onboarding']]
        
        for section_name in system_sections:
            section_data = umis_data[section_name]
            tool = self._create_system_tool(section_name, section_data)
            tools.append(tool)
            print(f"   ✅ tool:system:{section_name}")
        
        # 2. agents 섹션 전체 (옵션)
        if 'agents' in umis_data:
            tool = self._create_system_tool('agents', umis_data['agents'])
            tools.append(tool)
            print(f"   ✅ tool:system:agents (전체 Agent)")
        
        # 3. 각 Agent Complete 도구
        for agent in umis_data.get('agents', []):
            agent_id = agent.get('id')
            tool = self._create_agent_complete(agent_id, agent)
            tools.append(tool)
            print(f"   ✅ tool:{agent_id.lower()}:complete")
        
        print()
        print(f"   총 {len(tools)}개 도구 생성")
        print(f"   - Onboarding 도구: {len([t for t in tools if 'onboarding:' in t['tool_id']])}개")
        print(f"   - System 도구: {len([t for t in tools if 'system:' in t['tool_id']])}개")
        print(f"   - Complete 도구: {len([t for t in tools if ':complete' in t['tool_id']])}개")
        print()
        
        # 4. 레지스트리 구성
        registry = {
            'version': '7.11.1',
            'created': '2025-11-26',
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tools': len(tools),
            'auto_generated': True,
            'changelog': 'v7.11.1: Complete only (Task tools removed)',
            'source': 'umis.yaml (System + Complete, 0% loss)',
            'note': 'Task 도구 제거 결정 (v7.11.1) - CONTEXT_WINDOW_STRATEGY.md 참조',
            'sync_info': {
                'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': 'umis.yaml',
                'sync_script': 'scripts/sync_umis_to_rag.py'
            },
            'tools': tools
        }
        
        return registry
    
    def _create_onboarding_tools(self, onboarding_data):
        """Onboarding 도구 4개 생성"""
        tools = []
        
        onboarding_sections = ['quick_start', 'state_machine', 
                               'agent_essentials', 'workflow_primer']
        
        for section_name in onboarding_sections:
            if section_name not in onboarding_data:
                continue
            
            section_content = onboarding_data[section_name]
            
            # YAML 형태로 직렬화
            content_yaml = yaml.dump(
                {section_name: section_content},
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=120
            )
            
            # Content 포맷팅
            content = f"""# Onboarding: {section_name}

## 📋 출처
umis.yaml - ai_onboarding.{section_name} (Auto-Sync)

## 📖 내용 (YAML)

```yaml
{content_yaml}```

---

⚠️  이 도구는 자동 생성됩니다.
   수정하려면 umis.yaml의 ai_onboarding 섹션을 편집하세요.
"""
            
            # 토큰 추정
            char_count = len(content)
            token_estimate = int(char_count / 4)
            
            tool = {
                'tool_id': f'onboarding:{section_name}',
                'tool_key': f'tool:onboarding:{section_name}',
                'metadata': {
                    'agent': 'onboarding',
                    'category': 'ai_learning',
                    'context_size': char_count,
                    'token_estimate': token_estimate,
                    'priority': 'critical',
                    'source': f'umis.yaml ai_onboarding.{section_name} (auto-sync)',
                    'auto_generated': True
                },
                'when_to_use': {
                    'keywords': [section_name, 'onboarding', '학습', 'learning'],
                    'scenarios': [
                        f'AI 초기 학습: {section_name}',
                        'UMIS 시스템 빠른 파악'
                    ]
                },
                'content': content
            }
            
            tools.append(tool)
        
        return tools
    
    def _create_system_tool(self, section_name, section_data):
        """System 섹션 도구 생성"""
        content_yaml = yaml.dump(
            {section_name: section_data},
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120
        )
        
        return {
            'tool_id': f'system:{section_name}',
            'tool_key': f'tool:system:{section_name}',
            'metadata': {
                'agent': 'system',
                'category': 'complete_context',
                'context_size': len(content_yaml),
                'priority': 'high',
                'source': f'umis.yaml {section_name} (auto-sync)',
                'auto_generated': True
            },
            'when_to_use': {
                'keywords': [section_name, 'system', '전체'],
                'scenarios': [
                    f'{section_name} 전체 컨텍스트 필요',
                    'UMIS 시스템 구조 이해'
                ]
            },
            'content': f"""# System: {section_name} (0% Loss from umis.yaml)

## 📋 출처
umis.yaml - {section_name} 섹션 전체 (Auto-Sync)

## 📖 전체 내용 (YAML)

아래는 umis.yaml의 {section_name} 섹션을 0% 손실로 그대로 복사한 것입니다.

```yaml
{content_yaml}```

---

⚠️  이 도구는 자동 생성됩니다.
   수정하려면 umis.yaml을 편집하고 sync_umis_to_rag.py를 실행하세요.
"""
        }
    
    def _create_agent_complete(self, agent_id, agent_data):
        """Agent Complete 도구 생성"""
        content_yaml = yaml.dump(
            agent_data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120
        )
        
        role = agent_data.get('role', f'{agent_id} Agent')
        description = agent_data.get('description', '')
        
        return {
            'tool_id': f'{agent_id.lower()}:complete',
            'tool_key': f'tool:{agent_id.lower()}:complete',
            'metadata': {
                'agent': agent_id.lower(),
                'category': 'complete_context',
                'context_size': len(content_yaml),
                'priority': 'high',
                'source': f'umis.yaml agents.{agent_id} (auto-sync)',
                'auto_generated': True
            },
            'when_to_use': {
                'keywords': [agent_id.lower(), 'complete', '전체'],
                'scenarios': [
                    f'@{agent_id} 실제 작업 수행',
                    f'{agent_id} 전체 컨텍스트 필요'
                ]
            },
            'content': f"""# {agent_id}: Complete Context (0% Loss from umis.yaml)

## 📋 출처
umis.yaml agents section - {agent_id} 전체 (Auto-Sync)

## 🎯 역할
{role}

{description}

## 📖 전체 내용 (YAML)

아래는 umis.yaml의 {agent_id} 섹션을 0% 손실로 그대로 복사한 것입니다.
모든 작업 방식, 원칙, 프레임워크, 예시, 협업 방식이 포함되어 있습니다.

```yaml
{content_yaml}```

---

⚠️  이 도구는 자동 생성됩니다.
   수정하려면 umis.yaml의 {agent_id} 섹션을 편집하고 sync_umis_to_rag.py를 실행하세요.
"""
        }
    
    def _validate_registry(self, registry):
        """레지스트리 검증"""
        print("🔍 검증 중...")
        
        tools = registry['tools']
        
        # 1. 도구 수 체크
        if len(tools) < 10:
            raise ValueError(f"도구 수 부족: {len(tools)}")
        print(f"   ✅ 도구 수: {len(tools)}개")
        
        # 2. 필수 도구 존재 체크
        required_tools = [
            'onboarding:quick_start',
            'system:system_architecture',
            'observer:complete',
            'explorer:complete'
        ]
        
        tool_ids = {t['tool_id'] for t in tools}
        for req in required_tools:
            if req not in tool_ids:
                raise ValueError(f"필수 도구 누락: {req}")
        print(f"   ✅ 필수 도구 모두 존재")
        
        # 3. Content 크기 체크
        for tool in tools:
            size = len(tool.get('content', ''))
            if size < 100:
                raise ValueError(f"Content 너무 작음: {tool['tool_id']} ({size}자)")
        print(f"   ✅ 모든 도구 Content 정상")
        
        print()
    
    def _save_registry(self, registry):
        """레지스트리 저장"""
        print("💾 저장 중...")
        
        # 경고 헤더 추가
        warning_header = """# ========================================
# ⚠️  이 파일은 자동 생성됩니다!
# 
# 편집 금지! 대신 umis.yaml을 수정하세요.
# 
# 동기화 방법:
#   python3 scripts/sync_umis_to_rag.py
# 
# 마지막 동기화: {}
# ========================================

""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            f.write(warning_header)
            yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
        
        print(f"   ✅ {self.registry_path}")
        print()
    
    def _rebuild_rag(self):
        """RAG 재구축"""
        print("🔨 System RAG 재구축 중...")
        
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
        
        # 검색 테스트
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
        
        print()
        print("=" * 80)
        print("다음 단계:")
        print("  1. python3 scripts/query_system_rag.py --list (도구 목록 확인)")
        print("  2. python3 scripts/query_system_rag.py tool:observer:complete (테스트)")
        print("=" * 80)
        
    except Exception as e:
        print()
        print(f"❌ 에러 발생: {e}")
        print()
        print("롤백 방법:")
        print("  python3 scripts/rollback_rag.py")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()






