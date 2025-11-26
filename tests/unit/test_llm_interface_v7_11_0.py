"""
LLM Interface Unit Tests

Phase 1: 인터페이스 정의 테스트

작성: 2025-11-26
"""

import pytest
from umis_rag.core.llm_interface import (
    TaskType,
    BaseLLM,
    LLMProvider,
    TASK_TO_STAGE
)


class TestTaskType:
    """TaskType Enum 테스트"""
    
    def test_task_type_values(self):
        """TaskType 값 확인"""
        assert TaskType.PRIOR_ESTIMATION.value == "prior_estimation"
        assert TaskType.FERMI_DECOMPOSITION.value == "fermi_decomposition"
        assert TaskType.CERTAINTY_EVALUATION.value == "certainty_evaluation"
    
    def test_all_task_types_defined(self):
        """모든 Task Type 정의 확인"""
        expected_tasks = [
            "evidence_collection",
            "prior_estimation",
            "certainty_evaluation",
            "fermi_decomposition",
            "fermi_variable_estimation",
            "fusion_calculation",
            "boundary_validation",
            "guardrail_analysis"
        ]
        
        task_values = [task.value for task in TaskType]
        
        for expected in expected_tasks:
            assert expected in task_values


class TestTaskToStageMapping:
    """Task → Stage 매핑 테스트"""
    
    def test_stage1_tasks(self):
        """Stage 1 작업 매핑"""
        assert TASK_TO_STAGE[TaskType.EVIDENCE_COLLECTION] == 1
        assert TASK_TO_STAGE[TaskType.GUARDRAIL_ANALYSIS] == 1
    
    def test_stage2_tasks(self):
        """Stage 2 작업 매핑"""
        assert TASK_TO_STAGE[TaskType.PRIOR_ESTIMATION] == 2
        assert TASK_TO_STAGE[TaskType.CERTAINTY_EVALUATION] == 2
        assert TASK_TO_STAGE[TaskType.FERMI_VARIABLE_ESTIMATION] == 2
        assert TASK_TO_STAGE[TaskType.BOUNDARY_VALIDATION] == 2
    
    def test_stage3_tasks(self):
        """Stage 3 작업 매핑"""
        assert TASK_TO_STAGE[TaskType.FERMI_DECOMPOSITION] == 3
    
    def test_stage4_tasks(self):
        """Stage 4 작업 매핑"""
        assert TASK_TO_STAGE[TaskType.FUSION_CALCULATION] == 4
    
    def test_all_tasks_mapped(self):
        """모든 TaskType이 Stage에 매핑되었는지 확인"""
        for task in TaskType:
            assert task in TASK_TO_STAGE


class TestBaseLLMInterface:
    """BaseLLM 인터페이스 테스트"""
    
    def test_base_llm_is_abstract(self):
        """BaseLLM은 추상 클래스여야 함"""
        with pytest.raises(TypeError):
            # 추상 클래스 직접 인스턴스화 불가
            BaseLLM()
    
    def test_base_llm_has_required_methods(self):
        """BaseLLM 필수 메서드 확인"""
        required_methods = [
            "estimate",
            "decompose",
            "evaluate_certainty",
            "validate_boundary",
            "is_native"
        ]
        
        for method in required_methods:
            assert hasattr(BaseLLM, method)
            assert callable(getattr(BaseLLM, method))


class TestLLMProviderInterface:
    """LLMProvider 인터페이스 테스트"""
    
    def test_llm_provider_is_abstract(self):
        """LLMProvider는 추상 클래스여야 함"""
        with pytest.raises(TypeError):
            # 추상 클래스 직접 인스턴스화 불가
            LLMProvider()
    
    def test_llm_provider_has_required_methods(self):
        """LLMProvider 필수 메서드 확인"""
        required_methods = [
            "get_llm",
            "is_native",
            "get_mode_info"
        ]
        
        for method in required_methods:
            assert hasattr(LLMProvider, method)
            assert callable(getattr(LLMProvider, method))


class MockLLM(BaseLLM):
    """테스트용 Mock LLM"""
    
    def estimate(self, question, context, **kwargs):
        return {"value": 100, "source": "mock"}
    
    def decompose(self, question, context, budget, **kwargs):
        return {"variables": [], "formula": None}
    
    def evaluate_certainty(self, question, value, context, **kwargs):
        return "medium"
    
    def validate_boundary(self, value, context, **kwargs):
        return {"is_valid": True, "reason": "mock"}
    
    def is_native(self):
        return False


class MockLLMProvider(LLMProvider):
    """테스트용 Mock Provider"""
    
    def get_llm(self, task):
        return MockLLM()
    
    def is_native(self):
        return False
    
    def get_mode_info(self):
        return {"mode": "mock", "provider": "MockLLMProvider"}


class TestMockImplementation:
    """Mock 구현체 테스트 (인터페이스 준수 확인)"""
    
    def test_mock_llm_implements_interface(self):
        """MockLLM이 BaseLLM 인터페이스를 준수하는지 확인"""
        llm = MockLLM()
        
        # 모든 메서드 호출 가능
        assert llm.estimate("test", {}) is not None
        assert llm.decompose("test", {}, {}) is not None
        assert llm.evaluate_certainty("test", 100, {}) == "medium"
        assert llm.validate_boundary(100, {})["is_valid"] is True
        assert llm.is_native() is False
    
    def test_mock_provider_implements_interface(self):
        """MockLLMProvider가 LLMProvider 인터페이스를 준수하는지 확인"""
        provider = MockLLMProvider()
        
        # get_llm 호출
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        assert isinstance(llm, BaseLLM)
        
        # is_native 호출
        assert provider.is_native() is False
        
        # get_mode_info 호출
        info = provider.get_mode_info()
        assert "mode" in info
        assert "provider" in info
    
    def test_provider_returns_working_llm(self):
        """Provider가 반환한 LLM이 실제로 작동하는지 확인"""
        provider = MockLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        # LLM 메서드 호출
        result = llm.estimate("What is LTV?", {})
        assert result is not None
        assert "value" in result
        assert result["value"] == 100


class TestInterfaceUsagePattern:
    """인터페이스 사용 패턴 테스트"""
    
    def test_dependency_injection_pattern(self):
        """의존성 주입 패턴 테스트"""
        
        # Mock Provider 생성
        provider = MockLLMProvider()
        
        # Estimator처럼 사용 (시뮬레이션)
        class FakeEstimator:
            def __init__(self, llm_provider: LLMProvider):
                self.llm_provider = llm_provider
            
            def estimate(self, question):
                llm = self.llm_provider.get_llm(TaskType.PRIOR_ESTIMATION)
                return llm.estimate(question, {})
        
        # 의존성 주입
        estimator = FakeEstimator(llm_provider=provider)
        result = estimator.estimate("What is LTV?")
        
        assert result is not None
        assert result["value"] == 100
    
    def test_task_type_routing(self):
        """TaskType별 라우팅 테스트"""
        provider = MockLLMProvider()
        
        # 다양한 TaskType으로 LLM 획득
        tasks = [
            TaskType.PRIOR_ESTIMATION,
            TaskType.FERMI_DECOMPOSITION,
            TaskType.CERTAINTY_EVALUATION
        ]
        
        for task in tasks:
            llm = provider.get_llm(task)
            assert isinstance(llm, BaseLLM)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
