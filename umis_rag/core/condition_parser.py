"""
Condition Parser: 복잡한 조건 파싱 및 평가

Routing Policy Phase 2:
- AND, OR, NOT 조합
- 깊은 변수 참조 (patterns[0].metadata.confidence)
- 안전한 표현식 평가
"""

from typing import Any, Dict, List, Optional
import re

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class ConditionParser:
    """
    조건 파서 및 평가기
    
    지원 조건:
    - Simple: "always", "never"
    - Comparison: "count > 5", "confidence >= 0.7"
    - Logical: "A AND B", "A OR B", "NOT A"
    - Deep reference: "patterns[0].metadata.confidence"
    
    사용:
    -----
    parser = ConditionParser()
    result = parser.evaluate("patterns.count > 0 AND confidence >= 0.7", context)
    """
    
    def __init__(self):
        """초기화"""
        logger.info("ConditionParser 초기화")
    
    def evaluate(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        조건 평가
        
        Args:
            condition: 조건 문자열
            context: 변수 컨텍스트
        
        Returns:
            평가 결과 (True/False)
        """
        # 1. 단순 조건
        if condition == 'always':
            return True
        if condition == 'never':
            return False
        
        # 2. Logical 연산자 처리
        if ' AND ' in condition or ' OR ' in condition or condition.startswith('NOT '):
            return self._evaluate_logical(condition, context)
        
        # 3. 비교 연산자 처리
        if any(op in condition for op in ['>=', '<=', '==', '!=', '>', '<']):
            return self._evaluate_comparison(condition, context)
        
        # 4. 단순 변수 (truthy 체크)
        return self._evaluate_variable(condition, context)
    
    def _evaluate_logical(self, condition: str, context: Dict[str, Any]) -> bool:
        """논리 연산자 평가"""
        
        # NOT 처리
        if condition.startswith('NOT '):
            sub_condition = condition[4:].strip()
            return not self.evaluate(sub_condition, context)
        
        # AND 처리
        if ' AND ' in condition:
            parts = condition.split(' AND ')
            return all(self.evaluate(p.strip(), context) for p in parts)
        
        # OR 처리
        if ' OR ' in condition:
            parts = condition.split(' OR ')
            return any(self.evaluate(p.strip(), context) for p in parts)
        
        return False
    
    def _evaluate_comparison(self, condition: str, context: Dict[str, Any]) -> bool:
        """비교 연산자 평가"""
        
        # 연산자 찾기
        operators = ['>=', '<=', '==', '!=', '>', '<']
        op = None
        for operator in operators:
            if operator in condition:
                op = operator
                break
        
        if not op:
            return False
        
        # 좌변, 우변 분리
        parts = condition.split(op)
        if len(parts) != 2:
            return False
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        # 값 추출
        left_value = self._get_value(left, context)
        right_value = self._parse_literal(right)
        
        # 비교
        try:
            if op == '>=':
                return left_value >= right_value
            elif op == '<=':
                return left_value <= right_value
            elif op == '==':
                return left_value == right_value
            elif op == '!=':
                return left_value != right_value
            elif op == '>':
                return left_value > right_value
            elif op == '<':
                return left_value < right_value
        except Exception as e:
            logger.warning(f"  ⚠️  비교 실패: {condition} - {e}")
            return False
        
        return False
    
    def _evaluate_variable(self, var_name: str, context: Dict[str, Any]) -> bool:
        """변수 truthy 체크"""
        value = self._get_value(var_name, context)
        return bool(value)
    
    def _get_value(self, path: str, context: Dict[str, Any]) -> Any:
        """
        변수 경로에서 값 추출
        
        지원:
        - patterns
        - patterns.count
        - patterns[0].id
        - patterns[0].metadata.confidence
        
        Args:
            path: 변수 경로
            context: 컨텍스트
        
        Returns:
            추출된 값
        """
        path = path.strip()
        
        # patterns.count 같은 단순 경로
        if '.' in path and '[' not in path:
            parts = path.split('.')
            value = context.get(parts[0])
            
            for part in parts[1:]:
                if part == 'count':
                    # count는 len()으로
                    if isinstance(value, (list, dict, str)):
                        value = len(value)
                    else:
                        value = 0
                elif isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            
            return value
        
        # patterns[0] 같은 인덱스 접근
        if '[' in path:
            return self._get_indexed_value(path, context)
        
        # 단순 변수
        return context.get(path)
    
    def _get_indexed_value(self, path: str, context: Dict[str, Any]) -> Any:
        """
        인덱스 접근 처리
        
        예: patterns[0].metadata.confidence
        """
        # 정규식으로 파싱: var_name[index].field1.field2
        pattern = r'(\w+)\[(\d+)\](\.(.+))?'
        match = re.match(pattern, path)
        
        if not match:
            return None
        
        var_name = match.group(1)
        index = int(match.group(2))
        remaining = match.group(4)  # field1.field2
        
        # 변수 가져오기
        value = context.get(var_name)
        
        if not isinstance(value, (list, tuple)):
            return None
        
        if index >= len(value):
            return None
        
        value = value[index]
        
        # 남은 경로 처리
        if remaining:
            for field in remaining.split('.'):
                if isinstance(value, dict):
                    value = value.get(field)
                else:
                    return None
        
        return value
    
    def _parse_literal(self, literal: str) -> Any:
        """
        리터럴 파싱 (숫자, 문자열, 불린)
        
        Args:
            literal: 리터럴 문자열
        
        Returns:
            파싱된 값
        """
        literal = literal.strip()
        
        # 불린
        if literal.lower() == 'true':
            return True
        if literal.lower() == 'false':
            return False
        
        # None
        if literal.lower() == 'none' or literal.lower() == 'null':
            return None
        
        # 숫자
        try:
            if '.' in literal:
                return float(literal)
            else:
                return int(literal)
        except ValueError:
            pass
        
        # 문자열 (따옴표 제거)
        if literal.startswith('"') and literal.endswith('"'):
            return literal[1:-1]
        if literal.startswith("'") and literal.endswith("'"):
            return literal[1:-1]
        
        # 그대로 반환
        return literal


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("ConditionParser 테스트")
    print("=" * 60)
    
    parser = ConditionParser()
    
    # 테스트 컨텍스트
    context = {
        'patterns': [
            {'id': 'subscription', 'metadata': {'confidence': 0.85}},
            {'id': 'platform', 'metadata': {'confidence': 0.72}}
        ],
        'cases': ['case1', 'case2', 'case3'],
        'confidence': 0.8
    }
    
    # 테스트 케이스
    test_cases = [
        ("always", True),
        ("never", False),
        ("patterns.count > 0", True),
        ("patterns.count >= 2", True),
        ("patterns.count > 5", False),
        ("confidence >= 0.7", True),
        ("confidence < 0.5", False),
        ("patterns.count > 0 AND confidence >= 0.7", True),
        ("patterns.count > 5 OR confidence >= 0.7", True),
        ("patterns.count > 5 AND confidence >= 0.9", False),
        ("NOT patterns.count > 5", True),
        ("patterns[0].metadata.confidence >= 0.8", True),
        ("patterns[1].metadata.confidence >= 0.8", False),
    ]
    
    print("\n테스트 케이스:")
    print("=" * 60)
    
    passed = 0
    for condition, expected in test_cases:
        result = parser.evaluate(condition, context)
        status = "✅" if result == expected else "❌"
        print(f"{status} {condition:50s} → {result} (예상: {expected})")
        if result == expected:
            passed += 1
    
    print("=" * 60)
    print(f"통과: {passed}/{len(test_cases)}")
    print("\n✅ ConditionParser 작동 확인" if passed == len(test_cases) else "\n❌ 일부 실패")

