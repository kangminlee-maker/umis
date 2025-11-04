#!/usr/bin/env python3
"""
umis.yaml에서 tool_registry.yaml 재생성
양방향 ID 매핑 포함
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def extract_guestimation_from_umis(umis_data: Dict) -> Dict:
    """
    umis.yaml에서 Guestimation 추출하여 Tool Registry 형식으로 변환
    """
    
    # umis.yaml의 guestimation 섹션 찾기
    try:
        guestimation = (
            umis_data
            .get('implementation_guide', {})
            .get('tools_and_templates', {})
            .get('methodologies', {})
            .get('guestimation', {})
        )
    except:
        print("❌ umis.yaml에서 guestimation 섹션을 찾을 수 없습니다")
        return None
    
    if not guestimation:
        print("❌ guestimation 섹션이 비어있습니다")
        return None
    
    # Tool Registry 형식으로 변환 (압축)
    tool = {
        'tool_id': 'universal:guestimation',
        'tool_key': 'tool:universal:guestimation',
        'metadata': {
            'agent': 'all',
            'category': 'estimation_methodology',
            'complexity': 'medium',
            'context_size': 150,
            'priority': 'critical',
            'version': guestimation.get('version', '2.0'),
            'source_file': 'umis.yaml',
            'source_section': 'tools_and_templates.methodologies.guestimation',
            'source_lines': '5454-5688'
        },
        'when_to_use': {
            'keywords': ['추정', '근사', 'guestimate', 'estimate', '대략', '추론'],
            'conditions': [
                '직접 데이터 없음',
                '정확한 값 알 수 없음',
                '짧은 시간 내 판단 필요'
            ],
            'scenarios': [
                '전환율을 추정해야 하는데 데이터가 없어',
                '시장 규모를 대략적으로 알고 싶어',
                '이 가정이 합리적인지 검증하고 싶어'
            ]
        }
    }
    
    # Content 생성 (압축 버전)
    fermi = guestimation.get('fermi_4_principles', {})
    sources = guestimation.get('data_sources_8', {})
    criteria = guestimation.get('comparability_4_criteria', {})
    examples = guestimation.get('examples', {})
    
    content_lines = [
        "# Guestimation (Fermi Estimation)",
        "",
        f"**정의**: {guestimation.get('definition', {}).get('core', 'AI 추정 방법론')}",
        "",
        f"> \"{guestimation.get('definition', {}).get('philosophy', 'Fermi 철학')}\"",
        "",
        "## Fermi 4원리",
        "",
        f"1. **모형**: {fermi.get('model', '추상 → 계산 가능')}",
        f"2. **분해**: {fermi.get('decompose', '큰 → 작은')}",
        f"3. **제약조건**: {fermi.get('constraint', '물리적 한계')}",
        f"4. **Order of Magnitude**: {fermi.get('magnitude', '자릿수')}",
        "",
        "## 8개 데이터 출처 (AI 전략)",
        "",
        "1. **프로젝트 데이터**: 확정 (직접 사용)",
        "2. **LLM 직접 답변**: 즉시 ('한국 인구?') → 대략적",
        "3. **검색 공통 맥락**: 웹 서치 → 상위 결과 공통 값",
        "4. **법칙**: 물리/법률/도덕 (절대적)",
        "5. **행동경제학**: Loss Aversion, Anchoring 등",
        "6. **통계 패턴**: 80-20, 정규분포",
        "7. **Rule of Thumb**: 산업별 경험 공식 (RAG)",
        "8. **시공간 제약**: 하루 24h, 물리적 한계",
        "",
        "**RAG 위치**: 출처 7의 일부일 뿐 (12.5%)!",
        "",
        "**비교 4대 기준**: 제품 속성, 소비 주체, 가격대, 구매 맥락",
        "",
        "## 프로세스",
        "",
        "1. 문제 명확화 → 2. 모형 만들기 → 3. 분해 → 4. 계산 → ",
        "5. 비율 조정 → 6. Boundary → 7. 검증 → 8. 신뢰도",
        "",
        "## 예시",
        "",
        f"- Benchmark: {examples.get('benchmark', '피아노 전환율')}",
        f"- Decomposition: {examples.get('decomposition', '휴일 여행')}",
        f"- Constraint: {examples.get('constraint', '자장면')}",
        f"- Fermi 종합: {examples.get('fermi_classic', '전봇대')}",
        "",
        "## 구현",
        "",
        "```python",
        "from umis_rag.utils.guestimation import GuestimationEngine",
        "engine = GuestimationEngine()",
        "result = engine.check_comparability(target, candidate)",
        "```",
        "",
        "**상세**: umis.yaml → tools_and_templates.methodologies.guestimation"
    ]
    
    tool['content'] = '\n'.join(content_lines)
    
    return tool


def verify_umis_yaml_integrity():
    """umis.yaml 무결성 검증"""
    
    print("\n" + "="*70)
    print("📋 umis.yaml 무결성 검증")
    print("="*70)
    
    umis_file = Path('umis.yaml')
    
    with open(umis_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    checks = []
    
    # 1. Guestimation 존재 확인
    try:
        guestimation = (
            data['implementation_guide']
            ['tools_and_templates']
            ['methodologies']
            ['guestimation']
        )
        checks.append(("✅", "Guestimation 섹션 존재"))
        
        # 세부 확인
        if 'fermi_4_principles' in guestimation:
            checks.append(("✅", "Fermi 4원리"))
        else:
            checks.append(("❌", "Fermi 4원리 누락"))
        
        if 'data_sources_8' in guestimation:
            checks.append(("✅", "8개 데이터 출처"))
        else:
            checks.append(("❌", "8개 데이터 출처 누락"))
        
        if 'agent_usage_guide' in guestimation:
            checks.append(("✅", "Agent 사용 가이드"))
        else:
            checks.append(("❌", "Agent 사용 가이드 누락"))
        
    except Exception as e:
        checks.append(("❌", f"Guestimation 섹션 접근 실패: {e}"))
    
    # 2. Agent별 universal_tools 확인
    agents_to_check = ['Observer', 'Explorer', 'Quantifier', 'Validator', 'Guardian']
    
    for agent_data in data.get('agents', []):
        agent_id = agent_data.get('id')
        if agent_id in agents_to_check:
            if 'universal_tools' in agent_data and 'guestimation' in agent_data['universal_tools']:
                checks.append(("✅", f"{agent_id}: universal_tools.guestimation"))
            else:
                checks.append(("❌", f"{agent_id}: universal_tools 누락"))
    
    # 결과 출력
    print("\n검증 결과:")
    for status, msg in checks:
        print(f"  {status} {msg}")
    
    failed = sum(1 for status, _ in checks if status == "❌")
    
    print(f"\n총 {len(checks)}개 항목 중 {len(checks) - failed}개 통과")
    
    if failed > 0:
        print(f"⚠️  {failed}개 실패 - 수정 필요!")
        return False
    else:
        print("✅ 모든 검증 통과!")
        return True


def regenerate_tool_registry():
    """umis.yaml에서 tool_registry.yaml 재생성"""
    
    print("\n" + "="*70)
    print("🔧 Tool Registry 재생성")
    print("="*70)
    
    umis_file = Path('umis.yaml')
    registry_file = Path('config/tool_registry.yaml')
    
    # 기존 Tool Registry 로드
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)
    
    # umis.yaml 로드
    with open(umis_file, 'r', encoding='utf-8') as f:
        umis_data = yaml.safe_load(f)
    
    # Guestimation tool 추출
    new_guestimation = extract_guestimation_from_umis(umis_data)
    
    if not new_guestimation:
        print("❌ Guestimation 추출 실패")
        return False
    
    # 기존 registry에서 guestimation 교체
    tools = registry.get('tools', [])
    
    # 기존 guestimation 제거
    tools = [t for t in tools if t.get('tool_id') != 'universal:guestimation']
    
    # 새 guestimation 추가
    tools.append(new_guestimation)
    
    registry['tools'] = tools
    registry['updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # 저장
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print("✅ Tool Registry 재생성 완료")
    print(f"   파일: {registry_file}")
    print(f"   Guestimation: {len(new_guestimation['content'].split(chr(10)))}줄")
    
    return True


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 umis.yaml → tool_registry.yaml 재생성")
    print("="*70)
    
    # Step 1: 무결성 검증
    if not verify_umis_yaml_integrity():
        print("\n❌ umis.yaml 무결성 검증 실패")
        print("   먼저 누락된 항목을 추가하세요")
        exit(1)
    
    # Step 2: Tool Registry 재생성
    if not regenerate_tool_registry():
        print("\n❌ Tool Registry 재생성 실패")
        exit(1)
    
    print("\n" + "="*70)
    print("✅ 모든 작업 완료!")
    print("="*70)
    print("\n다음 단계:")
    print("  1. config/tool_registry.yaml 확인")
    print("  2. python scripts/build_system_knowledge.py (System RAG 재구축)")

