"""
Meta-RAG: Guardian Orchestrator

Guardian의 통합 평가 및 프로세스 감시 시스템:
- QueryMemory (순환 감지)
- GoalMemory (목표 정렬)
- RAEMemory (평가 일관성)
- Three-Stage Evaluation (품질 평가)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian.memory import GuardianMemory
from umis_rag.guardian.three_stage_evaluator import ThreeStageEvaluator, EvaluationResult
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetaRAGResult:
    """Meta-RAG 최종 결과"""
    passed: bool
    warnings: List[str]
    evaluation: EvaluationResult
    process_check: Dict[str, Any]
    recommendations: List[str]


class GuardianMetaRAG:
    """
    Guardian Meta-RAG Orchestrator
    
    통합 기능:
    - 프로세스 감시 (QueryMemory, GoalMemory)
    - 품질 평가 (3-Stage Evaluation)
    - 평가 일관성 (RAE Index)
    - 종합 판단 및 권장사항
    
    사용:
    -----
    guardian = GuardianMetaRAG()
    
    # 목표 설정
    guardian.set_goal("음악 스트리밍 시장 분석")
    
    # 작업 평가
    result = guardian.evaluate_deliverable({
        'id': 'OPP-001',
        'content': '...',
        'task_description': 'Spotify 구독 모델 분석'
    })
    
    if not result.passed:
        for warning in result.warnings:
            print(f"⚠️ {warning}")
        for rec in result.recommendations:
            print(f"💡 {rec}")
    """
    
    def __init__(self):
        """초기화"""
        logger.info("=" * 60)
        logger.info("Guardian Meta-RAG 초기화")
        logger.info("=" * 60)
        
        self.memory = GuardianMemory()
        self.evaluator = ThreeStageEvaluator()
        
        logger.info("✅ Guardian Meta-RAG 준비 완료")
        logger.info("  • QueryMemory (순환 감지)")
        logger.info("  • GoalMemory (목표 정렬)")
        logger.info("  • RAEMemory (평가 일관성)")
        logger.info("  • 3-Stage Evaluation (품질 평가)")
    
    def set_goal(self, goal_text: str) -> str:
        """
        목표 설정
        
        Args:
            goal_text: 목표 설명
        
        Returns:
            memory_id
        """
        return self.memory.set_goal(goal_text)
    
    def evaluate_deliverable(
        self,
        deliverable: Dict[str, Any]
    ) -> MetaRAGResult:
        """
        산출물 종합 평가
        
        Args:
            deliverable: 평가 대상
                - id: 산출물 ID
                - content: 내용
                - task_description: 작업 설명 (프로세스 체크용)
        
        Returns:
            MetaRAGResult (종합 결과)
        """
        deliverable_id = deliverable.get('id', 'unknown')
        task_desc = deliverable.get('task_description', deliverable.get('content', ''))
        
        logger.info(f"\n[Guardian Meta-RAG] 종합 평가: {deliverable_id}")
        logger.info("=" * 60)
        
        warnings = []
        recommendations = []
        
        # 1. 프로세스 체크 (Memory)
        logger.info("\n[1] 프로세스 체크")
        process_check = self.memory.check_process(task_desc)
        
        if not process_check['passed']:
            warnings.extend(process_check['warnings'])
        
        # 2. 품질 평가 (3-Stage)
        logger.info("\n[2] 품질 평가")
        evaluation = self.evaluator.evaluate(deliverable)
        
        if evaluation.grade in ['C', 'D']:
            warnings.append(f"품질 등급 낮음: {evaluation.grade} (점수 {evaluation.score:.2f})")
        
        # 3. 종합 판단
        passed = (
            process_check['passed'] and
            evaluation.grade in ['A', 'B']
        )
        
        # 4. 권장사항 생성
        recommendations = self._generate_recommendations(
            process_check,
            evaluation,
            passed
        )
        
        # 5. 최종 로깅
        logger.info("\n[Guardian] 종합 판단")
        logger.info("=" * 60)
        
        if passed:
            logger.info(f"  ✅ 통과: {evaluation.grade} ({evaluation.stage})")
        else:
            logger.warning(f"  ⚠️  경고: {len(warnings)}개")
            for warning in warnings:
                logger.warning(f"    - {warning}")
        
        if recommendations:
            logger.info(f"\n💡 Guardian 권장사항:")
            for rec in recommendations:
                logger.info(f"  • {rec}")
        
        return MetaRAGResult(
            passed=passed,
            warnings=warnings,
            evaluation=evaluation,
            process_check=process_check,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        process_check: Dict[str, Any],
        evaluation: EvaluationResult,
        passed: bool
    ) -> List[str]:
        """
        종합 권장사항 생성
        
        Args:
            process_check: 프로세스 체크 결과
            evaluation: 품질 평가 결과
            passed: 전체 통과 여부
        
        Returns:
            권장사항 리스트
        """
        recommendations = []
        
        if passed:
            recommendations.append("✅ 계속 진행하세요. 품질과 프로세스 모두 양호합니다.")
            return recommendations
        
        # 프로세스 문제
        if process_check.get('recommendation'):
            recommendations.append(process_check['recommendation'])
        
        # 품질 문제
        if evaluation.grade == 'D':
            recommendations.append("❗ 품질이 낮습니다. 근거와 정량화를 강화하세요.")
        elif evaluation.grade == 'C':
            recommendations.append("💭 품질 개선 가능합니다. 사례나 정량 데이터를 추가하세요.")
        
        # Stage 3까지 간 경우
        if evaluation.stage == 'stage_3':
            recommendations.append("🤔 애매한 케이스입니다. 추가 검토를 권장합니다.")
        
        return recommendations
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Guardian Meta-RAG 전체 요약
        
        Returns:
            요약 정보
        """
        memory_summary = self.memory.get_summary()
        
        return {
            'memory': memory_summary,
            'components': {
                'query_memory': True,
                'goal_memory': True,
                'rae_memory': True,
                'three_stage_eval': True
            },
            'ready': True
        }


# 예시 사용
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Guardian Meta-RAG 통합 테스트")
    print("=" * 60)
    
    guardian = GuardianMetaRAG()
    
    # 1. 목표 설정
    print("\n[1] 목표 설정")
    goal = "음악 스트리밍 시장의 구독 + 광고 이중 수익화 전략 발굴"
    guardian.set_goal(goal)
    print(f"✅ 목표: {goal}")
    
    # 2. 좋은 케이스
    print("\n[2] 좋은 케이스 평가")
    
    good_case = {
        'id': 'OPP-GOOD-001',
        'content': '''
음악 스트리밍 Freemium + 광고 모델

목표: Spotify와 유사한 이중 수익화
전략: 무료는 광고, 프리미엄은 구독
시장: 연 $10B
근거: Spotify 성공 사례, YouTube Music
        ''',
        'task_description': 'Spotify 구독 광고 모델 분석',
        'metadata': {
            'evidence_ids': ['CAN-spotify-001', 'CAN-youtube-002'],
            'has_examples': True
        }
    }
    
    result_good = guardian.evaluate_deliverable(good_case)
    
    print(f"\n결과:")
    print(f"  통과: {'✅' if result_good.passed else '⚠️'}")
    print(f"  등급: {result_good.evaluation.grade}")
    print(f"  Stage: {result_good.evaluation.stage}")
    
    # 3. 나쁜 케이스 (목표 이탈)
    print("\n[3] 나쁜 케이스 평가 (목표 이탈)")
    
    bad_case = {
        'id': 'OPP-BAD-001',
        'content': '자동차 전기차 충전소 비즈니스',
        'task_description': '자동차 EV 충전소 시장 분석',
        'metadata': {}
    }
    
    result_bad = guardian.evaluate_deliverable(bad_case)
    
    print(f"\n결과:")
    print(f"  통과: {'✅' if result_bad.passed else '⚠️'}")
    print(f"  경고: {len(result_bad.warnings)}개")
    
    if result_bad.warnings:
        print(f"\n  경고:")
        for w in result_bad.warnings:
            print(f"    - {w}")
    
    if result_bad.recommendations:
        print(f"\n  권장사항:")
        for r in result_bad.recommendations:
            print(f"    • {r}")
    
    # 4. 요약
    print("\n[4] Guardian Meta-RAG 요약")
    summary = guardian.get_summary()
    print(f"  총 상호작용: {summary['memory']['total_interactions']}")
    print(f"  활성 목표: {'있음' if summary['memory']['has_active_goal'] else '없음'}")
    print(f"  준비 상태: {summary['ready']}")
    
    print("\n✅ Guardian Meta-RAG 작동 확인")

