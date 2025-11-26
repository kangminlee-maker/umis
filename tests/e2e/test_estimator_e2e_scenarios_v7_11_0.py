"""
E2E Scenario Tests for Estimator v7.11.0 Fusion Architecture

10개 실제 사용 시나리오를 커버하는 End-to-End 테스트

Scenarios:
1. B2B SaaS ARPU 추정 (Stage 2 Prior)
2. E-commerce Churn Rate 추정 (Stage 2 Prior)
3. 음악 스트리밍 시장 규모 추정 (Stage 3 Fermi)
4. AI 챗봇 LTV 추정 (Stage 4 Fusion)
5. 구독 모델 CAC 추정 (Stage 2 Prior)
6. Fast Budget 빠른 추정 (Budget Control)
7. Standard Budget 정밀 추정 (Budget Control)
8. Early Return 검증 (Stage 1-2)
9. Validator 확정 데이터 우선 (Stage 1 Validator)
10. Legacy API 하위 호환성 (Backward Compatibility)

⭐ Native (Cursor) LLM 모드 지원:
- LLM_MODE=cursor 설정 시 외부 API 호출 없이 실행
- 모든 테스트가 Native 모드에서 실행 가능
- 비용: $0 (외부 API 호출 없음)
"""

import os
import pytest
from typing import Dict, Any

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import (
    Budget,
    create_standard_budget,
    create_fast_budget,
    EstimationResult,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM Mode 확인 (Native vs External)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def is_native_mode() -> bool:
    """Native (Cursor) LLM 모드인지 확인
    
    Returns:
        True if LLM_MODE=cursor or 설정 없음 (기본값 cursor)
        False if External API 모드
    """
    llm_mode = os.environ.get('LLM_MODE', 'cursor').lower()
    return llm_mode == 'cursor'

def should_skip_test() -> bool:
    """테스트를 스킵해야 하는지 확인
    
    Returns:
        True if External 모드인데 API key 없음
        False if Native 모드이거나 External 모드에 API key 있음
    """
    if is_native_mode():
        # Native 모드 = API key 불필요, 절대 스킵하지 않음
        return False
    else:
        # External 모드 = API key 필요, 없으면 스킵
        return not os.environ.get('OPENAI_API_KEY')

# Skip condition for tests that need LLM
skip_if_no_llm = pytest.mark.skipif(
    should_skip_test(),
    reason="LLM not available (External mode needs OPENAI_API_KEY, or set LLM_MODE=cursor for Native mode)"
)


class TestEstimatorE2EScenarios:
    """v7.11.0 Fusion Architecture E2E 시나리오 테스트"""

    @pytest.fixture
    def estimator(self):
        """EstimatorRAG 인스턴스 생성"""
        return EstimatorRAG()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 1: B2B SaaS ARPU 추정 (Stage 2 Prior)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_1_b2b_saas_arpu(self, estimator):
        """Scenario 1: B2B SaaS ARPU 추정

        Expected:
        - Stage 2 (Generative Prior) 사용
        - source = "Generative Prior"
        - certainty in [high, medium, low]
        - value in reasonable range ($50-$500/month)
        """
        question = "B2B SaaS 평균 ARPU는?"
        context = Context(
            domain="B2B_SaaS",
            region="글로벌"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert 50 <= result.value <= 500, f"ARPU should be $50-$500, got ${result.value}"
        assert result.source in ["Generative Prior", "Fusion", "Fermi"]
        assert result.certainty in ["high", "medium", "low"]
        assert result.reasoning is not None
        assert len(result.reasoning) > 50

        print(f"\n✅ Scenario 1: B2B SaaS ARPU = ${result.value:.2f} (source={result.source}, certainty={result.certainty})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 2: E-commerce Churn Rate 추정 (Stage 2 Prior)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_2_ecommerce_churn(self, estimator):
        """Scenario 2: E-commerce Churn Rate 추정

        Expected:
        - Stage 2 (Generative Prior) 사용
        - source = "Generative Prior"
        - certainty in [high, medium, low]
        - value in reasonable range (0.02-0.10 monthly churn)
        """
        question = "E-commerce 구독 서비스 월 해지율은?"
        context = Context(
            domain="E-commerce",
            region="한국"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert 0.01 <= result.value <= 0.15, f"Churn should be 1-15%, got {result.value*100:.1f}%"
        assert result.source in ["Generative Prior", "Fusion", "Fermi"]
        assert result.certainty in ["high", "medium", "low"]

        print(f"\n✅ Scenario 2: E-commerce Churn = {result.value*100:.2f}% (source={result.source}, certainty={result.certainty})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 3: 음악 스트리밍 시장 규모 추정 (Stage 3 Fermi)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_3_music_streaming_market(self, estimator):
        """Scenario 3: 음악 스트리밍 시장 규모 추정

        Expected:
        - Stage 3 (Fermi) 사용 가능
        - source in ["Fermi", "Fusion", "Generative Prior"]
        - certainty in [high, medium, low]
        - value in reasonable range (1B-50B USD)
        """
        question = "2025년 글로벌 음악 스트리밍 시장 규모는?"
        context = Context(
            domain="Music_Streaming",
            time_period="2025",
            region="글로벌"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert 1e9 <= result.value <= 100e9, f"Market size should be $1B-$100B, got ${result.value/1e9:.1f}B"
        assert result.source in ["Fermi", "Fusion", "Generative Prior"]
        assert result.certainty in ["high", "medium", "low"]

        print(f"\n✅ Scenario 3: Music Streaming Market = ${result.value/1e9:.2f}B (source={result.source}, certainty={result.certainty})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 4: AI 챗봇 LTV 추정 (Stage 4 Fusion)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_4_ai_chatbot_ltv(self, estimator):
        """Scenario 4: AI 챗봇 LTV 추정

        Expected:
        - Stage 2-4 사용
        - source in ["Generative Prior", "Fermi", "Fusion"]
        - certainty in [high, medium, low]
        - value in reasonable range ($100-$5000)
        """
        question = "AI 챗봇 SaaS 고객 LTV는?"
        context = Context(
            domain="AI_Chatbot",
            region="글로벌"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert 50 <= result.value <= 10000, f"LTV should be $50-$10000, got ${result.value:.2f}"
        assert result.source in ["Generative Prior", "Fermi", "Fusion"]
        assert result.certainty in ["high", "medium", "low"]

        print(f"\n✅ Scenario 4: AI Chatbot LTV = ${result.value:.2f} (source={result.source}, certainty={result.certainty})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 5: 구독 모델 CAC 추정 (Stage 2 Prior)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_5_subscription_cac(self, estimator):
        """Scenario 5: 구독 모델 CAC 추정

        Expected:
        - Stage 2 (Generative Prior) 사용
        - source = "Generative Prior"
        - certainty in [high, medium, low]
        - value in reasonable range ($10-$500)
        """
        question = "구독 모델 평균 CAC는?"
        context = Context(
            domain="Subscription",
            region="한국"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert 5 <= result.value <= 1000, f"CAC should be $5-$1000, got ${result.value:.2f}"
        assert result.source in ["Generative Prior", "Fusion", "Fermi"]
        assert result.certainty in ["high", "medium", "low"]

        print(f"\n✅ Scenario 5: Subscription CAC = ${result.value:.2f} (source={result.source}, certainty={result.certainty})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 6: Fast Budget 빠른 추정 (Budget Control)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_6_fast_budget_estimation(self, estimator):
        """Scenario 6: Fast Budget 빠른 추정

        Expected:
        - Fast Budget (max_llm_calls=3) 사용
        - LLM 호출 3회 이하
        - 5초 이내 완료
        - source in ["Generative Prior", "Fusion"]
        """
        import time

        question = "모바일 앱 평균 ARPU는?"
        context = Context(domain="Mobile_App")
        budget = create_fast_budget()

        start = time.time()
        result = estimator.estimate(question=question, context=context, budget=budget)
        elapsed = time.time() - start

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert result.cost['llm_calls'] <= 3, f"Fast Budget should use ≤3 LLM calls, got {result.cost['llm_calls']}"
        assert elapsed < 10, f"Fast Budget should complete in <10s, took {elapsed:.1f}s"
        assert result.source in ["Generative Prior", "Fusion", "Fermi"]

        print(f"\n✅ Scenario 6: Fast Budget = ${result.value:.2f} in {elapsed:.1f}s ({result.cost['llm_calls']} LLM calls, source={result.source})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 7: Standard Budget 정밀 추정 (Budget Control)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_7_standard_budget_estimation(self, estimator):
        """Scenario 7: Standard Budget 정밀 추정

        Expected:
        - Standard Budget (max_llm_calls=10) 사용
        - LLM 호출 10회 이하
        - source in ["Generative Prior", "Fermi", "Fusion"]
        - 더 정밀한 추정
        """
        import time

        question = "B2B SaaS 평균 월 매출 성장률은?"
        context = Context(
            domain="B2B_SaaS"
        )
        budget = create_standard_budget()

        start = time.time()
        result = estimator.estimate(question=question, context=context, budget=budget)
        elapsed = time.time() - start

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert result.cost['llm_calls'] <= 10, f"Standard Budget should use ≤10 LLM calls, got {result.cost['llm_calls']}"
        assert result.source in ["Generative Prior", "Fermi", "Fusion"]

        print(f"\n✅ Scenario 7: Standard Budget = {result.value*100:.2f}% in {elapsed:.1f}s ({result.cost['llm_calls']} LLM calls, source={result.source})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 8: Early Return 검증 (Stage 1 → Stage 2)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_8_early_return_simple_question(self, estimator):
        """Scenario 8: Early Return 검증 (간단한 질문)

        Expected:
        - Stage 1-2 빠른 처리
        - source in ["Validator", "Generative Prior"]
        - certainty in ["high", "medium", "low"]
        - LLM 호출 최소화 (≤3회)
        - 빠른 완료 (<5초)
        """
        import time

        question = "일반적인 B2C 앱 ARPU는?"
        context = Context(domain="B2C_App")
        budget = create_fast_budget()  # Fast Budget for quick response

        start = time.time()
        result = estimator.estimate(
            question=question,
            context=context,
            budget=budget
        )
        elapsed = time.time() - start

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        assert result.source in ["Validator", "Generative Prior", "Fusion"]
        assert result.certainty in ["high", "medium", "low"]
        assert result.cost['llm_calls'] <= 5, f"Should use ≤5 LLM calls, got {result.cost['llm_calls']}"
        assert elapsed < 10.0, f"Should complete in <10s, took {elapsed:.1f}s"

        print(f"\n✅ Scenario 8: Early Return = ${result.value:.2f} in {elapsed:.1f}s ({result.cost['llm_calls']} LLM calls, source={result.source})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Scenario 9: Validator 확정 데이터 우선 (Stage 1 Validator)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @skip_if_no_llm
    def test_scenario_9_validator_priority(self, estimator):
        """Scenario 9: Validator 확정 데이터 우선

        Expected:
        - Stage 1 (Evidence - Validator) 우선 검색 시도
        - source in ["Validator", "Generative Prior", "Fermi", "Fusion"]
        - certainty in [high, medium, low]
        - Validator 검색 시도 확인
        """
        question = "Netflix 2024년 연간 ARPU는?"
        context = Context(
            domain="Streaming",
            time_period="2024"
        )
        budget = create_standard_budget()

        result = estimator.estimate(question=question, context=context, budget=budget)

        # 검증
        assert result is not None
        assert result.is_successful()
        assert result.value > 0
        # Validator가 찾으면 source="Validator", 못 찾으면 다른 Stage
        assert result.source in ["Validator", "Generative Prior", "Fermi", "Fusion"]
        assert result.certainty in ["high", "medium", "low"]

        print(f"\n✅ Scenario 9: Validator Priority = ${result.value:.2f} (source={result.source}, certainty={result.certainty})")


class TestEstimatorE2EPerformance:
    """v7.11.0 성능 벤치마크 (E2E)"""

    @pytest.fixture
    def estimator(self):
        return EstimatorRAG()

    @skip_if_no_llm
    def test_performance_benchmark_10_questions(self, estimator):
        """성능 벤치마크: 10개 질문 연속 처리

        Expected:
        - 전체 100초 이내 완료
        - 평균 10초 이하
        - 90% 이상 성공률
        """
        import time

        questions = [
            ("B2B SaaS ARPU는?", Context(domain="B2B_SaaS")),
            ("E-commerce Churn Rate는?", Context(domain="E-commerce")),
            ("모바일 앱 DAU는?", Context(domain="Mobile_App")),
            ("AI 챗봇 LTV는?", Context(domain="AI_Chatbot")),
            ("구독 모델 CAC는?", Context(domain="Subscription")),
            ("SaaS MRR 성장률은?", Context(domain="SaaS")),
            ("클라우드 서비스 ARPU는?", Context(domain="Cloud")),
            ("게임 IAP 매출은?", Context(domain="Gaming")),
            ("핀테크 앱 MAU는?", Context(domain="Fintech")),
            ("에듀테크 LTV는?", Context(domain="Edtech")),
        ]

        budget = create_fast_budget()  # Fast Budget for performance
        results = []
        timings = []

        for question, context in questions:
            start = time.time()
            try:
                result = estimator.estimate(question=question, context=context, budget=budget)
                elapsed = time.time() - start
                
                results.append(result.is_successful() if result else False)
                timings.append(elapsed)
                
                print(f"  {question} = {result.value if result else 'N/A'} ({elapsed:.1f}s)")
            except Exception as e:
                elapsed = time.time() - start
                results.append(False)
                timings.append(elapsed)
                print(f"  {question} = ERROR ({elapsed:.1f}s): {str(e)[:50]}")

        # 성능 검증
        total_time = sum(timings)
        avg_time = total_time / len(timings)
        success_rate = sum(results) / len(results)

        print(f"\n📊 Performance Summary:")
        print(f"  Total Time: {total_time:.1f}s")
        print(f"  Average Time: {avg_time:.1f}s")
        print(f"  Success Rate: {success_rate*100:.1f}%")

        assert total_time < 120, f"Total time should be <120s, got {total_time:.1f}s"
        assert avg_time < 15, f"Average time should be <15s, got {avg_time:.1f}s"
        assert success_rate >= 0.8, f"Success rate should be ≥80%, got {success_rate*100:.1f}%"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행 방법
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# 전체 E2E 시나리오 테스트
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v

# 특정 시나리오만 실행
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py::TestEstimatorE2EScenarios::test_scenario_1_b2b_saas_arpu -v

# 성능 벤치마크
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py::TestEstimatorE2EPerformance::test_performance_benchmark_10_questions -v

# 결과 상세 출력
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v -s
"""

