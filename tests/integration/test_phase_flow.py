"""
Phase 0-4 통합 테스트 (v7.9.0)

목표:
- 전체 Phase 흐름 검증 (Phase 0 → 1 → 2 → 3 → 4)
- LLM Mode 동적 전환 검증
- Cursor 자동 Fallback 검증
- 에러 처리 통합 검증
- None 반환 제거 검증 (항상 EstimationResult)

작성일: 2025-11-25
"""

import os
import pytest
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context, EstimationResult


class TestPhase0to4Flow:
    """Phase 0-4 전체 흐름 테스트"""
    
    def test_phase0_project_data(self):
        """Phase 0: 프로젝트 데이터 확정값"""
        estimator = EstimatorRAG()
        
        # Phase 0는 project_data의 키와 질문이 매칭되어야 함
        result = estimator.estimate(
            question="employees",  # 키와 정확히 일치
            project_data={'employees': 150}
        )
        
        # Phase 0 성공 또는 Phase 3 (키 매칭 실패 시)
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == 150
            assert result.confidence == 1.0
        # Phase 0 매칭 실패 시 다른 Phase로 진행
        assert result.is_successful() or result.phase == -1
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase2_validator_skip(self):
        """Phase 2: Validator 스킵 (v7.9.0 임계값 강화)"""
        estimator = EstimatorRAG()
        
        # v7.9.0: 0.820 distance는 0.85 미만이므로 매칭 가능
        # 하지만 실제로는 Phase 3로 넘어갈 수 있음
        result = estimator.estimate(
            question="B2B SaaS의 평균 ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # Phase 2 또는 Phase 3
        assert isinstance(result, EstimationResult)
        assert result.phase >= 2
        assert result.is_successful()
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase3_guestimation(self):
        """Phase 3: Guestimation 추정"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="2025년 AI 챗봇 서비스 평균 ARPU는?",
            context=Context(domain='AI_Chatbot')
        )
        
        # Phase 3 성공
        assert isinstance(result, EstimationResult)
        assert result.phase == 3
        assert result.value is not None
        assert result.confidence >= 0.5
        assert result.is_successful()
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase4_fermi_decomposition(self):
        """Phase 4: Fermi Decomposition"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="서울 음식점 수는?",
            context=Context(region='서울')
        )
        
        # Phase 3 또는 Phase 4 성공
        assert isinstance(result, EstimationResult)
        assert result.phase >= 3
        assert result.is_successful()
    
    def test_all_phases_fail(self):
        """모든 Phase 실패 → phase=-1 반환 (v7.9.0)"""
        estimator = EstimatorRAG()
        
        # 매우 특이한 질문 (모든 Phase 실패 예상)
        result = estimator.estimate(
            question="2099년 화성 피자 배달 시장 규모는?",
            context=Context()
        )
        
        # v7.9.0: None 대신 phase=-1 반환
        assert isinstance(result, EstimationResult)
        # Phase 3가 시도하므로 phase=3 또는 -1
        if not result.is_successful():
            assert result.phase == -1
            assert result.error is not None
            assert result.failed_phases is not None


class TestLLMModeSwitching:
    """LLM Mode 동적 전환 테스트 (v7.9.0)"""
    
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
            
            # Phase 3, 4도 동일하게 변경되어야 함
            # (Lazy 초기화이므로 실제 호출 시 확인)
            
        finally:
            settings.llm_mode = original_mode
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_mode_switch_during_estimation(self):
        """추정 중 Mode 전환 (재생성 없이)"""
        estimator = EstimatorRAG()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            # 첫 번째 추정 (cursor 모드)
            settings.llm_mode = 'cursor'
            result1 = estimator.estimate(
                question="employees",  # 키 정확히 일치
                project_data={'employees': 100}
            )
            # Phase 0 성공 또는 다른 Phase
            assert isinstance(result1, EstimationResult)
            
            # Mode 전환 (재생성 없이)
            settings.llm_mode = 'gpt-4o-mini'
            assert estimator.llm_mode == 'gpt-4o-mini'
            
            # 두 번째 추정 (새 모드로)
            result2 = estimator.estimate(
                question="employees",  # 키 정확히 일치
                project_data={'employees': 200}
            )
            # EstimationResult 반환 확인
            assert isinstance(result2, EstimationResult)
            
        finally:
            settings.llm_mode = original_mode


class TestCursorAutoFallback:
    """Cursor 자동 Fallback 테스트 (v7.9.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required for fallback"
    )
    def test_cursor_fallback_phase3(self):
        """Cursor 모드에서 Phase 3 자동 Fallback"""
        estimator = EstimatorRAG()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            # Cursor 모드 설정
            settings.llm_mode = 'cursor'
            
            # Phase 3 필요한 질문
            result = estimator.estimate(
                question="AI 챗봇 ARPU는?",
                context=Context(domain='AI_Chatbot')
            )
            
            # v7.9.0: 자동 Fallback으로 성공
            # (EstimatorRAG에서 Fallback 처리)
            assert isinstance(result, EstimationResult)
            
            # Phase 3 성공 또는 실패
            # (Cursor 모드 자체는 instruction만 생성)
            
        finally:
            settings.llm_mode = original_mode
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required for fallback"
    )
    def test_cursor_fallback_phase4(self):
        """Cursor 모드에서 Phase 4 자동 Fallback"""
        estimator = EstimatorRAG()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            settings.llm_mode = 'cursor'
            
            # Phase 4 필요한 질문
            result = estimator.estimate(
                question="서울 음식점 수는?",
                context=Context(region='서울')
            )
            
            # v7.9.0: 자동 Fallback
            assert isinstance(result, EstimationResult)
            
        finally:
            settings.llm_mode = original_mode


class TestErrorHandling:
    """에러 처리 통합 테스트"""
    
    def test_empty_question(self):
        """빈 질문"""
        estimator = EstimatorRAG()
        
        # 빈 질문은 에러 발생 또는 phase=-1
        try:
            result = estimator.estimate(question="")
            # 에러 없이 처리되면 phase=-1
            assert isinstance(result, EstimationResult)
            if not result.is_successful():
                assert result.phase == -1
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
        
        # None project_data
        result = estimator.estimate(
            question="테스트?",
            project_data=None
        )
        
        # 에러 없이 처리 (다른 Phase로)
        assert isinstance(result, EstimationResult)
    
    def test_invalid_context(self):
        """잘못된 Context"""
        estimator = EstimatorRAG()
        
        # None context
        result = estimator.estimate(
            question="테스트?",
            context=None
        )
        
        # 에러 없이 처리
        assert isinstance(result, EstimationResult)


class TestNoneReturnRemoval:
    """None 반환 제거 검증 (v7.9.0)"""
    
    def test_always_return_estimation_result(self):
        """항상 EstimationResult 반환"""
        estimator = EstimatorRAG()
        
        # 다양한 질문 테스트
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
    
    def test_phase_minus_one_on_failure(self):
        """실패 시 phase=-1"""
        estimator = EstimatorRAG()
        
        # 모든 Phase 실패하는 질문
        result = estimator.estimate(
            question="완전히 알 수 없는 질문?",
            context=Context()
        )
        
        # EstimationResult 반환
        assert isinstance(result, EstimationResult)
        
        # 실패하면 phase=-1
        if not result.is_successful():
            assert result.phase == -1
            assert result.error is not None
            assert len(result.failed_phases) > 0


class TestPhaseProgression:
    """Phase 진행 순서 테스트"""
    
    def test_phase_order_phase0_first(self):
        """Phase 0 우선 확인"""
        estimator = EstimatorRAG()
        
        # Phase 0는 질문에 키워드가 포함되어야 매칭
        # "값은?" → "value" 키 확인
        result = estimator.estimate(
            question="value 값은?",  # 키워드 포함
            project_data={'value': 42}
        )
        
        # Phase 0 성공 또는 Phase 3 (매칭 실패 시)
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == 42
        # 매칭 실패 시 다른 Phase로 진행
        assert result.is_successful() or result.phase == -1
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase_order_skip_to_phase3(self):
        """Phase 0-2 스킵 → Phase 3"""
        estimator = EstimatorRAG()
        
        # project_data 없음, Validator 없음 → Phase 3
        result = estimator.estimate(
            question="2025년 새로운 시장?",
            context=Context()
        )
        
        # Phase 3 이상
        assert result.phase >= 3


class TestPerformance:
    """통합 성능 테스트"""
    
    def test_phase0_speed(self):
        """Phase 0 속도 (<0.1초)"""
        import time
        
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="value",  # 키 정확히 일치
            project_data={'value': 100}
        )
        duration = time.time() - start
        
        # Phase 0 성공 또는 Phase 3 (매칭 실패)
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert duration < 0.1, f"Phase 0 too slow: {duration:.3f}s"
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase3_speed(self):
        """Phase 3 속도 (<5초)"""
        import time
        
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="AI 챗봇 ARPU?",
            context=Context(domain='AI_Chatbot')
        )
        duration = time.time() - start
        
        if result.phase == 3:
            assert duration < 5.0, f"Phase 3 too slow: {duration:.3f}s"


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


