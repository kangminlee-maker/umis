#!/usr/bin/env python3
"""
v7.11.0 재귀 폭발 테스트

이전에 재귀 폭발이 발생했던 질문들을 v7.11.0로 테스트
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator import EstimatorRAG, create_standard_budget, create_fast_budget
from umis_rag.utils.logger import logger


# 이전에 재귀 폭발이 발생했던 복잡한 질문들
RECURSIVE_EXPLOSION_QUESTIONS = [
    {
        'id': 'ltv_cac_ratio',
        'question': '한국 B2B SaaS 시장 LTV/CAC 비율은?',
        'domain': 'B2B_SaaS',
        'region': '한국',
        'expected_time': 60,  # 60초 이내
        'description': '이전 재귀 폭발 원인: LTV → ARPU, Churn → 각각 재귀 → 무한 확장'
    },
    {
        'id': 'market_size',
        'question': '한국 B2B SaaS 시장 규모는?',
        'domain': 'B2B_SaaS',
        'region': '한국',
        'expected_time': 60,
        'description': '이전 재귀 폭발 원인: 시장 → 기업수, 도입률, ARPU → 각각 재귀'
    },
    {
        'id': 'restaurant_count',
        'question': '서울 음식점 수는?',
        'region': '서울',
        'expected_time': 30,
        'description': '이전 재귀 폭발 원인: 음식점 → 인구, 밀도 → 가구수, 평균가구 → 무한 재귀'
    },
    {
        'id': 'churn_rate',
        'question': 'B2B SaaS의 월 해지율은?',
        'domain': 'B2B_SaaS',
        'expected_time': 20,
        'description': '비교적 단순 (Phase 2-3에서 해결 가능)'
    },
    {
        'id': 'arpu',
        'question': 'B2B SaaS ARPU는?',
        'domain': 'B2B_SaaS',
        'region': '한국',
        'expected_time': 20,
        'description': '비교적 단순 (Phase 2-3에서 해결 가능)'
    }
]


def test_recursive_explosion_prevention():
    """재귀 폭발 방지 테스트"""
    
    logger.info("=" * 100)
    logger.info("v7.11.0 재귀 폭발 방지 테스트")
    logger.info("=" * 100)
    logger.info("")
    
    estimator = EstimatorRAG()
    budget = create_standard_budget()  # max_llm_calls=10, max_variables=8
    
    results = []
    
    for i, test_case in enumerate(RECURSIVE_EXPLOSION_QUESTIONS, 1):
        logger.info("")
        logger.info("━" * 100)
        logger.info(f"[테스트 {i}/{len(RECURSIVE_EXPLOSION_QUESTIONS)}] {test_case['question']}")
        logger.info("━" * 100)
        logger.info(f"설명: {test_case['description']}")
        logger.info(f"예상 시간: {test_case['expected_time']}초 이내")
        logger.info("")
        
        start_time = time.time()
        
        try:
            result = estimator.estimate(
                question=test_case['question'],
                domain=test_case.get('domain'),
                region=test_case.get('region'),
                budget=budget,
                use_fermi=True
            )
            
            elapsed = time.time() - start_time
            
            # 결과 기록
            test_result = {
                'id': test_case['id'],
                'question': test_case['question'],
                'success': True,
                'value': result.value if result else None,
                'source': result.source if result else None,
                'certainty': result.certainty if result else None,
                'cost': result.cost if result else {},
                'elapsed_time': elapsed,
                'expected_time': test_case['expected_time'],
                'time_within_limit': elapsed <= test_case['expected_time'],
                'decomposition': result.decomposition if (result and result.decomposition) else None,
                'error': None
            }
            
            results.append(test_result)
            
            # 결과 출력
            logger.info("")
            logger.info("✅ 테스트 성공")
            logger.info(f"  값: {result.value:,.0f}" if result else "  값: None")
            logger.info(f"  Source: {result.source}" if result else "")
            logger.info(f"  Certainty: {result.certainty}" if result else "")
            logger.info(f"  비용: {result.get_cost_summary()}" if result else "")
            logger.info(f"  실행 시간: {elapsed:.2f}초 (예상: {test_case['expected_time']}초)")
            
            if elapsed > test_case['expected_time']:
                logger.warning(f"  ⚠️  시간 초과 (+{elapsed - test_case['expected_time']:.2f}초)")
            else:
                logger.info(f"  ✅ 시간 내 완료")
            
            if result and result.decomposition:
                logger.info(f"  분해식: {result.decomposition.get('formula', 'N/A')}")
                variables_count = len(result.decomposition.get('variables', {}))
                logger.info(f"  변수 개수: {variables_count}")
                
                # 재귀 금지 확인
                if variables_count > 8:
                    logger.warning(f"  ⚠️  변수 개수 초과 (>{budget.max_variables})")
        
        except Exception as e:
            elapsed = time.time() - start_time
            
            logger.error(f"❌ 테스트 실패: {e}")
            logger.error(f"  실행 시간: {elapsed:.2f}초")
            
            import traceback
            traceback.print_exc()
            
            test_result = {
                'id': test_case['id'],
                'question': test_case['question'],
                'success': False,
                'value': None,
                'elapsed_time': elapsed,
                'expected_time': test_case['expected_time'],
                'time_within_limit': False,
                'error': str(e)
            }
            
            results.append(test_result)
    
    # 최종 요약
    logger.info("")
    logger.info("=" * 100)
    logger.info("📊 최종 요약")
    logger.info("=" * 100)
    
    success_count = sum(1 for r in results if r['success'])
    time_ok_count = sum(1 for r in results if r['time_within_limit'])
    
    logger.info(f"총 테스트: {len(results)}개")
    logger.info(f"성공: {success_count}개")
    logger.info(f"시간 내 완료: {time_ok_count}개")
    logger.info("")
    
    # 개별 결과
    logger.info("개별 결과:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        time_status = "✅" if r['time_within_limit'] else "⚠️"
        logger.info(f"  {status} {r['question']}")
        logger.info(f"     시간: {r['elapsed_time']:.2f}초 (예상: {r['expected_time']}초) {time_status}")
        if r['success'] and r['value']:
            logger.info(f"     값: {r['value']:,.0f}, Source: {r['source']}, Certainty: {r['certainty']}")
        if r.get('cost'):
            logger.info(f"     비용: LLM {r['cost'].get('llm_calls', 0)}회, 변수 {r['cost'].get('variables', 0)}개")
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_v7_11_0_recursive_explosion_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'version': 'v7.11.0',
            'test_name': 'recursive_explosion_prevention',
            'timestamp': timestamp,
            'summary': {
                'total': len(results),
                'success': success_count,
                'time_ok': time_ok_count
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info("")
    logger.info(f"결과 저장: {output_file}")
    
    # 검증
    logger.info("")
    logger.info("=" * 100)
    logger.info("🎯 v7.11.0 검증")
    logger.info("=" * 100)
    
    if success_count == len(results):
        logger.info("✅ 모든 테스트 성공 (재귀 폭발 해결)")
    else:
        logger.warning(f"⚠️  {len(results) - success_count}개 실패")
    
    if time_ok_count == len(results):
        logger.info("✅ 모든 테스트가 예상 시간 내 완료")
    else:
        logger.warning(f"⚠️  {len(results) - time_ok_count}개 시간 초과")
    
    # 재귀 금지 확인
    max_variables = max(
        (r['cost'].get('variables', 0) for r in results if r.get('cost')),
        default=0
    )
    
    if max_variables <= budget.max_variables:
        logger.info(f"✅ 변수 개수 제한 준수 (최대 {max_variables}개 <= {budget.max_variables}개)")
    else:
        logger.warning(f"⚠️  변수 개수 초과 (최대 {max_variables}개 > {budget.max_variables}개)")
    
    logger.info("=" * 100)
    
    return results


if __name__ == "__main__":
    # 환경 변수 체크
    from umis_rag.core.config import settings
    
    if not settings.openai_api_key:
        logger.error("❌ OPENAI_API_KEY 없음")
        logger.error("   .env 파일에 OPENAI_API_KEY 설정 필요")
        sys.exit(1)
    
    logger.info(f"LLM Mode: {settings.llm_mode}")
    logger.info(f"Phase 3 Model: {settings.llm_model_phase3}")
    logger.info(f"Phase 4 Model: {settings.llm_model_phase4}")
    logger.info("")
    
    # 테스트 실행
    try:
        results = test_recursive_explosion_prevention()
        
        # 성공 여부 확인
        success_count = sum(1 for r in results if r['success'])
        
        if success_count == len(results):
            logger.info("\n🎉 v7.11.0 재귀 폭발 방지 테스트 완료!")
            sys.exit(0)
        else:
            logger.error(f"\n❌ 일부 테스트 실패 ({success_count}/{len(results)})")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
