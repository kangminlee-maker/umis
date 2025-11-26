"""
Cursor LLM Unit Tests

Phase 2: Cursor 구현 테스트

작성: 2025-11-26
"""

import pytest
from umis_rag.core.llm_interface import TaskType, BaseLLM, LLMProvider
from umis_rag.core.llm_cursor import CursorLLM, CursorLLMProvider


class TestCursorLLM:
    """CursorLLM 테스트"""
    
    def test_cursor_llm_initialization(self):
        """CursorLLM 초기화"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        assert llm.task == TaskType.PRIOR_ESTIMATION
        assert llm.is_native() is True
    
    def test_cursor_llm_implements_base_llm(self):
        """CursorLLM이 BaseLLM 인터페이스를 구현하는지 확인"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        assert isinstance(llm, BaseLLM)
    
    def test_estimate_returns_none(self):
        """estimate()는 None 반환 (Cursor 모드)"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        result = llm.estimate(
            question="What is LTV?",
            context={"industry": "SaaS"}
        )
        assert result is None
    
    def test_decompose_returns_none(self):
        """decompose()는 None 반환 (Cursor 모드)"""
        llm = CursorLLM(TaskType.FERMI_DECOMPOSITION)
        result = llm.decompose(
            question="What is TAM?",
            context={"industry": "Music"},
            budget={"max_variables": 5}
        )
        assert result is None
    
    def test_evaluate_certainty_returns_medium(self):
        """evaluate_certainty()는 'medium' 반환 (기본값)"""
        llm = CursorLLM(TaskType.CERTAINTY_EVALUATION)
        certainty = llm.evaluate_certainty(
            question="What is churn rate?",
            value=5.0,
            context={"industry": "SaaS"}
        )
        assert certainty == "medium"
    
    def test_validate_boundary_returns_default_pass(self):
        """validate_boundary()는 기본 통과 반환"""
        llm = CursorLLM(TaskType.BOUNDARY_VALIDATION)
        result = llm.validate_boundary(
            value=100,
            context={"industry": "SaaS"}
        )
        
        assert result["is_valid"] is True
        assert "reason" in result
        assert result["suggested_range"] is None
    
    def test_is_native_returns_true(self):
        """is_native()는 True 반환"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        assert llm.is_native() is True


class TestCursorLLMProvider:
    """CursorLLMProvider 테스트"""
    
    def test_cursor_provider_initialization(self):
        """CursorLLMProvider 초기화"""
        provider = CursorLLMProvider()
        assert provider.is_native() is True
    
    def test_cursor_provider_implements_llm_provider(self):
        """CursorLLMProvider가 LLMProvider 인터페이스를 구현하는지 확인"""
        provider = CursorLLMProvider()
        assert isinstance(provider, LLMProvider)
    
    def test_get_llm_returns_cursor_llm(self):
        """get_llm()은 CursorLLM 반환"""
        provider = CursorLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        assert isinstance(llm, CursorLLM)
        assert isinstance(llm, BaseLLM)
    
    def test_get_llm_for_different_tasks(self):
        """다양한 Task에 대해 CursorLLM 반환"""
        provider = CursorLLMProvider()
        
        tasks = [
            TaskType.PRIOR_ESTIMATION,
            TaskType.FERMI_DECOMPOSITION,
            TaskType.CERTAINTY_EVALUATION
        ]
        
        for task in tasks:
            llm = provider.get_llm(task)
            assert isinstance(llm, CursorLLM)
            assert llm.task == task
    
    def test_is_native_returns_true(self):
        """is_native()는 True 반환"""
        provider = CursorLLMProvider()
        assert provider.is_native() is True
    
    def test_get_mode_info(self):
        """get_mode_info() 반환값 확인"""
        provider = CursorLLMProvider()
        info = provider.get_mode_info()
        
        assert info["mode"] == "cursor"
        assert info["provider"] == "CursorLLMProvider"
        assert info["uses_api"] is False
        assert info["automation"] is False
        assert "$0" in info["cost"]


class TestCursorWorkflow:
    """Cursor 워크플로우 테스트"""
    
    def test_estimator_pattern(self):
        """Estimator 사용 패턴 시뮬레이션"""
        
        # Provider 생성
        provider = CursorLLMProvider()
        
        # LLM 획득
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        # 추정 실행
        result = llm.estimate(
            question="What is SaaS LTV?",
            context={"industry": "SaaS", "region": "US"}
        )
        
        # Cursor 모드: None 반환
        assert result is None
        
        # Estimator는 None 체크 후 Cursor 포맷 응답 생성
        if result is None:
            cursor_response = {
                "mode": "cursor",
                "question": "What is SaaS LTV?",
                "instruction": "위 데이터로 추정 수행"
            }
            assert cursor_response["mode"] == "cursor"
    
    def test_fermi_decomposition_pattern(self):
        """Fermi 분해 패턴 시뮬레이션"""
        provider = CursorLLMProvider()
        llm = provider.get_llm(TaskType.FERMI_DECOMPOSITION)
        
        result = llm.decompose(
            question="What is Spotify revenue?",
            context={"industry": "Music"},
            budget={"max_variables": 5, "max_depth": 2}
        )
        
        # Cursor 모드: None 반환
        assert result is None
    
    def test_multiple_tasks_in_sequence(self):
        """여러 Task 순차 실행"""
        provider = CursorLLMProvider()
        
        # Task 1: Prior Estimation
        llm1 = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        result1 = llm1.estimate("What is LTV?", {})
        assert result1 is None
        
        # Task 2: Certainty Evaluation
        llm2 = provider.get_llm(TaskType.CERTAINTY_EVALUATION)
        certainty = llm2.evaluate_certainty("What is LTV?", 1000, {})
        assert certainty == "medium"
        
        # Task 3: Boundary Validation
        llm3 = provider.get_llm(TaskType.BOUNDARY_VALIDATION)
        validation = llm3.validate_boundary(1000, {})
        assert validation["is_valid"] is True


class TestCursorModeCharacteristics:
    """Cursor 모드 특성 테스트"""
    
    def test_no_api_calls(self):
        """API 호출 없음 (None 반환)"""
        provider = CursorLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        # 여러 번 호출해도 API 호출 없음 (항상 None)
        for _ in range(3):
            result = llm.estimate("test", {})
            assert result is None
    
    def test_zero_cost(self):
        """비용 $0"""
        provider = CursorLLMProvider()
        info = provider.get_mode_info()
        
        assert "$0" in info["cost"]
        assert info["uses_api"] is False
    
    def test_manual_mode(self):
        """수동 모드 (자동화 불가)"""
        provider = CursorLLMProvider()
        info = provider.get_mode_info()
        
        assert info["automation"] is False


class TestCursorHelperMethods:
    """Cursor 헬퍼 메서드 테스트"""
    
    def test_format_context_dict(self):
        """_format_context() - dict 입력"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        context = {"industry": "SaaS", "region": "US"}
        
        formatted = llm._format_context(context)
        assert "SaaS" in formatted
        assert "US" in formatted
    
    def test_format_context_none(self):
        """_format_context() - None 입력"""
        llm = CursorLLM(TaskType.PRIOR_ESTIMATION)
        formatted = llm._format_context(None)
        assert formatted == "{}"
    
    def test_format_budget_dict(self):
        """_format_budget() - dict 입력"""
        llm = CursorLLM(TaskType.FERMI_DECOMPOSITION)
        budget = {"max_variables": 5, "max_depth": 2}
        
        formatted = llm._format_budget(budget)
        assert "5" in formatted
        assert "2" in formatted
    
    def test_format_budget_none(self):
        """_format_budget() - None 입력"""
        llm = CursorLLM(TaskType.FERMI_DECOMPOSITION)
        formatted = llm._format_budget(None)
        assert formatted == "{}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
