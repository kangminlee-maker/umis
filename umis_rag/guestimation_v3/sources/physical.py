"""
Physical Constraints Sources

절대 한계 (Knock-out Rules)
- 시공간 법칙
- 보존 법칙
- 수학 정의
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from umis_rag.utils.logger import logger
from ..models import Boundary, SourceType, Context


class PhysicalConstraintBase:
    """Physical Constraint Base Class"""
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """
        제약 수집
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            List[Boundary]: 해당되는 제약들
        """
        raise NotImplementedError


class SpacetimeConstraintSource(PhysicalConstraintBase):
    """
    시공간 제약
    
    역할:
    -----
    - 거리/속도/시간 관계
    - 동시 다지점 불가
    - 사기 감지 등
    
    예시:
    -----
    - "서울-부산 최소 2.5시간"
    - "서울 12:00 → 부산 12:05 = 불가능"
    """
    
    def __init__(self):
        # 주요 도시 거리 DB (간단히)
        self.distances = {
            ('서울', '부산'): 400,  # km
            ('서울', '대구'): 300,
            ('서울', '광주'): 330,
            ('서울', '대전'): 150,
        }
        
        # 교통수단 속도
        self.speeds = {
            'KTX': 300,      # km/h
            '고속버스': 90,
            '자동차': 100,
            '비행기': 800,
        }
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """시공간 제약 수집"""
        
        constraints = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 이동 시간 제약
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        travel_constraint = self._check_travel_time(question, context)
        if travel_constraint:
            constraints.append(travel_constraint)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 시간 단위 제약
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        time_constraint = self._check_time_units(question, context)
        if time_constraint:
            constraints.append(time_constraint)
        
        return constraints
    
    def _check_travel_time(self, question: str, context: Optional[Context]) -> Optional[Boundary]:
        """이동 시간 제약"""
        
        # 간단한 패턴 매칭 (실제로는 LLM 사용 가능)
        # "서울에서 부산까지 시간?" 같은 질문
        
        # TODO: 실제 구현
        # 현재는 None
        return None
    
    def _check_time_units(self, question: str, context: Optional[Context]) -> Optional[Boundary]:
        """시간 단위 제약"""
        
        # "하루에 몇 시간 일?" → max 24
        # "주당 근무?" → max 168 (7×24)
        
        if any(word in question for word in ['하루', '일', '1일']):
            if any(word in question for word in ['시간', '시']):
                return Boundary(
                    source_type=SourceType.SPACETIME,
                    min_value=0,
                    max_value=24,
                    confidence=1.0,
                    reasoning="하루는 24시간 (물리적 한계)"
                )
        
        if any(word in question for word in ['주', '1주', '일주일']):
            if any(word in question for word in ['시간', '근무']):
                return Boundary(
                    source_type=SourceType.SPACETIME,
                    min_value=0,
                    max_value=168,
                    confidence=1.0,
                    reasoning="주 168시간 (7일×24시간)"
                )
        
        return None


class ConservationLawSource(PhysicalConstraintBase):
    """
    보존 법칙
    
    역할:
    -----
    - 입력 = 출력
    - 전체 >= 부분
    - 논리적 일관성
    
    예시:
    -----
    - "매출 = 고객 × 단가"
    - "전체 시장 >= 세그먼트"
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """보존 법칙 수집"""
        
        constraints = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 부분-전체 관계
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        part_whole = self._check_part_whole(question, context)
        if part_whole:
            constraints.append(part_whole)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 합산 관계
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 확정 데이터에서 관계 추출
        if context and context.project_data:
            sum_constraint = self._check_sum_relationship(context.project_data)
            if sum_constraint:
                constraints.append(sum_constraint)
        
        return constraints
    
    def _check_part_whole(self, question: str, context: Optional[Context]) -> Optional[Boundary]:
        """부분-전체 관계 체크"""
        
        # "세그먼트 시장" < "전체 시장"
        # "B2B 매출" < "전체 매출"
        
        # TODO: 실제 구현
        # 현재는 None
        return None
    
    def _check_sum_relationship(self, project_data: Dict) -> Optional[Boundary]:
        """합산 관계 체크"""
        
        # 예: customer_count와 revenue가 있으면
        #     arpu = revenue / customer_count (관계 도출)
        
        # TODO: 실제 구현
        return None


class MathematicalDefinitionSource(PhysicalConstraintBase):
    """
    수학적 정의
    
    역할:
    -----
    - 확률 [0, 1]
    - 백분율 [0, 100]
    - 음수 불가 (특정 지표)
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """수학 정의 수집"""
        
        constraints = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 확률 범위
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self._is_probability_question(question):
            constraints.append(Boundary(
                source_type=SourceType.MATHEMATICAL,
                min_value=0.0,
                max_value=1.0,
                confidence=1.0,
                reasoning="확률은 0~1 범위 (수학적 정의)"
            ))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 백분율 범위
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self._is_percentage_question(question):
            constraints.append(Boundary(
                source_type=SourceType.MATHEMATICAL,
                min_value=0.0,
                max_value=100.0,
                confidence=1.0,
                reasoning="백분율은 0~100% 범위 (수학적 정의)"
            ))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. 음수 불가 (금액, 개수 등)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self._is_non_negative_metric(question):
            constraints.append(Boundary(
                source_type=SourceType.MATHEMATICAL,
                min_value=0.0,
                max_value=None,
                confidence=1.0,
                reasoning="금액/개수는 음수 불가"
            ))
        
        return constraints
    
    def _is_probability_question(self, question: str) -> bool:
        """확률 질문인가?"""
        keywords = ['확률', 'probability', '가능성']
        return any(kw in question.lower() for kw in keywords)
    
    def _is_percentage_question(self, question: str) -> bool:
        """백분율 질문인가?"""
        keywords = ['%', '퍼센트', '비율', 'rate', 'churn', '전환율']
        return any(kw in question.lower() for kw in keywords)
    
    def _is_non_negative_metric(self, question: str) -> bool:
        """음수 불가 지표인가?"""
        keywords = ['금액', '매출', '비용', '가격', '개수', '명', '회', '원']
        return any(kw in question for kw in keywords)

