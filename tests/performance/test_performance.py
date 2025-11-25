"""
성능 테스트 (v7.9.0)

목표:
- Phase별 속도 측정 및 검증
- 목표: Phase 0-2 <1초, Phase 3 <5초, Phase 4 <10초
- 배치 추정 성능 검증
- 메모리 사용량 모니터링

작성일: 2025-11-25
"""

import os
import time
import pytest
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context, EstimationResult


class TestPhaseSpeed:
    """Phase별 속도 테스트"""
    
    def test_phase0_speed(self):
        """Phase 0 속도 (<0.1초 목표)"""
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="churn rate는?",  # 키워드 매칭
            project_data={'churn_rate': 0.05}
        )
        duration = time.time() - start
        
        if result.phase == 0:
            assert duration < 0.1, f"Phase 0 too slow: {duration:.3f}s (목표: <0.1s)"
            print(f"  Phase 0: {duration:.3f}s ✅")
        else:
            print(f"  Phase 0 매칭 실패 → Phase {result.phase}")
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase2_speed(self):
        """Phase 2 속도 (<1초 목표)"""
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="B2B SaaS ARPU는?",
            context=Context(domain='B2B_SaaS')
        )
        duration = time.time() - start
        
        # v7.9.0: Phase 2 임계값 강화로 Phase 3로 넘어갈 가능성
        if result.phase == 2:
            assert duration < 1.0, f"Phase 2 too slow: {duration:.3f}s (목표: <1s)"
            print(f"  Phase 2: {duration:.3f}s ✅")
        else:
            print(f"  Phase 2 스킵 → Phase {result.phase} ({duration:.3f}s)")
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase3_speed(self):
        """Phase 3 속도 (<5초 목표)"""
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="2025년 AI 챗봇 ARPU는?",
            context=Context(domain='AI_Chatbot')
        )
        duration = time.time() - start
        
        if result.phase == 3:
            assert duration < 5.0, f"Phase 3 too slow: {duration:.3f}s (목표: <5s)"
            print(f"  Phase 3: {duration:.3f}s ✅")
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_phase4_speed_simple(self):
        """Phase 4 속도 - 단순 모형 (<10초 목표)"""
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="서울 음식점 수는?",
            context=Context(region='서울')
        )
        duration = time.time() - start
        
        if result.phase == 4:
            # 단순 모형은 10초 이내
            assert duration < 10.0, f"Phase 4 too slow: {duration:.3f}s (목표: <10s)"
            print(f"  Phase 4 (단순): {duration:.3f}s ✅")


class TestBatchEstimation:
    """배치 추정 성능 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_batch_5_questions(self):
        """5개 질문 배치 추정"""
        estimator = EstimatorRAG()
        
        questions = [
            ("churn_rate", {"churn_rate": 0.05}),
            ("arpu", {"arpu": 50000}),
            ("ltv", {"ltv": 1000000}),
            ("B2B SaaS ARPU는?", {}),
            ("AI 챗봇 ARPU는?", {}),
        ]
        
        start = time.time()
        results = []
        
        for question, project_data in questions:
            result = estimator.estimate(
                question=question,
                project_data=project_data
            )
            results.append(result)
        
        duration = time.time() - start
        
        # 모든 결과 유효
        assert len(results) == 5
        for result in results:
            assert isinstance(result, EstimationResult)
        
        # 평균 속도
        avg_duration = duration / len(questions)
        print(f"  배치 5개: 총 {duration:.2f}s, 평균 {avg_duration:.2f}s")
        
        # 평균 5초 이내 (Phase 0-3 혼합)
        assert avg_duration < 5.0, f"Batch too slow: {avg_duration:.3f}s/question"
    
    def test_batch_phase0_only(self):
        """Phase 0만 사용 (빠른 배치)"""
        estimator = EstimatorRAG()
        
        questions = [
            ("churn_rate", {"churn_rate": 0.05}),
            ("arpu", {"arpu": 50000}),
            ("ltv", {"ltv": 1000000}),
            ("users", {"users": 10000}),
            ("revenue", {"revenue": 5000000}),
        ]
        
        start = time.time()
        results = []
        
        for question, project_data in questions:
            result = estimator.estimate(
                question=question,
                project_data=project_data
            )
            results.append(result)
        
        duration = time.time() - start
        
        # Phase 0만 사용하면 매우 빨라야 함
        print(f"  Phase 0 배치 5개: {duration:.3f}s")
        
        # Phase 0 성공한 것들만 체크
        phase0_count = sum(1 for r in results if r.phase == 0)
        if phase0_count > 0:
            # Phase 0는 평균 2초 이내 (초기화 포함)
            avg_phase0 = duration / phase0_count
            assert avg_phase0 < 2.0, f"Phase 0 batch too slow: {avg_phase0:.3f}s"


class TestExecutionTimeTracking:
    """실행 시간 추적 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_execution_time_accuracy(self):
        """execution_time 정확도"""
        estimator = EstimatorRAG()
        
        start = time.time()
        result = estimator.estimate(
            question="AI 챗봇 ARPU?",
            context=Context(domain='AI_Chatbot')
        )
        actual_duration = time.time() - start
        
        # EstimationResult.execution_time이 실제 시간과 유사해야 함
        if result.execution_time > 0:
            diff = abs(result.execution_time - actual_duration)
            assert diff < 0.5, f"Execution time mismatch: {diff:.3f}s"
            print(f"  측정: {actual_duration:.3f}s, 기록: {result.execution_time:.3f}s")


class TestMemoryUsage:
    """메모리 사용량 테스트"""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OpenAI API key required"
    )
    def test_memory_leak_prevention(self):
        """메모리 누수 방지"""
        import gc
        import sys
        
        estimator = EstimatorRAG()
        
        # 초기 메모리
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # 10회 추정
        for i in range(10):
            result = estimator.estimate(
                question=f"test_{i}",
                project_data={f"test_{i}": i}
            )
            assert isinstance(result, EstimationResult)
        
        # 가비지 컬렉션
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # 객체 증가량 확인 (심각한 누수 방지)
        growth = final_objects - initial_objects
        print(f"  객체 증가: {growth}")
        
        # 10회 추정 후 객체 1000개 이하 증가
        assert growth < 1000, f"Memory leak suspected: {growth} objects"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


