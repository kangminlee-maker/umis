"""
Estimator Phase 0-4 통합 테스트
- 13개 Fermi 문제 (3개 기본 + 10개 확장)
- Phase별 도달률 확인
- Model Config 시스템 사용
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.abspath('.'))

from umis_rag.agents.estimator import EstimatorRAG

# 13개 테스트 시나리오
SCENARIOS = [
    # 기본 3문제
    {
        'id': 'shampoo',
        'question': '한국에서 연간 소비되는 샴푸 양은?',
        'expected_value': 32000000000,
        'unit': '갑/년',
        'difficulty': 'medium',
        'category': 'basic'
    },
    {
        'id': 'piano_tuners',
        'question': '서울시에 피아노 조율사는 몇 명이나 있을까?',
        'expected_value': 250,
        'unit': '명',
        'difficulty': 'hard',
        'category': 'basic'
    },
    {
        'id': 'coffee_jeju',
        'question': '제주도에서 1년에 소비되는 커피는?',
        'expected_value': 50000000,
        'unit': '잔/년',
        'difficulty': 'medium',
        'category': 'basic'
    },
    # 확장 10문제
    {
        'id': 'delivery_boxes',
        'question': '부산에서 1년에 사용되는 택배 박스 수는?',
        'expected_value': 100000000,
        'unit': '개/년',
        'difficulty': 'medium',
        'category': 'extended'
    },
    {
        'id': 'chicken_consumption',
        'question': '한국에서 1년에 소비되는 치킨 수는?',
        'expected_value': 600000000,
        'unit': '마리/년',
        'difficulty': 'medium',
        'category': 'extended'
    },
    {
        'id': 'subway_passengers',
        'question': '서울 지하철 하루 이용객 수는?',
        'expected_value': 7000000,
        'unit': '명/일',
        'difficulty': 'easy',
        'category': 'extended'
    },
    {
        'id': 'convenience_stores',
        'question': '한국 편의점 총 개수는?',
        'expected_value': 50000,
        'unit': '개',
        'difficulty': 'easy',
        'category': 'extended'
    },
    {
        'id': 'taxis_seoul',
        'question': '서울 택시 대수는?',
        'expected_value': 70000,
        'unit': '대',
        'difficulty': 'easy',
        'category': 'extended'
    },
    {
        'id': 'smartphone_users',
        'question': '한국 스마트폰 사용자 수는?',
        'expected_value': 45000000,
        'unit': '명',
        'difficulty': 'easy',
        'category': 'extended'
    },
    {
        'id': 'gas_stations',
        'question': '한국 주유소 개수는?',
        'expected_value': 12000,
        'unit': '개',
        'difficulty': 'easy',
        'category': 'extended'
    },
    {
        'id': 'wedding_halls',
        'question': '서울 웨딩홀 개수는?',
        'expected_value': 500,
        'unit': '개',
        'difficulty': 'medium',
        'category': 'extended'
    },
    {
        'id': 'gym_members',
        'question': '한국 헬스장 회원 수는?',
        'expected_value': 5000000,
        'unit': '명',
        'difficulty': 'medium',
        'category': 'extended'
    },
    {
        'id': 'pizza_orders',
        'question': '한국에서 1년에 주문되는 피자 수는?',
        'expected_value': 200000000,
        'unit': '판/년',
        'difficulty': 'medium',
        'category': 'extended'
    }
]

def test_estimator_phases(model_name: str = None):
    """Estimator Phase 0-4 통합 테스트"""
    
    print("\n" + "━"*80)
    print("🚀 Estimator Phase 0-4 통합 테스트")
    print("━"*80)
    
    # 모델 설정
    if model_name:
        original_model = os.environ.get('LLM_MODEL_PHASE4')
        os.environ['LLM_MODEL_PHASE4'] = model_name
        print(f"\n📌 테스트 모델: {model_name}")
    else:
        model_name = os.environ.get('LLM_MODEL_PHASE4', 'default')
        print(f"\n📌 테스트 모델: {model_name} (.env 설정)")
    
    print(f"📊 테스트 항목: {len(SCENARIOS)}개")
    print(f"   - 기본: {len([s for s in SCENARIOS if s['category'] == 'basic'])}개")
    print(f"   - 확장: {len([s for s in SCENARIOS if s['category'] == 'extended'])}개")
    print()
    
    # Estimator 초기화
    estimator = EstimatorRAG()
    
    results = []
    phase_stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    
    # 각 시나리오 테스트
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n{'─'*80}")
        print(f"[{i:2d}/{len(SCENARIOS)}] {scenario['id']}")
        print(f"{'─'*80}")
        print(f"질문: {scenario['question']}")
        
        try:
            start_time = datetime.now()
            
            # 추정 실행
            result = estimator.estimate(scenario['question'])
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # 결과 처리
            if result:
                phase = result.phase
                value = result.value
                unit = result.unit
                
                # 오차 계산
                expected = scenario['expected_value']
                error_ratio = abs(value - expected) / expected if expected > 0 else float('inf')
                error_percent = error_ratio * 100
                
                phase_stats[phase] += 1
                
                print(f"\n✅ 완료 ({duration:.2f}초)")
                print(f"  Phase: {phase}")
                print(f"  값: {value:,}")
                print(f"  단위: {unit}")
                print(f"  예상값: {expected:,}")
                print(f"  오차: {error_percent:.1f}%")
                
                results.append({
                    'id': scenario['id'],
                    'category': scenario['category'],
                    'question': scenario['question'],
                    'phase': phase,
                    'value': value,
                    'unit': unit,
                    'expected': expected,
                    'error_ratio': error_ratio,
                    'error_percent': error_percent,
                    'duration': duration,
                    'success': True
                })
            else:
                print(f"\n❌ 추정 실패")
                results.append({
                    'id': scenario['id'],
                    'category': scenario['category'],
                    'question': scenario['question'],
                    'phase': None,
                    'success': False,
                    'duration': duration
                })
                
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'id': scenario['id'],
                'category': scenario['category'],
                'question': scenario['question'],
                'success': False,
                'error': str(e)
            })
    
    # 최종 통계
    print(f"\n\n{'='*80}")
    print("📊 Phase 0-4 통합 테스트 결과")
    print(f"{'='*80}")
    
    # Phase별 분포
    print(f"\n📈 Phase별 도달 분포:")
    total_success = sum(phase_stats.values())
    for phase in range(5):
        count = phase_stats[phase]
        percent = (count / total_success * 100) if total_success > 0 else 0
        bar = "█" * int(percent / 5)
        print(f"  Phase {phase}: {count:2d}개 ({percent:5.1f}%) {bar}")
    
    # 카테고리별 성공률
    print(f"\n📊 카테고리별 결과:")
    basic_results = [r for r in results if r['category'] == 'basic']
    extended_results = [r for r in results if r['category'] == 'extended']
    
    basic_success = len([r for r in basic_results if r.get('success')])
    extended_success = len([r for r in extended_results if r.get('success')])
    
    print(f"  기본 (3개):  {basic_success}/3  ({basic_success/3*100:.1f}%)")
    print(f"  확장 (10개): {extended_success}/10 ({extended_success/10*100:.1f}%)")
    print(f"  전체 (13개): {total_success}/13 ({total_success/13*100:.1f}%)")
    
    # 평균 소요 시간
    durations = [r.get('duration', 0) for r in results if r.get('success')]
    if durations:
        avg_duration = sum(durations) / len(durations)
        print(f"\n⏱️  평균 소요 시간: {avg_duration:.2f}초")
        print(f"   최소: {min(durations):.2f}초")
        print(f"   최대: {max(durations):.2f}초")
    
    # 오차 분석
    errors = [r.get('error_percent', 0) for r in results if r.get('success') and r.get('error_percent')]
    if errors:
        avg_error = sum(errors) / len(errors)
        print(f"\n📏 평균 오차: {avg_error:.1f}%")
    
    # JSON 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"estimator_phase0_4_test_{timestamp}.json"
    
    summary = {
        'model': model_name,
        'timestamp': timestamp,
        'total_scenarios': len(SCENARIOS),
        'phase_distribution': phase_stats,
        'success_count': total_success,
        'success_rate': total_success / len(SCENARIOS) * 100,
        'avg_duration': avg_duration if durations else 0,
        'avg_error_percent': avg_error if errors else 0,
        'results': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 결과 저장: {filename}")
    
    # 복원
    if model_name and 'original_model' in locals() and original_model:
        os.environ['LLM_MODEL_PHASE4'] = original_model
    
    return results

def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Estimator Phase 0-4 통합 테스트')
    parser.add_argument('--model', type=str, help='테스트할 모델 이름')
    
    args = parser.parse_args()
    
    results = test_estimator_phases(model_name=args.model)
    
    print("\n" + "="*80)
    print("✅ 테스트 완료!")
    print("="*80)
    
    return results

if __name__ == "__main__":
    main()
