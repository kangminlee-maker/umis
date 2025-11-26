"""
v7.11.0 EstimatorRAG - 10개 Fermi 문제 테스트

기존 Phase 4 Extended 테스트의 10개 문항을 v7.11.0 Fusion Architecture로 테스트
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.utils.logger import logger


# 10개 Fermi 문제 정의
FERMI_PROBLEMS = [
    {
        'id': 'extended_delivery_riders',
        'question': '한국 전체 배달 기사(라이더) 수는?',
        'name': '한국 전체 배달 기사(라이더) 수',
        'expected_value': 400000,
        'unit': '명',
        'context': {
            'domain': 'Platform Economy',
            'region': 'Korea',
            'industry': 'Food Delivery'
        }
    },
    {
        'id': 'extended_chicken_delivery',
        'question': '한국 연간 치킨 배달 주문 건수는?',
        'name': '한국 연간 치킨 배달 주문 건수',
        'expected_value': 1100000000,
        'unit': '건',
        'context': {
            'domain': 'Food Delivery',
            'region': 'Korea',
            'industry': 'Restaurant'
        }
    },
    {
        'id': 'extended_taxi_passengers',
        'question': '서울시 하루 평균 택시 승객 수는?',
        'name': '서울시 하루 평균 택시 승객 수',
        'expected_value': 1500000,
        'unit': '명',
        'context': {
            'domain': 'Transportation',
            'region': 'Seoul',
            'industry': 'Taxi'
        }
    },
    {
        'id': 'extended_credit_card',
        'question': '한국 연간 신용카드 승인 건수는?',
        'name': '한국 연간 신용카드 승인 건수',
        'expected_value': 30000000000,
        'unit': '건',
        'context': {
            'domain': 'FinTech',
            'region': 'Korea',
            'industry': 'Payment'
        }
    },
    {
        'id': 'extended_hospital_visits',
        'question': '한국 연간 병원 외래 진료 건수는?',
        'name': '한국 연간 병원 외래 진료 건수',
        'expected_value': 1700000000,
        'unit': '건',
        'context': {
            'domain': 'Healthcare',
            'region': 'Korea',
            'industry': 'Hospital'
        }
    },
    {
        'id': 'extended_private_education',
        'question': '한국 초중고 학생 연간 사교육비 총액은?',
        'name': '한국 초중고 학생 연간 사교육비 총액',
        'expected_value': 26000000000000,
        'unit': '원',
        'context': {
            'domain': 'Education',
            'region': 'Korea',
            'industry': 'Private Education'
        }
    },
    {
        'id': 'extended_jeonse_contracts',
        'question': '서울시 연간 전세 계약 건수는?',
        'name': '서울시 연간 전세 계약 건수',
        'expected_value': 400000,
        'unit': '건',
        'context': {
            'domain': 'Real Estate',
            'region': 'Seoul',
            'industry': 'Rental'
        }
    },
    {
        'id': 'extended_ott_subscribers',
        'question': '한국 유료 OTT 구독자 수는?',
        'name': '한국 유료 OTT 구독자 수',
        'expected_value': 25000000,
        'unit': '명',
        'context': {
            'domain': 'Media',
            'region': 'Korea',
            'industry': 'Streaming'
        }
    },
    {
        'id': 'extended_coupang_boxes',
        'question': '쿠팡 일평균 배송 물량은?',
        'name': '쿠팡 일평균 배송 물량',
        'expected_value': 12000000,
        'unit': '박스',
        'context': {
            'domain': 'E-commerce',
            'region': 'Korea',
            'industry': 'Logistics'
        }
    },
    {
        'id': 'extended_disposable_cups',
        'question': '한국 연간 일회용 컵 사용량은?',
        'name': '한국 연간 일회용 컵 사용량',
        'expected_value': 33000000000,
        'unit': '개',
        'context': {
            'domain': 'Environment',
            'region': 'Korea',
            'industry': 'Cafe'
        }
    }
]


def calculate_error_percentage(estimated: float, expected: float) -> float:
    """오차율 계산"""
    if expected == 0:
        return 0.0
    return abs(estimated - expected) / expected * 100


def evaluate_result(problem: dict, result) -> dict:
    """결과 평가"""
    estimated_value = result.value
    expected_value = problem['expected_value']
    
    error_pct = calculate_error_percentage(estimated_value, expected_value)
    
    # 정확도 점수 (50점 만점)
    if error_pct <= 10:
        accuracy_score = 50
    elif error_pct <= 20:
        accuracy_score = 40
    elif error_pct <= 30:
        accuracy_score = 30
    elif error_pct <= 50:
        accuracy_score = 20
    elif error_pct <= 100:
        accuracy_score = 10
    else:
        accuracy_score = 5
    
    # Certainty 점수 (20점 만점)
    certainty_map = {'high': 20, 'medium': 15, 'low': 10}
    certainty_score = certainty_map.get(result.certainty, 10)
    
    # 사용한 Stage 점수 (20점 만점)
    stage_score = 0
    if 'Evidence' in result.source:
        stage_score = 20  # 확정 값
    elif 'Prior' in result.source:
        stage_score = 15  # Generative Prior
    elif 'Fermi' in result.source:
        stage_score = 18  # 구조적 설명
    elif 'Fusion' in result.source:
        stage_score = 17  # 통합
    else:
        stage_score = 10
    
    # 효율성 점수 (10점 만점)
    cost_summary = result.cost
    llm_calls = cost_summary.get('llm_calls', 0)
    
    if llm_calls == 0:
        efficiency_score = 10  # Phase 0 즉시 반환
    elif llm_calls <= 3:
        efficiency_score = 9
    elif llm_calls <= 6:
        efficiency_score = 8
    elif llm_calls <= 10:
        efficiency_score = 7
    else:
        efficiency_score = 5
    
    total_score = accuracy_score + certainty_score + stage_score + efficiency_score
    
    return {
        'estimated_value': estimated_value,
        'expected_value': expected_value,
        'error_pct': error_pct,
        'accuracy_score': accuracy_score,
        'certainty_score': certainty_score,
        'stage_score': stage_score,
        'efficiency_score': efficiency_score,
        'total_score': total_score,
        'max_score': 100
    }


def run_test():
    """10개 문제 테스트 실행"""
    
    print("=" * 120)
    print("🚀 v7.11.0 EstimatorRAG - 10개 Fermi 문제 테스트")
    print("=" * 120)
    print()
    print("📊 테스트 구성:")
    print("  • 아키텍처: v7.11.0 Fusion Architecture (4-Stage)")
    print("  • 문제 수: 10개")
    print("  • 특징:")
    print("    - ✅ 재귀 완전 제거 (Recursion FORBIDDEN)")
    print("    - ✅ Budget 기반 탐색 (max_llm_calls=10, max_depth=2)")
    print("    - ✅ Evidence → Prior → Fermi → Fusion")
    print("    - ✅ Phase 0 (Literal) + Guardrail Engine")
    print()
    
    # EstimatorRAG 초기화
    estimator = EstimatorRAG()
    
    all_results = []
    
    for i, problem in enumerate(FERMI_PROBLEMS, 1):
        print("\n" + "=" * 120)
        print(f"📋 문제 {i}/10: {problem['name']}")
        print(f"   질문: {problem['question']}")
        print(f"   정답: {problem['expected_value']:,} {problem['unit']}")
        print("=" * 120)
        
        try:
            start_time = time.time()
            
            # Context 생성
            context = problem['context']
            
            # 추정 실행
            logger.info(f"\n[Test {i}] {problem['name']}")
            result = estimator.estimate(
                question=problem['question'],
                context=context
            )
            
            elapsed = time.time() - start_time
            
            # 평가
            evaluation = evaluate_result(problem, result)
            
            # 결과 출력
            print(f"\n✅ 결과:")
            print(f"   추정값: {result.value:,.0f} {problem['unit']}")
            print(f"   정답: {evaluation['expected_value']:,} {problem['unit']}")
            print(f"   오차율: {evaluation['error_pct']:.1f}%")
            print(f"   Certainty: {result.certainty}")
            print(f"   Source: {result.source}")
            print(f"   실행 시간: {elapsed:.2f}초")
            print(f"\n📊 점수:")
            print(f"   정확도: {evaluation['accuracy_score']}/50")
            print(f"   Certainty: {evaluation['certainty_score']}/20")
            print(f"   Stage: {evaluation['stage_score']}/20")
            print(f"   효율성: {evaluation['efficiency_score']}/10")
            print(f"   총점: {evaluation['total_score']}/100")
            
            # 비용 정보
            cost_summary = result.cost
            if cost_summary and isinstance(cost_summary, dict):
                print(f"\n💰 비용:")
                print(f"   LLM Calls: {cost_summary.get('llm_calls', 0)}")
                print(f"   Variables: {cost_summary.get('variables', 0)}")
                print(f"   Time: {cost_summary.get('time', 0):.2f}초")
            
            # Decomposition 정보
            if result.decomposition:
                print(f"\n🔍 분해:")
                formula = result.decomposition.get('formula', '')
                variables = result.decomposition.get('variables', {})
                print(f"   Formula: {formula}")
                if variables:
                    print(f"   Variables: {len(variables)}개")
                    for var, val in list(variables.items())[:3]:
                        print(f"     - {var}: {val:,.0f}")
            
            # 결과 저장
            all_results.append({
                'problem_id': problem['id'],
                'problem_name': problem['name'],
                'question': problem['question'],
                'estimated_value': result.value,
                'expected_value': problem['expected_value'],
                'unit': problem['unit'],
                'error_pct': evaluation['error_pct'],
                'certainty': result.certainty,
                'source': result.source,
                'elapsed_time': elapsed,
                'cost': cost_summary,
                'evaluation': evaluation,
                'decomposition': result.decomposition,
                'metadata': result.metadata
            })
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            logger.error(f"Problem {i} failed: {e}", exc_info=True)
            
            all_results.append({
                'problem_id': problem['id'],
                'problem_name': problem['name'],
                'question': problem['question'],
                'error': str(e),
                'status': 'failed'
            })
    
    # 최종 통계
    print("\n" + "=" * 120)
    print("🏆 최종 결과")
    print("=" * 120)
    print()
    
    successful_results = [r for r in all_results if 'evaluation' in r]
    
    if successful_results:
        avg_total_score = sum(r['evaluation']['total_score'] for r in successful_results) / len(successful_results)
        avg_accuracy_score = sum(r['evaluation']['accuracy_score'] for r in successful_results) / len(successful_results)
        avg_certainty_score = sum(r['evaluation']['certainty_score'] for r in successful_results) / len(successful_results)
        avg_stage_score = sum(r['evaluation']['stage_score'] for r in successful_results) / len(successful_results)
        avg_efficiency_score = sum(r['evaluation']['efficiency_score'] for r in successful_results) / len(successful_results)
        avg_error_pct = sum(r['error_pct'] for r in successful_results) / len(successful_results)
        avg_time = sum(r['elapsed_time'] for r in successful_results) / len(successful_results)
        
        total_llm_calls = sum(r['cost'].get('llm_calls', 0) for r in successful_results if 'cost' in r and r['cost'])
        avg_llm_calls = total_llm_calls / len(successful_results) if successful_results else 0
        
        print(f"성공한 문제: {len(successful_results)}/{len(FERMI_PROBLEMS)}")
        print()
        print(f"평균 총점: {avg_total_score:.1f}/100")
        print(f"  - 정확도: {avg_accuracy_score:.1f}/50")
        print(f"  - Certainty: {avg_certainty_score:.1f}/20")
        print(f"  - Stage: {avg_stage_score:.1f}/20")
        print(f"  - 효율성: {avg_efficiency_score:.1f}/10")
        print()
        print(f"평균 오차율: {avg_error_pct:.1f}%")
        print(f"평균 실행 시간: {avg_time:.2f}초")
        print(f"평균 LLM Calls: {avg_llm_calls:.1f}회")
        
        # 순위
        print("\n" + "-" * 120)
        print("📊 문제별 순위:")
        print("-" * 120)
        print()
        
        sorted_results = sorted(successful_results, key=lambda x: x['evaluation']['total_score'], reverse=True)
        
        print(f"{'순위':<6} | {'문제':<40} | {'오차율':<10} | {'총점':<10} | {'시간':<10}")
        print("-" * 120)
        
        for rank, r in enumerate(sorted_results, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal}{rank:<4} | {r['problem_name']:<40} | {r['error_pct']:>7.1f}% | "
                  f"{r['evaluation']['total_score']:>7.1f}/100 | {r['elapsed_time']:>7.2f}초")
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'v7_11_0_fermi_10problems_{timestamp}.json'
    
    output_data = {
        'timestamp': timestamp,
        'test_name': 'v7.11.0 EstimatorRAG - 10 Fermi Problems',
        'architecture': 'v7.11.0 Fusion Architecture (4-Stage)',
        'features': [
            'Recursion FORBIDDEN',
            'Budget-based Exploration',
            'Evidence → Prior → Fermi → Fusion',
            'Phase 0 (Literal)',
            'Guardrail Engine'
        ],
        'problems': FERMI_PROBLEMS,
        'results': all_results,
        'summary': {
            'total_problems': len(FERMI_PROBLEMS),
            'successful': len(successful_results),
            'failed': len(FERMI_PROBLEMS) - len(successful_results),
            'avg_total_score': avg_total_score if successful_results else 0,
            'avg_accuracy_score': avg_accuracy_score if successful_results else 0,
            'avg_error_pct': avg_error_pct if successful_results else 0,
            'avg_time': avg_time if successful_results else 0,
            'avg_llm_calls': avg_llm_calls if successful_results else 0
        }
    }
    
    output_path = project_root / output_file
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("\n🎉 전체 테스트 완료!")
    
    return all_results


if __name__ == '__main__':
    run_test()
