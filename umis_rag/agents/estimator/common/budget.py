"""
Budget - 예산 기반 탐색 제약 (v7.11.0)

재귀 대신 예산(Budget)을 사용하여 탐색 범위를 명시적으로 제한합니다.

설계 원칙:
- 모든 리소스(LLM 호출, 변수 개수, 시간)를 명시적으로 제한
- 예산 초과 시 즉시 중단 (fallback으로 이동)
- 추정 품질 vs 비용 트레이드오프를 사용자가 제어 가능
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class Budget:
    """
    예산 기반 탐색 제약

    Attributes:
        max_llm_calls: 최대 LLM 호출 횟수 (기본 10)
        max_variables: 최대 변수 추정 개수 (기본 8)
        max_runtime_seconds: 최대 실행 시간 (초, 기본 60)
        max_depth: 최대 분해 깊이 (기본 2)

        _consumed_llm_calls: 소비된 LLM 호출 횟수 (내부용)
        _consumed_variables: 소비된 변수 개수 (내부용)
        _start_time: 시작 시간 (내부용)
    """

    # 외부 설정 가능
    max_llm_calls: int = 10
    max_variables: int = 8
    max_runtime_seconds: float = 60.0
    max_depth: int = 2

    # 내부 상태 (수정 금지)
    _consumed_llm_calls: int = 0
    _consumed_variables: int = 0
    _start_time: Optional[float] = None

    def __post_init__(self):
        """초기화 후 시작 시간 설정"""
        if self._start_time is None:
            self._start_time = time.time()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예산 소비 (Consumption)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def consume_llm_call(self, count: int = 1) -> bool:
        """
        LLM 호출 소비

        Args:
            count: 소비할 호출 횟수

        Returns:
            성공 여부 (예산 초과 시 False)
        """
        if self._consumed_llm_calls + count > self.max_llm_calls:
            return False
        self._consumed_llm_calls += count
        return True

    def consume_variable(self, count: int = 1) -> bool:
        """
        변수 추정 소비

        Args:
            count: 소비할 변수 개수

        Returns:
            성공 여부 (예산 초과 시 False)
        """
        if self._consumed_variables + count > self.max_variables:
            return False
        self._consumed_variables += count
        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예산 체크 (Check)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def can_call_llm(self, count: int = 1) -> bool:
        """LLM 호출 가능 여부"""
        return self._consumed_llm_calls + count <= self.max_llm_calls

    def can_estimate_variable(self, count: int = 1) -> bool:
        """변수 추정 가능 여부"""
        return self._consumed_variables + count <= self.max_variables

    def has_time(self) -> bool:
        """시간 예산 잔여 여부"""
        if self._start_time is None:
            return True
        elapsed = time.time() - self._start_time
        return elapsed < self.max_runtime_seconds

    def is_exhausted(self) -> bool:
        """
        예산 완전 소진 여부

        다음 중 하나라도 초과하면 True:
        - LLM 호출 횟수
        - 변수 추정 개수
        - 실행 시간
        """
        if not self.has_time():
            return True
        if self._consumed_llm_calls >= self.max_llm_calls:
            return True
        if self._consumed_variables >= self.max_variables:
            return True
        return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 상태 조회 (Status)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_remaining_llm_calls(self) -> int:
        """잔여 LLM 호출 횟수"""
        return max(0, self.max_llm_calls - self._consumed_llm_calls)

    def get_remaining_variables(self) -> int:
        """잔여 변수 추정 개수"""
        return max(0, self.max_variables - self._consumed_variables)

    def get_elapsed_time(self) -> float:
        """경과 시간 (초)"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def get_remaining_time(self) -> float:
        """잔여 시간 (초)"""
        return max(0.0, self.max_runtime_seconds - self.get_elapsed_time())

    def get_status_summary(self) -> dict:
        """
        예산 상태 요약

        Returns:
            {
                'llm_calls': '3/10',
                'variables': '5/8',
                'time': '12.3/60.0s',
                'exhausted': False
            }
        """
        return {
            'llm_calls': f"{self._consumed_llm_calls}/{self.max_llm_calls}",
            'variables': f"{self._consumed_variables}/{self.max_variables}",
            'time': f"{self.get_elapsed_time():.1f}/{self.max_runtime_seconds}s",
            'exhausted': self.is_exhausted()
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 예산 복사 (Copy)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def create_sub_budget(
        self,
        llm_calls: Optional[int] = None,
        variables: Optional[int] = None,
        runtime: Optional[float] = None,
        depth: Optional[int] = None
    ) -> 'Budget':
        """
        하위 예산 생성 (독립적인 Budget 인스턴스)

        Args:
            llm_calls: 새 최대 LLM 호출 (None이면 잔여량)
            variables: 새 최대 변수 (None이면 잔여량)
            runtime: 새 최대 시간 (None이면 잔여량)
            depth: 새 최대 깊이 (None이면 현재 -1)

        Returns:
            새로운 Budget 인스턴스 (소비 상태 초기화)
        """
        return Budget(
            max_llm_calls=llm_calls if llm_calls is not None else self.get_remaining_llm_calls(),
            max_variables=variables if variables is not None else self.get_remaining_variables(),
            max_runtime_seconds=runtime if runtime is not None else self.get_remaining_time(),
            max_depth=depth if depth is not None else max(0, self.max_depth - 1),
            _start_time=time.time()
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프리셋 (Presets)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_fast_budget() -> Budget:
    """
    빠른 추정 예산 (3초 이내)

    - max_llm_calls: 3
    - max_variables: 3
    - max_runtime_seconds: 10.0
    - max_depth: 1
    """
    return Budget(
        max_llm_calls=3,
        max_variables=3,
        max_runtime_seconds=10.0,
        max_depth=1
    )


def create_standard_budget() -> Budget:
    """
    표준 추정 예산 (기본값)

    - max_llm_calls: 10
    - max_variables: 8
    - max_runtime_seconds: 60.0
    - max_depth: 2
    """
    return Budget()


def create_thorough_budget() -> Budget:
    """
    정밀 추정 예산 (최대 2분)

    - max_llm_calls: 20
    - max_variables: 15
    - max_runtime_seconds: 120.0
    - max_depth: 3
    """
    return Budget(
        max_llm_calls=20,
        max_variables=15,
        max_runtime_seconds=120.0,
        max_depth=3
    )
