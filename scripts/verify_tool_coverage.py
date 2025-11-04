#!/usr/bin/env python3
"""
Tool Coverage 검증
umis.yaml에 언급된 모든 도구가 Tool Registry에 있는지 확인
"""

import yaml
import re
from pathlib import Path
from typing import Set, List, Dict


def extract_tools_from_umis_yaml(umis_file: Path) -> Set[str]:
    """umis.yaml에서 언급되는 도구/프레임워크 추출"""
    
    tools_mentioned = set()
    
    with open(umis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 주요 프레임워크/도구 패턴
    patterns = {
        # Frameworks
        '13_dimensions': ['13개 차원', '13 dimensions', 'market_boundary_dimensions', '13개 핵심 시장 경계'],
        'discovery_sprint': ['Discovery Sprint', 'discovery', 'fast_track_discovery', 'full_discovery_sprint'],
        '7_powers': ['7 Powers', 'Seven Powers', 'sustainable_value', 'Scale Economies', 'Network Effects'],
        'counter_positioning': ['Counter-Positioning', 'counter_positioning', '역포지셔닝'],
        'value_chain_analysis': ['Value Chain', 'value_chain', 'value_exchange_mapping', '가치사슬'],
        'competitive_analysis': ['competitive', "Porter's 5 Forces", "Porter's Five Forces", 'competition'],
        'market_definition': ['market_definition', 'TAM/SAM/SOM', 'market_boundary'],
        
        # Explorer
        'pattern_search': ['pattern', 'RAG', 'business_model_pattern', '패턴 검색'],
        '7_step_process': ['7단계', '7-step', 'opportunity_discovery_process'],
        'validation_protocol': ['validation', '검증 프로토콜'],
        'hypothesis_generation': ['hypothesis', '가설 생성', 'LLM'],
        
        # Quantifier
        'sam_4methods': ['SAM', '4가지 방법', 'Top-Down', 'Bottom-Up', 'Proxy', 'Competitor'],
        'growth_analysis': ['growth', '성장률', 'CAGR'],
        'scenario_planning': ['scenario', '시나리오', 'Best/Base/Worst'],
        'benchmark_analysis': ['benchmark', '벤치마크'],
        
        # Validator
        'data_definition': ['데이터 정의', 'definition', '정의 검증'],
        'creative_sourcing': ['creative', 'sourcing', '창의적 소싱', '12가지'],
        'gap_analysis': ['gap', 'Gap 분석', '정의 불일치'],
        'source_verification': ['source', '출처', '신뢰도'],
        
        # Observer
        'market_structure': ['market_structure', '시장 구조', '경쟁 구조'],
        'value_chain': ['value_chain', '가치사슬', 'value_exchange'],
        'inefficiency_detection': ['inefficiency', '비효율성', '정보 비대칭'],
        'disruption_opportunity': ['disruption', '파괴적', 'disruptive'],
        
        # Guardian
        'progress_monitoring': ['monitoring', '모니터링', 'goal_alignment'],
        'quality_evaluation': ['quality', '품질', 'evaluation', 'ThreeStage'],
    }
    
    # 각 패턴이 umis.yaml에 언급되는지 확인
    for tool_name, keywords in patterns.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                tools_mentioned.add(tool_name)
                break
    
    return tools_mentioned


def get_tools_from_registry(registry_file: Path) -> Set[str]:
    """Tool Registry에 있는 도구 목록"""
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)
    
    tools_in_registry = set()
    
    for tool in registry.get('tools', []):
        tool_id = tool.get('tool_id', '')
        # tool_id에서 agent: 부분 제거하고 tool 이름만
        if ':' in tool_id:
            tool_name = tool_id.split(':')[1]
            tools_in_registry.add(tool_name)
    
    return tools_in_registry


def main():
    """메인 함수"""
    
    umis_file = Path('umis.yaml')
    registry_file = Path('config/tool_registry.yaml')
    
    print("\n" + "="*60)
    print("🔍 Tool Coverage 검증")
    print("="*60)
    
    # 1. umis.yaml에서 언급되는 도구
    tools_mentioned = extract_tools_from_umis_yaml(umis_file)
    
    print(f"\n📖 umis.yaml에 언급된 도구: {len(tools_mentioned)}개")
    for tool in sorted(tools_mentioned):
        print(f"   - {tool}")
    
    # 2. Tool Registry에 있는 도구
    tools_in_registry = get_tools_from_registry(registry_file)
    
    print(f"\n📦 Tool Registry에 있는 도구: {len(tools_in_registry)}개")
    for tool in sorted(tools_in_registry):
        print(f"   - {tool}")
    
    # 3. 비교
    missing = tools_mentioned - tools_in_registry
    extra = tools_in_registry - tools_mentioned
    
    print(f"\n" + "="*60)
    print("결과")
    print("="*60)
    
    if missing:
        print(f"\n❌ umis.yaml에는 있지만 Tool Registry에 없음: {len(missing)}개")
        for tool in sorted(missing):
            print(f"   - {tool}")
        print("\n   → 추가 필요!")
    else:
        print(f"\n✅ umis.yaml에 언급된 모든 도구가 Tool Registry에 포함됨!")
    
    if extra:
        print(f"\n📌 Tool Registry에만 있음 (umis.yaml 미언급): {len(extra)}개")
        for tool in sorted(extra):
            print(f"   - {tool}")
        print("\n   → 새로 추가된 도구 (정상)")
    
    # 커버리지 계산
    if tools_mentioned:
        coverage = len(tools_in_registry & tools_mentioned) / len(tools_mentioned) * 100
        print(f"\n📊 커버리지: {coverage:.1f}%")
    
    # 종료 코드
    if missing:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

