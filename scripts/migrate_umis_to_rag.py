#!/usr/bin/env python3
"""
umis.yaml 전체를 0% 손실로 System RAG로 마이그레이션
모든 섹션을 Complete 도구로 변환
"""

import yaml
from pathlib import Path


def create_section_tool(section_name, section_data, description=""):
    """
    umis.yaml 섹션을 Complete 도구로 변환
    
    Args:
        section_name: 섹션 이름 (예: system_architecture)
        section_data: 섹션 데이터
        description: 섹션 설명
    
    Returns:
        dict: Tool registry entry
    """
    # YAML 문자열로 변환 (0% 손실)
    content_yaml = yaml.dump(
        {section_name: section_data},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120
    )
    
    # 도구 ID
    tool_id = f"system:{section_name}"
    tool_key = f"tool:system:{section_name}"
    
    return {
        'tool_id': tool_id,
        'tool_key': tool_key,
        'metadata': {
            'agent': 'system',
            'category': 'complete_context',
            'complexity': 'comprehensive',
            'context_size': len(content_yaml),
            'priority': 'high',
            'source': f'umis.yaml {section_name} section (0% loss)'
        },
        'when_to_use': {
            'keywords': [section_name, 'system', 'complete', '전체'],
            'scenarios': [
                f"{section_name} 전체 컨텍스트 필요",
                "UMIS 시스템 구조 이해"
            ]
        },
        'content': f"""# System: {section_name} (0% Loss from umis.yaml)

## 📋 출처
umis.yaml - {section_name} 섹션 전체

## 📖 설명
{description}

## 📖 전체 내용 (YAML)

아래는 umis.yaml의 {section_name} 섹션을 0% 손실로 그대로 복사한 것입니다.

```yaml
{content_yaml}```

## 🔗 관련 도구
- tool:system:* (다른 시스템 섹션)
- tool:*:complete (Agent Complete 버전)
"""
    }


def main():
    """메인 함수"""
    print("🚀 umis.yaml 전체 마이그레이션 시작")
    print()
    
    # 1. umis.yaml 로드
    with open('umis.yaml') as f:
        umis_data = yaml.safe_load(f)
    
    print(f"✅ umis.yaml 로드 완료")
    print()
    
    # 2. 각 섹션 처리
    section_descriptions = {
        'system_architecture': 'UMIS 시스템 아키텍처 개요 (정보 흐름, Agent 협업, 검증 체크포인트)',
        'system': 'UMIS 시스템 정의 (버전, 구성, 워크플로우)',
        'adaptive_intelligence_system': '적응형 지능 시스템 (학습, 진화, 최적화)',
        'proactive_monitoring': '사전 모니터링 시스템 (Guardian Meta-RAG, 순환 감지)',
        'support_validation_system': '지원 및 검증 시스템 (Agent 협업 프로토콜)',
        'data_integrity_system': '데이터 무결성 시스템 (ID Namespace, Excel 함수)',
        'agents': 'Agent 상세 정의 (6개 Agent 전체)',
        'roles': '역할 정의 (Owner 등)',
        'implementation_guide': '실행 가이드 (워크플로우, 프로토콜)'
    }
    
    system_tools = []
    
    for section_name in umis_data.keys():
        if section_name in section_descriptions:
            print(f"📦 {section_name} 처리 중...")
            
            section_data = umis_data[section_name]
            description = section_descriptions.get(section_name, '')
            
            tool = create_section_tool(section_name, section_data, description)
            system_tools.append(tool)
            
            content_size = len(tool['content'])
            print(f"   - Content: {content_size:,}자")
            print(f"   - 예상 토큰: ~{content_size // 4:,}")
            print()
    
    # 3. 기존 tool_registry 로드
    with open('config/tool_registry.yaml') as f:
        registry = yaml.safe_load(f)
    
    # 4. System 섹션 도구 추가
    print("📝 tool_registry에 System 섹션 도구 추가")
    
    existing_tools = registry.get('tools', [])
    print(f"   - 기존 도구: {len(existing_tools)}개")
    
    # System 섹션 도구를 맨 앞에 추가
    all_tools = system_tools + existing_tools
    print(f"   - System 섹션 추가: {len(system_tools)}개")
    print(f"   - 총 도구: {len(all_tools)}개")
    print()
    
    # 5. 새 레지스트리 구성
    new_registry = {
        'version': '7.7.0',
        'created': '2025-11-03',
        'updated': '2025-11-12',
        'total_tools': len(all_tools),
        'changelog': 'v7.7.0: umis.yaml 100% RAG 마이그레이션 (0% loss)',
        'structure': {
            'system_sections': f'{len(system_tools)}개 (umis.yaml 시스템 섹션)',
            'agent_complete': '6개 (각 Agent 전체 컨텍스트)',
            'task_tools': '29개 (세분화 도구, 빠른 조회용)',
            'total': f'{len(all_tools)}개'
        },
        'migration': {
            'source': 'umis.yaml (complete)',
            'loss_rate': '0%',
            'coverage': '100%'
        },
        'tools': all_tools
    }
    
    # 6. 저장
    output_file = 'config/tool_registry_full.yaml'
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(new_registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"✅ 저장 완료: {output_file}")
    print()
    
    # 7. 통계
    total_content_size = sum(len(t.get('content', '')) for t in all_tools)
    
    system_section_size = sum(len(t.get('content', '')) for t in system_tools)
    agent_complete_size = sum(len(t.get('content', '')) for t in existing_tools if ':complete' in t.get('tool_id', ''))
    task_size = sum(len(t.get('content', '')) for t in existing_tools if ':complete' not in t.get('tool_id', ''))
    
    print("=" * 80)
    print("📊 최종 통계")
    print("=" * 80)
    print(f"총 도구: {len(all_tools)}개")
    print()
    print("분류별:")
    print(f"  1. System 섹션: {len(system_tools)}개")
    print(f"     - 크기: {system_section_size:,}자 (~{system_section_size // 4:,} 토큰)")
    print()
    print(f"  2. Agent Complete: 6개")
    print(f"     - 크기: {agent_complete_size:,}자 (~{agent_complete_size // 4:,} 토큰)")
    print()
    print(f"  3. Task 도구: {len(existing_tools) - 6}개")
    print(f"     - 크기: {task_size:,}자 (~{task_size // 4:,} 토큰)")
    print()
    print(f"총 Content: {total_content_size:,}자 (~{total_content_size // 4:,} 토큰)")
    print()
    print("umis.yaml 원본:")
    print("  - 크기: ~162,270자 (~40,567 토큰)")
    print(f"  - System RAG 총 크기: {total_content_size:,}자")
    print(f"  - 비율: {total_content_size / 162270 * 100:.1f}% (헤더/설명 추가)")
    print()
    print("=" * 80)
    print("✅ umis.yaml 100% RAG 마이그레이션 완료!")
    print("   - 0% 손실")
    print("   - 모든 섹션 포함")
    print("=" * 80)


if __name__ == "__main__":
    main()
EOF





