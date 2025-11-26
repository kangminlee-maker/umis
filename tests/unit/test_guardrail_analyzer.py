"""
Week 4: GuardrailAnalyzer 단위 테스트 (v7.10.0)

테스트 대상:
- GuardrailAnalyzer LLM 2단계 체인
- 관계 판단 (Step 1)
- Hard/Soft 판정 (Step 2)
- Stage 1 통합
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from umis_rag.agents.estimator.guardrail_analyzer import (
    GuardrailAnalyzer, RelationshipType, AnalysisResult
)
from umis_rag.agents.estimator.models import (
    Context, EstimationResult, GuardrailCollector,
    Guardrail, GuardrailType
)


class TestGuardrailAnalyzer:
    """GuardrailAnalyzer 기본 테스트"""

    def test_init(self):
        """초기화 테스트"""
        analyzer = GuardrailAnalyzer()
        assert analyzer._llm is None  # Lazy 초기화
        assert analyzer._llm_mode is None

    def test_init_with_mode(self):
        """LLM 모드 지정 초기화"""
        analyzer = GuardrailAnalyzer(llm_mode="gpt-4o-mini")
        assert analyzer.llm_mode == "gpt-4o-mini"


class TestStep1Relationship:
    """Step 1: 관계 판단 테스트"""

    def test_upper_bound_detection(self):
        """상한 관계 감지"""
        analyzer = GuardrailAnalyzer()

        # Mock LLM 응답
        mock_response = Mock()
        mock_response.content = '{"relationship": "UPPER_BOUND", "reasoning": "부분 <= 전체"}'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            result = analyzer._step1_relationship(
                target_question="개인사업자 수는?",
                similar_question="전체 사업자 수는?"
            )

        assert result == RelationshipType.UPPER_BOUND

    def test_lower_bound_detection(self):
        """하한 관계 감지"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = '{"relationship": "LOWER_BOUND", "reasoning": "전체 >= 부분"}'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            result = analyzer._step1_relationship(
                target_question="전체 사업자 수는?",
                similar_question="개인사업자 수는?"
            )

        assert result == RelationshipType.LOWER_BOUND

    def test_unrelated_detection(self):
        """무관 관계 감지"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = '{"relationship": "UNRELATED", "reasoning": "관계 없음"}'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            result = analyzer._step1_relationship(
                target_question="커피숍 수는?",
                similar_question="자동차 수는?"
            )

        assert result == RelationshipType.UNRELATED

    def test_parsing_failure_returns_unrelated(self):
        """파싱 실패 시 UNRELATED 반환"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = 'invalid json'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            result = analyzer._step1_relationship(
                target_question="테스트",
                similar_question="테스트"
            )

        assert result == RelationshipType.UNRELATED


class TestStep2Hardness:
    """Step 2: Hard/Soft 판정 테스트"""

    def test_hard_detection(self):
        """Hard 제약 감지"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = '{"is_hard": true, "reasoning": "논리적으로 위반 불가"}'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            is_hard, reasoning = analyzer._step2_hardness(
                target_question="개인사업자 수는?",
                similar_question="경제활동인구 수는?",
                relationship=RelationshipType.UPPER_BOUND
            )

        assert is_hard is True
        assert "논리적" in reasoning

    def test_soft_detection(self):
        """Soft 제약 감지"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = '{"is_hard": false, "reasoning": "경험적으로 성립"}'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            is_hard, reasoning = analyzer._step2_hardness(
                target_question="평균 매출",
                similar_question="업계 최대 매출",
                relationship=RelationshipType.UPPER_BOUND
            )

        assert is_hard is False

    def test_parsing_failure_returns_soft(self):
        """파싱 실패 시 Soft 반환"""
        analyzer = GuardrailAnalyzer()

        mock_response = Mock()
        mock_response.content = 'invalid json'

        with patch.object(analyzer, '_get_llm') as mock_llm:
            mock_llm.return_value.invoke.return_value = mock_response

            is_hard, reasoning = analyzer._step2_hardness(
                target_question="테스트",
                similar_question="테스트",
                relationship=RelationshipType.UPPER_BOUND
            )

        assert is_hard is False
        assert "파싱 실패" in reasoning


class TestAnalyze:
    """analyze() 전체 흐름 테스트"""

    def test_analyze_returns_guardrail(self):
        """정상 분석 시 Guardrail 반환"""
        analyzer = GuardrailAnalyzer()

        # Mock Step 1: UPPER_BOUND
        # Mock Step 2: Hard
        with patch.object(analyzer, '_step1_relationship', return_value=RelationshipType.UPPER_BOUND):
            with patch.object(analyzer, '_step2_hardness', return_value=(True, "논리적 제약")):
                guardrail = analyzer.analyze(
                    target_question="개인사업자 수는?",
                    similar_question="경제활동인구 수는?",
                    similar_value=28_000_000
                )

        assert guardrail is not None
        assert guardrail.type == GuardrailType.HARD_UPPER
        assert guardrail.value == 28_000_000
        assert guardrail.confidence == 0.95
        assert guardrail.is_hard is True

    def test_analyze_returns_none_for_unrelated(self):
        """무관한 경우 None 반환"""
        analyzer = GuardrailAnalyzer()

        with patch.object(analyzer, '_step1_relationship', return_value=RelationshipType.UNRELATED):
            guardrail = analyzer.analyze(
                target_question="커피숍 수는?",
                similar_question="자동차 수는?",
                similar_value=1_000_000
            )

        assert guardrail is None

    def test_analyze_soft_lower_bound(self):
        """Soft 하한 Guardrail 생성"""
        analyzer = GuardrailAnalyzer()

        with patch.object(analyzer, '_step1_relationship', return_value=RelationshipType.LOWER_BOUND):
            with patch.object(analyzer, '_step2_hardness', return_value=(False, "경험적")):
                guardrail = analyzer.analyze(
                    target_question="전체 매출",
                    similar_question="주요 고객 매출",
                    similar_value=1_000_000
                )

        assert guardrail is not None
        assert guardrail.type == GuardrailType.SOFT_LOWER
        assert guardrail.confidence == 0.75
        assert guardrail.is_hard is False


class TestAnalyzeBatch:
    """배치 분석 테스트"""

    def test_analyze_batch(self):
        """여러 유사 데이터 배치 분석"""
        analyzer = GuardrailAnalyzer()

        mock_guardrail = Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=100000,
            confidence=0.95,
            is_hard=True,
            reasoning="테스트",
            source="Test"
        )

        with patch.object(analyzer, 'analyze', return_value=mock_guardrail):
            guardrails = analyzer.analyze_batch(
                target_question="테스트",
                similar_items=[
                    ("유사1", 100000),
                    ("유사2", 200000),
                    ("유사3", 300000)
                ]
            )

        assert len(guardrails) == 3

    def test_analyze_batch_max_guardrails(self):
        """max_guardrails 제한"""
        analyzer = GuardrailAnalyzer()

        mock_guardrail = Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=100000,
            confidence=0.95,
            is_hard=True,
            reasoning="테스트",
            source="Test"
        )

        with patch.object(analyzer, 'analyze', return_value=mock_guardrail):
            guardrails = analyzer.analyze_batch(
                target_question="테스트",
                similar_items=[("유사", i) for i in range(10)],
                max_guardrails=3
            )

        assert len(guardrails) == 3


class TestStage1Integration:
    """Stage 1 통합 테스트"""

    def test_analyze_phase2_result_cursor_mode(self):
        """Cursor 모드에서는 기존 방식 사용"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase2_result = EstimationResult(
            question="유사 데이터",
            value=100000,
            confidence=0.70,
            phase=2,
            reasoning="Validator 유사 데이터"
        )

        # Cursor 모드 (기본값) - settings.llm_mode patch
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        settings.llm_mode = "cursor"

        try:
            guardrail = estimator._analyze_phase2_result(
                question="테스트",
                phase2_result=phase2_result,
                context=Context()
            )
        finally:
            settings.llm_mode = original_mode

        assert guardrail.type == GuardrailType.EXPECTED_RANGE
        assert guardrail.value == 100000

    def test_analyze_phase2_result_external_mode(self):
        """External 모드에서는 GuardrailAnalyzer 사용 시도"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase2_result = EstimationResult(
            question="경제활동인구 수",
            value=28_000_000,
            confidence=0.70,
            phase=2,
            reasoning="통계청 데이터"
        )

        # External 모드 - settings.llm_mode patch
        from umis_rag.core.config import settings
        original_mode = settings.llm_mode
        settings.llm_mode = "gpt-4o-mini"

        try:
            # GuardrailAnalyzer가 실패해도 Fallback으로 처리됨
            guardrail = estimator._analyze_phase2_result(
                question="개인사업자 수는?",
                phase2_result=phase2_result,
                context=Context()
            )
        finally:
            settings.llm_mode = original_mode

        # Fallback 또는 GuardrailAnalyzer 결과
        assert guardrail is not None
        assert guardrail.value == 28_000_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
