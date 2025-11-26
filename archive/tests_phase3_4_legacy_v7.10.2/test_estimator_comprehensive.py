#!/usr/bin/env python3
"""
Estimator Phase 0-4 종합 테스트
- Native Mode vs External LLM 모드 비교
- 13개 문항 (기본 3개 + 확장 10개)
- Phase별 커버리지, 정확도, 시간, 비용 분석
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# v7.8.1: settings 로드 전에 LLM_MODE 설정 (External API 모드)
os.environ['LLM_MODE'] = 'gpt-4o-mini'  # cursor / gpt-4o-mini / o1-mini 등

sys.path.insert(0, '.')

from umis_rag.agents.estimator import EstimatorRAG


# 기본 3개 문항 (Phase 4 핵심)
CORE_SCENARIOS = [
    {
        'id': 'phase4_korean_businesses',
        'question': '한국 전체 사업자 수는 몇 개일까?',
        'expected_value': 8200000,
        'expected_unit': '개',
        'expected_phase': 4,
        'difficulty': 'medium',
        'domain': 'business'
    },
    {
        'id': 'phase4_seoul_population',
        'question': '서울시 인구는 몇 명일까?',
        'expected_value': 9500000,
        'expected_unit': '명',
        'expected_phase': 2,  # Validator에 있을 가능성
        'difficulty': 'easy',
        'domain': 'demographics'
    },
    {
        'id': 'phase4_coffee_shops',
        'question': '한국 커피 전문점 수는?',
        'expected_value': 100000,
        'expected_unit': '개',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'retail'
    }
]

# 확장 10개 문항
EXTENDED_SCENARIOS = [
    {
        'id': 'extended_delivery_riders',
        'question': '한국 전체 배달 기사(라이더) 수는?',
        'expected_value': 400000,
        'expected_unit': '명',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'logistics'
    },
    {
        'id': 'extended_chicken_delivery',
        'question': '한국 연간 치킨 배달 주문 건수는?',
        'expected_value': 1100000000,
        'expected_unit': '건',
        'expected_phase': 4,
        'difficulty': 'hard',
        'domain': 'food_service'
    },
    {
        'id': 'extended_taxi_passengers',
        'question': '서울시 하루 평균 택시 승객 수는?',
        'expected_value': 1500000,
        'expected_unit': '명',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'transportation'
    },
    {
        'id': 'extended_credit_card',
        'question': '한국 연간 신용카드 승인 건수는?',
        'expected_value': 30000000000,
        'expected_unit': '건',
        'expected_phase': 3,
        'difficulty': 'hard',
        'domain': 'finance'
    },
    {
        'id': 'extended_hospital_visits',
        'question': '한국 연간 병원 외래 진료 건수는?',
        'expected_value': 1700000000,
        'expected_unit': '건',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'healthcare'
    },
    {
        'id': 'extended_private_education',
        'question': '한국 초중고 학생 연간 사교육비 총액은?',
        'expected_value': 26000000000000,
        'expected_unit': '원',
        'expected_phase': 2,  # 통계청 데이터 가능
        'difficulty': 'medium',
        'domain': 'education'
    },
    {
        'id': 'extended_jeonse_contracts',
        'question': '서울시 연간 전세 계약 건수는?',
        'expected_value': 400000,
        'expected_unit': '건',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'real_estate'
    },
    {
        'id': 'extended_ott_subscribers',
        'question': '한국 유료 OTT 구독자 수는?',
        'expected_value': 25000000,
        'expected_unit': '명',
        'expected_phase': 3,
        'difficulty': 'medium',
        'domain': 'entertainment'
    },
    {
        'id': 'extended_coupang_boxes',
        'question': '쿠팡 일평균 배송 물량(박스 수)은?',
        'expected_value': 12000000,
        'expected_unit': '박스',
        'expected_phase': 3,
        'difficulty': 'hard',
        'domain': 'ecommerce'
    },
    {
        'id': 'extended_disposable_cups',
        'question': '한국 연간 일회용 컵 사용량은?',
        'expected_value': 33000000000,
        'expected_unit': '개',
        'expected_phase': 4,
        'difficulty': 'hard',
        'domain': 'environment'
    }
]

ALL_SCENARIOS = CORE_SCENARIOS + EXTENDED_SCENARIOS


def calculate_accuracy_score(estimated, expected):
    """정확도 점수 계산 (log10 오차 기반)"""
    if estimated == 0 or expected == 0:
        return 0.0
    
    import math
    ratio = estimated / expected
    log_error = abs(math.log10(ratio))
    
    # log10 오차 → 점수 (0~100)
    if log_error <= 0.1:  # 10% 이내
        return 100.0
    elif log_error <= 0.3:  # 2배 이내
        return 90.0
    elif log_error <= 0.5:  # 3배 이내
        return 70.0
    elif log_error <= 1.0:  # 10배 이내
        return 50.0
    else:
        return max(0, 50 - (log_error - 1.0) * 25)


def test_single_mode(mode_name, scenarios, estimator_kwargs=None):
    """단일 모드로 전체 시나리오 테스트"""
    
    print(f"\n{'='*100}")
    print(f"🧪 {mode_name} 모드 테스트")
    print(f"{'='*100}\n")
    
    if estimator_kwargs is None:
        estimator_kwargs = {}
    
    estimator = EstimatorRAG(**estimator_kwargs)
    results = []
    phase_stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*100}")
        print(f"[{i}/{len(scenarios)}] {scenario['id']}")
        print(f"{'─'*100}")
        print(f"질문: {scenario['question']}")
        print(f"예상 답: {scenario['expected_value']:,} {scenario['expected_unit']}")
        print(f"난이도: {scenario['difficulty']} | 도메인: {scenario['domain']}")
        
        try:
            start = datetime.now()
            result = estimator.estimate(scenario['question'])
            duration = (datetime.now() - start).total_seconds()
            
            if result:
                phase_stats[result.phase] += 1
                accuracy = calculate_accuracy_score(result.value, scenario['expected_value'])
                
                print(f"\n✅ 완료 ({duration:.2f}초)")
                print(f"  Phase: {result.phase}")
                print(f"  추정값: {result.value:,} {result.unit}")
                print(f"  신뢰도: {result.confidence:.2f}")
                print(f"  정확도: {accuracy:.1f}점")
                
                # Phase 정보
                phase_names = ['Literal', 'Direct RAG', 'Validator', 'Guestimation', 'Fermi']
                print(f"  방법: Phase {result.phase} ({phase_names[result.phase]})")
                
                results.append({
                    'id': scenario['id'],
                    'question': scenario['question'],
                    'domain': scenario['domain'],
                    'difficulty': scenario['difficulty'],
                    'expected_value': scenario['expected_value'],
                    'expected_unit': scenario['expected_unit'],
                    'expected_phase': scenario.get('expected_phase'),
                    'phase': result.phase,
                    'value': result.value,
                    'unit': result.unit,
                    'confidence': result.confidence,
                    'accuracy': accuracy,
                    'duration': duration,
                    'success': True
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
    
    # 모드별 결과 요약
    print(f"\n\n{'='*100}")
    print(f"📊 {mode_name} 모드 결과 요약")
    print(f"{'='*100}\n")
    
    total = sum(phase_stats.values())
    print(f"📈 Phase별 분포:")
    for phase in range(5):
        count = phase_stats[phase]
        percent = (count / total * 100) if total > 0 else 0
        bar = '█' * int(percent / 5)
        
        phase_names = ['Literal', 'Direct RAG', 'Validator', 'Guestimation', 'Fermi']
        print(f"  Phase {phase} ({phase_names[phase]:12}): {count:2d}개 ({percent:5.1f}%) {bar}")
    
    # 평균 지표
    successful = [r for r in results if r.get('success')]
    if successful:
        avg_accuracy = sum(r.get('accuracy', 0) for r in successful) / len(successful)
        avg_confidence = sum(r.get('confidence', 0) for r in successful) / len(successful)
        avg_duration = sum(r.get('duration', 0) for r in successful) / len(successful)
        
        print(f"\n🎯 평균 지표:")
        print(f"  정확도: {avg_accuracy:.1f}점")
        print(f"  신뢰도: {avg_confidence:.2f}")
        print(f"  소요 시간: {avg_duration:.2f}초")
    
    return {
        'mode': mode_name,
        'phase_distribution': phase_stats,
        'results': results,
        'summary': {
            'total': len(scenarios),
            'success': len(successful),
            'success_rate': len(successful) / len(scenarios) * 100 if scenarios else 0,
            'avg_accuracy': avg_accuracy if successful else 0,
            'avg_confidence': avg_confidence if successful else 0,
            'avg_duration': avg_duration if successful else 0
        }
    }


def compare_modes(native_results, external_results):
    """Native vs External 비교 분석"""
    
    print(f"\n\n{'='*100}")
    print("🔬 Native vs External 비교 분석")
    print(f"{'='*100}\n")
    
    # 1. Phase 분포 비교
    print("📊 Phase 분포 비교:\n")
    print(f"{'Phase':<15} | {'Native':<15} | {'External':<15} | {'차이':<15}")
    print("─" * 70)
    
    phase_names = ['Literal', 'Direct RAG', 'Validator', 'Guestimation', 'Fermi']
    for phase in range(5):
        native_count = native_results['phase_distribution'][phase]
        external_count = external_results['phase_distribution'][phase]
        diff = native_count - external_count
        
        print(f"{phase} ({phase_names[phase]:12}) | {native_count:>2d}개 ({native_count/13*100:>5.1f}%) | "
              f"{external_count:>2d}개 ({external_count/13*100:>5.1f}%) | {diff:+3d}")
    
    # 2. 성능 지표 비교
    print(f"\n🎯 성능 지표 비교:\n")
    print(f"{'지표':<20} | {'Native':<15} | {'External':<15} | {'차이':<15}")
    print("─" * 70)
    
    metrics = [
        ('정확도', 'avg_accuracy', '점'),
        ('신뢰도', 'avg_confidence', ''),
        ('소요 시간', 'avg_duration', '초')
    ]
    
    for label, key, unit in metrics:
        native_val = native_results['summary'][key]
        external_val = external_results['summary'][key]
        diff = native_val - external_val
        
        if key == 'avg_duration':
            diff_str = f"{diff:+.2f}{unit}"
        elif key == 'avg_confidence':
            diff_str = f"{diff:+.2f}"
        else:
            diff_str = f"{diff:+.1f}{unit}"
        
        print(f"{label:<20} | {native_val:>13.2f}{unit:>2} | {external_val:>13.2f}{unit:>2} | {diff_str:>15}")
    
    # 3. 개별 문항 비교
    print(f"\n📋 개별 문항 비교 (Phase 차이):\n")
    
    native_by_id = {r['id']: r for r in native_results['results'] if r.get('success')}
    external_by_id = {r['id']: r for r in external_results['results'] if r.get('success')}
    
    phase_diffs = []
    for scenario_id in native_by_id.keys():
        if scenario_id in external_by_id:
            native_phase = native_by_id[scenario_id]['phase']
            external_phase = external_by_id[scenario_id]['phase']
            if native_phase != external_phase:
                phase_diffs.append({
                    'id': scenario_id,
                    'question': native_by_id[scenario_id]['question'],
                    'native_phase': native_phase,
                    'external_phase': external_phase
                })
    
    if phase_diffs:
        for diff in phase_diffs:
            phase_names = ['Literal', 'Direct RAG', 'Validator', 'Guestimation', 'Fermi']
            print(f"  • {diff['id']}")
            print(f"    질문: {diff['question']}")
            print(f"    Native: Phase {diff['native_phase']} ({phase_names[diff['native_phase']]})")
            print(f"    External: Phase {diff['external_phase']} ({phase_names[diff['external_phase']]})")
            print()
    else:
        print("  → 모든 문항이 동일한 Phase에서 해결되었습니다.")
    
    # 4. 비용 분석 (External만)
    print(f"\n💰 비용 분석:\n")
    print(f"  Native Mode: $0 (무료)")
    
    # External 비용 추정 (Phase 4만 계산)
    phase4_count = external_results['phase_distribution'][4]
    phase4_cost = phase4_count * 0.003  # o1-mini 기준
    
    phase3_count = external_results['phase_distribution'][3]
    phase3_cost = phase3_count * 0.0001  # gpt-4o-mini 기준
    
    total_cost = phase4_cost + phase3_cost
    
    print(f"  External Mode:")
    print(f"    - Phase 4 ({phase4_count}개): ${phase4_cost:.4f}")
    print(f"    - Phase 3 ({phase3_count}개): ${phase3_cost:.4f}")
    print(f"    - 총 비용: ${total_cost:.4f}")
    print(f"    - 1,000회 기준: ${total_cost * 1000 / 13:.2f}")


def run_comprehensive_test():
    """종합 테스트 실행 (v7.8.1: External Mode만)"""
    
    print("\n" + "="*100)
    print("🚀 Estimator Phase 0-4 종합 테스트 (v7.8.1)")
    print("="*100)
    print(f"\n⚠️  Cursor AI (LLM_MODE=cursor): 대화형 추정 전용 (자동 테스트 불가)")
    print(f"✅ External LLM Mode로 테스트 진행 (LLM_MODE=gpt-4o-mini)")
    print(f"\n문항: {len(ALL_SCENARIOS)}개 (기본 3개 + 확장 10개)")
    print(f"모드: External (o1-mini/gpt-4o-mini)")
    print()
    
    # External Mode만 테스트
    original_mode = os.environ.get('LLM_MODE')  # v7.8.1: LLM_MODE로 변경
    os.environ['LLM_MODE'] = 'gpt-4o-mini'
    
    external_results = test_single_mode(
        mode_name="External (o1-mini/gpt-4o-mini)",
        scenarios=ALL_SCENARIOS
    )
    
    # 환경 복구
    if original_mode:
        os.environ['LLM_MODE'] = original_mode
    else:
        os.environ.pop('LLM_MODE', None)
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'estimator_comprehensive_{timestamp}.json'
    
    output = {
        'timestamp': timestamp,
        'test_type': 'comprehensive_phase_0_4_external_only',
        'note': 'Native Mode는 대화형 추정 전용 (자동 테스트 불가)',
        'scenarios': ALL_SCENARIOS,
        'external_results': external_results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n\n💾 결과 저장: {filename}")
    print("\n✅ 종합 테스트 완료!")
    
    return output


if __name__ == '__main__':
    run_comprehensive_test()




