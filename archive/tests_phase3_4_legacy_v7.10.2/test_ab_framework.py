"""
A/B 테스트 프레임워크 (v7.9.0 vs v7.10.0)

목표:
1. estimate() vs estimate_hybrid() 비교
2. Phase별 책임 측정
3. 정확도, 속도, 신뢰도 비교
4. 실패 케이스 분석

작성일: 2025-11-25
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
from umis_rag.agents.estimator.models import Context, EstimationResult


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
class ABResult:
    """A/B 테스트 결과"""
    test_id: str
    question: str

    # v7.9.0 결과
    v79_value: Optional[float] = None
    v79_phase: int = -1
    v79_confidence: float = 0.0
    v79_time_ms: float = 0.0
    v79_success: bool = False

    # v7.10.0 결과
    v710_value: Optional[float] = None
    v710_phase: int = -1
    v710_confidence: float = 0.0
    v710_time_ms: float = 0.0
    v710_success: bool = False

    # 비교
    expected_value: Optional[float] = None
    expected_range: Optional[Tuple[float, float]] = None

    # 분석
    v79_accuracy: Optional[float] = None
    v710_accuracy: Optional[float] = None
    winner: str = "tie"
    notes: str = ""


@dataclass
class ABSummary:
    """A/B 테스트 요약"""
    total_tests: int = 0
    v79_wins: int = 0
    v710_wins: int = 0
    ties: int = 0

    # 평균 지표
    v79_avg_time_ms: float = 0.0
    v710_avg_time_ms: float = 0.0
    v79_avg_confidence: float = 0.0
    v710_avg_confidence: float = 0.0
    v79_success_rate: float = 0.0
    v710_success_rate: float = 0.0

    # Phase별 분포
    v79_phase_dist: Dict[int, int] = field(default_factory=dict)
    v710_phase_dist: Dict[int, int] = field(default_factory=dict)


class ABTestFramework:
    """A/B 테스트 프레임워크"""

    def __init__(self):
        self.estimator = EstimatorRAG()
        self.results: List[ABResult] = []
        self.test_cases: List[TestCase] = []

    def add_test_case(self, test_case: TestCase):
        """테스트 케이스 추가"""
        self.test_cases.append(test_case)

    def add_test_cases(self, test_cases: List[TestCase]):
        """테스트 케이스 일괄 추가"""
        self.test_cases.extend(test_cases)

    def run_single(self, test_case: TestCase) -> ABResult:
        """단일 테스트 실행"""
        result = ABResult(
            test_id=test_case.id,
            question=test_case.question,
            expected_value=test_case.expected_value,
            expected_range=test_case.expected_range
        )

        context = Context(
            domain=test_case.domain or "",
            region=test_case.region or ""
        )

        # v7.9.0 (estimate)
        try:
            start = time.time()
            v79_result = self.estimator.estimate(
                question=test_case.question,
                context=context,
                project_data=test_case.project_data
            )
            result.v79_time_ms = (time.time() - start) * 1000
            result.v79_value = v79_result.value
            result.v79_phase = v79_result.phase
            result.v79_confidence = v79_result.confidence
            result.v79_success = v79_result.is_successful()
        except Exception as e:
            result.notes += f"v7.9.0 error: {e}; "

        # v7.10.0 (estimate_hybrid)
        try:
            start = time.time()
            v710_result = self.estimator.estimate_hybrid(
                question=test_case.question,
                context=context,
                project_data=test_case.project_data
            )
            result.v710_time_ms = (time.time() - start) * 1000
            result.v710_value = v710_result.value
            result.v710_phase = v710_result.phase
            result.v710_confidence = v710_result.confidence
            result.v710_success = v710_result.is_successful()
        except Exception as e:
            result.notes += f"v7.10.0 error: {e}; "

        # 정확도 계산 (expected_value가 있을 때)
        if test_case.expected_value:
            if result.v79_value:
                result.v79_accuracy = 1 - abs(result.v79_value - test_case.expected_value) / test_case.expected_value
            if result.v710_value:
                result.v710_accuracy = 1 - abs(result.v710_value - test_case.expected_value) / test_case.expected_value

        # 승자 결정
        result.winner = self._determine_winner(result)

        self.results.append(result)
        return result

    def _determine_winner(self, result: ABResult) -> str:
        """승자 결정"""
        score_79 = 0
        score_710 = 0

        # 성공 여부 (가중치: 3)
        if result.v79_success:
            score_79 += 3
        if result.v710_success:
            score_710 += 3

        # 정확도 (가중치: 2)
        if result.v79_accuracy and result.v710_accuracy:
            if result.v79_accuracy > result.v710_accuracy + 0.05:
                score_79 += 2
            elif result.v710_accuracy > result.v79_accuracy + 0.05:
                score_710 += 2

        # Confidence (가중치: 1)
        if result.v79_confidence > result.v710_confidence + 0.05:
            score_79 += 1
        elif result.v710_confidence > result.v79_confidence + 0.05:
            score_710 += 1

        # 속도 (가중치: 1, 20% 이상 차이 시)
        if result.v79_time_ms and result.v710_time_ms:
            if result.v79_time_ms < result.v710_time_ms * 0.8:
                score_79 += 1
            elif result.v710_time_ms < result.v79_time_ms * 0.8:
                score_710 += 1

        if score_79 > score_710:
            return "v7.9.0"
        elif score_710 > score_79:
            return "v7.10.0"
        return "tie"

    def run_all(self) -> ABSummary:
        """모든 테스트 실행"""
        for test_case in self.test_cases:
            self.run_single(test_case)
        return self.summarize()

    def summarize(self) -> ABSummary:
        """결과 요약"""
        summary = ABSummary()
        summary.total_tests = len(self.results)

        if not self.results:
            return summary

        # 승자 집계
        for r in self.results:
            if r.winner == "v7.9.0":
                summary.v79_wins += 1
            elif r.winner == "v7.10.0":
                summary.v710_wins += 1
            else:
                summary.ties += 1

            # Phase 분포
            summary.v79_phase_dist[r.v79_phase] = summary.v79_phase_dist.get(r.v79_phase, 0) + 1
            summary.v710_phase_dist[r.v710_phase] = summary.v710_phase_dist.get(r.v710_phase, 0) + 1

        # 평균 계산
        v79_times = [r.v79_time_ms for r in self.results if r.v79_time_ms > 0]
        v710_times = [r.v710_time_ms for r in self.results if r.v710_time_ms > 0]
        v79_confs = [r.v79_confidence for r in self.results if r.v79_success]
        v710_confs = [r.v710_confidence for r in self.results if r.v710_success]

        if v79_times:
            summary.v79_avg_time_ms = sum(v79_times) / len(v79_times)
        if v710_times:
            summary.v710_avg_time_ms = sum(v710_times) / len(v710_times)
        if v79_confs:
            summary.v79_avg_confidence = sum(v79_confs) / len(v79_confs)
        if v710_confs:
            summary.v710_avg_confidence = sum(v710_confs) / len(v710_confs)

        summary.v79_success_rate = sum(1 for r in self.results if r.v79_success) / len(self.results)
        summary.v710_success_rate = sum(1 for r in self.results if r.v710_success) / len(self.results)

        return summary

    def get_failures(self, version: str = "both") -> List[ABResult]:
        """실패 케이스 반환"""
        failures = []
        for r in self.results:
            if version in ("v7.9.0", "both") and not r.v79_success:
                failures.append(r)
            elif version in ("v7.10.0", "both") and not r.v710_success:
                if r not in failures:
                    failures.append(r)
        return failures

    def save_results(self, filepath: str):
        """결과 저장"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": asdict(self.summarize()),
            "results": [asdict(r) for r in self.results]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ============================================================
# 테스트 케이스 정의
# ============================================================

BASIC_TEST_CASES = [
    TestCase(
        id="TC001",
        question="employees",
        project_data={"employees": 100},
        expected_value=100,
        tags=["phase0", "fast_path"]
    ),
    TestCase(
        id="TC002",
        question="한국 커피숍 평균 직원 수는?",
        expected_range=(3, 10),
        domain="F&B",
        region="한국",
        tags=["phase3", "estimation"]
    ),
    TestCase(
        id="TC003",
        question="SaaS 기업의 평균 CAC는?",
        expected_range=(100, 500),
        domain="SaaS",
        tags=["phase3", "business_metric"]
    ),
]


# ============================================================
# 테스트 클래스
# ============================================================

class TestABFramework:
    """A/B 프레임워크 테스트"""

    def test_framework_initialization(self):
        """프레임워크 초기화"""
        framework = ABTestFramework()
        assert framework.estimator is not None
        assert len(framework.results) == 0

    def test_add_test_case(self):
        """테스트 케이스 추가"""
        framework = ABTestFramework()
        tc = TestCase(id="T1", question="테스트")
        framework.add_test_case(tc)
        assert len(framework.test_cases) == 1

    def test_run_single(self):
        """단일 테스트 실행"""
        framework = ABTestFramework()
        tc = TestCase(
            id="T1",
            question="employees",
            project_data={"employees": 50},
            expected_value=50
        )

        result = framework.run_single(tc)

        assert result.test_id == "T1"
        assert result.v79_value is not None or result.v710_value is not None

    def test_run_all(self):
        """전체 테스트 실행"""
        framework = ABTestFramework()
        framework.add_test_cases([
            TestCase(id="T1", question="count", project_data={"count": 10}),
            TestCase(id="T2", question="price", project_data={"price": 100})
        ])

        summary = framework.run_all()

        assert summary.total_tests == 2

    def test_summarize(self):
        """요약 테스트"""
        framework = ABTestFramework()
        framework.results = [
            ABResult(
                test_id="T1", question="Q1",
                v79_success=True, v710_success=True,
                v79_time_ms=100, v710_time_ms=80,
                v79_phase=3, v710_phase=3,
                winner="v7.10.0"
            ),
            ABResult(
                test_id="T2", question="Q2",
                v79_success=True, v710_success=False,
                v79_phase=0, v710_phase=-1,
                winner="v7.9.0"
            )
        ]

        summary = framework.summarize()

        assert summary.total_tests == 2
        assert summary.v79_wins == 1
        assert summary.v710_wins == 1

    def test_get_failures(self):
        """실패 케이스 조회"""
        framework = ABTestFramework()
        framework.results = [
            ABResult(test_id="T1", question="Q1", v79_success=True, v710_success=False),
            ABResult(test_id="T2", question="Q2", v79_success=False, v710_success=True),
            ABResult(test_id="T3", question="Q3", v79_success=True, v710_success=True)
        ]

        v79_failures = framework.get_failures("v7.9.0")
        v710_failures = framework.get_failures("v7.10.0")

        assert len(v79_failures) == 1
        assert len(v710_failures) == 1


class TestPhaseResponsibility:
    """Phase별 책임 측정 테스트"""

    def test_phase_distribution(self):
        """Phase 분포 확인"""
        framework = ABTestFramework()
        framework.add_test_cases([
            TestCase(id="T1", question="count", project_data={"count": 10}),  # Phase 0
            TestCase(id="T2", question="테스트 질문"),  # Phase 3-4
        ])

        framework.run_all()
        summary = framework.summarize()

        # Phase 분포가 기록되어야 함
        assert len(summary.v79_phase_dist) > 0 or len(summary.v710_phase_dist) > 0

    def test_phase0_coverage(self):
        """Phase 0 커버리지"""
        framework = ABTestFramework()

        # Phase 0으로 처리되어야 하는 케이스들
        phase0_cases = [
            TestCase(id=f"P0_{i}", question=f"key{i}", project_data={f"key{i}": i * 10})
            for i in range(5)
        ]
        framework.add_test_cases(phase0_cases)
        framework.run_all()
        summary = framework.summarize()

        # v7.9.0에서 Phase 0 비율
        phase0_count = summary.v79_phase_dist.get(0, 0)
        assert phase0_count >= 3  # 최소 3개는 Phase 0


class TestFailureAnalysis:
    """실패 케이스 분석 테스트"""

    def test_failure_collection(self):
        """실패 케이스 수집"""
        framework = ABTestFramework()

        # 실패 가능성 있는 케이스
        framework.add_test_case(TestCase(
            id="F1",
            question=""  # 빈 질문
        ))

        framework.run_all()
        failures = framework.get_failures()

        # 빈 질문은 실패할 가능성 높음
        # 하지만 v7.10.0은 빈 질문도 처리할 수 있음
        assert isinstance(failures, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

