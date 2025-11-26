"""
v7.11.0 Stage 기반 A/B 테스트 프레임워크

목표:
1. Stage 1-4 비교 (Evidence → Prior → Fermi → Fusion)
2. Budget 기반 탐색 비교 (Standard vs Fast)
3. Certainty 측정 (high/medium/low)
4. 정확도, 속도, Cost 비교

마이그레이션:
- v7.9.0 vs v7.10.0 → v7.10.2 (Legacy) vs v7.11.0 (Fusion)
- phase/confidence → source/certainty
- estimate_hybrid 제거 → estimate만 사용

작성일: 2025-11-26
"""

import pytest
import time
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import EstimationResult, Budget, create_standard_budget, create_fast_budget


@dataclass
class TestCase:
    """테스트 케이스"""
    id: str
    question: str
    expected_value: Optional[float] = None
    expected_range: Optional[Tuple[float, float]] = None
    domain: Optional[str] = None
    region: Optional[str] = None
    project_data: Optional[Dict] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class StageABResult:
    """Stage 기반 A/B 테스트 결과"""
    test_id: str
    question: str

    # Standard Budget 결과
    standard_value: Optional[float] = None
    standard_source: str = ""
    standard_certainty: str = ""
    standard_time_ms: float = 0.0
    standard_llm_calls: int = 0
    standard_success: bool = False

    # Fast Budget 결과
    fast_value: Optional[float] = None
    fast_source: str = ""
    fast_certainty: str = ""
    fast_time_ms: float = 0.0
    fast_llm_calls: int = 0
    fast_success: bool = False

    # 비교
    expected_value: Optional[float] = None
    expected_range: Optional[Tuple[float, float]] = None

    # 분석
    standard_accuracy: Optional[float] = None
    fast_accuracy: Optional[float] = None
    winner: str = "tie"
    notes: str = ""


@dataclass
class StageABSummary:
    """Stage 기반 A/B 테스트 요약"""
    total_tests: int = 0
    standard_wins: int = 0
    fast_wins: int = 0
    ties: int = 0

    # 평균 지표
    standard_avg_time_ms: float = 0.0
    fast_avg_time_ms: float = 0.0
    standard_avg_llm_calls: float = 0.0
    fast_avg_llm_calls: float = 0.0
    standard_success_rate: float = 0.0
    fast_success_rate: float = 0.0

    # Source별 분포 (Literal, Direct RAG, Validator, Prior, Fermi, Fusion)
    standard_source_dist: Dict[str, int] = field(default_factory=dict)
    fast_source_dist: Dict[str, int] = field(default_factory=dict)

    # Certainty 분포 (high, medium, low)
    standard_certainty_dist: Dict[str, int] = field(default_factory=dict)
    fast_certainty_dist: Dict[str, int] = field(default_factory=dict)


class StageABTestFramework:
    """Stage 기반 A/B 테스트 프레임워크"""

    def __init__(self):
        self.estimator = EstimatorRAG()
        self.results: List[StageABResult] = []
        self.test_cases: List[TestCase] = []

    def add_test_case(self, test_case: TestCase):
        """테스트 케이스 추가"""
        self.test_cases.append(test_case)

    def add_test_cases(self, test_cases: List[TestCase]):
        """테스트 케이스 일괄 추가"""
        self.test_cases.extend(test_cases)

    def run_single(self, test_case: TestCase) -> StageABResult:
        """단일 테스트 실행"""
        result = StageABResult(
            test_id=test_case.id,
            question=test_case.question,
            expected_value=test_case.expected_value,
            expected_range=test_case.expected_range
        )

        context = Context(
            domain=test_case.domain or "",
            region=test_case.region or ""
        )

        # Standard Budget
        try:
            start = time.time()
            standard_result = self.estimator.estimate(
                question=test_case.question,
                context=context,
                project_data=test_case.project_data
            )
            result.standard_time_ms = (time.time() - start) * 1000
            result.standard_value = standard_result.value
            result.standard_source = standard_result.source
            result.standard_certainty = standard_result.certainty
            result.standard_llm_calls = standard_result.cost.get('llm_calls', 0)
            result.standard_success = standard_result.is_successful()
        except Exception as e:
            result.notes += f"Standard error: {e}; "

        # Fast Budget (EstimatorRAG에 fast_mode 파라미터 추가 필요, 임시로 동일)
        try:
            start = time.time()
            fast_result = self.estimator.estimate(
                question=test_case.question,
                context=context,
                project_data=test_case.project_data
                # TODO: fast_mode=True 파라미터 추가
            )
            result.fast_time_ms = (time.time() - start) * 1000
            result.fast_value = fast_result.value
            result.fast_source = fast_result.source
            result.fast_certainty = fast_result.certainty
            result.fast_llm_calls = fast_result.cost.get('llm_calls', 0)
            result.fast_success = fast_result.is_successful()
        except Exception as e:
            result.notes += f"Fast error: {e}; "

        # 정확도 계산
        if result.expected_value:
            if result.standard_value:
                result.standard_accuracy = self._calculate_accuracy(
                    result.standard_value, result.expected_value, result.expected_range
                )
            if result.fast_value:
                result.fast_accuracy = self._calculate_accuracy(
                    result.fast_value, result.expected_value, result.expected_range
                )

        # Winner 결정
        result.winner = self._determine_winner(result)

        return result

    def _calculate_accuracy(self, value: float, expected: float, expected_range: Optional[Tuple[float, float]]) -> float:
        """정확도 계산 (0.0-1.0)"""
        if expected_range:
            low, high = expected_range
            if low <= value <= high:
                return 1.0
            else:
                # Range 벗어난 정도에 따라 점수 감소
                distance = min(abs(value - low), abs(value - high))
                range_width = high - low
                return max(0.0, 1.0 - (distance / range_width))
        else:
            # Range 없으면 상대 오차 사용
            error = abs(value - expected) / expected
            return max(0.0, 1.0 - error)

    def _determine_winner(self, result: StageABResult) -> str:
        """Winner 결정"""
        if not result.standard_success and not result.fast_success:
            return "tie (both failed)"

        if not result.standard_success:
            return "fast"
        if not result.fast_success:
            return "standard"

        # 정확도 비교
        if result.standard_accuracy and result.fast_accuracy:
            acc_diff = abs(result.standard_accuracy - result.fast_accuracy)
            if acc_diff < 0.1:
                # 정확도 비슷하면 속도 비교
                if result.fast_time_ms < result.standard_time_ms * 0.7:
                    return "fast"
                else:
                    return "standard"
            elif result.standard_accuracy > result.fast_accuracy:
                return "standard"
            else:
                return "fast"

        # Certainty 비교
        certainty_score = {"high": 3, "medium": 2, "low": 1}
        standard_cert = certainty_score.get(result.standard_certainty, 0)
        fast_cert = certainty_score.get(result.fast_certainty, 0)

        if standard_cert > fast_cert:
            return "standard"
        elif fast_cert > standard_cert:
            return "fast"
        else:
            return "tie"

    def run_all(self) -> StageABSummary:
        """모든 테스트 실행"""
        self.results = []
        for test_case in self.test_cases:
            result = self.run_single(test_case)
            self.results.append(result)

        return self.summarize()

    def summarize(self) -> StageABSummary:
        """결과 요약"""
        summary = StageABSummary(total_tests=len(self.results))

        # 집계
        for result in self.results:
            if result.winner.startswith("standard"):
                summary.standard_wins += 1
            elif result.winner.startswith("fast"):
                summary.fast_wins += 1
            else:
                summary.ties += 1

            # 평균 계산용
            summary.standard_avg_time_ms += result.standard_time_ms
            summary.fast_avg_time_ms += result.fast_time_ms
            summary.standard_avg_llm_calls += result.standard_llm_calls
            summary.fast_avg_llm_calls += result.fast_llm_calls

            if result.standard_success:
                summary.standard_success_rate += 1
            if result.fast_success:
                summary.fast_success_rate += 1

            # Source 분포
            if result.standard_source:
                summary.standard_source_dist[result.standard_source] = \
                    summary.standard_source_dist.get(result.standard_source, 0) + 1
            if result.fast_source:
                summary.fast_source_dist[result.fast_source] = \
                    summary.fast_source_dist.get(result.fast_source, 0) + 1

            # Certainty 분포
            if result.standard_certainty:
                summary.standard_certainty_dist[result.standard_certainty] = \
                    summary.standard_certainty_dist.get(result.standard_certainty, 0) + 1
            if result.fast_certainty:
                summary.fast_certainty_dist[result.fast_certainty] = \
                    summary.fast_certainty_dist.get(result.fast_certainty, 0) + 1

        # 평균 계산
        if summary.total_tests > 0:
            summary.standard_avg_time_ms /= summary.total_tests
            summary.fast_avg_time_ms /= summary.total_tests
            summary.standard_avg_llm_calls /= summary.total_tests
            summary.fast_avg_llm_calls /= summary.total_tests
            summary.standard_success_rate /= summary.total_tests
            summary.fast_success_rate /= summary.total_tests

        return summary

    def export_json(self, filename: str):
        """결과 JSON 저장"""
        summary = self.summarize()
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': asdict(summary),
            'results': [asdict(r) for r in self.results]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def print_summary(self):
        """요약 출력"""
        summary = self.summarize()

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 Stage 기반 A/B 테스트 요약 (v7.11.0)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        print(f"\n전체 테스트: {summary.total_tests}개")
        print(f"  - Standard Budget 승리: {summary.standard_wins}개")
        print(f"  - Fast Budget 승리: {summary.fast_wins}개")
        print(f"  - 무승부: {summary.ties}개")

        print(f"\n평균 속도:")
        print(f"  - Standard: {summary.standard_avg_time_ms:.1f}ms")
        print(f"  - Fast: {summary.fast_avg_time_ms:.1f}ms")

        print(f"\n평균 LLM 호출:")
        print(f"  - Standard: {summary.standard_avg_llm_calls:.1f}회")
        print(f"  - Fast: {summary.fast_avg_llm_calls:.1f}회")

        print(f"\n성공률:")
        print(f"  - Standard: {summary.standard_success_rate*100:.1f}%")
        print(f"  - Fast: {summary.fast_success_rate*100:.1f}%")

        print(f"\nSource 분포 (Standard):")
        for source, count in summary.standard_source_dist.items():
            print(f"  - {source}: {count}개")

        print(f"\nSource 분포 (Fast):")
        for source, count in summary.fast_source_dist.items():
            print(f"  - {source}: {count}개")

        print(f"\nCertainty 분포 (Standard):")
        for cert, count in summary.standard_certainty_dist.items():
            print(f"  - {cert}: {count}개")

        print(f"\nCertainty 분포 (Fast):")
        for cert, count in summary.fast_certainty_dist.items():
            print(f"  - {cert}: {count}개")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


# ============================================================
# 테스트 케이스
# ============================================================

def get_standard_test_cases() -> List[TestCase]:
    """표준 테스트 케이스"""
    return [
        TestCase(
            id="TC01",
            question="employees",
            project_data={'employees': 150},
            expected_value=150,
            tags=["literal", "definite"]
        ),
        TestCase(
            id="TC02",
            question="B2B SaaS 평균 ARPU는?",
            domain="B2B_SaaS",
            expected_range=(50000, 200000),
            tags=["validator", "range"]
        ),
        TestCase(
            id="TC03",
            question="서울 음식점 수는?",
            region="서울",
            expected_range=(80000, 120000),
            tags=["fermi", "decomposition"]
        ),
        TestCase(
            id="TC04",
            question="2025년 AI 챗봇 서비스 평균 ARPU는?",
            domain="AI_Chatbot",
            expected_range=(10000, 50000),
            tags=["prior", "generative"]
        ),
        TestCase(
            id="TC05",
            question="서울 전체 음식점 매출은?",
            region="서울",
            expected_range=(5000000000000, 10000000000000),
            tags=["fermi", "complex"]
        ),
    ]


# ============================================================
# Pytest 테스트
# ============================================================

class TestStageABFramework:
    """Stage 기반 A/B 프레임워크 테스트"""

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.parent.joinpath('.env').exists(),
        reason="API key required"
    )
    def test_ab_framework_basic(self):
        """기본 A/B 테스트"""
        framework = StageABTestFramework()
        framework.add_test_cases(get_standard_test_cases())

        summary = framework.run_all()

        # 기본 검증
        assert summary.total_tests == 5
        assert summary.standard_success_rate >= 0.6  # 60% 이상 성공
        assert summary.fast_success_rate >= 0.6

        # 결과 출력
        framework.print_summary()

    def test_ab_export_json(self, tmp_path):
        """JSON 내보내기 테스트"""
        framework = StageABTestFramework()
        framework.add_test_case(get_standard_test_cases()[0])  # TC01만

        framework.run_all()

        output_file = tmp_path / "ab_results.json"
        framework.export_json(str(output_file))

        # JSON 파일 생성 확인
        assert output_file.exists()

        # JSON 로드 확인
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'summary' in data
            assert 'results' in data


if __name__ == "__main__":
    # 직접 실행 시
    framework = StageABTestFramework()
    framework.add_test_cases(get_standard_test_cases())
    framework.run_all()
    framework.print_summary()
    framework.export_json("stage_ab_results.json")

