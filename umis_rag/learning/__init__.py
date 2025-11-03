"""
UMIS Learning Module

LLM 판단 로그를 분석하여 자동으로 규칙 학습

주요 기능:
- LLM 로그 분석
- 패턴 추출
- 자동 규칙 생성
- config/projection_rules.yaml 업데이트
"""

from .rule_learner import RuleLearner, learn_from_logs

__all__ = [
    'RuleLearner',
    'learn_from_logs',
]

