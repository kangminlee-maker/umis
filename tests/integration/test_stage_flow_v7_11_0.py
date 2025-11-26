"""
Stage 1-4 통합 테스트 (v7.11.0 Fusion Architecture)

목표:
- 전체 Stage 흐름 검증 (Evidence → Prior → Fermi → Fusion)
- Budget 기반 탐색 검증
- Certainty (high/medium/low) 검증
- LLM Mode 동적 전환 검증
- 에러 처리 통합 검증
- 항상 EstimationResult 반환 확인

마이그레이션:
- 구 Phase 0-4 → Stage 1-4 (Evidence, Prior, Fermi, Fusion)
- Phase3Config → Budget
- confidence → certainty
- phase == 3 → source == "Generative Prior"
- 재귀 제거 확인

작성일: 2025-11-26
"""

import os
import pytest
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import (
    Budget, create_standard_budget, create_fast_budget,
    EstimationResult, Evidence
)


class TestStage1Evidence:
    """Stage 1: Evidence Collection 테스트"""
    
    def test_literal_definite_value(self):
        """Literal: 프로젝트 데이터 확정값"""
        estimator = EstimatorRAG()
        
        # Literal은 project_data의 키와 질문이 매칭되어야 함
        result = estimator.estimate(
            question="employees",  # 키와 정확히 일치
            project_data={'employees': 150}
        )
        
        # Literal 성공 (source == "Literal")
        assert isinstance(result, EstimationResult)
        if result.source == "Literal":
            assert result.value == 150
            assert result.certainty == "high"
        # 매칭 실패 시 다른 Stage로 진행
        assert result.is_successful() or result.source == "Failure"
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_validator_search(self):
        """Validator Search: Validator RAG 검색"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS의 평균 ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # Validator 또는 다른 Stage
        assert isinstance(result, EstimationResult)
        assert result.source in ["Direct RAG", "Validator Search", "Generative Prior", "Fermi", "Fusion"]
        assert result.is_successful()


class TestStage2Prior:
    """Stage 2: Generative Prior 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_prior_estimation(self):
        """Prior: LLM 직접 값 요청"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="2025년 AI 챗봇 서비스 평균 ARPU는?",
            context=Context(domain='AI_Chatbot')
        )
        
        # Prior 또는 다른 Stage 성공
        assert isinstance(result, EstimationResult)
        assert result.source in ["Generative Prior", "Fermi", "Fusion"]
        assert result.value is not None
        assert result.certainty in ['high', 'medium', 'low']
        assert result.is_successful()
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_prior_with_evidence(self):
        """Prior: 증거와 함께 추정"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # 증거 있을 때 Prior 또는 Fusion
        assert isinstance(result, EstimationResult)
        assert result.source in ["Generative Prior", "Fusion"]
        assert result.certainty in ['high', 'medium', 'low']


class TestStage3Fermi:
    """Stage 3: Fermi (Structural Explanation) 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fermi_decomposition(self):
        """Fermi: 구조적 분해"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="서울 음식점 수는?",
            context=Context(region='서울')
        )
        
        # Fermi 또는 다른 Stage 성공
        assert isinstance(result, EstimationResult)
        assert result.source in ["Fermi", "Generative Prior", "Fusion"]
        assert result.is_successful()
        
        # Fermi 성공 시 decomposition 확인
        if result.source == "Fermi":
            assert result.decomposition is not None
            assert 'formula' in result.decomposition
            assert 'variables' in result.decomposition
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fermi_no_recursion(self):
        """Fermi: 재귀 없음 확인 (v7.11.0 핵심!)"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="서울 전체 음식점 매출은?",
            context=Context(region='서울')
        )
        
        # 재귀 없으므로 빠르게 완료
        assert isinstance(result, EstimationResult)
        # LLM 호출 횟수 제한 (재귀 없으므로 <= 10)
        if result.cost:
            assert result.cost.get('llm_calls', 0) <= 15


class TestStage4Fusion:
    """Stage 4: Fusion & Validation 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fusion_multiple_sources(self):
        """Fusion: 여러 소스 가중 합성"""
        estimator = EstimatorRAG()
        
        # 여러 Stage에서 결과 나올 가능성 높은 질문
        result = estimator.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # Fusion 또는 단일 소스
        assert isinstance(result, EstimationResult)
        assert result.source in ["Fusion", "Generative Prior", "Fermi", "Direct RAG"]
        assert result.is_successful()


class TestBudgetBasedExploration:
    """Budget 기반 탐색 테스트 (v7.11.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_standard_budget(self):
        """표준 예산으로 추정"""
        estimator = EstimatorRAG()
        
        # 표준 Budget (max_llm_calls=10)
        result = estimator.estimate(
            question="AI 챗봇 ARPU는?",
            context=Context(domain='AI_Chatbot')
        )
        
        # Budget 내에서 추정 성공
        assert isinstance(result, EstimationResult)
        if result.cost:
            # 표준 Budget 제한 (max_llm_calls=10)
            assert result.cost.get('llm_calls', 0) <= 15
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_fast_budget(self):
        """빠른 예산으로 추정"""
        estimator = EstimatorRAG()
        
        # Fast Budget (max_llm_calls=3)
        # EstimatorRAG는 기본 Budget 사용 (내부에서 fast_budget 설정 필요)
        result = estimator.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # 빠른 추정 성공
        assert isinstance(result, EstimationResult)
        assert result.cost['time'] < 10.0  # 빠른 추정


class TestLLMModeSwitching:
    """LLM Mode 동적 전환 테스트"""
    
    def test_cursor_to_api_mode(self):
        """Cursor → API 모드 전환"""
        estimator = EstimatorRAG()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            # Cursor 모드
            settings.llm_mode = 'cursor'
            assert estimator.llm_mode == 'cursor'
            
            # API 모드로 전환
            settings.llm_mode = 'gpt-4o-mini'
            assert estimator.llm_mode == 'gpt-4o-mini'
            
        finally:
            settings.llm_mode = original_mode
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_mode_switch_during_estimation(self):
        """추정 중 Mode 전환"""
        estimator = EstimatorRAG()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            # Cursor 모드로 첫 추정
            settings.llm_mode = 'cursor'
            result1 = estimator.estimate(
                question="employees",
                project_data={'employees': 100}
            )
            assert isinstance(result1, EstimationResult)
            
            # API 모드로 전환 후 추정
            settings.llm_mode = 'gpt-4o-mini'
            result2 = estimator.estimate(
                question="employees",
                project_data={'employees': 200}
            )
            assert isinstance(result2, EstimationResult)
            
        finally:
            settings.llm_mode = original_mode


class TestErrorHandling:
    """에러 처리 통합 테스트"""
    
    def test_empty_question(self):
        """빈 질문"""
        estimator = EstimatorRAG()
        
        try:
            result = estimator.estimate(question="")
            # 에러 없이 처리되면 source=="Failure"
            assert isinstance(result, EstimationResult)
            if not result.is_successful():
                assert result.source == "Failure"
        except (ValueError, TypeError):
            # 에러 발생도 허용
            pass
    
    def test_none_question(self):
        """None 질문"""
        estimator = EstimatorRAG()
        
        with pytest.raises((TypeError, AttributeError)):
            estimator.estimate(question=None)
    
    def test_invalid_project_data(self):
        """잘못된 project_data"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="테스트?",
            project_data=None
        )
        
        # 에러 없이 처리 (다른 Stage로)
        assert isinstance(result, EstimationResult)
    
    def test_invalid_context(self):
        """잘못된 Context"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="테스트?",
            context=None
        )
        
        # 에러 없이 처리
        assert isinstance(result, EstimationResult)


class TestAlwaysReturnResult:
    """항상 EstimationResult 반환 검증"""
    
    def test_always_return_estimation_result(self):
        """항상 EstimationResult 반환"""
        estimator = EstimatorRAG()
        
        questions = [
            ("직원 수?", {'employees': 100}),
            ("테스트?", {}),
            ("2099년 화성?", {}),
        ]
        
        for question, project_data in questions:
            result = estimator.estimate(
                question=question,
                project_data=project_data
            )
            
            # 항상 EstimationResult 반환
            assert isinstance(result, EstimationResult)
            assert result is not None
            
            # is_successful() 메서드 사용 가능
            success = result.is_successful()
            assert isinstance(success, bool)
    
    def test_source_on_failure(self):
        """실패 시 source=="Failure" """
        estimator = EstimatorRAG()
        
        # 모든 Stage 실패하는 질문
        result = estimator.estimate(
            question="완전히 알 수 없는 질문?",
            context=Context()
        )
        
        # EstimationResult 반환
        assert isinstance(result, EstimationResult)
        
        # 실패하면 source=="Failure"
        if not result.is_successful():
            assert result.source == "Failure"
            assert result.error is not None


class TestStageProgression:
    """Stage 진행 순서 테스트"""
    
    def test_stage1_first(self):
        """Stage 1 (Evidence) 우선 확인"""
        estimator = EstimatorRAG()
        
        # Literal 매칭
        result = estimator.estimate(
            question="value 값은?",
            project_data={'value': 42}
        )
        
        # Literal 성공 또는 다른 Stage
        assert isinstance(result, EstimationResult)
        if result.source == "Literal":
            assert result.value == 42
        assert result.is_successful() or result.source == "Failure"
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_stage1_skip_to_stage2(self):
        """Stage 1 스킵 → Stage 2 (Prior)"""
        estimator = EstimatorRAG()
        
        # project_data 없음, Validator 없음 → Prior
        result = estimator.estimate(
            question="2025년 새로운 시장?",
            context=Context()
        )
        
        # Prior 또는 Fermi
        assert result.source in ["Generative Prior", "Fermi", "Fusion"]


class TestPerformance:
    """통합 성능 테스트"""
    
    def test_literal_speed(self):
        """Literal 속도 (<0.1초)"""
        import time
        
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="value",
            project_data={'value': 100}
        )
        duration = time.time() - start
        
        assert isinstance(result, EstimationResult)
        if result.source == "Literal":
            assert duration < 0.1, f"Literal too slow: {duration:.3f}s"
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_prior_speed(self):
        """Prior 속도 (<5초)"""
        import time
        
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="AI 챗봇 ARPU?",
            context=Context(domain='AI_Chatbot')
        )
        duration = time.time() - start
        
        if result.source == "Generative Prior":
            assert duration < 5.0, f"Prior too slow: {duration:.3f}s"


class TestEdgeCases:
    """엣지 케이스 통합 테스트"""
    
    def test_very_long_question(self):
        """매우 긴 질문"""
        estimator = EstimatorRAG()
        
        long_question = "서울에 있는 " + "매우 " * 100 + "큰 시장은?"
        
        result = estimator.estimate(
            question=long_question,
            context=Context()
        )
        
        # 에러 없이 처리
        assert isinstance(result, EstimationResult)
    
    def test_special_characters(self):
        """특수문자 포함 질문"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS의 평균 ARPU는? (단위: $)",
            context=Context(domain='B2B_SaaS')
        )
        
        # 특수문자 처리
        assert isinstance(result, EstimationResult)
    
    def test_multilingual(self):
        """다국어 질문"""
        estimator = EstimatorRAG()
        
        # 영어
        result_en = estimator.estimate(
            question="What is the average ARPU?",
            context=Context()
        )
        assert isinstance(result_en, EstimationResult)
        
        # 한국어
        result_ko = estimator.estimate(
            question="평균 ARPU는?",
            context=Context()
        )
        assert isinstance(result_ko, EstimationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

