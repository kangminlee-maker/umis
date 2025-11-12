"""
Physical Constraints Sources (v7.8.0 재설계)

개념 기반 상한/하한 (의미 있는 제약만)
- 개념 타입 추출 (rate, count, income, consumption)
- 개념별 명백한 상한/하한
- 너무 넓은 범위는 제공 안 함

v7.8.0 핵심 변경:
------------------
- 샘플 데이터 제거 → 개념 기반 접근
- 의미 있는 제약만 (범위 10,000배 이하)
- 3개 클래스 통합 고려
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


class UnifiedPhysicalConstraintSource:
    """
    통합 Physical Constraints (v7.8.0)
    
    역할:
    -----
    - 개념 기반 상한/하한 도출
    - 의미 있는 제약만 제공
    - 너무 넓은 범위 제외
    
    개념 타입:
    ---------
    - rate: 0.0 ~ 1.0 (항상 의미 있음)
    - consumption: 0 ~ 인구 × 최대소비
    - duration: 0 ~ 현실적 최대
    - count/size/income: 상한 설정 어려움
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[Boundary]:
        """
        개념 기반 Boundary 수집
        
        프로세스:
        1. 개념 타입 추출
        2. 개념별 상한/하한 생성
        3. 범위 의미성 검증
        """
        
        # Step 1: 개념 타입 추출
        concept_type = self._extract_concept_type(question)
        
        if not concept_type:
            return []  # 개념 파악 불가
        
        # Step 2: 개념별 Boundary 생성
        boundary = self._create_boundary_for_concept(
            concept_type=concept_type,
            question=question,
            context=context
        )
        
        if not boundary:
            return []
        
        # Step 3: 범위 의미성 검증
        if self._is_range_too_wide(boundary):
            logger.info(f"  [Physical] 범위 너무 넓음 → 제공 안 함")
            return []
        
        min_val = boundary.min_value if boundary.min_value else 0
        max_val = boundary.max_value if boundary.max_value else 0
        logger.info(f"  [Physical] Boundary: [{min_val:,.0f}, {max_val:,.0f}]")
        return [boundary]
    
    def _extract_concept_type(self, question: str) -> Optional[str]:
        """
        개념 타입 추출
        
        Returns:
            "rate"         - 비율 (0-1)
            "count"        - 개수
            "size"         - 크기
            "income"       - 소득
            "duration"     - 기간
            "consumption"  - 소비량
            None           - 파악 불가
        """
        
        # Rate (비율) - 가장 명확
        rate_keywords = ['률', 'rate', 'churn', '전환', '점유율', '성장률', '%']
        if any(kw in question.lower() for kw in rate_keywords):
            return "rate"
        
        # Consumption (소비량)
        consumption_keywords = ['판매량', '소비량', '사용량', '구매량']
        if any(kw in question.lower() for kw in consumption_keywords):
            return "consumption"
        
        # Duration (기간)
        duration_keywords = ['ltv', 'lifetime', 'payback', '기간', '개월']
        if any(kw in question.lower() for kw in duration_keywords):
            return "duration"
        
        # Count (개수)
        count_keywords = ['수', '개수', '인구', '고객 수', '사용자 수', '명']
        if any(kw in question.lower() for kw in count_keywords):
            return "count"
        
        # Income (소득)
        income_keywords = ['arpu', '임금', '소득', '수익']
        if any(kw in question.lower() for kw in income_keywords):
            return "income"
        
        # Size (크기)
        size_keywords = ['규모', '면적', '크기', 'tam', 'sam']
        if any(kw in question.lower() for kw in size_keywords):
            return "size"
        
        return None
    
    def _create_boundary_for_concept(
        self,
        concept_type: str,
        question: str,
        context: Optional[Context]
    ) -> Optional[Boundary]:
        """
        개념별 Boundary 생성
        
        원칙: 개념적으로 명백한 상한/하한만
        """
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Rate (비율): 0.0 ~ 1.0 (항상 의미 있음)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "rate":
            return Boundary(
                source_type=SourceType.PHYSICAL,
                min_value=0.0,
                max_value=1.0,
                confidence=1.0,
                reasoning="비율의 수학적 범위 (0-100%)"
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Duration: Payback은 상한 있음
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "duration":
            if "payback" in question.lower():
                return Boundary(
                    source_type=SourceType.PHYSICAL,
                    min_value=0.0,
                    max_value=120.0,  # 10년 (월 단위)
                    confidence=0.90,
                    reasoning="Payback > 10년은 비현실적 (비즈니스 지속 어려움)"
                )
            
            return None  # LTV 등은 상한 설정 어려움
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Consumption: 인구 기반 상한 (의미 있는 경우만)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == "consumption":
            # 담배 판매량 (명확한 케이스)
            if "담배" in question and context and context.region:
                if "한국" in context.region or "korea" in context.region.lower():
                    adult_population = 40_000_000  # 한국 성인 인구
                    max_per_person = 3  # 갑/일 (헤비 스모커 최대)
                    
                    upper = adult_population * max_per_person
                    
                    return Boundary(
                        source_type=SourceType.PHYSICAL,
                        min_value=0.0,
                        max_value=upper,
                        confidence=0.85,
                        reasoning=f"한국 성인 {adult_population:,}명 × 최대 3갑/일 = {upper:,}갑"
                    )
            
            # 일반 소비량: 인구 기반 추정 어려움
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Count, Size, Income: 상한 설정 어려움
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        return None
    
    def _is_range_too_wide(self, boundary: Boundary) -> bool:
        """
        범위가 너무 넓은지 검증
        
        기준: max/min > 10,000 이면 무의미
        """
        
        min_val = boundary.min_value if boundary.min_value else 0
        max_val = boundary.max_value if boundary.max_value else 0
        
        if min_val <= 0:
            # 하한이 0이면 범위 무한대 → 체크 필요
            if max_val > 1e15:  # 1000조 이상
                return True
            return False  # 0이지만 상한이 합리적이면 OK
        
        ratio = max_val / min_val
        
        if ratio > 10_000:
            logger.debug(f"    범위 비율: {ratio:,.0f}배 (너무 넓음)")
            return True
        
        return False


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

