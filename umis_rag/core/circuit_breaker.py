"""
Circuit Breaker: Fail-Safe Tier 3

자동 보호 시스템:
- 연속 실패 감지
- 자동 비활성화
- 자동 복구
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import time

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CircuitState:
    """Circuit Breaker 상태"""
    name: str
    state: str = "closed"  # closed / open / half_open
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    opened_at: Optional[datetime] = None


class CircuitBreaker:
    """
    Circuit Breaker 패턴 구현
    
    상태:
    - CLOSED: 정상 작동 (실패 카운트 추적)
    - OPEN: 차단됨 (복구 대기)
    - HALF_OPEN: 테스트 중 (1회 허용)
    
    워크플로우:
    - CLOSED → (3회 실패) → OPEN
    - OPEN → (60초 대기) → HALF_OPEN
    - HALF_OPEN → (성공) → CLOSED
    - HALF_OPEN → (실패) → OPEN
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
        timeout_seconds: int = 30
    ):
        """
        Args:
            name: Circuit Breaker 이름
            failure_threshold: 실패 임계값 (3회)
            recovery_timeout: 복구 대기 시간 (60초)
            timeout_seconds: 타임아웃 (30초)
        """
        self.state = CircuitState(name=name)
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout_seconds = timeout_seconds
        
        logger.info(f"CircuitBreaker '{name}' 초기화")
        logger.info(f"  실패 임계값: {failure_threshold}회")
        logger.info(f"  복구 시간: {recovery_timeout}초")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Circuit Breaker로 함수 호출
        
        Args:
            func: 호출할 함수
            *args, **kwargs: 함수 인자
        
        Returns:
            함수 결과
        
        Raises:
            CircuitBreakerOpenError: Circuit이 OPEN 상태일 때
        """
        # 1. 상태 체크
        if self.state.state == "open":
            # 복구 시간 체크
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                logger.warning(f"  ⚠️  Circuit OPEN: {self.state.name} 차단됨")
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.state.name}' is OPEN"
                )
        
        # 2. 함수 실행
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # 타임아웃 체크
            if elapsed > self.timeout_seconds:
                logger.warning(f"  ⚠️  타임아웃: {elapsed:.1f}초 > {self.timeout_seconds}초")
                self._record_failure()
                raise TimeoutError(f"Function took {elapsed:.1f}s > {self.timeout_seconds}s")
            
            # 성공 기록
            self._record_success()
            return result
            
        except Exception as e:
            # 실패 기록
            self._record_failure()
            
            logger.error(f"  ❌ Circuit Breaker에서 실패 감지: {e}")
            raise
    
    def _record_success(self):
        """성공 기록"""
        self.state.last_success_time = datetime.now()
        
        # HALF_OPEN → CLOSED
        if self.state.state == "half_open":
            self._transition_to_closed()
            logger.info(f"  ✅ Circuit CLOSED: {self.state.name} 복구됨")
        
        # CLOSED 상태에서 성공 시 카운트 리셋
        if self.state.state == "closed":
            self.state.failure_count = 0
    
    def _record_failure(self):
        """실패 기록"""
        self.state.failure_count += 1
        self.state.last_failure_time = datetime.now()
        
        logger.warning(
            f"  ⚠️  실패 {self.state.failure_count}/{self.failure_threshold}: "
            f"{self.state.name}"
        )
        
        # 임계값 도달 → OPEN
        if self.state.failure_count >= self.failure_threshold:
            self._transition_to_open()
            logger.error(f"  🚨 Circuit OPEN: {self.state.name} 차단됨 (복구 대기 {self.recovery_timeout}초)")
        
        # HALF_OPEN에서 실패 → OPEN
        if self.state.state == "half_open":
            self._transition_to_open()
            logger.error(f"  🚨 Circuit OPEN: {self.state.name} 복구 실패")
    
    def _should_attempt_reset(self) -> bool:
        """복구 시도 가능한지 체크"""
        if self.state.opened_at is None:
            return False
        
        elapsed = (datetime.now() - self.state.opened_at).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _transition_to_closed(self):
        """CLOSED 상태로 전환"""
        self.state.state = "closed"
        self.state.failure_count = 0
        self.state.opened_at = None
    
    def _transition_to_open(self):
        """OPEN 상태로 전환"""
        self.state.state = "open"
        self.state.opened_at = datetime.now()
    
    def _transition_to_half_open(self):
        """HALF_OPEN 상태로 전환"""
        logger.info(f"  🔄 Circuit HALF_OPEN: {self.state.name} 복구 시도")
        self.state.state = "half_open"
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태 조회"""
        return {
            'name': self.state.name,
            'state': self.state.state,
            'failure_count': self.state.failure_count,
            'last_failure': self.state.last_failure_time.isoformat() if self.state.last_failure_time else None,
            'last_success': self.state.last_success_time.isoformat() if self.state.last_success_time else None,
            'opened_at': self.state.opened_at.isoformat() if self.state.opened_at else None
        }
    
    def reset(self):
        """수동 리셋"""
        logger.info(f"  🔄 Circuit 수동 리셋: {self.state.name}")
        self._transition_to_closed()


class CircuitBreakerOpenError(Exception):
    """Circuit Breaker가 OPEN 상태일 때 발생하는 예외"""
    pass


# 전역 Circuit Breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 3,
    recovery_timeout: int = 60
) -> CircuitBreaker:
    """
    Circuit Breaker 가져오기 (싱글톤)
    
    Args:
        name: Circuit Breaker 이름
        failure_threshold: 실패 임계값
        recovery_timeout: 복구 대기 시간
    
    Returns:
        CircuitBreaker 인스턴스
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    
    return _circuit_breakers[name]


# Decorator
def circuit_breaker(
    name: str,
    failure_threshold: int = 3,
    recovery_timeout: int = 60
):
    """
    Circuit Breaker 데코레이터
    
    사용:
        @circuit_breaker("neo4j", failure_threshold=3)
        def query_neo4j():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cb = get_circuit_breaker(name, failure_threshold, recovery_timeout)
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("Circuit Breaker 테스트")
    print("=" * 60)
    
    # 테스트 함수 (가끔 실패)
    call_count = 0
    
    def unstable_function():
        global call_count
        call_count += 1
        
        # 1-3회는 실패, 4회부터 성공
        if call_count <= 3:
            raise Exception(f"실패 {call_count}회")
        return f"성공 (call {call_count})"
    
    # Circuit Breaker 생성
    cb = CircuitBreaker("test_circuit", failure_threshold=3, recovery_timeout=2)
    
    # 테스트 시나리오
    print("\n[1] 연속 실패 (3회) → OPEN 예상")
    for i in range(4):
        try:
            result = cb.call(unstable_function)
            print(f"  호출 {i+1}: {result}")
        except CircuitBreakerOpenError as e:
            print(f"  호출 {i+1}: Circuit OPEN - {e}")
        except Exception as e:
            print(f"  호출 {i+1}: 실패 - {e}")
    
    # 상태 확인
    state = cb.get_state()
    print(f"\n현재 상태: {state['state']}")
    print(f"실패 횟수: {state['failure_count']}")
    
    # 복구 대기
    print(f"\n[2] 복구 대기 (2초)...")
    time.sleep(2.5)
    
    # 복구 시도
    print("\n[3] 복구 시도 (HALF_OPEN)")
    try:
        result = cb.call(unstable_function)
        print(f"  호출: {result}")
        print(f"  상태: {cb.get_state()['state']}")
    except Exception as e:
        print(f"  호출: 실패 - {e}")
    
    print(f"\n✅ Circuit Breaker 테스트 완료")

