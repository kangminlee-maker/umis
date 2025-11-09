"""
Guestimation v3.0 Data Models

모든 데이터 구조 정의 (자연어 설계 → Python 구현)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════

class SourceCategory(Enum):
    """Source Category (3가지)"""
    PHYSICAL = "physical"  # Hard Constraints
    SOFT = "soft"          # Soft Constraints  
    VALUE = "value"        # Value Sources


class SourceType(Enum):
    """Source Type (11개)"""
    # Physical (3개)
    SPACETIME = "spacetime"
    CONSERVATION = "conservation"
    MATHEMATICAL = "mathematical"
    
    # Soft (3개)
    LEGAL = "legal"
    STATISTICAL = "statistical"
    BEHAVIORAL = "behavioral"
    
    # Value (5개)
    DEFINITE_DATA = "definite_data"
    LLM_ESTIMATION = "llm_estimation"
    WEB_SEARCH = "web_search"
    RAG_BENCHMARK = "rag_benchmark"
    STATISTICAL_VALUE = "statistical_value"


class DistributionType(Enum):
    """통계 분포 유형 (7가지)"""
    NORMAL = "normal"
    POWER_LAW = "power_law"
    EXPONENTIAL = "exponential"
    BIMODAL = "bimodal"
    UNIFORM = "uniform"
    LOGNORMAL = "lognormal"
    CONDITIONAL = "conditional"


class Intent(Enum):
    """질문 의도"""
    GET_VALUE = "get_value"
    UNDERSTAND_MARKET = "understand_market"
    MAKE_DECISION = "make_decision"
    COMPARE = "compare"
    PREDICT = "predict"


class Granularity(Enum):
    """세분화 수준"""
    MACRO = "macro"
    SEGMENT = "segment"
    MICRO = "micro"


# ═══════════════════════════════════════════════════════
# Core Data Classes
# ═══════════════════════════════════════════════════════

@dataclass
class Context:
    """질문 맥락"""
    
    # 핵심 맥락
    intent: Intent = Intent.GET_VALUE
    domain: str = "General"
    granularity: Granularity = Granularity.MACRO
    
    # 시공간
    region: Optional[str] = None
    time_period: Optional[str] = None
    
    # Fermi 재귀 관련
    parent_model: Optional[Any] = None
    variable_role: Optional[str] = None
    
    # 데이터 및 제약
    project_data: Dict[str, Any] = field(default_factory=dict)
    constraints: List['Boundary'] = field(default_factory=list)
    
    # 메타
    depth: int = 0
    parent_question: Optional[str] = None


@dataclass
class Boundary:
    """Hard Constraint - 절대 한계"""
    
    source_type: SourceType
    
    # Boundary 정보
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    relationship: Optional[str] = None  # "A < B", "A + B = C"
    
    # 메타
    confidence: float = 1.0
    reasoning: str = ""
    conditions: List[str] = field(default_factory=list)
    
    # 원본
    raw_output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionInfo:
    """통계 분포 정보"""
    
    distribution_type: DistributionType
    
    # 정규분포
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    
    # Percentiles (모든 분포)
    percentiles: Dict[str, float] = field(default_factory=dict)  # {p10, p25, p50, p75, p90}
    
    # Power Law
    alpha: Optional[float] = None
    
    # 지수분포
    lambda_param: Optional[float] = None
    
    # 이봉분포
    peaks: List[Dict] = field(default_factory=list)
    
    # 조건부
    conditional_distributions: List[Dict] = field(default_factory=list)
    
    # 메타
    sample_size: Optional[int] = None
    data_year: Optional[int] = None
    cv: Optional[float] = None  # Coefficient of Variation (변동계수)


@dataclass
class SoftGuide:
    """Soft Constraint - 범위 제안, 경향성"""
    
    source_type: SourceType
    
    # 범위 정보
    suggested_range: Optional[Tuple[float, float]] = None
    typical_value: Optional[float] = None
    
    # 분포 (통계 패턴)
    distribution: Optional[DistributionInfo] = None
    
    # 정성적 통찰 (행동경제학)
    insight: Optional[str] = None
    quantitative_hint: Optional[Dict] = None
    
    # 법률 예외
    exceptions: List[Dict] = field(default_factory=list)
    
    # 메타
    confidence: float = 0.7
    reasoning: str = ""
    conditions: List[str] = field(default_factory=list)
    applicability: float = 1.0
    
    # 원본
    raw_output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValueEstimate:
    """Value Source - 구체적 값"""
    
    source_type: SourceType
    
    # 값
    value: float
    value_range: Optional[Tuple[float, float]] = None
    unit: str = ""
    
    # 신뢰도
    confidence: float = 0.7
    uncertainty: float = 0.3  # ±%
    
    # 조정 (시의성 등)
    adjusted_confidence: Optional[float] = None
    adjustment_reason: Optional[str] = None
    
    # 맥락 적합도
    relevance: float = 1.0
    reliability: float = 1.0
    recency: float = 1.0
    
    # 메타
    reasoning: str = ""
    source_detail: str = ""
    
    # 원본
    raw_data: Any = None


@dataclass
class SourceOutput:
    """통합 Source 출력 (모든 역할 표현 가능)"""
    
    source_id: str
    source_category: SourceCategory
    source_type: SourceType
    
    # 역할별 출력
    role: str  # "boundary" | "range" | "value" | "insight"
    
    # Boundary (Physical)
    boundary: Optional[Boundary] = None
    
    # Range/Insight (Soft)
    soft_guide: Optional[SoftGuide] = None
    
    # Value
    value_estimate: Optional[ValueEstimate] = None
    
    # 공통
    confidence: float = 0.7
    conditions: List[str] = field(default_factory=list)
    
    # 메타
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time: float = 0.0


@dataclass
class EstimationResult:
    """최종 추정 결과"""
    
    question: str
    
    # 최종 값
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None
    unit: str = ""
    
    # 메타 정보
    tier: int = 0  # 1, 2, 3
    confidence: float = 0.0
    uncertainty: float = 0.3
    
    # Tier 2 전용
    context: Optional[Context] = None
    
    # 수집된 Source들
    boundaries: List[Boundary] = field(default_factory=list)
    soft_guides: List[SoftGuide] = field(default_factory=list)
    value_estimates: List[ValueEstimate] = field(default_factory=list)
    
    # 판단 과정
    judgment_strategy: str = ""
    reasoning: str = ""
    logic_steps: List[str] = field(default_factory=list)
    
    # 충돌 처리
    conflicts_detected: List[Dict] = field(default_factory=list)
    conflicts_resolved: bool = True
    
    # Tier 3 (Fermi)
    fermi_model: Optional[Any] = None
    variable_results: Dict[str, 'EstimationResult'] = field(default_factory=dict)
    
    # 성능
    execution_time: float = 0.0
    cost: float = 0.0
    
    # 학습
    should_learn: bool = False
    learn_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # v7.3.2: 추정 근거 및 추적 (Single Source)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 상세 근거
    reasoning_detail: Dict[str, Any] = field(default_factory=dict)
    # {
    #   'method': 'weighted_average',
    #   'sources_used': ['statistical', 'rag'],
    #   'why_this_method': '증거 3개, 신뢰도 유사',
    #   'evidence_breakdown': [...]
    # }
    
    # Decomposition 추적 (Tier 3용, 선택)
    decomposition: Optional['DecompositionTrace'] = None
    
    # 개별 요소 추정 논리
    component_estimations: List['ComponentEstimation'] = field(default_factory=list)
    
    # 추정 과정 추적
    estimation_trace: List[str] = field(default_factory=list)
    
    def is_successful(self) -> bool:
        """추정 성공 여부"""
        return self.value is not None or self.value_range is not None
    
    def get_display_value(self) -> str:
        """표시용 값"""
        if self.value is not None:
            return f"{self.value:,.0f}{self.unit}"
        elif self.value_range:
            return f"{self.value_range[0]:,.0f} ~ {self.value_range[1]:,.0f}{self.unit}"
        return "추정 불가"


@dataclass
class ComponentEstimation:
    """
    개별 요소의 추정 논리 (v7.3.2)
    
    예: "월결제액 = 10,000원"을 어떻게 추정했는지 기록
    """
    component_name: str  # "월결제액"
    component_value: float  # 10,000
    estimation_method: str  # "statistical_pattern"
    reasoning: str  # "SaaS 평균 요금 분포"
    confidence: float  # 0.75
    sources: List[str] = field(default_factory=list)  # ["rag_benchmark"]
    
    # 추가 메타
    raw_data: Any = None


@dataclass
class DecompositionTrace:
    """
    Decomposition 추적 (v7.3.2 - Tier 3용)
    
    Fermi처럼 분해한 경우의 이력
    예: ARPU = 월결제액 / 활성사용자
    """
    formula: str  # "ARPU = 월결제액 / 활성사용자"
    variables: Dict[str, EstimationResult] = field(default_factory=dict)
    # {
    #   '월결제액': EstimationResult(...),
    #   '활성사용자': EstimationResult(...)
    # }
    calculation_logic: str = ""  # 계산 논리 설명
    depth: int = 0  # 재귀 깊이 (max 4)
    
    # 추가 메타
    decomposition_reasoning: str = ""  # 왜 이렇게 분해했는지


# ═══════════════════════════════════════════════════════
# 학습 관련
# ═══════════════════════════════════════════════════════

@dataclass
class LearnedRule:
    """학습된 규칙 (Tier 1 편입용)"""
    
    rule_id: str
    
    # 질문 패턴
    question_original: str
    question_normalized: str
    question_template: str
    question_keywords: List[str] = field(default_factory=list)
    
    # 맥락
    context: Context = field(default_factory=Context)
    
    # 결과
    value: float = 0.0
    value_range: Tuple[float, float] = (0.0, 0.0)
    unit: str = ""
    confidence: float = 0.0
    uncertainty: float = 0.3
    
    # 출처
    tier_origin: str = ""  # "tier2" | "tier3" | "user_contributed"
    sources: List[str] = field(default_factory=list)
    judgment_strategy: str = ""
    evidence_count: int = 0
    
    # 통계
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    last_verified: str = field(default_factory=lambda: datetime.now().date().isoformat())
    
    # 사용자 기여 (조건부)
    contributors: List[Dict] = field(default_factory=list)
    verification: Optional[Dict] = None


@dataclass
class UserFact:
    """사용자 기여 데이터"""
    
    fact_id: str
    
    # 분류
    fact_type: str  # "definite" | "industry_common" | "personal_experience"
    scope: str  # "project" | "domain" | "global"
    
    # 진술
    statement_original: str
    statement_normalized: str
    
    # 값
    metric: str
    value: float
    unit: str = ""
    value_type: str = "point"  # "point" | "range" | "distribution"
    
    # 맥락
    project_id: Optional[str] = None
    user_id: str = ""
    domain: str = "General"
    region: Optional[str] = None
    time_period: Optional[str] = None
    
    # 출처
    source_type: str = "user_stated"  # "user_stated" | "user_file" | "user_experience"
    confidence_claim: str = ""  # "확실" | "들었음" | "경험상"
    
    # 검증
    verification_status: str = "pending"  # "pending" | "passed" | "failed"
    verification_method: Optional[str] = None
    
    # 통계
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════
# 설정 관련
# ═══════════════════════════════════════════════════════

@dataclass
class Tier1Config:
    """Tier 1 설정"""
    enabled: bool = True
    
    # 임계값
    min_similarity: float = 0.95  # RAG 검색 (v7.5.0: 0.85→0.95 강화, Tier 3 집중)
    
    # Built-in 규칙
    builtin_rules_count: int = 20
    
    # 성능
    timeout_seconds: float = 0.5


@dataclass
class Tier2Config:
    """Tier 2 설정"""
    enabled: bool = True
    
    # 임계값
    min_confidence: float = 0.80  # v7.5.0: 0.60→0.80 강화, Tier 3 집중
    min_evidence_count: int = 2
    max_evidence_count: int = 5
    
    # 수집
    collection_mode: str = "parallel"  # "parallel" | "sequential"
    
    # 판단
    judgment_strategy: str = "auto"  # "auto" | "weighted_average" | ...
    
    # 성능
    timeout_seconds: float = 8.0


@dataclass
class Tier3Config:
    """Tier 3 설정"""
    enabled: bool = True
    
    # Fermi
    max_depth: int = 4
    force_judgment_at_max_depth: bool = True
    
    # 성능
    timeout_seconds: float = 30.0


@dataclass
class GuestimationConfig:
    """전체 시스템 설정"""
    
    tier1: Tier1Config = field(default_factory=Tier1Config)
    tier2: Tier2Config = field(default_factory=Tier2Config)
    tier3: Tier3Config = field(default_factory=Tier3Config)
    
    # LLM 모드
    llm_mode: str = "native"  # "native" | "external" | "skip"
    
    # 웹 검색
    web_search_enabled: bool = True
    
    # 학습
    learning_enabled: bool = True
    learning_threshold_usage: int = 10
    learning_threshold_confidence: float = 0.85
    
    # 로깅
    verbose: bool = False
    log_all_sources: bool = True

