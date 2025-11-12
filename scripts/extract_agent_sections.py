#!/usr/bin/env python3
"""
umis.yaml Agent 섹션 추출 → tool_registry.yaml Complete 버전 생성
0% 손실로 전체 내용을 그대로 복사
"""

import yaml
from pathlib import Path


def extract_agent_section(agent_data):
    """
    Agent 데이터를 YAML 문자열로 변환 (0% 손실)
    
    Args:
        agent_data: Agent dictionary from umis.yaml
    
    Returns:
        str: YAML formatted string
    """
    return yaml.dump(
        agent_data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100
    )


def create_complete_tool(agent_id, agent_data):
    """
    Agent 섹션으로 Complete 도구 생성
    
    Args:
        agent_id: Agent ID (Observer, Explorer, etc.)
        agent_data: Agent dictionary
    
    Returns:
        dict: Tool registry entry
    """
    # Agent YAML 전체를 문자열로
    content = extract_agent_section(agent_data)
    
    # 도구 ID
    tool_id = f"{agent_id.lower()}:complete"
    tool_key = f"tool:{agent_id.lower()}:complete"
    
    # Role 설명
    role = agent_data.get('role', f'{agent_id} Agent')
    description = agent_data.get('description', '')
    
    return {
        'tool_id': tool_id,
        'tool_key': tool_key,
        'metadata': {
            'agent': agent_id.lower(),
            'category': 'complete_context',
            'complexity': 'comprehensive',
            'context_size': len(content),
            'priority': 'high',
            'source': 'umis.yaml agents section (0% loss)'
        },
        'when_to_use': {
            'keywords': [agent_id.lower(), 'complete', 'full context', '전체'],
            'scenarios': [
                f"@{agent_id}, (실제 작업 수행)",
                f"{agent_id} 전체 컨텍스트 필요"
            ]
        },
        'content': f"""# {agent_id}: Complete Context (0% Loss from umis.yaml)

## 📋 출처
umis.yaml agents section - {agent_id} 전체

## 🎯 역할
{role}

{description}

## 📖 전체 내용 (YAML)

아래는 umis.yaml의 {agent_id} 섹션을 0% 손실로 그대로 복사한 것입니다.
모든 작업 방식, 원칙, 프레임워크, 예시, 협업 방식이 포함되어 있습니다.

```yaml
{content}```

## 🔗 세분화 도구 (빠른 조회용)
- tool:{agent_id.lower()}:market_structure (해당 시)
- tool:{agent_id.lower()}:7_step_process (해당 시)
- tool:{agent_id.lower()}:sam_4methods (해당 시)
등 세분화 도구는 빠른 확인용입니다.

전체 컨텍스트가 필요하면 이 complete 버전을 사용하세요.
"""
    }


def main():
    """메인 함수"""
    print("🚀 umis.yaml Agent 섹션 추출 시작")
    print()
    
    # 1. umis.yaml 로드
    with open('umis.yaml') as f:
        umis_data = yaml.safe_load(f)
    
    agents = umis_data.get('agents', [])
    print(f"✅ {len(agents)}개 Agent 발견")
    print()
    
    # 2. 각 Agent의 Complete 도구 생성
    complete_tools = []
    
    for agent in agents:
        agent_id = agent.get('id', 'Unknown')
        
        print(f"📦 {agent_id} 처리 중...")
        
        tool = create_complete_tool(agent_id, agent)
        complete_tools.append(tool)
        
        content_size = len(tool['content'])
        print(f"   - Content: {content_size:,}자")
        print(f"   - 예상 토큰: ~{content_size // 4:,}")
        print()
    
    # 3. 기존 tool_registry 로드
    with open('config/tool_registry.yaml') as f:
        registry = yaml.safe_load(f)
    
    # 4. Complete 도구 추가
    print("📝 기존 tool_registry에 Complete 도구 추가")
    
    # 기존 도구들 유지
    existing_tools = registry.get('tools', [])
    print(f"   - 기존 도구: {len(existing_tools)}개")
    
    # Complete 도구 추가
    all_tools = complete_tools + existing_tools
    print(f"   - Complete 추가: {len(complete_tools)}개")
    print(f"   - 총 도구: {len(all_tools)}개")
    print()
    
    # 5. 새 레지스트리 구성
    new_registry = {
        'version': '7.7.0',
        'created': '2025-11-03',
        'updated': '2025-11-12',
        'total_tools': len(all_tools),
        'changelog': 'v7.7.0: Agent Complete 버전 추가 (0% loss from umis.yaml)',
        'structure': {
            'complete_tools': f'{len(complete_tools)}개 (각 Agent 전체 컨텍스트)',
            'task_tools': f'{len(existing_tools)}개 (세분화 도구, 빠른 조회용)'
        },
        'tools': all_tools
    }
    
    # 6. 저장
    output_file = 'config/tool_registry_with_complete.yaml'
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(new_registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"✅ 저장 완료: {output_file}")
    print()
    
    # 7. 통계
    total_content_size = sum(len(t.get('content', '')) for t in all_tools)
    avg_size = total_content_size / len(all_tools)
    
    print("=" * 80)
    print("📊 최종 통계")
    print("=" * 80)
    print(f"총 도구: {len(all_tools)}개")
    print(f"  - Complete: {len(complete_tools)}개 (평균 ~{sum(len(t.get('content', '')) for t in complete_tools) // len(complete_tools):,}자)")
    print(f"  - Task: {len(existing_tools)}개 (평균 ~{sum(len(t.get('content', '')) for t in existing_tools) // len(existing_tools):,}자)")
    print()
    print(f"총 Content: {total_content_size:,}자")
    print(f"평균 크기: {avg_size:,.0f}자")
    print()
    print("예상 사용:")
    print("  - 3개 Complete: ~30KB (~7,500 토큰)")
    print("  - 5개 Complete: ~50KB (~12,500 토큰)")
    print()
    print("⚠️ 주의: Complete 버전은 크므로 필요시만 사용")
    print("       빠른 확인은 Task 버전 (예: market_structure) 사용")
    print("=" * 80)


if __name__ == "__main__":
    main()
EOF

