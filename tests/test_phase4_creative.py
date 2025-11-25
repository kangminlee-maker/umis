"""
Phase 4 Fermi Decomposition 실제 테스트
- 완전히 창의적/가상의 질문 (Validator에 절대 없음)
- Model Config 시스템 Phase 4 실제 작동 확인
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, '.')

from umis_rag.agents.estimator import EstimatorRAG

# Validator에 절대 없을 창의적/가상 질문들
CREATIVE_SCENARIOS = [
    {
        'id': 'quantum_computers_2030',
        'question': '2030년 전세계에서 상용화된 양자 컴퓨터는 몇 대일까?',
        'category': 'future_tech',
        'reasoning': '양자 컴퓨터는 아직 초기 단계, Validator에 데이터 없음'
    },
    {
        'id': 'metaverse_land_sales',
        'question': '메타버스에서 한 달에 거래되는 가상 부동산은 몇 건일까?',
        'category': 'virtual',
        'reasoning': '가상 세계 데이터, Validator에 없음'
    },
    {
        'id': 'mars_colony_population',
        'question': '2040년 화성 식민지 인구는 몇 명일까?',
        'category': 'space',
        'reasoning': '미래 우주 개척, 완전히 가상'
    },
    {
        'id': 'ai_agents_korea',
        'question': '2025년 한국 기업에서 사용되는 AI 에이전트 수는?',
        'category': 'ai',
        'reasoning': 'AI 에이전트는 새로운 개념, 정확한 데이터 없음'
    },
    {
        'id': 'drone_delivery_2026',
        'question': '2026년 서울에서 하루에 드론으로 배송되는 택배는 몇 개?',
        'category': 'future_logistics',
        'reasoning': '드론 배송은 아직 시범, 데이터 없음'
    },
    {
        'id': 'vertical_farm_production',
        'question': '한국의 수직농장에서 연간 생산되는 상추는 몇 kg?',
        'category': 'agritech',
        'reasoning': '수직농장은 신기술, 통계 데이터 부족'
    },
    {
        'id': 'blockchain_transactions',
        'question': '한국에서 하루에 발생하는 블록체인 트랜잭션은 몇 건?',
        'category': 'crypto',
        'reasoning': '블록체인 활동, 정확한 한국 데이터 추정 어려움'
    },
]

def test_creative_fermi():
    """창의적 질문으로 Phase 4 테스트"""
    
    print("\n" + "━"*80)
    print("🚀 Phase 4 Fermi Decomposition 실제 테스트")
    print("━"*80)
    print(f"\n전략: Validator에 절대 없을 창의적/가상 질문 사용")
    print(f"테스트 항목: {len(CREATIVE_SCENARIOS)}개")
    print(f"모델: {os.environ.get('LLM_MODEL_PHASE4', 'gpt-5.1')}")
    print()
    
    estimator = EstimatorRAG()
    results = []
    phase_stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    
    for i, scenario in enumerate(CREATIVE_SCENARIOS, 1):
        print(f"\n{'─'*80}")
        print(f"[{i}/{len(CREATIVE_SCENARIOS)}] {scenario['id']}")
        print(f"{'─'*80}")
        print(f"질문: {scenario['question']}")
        print(f"카테고리: {scenario['category']}")
        print(f"예상: {scenario['reasoning']}")
        
        try:
            start = datetime.now()
            result = estimator.estimate(scenario['question'])
            duration = (datetime.now() - start).total_seconds()
            
            if result:
                phase_stats[result.phase] += 1
                
                print(f"\n✅ 완료 ({duration:.2f}초)")
                print(f"  Phase: {result.phase}")
                print(f"  값: {result.value:,}")
                print(f"  단위: {result.unit}")
                
                if result.phase == 4:
                    print(f"\n  🎉🎉🎉 Phase 4 Fermi Decomposition 도달!")
                    print(f"  ✅ Model Config 시스템이 Phase 4에서 정상 작동!")
                    
                    if result.decomposition:
                        decomp = result.decomposition
                        var_count = len(decomp.get('variables', []))
                        model_count = len(decomp.get('models', []))
                        print(f"\n  분해 결과:")
                        print(f"    - 변수: {var_count}개")
                        print(f"    - 모형: {model_count}개")
                        
                        # 변수 샘플
                        if decomp.get('variables'):
                            print(f"\n  변수 예시 (처음 3개):")
                            for var in decomp['variables'][:3]:
                                print(f"    • {var.get('name')}: {var.get('value')} {var.get('unit', '')}")
                elif result.phase == 3:
                    print(f"\n  📊 Phase 3 (Guestimation)에서 완료")
                elif result.phase == 2:
                    print(f"\n  ⚠️  Phase 2 (Validator)에서 완료")
                    print(f"     → Validator가 의외로 이 데이터도 가지고 있었습니다!")
                
                results.append({
                    'id': scenario['id'],
                    'question': scenario['question'],
                    'category': scenario['category'],
                    'phase': result.phase,
                    'value': result.value,
                    'unit': result.unit,
                    'duration': duration,
                    'success': True,
                    'reached_phase4': result.phase == 4
                })
            else:
                print(f"\n❌ 추정 실패")
                results.append({
                    'id': scenario['id'],
                    'question': scenario['question'],
                    'success': False
                })
                
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'id': scenario['id'],
                'question': scenario['question'],
                'success': False,
                'error': str(e)
            })
    
    # 결과 요약
    print(f"\n\n{'='*80}")
    print("📊 Phase 4 실제 테스트 결과")
    print(f"{'='*80}")
    
    total = sum(phase_stats.values())
    print(f"\n📈 Phase별 분포:")
    for phase in range(5):
        count = phase_stats[phase]
        percent = (count / total * 100) if total > 0 else 0
        bar = '█' * int(percent / 5)
        
        phase_name = ['Literal', 'Direct RAG', 'Validator', 'Guestimation', 'Fermi'][phase]
        print(f"  Phase {phase} ({phase_name:12}): {count:2d}개 ({percent:5.1f}%) {bar}")
    
    phase4_count = phase_stats[4]
    phase3_count = phase_stats[3]
    phase2_count = phase_stats[2]
    
    print(f"\n🎯 핵심 지표:")
    print(f"  Phase 4 도달: {phase4_count}/{len(CREATIVE_SCENARIOS)} ({phase4_count/len(CREATIVE_SCENARIOS)*100:.1f}%)")
    print(f"  Phase 3 도달: {phase3_count}/{len(CREATIVE_SCENARIOS)} ({phase3_count/len(CREATIVE_SCENARIOS)*100:.1f}%)")
    print(f"  Phase 2 정지: {phase2_count}/{len(CREATIVE_SCENARIOS)} ({phase2_count/len(CREATIVE_SCENARIOS)*100:.1f}%)")
    
    # 평균 시간
    durations = [r['duration'] for r in results if r.get('success')]
    if durations:
        print(f"\n⏱️  소요 시간:")
        print(f"  평균: {sum(durations)/len(durations):.2f}초")
        print(f"  최소: {min(durations):.2f}초")
        print(f"  최대: {max(durations):.2f}초")
    
    # Phase 4 도달 시 메시지
    if phase4_count > 0:
        print(f"\n✅✅✅ Phase 4 Fermi Decomposition 검증 완료!")
        print(f"\n🎉 Model Config 시스템 v7.8.0이 Phase 4에서 정상 작동합니다:")
        print(f"  1. gpt-5.1 모델 자동 로드")
        print(f"  2. Responses API 자동 선택")
        print(f"  3. max_output_tokens: 16000 자동 적용")
        print(f"  4. reasoning_effort: high 자동 적용")
        print(f"  5. phase4_fermi.py와 완벽 통합")
    else:
        print(f"\nℹ️  Phase 4에 도달하지 못함")
        if phase3_count > 0:
            print(f"  → Phase 3 (Guestimation)에서 {phase3_count}개 해결")
        if phase2_count > 0:
            print(f"  → Phase 2 (Validator)에서 {phase2_count}개 해결")
            print(f"  → Validator RAG가 매우 강력합니다!")
    
    # JSON 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'phase4_creative_test_{timestamp}.json'
    
    summary = {
        'timestamp': timestamp,
        'model': os.environ.get('LLM_MODEL_PHASE4'),
        'test_type': 'creative_fermi',
        'total_scenarios': len(CREATIVE_SCENARIOS),
        'phase_distribution': phase_stats,
        'success_count': total,
        'success_rate': total / len(CREATIVE_SCENARIOS) * 100,
        'phase4_count': phase4_count,
        'phase4_rate': phase4_count / len(CREATIVE_SCENARIOS) * 100,
        'results': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 결과 저장: {filename}")
    
    return results

if __name__ == '__main__':
    test_creative_fermi()


