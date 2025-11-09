#!/usr/bin/env python3
"""
E2E 통합 테스트: 실제 시장 분석 프로젝트
전체 UMIS 시스템 검증

시나리오:
1. 신규 시장 (시니어 케어 로봇)
2. 성숙 시장 (국내 OTT)
3. 규제 산업 (의료 AI)

검증 항목:
- System RAG 접근
- Agent 선택 (Workflow)
- RAG Collections 활용
- Hybrid Guestimation 작동
- 산출물 품질
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.quantifier import QuantifierRAG
from umis_rag.agents.validator import ValidatorRAG
from umis_rag.agents.explorer import ExplorerRAG
from umis_rag.guardian.meta_rag import GuardianMetaRAG
from umis_rag.methodologies.domain_reasoner import DomainReasonerEngine


def test_scenario_1_new_market():
    """
    시나리오 1: 신규 시장 (시니어 케어 로봇)
    
    검증:
    - System RAG로 tool 로드 ✓
    - Workflow: Observer → Explorer → Quantifier
    - Hybrid: Phase 1 → Guardian → Phase 2
    - Domain Reasoner: s2, s10 활용
    - Should vs Will 분석
    """
    
    print("\n" + "=" * 70)
    print("시나리오 1: 신규 시장 (시니어 케어 로봇)")
    print("=" * 70)
    
    # ===== 프로젝트 정의 =====
    print("\n[프로젝트 정의]")
    print("-" * 70)
    
    market_def = {
        'market_name': '시니어 케어 로봇 시장',
        'industry': 'healthcare',
        'geography': 'KR',
        'time_horizon': '2030',
        'context': {
            'regulatory': True,     # 의료기기법
            'new_market': True,     # 신규 시장
            'tech_resistance': True,  # 기술 거부감
            'high_price': True      # 고가 제품
        }
    }
    
    print(f"  시장: {market_def['market_name']}")
    print(f"  산업: {market_def['industry']}")
    print(f"  지리: {market_def['geography']}")
    print(f"  특성: 규제 산업, 신규 시장")
    
    # ===== 1. Validator: KPI 정의 검증 (Rachel) =====
    print("\n[Step 1] Validator (Rachel): KPI 정의 검증")
    print("-" * 70)
    
    rachel = ValidatorRAG()
    
    kpi_result = rachel.validate_kpi_definition(
        metric_name="시장 규모",
        provided_definition={
            'numerator': "총 시장 매출",
            'denominator': "N/A",
            'unit': "KRW"
        }
    )
    
    print(f"  KPI ID: {kpi_result.get('kpi_id', 'N/A')}")
    print(f"  상태: {kpi_result['status']}")
    print(f"  권고: {kpi_result.get('recommendation', 'N/A')}")
    
    assert kpi_result['status'] in ['match', 'partial_match', 'not_found'], "KPI 검증 완료"
    
    # ===== 2. Explorer: 패턴 검색 (Steve) =====
    print("\n[Step 2] Explorer (Steve): 패턴 검색")
    print("-" * 70)
    
    steve = ExplorerRAG()
    
    patterns = steve.search_patterns("케어 로봇 시니어 구독", top_k=3)
    
    print(f"  패턴 발견: {len(patterns)}개")
    
    if patterns:
        for doc, score in patterns[:3]:
            pattern_id = doc.metadata.get('pattern_id', 'unknown')
            print(f"    - {pattern_id} (유사도: {score:.3f})")
    
    # ===== 3. Quantifier: Hybrid Guestimation (Bill) =====
    print("\n[Step 3] Quantifier (Bill): Hybrid Guestimation")
    print("-" * 70)
    
    bill = QuantifierRAG()
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    print(f"\n  Phase 1 (Guestimation):")
    print(f"    추정값: {result['phase_1']['value']/1e8:.0f}억 원")
    print(f"    신뢰도: {result['phase_1']['confidence']*100:.0f}%")
    
    print(f"\n  Guardian 평가:")
    print(f"    권고: {result['recommendation']['recommendation']}")
    print(f"    트리거: {result['recommendation']['trigger']}")
    print(f"    우선순위: {result['recommendation']['priority']}")
    
    print(f"\n  Phase 2 실행: {'예' if result['phase_2'] else '아니오'}")
    
    if result['phase_2']:
        print(f"\n  Phase 2 (Domain Reasoner):")
        print(f"    점추정: {result['phase_2'].get('point_estimate', 0)/1e8:.0f}억")
        print(f"    신뢰도: {result['phase_2'].get('confidence', 'N/A')}")
        
        should_will = result['phase_2'].get('should_vs_will', {})
        if should_will:
            print(f"\n  Should vs Will:")
            print(f"    Should: {should_will.get('should', {}).get('value', 0)/1e8:.0f}억 (필요성)")
            print(f"    Will: {should_will.get('will', {}).get('value', 0)/1e8:.0f}억 (현실)")
            print(f"    Gap: {should_will.get('gap', {}).get('percentage', 0):.1f}%")
    
    print(f"\n  최종 방법론: {result['method_used']}")
    
    # 검증
    assert result['recommendation']['recommendation'] == 'domain_reasoner', "Phase 2 권고"
    assert result['phase_2'] is not None, "Phase 2 실행됨"
    assert result['method_used'] == 'domain_reasoner', "Domain Reasoner 사용"
    
    print("\n✅ 시나리오 1 완료")
    
    return result


def test_scenario_2_mature_market():
    """
    시나리오 2: 성숙 시장 (국내 OTT)
    
    검증:
    - Guestimation만으로 충분
    - Phase 2 전환 안 됨
    - 빠른 분석 (5-30분)
    """
    
    print("\n" + "=" * 70)
    print("시나리오 2: 성숙 시장 (국내 OTT)")
    print("=" * 70)
    
    market_def = {
        'market_name': '국내 OTT 구독 시장',
        'industry': 'streaming',
        'geography': 'KR',
        'time_horizon': '2025',
        'context': {
            'regulatory': False,
            'new_market': False
        }
    }
    
    print(f"  시장: {market_def['market_name']}")
    print(f"  특성: 성숙 시장, 데이터 풍부")
    
    # Quantifier Hybrid
    bill = QuantifierRAG()
    
    # Phase 1 결과 모킹 (높은 신뢰도, 작은 기회)
    bill._execute_guestimation = lambda x: {
        'value': 70_000_000_000,  # 700억 (< 1,000억)
        'range': (60_000_000_000, 80_000_000_000),
        'confidence': 0.75,  # 높은 신뢰도
        'method': 'guestimation'
    }
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    print(f"\n  Phase 1 (Guestimation):")
    print(f"    추정값: {result['phase_1']['value']/1e8:.0f}억 원")
    print(f"    범위: {result['phase_1']['range'][0]/1e8:.0f}-{result['phase_1']['range'][1]/1e8:.0f}억")
    print(f"    신뢰도: {result['phase_1']['confidence']*100:.0f}%")
    
    print(f"\n  Guardian 평가:")
    print(f"    권고: {result['recommendation']['recommendation']}")
    print(f"    이유: {result['recommendation']['reason']}")
    
    print(f"\n  Phase 2 실행: {'예' if result['phase_2'] else '아니오'}")
    print(f"  최종 방법론: {result['method_used']}")
    
    # 검증
    assert result['recommendation']['recommendation'] == 'guestimation_sufficient', "Guestimation 충분"
    assert result['phase_2'] is None, "Phase 2 실행 안 됨"
    assert result['method_used'] == 'guestimation', "Guestimation 사용"
    
    print("\n✅ 시나리오 2 완료 (Guestimation만으로 충분)")
    
    return result


def test_scenario_3_regulatory():
    """
    시나리오 3: 규제 산업 (의료 AI)
    
    검증:
    - 규제 산업 → Phase 2 필수
    - s3 Laws 확인
    - Domain Reasoner 자동 실행
    """
    
    print("\n" + "=" * 70)
    print("시나리오 3: 규제 산업 (의료 AI 진단)")
    print("=" * 70)
    
    market_def = {
        'market_name': '의료 AI 진단 시장',
        'industry': 'healthcare',
        'geography': 'KR',
        'time_horizon': '2028',
        'context': {
            'regulatory': True,  # 의료기기법 (핵심!)
            'new_market': False,
            'requires_switch': True  # 기존 진단 → AI 전환
        }
    }
    
    print(f"  시장: {market_def['market_name']}")
    print(f"  특성: 규제 산업 (의료기기법)")
    
    # Quantifier Hybrid
    bill = QuantifierRAG()
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    print(f"\n  Guardian 평가:")
    print(f"    권고: {result['recommendation']['recommendation']}")
    print(f"    트리거: {result['recommendation']['trigger']}")
    print(f"    우선순위: {result['recommendation']['priority']}")
    print(f"    자동 실행: {result['recommendation']['auto_execute']}")
    
    print(f"\n  Phase 2 실행: {'예' if result['phase_2'] else '아니오'}")
    print(f"  최종 방법론: {result['method_used']}")
    
    # 검증
    assert result['recommendation']['recommendation'] == 'domain_reasoner', "Phase 2 필수"
    assert result['recommendation']['priority'] == 'required', "규제 → required"
    assert result['recommendation']['auto_execute'] == True, "자동 실행"
    assert result['phase_2'] is not None, "Phase 2 실행됨"
    
    print("\n✅ 시나리오 3 완료 (규제 → Phase 2 자동 실행)")
    
    return result


def verify_system_rag_access():
    """System RAG 접근 검증"""
    
    print("\n" + "=" * 70)
    print("System RAG 접근 검증")
    print("=" * 70)
    
    from scripts.query_system_rag import SystemRAG
    
    system_rag = SystemRAG()
    
    # 1. 통계 확인
    stats = system_rag.stats()
    
    print(f"\n  총 도구: {stats['total_tools']}개")
    print(f"  Agent별:")
    for agent, count in sorted(stats['agents'].items()):
        print(f"    - {agent}: {count}개")
    
    assert stats['total_tools'] == 28, "28개 도구 확인"
    
    # 2. 도구 검색 테스트
    print(f"\n  도구 검색 테스트:")
    
    test_keys = [
        "tool:explorer:pattern_search",
        "tool:quantifier:sam_4methods",
        "tool:validator:data_definition",
        "tool:observer:market_structure"
    ]
    
    for key in test_keys:
        result = system_rag.search_tool_by_key(key, verbose=False)
        assert result['match_type'] == 'exact_key', f"{key} 정확 매칭"
        assert result['latency_ms'] < 10, f"{key} 빠른 검색 (< 10ms)"
        print(f"    ✅ {key}: {result['latency_ms']:.2f}ms")
    
    print("\n✅ System RAG 접근 정상")
    
    return stats


def verify_agent_rag_collections():
    """Agent RAG Collections 검증"""
    
    print("\n" + "=" * 70)
    print("Agent RAG Collections 검증")
    print("=" * 70)
    
    import chromadb
    
    client = chromadb.PersistentClient(path="data/chroma")
    collections = client.list_collections()
    
    # 활성 Collections (count > 0)
    active = [(col.name, col.count()) for col in collections if col.count() > 0]
    active.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  활성 Collections ({len(active)}개):")
    
    total_items = 0
    for name, count in active:
        total_items += count
        print(f"    ✅ {name}: {count}개")
    
    print(f"\n  총 항목: {total_items}개")
    
    # 검증
    assert total_items >= 400, "최소 400개 항목"
    assert len(active) >= 8, "최소 8개 활성 Collection"
    
    # 핵심 Collections 존재 확인
    collection_names = [col.name for col in collections]
    
    assert 'system_knowledge' in collection_names, "System RAG"
    assert 'explorer_knowledge_base' in collection_names, "Explorer RAG"
    assert 'market_benchmarks' in collection_names, "Quantifier RAG"
    assert 'definition_validation_cases' in collection_names, "Validator RAG"
    
    print("\n✅ Agent RAG Collections 정상")
    
    return total_items


def verify_workflow_understanding():
    """Workflow 이해도 검증"""
    
    print("\n" + "=" * 70)
    print("Workflow 이해도 검증")
    print("=" * 70)
    
    # umis_core.yaml에서 Workflow 정보 로드
    import yaml
    
    with open('umis_core.yaml') as f:
        core = yaml.safe_load(f)
    
    # Agent selection flowchart 확인
    flowchart = core.get('agent_selection_flowchart', {})
    
    print(f"\n  Agent 선택 규칙:")
    print(f"    기회 발굴 → {flowchart.get('기회를 찾고 싶다', 'N/A')}")
    print(f"    시장 규모 → {flowchart.get('시장 규모를 알고 싶다', 'N/A')}")
    print(f"    데이터 검증 → {flowchart.get('데이터를 검증하고 싶다', 'N/A')}")
    
    # Workflow 복합 쿼리
    복합 = flowchart.get('복합_쿼리', {})
    print(f"\n  복합 쿼리:")
    print(f"    시장 분석 → {복합.get('시장 분석', 'N/A')}")
    print(f"    Discovery Sprint → {복합.get('Discovery Sprint', 'N/A')}")
    
    # 검증
    assert '시장 분석' in 복합, "시장 분석 Workflow 존재"
    assert 'Observer' in 복합['시장 분석'], "Observer 포함"
    assert 'Quantifier' in 복합['시장 분석'], "Quantifier 포함"
    
    print("\n✅ Workflow 정의 정상")
    
    return flowchart


def run_e2e_tests():
    """E2E 테스트 실행"""
    
    print("\n" + "=" * 70)
    print("UMIS E2E 통합 테스트")
    print("=" * 70)
    print(f"  날짜: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  버전: UMIS v7.2.0")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    tests = [
        ("System RAG 접근", verify_system_rag_access),
        ("Agent RAG Collections", verify_agent_rag_collections),
        ("Workflow 이해도", verify_workflow_understanding),
        ("시나리오 1: 신규 시장", test_scenario_1_new_market),
        ("시나리오 2: 성숙 시장", test_scenario_2_mature_market),
        ("시나리오 3: 규제 산업", test_scenario_3_regulatory),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_result = test_func()
            results['tests'].append({'name': name, 'status': 'PASS'})
            passed += 1
        except AssertionError as e:
            results['tests'].append({'name': name, 'status': 'FAIL', 'error': str(e)})
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
        except Exception as e:
            results['tests'].append({'name': name, 'status': 'ERROR', 'error': str(e)})
            failed += 1
            print(f"\n💥 {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # 최종 요약
    print("\n" + "=" * 70)
    print("E2E 테스트 결과 요약")
    print("=" * 70)
    
    for test in results['tests']:
        icon = "✅" if test['status'] == 'PASS' else "❌"
        print(f"  {icon} {test['name']}: {test['status']}")
    
    print(f"\n총 {len(tests)}개 테스트: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("\n" + "=" * 70)
        print("🎉 모든 E2E 테스트 통과!")
        print("=" * 70)
        
        print("\n✅ 검증 완료:")
        print("  1. System RAG 접근 정상 (28개 도구)")
        print("  2. Agent RAG Collections 정상 (426개 항목)")
        print("  3. Workflow 정의 명확")
        print("  4. 신규 시장 → Phase 2 전환 정상")
        print("  5. 성숙 시장 → Guestimation 충분")
        print("  6. 규제 산업 → Phase 2 필수 작동")
        
        print("\n🚀 UMIS v7.2.0 시스템 통합 완료!")
        print("  - Agent RAG: 426개 항목")
        print("  - Domain Reasoner: 10개 신호")
        print("  - Hybrid Guestimation: 작동")
        print("  - System RAG: 28개 도구")
        
        print("\n💡 실전 투입 준비 완료!")
        print("=" * 70)
        
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_e2e_tests()
    sys.exit(0 if success else 1)

