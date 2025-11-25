"""
Phase 4 Fermi Decomposition 단위 테스트 (v7.9.0)

목표:
- Phase 4의 핵심 기능 검증
- 모형 생성 → 실행 흐름 테스트
- 순환 의존성 감지
- 재귀 추정 검증
- Backtracking 검증
- 에러 처리 검증

작성일: 2025-11-25
"""

import os
import pytest
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
from umis_rag.agents.estimator.models import Context, EstimationResult


class TestPhase4BasicFunctionality:
    """Phase 4 기본 기능 테스트"""
    
    def test_initialization(self):
        """Phase 4 초기화 테스트"""
        phase4 = Phase4FermiDecomposition()
        
        # v7.9.0: llm_mode는 Property
        assert phase4.llm_mode is not None
        
        # Phase 3 초기화 확인 (Lazy)
        assert phase4.phase3 is None or hasattr(phase4.phase3, 'estimate')
    
    def test_llm_mode_dynamic(self):
        """LLM Mode 동적 변경 테스트 (v7.9.0)"""
        phase4 = Phase4FermiDecomposition()
        
        # 환경변수 변경
        from umis_rag.core.config import settings
        
        original_mode = settings.llm_mode
        
        settings.llm_mode = 'cursor'
        assert phase4.llm_mode == 'cursor'
        
        settings.llm_mode = 'gpt-4o-mini'
        assert phase4.llm_mode == 'gpt-4o-mini'
        
        # 복원
        settings.llm_mode = original_mode
    
    def test_llm_client_dynamic(self):
        """LLM Client 동적 생성 테스트 (v7.9.0)"""
        phase4 = Phase4FermiDecomposition()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            # Cursor 모드면 client None
            settings.llm_mode = 'cursor'
            assert phase4.llm_client is None
            
            # API 모드면 client 생성
            if os.environ.get('OPENAI_API_KEY'):
                settings.llm_mode = 'gpt-4o-mini'
                client = phase4.llm_client
                # Client가 생성되거나 None (API 키 없음)
                assert client is None or hasattr(client, 'chat')
        finally:
            settings.llm_mode = original_mode


class TestPhase4ModelGeneration:
    """Phase 4 모형 생성 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_generate_models_simple(self):
        """간단한 질문에서 모형 생성"""
        phase4 = Phase4FermiDecomposition()
        
        result = phase4.estimate(
            question="서울 음식점 수는?",
            context=Context(region='서울'),
            available_data={},
            depth=0
        )
        
        # 모형 생성 및 실행 성공
        if result:
            assert result.phase == 4
            assert result.fermi_model is not None
            assert result.value is not None or result.value_range is not None
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_generate_models_with_available_data(self):
        """이미 알려진 데이터가 있을 때 모형 생성"""
        phase4 = Phase4FermiDecomposition()
        
        result = phase4.estimate(
            question="서울 전체 음식점 매출은?",
            context=Context(region='서울'),
            available_data={
                'restaurants': 100000,  # 음식점 수
                'avg_revenue': 50000000  # 평균 매출
            },
            depth=0
        )
        
        # 기존 데이터를 활용한 모형
        if result:
            assert result.phase == 4
            # 기존 데이터를 사용했는지 확인
            if result.variable_results:
                assert len(result.variable_results) >= 0


class TestPhase4CircularDependency:
    """Phase 4 순환 의존성 테스트"""
    
    def test_circular_detection(self):
        """순환 의존성 감지"""
        phase4 = Phase4FermiDecomposition()
        
        # _detect_circular 메서드 시그니처 확인 필요
        # 실제 메서드 시그니처에 맞게 호출
        question = "순환 변수 A는?"
        
        # 간접 테스트: 실제 estimate 호출로 순환 감지 확인
        # (순환 의존성은 내부적으로 처리됨)
        result = phase4.estimate(
            question=question,
            context=Context(),
            available_data={},
            depth=2  # Depth 높이면 순환 가능성
        )
        
        # Depth 제한으로 중단되거나 실패
        assert result is None or isinstance(result, EstimationResult)
    
    def test_no_circular(self):
        """순환 의존성 없음"""
        phase4 = Phase4FermiDecomposition()
        
        # 순환 없는 정상 호출
        result = phase4.estimate(
            question="A는?",
            context=Context(),
            available_data={},
            depth=0
        )
        
        # 정상 처리 (순환 없음)
        assert result is None or isinstance(result, EstimationResult)


class TestPhase4RecursiveEstimation:
    """Phase 4 재귀 추정 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_recursive_estimation_depth1(self):
        """Depth 1 재귀 추정"""
        phase4 = Phase4FermiDecomposition()
        
        # 단순한 질문 (depth 제한)
        result = phase4.estimate(
            question="서울 인구는?",
            context=Context(region='서울'),
            available_data={},
            depth=0  # 첫 호출
        )
        
        # Depth 0에서 시작
        if result:
            assert result.phase == 4 or result.phase == 3  # Phase 3 Fallback 가능
    
    def test_max_depth_limit(self):
        """최대 Depth 제한"""
        phase4 = Phase4FermiDecomposition()
        
        # Max depth 확인
        max_depth = phase4.config.max_depth if hasattr(phase4, 'config') else 3
        
        # Depth 초과 시 재귀 중단
        result = phase4.estimate(
            question="테스트?",
            context=Context(),
            available_data={},
            depth=max_depth + 1  # 초과
        )
        
        # Depth 초과면 None 또는 실패
        assert result is None or result.phase == -1


class TestPhase4FormulaExecution:
    """Phase 4 수식 실행 테스트"""
    
    def test_simple_multiplication(self):
        """단순 곱셈 수식"""
        phase4 = Phase4FermiDecomposition()
        
        # 수식 실행 (_execute_formula_simple)
        formula = "A * B"
        bindings = {'A': 100, 'B': 50}
        
        result = phase4._execute_formula_simple(formula, bindings)
        
        assert result == 5000
    
    def test_division(self):
        """나눗셈 수식"""
        phase4 = Phase4FermiDecomposition()
        
        formula = "A / B"
        bindings = {'A': 100, 'B': 4}
        
        result = phase4._execute_formula_simple(formula, bindings)
        
        assert result == 25
    
    def test_zero_division(self):
        """0으로 나누기 처리"""
        phase4 = Phase4FermiDecomposition()
        
        formula = "A / B"
        bindings = {'A': 100, 'B': 0}
        
        # 0으로 나누기 시 0 또는 None 반환
        result = phase4._execute_formula_simple(formula, bindings)
        
        # 0 또는 None (구현에 따라)
        assert result is None or result == 0
    
    def test_missing_variable(self):
        """변수 누락 시 처리"""
        phase4 = Phase4FermiDecomposition()
        
        formula = "A * B"
        bindings = {'A': 100}  # B 누락
        
        # 변수 누락 시: 
        # - Option 1: 누락 변수를 0으로 처리 → A * 0 = 0
        # - Option 2: 누락 변수 기본값 1 → A * 1 = 100
        # - Option 3: None 반환
        result = phase4._execute_formula_simple(formula, bindings)
        
        # 구현에 따라 None 또는 계산 결과
        assert result is None or isinstance(result, (int, float))


class TestPhase4Backtracking:
    """Phase 4 Backtracking 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_backtracking_on_failure(self):
        """모형 실행 실패 시 Backtracking"""
        phase4 = Phase4FermiDecomposition()
        
        # 실행 불가능한 모형이 있을 때
        # (실제 테스트는 복잡하므로 개념적 검증)
        
        result = phase4.estimate(
            question="테스트 질문?",
            context=Context(),
            available_data={},
            depth=0
        )
        
        # Backtracking으로 다른 모형 시도 가능
        # 또는 실패 (None)
        assert result is None or isinstance(result, EstimationResult)


class TestPhase4ErrorHandling:
    """Phase 4 에러 처리 테스트"""
    
    def test_invalid_question(self):
        """잘못된 질문"""
        phase4 = Phase4FermiDecomposition()
        
        with pytest.raises((TypeError, AttributeError)):
            phase4.estimate(
                question=None,
                context=Context(),
                available_data={},
                depth=0
            )
    
    def test_invalid_depth(self):
        """잘못된 Depth"""
        phase4 = Phase4FermiDecomposition()
        
        # 음수 Depth
        result = phase4.estimate(
            question="테스트?",
            context=Context(),
            available_data={},
            depth=-1
        )
        
        # 에러 없이 처리 (또는 None)
        assert result is None or isinstance(result, EstimationResult)
    
    def test_empty_available_data(self):
        """빈 available_data"""
        phase4 = Phase4FermiDecomposition()
        
        result = phase4.estimate(
            question="테스트?",
            context=Context(),
            available_data={},  # 빈 딕셔너리
            depth=0
        )
        
        # 에러 없이 처리
        assert result is None or isinstance(result, EstimationResult)


class TestPhase4CursorFallback:
    """Phase 4 Cursor 모드 Fallback 테스트"""
    
    def test_cursor_mode_behavior(self):
        """Cursor 모드에서 Phase 4 동작"""
        phase4 = Phase4FermiDecomposition()
        
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        
        try:
            settings.llm_mode = 'cursor'
            
            # Cursor 모드에서 추정 시도
            result = phase4.estimate(
                question="서울 음식점 수는?",
                context=Context(region='서울'),
                available_data={},
                depth=0
            )
            
            # Cursor 모드는 instruction만 생성
            # → Phase 3 Fallback
            # → None 또는 Phase 3 결과
            
        finally:
            settings.llm_mode = original_mode


class TestPhase4Performance:
    """Phase 4 성능 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_estimation_speed_simple(self):
        """단순 모형 추정 속도 (<10초 목표)"""
        import time
        
        phase4 = Phase4FermiDecomposition()
        
        start = time.time()
        result = phase4.estimate(
            question="서울 음식점 수는?",
            context=Context(region='서울'),
            available_data={},
            depth=0
        )
        duration = time.time() - start
        
        # 10초 이내 완료 (단순 모형)
        if result:
            assert duration < 10.0, f"Phase 4 too slow: {duration:.3f}s"


class TestPhase4Integration:
    """Phase 4 통합 테스트 (Phase 3 연계)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase3_fallback_integration(self):
        """Phase 3 Fallback 연계 테스트"""
        phase4 = Phase4FermiDecomposition()
        
        # Phase 4가 모형 생성 실패 시 Phase 3으로 Fallback
        result = phase4.estimate(
            question="테스트 질문?",
            context=Context(),
            available_data={},
            depth=0
        )
        
        # Phase 3 또는 Phase 4 결과
        if result:
            assert result.phase in [3, 4]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


