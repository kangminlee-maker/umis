#!/usr/bin/env python3
"""
Evidence Collector 테스트

Phase 1, 2의 올바른 통합 확인
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator import EstimatorRAG, create_fast_budget
from umis_rag.utils.logger import logger


def test_evidence_collector():
    """Evidence Collector 테스트"""
    
    logger.info("=" * 80)
    logger.info("Evidence Collector 테스트")
    logger.info("=" * 80)
    
    estimator = EstimatorRAG()
    
    # 테스트 1: 단순 질문 (Phase 1 또는 Phase 2에서 처리)
    logger.info("\n[테스트 1] B2B SaaS Churn Rate")
    result1 = estimator.estimate(
        question="B2B SaaS의 월 해지율은?",
        domain="B2B_SaaS",
        budget=create_fast_budget()
    )
    
    if result1:
        logger.info(f"✅ 결과: {result1.value}")
        logger.info(f"  Source: {result1.source}")
        logger.info(f"  Certainty: {result1.certainty}")
        logger.info(f"  비용: {result1.get_cost_summary()}")
    
    # 테스트 2: 복잡한 질문 (Fermi가 필요할 수 있음)
    logger.info("\n[테스트 2] 한국 B2B SaaS 시장 규모")
    result2 = estimator.estimate(
        question="한국 B2B SaaS 시장 규모는?",
        domain="B2B_SaaS",
        region="한국",
        budget=create_fast_budget(),
        use_fermi=True
    )
    
    if result2:
        logger.info(f"✅ 결과: {result2.value:,.0f}")
        logger.info(f"  Source: {result2.source}")
        logger.info(f"  Certainty: {result2.certainty}")
        logger.info(f"  비용: {result2.get_cost_summary()}")
        
        if result2.decomposition:
            logger.info(f"  분해식: {result2.decomposition.get('formula', 'N/A')}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Evidence Collector 테스트 완료")
    logger.info("=" * 80)


if __name__ == "__main__":
    from umis_rag.core.config import settings
    
    if not settings.openai_api_key:
        logger.error("❌ OPENAI_API_KEY 없음")
        sys.exit(1)
    
    logger.info(f"LLM Mode: {settings.llm_mode}")
    logger.info("")
    
    try:
        test_evidence_collector()
        logger.info("\n🎉 테스트 성공!")
    except Exception as e:
        logger.error(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
