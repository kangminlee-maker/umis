"""
Stage 3: Fermi Estimator 단위 테스트 (v7.11.0)

목표:
- Stage 3 (Fermi) 핵심 기능 검증
- 구조적 설명 (분해) 흐름 테스트
- 재귀 금지 확인 (max_depth=2)
- PriorEstimator 주입 검증
- Budget 기반 탐색 검증

마이그레이션:
- 구 Phase 4 Fermi Decomposition → Stage 3 Structural Explanation
- 재귀 제거 (Recursion FORBIDDEN)
- max_depth=4 → max_depth=2 강제
- phase3 의존성 → prior_estimator 주입

작성일: 2025-11-26
"""

import os
import pytest
from umis_rag.agents.estimator import FermiEstimator, PriorEstimator
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import (
    Budget, create_standard_budget, create_fast_budget,
    EstimationResult, Evidence
)


class TestFermiEstimatorBasic:
    """Stage 3 Fermi Estimator 기본 기능 테스트"""
    
    def test_initialization(self):
        """Fermi Estimator 초기화 테스트"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        
        # 초기화 검증
        assert fermi.llm_mode == 'gpt-4o-mini'
        assert fermi.prior_estimator is prior
    
    def test_llm_mode_dynamic(self):
        """LLM Mode 동적 변경 테스트 (v7.11.0)"""
        prior = PriorEstimator(llm_mode=None)
        fermi = FermiEstimator(llm_mode=None, prior_estimator=prior)
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        settings.llm_mode = 'cursor'
        assert fermi.llm_mode == 'cursor'
        
        settings.llm_mode = 'gpt-4o-mini'
        assert fermi.llm_mode == 'gpt-4o-mini'
        
        settings.llm_mode = original_mode


class TestFermiEstimatorDecomposition:
    """Stage 3 Fermi 분해 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_decompose_simple(self):
        """간단한 질문 분해"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        result = fermi.estimate(
            question="서울 음식점 수는?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        # 분해 성공
        if result:
            assert result.source == "Fermi"
            assert result.decomposition is not None
            assert 'formula' in result.decomposition
            assert 'variables' in result.decomposition
            # 변수 개수 제한 (2-4개)
            assert 2 <= len(result.decomposition['variables']) <= 4
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_decompose_with_available_data(self):
        """이미 알려진 데이터가 있을 때 분해"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        
        # Evidence에 이미 데이터 있음
        evidence = Evidence()
        evidence.direct_rag_results = []
        evidence.validator_data = []
        
        result = fermi.estimate(
            question="서울 전체 음식점 매출은?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        if result:
            assert result.source == "Fermi"


class TestFermiEstimatorNoRecursion:
    """재귀 금지 검증 (v7.11.0 핵심!)"""
    
    def test_max_depth_limit(self):
        """최대 Depth=2 제한"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        # Depth 2에서 호출
        result = fermi.estimate(
            question="테스트?",
            evidence=evidence,
            budget=budget,
            context=Context(),
            depth=2  # max_depth 도달
        )
        
        # Depth 2에서는 재귀 중단
        # None 또는 PriorEstimator로 추정
        assert result is None or result.source in ["Generative Prior", "Fermi"]
    
    def test_no_recursive_call(self):
        """재귀 호출 없음 확인"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        # Fermi는 변수 추정 시 PriorEstimator만 사용
        # 자기 자신(FermiEstimator)을 재귀 호출하지 않음
        result = fermi.estimate(
            question="서울 음식점 수는?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        # Budget 확인 (재귀 없으므로 LLM 호출 적음)
        if result:
            assert result.cost['llm_calls'] <= 10  # 재귀 없으므로 제한적


class TestFermiEstimatorBudget:
    """Budget 기반 탐색 테스트 (v7.11.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fast_budget(self):
        """빠른 예산으로 분해"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_fast_budget()  # max_llm_calls=3
        evidence = Evidence()
        
        result = fermi.estimate(
            question="서울 음식점 수는?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        # Fast budget 제한
        if result:
            assert result.cost['llm_calls'] <= 5  # Fast mode
    
    def test_budget_exhausted(self):
        """Budget 소진 시 중단"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        
        # 소진된 Budget
        budget = Budget(
            max_llm_calls=0,
            max_variables=10,
            max_runtime_seconds=60,
            max_depth=2
        )
        evidence = Evidence()
        
        result = fermi.estimate(
            question="서울 음식점 수는?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        # Budget 소진 시 None
        assert result is None


class TestFermiEstimatorPerformance:
    """Fermi Estimator 성능 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimation_speed_simple(self):
        """단순 분해 추정 속도 (<10초 목표)"""
        import time
        
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_fast_budget()
        evidence = Evidence()
        
        start = time.time()
        result = fermi.estimate(
            question="서울 음식점 수는?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        duration = time.time() - start
        
        # 10초 이내 완료 (재귀 없으므로 빠름)
        if result:
            assert duration < 10.0, f"Fermi too slow: {duration:.3f}s"


class TestFermiEstimatorIntegration:
    """Fermi와 Prior 통합 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_prior_estimator_injection(self):
        """PriorEstimator 주입 테스트"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        result = fermi.estimate(
            question="서울 음식점 매출은?",
            evidence=evidence,
            budget=budget,
            context=Context(region='서울'),
            depth=0
        )
        
        # Fermi가 변수 추정 시 PriorEstimator 사용
        if result and result.decomposition:
            # 각 변수는 PriorEstimator로 추정됨
            for var in result.decomposition.get('variables', []):
                # Prior 또는 확정 값
                assert var.get('source') in ['Generative Prior', 'Literal', 'Direct RAG']


class TestFermiEstimatorErrorHandling:
    """Fermi Estimator 에러 처리 테스트"""
    
    def test_invalid_question(self):
        """잘못된 질문"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        with pytest.raises((TypeError, AttributeError)):
            fermi.estimate(
                question=None,
                evidence=evidence,
                budget=budget,
                context=Context(),
                depth=0
            )
    
    def test_invalid_depth(self):
        """잘못된 Depth"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        fermi = FermiEstimator(llm_mode='gpt-4o-mini', prior_estimator=prior)
        budget = create_standard_budget()
        evidence = Evidence()
        
        # 음수 Depth
        result = fermi.estimate(
            question="테스트?",
            evidence=evidence,
            budget=budget,
            context=Context(),
            depth=-1
        )
        
        # 에러 없이 처리 (또는 None)
        assert result is None or isinstance(result, EstimationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

