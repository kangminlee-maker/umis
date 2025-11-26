"""
Stage 2: Generative Prior 단위 테스트 (v7.11.0)

목표:
- Stage 2 (Generative Prior) 핵심 기능 검증
- LLM 직접 값 요청 흐름 테스트
- Certainty (high/medium/low) 검증
- Budget 기반 탐색 검증

마이그레이션:
- 구 Phase 3 Guestimation → Stage 2 Generative Prior
- Phase3Config → Budget
- confidence → certainty
- phase == 3 → source == "Generative Prior"

작성일: 2025-11-26
"""

import os
import pytest
from umis_rag.agents.estimator import PriorEstimator
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import (
    Budget, create_standard_budget, create_fast_budget,
    EstimationResult, Evidence
)


class TestPriorEstimatorBasic:
    """Stage 2 Prior Estimator 기본 기능 테스트"""
    
    def test_initialization(self):
        """Prior Estimator 초기화 테스트"""
        # Default
        prior = PriorEstimator(llm_mode=None)
        assert prior.llm_mode is not None
        
        # 명시적 모드 지정
        prior_gpt = PriorEstimator(llm_mode='gpt-4o-mini')
        assert prior_gpt.llm_mode == 'gpt-4o-mini'
    
    def test_llm_mode_dynamic(self):
        """LLM Mode 동적 변경 테스트 (v7.11.0)"""
        prior = PriorEstimator(llm_mode=None)
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        settings.llm_mode = 'cursor'
        assert prior.llm_mode == 'cursor'
        
        settings.llm_mode = 'gpt-4o-mini'
        assert prior.llm_mode == 'gpt-4o-mini'
        
        settings.llm_mode = original_mode


class TestPriorEstimatorWithEvidence:
    """증거가 있을 때 Prior Estimator 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimate_with_context(self):
        """Context가 있을 때 추정 성공"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        evidence = Evidence()
        
        result = prior.estimate(
            question="2025년 AI 챗봇 서비스 평균 ARPU는?",
            evidence=evidence,
            budget=budget,
            context=Context(domain='AI_Chatbot')
        )
        
        # Stage 2 성공 검증
        assert result is not None
        assert isinstance(result, EstimationResult)
        assert result.source == "Generative Prior"
        assert result.value is not None
        assert result.certainty in ['high', 'medium', 'low']
        assert result.cost['time'] > 0
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimate_different_domains(self):
        """다양한 Domain에서 추정"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        
        domains = ['B2B_SaaS', 'E_Commerce', 'Food_Service']
        
        for domain in domains:
            evidence = Evidence()
            result = prior.estimate(
                question=f"{domain} 평균 ARPU는?",
                evidence=evidence,
                budget=budget,
                context=Context(domain=domain)
            )
            
            # 각 도메인에서 결과 반환
            if result:
                assert result.source == "Generative Prior"
                assert hasattr(result, 'certainty')


class TestPriorEstimatorWithoutEvidence:
    """증거가 없을 때 Prior Estimator 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimate_without_evidence(self):
        """증거 없을 때도 LLM이 추정 시도"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        evidence = Evidence()  # 빈 증거
        
        result = prior.estimate(
            question="2099년 화성 피자 배달 시장 규모는?",
            evidence=evidence,
            budget=budget,
            context=Context()
        )
        
        # LLM이 있으면 항상 시도
        if result:
            assert result.source == "Generative Prior"
            # Certainty가 낮을 가능성
            assert result.certainty in ['high', 'medium', 'low']
    
    def test_estimate_empty_context(self):
        """빈 Context로 추정"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        evidence = Evidence()
        
        result = prior.estimate(
            question="평균 ARPU는?",
            evidence=evidence,
            budget=budget,
            context=Context()  # domain 없음
        )
        
        # Context 없으면 certainty 낮을 수 있음
        if result:
            assert result.certainty in ['high', 'medium', 'low']


class TestPriorEstimatorBudget:
    """Budget 기반 탐색 테스트 (v7.11.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fast_budget(self):
        """빠른 예산으로 추정"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_fast_budget()  # max_llm_calls=3
        evidence = Evidence()
        
        result = prior.estimate(
            question="B2B SaaS ARPU는?",
            evidence=evidence,
            budget=budget,
            context=Context(domain='B2B_SaaS')
        )
        
        # 빠른 예산으로도 추정 성공
        if result:
            assert result.cost['llm_calls'] <= 3  # Fast budget 제한
    
    def test_budget_exhausted(self):
        """Budget 소진 시 처리"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        
        # 소진된 Budget
        budget = Budget(
            max_llm_calls=0,  # 이미 소진
            max_variables=10,
            max_runtime_seconds=60,
            max_depth=2
        )
        evidence = Evidence()
        
        result = prior.estimate(
            question="테스트?",
            evidence=evidence,
            budget=budget,
            context=Context()
        )
        
        # Budget 소진 시 None 반환
        assert result is None


class TestPriorEstimatorPerformance:
    """Prior Estimator 성능 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimation_speed(self):
        """추정 속도 테스트 (<5초 목표)"""
        import time
        
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_fast_budget()
        evidence = Evidence()
        
        start = time.time()
        result = prior.estimate(
            question="B2B SaaS ARPU는?",
            evidence=evidence,
            budget=budget,
            context=Context(domain='B2B_SaaS')
        )
        duration = time.time() - start
        
        # 5초 이내 완료
        assert duration < 5.0, f"Prior too slow: {duration:.3f}s"
        
        if result:
            # 실제 시간과 유사해야 함
            assert abs(result.cost['time'] - duration) < 0.5


class TestPriorEstimatorErrorHandling:
    """Prior Estimator 에러 처리 테스트"""
    
    def test_invalid_question_type(self):
        """잘못된 질문 타입"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        evidence = Evidence()
        
        # None 질문은 에러
        with pytest.raises((TypeError, AttributeError)):
            prior.estimate(
                question=None,
                evidence=evidence,
                budget=budget,
                context=Context()
            )
    
    def test_invalid_budget_type(self):
        """잘못된 Budget 타입"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        evidence = Evidence()
        
        # Budget이 None이면 처리 필요
        # (실제 구현에서는 None 체크)
        with pytest.raises((TypeError, AttributeError)):
            prior.estimate(
                question="테스트?",
                evidence=evidence,
                budget=None,  # None
                context=Context()
            )


class TestPriorEstimatorCertainty:
    """Certainty (high/medium/low) 테스트 (v7.11.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_certainty_values(self):
        """Certainty 값 검증"""
        prior = PriorEstimator(llm_mode='gpt-4o-mini')
        budget = create_standard_budget()
        evidence = Evidence()
        
        result = prior.estimate(
            question="B2B SaaS ARPU는?",
            evidence=evidence,
            budget=budget,
            context=Context(domain='B2B_SaaS')
        )
        
        if result:
            # Certainty는 high/medium/low만 가능
            assert result.certainty in ['high', 'medium', 'low']
            # source는 "Generative Prior"
            assert result.source == "Generative Prior"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

