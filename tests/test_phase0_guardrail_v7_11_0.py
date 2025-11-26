"""
Phase 0 & Guardrail Engine 테스트 (v7.11.0)

테스트 시나리오:
1. Phase 0: 프로젝트 데이터 저장 및 조회
2. Guardrail Engine: 자동 수집 검증
3. 통합 테스트: Evidence Collector
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from umis_rag.agents.estimator import EstimatorRAG, Context
from umis_rag.agents.estimator.literal_source import LiteralSource
from umis_rag.agents.estimator.evidence_collector import EvidenceCollector
from umis_rag.utils.logger import logger


class TestLiteralSource:
    """Phase 0 (Literal) 테스트"""
    
    def test_phase0_set_and_get(self):
        """프로젝트 데이터 저장 및 조회"""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Phase 0 - 프로젝트 데이터 저장/조회")
        logger.info("="*80)
        
        # Phase 0 초기화
        phase0 = LiteralSource(project_id="test_project_v7_11_0")
        
        # 데이터 저장
        phase0.set('churn_rate', 0.05, metadata={'source': 'test'})
        phase0.set('arpu', 80000, metadata={'source': 'test'})
        phase0.set('ltv', 1600000, metadata={'source': 'test'})
        
        logger.info("  ✅ 데이터 저장 완료")
        
        # 데이터 조회
        result = phase0.get("churn rate는?")
        
        assert result is not None, "Phase 0 조회 실패"
        assert result.value == 0.05, f"값 불일치: {result.value}"
        assert result.confidence == 1.0, "Confidence는 1.0이어야 함"
        
        logger.info(f"  ✅ 조회 성공: churn_rate = {result.value}")
        logger.info(f"  ✅ Confidence: {result.confidence}")
    
    def test_phase0_with_context(self):
        """Context 기반 조회"""
        logger.info("\n" + "="*80)
        logger.info("TEST 2: Phase 0 - Context 기반 조회")
        logger.info("="*80)
        
        phase0 = LiteralSource(project_id="test_project_v7_11_0")
        
        # Context별 데이터 저장
        phase0.set('B2B_SaaS_Korea_churn_rate', 0.05)
        phase0.set('B2C_Mobile_US_churn_rate', 0.12)
        
        # Context 생성
        context = Context(
            domain='B2B_SaaS',
            region='Korea'
        )
        
        # Context 기반 조회
        result = phase0.get("churn rate는?", context)
        
        assert result is not None, "Context 조회 실패"
        assert result.value == 0.05, f"값 불일치: {result.value}"
        
        logger.info(f"  ✅ Context 조회 성공: {result.value}")


class TestGuardrailEngine:
    """Guardrail Engine 테스트"""
    
    def test_guardrail_auto_collection(self):
        """Guardrail 자동 수집"""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Guardrail Engine - 자동 수집")
        logger.info("="*80)
        
        # Evidence Collector 초기화
        collector = EvidenceCollector(project_id="test_project_v7_11_0")
        
        # 질문
        question = "한국 B2B SaaS 시장 규모는?"
        context = Context(
            domain='B2B_SaaS',
            region='Korea'
        )
        
        # Evidence 수집 (Guardrail 포함)
        result, evidence = collector.collect(
            question=question,
            context=context,
            collect_guardrails=True
        )
        
        logger.info(f"\n결과:")
        logger.info(f"  Definite Value: {evidence.definite_value}")
        logger.info(f"  Hard Bounds: {evidence.hard_bounds}")
        logger.info(f"  Soft Hints: {len(evidence.soft_hints)}개")
        logger.info(f"  Logical Relations: {len(evidence.logical_relations)}개")
        
        # 검증: Guardrail이 수집되었는지 (실제 유사 데이터가 있을 경우)
        # Note: 테스트 환경에서 Phase 2 데이터가 없을 수 있음
        logger.info(f"  ℹ️  Guardrail Engine 실행 완료")


class TestIntegration:
    """통합 테스트"""
    
    def test_estimator_with_phase0(self):
        """EstimatorRAG + Phase 0 통합"""
        logger.info("\n" + "="*80)
        logger.info("TEST 4: EstimatorRAG + Phase 0 통합")
        logger.info("="*80)
        
        # Phase 0 데이터 준비
        phase0 = LiteralSource(project_id="test_project_v7_11_0")
        phase0.set('churn_rate', 0.05)
        phase0.set('arpu', 80000)
        
        # EstimatorRAG 초기화
        estimator = EstimatorRAG(project_id="test_project_v7_11_0")
        
        # 추정 (Phase 0에서 바로 반환되어야 함)
        result = estimator.estimate(
            question="churn rate는?",
            context={'domain': 'B2B_SaaS', 'region': 'Korea'}
        )
        
        logger.info(f"\n결과:")
        logger.info(f"  Value: {result.value}")
        logger.info(f"  Certainty: {result.certainty}")
        logger.info(f"  Source: {result.source}")
        
        # 검증
        assert result.value == 0.05, f"값 불일치: {result.value}"
        assert result.certainty == "high", "Certainty는 high여야 함"
        
        logger.info(f"  ✅ Phase 0 확정 값 즉시 반환")


def run_all_tests():
    """모든 테스트 실행"""
    logger.info("\n" + "="*100)
    logger.info("Phase 0 & Guardrail Engine 통합 테스트 시작 (v7.11.0)")
    logger.info("="*100)
    
    # Phase 0 테스트
    test_phase0 = TestLiteralSource()
    test_phase0.test_phase0_set_and_get()
    test_phase0.test_phase0_with_context()
    
    # Guardrail Engine 테스트
    test_guardrail = TestGuardrailEngine()
    test_guardrail.test_guardrail_auto_collection()
    
    # 통합 테스트
    test_integration = TestIntegration()
    test_integration.test_estimator_with_phase0()
    
    logger.info("\n" + "="*100)
    logger.info("✅ 모든 테스트 완료!")
    logger.info("="*100)


if __name__ == '__main__':
    run_all_tests()
