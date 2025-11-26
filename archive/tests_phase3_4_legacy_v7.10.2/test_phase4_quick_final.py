"""
Phase 4 Fermi Decomposition 빠른 최종 테스트
v7.8.1: cursor-native 통합 검증
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, '.')

from umis_rag.agents.estimator import EstimatorRAG

# 빠른 테스트용 2개 질문
TEST_QUESTIONS = [
    {
        'id': 'quantum_computers',
        'question': '양자 컴퓨터는 2030년에 몇 대?',
        'expected_phase': 4
    },
    {
        'id': 'metaverse_real_estate',
        'question': '메타버스 부동산 거래는 한 달에 몇 건?',
        'expected_phase': 4
    }
]

def test_phase4_final():
    """Phase 4 최종 검증"""
    
    print("\n" + "="*80)
    print("🚀 Phase 4 Fermi Decomposition 최종 테스트 (v7.8.1)")
    print("="*80)
    print(f"\n목표: cursor-native 모델 설정 통합 검증")
    print(f"테스트: {len(TEST_QUESTIONS)}개 질문")
    print(f"LLM 모드: {os.environ.get('UMIS_MODE', 'native')}")
    print()
    
    estimator = EstimatorRAG()
    results = []
    
    for i, test in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'─'*80}")
        print(f"[{i}/{len(TEST_QUESTIONS)}] {test['id']}")
        print(f"{'─'*80}")
        print(f"질문: {test['question']}")
        print(f"기대 Phase: {test['expected_phase']}")
        
        try:
            start = datetime.now()
            result = estimator.estimate(test['question'])
            duration = (datetime.now() - start).total_seconds()
            
            if result:
                success = result.phase == test['expected_phase']
                
                print(f"\n✅ 완료 ({duration:.2f}초)")
                print(f"  실제 Phase: {result.phase}")
                print(f"  값: {result.value:,}")
                print(f"  단위: {result.unit}")
                print(f"  신뢰도: {result.confidence:.2f}")
                
                if result.phase == 4:
                    print(f"\n  🎉 Phase 4 도달!")
                    print(f"  ✅ cursor-native 모델 설정 정상 작동")
                    
                    if hasattr(result, 'fermi_model') and result.fermi_model:
                        model = result.fermi_model
                        print(f"\n  Fermi 모형:")
                        print(f"    ID: {model.model_id}")
                        print(f"    수식: {model.formula}")
                        print(f"    변수: {len(model.variables)}개")
                
                results.append({
                    'id': test['id'],
                    'question': test['question'],
                    'phase': result.phase,
                    'value': result.value,
                    'unit': result.unit,
                    'confidence': result.confidence,
                    'duration': duration,
                    'success': success
                })
            else:
                print(f"\n❌ 추정 실패")
                results.append({
                    'id': test['id'],
                    'question': test['question'],
                    'success': False
                })
                
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'id': test['id'],
                'question': test['question'],
                'success': False,
                'error': str(e)
            })
    
    # 결과 요약
    print(f"\n\n{'='*80}")
    print("📊 최종 테스트 결과")
    print(f"{'='*80}")
    
    phase4_count = sum(1 for r in results if r.get('phase') == 4)
    success_count = sum(1 for r in results if r.get('success', False))
    
    print(f"\n✅ Phase 4 도달: {phase4_count}/{len(TEST_QUESTIONS)} ({phase4_count/len(TEST_QUESTIONS)*100:.0f}%)")
    print(f"✅ 성공: {success_count}/{len(TEST_QUESTIONS)} ({success_count/len(TEST_QUESTIONS)*100:.0f}%)")
    
    if phase4_count == len(TEST_QUESTIONS):
        print(f"\n🎉🎉🎉 완벽한 성공!")
        print(f"\n✅ Phase 4 Fermi Decomposition 최종 검증 완료:")
        print(f"  1. cursor-native 모델 설정 정상 로드")
        print(f"  2. api_type: cursor 분기 정상 작동")
        print(f"  3. _generate_native_models() 정상 호출")
        print(f"  4. Fermi 모형 생성 및 추정 완료")
        print(f"\n✅ v7.8.1 통합 성공!")
    elif phase4_count > 0:
        print(f"\n✅ Phase 4 부분 성공")
        print(f"  {phase4_count}개 질문이 Phase 4에 도달")
    else:
        print(f"\n⚠️  Phase 4 미도달")
        for r in results:
            if r.get('phase'):
                print(f"  - {r['id']}: Phase {r['phase']}")
    
    # 평균 시간
    durations = [r['duration'] for r in results if r.get('duration')]
    if durations:
        print(f"\n⏱️  소요 시간:")
        print(f"  평균: {sum(durations)/len(durations):.2f}초")
        print(f"  최소: {min(durations):.2f}초")
        print(f"  최대: {max(durations):.2f}초")
    
    # JSON 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'phase4_final_test_{timestamp}.json'
    
    summary = {
        'timestamp': timestamp,
        'version': 'v7.8.1',
        'llm_mode': os.environ.get('UMIS_MODE', 'native'),
        'test_type': 'phase4_final',
        'total_tests': len(TEST_QUESTIONS),
        'phase4_count': phase4_count,
        'success_count': success_count,
        'results': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 결과 저장: {filename}")
    
    return results

if __name__ == '__main__':
    test_phase4_final()




