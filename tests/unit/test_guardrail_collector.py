"""
GuardrailCollector 단위 테스트 (v7.10.0)
"""

import pytest
from umis_rag.agents.estimator.models import (
    GuardrailType, Guardrail, GuardrailCollector, EstimationResult
)


class TestGuardrailCollector:
    """GuardrailCollector 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        collector = GuardrailCollector()
        assert len(collector.definite_values) == 0
        assert len(collector.hard_guardrails) == 0
        assert len(collector.soft_guardrails) == 0
    
    def test_add_definite_value(self):
        """확정값 추가 테스트"""
        collector = GuardrailCollector()
        
        result = EstimationResult(
            question="test",
            value=100.0,
            confidence=1.0,
            phase=0
        )
        
        collector.add_definite(result)
        assert len(collector.definite_values) == 1
        assert collector.has_definite_value()
    
    def test_add_definite_ignores_low_confidence(self):
        """낮은 신뢰도는 무시"""
        collector = GuardrailCollector()
        
        result = EstimationResult(
            question="test",
            value=100.0,
            confidence=0.8,  # < 1.0
            phase=3
        )
        
        collector.add_definite(result)
        assert len(collector.definite_values) == 0
    
    def test_add_hard_guardrail(self):
        """Hard Guardrail 추가 테스트"""
        collector = GuardrailCollector()
        
        guard = Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=1000.0,
            confidence=0.95,
            is_hard=True,
            reasoning="논리적 상한",
            source="Validator"
        )
        
        collector.add_guardrail(guard)
        assert len(collector.hard_guardrails) == 1
        assert len(collector.soft_guardrails) == 0
    
    def test_add_soft_guardrail(self):
        """Soft Guardrail 추가 테스트"""
        collector = GuardrailCollector()
        
        guard = Guardrail(
            type=GuardrailType.SOFT_UPPER,
            value=800.0,
            confidence=0.70,
            is_hard=False,
            reasoning="경험적 상한",
            source="Phase1"
        )
        
        collector.add_guardrail(guard)
        assert len(collector.hard_guardrails) == 0
        assert len(collector.soft_guardrails) == 1
    
    def test_get_hard_bounds_empty(self):
        """Empty Bounds 테스트"""
        collector = GuardrailCollector()
        bounds = collector.get_hard_bounds()
        
        assert bounds['min'] == 0.0
        assert bounds['max'] == float('inf')
    
    def test_get_hard_bounds_upper_only(self):
        """상한만 있는 경우"""
        collector = GuardrailCollector()
        
        guard = Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=1000.0,
            confidence=0.95,
            is_hard=True,
            reasoning="상한",
            source="Validator"
        )
        
        collector.add_guardrail(guard)
        bounds = collector.get_hard_bounds()
        
        assert bounds['min'] == 0.0
        assert bounds['max'] == 1000.0
    
    def test_get_hard_bounds_lower_only(self):
        """하한만 있는 경우"""
        collector = GuardrailCollector()
        
        guard = Guardrail(
            type=GuardrailType.HARD_LOWER,
            value=100.0,
            confidence=0.95,
            is_hard=True,
            reasoning="하한",
            source="Phase0"
        )
        
        collector.add_guardrail(guard)
        bounds = collector.get_hard_bounds()
        
        assert bounds['min'] == 100.0
        assert bounds['max'] == float('inf')
    
    def test_get_hard_bounds_multiple(self):
        """여러 Guardrails"""
        collector = GuardrailCollector()
        
        # 하한 2개 (더 높은 것 선택)
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_LOWER,
            value=100.0,
            confidence=0.95,
            is_hard=True,
            reasoning="하한1",
            source="Phase0"
        ))
        
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_LOWER,
            value=200.0,
            confidence=0.95,
            is_hard=True,
            reasoning="하한2",
            source="Phase1"
        ))
        
        # 상한 2개 (더 낮은 것 선택)
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=1000.0,
            confidence=0.95,
            is_hard=True,
            reasoning="상한1",
            source="Validator"
        ))
        
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=800.0,
            confidence=0.95,
            is_hard=True,
            reasoning="상한2",
            source="Phase2"
        ))
        
        bounds = collector.get_hard_bounds()
        
        assert bounds['min'] == 200.0  # max(100, 200)
        assert bounds['max'] == 800.0  # min(1000, 800)
    
    def test_get_best_definite(self):
        """최고 확정값 선택"""
        collector = GuardrailCollector()
        
        # Phase 2 (나중)
        collector.add_definite(EstimationResult(
            question="test",
            value=100.0,
            confidence=1.0,
            phase=2
        ))
        
        # Phase 0 (먼저, 우선순위 높음)
        collector.add_definite(EstimationResult(
            question="test",
            value=200.0,
            confidence=1.0,
            phase=0
        ))
        
        best = collector.get_best_definite()
        assert best.value == 200.0
        assert best.phase == 0
    
    def test_summary(self):
        """요약 테스트"""
        collector = GuardrailCollector()
        
        collector.add_definite(EstimationResult(
            question="test",
            value=100.0,
            confidence=1.0,
            phase=0
        ))
        
        collector.add_guardrail(Guardrail(
            type=GuardrailType.HARD_UPPER,
            value=1000.0,
            confidence=0.95,
            is_hard=True,
            reasoning="상한",
            source="Validator"
        ))
        
        collector.add_guardrail(Guardrail(
            type=GuardrailType.SOFT_LOWER,
            value=50.0,
            confidence=0.70,
            is_hard=False,
            reasoning="경험적 하한",
            source="Phase1"
        ))
        
        summary = collector.summary()
        
        assert summary['definite_count'] == 1
        assert summary['hard_guardrails'] == 1
        assert summary['soft_guardrails'] == 1
        assert summary['has_fast_path'] == True
        assert summary['hard_bounds']['max'] == 1000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
