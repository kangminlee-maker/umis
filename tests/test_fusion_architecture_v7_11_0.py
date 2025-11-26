"""
테스트: v7.11.0 Fusion Architecture

간단한 통합 테스트
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator import EstimatorRAG, create_fast_budget, create_standard_budget
from umis_rag.utils.logger import logger


def test_basic_estimation():
    """기본 추정 테스트"""
    logger.info("\n\n" + "=" * 80)
    logger.info("TEST 1: 기본 추정 (B2B SaaS Churn Rate)")
    logger.info("=" * 80)
    
    estimator = EstimatorRAG()
    
    result = estimator.estimate(
        question="B2B SaaS의 월 해지율은?",
        domain="B2B_SaaS",
        region="한국"
    )
    
    assert result is not None, "추정 실패"
    assert result.value > 0, "값이 0 이하"
    
    logger.info(f"\n✅ TEST 1 통과")
    logger.info(f"  값: {result.value:.2%}")
    logger.info(f"  Source: {result.source}")
    logger.info(f"  Certainty: {result.certainty}")


def test_fast_estimation():
    """빠른 추정 테스트"""
    logger.info("\n\n" + "=" * 80)
    logger.info("TEST 2: 빠른 추정 (10초 제한)")
    logger.info("=" * 80)
    
    estimator = EstimatorRAG()
    
    result = estimator.estimate_fast(
        question="B2B SaaS ARPU는?"
    )
    
    assert result is not None, "추정 실패"
    assert result.cost.get('time', 0) < 15, "시간 초과 (>15초)"
    
    logger.info(f"\n✅ TEST 2 통과")
    logger.info(f"  값: {result.value:,.0f}원")
    logger.info(f"  시간: {result.cost.get('time', 0):.2f}초")


def test_fermi_decomposition():
    """Fermi 분해 테스트 (재귀 금지 확인)"""
    logger.info("\n\n" + "=" * 80)
    logger.info("TEST 3: Fermi 분해 (재귀 금지)")
    logger.info("=" * 80)
    
    estimator = EstimatorRAG()
    
    result = estimator.estimate(
        question="한국 B2B SaaS 시장 규모는?",
        domain="B2B_SaaS",
        region="한국",
        use_fermi=True
    )
    
    assert result is not None, "추정 실패"
    
    # 재귀 금지 확인: 변수 개수가 Budget max_variables 이하여야 함
    if result.decomposition:
        variables_count = len(result.decomposition.get('variables', {}))
        logger.info(f"  변수 개수: {variables_count}")
        assert variables_count <= 8, f"변수 개수 초과 (>{8})"
        
        logger.info(f"  분해식: {result.decomposition.get('formula', 'N/A')}")
    
    logger.info(f"\n✅ TEST 3 통과")
    logger.info(f"  값: {result.value:,.0f}원")
    logger.info(f"  Source: {result.source}")


def test_budget_limit():
    """예산 제한 테스트"""
    logger.info("\n\n" + "=" * 80)
    logger.info("TEST 4: 예산 제한 (max_llm_calls=3)")
    logger.info("=" * 80)
    
    estimator = EstimatorRAG()
    budget = create_fast_budget()  # max_llm_calls=3
    
    result = estimator.estimate(
        question="서울 음식점 수는?",
        budget=budget,
        use_fermi=True
    )
    
    assert result is not None, "추정 실패"
    
    # LLM 호출 횟수 체크
    llm_calls = result.cost.get('llm_calls', 0)
    logger.info(f"  LLM 호출 횟수: {llm_calls}")
    assert llm_calls <= budget.max_llm_calls, f"예산 초과 (LLM calls: {llm_calls} > {budget.max_llm_calls})"
    
    logger.info(f"\n✅ TEST 4 통과")
    logger.info(f"  값: {result.value:,.0f}")
    logger.info(f"  예산 상태: {budget.get_status_summary()}")


if __name__ == "__main__":
    # 환경 변수 체크
    from umis_rag.core.config import settings
    
    if not settings.openai_api_key:
        logger.error("❌ OPENAI_API_KEY 없음")
        logger.error("   .env 파일에 OPENAI_API_KEY 설정 필요")
        sys.exit(1)
    
    logger.info(f"LLM Mode: {settings.llm_mode}")
    
    # 테스트 실행
    try:
        test_basic_estimation()
        test_fast_estimation()
        test_fermi_decomposition()
        test_budget_limit()
        
        logger.info("\n\n" + "=" * 80)
        logger.info("🎉 모든 테스트 통과!")
        logger.info("=" * 80)
    
    except AssertionError as e:
        logger.error(f"\n\n❌ 테스트 실패: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
