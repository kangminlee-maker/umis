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
    
    def recommend_methodology(
        self,
        estimate_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        추정 결과 기반 방법론 권고 (Hybrid Guestimation)
        
        Args:
            estimate_result: Phase 1 (Guestimation) 결과
                - value: 추정값 (float)
                - range: 범위 (tuple: 하한, 상한)
                - confidence: 신뢰도 (0-1)
                - method: 사용한 방법 (기본 'guestimation')
            
            context: 추가 맥락 (선택)
                - domain: 산업/영역
                - geography: 지리
                - regulatory: 규제 산업 여부 (bool)
                - new_market: 신규 시장 여부 (bool)
        
        Returns:
            권고 결과
                - recommendation: str ('domain_reasoner' | 'guestimation_sufficient')
                - reason: str (권고 이유)
                - priority: str ('required' | 'high' | 'medium' | 'low')
                - trigger: str (트리거 종류)
                - estimated_time: str (예상 소요 시간)
        
        Example:
            >>> guardian = GuardianMetaRAG()
            >>> result = guardian.recommend_methodology(
            ...     estimate_result={
            ...         'value': 50_000_000_000,  # 500억
            ...         'range': (20_000_000_000, 80_000_000_000),
            ...         'confidence': 0.3
            ...     },
            ...     context={'domain': 'healthcare', 'regulatory': True}
            ... )
            >>> print(result['recommendation'])  # 'domain_reasoner'
            >>> print(result['priority'])  # 'required'
        """
        if context is None:
            context = {}
        
        # 입력 추출
        value = estimate_result.get('value', 0)
        range_tuple = estimate_result.get('range', (0, 0))
        confidence = estimate_result.get('confidence', 0)
        current_method = estimate_result.get('method', 'guestimation')
        
        # 범위 폭 계산
        if range_tuple[0] > 0:
            range_width = range_tuple[1] / range_tuple[0]
        else:
            range_width = float('inf')
        
        # 맥락 추출
        is_regulatory = context.get('regulatory', False)
        is_new_market = context.get('new_market', False)
        
        logger.info("\n[Guardian] 방법론 권고 평가")
        logger.info("=" * 60)
        logger.info(f"  추정값: {value:,.0f}")
        logger.info(f"  범위: {range_tuple[0]:,.0f} - {range_tuple[1]:,.0f}")
        logger.info(f"  신뢰도: {confidence*100:.0f}%")
        logger.info(f"  범위 폭: ±{(range_width-1)*50:.0f}%")
        
        # === 우선순위별 트리거 검사 ===
        
        # Trigger 1: 규제 산업 (최우선, required)
        if is_regulatory:
            logger.info("\n  ✅ Trigger 4: 규제 산업 감지")
            logger.info(f"     → Phase 2 필수 (s3 Laws/Ethics/Physics 검증)")
            
            return {
                'recommendation': 'domain_reasoner',
                'reason': '규제 산업 (의료/금융/교육) → s3 Laws/Ethics/Physics 검증 필수',
                'priority': 'required',
                'trigger': 'regulatory_industry',
                'estimated_time': '2-4시간',
                'auto_execute': True
            }
        
        # Trigger 2: 신뢰도 낮음 (high)
        if confidence < 0.5:
            logger.info(f"\n  ✅ Trigger 1: 신뢰도 낮음 ({confidence*100:.0f}% < 50%)")
            logger.info(f"     → Phase 2 권고 (s2 RAG Consensus 필요)")
            
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'신뢰도 {confidence*100:.0f}% → 50% 미만 → RAG Consensus (s2) 필요',
                'priority': 'high',
                'trigger': 'low_confidence',
                'estimated_time': '1-4시간',
                'auto_execute': False
            }
        
        # Trigger 3: 범위 너무 넓음 (high)
        if range_width > 1.75:  # ±75% 이상
            logger.info(f"\n  ✅ Trigger 2: 범위 폭 과다 (±{(range_width-1)*50:.0f}% > ±75%)")
            logger.info(f"     → Phase 2 권고 (정밀 수렴 필요)")
            
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'범위 폭 ±{(range_width-1)*50:.0f}% → ±75% 초과 → 정밀 수렴 필요',
                'priority': 'high',
                'trigger': 'wide_range',
                'estimated_time': '1-3시간',
                'auto_execute': False
            }
        
        # Trigger 4: 기회 크기 큼 (medium)
        if value > 100_000_000_000:  # 1,000억
            value_billions = value / 1_000_000_000
            logger.info(f"\n  ✅ Trigger 3: 큰 기회 ({value_billions:.0f}억 > 1,000억)")
            logger.info(f"     → Phase 2 권고 (정밀 검증)")
            
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'기회 크기 {value_billions:.0f}억 → 1,000억 초과 → 정밀 검증 필요',
                'priority': 'medium',
                'trigger': 'large_opportunity',
                'estimated_time': '2-4시간',
                'auto_execute': False
            }
        
        # Trigger 5: 신규 시장 (medium)
        if is_new_market:
            logger.info(f"\n  ✅ Trigger 5: 신규 시장 감지")
            logger.info(f"     → Phase 2 권고 (s9 Case Analogies 전이)")
            
            return {
                'recommendation': 'domain_reasoner',
                'reason': '신규 시장 (직접 데이터 부족) → s9 Case Analogies (사례 전이) 필요',
                'priority': 'medium',
                'trigger': 'new_market',
                'estimated_time': '2-3시간',
                'auto_execute': False
            }
        
        # 모든 트리거 없음 → Guestimation 충분
        logger.info(f"\n  ✅ 모든 트리거 통과 → Guestimation 충분")
        logger.info(f"     신뢰도: {confidence*100:.0f}%, 범위: ±{(range_width-1)*50:.0f}%")
        
        return {
            'recommendation': 'guestimation_sufficient',
            'reason': f'신뢰도 {confidence*100:.0f}%, 범위 ±{(range_width-1)*50:.0f}% → Guestimation 충분',
            'priority': 'low',
            'trigger': 'sufficient',
            'estimated_time': 'N/A',
            'auto_execute': False
        }
    
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

