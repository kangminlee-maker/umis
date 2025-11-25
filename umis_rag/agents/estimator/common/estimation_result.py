"""
EstimationResult - 통합 추정 결과 인터페이스 (v7.11.0)

모든 Estimation Engine (Evidence, Prior, Fermi)이 동일한 인터페이스로 결과를 반환합니다.

설계 원칙:
- 모든 추정 엔진은 동일한 EstimationResult를 반환
- "증거 기반 confidence"가 아닌 "LLM 내적 certainty"를 사용
- 비용(cost) 추적으로 예산 소비 가시화
- 융합(Fusion)에 필요한 모든 정보 포함
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


@dataclass
class Evidence:
    """
    증거 / 가드레일 (v7.11.0)

    Evidence는 "확정된 사실" 또는 "논리적/경험적 제약"을 나타냅니다.

    Attributes:
        definite_value: 확정 값 (Phase 0, 1, 2에서 발견)
        hard_bounds: 논리적 상/하한 (절대 위반 불가)
        soft_hints: 경험적 가이드 (위반 가능하지만 경고)
        logical_relations: 논리적 관계식 (예: "LTV = ARPU / Churn")
        source: 증거 출처 (예: "Phase 2 Validator", "Guardrail Engine")
        confidence: 증거 신뢰도 (0.0-1.0)
        reasoning: 증거 발견 과정
    """
    # 확정 값 (있으면 이게 정답)
    definite_value: Optional[float] = None

    # Hard Constraints (논리적 제약)
    hard_bounds: Optional[Tuple[float, float]] = None  # (min, max)

    # Soft Hints (경험적 가이드)
    soft_hints: List[Dict[str, Any]] = field(default_factory=list)
    # [{'type': 'range', 'min': 1000, 'max': 5000, 'source': '...'}]

    # 논리적 관계식
    logical_relations: List[str] = field(default_factory=list)
    # ['LTV = ARPU / Churn', 'Revenue = Users * ARPU']

    # 메타데이터
    source: str = ""
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class EstimationResult:
    """
    통합 추정 결과 (v7.11.0)

    모든 Estimation Engine이 반환하는 공통 인터페이스

    Attributes:
        value: 추정 값
        value_range: 값 범위 (min, max)
        
        certainty: LLM의 내적 확신도 (high/medium/low)
        uncertainty: 불확실성 (0.0-1.0, 낮을수록 확실)
        
        cost: 비용 정보 (llm_calls, variables, time)
        
        decomposition: Fermi 분해 구조 (있으면)
        used_evidence: 사용된 증거 목록
        fusion_weights: Fusion Layer가 부여한 가중치 (융합 결과만)
        
        source: 추정 엔진 식별 (예: "Evidence", "Prior", "Fermi")
        reasoning: 추정 근거
        metadata: 추가 정보
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 핵심 추정 값
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    value: float
    value_range: Optional[Tuple[float, float]] = None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 확신도 (v7.11.0: confidence → certainty)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    certainty: str = "medium"  # "high", "medium", "low"
    uncertainty: float = 0.5   # 0.0-1.0 (낮을수록 확실)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 비용 추적 (v7.11.0)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    cost: Dict[str, Any] = field(default_factory=dict)
    # {'llm_calls': 3, 'variables': 5, 'time': 12.3}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 추정 구조 (Fermi용)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    decomposition: Optional[Dict[str, Any]] = None
    # {
    #   'formula': 'LTV = ARPU / Churn',
    #   'variables': {'ARPU': result1, 'Churn': result2},
    #   'depth': 1
    # }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 증거 및 융합 정보
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    used_evidence: List[Evidence] = field(default_factory=list)
    fusion_weights: Optional[Dict[str, float]] = None
    # {'evidence': 0.7, 'prior': 0.2, 'fermi': 0.1}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메타데이터
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    source: str = ""  # "Evidence", "Prior", "Fermi", "Fusion"
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 타임스탬프
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    created_at: datetime = field(default_factory=datetime.now)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Helper Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def is_definite(self) -> bool:
        """
        확정 값 여부 (증거 기반)
        
        Returns:
            used_evidence에 definite_value가 있으면 True
        """
        return any(
            ev.definite_value is not None
            for ev in self.used_evidence
        )
    
    def get_certainty_score(self) -> float:
        """
        Certainty를 0-1 스케일로 변환
        
        Returns:
            high: 0.9, medium: 0.6, low: 0.3
        """
        mapping = {
            'high': 0.9,
            'medium': 0.6,
            'low': 0.3
        }
        return mapping.get(self.certainty, 0.5)
    
    def get_cost_summary(self) -> str:
        """
        비용 요약 문자열
        
        Returns:
            예: "3 LLM calls, 5 vars, 12.3s"
        """
        llm = self.cost.get('llm_calls', 0)
        vars = self.cost.get('variables', 0)
        time = self.cost.get('time', 0.0)
        return f"{llm} LLM calls, {vars} vars, {time:.1f}s"
    
    def is_within_bounds(self, min_val: Optional[float], max_val: Optional[float]) -> bool:
        """
        값이 범위 내에 있는지 확인
        
        Args:
            min_val: 최소값 (None이면 무시)
            max_val: 최대값 (None이면 무시)
        
        Returns:
            범위 내에 있으면 True
        """
        if min_val is not None and self.value < min_val:
            return False
        if max_val is not None and self.value > max_val:
            return False
        return True
    
    def clip_to_bounds(self, min_val: Optional[float], max_val: Optional[float]) -> float:
        """
        값을 범위로 클리핑
        
        Args:
            min_val: 최소값 (None이면 무시)
            max_val: 최대값 (None이면 무시)
        
        Returns:
            클리핑된 값
        """
        result = self.value
        if min_val is not None:
            result = max(result, min_val)
        if max_val is not None:
            result = min(result, max_val)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환 (JSON 직렬화용)
        
        Returns:
            딕셔너리 형태의 결과
        """
        return {
            'value': self.value,
            'value_range': self.value_range,
            'certainty': self.certainty,
            'uncertainty': self.uncertainty,
            'cost': self.cost,
            'source': self.source,
            'reasoning': self.reasoning,
            'decomposition': self.decomposition,
            'fusion_weights': self.fusion_weights,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        """간결한 표현"""
        return (
            f"EstimationResult(value={self.value:,.0f}, "
            f"certainty={self.certainty}, "
            f"source={self.source})"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Factory Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_definite_result(
    value: float,
    evidence: Evidence,
    reasoning: str = ""
) -> EstimationResult:
    """
    확정 값 결과 생성 (Phase 0-2)
    
    Args:
        value: 확정 값
        evidence: 증거
        reasoning: 근거
    
    Returns:
        EstimationResult (certainty=high, uncertainty=0.0)
    """
    return EstimationResult(
        value=value,
        certainty="high",
        uncertainty=0.0,
        used_evidence=[evidence],
        source="Evidence",
        reasoning=reasoning,
        cost={'llm_calls': 0, 'variables': 0, 'time': 0.0}
    )


def create_prior_result(
    value: float,
    value_range: Tuple[float, float],
    certainty: str,
    reasoning: str,
    llm_calls: int = 1
) -> EstimationResult:
    """
    Prior 추정 결과 생성 (Phase 3)
    
    Args:
        value: 추정 값
        value_range: 값 범위
        certainty: 확신도 (high/medium/low)
        reasoning: 추정 근거
        llm_calls: LLM 호출 횟수
    
    Returns:
        EstimationResult
    """
    uncertainty_map = {'high': 0.1, 'medium': 0.3, 'low': 0.5}
    
    return EstimationResult(
        value=value,
        value_range=value_range,
        certainty=certainty,
        uncertainty=uncertainty_map.get(certainty, 0.3),
        source="Prior",
        reasoning=reasoning,
        cost={'llm_calls': llm_calls, 'variables': 1, 'time': 0.0}
    )


def create_fermi_result(
    value: float,
    decomposition: Dict[str, Any],
    certainty: str,
    reasoning: str,
    cost: Dict[str, Any]
) -> EstimationResult:
    """
    Fermi 분해 결과 생성 (Phase 4)
    
    Args:
        value: 계산된 값
        decomposition: 분해 구조
        certainty: 확신도
        reasoning: 분해 과정 설명
        cost: 비용 정보
    
    Returns:
        EstimationResult
    """
    return EstimationResult(
        value=value,
        decomposition=decomposition,
        certainty=certainty,
        uncertainty=0.3,
        source="Fermi",
        reasoning=reasoning,
        cost=cost
    )
