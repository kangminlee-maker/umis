"""
엣지 케이스 테스트 (v7.9.0)

목표:
- 예외 상황 및 경계 조건 검증
- 빈 질문, 긴 질문 처리
- 특수문자, 다국어 처리
- 수치 경계값 (0, 음수, 매우 큰 수)
- 동시성 테스트

작성일: 2025-11-25
"""

import os
import pytest
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context, EstimationResult


class TestEmptyAndLongQuestions:
    """빈 질문 및 긴 질문 테스트"""
    
    def test_empty_question(self):
        """빈 질문 처리"""
        estimator = EstimatorRAG()
        
        try:
            result = estimator.estimate(question="")
            # 에러 없이 처리되면 검증
            assert isinstance(result, EstimationResult)
            # 실패 가능
            if not result.is_successful():
                assert result.phase == -1
        except (ValueError, TypeError):
            # 에러 발생도 허용
            pass
    
    def test_whitespace_only_question(self):
        """공백만 있는 질문"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(question="   ")
        
        # 에러 없이 처리
        assert isinstance(result, EstimationResult)
    
    def test_very_long_question(self):
        """매우 긴 질문 (토큰 제한 테스트)"""
        estimator = EstimatorRAG()
        
        # 1000자 이상 질문
        long_question = "서울에 있는 " + "매우 " * 500 + "큰 시장의 규모는?"
        
        result = estimator.estimate(
            question=long_question,
            context=Context()
        )
        
        # 에러 없이 처리 (토큰 제한 초과 가능)
        assert isinstance(result, EstimationResult)
    
    def test_single_word_question(self):
        """단어 하나만 있는 질문"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(question="ARPU")
        
        # 단어만으로도 처리
        assert isinstance(result, EstimationResult)


class TestSpecialCharacters:
    """특수문자 테스트"""
    
    def test_special_chars_parentheses(self):
        """괄호 포함"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS ARPU는? (단위: 원)",
            context=Context(domain='B2B_SaaS')
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_special_chars_symbols(self):
        """특수 기호 포함"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="ARPU @ 2024년 = ?",
            context=Context()
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_special_chars_emoji(self):
        """이모지 포함"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="🍕 피자 시장 규모는? 📈",
            context=Context()
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_special_chars_math_symbols(self):
        """수학 기호 포함"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="ARPU ≈ 얼마?",
            context=Context()
        )
        
        assert isinstance(result, EstimationResult)


class TestMultilingual:
    """다국어 테스트"""
    
    def test_english_question(self):
        """영어 질문"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="What is the average ARPU of B2B SaaS?",
            context=Context(domain='B2B_SaaS')
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_korean_question(self):
        """한국어 질문"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS의 평균 ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_mixed_language(self):
        """혼합 언어"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="B2B SaaS average ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        
        assert isinstance(result, EstimationResult)


class TestNumericalBoundaries:
    """수치 경계값 테스트"""
    
    def test_zero_value(self):
        """0 값 처리"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="zero_value",
            project_data={'zero_value': 0}
        )
        
        # 0도 유효한 값
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == 0
    
    def test_negative_value(self):
        """음수 값 처리"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="negative_value",
            project_data={'negative_value': -100}
        )
        
        # 음수도 유효한 값 (예: 손실)
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == -100
    
    def test_very_large_value(self):
        """매우 큰 값 처리"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="large_value",
            project_data={'large_value': 1e15}  # 1조
        )
        
        # 큰 값도 처리
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == 1e15
    
    def test_very_small_value(self):
        """매우 작은 값 처리"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="small_value",
            project_data={'small_value': 0.000001}
        )
        
        # 작은 값도 처리
        assert isinstance(result, EstimationResult)
        if result.phase == 0:
            assert result.value == 0.000001


class TestConcurrentEstimation:
    """동시 추정 테스트 (스레드 안전성)"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_sequential_estimation(self):
        """순차 추정"""
        estimator = EstimatorRAG()
        
        questions = [
            "employees",
            "revenue",
            "customers"
        ]
        
        results = []
        for q in questions:
            result = estimator.estimate(
                question=q,
                project_data={q: 100}
            )
            results.append(result)
        
        # 모든 결과가 유효
        assert len(results) == 3
        for result in results:
            assert isinstance(result, EstimationResult)


class TestContextVariations:
    """다양한 Context 테스트"""
    
    def test_minimal_context(self):
        """최소 Context"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="ARPU?",
            context=Context()  # domain=General
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_full_context(self):
        """전체 Context"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="ARPU?",
            context=Context(
                domain='B2B_SaaS',
                region='한국',
                time_period='2024'
            )
        )
        
        assert isinstance(result, EstimationResult)
    
    def test_none_context(self):
        """None Context"""
        estimator = EstimatorRAG()
        
        result = estimator.estimate(
            question="ARPU?",
            context=None
        )
        
        # None context도 처리 (기본 Context 생성)
        assert isinstance(result, EstimationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])





