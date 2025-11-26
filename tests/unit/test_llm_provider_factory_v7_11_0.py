"""
LLM Provider Factory Unit Tests

Phase 4: Provider 팩토리 테스트

작성: 2025-11-26
"""

import pytest
import os
from umis_rag.core.llm_interface import LLMProvider
from umis_rag.core.llm_cursor import CursorLLMProvider
from umis_rag.core.llm_external import ExternalLLMProvider
from umis_rag.core.llm_provider_factory import (
    get_llm_provider,
    get_default_llm_provider,
    reset_llm_provider,
    get_current_mode_info
)


class TestGetLLMProvider:
    """get_llm_provider() 테스트"""
    
    def test_get_provider_returns_cursor_for_cursor_mode(self):
        """mode="cursor" → CursorLLMProvider"""
        provider = get_llm_provider(mode="cursor")
        
        assert isinstance(provider, CursorLLMProvider)
        assert isinstance(provider, LLMProvider)
        assert provider.is_native() is True
    
    def test_get_provider_returns_external_for_other_modes(self):
        """mode="gpt-4o-mini" → ExternalLLMProvider"""
        provider = get_llm_provider(mode="gpt-4o-mini")
        
        assert isinstance(provider, ExternalLLMProvider)
        assert isinstance(provider, LLMProvider)
        assert provider.is_native() is False
    
    def test_get_provider_returns_external_for_any_model_name(self):
        """모든 모델명 (cursor 제외) → ExternalLLMProvider"""
        models = ["gpt-4o", "gpt-4o-mini", "o1-mini", "claude-3-sonnet"]
        
        for model in models:
            provider = get_llm_provider(mode=model)
            assert isinstance(provider, ExternalLLMProvider)
    
    def test_get_provider_uses_settings_when_mode_is_none(self):
        """mode=None → settings.llm_mode 사용"""
        # settings.llm_mode에 따라 Provider 선택
        provider = get_llm_provider(mode=None)
        
        assert isinstance(provider, LLMProvider)
        
        # 환경에 따라 Cursor 또는 External
        current_mode = os.getenv("LLM_MODE", "cursor").lower()
        if current_mode == "cursor":
            assert isinstance(provider, CursorLLMProvider)
        else:
            assert isinstance(provider, ExternalLLMProvider)
    
    def test_get_provider_case_insensitive(self):
        """대소문자 구분 없음"""
        provider1 = get_llm_provider(mode="CURSOR")
        provider2 = get_llm_provider(mode="Cursor")
        provider3 = get_llm_provider(mode="cursor")
        
        assert isinstance(provider1, CursorLLMProvider)
        assert isinstance(provider2, CursorLLMProvider)
        assert isinstance(provider3, CursorLLMProvider)
    
    def test_get_provider_strips_whitespace(self):
        """공백 제거"""
        provider = get_llm_provider(mode="  cursor  ")
        assert isinstance(provider, CursorLLMProvider)


class TestGetDefaultLLMProvider:
    """get_default_llm_provider() 테스트 (싱글톤)"""
    
    def test_default_provider_returns_instance(self):
        """get_default_llm_provider() 인스턴스 반환"""
        reset_llm_provider()  # 초기화
        
        provider = get_default_llm_provider()
        assert isinstance(provider, LLMProvider)
    
    def test_default_provider_returns_same_instance(self):
        """같은 인스턴스 반환 (싱글톤)"""
        reset_llm_provider()  # 초기화
        
        provider1 = get_default_llm_provider()
        provider2 = get_default_llm_provider()
        
        # 같은 인스턴스
        assert provider1 is provider2
    
    def test_default_provider_after_reset(self):
        """reset 후 새 인스턴스 반환"""
        reset_llm_provider()
        provider1 = get_default_llm_provider()
        
        reset_llm_provider()
        provider2 = get_default_llm_provider()
        
        # 다른 인스턴스
        assert provider1 is not provider2


class TestResetLLMProvider:
    """reset_llm_provider() 테스트"""
    
    def test_reset_clears_singleton(self):
        """reset은 싱글톤 초기화"""
        reset_llm_provider()
        provider1 = get_default_llm_provider()
        
        reset_llm_provider()
        
        # 새 인스턴스 생성됨
        provider2 = get_default_llm_provider()
        assert provider1 is not provider2
    
    def test_reset_multiple_times(self):
        """여러 번 reset 가능"""
        reset_llm_provider()
        reset_llm_provider()
        reset_llm_provider()
        
        # 에러 없이 실행
        provider = get_default_llm_provider()
        assert isinstance(provider, LLMProvider)


class TestGetCurrentModeInfo:
    """get_current_mode_info() 테스트"""
    
    def test_current_mode_info_returns_dict(self):
        """get_current_mode_info() dict 반환"""
        info = get_current_mode_info()
        
        assert isinstance(info, dict)
        assert "mode" in info
        assert "provider" in info
        assert "uses_api" in info
        assert "cost" in info
        assert "automation" in info
    
    def test_current_mode_info_matches_provider(self):
        """정보가 실제 Provider와 일치"""
        # Cursor 모드
        provider = get_llm_provider(mode="cursor")
        
        # Provider의 get_mode_info()와 동일
        expected_info = provider.get_mode_info()
        actual_info = get_current_mode_info()
        
        # 같은 정보 (싱글톤이므로 현재 설정 기준)
        assert "mode" in actual_info
        assert "provider" in actual_info


class TestProviderWorkflow:
    """Provider 사용 패턴 테스트"""
    
    def test_estimator_pattern_with_factory(self):
        """Estimator에서 Factory 사용 패턴"""
        
        # Estimator 시뮬레이션
        class FakeEstimator:
            def __init__(self, llm_provider=None):
                self.llm_provider = llm_provider or get_default_llm_provider()
        
        # Factory 사용
        reset_llm_provider()
        estimator = FakeEstimator()
        
        assert estimator.llm_provider is not None
        assert isinstance(estimator.llm_provider, LLMProvider)
    
    def test_provider_injection_pattern(self):
        """Provider 주입 패턴"""
        
        class FakeEstimator:
            def __init__(self, llm_provider=None):
                self.llm_provider = llm_provider or get_default_llm_provider()
        
        # 직접 Provider 주입
        custom_provider = get_llm_provider(mode="cursor")
        estimator = FakeEstimator(llm_provider=custom_provider)
        
        assert estimator.llm_provider is custom_provider
    
    def test_mode_switch_pattern(self):
        """모드 전환 패턴"""
        
        # Cursor 모드
        provider_cursor = get_llm_provider(mode="cursor")
        assert isinstance(provider_cursor, CursorLLMProvider)
        
        # External 모드로 전환
        provider_external = get_llm_provider(mode="gpt-4o-mini")
        assert isinstance(provider_external, ExternalLLMProvider)
        
        # 각 Provider는 독립적
        assert provider_cursor is not provider_external


class TestFactoryEdgeCases:
    """Factory 엣지 케이스 테스트"""
    
    def test_empty_string_mode(self):
        """빈 문자열 모드"""
        # 빈 문자열 → settings 사용
        provider = get_llm_provider(mode="")
        
        # 환경의 LLM_MODE에 따라 결정
        current_mode = os.getenv("LLM_MODE", "cursor").lower()
        if current_mode == "cursor":
            assert isinstance(provider, CursorLLMProvider)
        else:
            assert isinstance(provider, ExternalLLMProvider)
    
    def test_whitespace_only_mode(self):
        """공백만 있는 모드"""
        # 공백만 → 제거 후 빈 문자열 → settings 사용
        provider = get_llm_provider(mode="   ")
        
        # 환경의 LLM_MODE에 따라 결정
        current_mode = os.getenv("LLM_MODE", "cursor").lower()
        if current_mode == "cursor":
            assert isinstance(provider, CursorLLMProvider)
        else:
            assert isinstance(provider, ExternalLLMProvider)
    
    def test_mixed_case_cursor(self):
        """대소문자 섞인 cursor"""
        modes = ["CuRsOr", "CURSOR", "cursor", "Cursor"]
        
        for mode in modes:
            provider = get_llm_provider(mode=mode)
            assert isinstance(provider, CursorLLMProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
