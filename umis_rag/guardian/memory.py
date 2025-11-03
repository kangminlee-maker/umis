"""
GuardianMemory: 통합 메모리 시스템

QueryMemory + GoalMemory 통합

Guardian (Stewart)의 프로세스 자동 감시
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian.query_memory import QueryMemory
from umis_rag.guardian.goal_memory import GoalMemory
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class GuardianMemory:
    """
    Guardian 통합 메모리 시스템
    
    기능:
    - 순환 감지 (QueryMemory)
    - 목표 정렬 (GoalMemory)
    - 종합 판단 (Guardian 알림)
    
    사용:
    -----
    guardian = GuardianMemory()
    
    # 목표 설정
    guardian.set_goal("음악 스트리밍 시장 분석")
    
    # 작업 시작 시 체크
    result = guardian.check_process("Spotify 구독 모델 분석")
    
    if result['warnings']:
        for warning in result['warnings']:
            print(f"⚠️ {warning}")
    """
    
    def __init__(self):
        """Guardian Memory 초기화"""
        logger.info("=" * 60)
        logger.info("GuardianMemory 초기화")
        logger.info("=" * 60)
        
        self.query_memory = QueryMemory()
        self.goal_memory = GoalMemory()
        
        logger.info("✅ GuardianMemory 준비 완료")
    
    def set_goal(self, goal_text: str) -> str:
        """
        목표 설정
        
        Args:
            goal_text: 목표 설명
        
        Returns:
            memory_id
        """
        logger.info(f"\n[Guardian] 목표 설정: {goal_text}")
        return self.goal_memory.set_goal(goal_text)
    
    def check_process(
        self,
        current_task_or_query: str
    ) -> Dict[str, Any]:
        """
        프로세스 종합 체크
        
        Args:
            current_task_or_query: 현재 작업 또는 질문
        
        Returns:
            {
                'passed': bool,  # 전체 통과 여부
                'warnings': List[str],  # 경고 목록
                'circular': Dict,  # 순환 정보
                'alignment': Dict,  # 정렬 정보
                'recommendation': str  # Guardian 권장사항
            }
        """
        logger.info(f"\n[Guardian] 프로세스 체크: {current_task_or_query[:50]}...")
        
        warnings = []
        passed = True
        
        # 1. 순환 체크
        is_circular, circular_info = self.query_memory.check_and_store(current_task_or_query)
        
        if is_circular:
            warnings.append(
                f"순환 감지: 유사한 질문을 {circular_info['repetition_count']}회 반복하고 있습니다"
            )
            passed = False
        
        # 2. 목표 정렬 체크
        is_aligned, alignment_info = self.goal_memory.check_alignment(current_task_or_query)
        
        if not is_aligned:
            warnings.append(
                f"목표 이탈: 정렬도 {alignment_info['alignment_score']:.2f} "
                f"(임계값 {alignment_info['threshold']}) - {alignment_info['message']}"
            )
            passed = False
        
        # 3. Guardian 권장사항 생성
        recommendation = self._generate_recommendation(
            is_circular, circular_info,
            is_aligned, alignment_info
        )
        
        # 4. 결과 로깅
        if passed:
            logger.info("  ✅ Guardian 체크: 통과")
        else:
            logger.warning(f"  ⚠️  Guardian 체크: 경고 {len(warnings)}개")
            for warning in warnings:
                logger.warning(f"    - {warning}")
        
        return {
            'passed': passed,
            'warnings': warnings,
            'circular': circular_info,
            'alignment': alignment_info,
            'recommendation': recommendation
        }
    
    def _generate_recommendation(
        self,
        is_circular: bool,
        circular_info: Dict[str, Any],
        is_aligned: bool,
        alignment_info: Dict[str, Any]
    ) -> str:
        """
        Guardian 권장사항 생성
        
        Args:
            is_circular: 순환 여부
            circular_info: 순환 정보
            is_aligned: 정렬 여부
            alignment_info: 정렬 정보
        
        Returns:
            권장사항 문자열
        """
        # 둘 다 문제 없음
        if not is_circular and is_aligned:
            return "✅ 계속 진행하세요. 목표에 잘 정렬되어 있습니다."
        
        recommendations = []
        
        # 순환 문제
        if is_circular:
            if circular_info.get('similar_queries'):
                past_query = circular_info['similar_queries'][0]['query']
                recommendations.append(
                    f"⚠️ 이전 질문을 참고하세요: \"{past_query[:50]}...\""
                )
            recommendations.append(
                f"💡 다른 접근 방법을 시도해보세요"
            )
        
        # 목표 이탈
        if not is_aligned:
            goal = alignment_info.get('goal_text', '')
            score = alignment_info.get('alignment_score', 0)
            
            if score < 0.60:
                recommendations.append(
                    f"🎯 목표를 재확인하세요: \"{goal[:50]}...\""
                )
                recommendations.append(
                    f"❓ 현재 작업이 목표 달성에 어떻게 기여하는지 검토하세요"
                )
            else:
                recommendations.append(
                    f"💭 목표와의 연관성을 명확히 하면 좋습니다 (현재 {score:.2f})"
                )
        
        return "\n".join(recommendations) if recommendations else "✅ 문제 없음"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Guardian Memory 전체 요약
        
        Returns:
            요약 정보
        """
        query_stats = self.query_memory.get_stats()
        goal_stats = self.goal_memory.get_stats()
        
        return {
            'query_memory': query_stats,
            'goal_memory': goal_stats,
            'has_active_goal': goal_stats['has_active'],
            'total_interactions': query_stats['total_queries'],
            'circular_warnings': query_stats['circular_warnings']
        }


# 편의 함수
def check_with_guardian(
    task: str,
    goal: Optional[str] = None
) -> Dict[str, Any]:
    """
    편의 함수: Guardian 종합 체크
    
    Args:
        task: 현재 작업/질문
        goal: 목표 (선택, 없으면 기존 목표 사용)
    
    Returns:
        Guardian 체크 결과
    """
    guardian = GuardianMemory()
    
    if goal:
        guardian.set_goal(goal)
    
    return guardian.check_process(task)


# 예시 사용
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GuardianMemory 통합 테스트")
    print("=" * 60)
    
    guardian = GuardianMemory()
    
    # 1. 목표 설정
    print("\n[1] 목표 설정")
    goal = "음악 스트리밍 구독 시장의 수익화 전략 발굴"
    guardian.set_goal(goal)
    print(f"✅ 목표: {goal}")
    
    # 2. 시나리오 테스트
    print("\n[2] 프로세스 체크 시나리오")
    print("=" * 60)
    
    scenarios = [
        "Spotify 프리미엄 구독 모델 분석",
        "Spotify 프리미엄 구독 모델 분석",  # 반복
        "자동차 전기차 시장 분석",           # 이탈
        "YouTube Music 수익화 전략",         # 정렬됨
    ]
    
    for i, task in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i} ---")
        print(f"작업: {task}")
        
        result = guardian.check_process(task)
        
        print(f"통과: {'✅' if result['passed'] else '⚠️'}")
        
        if result['warnings']:
            print("\n경고:")
            for warning in result['warnings']:
                print(f"  {warning}")
        
        print(f"\nGuardian 권장사항:")
        print(f"  {result['recommendation']}")
    
    # 3. 전체 요약
    print(f"\n{'='*60}")
    print("Guardian Memory 요약")
    print(f"{'='*60}")
    
    summary = guardian.get_summary()
    print(f"총 상호작용: {summary['total_interactions']}")
    print(f"순환 경고: {summary['circular_warnings']}")
    print(f"활성 목표: {'있음' if summary['has_active_goal'] else '없음'}")

