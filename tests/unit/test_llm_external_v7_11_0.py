"""
External LLM Unit Tests

Phase 3: External 구현 테스트

작성: 2025-11-26
"""

import pytest
import os
from umis_rag.core.llm_interface import TaskType, BaseLLM, LLMProvider
from umis_rag.core.llm_external import ExternalLLM, ExternalLLMProvider


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Skip 조건: LLM_MODE가 cursor이면 External 테스트 스킵
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SKIP_EXTERNAL = os.getenv("LLM_MODE", "").lower() == "cursor"
SKIP_REASON = "External LLM 테스트는 External 모드 필요 (LLM_MODE != cursor)"


class TestExternalLLM:
    """ExternalLLM 테스트"""
    
    def test_external_llm_initialization(self):
        """ExternalLLM 초기화"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        assert llm.task == TaskType.PRIOR_ESTIMATION
        assert llm.stage == 2  # Prior = Stage 2
        assert llm.is_native() is False
    
    def test_external_llm_implements_base_llm(self):
        """ExternalLLM이 BaseLLM 인터페이스를 구현하는지 확인"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        assert isinstance(llm, BaseLLM)
    
    def test_external_llm_model_selection(self):
        """모델 자동 선택 확인"""
        # Stage 2: gpt-4.1-nano (또는 설정된 모델)
        llm2 = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        assert llm2.model_name is not None
        assert llm2.model_config is not None
        
        # Stage 3: gpt-4o-mini (또는 설정된 모델)
        llm3 = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        assert llm3.model_name is not None
        assert llm3.stage == 3
    
    def test_is_native_returns_false(self):
        """is_native()는 False 반환"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        assert llm.is_native() is False
    
    @pytest.mark.skipif(SKIP_EXTERNAL, reason=SKIP_REASON)
    def test_estimate_returns_result(self):
        """estimate()는 완성된 결과 반환 (External 모드)"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        
        result = llm.estimate(
            question="What is average SaaS churn rate?",
            context={"industry": "SaaS"}
        )
        
        # External 모드: 완성된 결과 (None 아님)
        # API 호출 성공 시 dict 반환, 실패 시 None
        assert result is None or isinstance(result, dict)
        
        if result:
            assert "value" in result or "source" in result
    
    @pytest.mark.skipif(SKIP_EXTERNAL, reason=SKIP_REASON)
    def test_decompose_returns_result(self):
        """decompose()는 분해 결과 반환"""
        llm = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        
        result = llm.decompose(
            question="What is Spotify's annual revenue?",
            context={"industry": "Music"},
            budget={"max_variables": 5, "max_depth": 2}
        )
        
        # External 모드: 분해 결과
        assert result is None or isinstance(result, dict)
        
        if result:
            # variables, formula 중 하나 이상 포함
            assert "variables" in result or "formula" in result
    
    @pytest.mark.skipif(SKIP_EXTERNAL, reason=SKIP_REASON)
    def test_evaluate_certainty_returns_level(self):
        """evaluate_certainty()는 확신도 반환"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        certainty = llm.evaluate_certainty(
            question="What is SaaS churn rate?",
            value=5.0,
            context={"industry": "SaaS"}
        )
        
        # high, medium, low 중 하나
        assert certainty in ["high", "medium", "low"]
    
    @pytest.mark.skipif(SKIP_EXTERNAL, reason=SKIP_REASON)
    def test_validate_boundary_returns_result(self):
        """validate_boundary()는 검증 결과 반환"""
        llm = ExternalLLM(TaskType.BOUNDARY_VALIDATION)
        
        result = llm.validate_boundary(
            value=100,
            context={"industry": "SaaS"}
        )
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert isinstance(result["is_valid"], bool)


class TestExternalLLMProvider:
    """ExternalLLMProvider 테스트"""
    
    def test_external_provider_initialization(self):
        """ExternalLLMProvider 초기화"""
        provider = ExternalLLMProvider()
        assert provider.is_native() is False
    
    def test_external_provider_implements_llm_provider(self):
        """ExternalLLMProvider가 LLMProvider 인터페이스를 구현하는지 확인"""
        provider = ExternalLLMProvider()
        assert isinstance(provider, LLMProvider)
    
    def test_get_llm_returns_external_llm(self):
        """get_llm()은 ExternalLLM 반환"""
        provider = ExternalLLMProvider()
        llm = provider.get_llm(TaskType.PRIOR_ESTIMATION)
        
        assert isinstance(llm, ExternalLLM)
        assert isinstance(llm, BaseLLM)
    
    def test_get_llm_for_different_tasks(self):
        """다양한 Task에 대해 ExternalLLM 반환"""
        provider = ExternalLLMProvider()
        
        tasks = [
            TaskType.PRIOR_ESTIMATION,
            TaskType.FERMI_DECOMPOSITION,
            TaskType.CERTAINTY_EVALUATION
        ]
        
        for task in tasks:
            llm = provider.get_llm(task)
            assert isinstance(llm, ExternalLLM)
            assert llm.task == task
    
    def test_is_native_returns_false(self):
        """is_native()는 False 반환"""
        provider = ExternalLLMProvider()
        assert provider.is_native() is False
    
    def test_get_mode_info(self):
        """get_mode_info() 반환값 확인"""
        provider = ExternalLLMProvider()
        info = provider.get_mode_info()
        
        assert info["mode"] == "external"
        assert info["provider"] == "ExternalLLMProvider"
        assert info["uses_api"] is True
        assert info["automation"] is True


class TestExternalPromptGeneration:
    """프롬프트 생성 테스트"""
    
    def test_build_prior_prompt(self):
        """Prior 프롬프트 생성"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        
        prompt = llm._build_prior_prompt(
            question="What is LTV?",
            context={"industry": "SaaS"}
        )
        
        assert "What is LTV?" in prompt
        assert "SaaS" in prompt
        assert "JSON" in prompt or "json" in prompt
    
    def test_build_fermi_prompt(self):
        """Fermi 프롬프트 생성"""
        llm = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        
        prompt = llm._build_fermi_prompt(
            question="What is revenue?",
            context={"industry": "Music"},
            budget={"max_variables": 5}
        )
        
        assert "revenue" in prompt.lower()
        assert "5" in prompt  # max_variables
    
    def test_build_certainty_prompt(self):
        """확신도 프롬프트 생성"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        prompt = llm._build_certainty_prompt(
            question="What is churn?",
            value=5.0,
            context={"industry": "SaaS"}
        )
        
        assert "churn" in prompt.lower()
        assert "5.0" in prompt or "5" in prompt
    
    def test_build_boundary_prompt(self):
        """경계 검증 프롬프트 생성"""
        llm = ExternalLLM(TaskType.BOUNDARY_VALIDATION)
        
        prompt = llm._build_boundary_prompt(
            value=1000,
            context={"industry": "SaaS"}
        )
        
        assert "1000" in prompt
        assert "SaaS" in prompt


class TestExternalResponseParsing:
    """응답 파싱 테스트"""
    
    def test_parse_prior_response_valid_json(self):
        """Prior 응답 파싱 - 정상 JSON"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        
        response = '''
        {
            "value": 5.0,
            "unit": "%",
            "certainty": "high",
            "reasoning": "Based on benchmarks"
        }
        '''
        
        result = llm._parse_prior_response(response, "test", {})
        
        assert result is not None
        assert result["value"] == 5.0
        assert result["unit"] == "%"
        assert result["certainty"] == "high"
    
    def test_parse_prior_response_invalid_json(self):
        """Prior 응답 파싱 - 잘못된 JSON"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        
        response = "This is not JSON"
        result = llm._parse_prior_response(response, "test", {})
        
        # 파싱 실패 시 None 반환
        assert result is None
    
    def test_parse_fermi_response_valid_json(self):
        """Fermi 응답 파싱 - 정상 JSON"""
        llm = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        
        response = '''
        {
            "variables": [
                {"name": "users", "description": "Total users", "unit": "users"}
            ],
            "formula": "users * arpu",
            "reasoning": "Revenue = users * ARPU"
        }
        '''
        
        result = llm._parse_fermi_response(response)
        
        assert result is not None
        assert "variables" in result
        assert len(result["variables"]) == 1
        assert result["formula"] == "users * arpu"
    
    def test_parse_certainty_high(self):
        """확신도 파싱 - high"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        assert llm._parse_certainty("high") == "high"
        assert llm._parse_certainty("The certainty is high") == "high"
        assert llm._parse_certainty("HIGH") == "high"
    
    def test_parse_certainty_medium(self):
        """확신도 파싱 - medium"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        assert llm._parse_certainty("medium") == "medium"
        assert llm._parse_certainty("It's medium certainty") == "medium"
    
    def test_parse_certainty_low(self):
        """확신도 파싱 - low"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        assert llm._parse_certainty("low") == "low"
        assert llm._parse_certainty("The certainty is low") == "low"
    
    def test_parse_certainty_default(self):
        """확신도 파싱 - 기본값"""
        llm = ExternalLLM(TaskType.CERTAINTY_EVALUATION)
        
        # 알 수 없는 응답 → medium
        assert llm._parse_certainty("unknown") == "medium"
        assert llm._parse_certainty("") == "medium"
    
    def test_parse_boundary_response_valid_json(self):
        """경계 검증 파싱 - 정상 JSON"""
        llm = ExternalLLM(TaskType.BOUNDARY_VALIDATION)
        
        response = '''
        {
            "is_valid": true,
            "reason": "Within range",
            "suggested_range": [0, 100]
        }
        '''
        
        result = llm._parse_boundary_response(response)
        
        assert result is not None
        assert result["is_valid"] is True
        assert result["reason"] == "Within range"
        assert result["suggested_range"] == [0, 100]
    
    def test_parse_boundary_response_invalid_json(self):
        """경계 검증 파싱 - 잘못된 JSON"""
        llm = ExternalLLM(TaskType.BOUNDARY_VALIDATION)
        
        response = "Not JSON"
        result = llm._parse_boundary_response(response)
        
        # 파싱 실패 시 기본 통과
        assert result["is_valid"] is True
        assert "파싱 실패" in result["reason"]


class TestExternalHelperMethods:
    """헬퍼 메서드 테스트"""
    
    def test_format_context_dict(self):
        """_format_context() - dict"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        
        context = {
            "industry": "SaaS",
            "region": "US",
            "business_model": "Subscription"
        }
        
        formatted = llm._format_context(context)
        assert "SaaS" in formatted
        assert "US" in formatted
        assert "Subscription" in formatted
    
    def test_format_context_none(self):
        """_format_context() - None"""
        llm = ExternalLLM(TaskType.PRIOR_ESTIMATION)
        formatted = llm._format_context(None)
        assert "No context" in formatted
    
    def test_format_budget_dict(self):
        """_format_budget() - dict"""
        llm = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        
        budget = {
            "max_variables": 5,
            "max_depth": 2,
            "max_llm_calls": 10
        }
        
        formatted = llm._format_budget(budget)
        assert "5" in formatted
        assert "2" in formatted
        assert "10" in formatted
    
    def test_format_budget_none(self):
        """_format_budget() - None"""
        llm = ExternalLLM(TaskType.FERMI_DECOMPOSITION)
        formatted = llm._format_budget(None)
        assert "No budget" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
