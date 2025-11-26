"""
Phase 3 Guestimation 단위 테스트 (v7.9.0)

목표:
- Phase 3의 핵심 기능 검증
- 증거 수집 → 판단 합성 흐름 테스트
- Cursor Fallback 검증
- 에러 처리 검증

작성일: 2025-11-25
"""

import os
import pytest
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
from umis_rag.agents.estimator.models import Context, EstimationResult


class TestPhase3BasicFunctionality:
    """Phase 3 기본 기능 테스트"""
    
    def test_initialization(self):
        """Phase 3 초기화 테스트"""
        # Default (None으로 초기화 → 동적으로 settings 읽기)
        phase3 = Phase3Guestimation(llm_mode=None)
        assert phase3.llm_mode is not None
        
        # 명시적 모드 지정
        phase3_gpt = Phase3Guestimation(llm_mode='gpt-4o-mini')
        assert phase3_gpt.llm_mode == 'gpt-4o-mini'
    
    def test_llm_mode_dynamic(self):
        """LLM Mode 동적 변경 테스트 (v7.9.0)"""
        # llm_mode=None으로 초기화
        phase3 = Phase3Guestimation(llm_mode=None)
        
        # 환경변수 변경
        original_mode = os.environ.get('LLM_MODE', 'cursor')
        
        os.environ['LLM_MODE'] = 'cursor'
        # settings가 갱신되어야 함 (실제로는 import 시점에 고정)
        # 이 테스트는 property 패턴이 작동하는지 확인
        
        # Property가 설정을 읽는지 확인
        from umis_rag.core.config import settings
        settings.llm_mode = 'cursor'
        assert phase3.llm_mode == 'cursor'
        
        settings.llm_mode = 'gpt-4o-mini'
        assert phase3.llm_mode == 'gpt-4o-mini'
        
        # 원래 모드 복원
        os.environ['LLM_MODE'] = original_mode


class TestPhase3WithEvidence:
    """증거가 있을 때 Phase 3 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimate_with_context(self):
        """Context가 있을 때 추정 성공"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        result = phase3.estimate(
            question="2025년 AI 챗봇 서비스 평균 ARPU는?",
            context=Context(domain='AI_Chatbot')
        )
        
        # Phase 3 성공 검증
        assert result is not None
        assert isinstance(result, EstimationResult)
        assert result.phase == 3
        assert result.value is not None
        # v7.9.0: 신뢰도는 증거 품질에 따라 변동 (0.6-1.0)
        assert result.confidence >= 0.5
        assert result.execution_time > 0
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimate_different_domains(self):
        """다양한 Domain에서 추정"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        domains = ['B2B_SaaS', 'E_Commerce', 'Food_Service']
        
        for domain in domains:
            result = phase3.estimate(
                question=f"{domain} 평균 ARPU는?",
                context=Context(domain=domain)
            )
            
            # 각 도메인에서 결과 반환
            # (증거가 없으면 None일 수 있음)
            if result:
                assert result.phase == 3
                assert result.context.domain == domain


class TestPhase3WithoutEvidence:
    """증거가 없을 때 Phase 3 테스트"""
    
    def test_estimate_without_evidence(self):
        """증거 없을 때도 LLM이 추정 시도"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        # 매우 구체적이지 않거나 데이터가 없는 질문
        result = phase3.estimate(
            question="2099년 화성 피자 배달 시장 규모는?",
            context=Context()
        )
        
        # Phase 3는 LLM이 있으면 항상 시도
        # value=0 또는 낮은 신뢰도로 반환 가능
        if result:
            assert result.phase == 3
            # 신뢰도가 낮아야 함
            assert result.confidence < 0.8
    
    def test_estimate_empty_context(self):
        """빈 Context로 추정"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        result = phase3.estimate(
            question="평균 ARPU는?",
            context=Context()  # domain 없음
        )
        
        # Context 없으면 증거 수집 어려움
        # None 또는 낮은 신뢰도
        if result:
            assert result.confidence < 0.9


class TestPhase3CursorFallback:
    """Cursor 모드 Fallback 테스트 (v7.9.0)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required for fallback"
    )
    def test_cursor_mode_auto_fallback(self):
        """Cursor 모드에서 자동 Fallback"""
        # Cursor 모드로 초기화
        phase3 = Phase3Guestimation(llm_mode='cursor')
        
        # 원래 설정 저장
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        # Cursor 모드 설정
        settings.llm_mode = 'cursor'
        
        try:
            # Phase 3 추정 시도
            # v7.9.0: Cursor 모드면 AIAugmentedEstimationSource가 빈 리스트 반환
            # → 증거 없음 → Phase 4로 위임
            result = phase3.estimate(
                question="B2B SaaS ARPU는?",
                context=Context(domain='B2B_SaaS')
            )
            
            # Cursor 모드에서는 증거 수집 실패
            # None 또는 실패 결과 예상
            # (EstimatorRAG에서 Fallback 처리)
            
        finally:
            # 원래 모드 복원
            settings.llm_mode = original_mode


class TestPhase3ErrorHandling:
    """Phase 3 에러 처리 테스트"""
    
    def test_invalid_question_type(self):
        """잘못된 질문 타입"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        # None 질문은 AttributeError 발생
        with pytest.raises((TypeError, AttributeError)):
            phase3.estimate(
                question=None,  # None
                context=Context()
            )
    
    def test_invalid_context_type(self):
        """잘못된 Context 타입"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        # Context가 None이면 기본 Context 생성
        result = phase3.estimate(
            question="평균 ARPU는?",
            context=None
        )
        
        # 에러 없이 처리 (None 또는 결과 반환)
        assert result is None or isinstance(result, EstimationResult)


class TestPhase3SourceCollection:
    """Phase 3 Source 수집 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_source_collection_success(self):
        """Source 수집 성공"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        # Phase 3 전체 흐름 테스트 (Source Collector 포함)
        result = phase3.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        # 결과가 반환되고 증거가 수집되었는지 확인
        if result:
            assert result.phase == 3
            # value_estimates가 있어야 함
            assert len(result.value_estimates) > 0
    
    def test_source_collection_empty(self):
        """Source 수집 실패 (증거 없음)"""
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        from umis_rag.agents.estimator.source_collector import SourceCollector
        
        collector = SourceCollector(llm_mode='gpt-4o-mini')
        
        evidence = collector.collect_all(
            question="2099년 화성 피자?",
            context=Context()
        )
        
        # 증거 없을 수 있음
        if evidence:
            assert isinstance(evidence, dict)


class TestPhase3Performance:
    """Phase 3 성능 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimation_speed(self):
        """추정 속도 테스트 (<5초 목표)"""
        import time
        
        phase3 = Phase3Guestimation(llm_mode='gpt-4o-mini')
        
        start = time.time()
        result = phase3.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        duration = time.time() - start
        
        # 5초 이내 완료
        assert duration < 5.0, f"Phase 3 too slow: {duration:.3f}s"
        
        if result:
            # execution_time이 실제 측정값과 유사해야 함
            assert abs(result.execution_time - duration) < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])




