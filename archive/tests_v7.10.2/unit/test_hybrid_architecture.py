"""
Week 2: Hybrid Architecture 단위 테스트 (v7.10.0)

테스트 대상:
- Stage 1: Phase 1-2 병렬 수집
- Stage 2: Phase 3-4 병렬 추정
- Stage 3: Synthesis 교차 검증
- estimate_hybrid() 전체 파이프라인
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from umis_rag.agents.estimator.models import (
    Context, EstimationResult, GuardrailCollector,
    Guardrail, GuardrailType
)


class TestStage1Collect:
    """Stage 1: 검증 & 가드레일 수집 테스트"""

    def test_fast_path_with_project_data(self):
        """Phase 0 확정값 있으면 Fast Path"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Mock _check_project_data
        mock_result = EstimationResult(
            question="직원 수는?",
            value=150,
            confidence=1.0,
            phase=0
        )

        with patch.object(estimator, '_check_project_data', return_value=mock_result):
            collector, definite = estimator._stage1_collect(
                question="직원 수는?",
                context=Context(),
                project_data={"employees": 150}
            )

        assert definite is not None
        assert definite.value == 150
        assert definite.phase == 0

    def test_parallel_phase1_phase2(self):
        """Phase 1-2 병렬 실행 확인"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Mock Phase 1 결과
        mock_phase1 = EstimationResult(
            question="ARPU는?",
            value=80000,
            confidence=0.85,  # 0.95 미만 → 확정값 아님
            phase=1
        )

        # Mock Phase 2 결과
        mock_phase2 = EstimationResult(
            question="ARPU는?",
            value=75000,
            confidence=0.70,  # Soft Guardrail로 추가
            phase=2,
            reasoning="유사 SaaS 데이터"
        )

        with patch.object(estimator.phase1, 'estimate', return_value=mock_phase1):
            with patch.object(estimator, '_search_validator', return_value=mock_phase2):
                collector, definite = estimator._stage1_collect(
                    question="B2B SaaS ARPU는?",
                    context=Context(domain="B2B_SaaS")
                )

        # 확정값 없음
        assert definite is None
        # Soft Guardrail 추가됨
        assert len(collector.soft_guardrails) == 1
        assert collector.soft_guardrails[0].value == 75000


class TestStage2Estimate:
    """Stage 2: 병렬 추정 테스트"""

    def test_parallel_phase3_phase4(self):
        """Phase 3-4 병렬 실행 확인 (API 모드)"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG
        from umis_rag.core.config import settings

        estimator = EstimatorRAG()

        # Mock Phase 3 결과
        mock_phase3 = EstimationResult(
            question="서울 음식점 수는?",
            value=100000,
            value_range=(80000, 120000),
            confidence=0.85,
            phase=3
        )

        # Mock Phase 4 결과
        mock_phase4 = EstimationResult(
            question="서울 음식점 수는?",
            value=95000,
            confidence=0.80,
            phase=4,
            decomposition=Mock(formula="인구 * 밀도")
        )

        estimator._ensure_phase3_initialized()
        estimator._ensure_phase4_initialized()

        # API 모드로 전환하여 Phase 3-4 병렬 실행 테스트
        original_mode = settings.llm_mode
        settings.llm_mode = "gpt-4o-mini"

        try:
            with patch.object(estimator.phase3, 'estimate', return_value=mock_phase3):
                with patch.object(estimator.phase4, 'estimate', return_value=mock_phase4):
                    phase3_result, phase4_result = estimator._stage2_estimate(
                        question="서울 음식점 수는?",
                        context=Context(region="서울"),
                        collector=GuardrailCollector()
                    )
        finally:
            settings.llm_mode = original_mode

        assert phase3_result is not None
        assert phase3_result.value_range == (80000, 120000)
        assert phase4_result is not None
        assert phase4_result.value == 95000

    def test_cursor_mode_phase3_only(self):
        """Cursor 모드에서는 Phase 3만 실행"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG
        from umis_rag.core.config import settings

        estimator = EstimatorRAG()

        mock_phase3 = EstimationResult(
            question="테스트",
            value=100000,
            confidence=0.85,
            phase=3
        )

        estimator._ensure_phase3_initialized()
        estimator._ensure_phase4_initialized()

        # Cursor 모드 확인
        original_mode = settings.llm_mode
        settings.llm_mode = "cursor"

        try:
            with patch.object(estimator.phase3, 'estimate', return_value=mock_phase3):
                phase3_result, phase4_result = estimator._stage2_estimate(
                    question="테스트",
                    context=Context(),
                    collector=GuardrailCollector()
                )
        finally:
            settings.llm_mode = original_mode

        # Cursor 모드에서는 Phase 3만 실행
        assert phase3_result is not None
        assert phase3_result.value == 100000
        assert phase4_result is None  # Phase 4는 실행 안 됨


class TestStage3Synthesize:
    """Stage 3: Synthesis 교차 검증 테스트"""

    def test_cross_validation_success(self):
        """교차 검증 성공 시 신뢰도 +15%"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase3 = EstimationResult(
            question="서울 음식점 수는?",
            value=100000,
            value_range=(80000, 120000),  # Range
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="서울 음식점 수는?",
            value=95000,  # Range 내에 있음!
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="서울 음식점 수는?",
            context=Context(region="서울"),
            collector=GuardrailCollector(),
            phase3_result=phase3,
            phase4_result=phase4
        )

        # 교차 검증 성공 → +0.15
        assert result.confidence == pytest.approx(0.95, rel=1e-6)  # 0.80 + 0.15
        # Weighted Fusion 적용으로 값이 약간 변경됨 (P3:0.85, P4:0.80 가중평균)
        # (100000 * 0.85 + 95000 * 0.80) / (0.85 + 0.80) = 97575.76
        assert result.value == pytest.approx(97575.76, rel=1e-3)
        assert result.value_range == (80000, 120000)
        assert "Cross=True" in result.reasoning

    def test_cross_validation_failure(self):
        """교차 검증 실패 시 신뢰도 보너스 없음"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase3 = EstimationResult(
            question="서울 음식점 수는?",
            value=100000,
            value_range=(80000, 120000),
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="서울 음식점 수는?",
            value=150000,  # Range 밖!
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="서울 음식점 수는?",
            context=Context(region="서울"),
            collector=GuardrailCollector(),
            phase3_result=phase3,
            phase4_result=phase4
        )

        # 교차 검증 실패 → 보너스 없음
        assert result.confidence == 0.80
        assert "Cross=False" in result.reasoning

    def test_hard_guardrail_applied(self):
        """Hard Guardrail 적용 확인"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Hard Upper Guardrail 설정
        collector = GuardrailCollector()
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=100000,
            confidence=0.95,
            is_hard=True,
            reasoning="최대값 제한",
            source="Test"
        ))

        phase3 = EstimationResult(
            question="테스트",
            value=90000,
            value_range=(80000, 100000),
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="테스트",
            value=150000,  # Hard 상한 초과!
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="테스트",
            context=Context(),
            collector=collector,
            phase3_result=phase3,
            phase4_result=phase4
        )

        # Hard 상한 적용됨
        assert result.value == 100000


class TestEstimateHybrid:
    """estimate_hybrid() 전체 파이프라인 테스트"""

    def test_fast_path_returns_immediately(self):
        """확정값 있으면 Stage 2-3 스킵"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Mock Phase 0 확정값
        mock_result = EstimationResult(
            question="직원 수는?",
            value=150,
            confidence=1.0,
            phase=0
        )

        with patch.object(estimator, '_check_project_data', return_value=mock_result):
            result = estimator.estimate_hybrid(
                question="직원 수는?",
                project_data={"employees": 150}
            )

        assert result.value == 150
        assert result.phase == 0

    def test_full_pipeline_execution(self):
        """전체 파이프라인 실행 (Stage 1-2-3, API 모드)"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG
        from umis_rag.core.config import settings

        estimator = EstimatorRAG()

        # API 모드로 전환
        original_mode = settings.llm_mode
        settings.llm_mode = "gpt-4o-mini"

        try:
            # Stage 1: 확정값 없음
            with patch.object(estimator.phase1, 'estimate', return_value=None):
                with patch.object(estimator, '_search_validator', return_value=None):
                    # Stage 2: Mock 결과
                    mock_phase3 = EstimationResult(
                        question="테스트",
                        value=100000,
                        value_range=(80000, 120000),
                        confidence=0.85,
                        phase=3
                    )
                    mock_phase4 = EstimationResult(
                        question="테스트",
                        value=95000,
                        confidence=0.80,
                        phase=4
                    )

                    estimator._ensure_phase3_initialized()
                    estimator._ensure_phase4_initialized()

                    with patch.object(estimator.phase3, 'estimate', return_value=mock_phase3):
                        with patch.object(estimator.phase4, 'estimate', return_value=mock_phase4):
                            result = estimator.estimate_hybrid(
                                question="테스트 질문",
                                domain="General"
                            )
        finally:
            settings.llm_mode = original_mode

        # Synthesis 결과 (Weighted Fusion 적용)
        assert result.value == pytest.approx(97575.76, rel=1e-3)
        assert result.value_range == (80000, 120000)
        assert result.confidence == pytest.approx(0.95, rel=1e-6)  # 교차 검증 성공


class TestEnhancedSynthesis:
    """Week 3: Enhanced Synthesis 테스트"""

    def test_soft_guardrail_bonus(self):
        """Soft Guardrail 일치 시 +5% 보너스"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Soft Guardrail 추가
        collector = GuardrailCollector()
        collector.add_guardrail(Guardrail(
            type=GuardrailType.EXPECTED_RANGE,
            value=95000,  # Phase 4 값과 근접 (20% 이내)
            confidence=0.70,
            is_hard=False,
            reasoning="예상 범위",
            source="Test"
        ))

        phase3 = EstimationResult(
            question="테스트",
            value=100000,
            value_range=(80000, 120000),
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="테스트",
            value=95000,  # Soft Guardrail과 일치!
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="테스트",
            context=Context(),
            collector=collector,
            phase3_result=phase3,
            phase4_result=phase4
        )

        # Cross-Validation +0.15, Soft +0.05 = 0.80 + 0.20 = 1.00 → 0.99 (cap)
        assert result.confidence == pytest.approx(0.99, rel=1e-6)

    def test_soft_guardrail_penalty(self):
        """Soft Guardrail 불일치 시 -10% 페널티"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Soft Guardrail 추가 (값과 불일치)
        collector = GuardrailCollector()
        collector.add_guardrail(Guardrail(
            type=GuardrailType.SOFT_UPPER,
            value=50000,  # Phase 4 값 (95000) 보다 작음 → 불일치
            confidence=0.70,
            is_hard=False,
            reasoning="상한 제안",
            source="Test"
        ))

        phase3 = EstimationResult(
            question="테스트",
            value=100000,
            value_range=(80000, 120000),
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="테스트",
            value=95000,  # Soft Upper(50000)보다 큼 → 불일치
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="테스트",
            context=Context(),
            collector=collector,
            phase3_result=phase3,
            phase4_result=phase4
        )

        # Cross-Validation +0.15, Soft -0.10 = 0.80 + 0.05 = 0.85
        assert result.confidence == pytest.approx(0.85, rel=1e-6)

    def test_uncertainty_calculation(self):
        """95% CI 및 Uncertainty 계산 확인"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase3 = EstimationResult(
            question="테스트",
            value=100000,
            value_range=(80000, 120000),  # Range width = 40000
            confidence=0.85,
            phase=3
        )

        phase4 = EstimationResult(
            question="테스트",
            value=100000,
            confidence=0.80,
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="테스트",
            context=Context(),
            collector=GuardrailCollector(),
            phase3_result=phase3,
            phase4_result=phase4
        )

        # Uncertainty 계산: range_width / (2 * value) = 40000 / 200000 = 0.2
        assert result.uncertainty == pytest.approx(0.2, rel=0.1)

        # 95% CI 계산 확인
        ci_info = result.reasoning_detail['steps']['confidence_interval']
        assert ci_info['ci_95_lower'] is not None
        assert ci_info['ci_95_upper'] is not None
        assert ci_info['ci_95_lower'] < result.value < ci_info['ci_95_upper']

    def test_weighted_fusion_applied(self):
        """Weighted Fusion 적용 확인"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        phase3 = EstimationResult(
            question="테스트",
            value=100000,  # Range 중앙값
            value_range=(80000, 120000),
            confidence=0.90,  # 높은 confidence
            phase=3
        )

        phase4 = EstimationResult(
            question="테스트",
            value=95000,
            confidence=0.80,  # 낮은 confidence
            phase=4
        )

        result = estimator._stage3_synthesize(
            question="테스트",
            context=Context(),
            collector=GuardrailCollector(),
            phase3_result=phase3,
            phase4_result=phase4
        )

        # Weighted: (100000 * 0.90 + 95000 * 0.80) / (0.90 + 0.80) = 97647.06
        expected_value = (100000 * 0.90 + 95000 * 0.80) / (0.90 + 0.80)
        assert result.value == pytest.approx(expected_value, rel=1e-3)

        # reasoning_detail에 가중치 정보 포함
        fusion_info = result.reasoning_detail['steps']['weighted_fusion']
        assert fusion_info['phase3_weight'] == 0.90
        assert fusion_info['phase4_weight'] == 0.80


class TestPerformance:
    """성능 테스트"""

    def test_parallel_faster_than_sequential(self):
        """병렬 실행이 순차보다 빠른지 확인"""
        from umis_rag.agents.estimator.estimator import EstimatorRAG

        estimator = EstimatorRAG()

        # Mock: 각 Phase가 0.5초 걸림
        def slow_phase1(*args):
            time.sleep(0.3)
            return None

        def slow_phase2(*args):
            time.sleep(0.3)
            return None

        with patch.object(estimator.phase1, 'estimate', side_effect=slow_phase1):
            with patch.object(estimator, '_search_validator', side_effect=slow_phase2):
                start = time.time()
                collector, definite = estimator._stage1_collect(
                    question="테스트",
                    context=Context()
                )
                elapsed = time.time() - start

        # 병렬: ~0.3초, 순차: ~0.6초
        # 병렬이므로 0.5초 미만이어야 함
        assert elapsed < 0.5, f"병렬 실행 시간 초과: {elapsed:.2f}초"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
