"""
Error Handler: 고급 에러 처리

Routing Policy Phase 2:
- 에러별 다른 처리
- 재시도 로직
- Fallback 체인
"""

from typing import Callable, Any, Dict, Optional, List
import time
from functools import wraps

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    고급 에러 처리기
    
    기능:
    - 재시도 로직 (exponential backoff)
    - 에러 타입별 처리
    - Fallback 체인
    
    사용:
    -----
    handler = ErrorHandler(max_retries=3)
    
    result = handler.with_retry(
        func=api_call,
        args=(param,),
        fallback=lambda: default_value
    )
    """
    
    def __init__(
        self,
        max_retries: int = 2,
        base_delay: float = 1.0,
        max_delay: float = 10.0
    ):
        """
        Args:
            max_retries: 최대 재시도 횟수
            base_delay: 기본 대기 시간 (초)
            max_delay: 최대 대기 시간 (초)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        logger.info(f"ErrorHandler 초기화")
        logger.info(f"  최대 재시도: {max_retries}회")
        logger.info(f"  기본 대기: {base_delay}초")
    
    def with_retry(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = {},
        fallback: Optional[Callable] = None,
        retryable_errors: Optional[List[type]] = None
    ) -> Any:
        """
        재시도 로직으로 함수 실행
        
        Args:
            func: 실행할 함수
            args: 함수 인자
            kwargs: 함수 키워드 인자
            fallback: 모든 재시도 실패 시 실행할 함수
            retryable_errors: 재시도할 에러 타입 (None이면 모두)
        
        Returns:
            함수 결과
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # 함수 실행
                result = func(*args, **kwargs)
                
                # 성공
                if attempt > 0:
                    logger.info(f"  ✅ 재시도 성공 ({attempt}회 후)")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # 재시도 가능한 에러인지 체크
                if retryable_errors and not isinstance(e, tuple(retryable_errors)):
                    logger.error(f"  ❌ 재시도 불가 에러: {type(e).__name__}: {e}")
                    break
                
                # 마지막 시도가 아니면 재시도
                if attempt < self.max_retries:
                    # Exponential backoff
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"  ⚠️  시도 {attempt + 1} 실패, {delay:.1f}초 후 재시도: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"  ❌ 모든 재시도 실패: {e}")
        
        # Fallback 실행
        if fallback:
            try:
                logger.info(f"  🔄 Fallback 실행...")
                return fallback()
            except Exception as fallback_error:
                logger.error(f"  ❌ Fallback도 실패: {fallback_error}")
        
        # 최종 실패
        raise last_exception
    
    def with_fallback_chain(
        self,
        primary: Callable,
        fallbacks: List[Callable],
        context: Optional[Dict] = None
    ) -> Any:
        """
        Fallback 체인으로 실행
        
        Args:
            primary: 주 함수
            fallbacks: Fallback 함수 리스트 (순서대로 시도)
            context: 컨텍스트 (로깅용)
        
        Returns:
            첫 번째 성공한 함수의 결과
        """
        # Primary 시도
        try:
            result = primary()
            logger.info(f"  ✅ Primary 성공")
            return result
        except Exception as e:
            logger.warning(f"  ⚠️  Primary 실패: {e}")
        
        # Fallback 순서대로 시도
        for i, fallback in enumerate(fallbacks, 1):
            try:
                result = fallback()
                logger.info(f"  ✅ Fallback {i} 성공")
                return result
            except Exception as e:
                logger.warning(f"  ⚠️  Fallback {i} 실패: {e}")
        
        # 모두 실패
        logger.error(f"  ❌ 모든 Fallback 실패")
        raise Exception("All functions in fallback chain failed")


# Decorator
def retry_on_error(
    max_retries: int = 2,
    base_delay: float = 1.0,
    fallback_value: Any = None
):
    """
    재시도 데코레이터
    
    사용:
        @retry_on_error(max_retries=3, fallback_value=[])
        def api_call():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler(max_retries=max_retries, base_delay=base_delay)
            
            try:
                return handler.with_retry(
                    func,
                    args=args,
                    kwargs=kwargs,
                    fallback=lambda: fallback_value if fallback_value is not None else None
                )
            except Exception:
                if fallback_value is not None:
                    return fallback_value
                raise
        
        return wrapper
    return decorator


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("ErrorHandler 테스트")
    print("=" * 60)
    
    handler = ErrorHandler(max_retries=2, base_delay=0.5)
    
    # 1. 재시도 성공 케이스
    print("\n[1] 재시도 성공 케이스")
    
    class Counter:
        def __init__(self):
            self.count = 0
    
    counter = Counter()
    
    def unstable_func():
        counter.count += 1
        if counter.count <= 2:
            raise Exception(f"실패 {counter.count}")
        return f"성공 (시도 {counter.count})"
    
    result = handler.with_retry(unstable_func)
    print(f"결과: {result}")
    
    # 2. Fallback 케이스
    print("\n[2] Fallback 케이스")
    
    def always_fail():
        raise Exception("항상 실패")
    
    def fallback_func():
        return "Fallback 값"
    
    result2 = handler.with_retry(always_fail, fallback=fallback_func)
    print(f"결과: {result2}")
    
    # 3. Fallback 체인
    print("\n[3] Fallback 체인")
    
    def primary():
        raise Exception("Primary 실패")
    
    def fallback1():
        raise Exception("Fallback 1 실패")
    
    def fallback2():
        return "Fallback 2 성공"
    
    result3 = handler.with_fallback_chain(primary, [fallback1, fallback2])
    print(f"결과: {result3}")
    
    print("\n✅ ErrorHandler 작동 확인")

