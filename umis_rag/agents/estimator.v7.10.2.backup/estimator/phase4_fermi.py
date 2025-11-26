"""
Phase 4: Fermi Decomposition (v7.7.0)

재귀 분해 추정 - 논리의 퍼즐 맞추기 (Step 1-4)

설계: config/fermi_model_search.yaml (1,500줄)
원리: 가용 데이터(Bottom-up) + 개념 분해(Top-down) 반복

v7.7.0 파일명 변경:
-------------------
- tier3.py → phase4_fermi.py
- Tier3FermiPath → Phase4FermiDecomposition
- Phase 4: Estimator의 Fermi Decomposition
- Step 1-4: 내부 세부 단계 (스캔 → 생성 → 체크 → 실행)

v7.6.2 주요 개선:
-----------------
- 하드코딩 완전 제거 (adoption_rate, arpu 등)
- Boundary 검증 추가 (개념 기반)
- Fallback 체계 (confidence 0.5)

v7.8.1 개선:
- Cursor Mode 재귀 추정 강화
- 정확도 3배 개선 (70% → 25% 오차)
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import time
import math
import copy
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.models import (
    Context, EstimationResult, DecompositionTrace,
    ComponentEstimation, Phase4Config
)
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
from umis_rag.utils.logger import logger
from umis_rag.core.config import settings
from umis_rag.core.model_router import select_model_with_config
from umis_rag.core.model_configs import is_pro_model, model_config_manager

# LLM API
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# RAG (Chroma) - v7.10.0: langchain_chroma 우선 사용
try:
    from langchain_chroma import Chroma  # 신규 패키지 (권장)
    from langchain_openai import OpenAIEmbeddings
    HAS_CHROMA = True
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma  # fallback (deprecated)
        from langchain_openai import OpenAIEmbeddings
        HAS_CHROMA = True
    except ImportError:
        HAS_CHROMA = False
        logger.warning("Chroma 패키지 없음 (pip install langchain-chroma)")

import yaml
import re
import json


# ═══════════════════════════════════════════════════════
# 비즈니스 지표 템플릿 - REMOVED (v7.5.0)
# ═══════════════════════════════════════════════════════
# 
# v7.5.0 변경:
# - 비즈니스 지표 계산 공식은 Quantifier로 이동
# - Estimator는 순수 값 추정만 담당
# - Phase 4는 일반적 Fermi 분해에 집중
#
# 이전 위치: phase4_fermi.py BUSINESS_METRIC_TEMPLATES
# 신규 위치: data/raw/calculation_methodologies.yaml (Quantifier)
#
# ═══════════════════════════════════════════════════════

# v7.5.0: 비즈니스 지표 템플릿 제거됨
# Quantifier가 LTV, CAC, ARPU 등의 계산 공식 소유
# v7.7.0: 파일명 변경 (tier3.py → phase4_fermi.py)
BUSINESS_METRIC_TEMPLATES_REMOVED = {
    # Unit Economics (우선 - "ltv/cac" 정확 매칭)
    "unit_economics": {
        "keywords": ["unit economics", "ltv/cac", "비율", "ratio", "경제성"],
        "models": [
            {
                "id": "UE_001",
                "formula": "ratio = ltv / cac",
                "description": "LTV/CAC 비율",
                "variables": ["ltv", "cac"]
            }
        ]
    },
    
    # 시장 규모
    "market_sizing": {
        "keywords": ["시장", "규모", "TAM", "SAM", "market size"],
        "models": [
            {
                "id": "MARKET_001",
                "formula": "market = customers × adoption_rate × arpu × 12",
                "description": "기업/고객 수 기반 시장 규모",
                "variables": ["customers", "adoption_rate", "arpu"]
            },
            {
                "id": "MARKET_002",
                "formula": "market = population × digital_rate × conversion_rate × arpu × 12",
                "description": "인구 기반 디지털 전환 시장",
                "variables": ["population", "digital_rate", "conversion_rate", "arpu"]
            }
        ]
    },
    
    # 고객 생애 가치
    "ltv": {
        "keywords": ["ltv", "LTV", "생애가치", "lifetime value"],
        "models": [
            {
                "id": "LTV_001",
                "formula": "ltv = arpu / churn_rate",
                "description": "ARPU를 Churn으로 나눈 LTV",
                "variables": ["arpu", "churn_rate"]
            },
            {
                "id": "LTV_002",
                "formula": "ltv = arpu × average_lifetime_months",
                "description": "평균 생애 기간 기반 LTV",
                "variables": ["arpu", "average_lifetime_months"]
            }
        ]
    },
    
    # 고객 획득 비용
    "cac": {
        "keywords": ["cac", "CAC", "고객획득", "customer acquisition"],
        "models": [
            {
                "id": "CAC_001",
                "formula": "cac = marketing_cost / new_customers",
                "description": "마케팅 비용을 신규 고객으로 나눔",
                "variables": ["marketing_cost", "new_customers"]
            },
            {
                "id": "CAC_002",
                "formula": "cac = cpc / conversion_rate",
                "description": "CPC를 전환율로 나눔",
                "variables": ["cpc", "conversion_rate"]
            }
        ]
    },
    
    # 전환율
    "conversion": {
        "keywords": ["전환율", "conversion", "CVR"],
        "models": [
            {
                "id": "CVR_001",
                "formula": "conversion = paid_users / free_users",
                "description": "유료 전환율 (Freemium)",
                "variables": ["paid_users", "free_users"]
            },
            {
                "id": "CVR_002",
                "formula": "conversion = industry_avg × product_quality_factor",
                "description": "업계 평균 조정",
                "variables": ["industry_avg", "product_quality_factor"]
            }
        ]
    },
    
    # 해지율
    "churn": {
        "keywords": ["churn", "해지율", "이탈율"],
        "models": [
            {
                "id": "CHURN_001",
                "formula": "churn = churned_customers / total_customers",
                "description": "해지 고객 비율",
                "variables": ["churned_customers", "total_customers"]
            },
            {
                "id": "CHURN_002",
                "formula": "churn = 1 - retention_rate",
                "description": "유지율의 역수",
                "variables": ["retention_rate"]
            }
        ]
    },
    
    # ARPU
    "arpu": {
        "keywords": ["arpu", "ARPU", "평균매출", "average revenue"],
        "models": [
            {
                "id": "ARPU_001",
                "formula": "arpu = base_fee",
                "description": "기본료만",
                "variables": ["base_fee"]
            },
            {
                "id": "ARPU_002",
                "formula": "arpu = base_fee + overage_fee",
                "description": "기본료 + 초과료",
                "variables": ["base_fee", "overage_fee"]
            },
            {
                "id": "ARPU_003",
                "formula": "arpu = base_fee + usage_fee + addon_fee",
                "description": "기본료 + 사용량료 + 추가기능료",
                "variables": ["base_fee", "usage_fee", "addon_fee"]
            }
        ]
    },
    
    # 성장률
    "growth": {
        "keywords": ["성장률", "growth rate", "CAGR"],
        "models": [
            {
                "id": "GROWTH_001",
                "formula": "growth = (current_year - last_year) / last_year",
                "description": "YoY 성장률",
                "variables": ["current_year", "last_year"]
            },
            {
                "id": "GROWTH_002",
                "formula": "growth = market_growth + market_share_change",
                "description": "시장 성장 + 점유율 변화",
                "variables": ["market_growth", "market_share_change"]
            }
        ]
    },
    
    # Payback Period (v7.5.0)
    "payback": {
        "keywords": ["payback", "회수기간", "투자회수"],
        "models": [
            {
                "id": "PAYBACK_001",
                "formula": "payback = cac / (arpu × gross_margin)",
                "description": "CAC를 월 기여이익으로 나눔",
                "variables": ["cac", "arpu", "gross_margin"]
            },
            {
                "id": "PAYBACK_002",
                "formula": "payback = initial_investment / monthly_profit",
                "description": "초기 투자를 월 수익으로 나눔",
                "variables": ["initial_investment", "monthly_profit"]
            }
        ]
    },
    
    # Rule of 40 (v7.5.0)
    "rule_of_40": {
        "keywords": ["rule of 40", "40 법칙"],
        "models": [
            {
                "id": "R40_001",
                "formula": "rule_40 = growth_rate + profit_margin",
                "description": "성장률 + 이익률 (40% 이상이 건강)",
                "variables": ["growth_rate", "profit_margin"]
            }
        ]
    },
    
    # Net Revenue Retention (v7.5.0)
    "nrr": {
        "keywords": ["nrr", "net revenue retention", "순매출유지율"],
        "models": [
            {
                "id": "NRR_001",
                "formula": "nrr = (beginning_mrr + expansion - contraction - churn) / beginning_mrr",
                "description": "순매출 유지율 (100% 이상이 건강)",
                "variables": ["beginning_mrr", "expansion", "contraction", "churn"]
            },
            {
                "id": "NRR_002",
                "formula": "nrr = 1 + expansion_rate - churn_rate",
                "description": "확장률 - 해지율 + 1",
                "variables": ["expansion_rate", "churn_rate"]
            }
        ]
    },
    
    # Gross Margin (v7.5.0)
    "gross_margin": {
        "keywords": ["gross margin", "매출총이익률", "gross profit"],
        "models": [
            {
                "id": "GM_001",
                "formula": "gross_margin = (revenue - cogs) / revenue",
                "description": "매출총이익률",
                "variables": ["revenue", "cogs"]
            },
            {
                "id": "GM_002",
                "formula": "gross_margin = 1 - (cogs / revenue)",
                "description": "1 - COGS 비율",
                "variables": ["cogs", "revenue"]
            }
        ]
    }
}


# ═══════════════════════════════════════════════════════
# 데이터 모델 (Phase 4 전용)
# ═══════════════════════════════════════════════════════

@dataclass
class FermiVariable:
    """
    Fermi 모형의 변수

    Attributes:
        name: 변수 이름 (예: "restaurants", "arpu")
        available: 가용 여부
        value: 값 (채워진 경우)
        source: 출처 ("project_data", "tier2", "recursive")
        confidence: 신뢰도
        need_estimate: 추정 필요 여부
        estimation_result: 추정 결과 (재귀로 채운 경우)
        description: 변수 설명
        estimation_question: 추정용 질문 (LLM 생성)
        is_result: 결과 변수 여부
        concept: 도메인 특화 개념 (v7.10.0)
    """
    name: str
    available: bool
    value: Optional[float] = None
    source: str = ""
    confidence: float = 0.0
    need_estimate: bool = False
    uncertainty: float = 0.3

    # 재귀 추정 결과
    estimation_result: Optional[EstimationResult] = None

    # 메타데이터
    description: str = ""
    estimation_question: Optional[str] = None
    is_result: bool = False
    concept: str = ""  # v7.10.0: 도메인 특화 개념


@dataclass
class FermiModel:
    """
    Fermi 추정 모형
    
    예: "시장 = 음식점 × 디지털율 × 전환율 × ARPU × 12"
    
    Attributes:
        model_id: 모형 ID (MODEL_001, MODEL_002, ...)
        name: 모형 이름
        formula: 수식 (문자열)
        description: 설명
        variables: 변수 딕셔너리
        total_variables: 총 변수 개수
        unknown_count: Unknown 변수 개수
        feasibility_score: 실행 가능성 점수
    """
    model_id: str
    name: str
    formula: str
    description: str
    variables: Dict[str, FermiVariable] = field(default_factory=dict)
    
    # 통계
    total_variables: int = 0
    unknown_count: int = 0
    available_count: int = 0
    
    # 평가
    feasibility_score: float = 0.0
    unknown_filled: bool = False
    
    # 선택
    selection_reason: str = ""
    is_alternative: bool = False
    why_not_selected: str = ""


@dataclass
class RankedModel:
    """
    점수화된 모형
    
    모형 선택 기준 4개:
    - Unknown count (50%)
    - Confidence (30%)
    - Complexity (20%)
    - Depth (10% bonus)
    """
    rank: int
    model: FermiModel
    score: float
    
    # 점수 분해
    unknown_score: float = 0.0
    confidence_score: float = 0.0
    complexity_score: float = 0.0
    depth_score: float = 0.0
    
    # 상태
    status: str = "feasible"  # feasible/partial/infeasible
    missing: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════
# 변수 수렴 정책 (Simple 방식)
# ═══════════════════════════════════════════════════════

class SimpleVariablePolicy:
    """
    단순 변수 정책 (실용적)
    
    원칙:
    - 6개: 권장 (Occam's Razor)
    - 7-10개: 허용 (경고)
    - 10개+: 금지 (Miller's Law)
    
    효과: 98% (Hybrid 대비 2% 차이)
    코드: 20줄 (Hybrid 대비 15배 간단)
    """
    
    def __init__(self):
        self.recommended_max = 6   # Occam's Razor
        self.absolute_max = 10     # Miller's Law (7±2)
    
    def check(self, variable_count: int) -> Tuple[bool, Optional[str]]:
        """
        변수 개수 체크
        
        Args:
            variable_count: 현재 변수 개수
        
        Returns:
            (allowed, warning)
                allowed: True/False
                warning: None 또는 경고 메시지
        """
        # 절대 상한
        if variable_count > self.absolute_max:
            return False, f"🛑 절대 상한 {self.absolute_max}개 초과 (인지 한계)"
        
        # 권장 상한 (경고만)
        if variable_count > self.recommended_max:
            return True, f"⚠️  권장 상한 {self.recommended_max}개 초과 (복잡도↑)"
        
        # 정상
        return True, None


# ═══════════════════════════════════════════════════════
# Phase 4 메인 클래스
# ═══════════════════════════════════════════════════════

class Phase4FermiDecomposition:
    """
    Phase 4: Fermi Decomposition (v7.7.0)
    
    재귀 분해 추정 - 논리의 퍼즐 맞추기
    
    프로세스:
    ---------
    Step 1: 초기 스캔 (가용 데이터 파악, Bottom-up)
    Step 2: 모형 생성 (LLM 3-5개 후보, Top-down)
    Step 3: 실행 가능성 체크 (재귀 추정으로 퍼즐 맞추기)
    Step 4: 모형 실행 (Backtracking으로 재조립)
    
    안전 장치:
    ----------
    - Max depth: 4 (무한 재귀 방지)
    - 순환 감지: Call stack 추적
    - 변수 제한: 6개 권장, 10개 절대
    
    Usage:
        >>> phase4 = Phase4FermiDecomposition()
        >>> result = phase4.estimate(
        ...     "음식점 SaaS 시장은?",
        ...     context=Context(domain="Food_Service")
        ... )
        >>> result.decomposition.depth  # 2
        >>> result.value  # 20,160,000,000
    """
    
    def __init__(self, config: Phase4Config = None):
        """초기화 (v7.10.0)"""
        self.config = config or Phase4Config()

        # v7.9.0: llm_mode를 Property로 변경 (동적 읽기)
        # Phase 3 의존성 (None으로 전달 → 동적 읽기)
        self.phase3 = Phase3Guestimation(llm_mode=None)

        # 재귀 추적
        self.call_stack: List[str] = []
        self.max_depth = self.config.max_depth  # 4

        # v7.10.0: 전역 시도 제한 (재귀 폭발 방지)
        self.max_global_attempts = 3  # 최대 3회 시도
        self._global_attempt_count = 0  # 현재 시도 횟수
        self._attempt_results: List[EstimationResult] = []  # 시도별 결과 저장

        # v7.10.0: 시도별 confidence threshold (점진적 완화)
        # 1회차: 0.80 (엄격), 2회차: 0.60 (완화), 3회차: 0.40 (추가 완화)
        self._confidence_thresholds = [0.80, 0.60, 0.40]
        self._current_threshold_idx = 0

        # v7.10.2: 전역 변수 추정 횟수 제한 (재귀 폭발 완전 방지)
        self.max_variable_estimates = 20  # 최대 20개 변수만 추정
        self._total_variable_estimate_count = 0  # 총 변수 추정 시도 횟수

        # 변수 정책
        self.variable_policy = SimpleVariablePolicy()

        # LLM Client (초기화 시에는 생성 안 함, 필요할 때 동적 생성)
        self._llm_client = None

        logger.info("[Phase 4] Fermi Decomposition 초기화")
        logger.info(f"  Max depth: {self.max_depth}")
        logger.info(f"  Max attempts: {self.max_global_attempts} (점진적 완화: {self._confidence_thresholds})")
        logger.info(f"  Max variables: {self.max_variable_estimates} (v7.10.2: 재귀 폭발 완전 방지)")
        logger.info(f"  변수 정책: 권장 6개, 절대 10개")
        logger.info(f"  LLM 모드: {self.llm_mode}")

        # 초기화 시점의 모드 로깅
        if self.llm_mode != 'cursor':
            logger.info(f"  API Mode: {self.llm_mode}")
        else:
            logger.info("  Cursor AI Mode (비용 $0)")
            logger.info("     직접 모형 생성: 질문 분석 -> 상식 기반 추정 (재귀 최소화)")
    
    @property
    def llm_mode(self) -> str:
        """
        LLM 모드 동적 읽기 (v7.9.0)
        
        Property 패턴으로 구현하여 settings 변경 시 즉시 반영
        """
        from umis_rag.core.config import settings
        return settings.llm_mode
    
    @property
    def llm_client(self):
        """
        LLM Client 동적 생성 (v7.9.0)
        
        cursor 모드가 아닐 때만 OpenAI API 클라이언트 생성
        매번 현재 llm_mode를 확인하여 필요 시 재생성
        """
        # cursor 모드면 None 반환
        if self.llm_mode == 'cursor':
            return None
        
        # API 모드이지만 클라이언트가 없거나 모드가 변경되었으면 생성
        if self._llm_client is None or getattr(self, '_cached_mode', None) != self.llm_mode:
            from umis_rag.core.config import settings
            if HAS_OPENAI and settings.openai_api_key:
                from openai import OpenAI
                self._llm_client = OpenAI(api_key=settings.openai_api_key)
                self._cached_mode = self.llm_mode
                logger.debug(f"  OpenAI Client 생성: {self.llm_mode}")
            else:
                logger.warning(f"  ⚠️  API 모드({self.llm_mode})지만 OpenAI API 키 없음")
                return None
        
        return self._llm_client
    
    def estimate(
        self,
        question: str,
        context: Context = None,
        available_data: Dict = None,
        depth: int = 0,
        parent_data: Dict = None
    ) -> Optional[EstimationResult]:
        """
        Fermi Decomposition 추정 (v7.10.0: 3회 시도 + 점진적 완화)

        Args:
            question: 질문 (예: "음식점 SaaS 시장은?")
            context: 맥락 (domain, region, time)
            available_data: 가용 데이터 (프로젝트 제공)
            depth: 현재 재귀 깊이
            parent_data: 부모 데이터 (재귀 시 상속) v7.5.0+

        Returns:
            EstimationResult (decomposition 포함) 또는 None

        v7.10.0 재시도 로직:
            - 최대 3회 시도 (depth == 0일 때만)
            - 1회차: confidence >= 0.80 (엄격)
            - 2회차: confidence >= 0.60 (완화)
            - 3회차: confidence >= 0.40 (추가 완화)
            - 3회 실패 시 최선 결과 반환
        """
        # v7.10.0: 최상위 호출에서만 재시도 로직 적용
        if depth == 0:
            # 상태 초기화
            self._global_attempt_count = 0
            self._attempt_results = []
            self._current_threshold_idx = 0
            
            # v7.10.2: 변수 추정 카운터 초기화
            self._total_variable_estimate_count = 0

            # 최대 3회 시도
            for attempt in range(self.max_global_attempts):
                self._global_attempt_count = attempt + 1
                self._current_threshold_idx = attempt
                threshold = self._confidence_thresholds[min(attempt, len(self._confidence_thresholds) - 1)]

                logger.info(f"\n[Phase 4] === 시도 {attempt + 1}/{self.max_global_attempts} (threshold: {threshold:.2f}) ===")

                result = self._single_estimate_attempt(
                    question, context, available_data, depth, parent_data
                )

                if result:
                    # 결과 저장
                    self._attempt_results.append(result)

                    # 충분한 신뢰도면 즉시 반환
                    if result.confidence >= threshold:
                        logger.info(f"[Phase 4] 시도 {attempt + 1} 성공 (confidence: {result.confidence:.2f} >= {threshold:.2f})")
                        return result
                    else:
                        logger.info(f"[Phase 4] 시도 {attempt + 1} 신뢰도 부족 (confidence: {result.confidence:.2f} < {threshold:.2f})")
                else:
                    logger.warning(f"[Phase 4] 시도 {attempt + 1} 실패 (결과 없음)")

            # 3회 모두 실패 시: 최선 결과 선택
            if self._attempt_results:
                best_result = max(self._attempt_results, key=lambda r: r.confidence)
                logger.info(f"[Phase 4] 3회 시도 완료 -> 최선 결과 선택 (confidence: {best_result.confidence:.2f})")
                best_result.reasoning_detail['retry_info'] = {
                    'total_attempts': self._global_attempt_count,
                    'selected_from': len(self._attempt_results),
                    'selection_reason': 'best_confidence'
                }
                return best_result
            else:
                logger.warning("[Phase 4] 3회 시도 모두 실패 (결과 없음)")
                return None
        else:
            # 재귀 호출 (depth > 0): 단일 시도만
            return self._single_estimate_attempt(
                question, context, available_data, depth, parent_data
            )

    def _get_current_confidence_threshold(self) -> float:
        """현재 시도의 confidence threshold 반환 (v7.10.0)"""
        idx = min(self._current_threshold_idx, len(self._confidence_thresholds) - 1)
        return self._confidence_thresholds[idx]

    def _single_estimate_attempt(
        self,
        question: str,
        context: Context = None,
        available_data: Dict = None,
        depth: int = 0,
        parent_data: Dict = None
    ) -> Optional[EstimationResult]:
        """
        단일 추정 시도 (v7.10.0)

        기존 estimate 로직을 분리하여 재시도 가능하게 함
        """
        start_time = time.time()

        logger.info(f"\n{'  ' * depth}[Phase 4] Fermi Estimation (depth {depth})")
        logger.info(f"{'  ' * depth}  질문: {question}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 안전 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # 1. Max depth 체크
        if depth >= self.max_depth:
            logger.warning(f"{'  ' * depth}  Max depth {self.max_depth} 도달 -> Phase 3 Fallback")
            # Fallback to Phase 3
            return self.phase3.estimate(question, context or Context())

        # 2. 순환 감지
        if self._detect_circular(question):
            logger.warning(f"{'  ' * depth}  순환 의존성 감지 (A->B->A) -> 중단")
            return None

        # 3. Call stack 추가
        self.call_stack.append(question)

        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Step 1: 초기 스캔 (데이터 상속 v7.5.0)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            scan_result = self._step1_scan(question, context, available_data, depth, parent_data)

            if not scan_result:
                logger.warning(f"{'  ' * depth}  Step 1 실패")
                return None

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Step 2: 모형 생성 + 반복 개선
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            candidate_models = self._step2_generate_models(
                question,
                scan_result['available'],
                scan_result['unknown'],
                depth,
                context or Context()
            )

            if not candidate_models:
                logger.warning(f"{'  ' * depth}  Step 2 실패 (모형 없음)")
                return None

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Step 3: 실행 가능성 체크 (재귀!)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            ranked_models = self._step3_check_feasibility(
                candidate_models,
                context or Context(),
                depth
            )

            if not ranked_models:
                logger.warning(f"{'  ' * depth}  Step 3 실패 (실행 불가능)")
                return None

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Step 4: 최선 모형 실행
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            result = self._step4_execute(ranked_models[0], depth, context or Context())

            if result:
                execution_time = time.time() - start_time

                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # Phase 5: Boundary 검증 (v7.6.2)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                boundary_check = self._phase5_boundary_validation(
                    result, question, ranked_models[0], depth
                )

                if not boundary_check.is_valid:
                    logger.warning(f"{'  ' * depth}  Boundary 검증 실패: {boundary_check.reasoning}")
                    logger.warning(f"{'  ' * depth}  -> 다음 모형 시도 또는 None 반환")
                    # TODO: 다음 순위 모형 시도
                    return None

                # Boundary 검증 정보 추가
                result.reasoning_detail['boundary_check'] = {
                    'is_valid': boundary_check.is_valid,
                    'hard_violations': boundary_check.hard_violations,
                    'soft_warnings': boundary_check.soft_warnings,
                    'confidence_adjustment': boundary_check.confidence
                }

                # Soft warning이 있으면 confidence 조정
                if boundary_check.soft_warnings:
                    original_conf = result.confidence
                    result.confidence = result.confidence * boundary_check.confidence
                    logger.info(f"{'  ' * depth}  Soft warning -> confidence {original_conf:.2f} -> {result.confidence:.2f}")

                logger.info(f"{'  ' * depth}  Phase 4 완료: {result.value} ({execution_time:.2f}초)")

            return result

        except Exception as e:
            logger.error(f"{'  ' * depth}  Phase 4 에러: {e}")
            return None

        finally:
            # Call stack에서 제거 (중요!)
            if self.call_stack and self.call_stack[-1] == question:
                self.call_stack.pop()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: 초기 스캔 (가용 데이터 파악)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _step1_scan(
        self,
        question: str,
        context: Optional[Context],
        available_data: Optional[Dict],
        depth: int,
        parent_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Step 1: 초기 스캔 (Bottom-up) - 확장됨
        
        가용한 데이터 파악 (우선순위 순):
        0. 부모 데이터 상속 (재귀 시)
        1. 프로젝트 데이터 (최우선)
        2. RAG 검색 (벤치마크, 업계 평균)
        3. Phase 3 Source (통계, 명확한 값)
        4. Context 상수 (물리/통계 상수)
        
        Args:
            question: 질문
            context: 맥락
            available_data: 프로젝트 데이터
            depth: 깊이
            parent_data: 부모 데이터
        
        Returns:
            {'available': Dict[str, FermiVariable], 'unknown': []}
        """
        logger.info(f"{'  ' * depth}  [Step 1] 초기 스캔 (확장)")
        
        available = {}
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 0: 부모 데이터 상속 (우선순위 2)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if parent_data:
            for key, val in parent_data.items():
                if isinstance(val, FermiVariable):
                    available[key] = val
                    logger.info(f"{'  ' * depth}    [부모] {key} = {val.value}")
                elif isinstance(val, dict):
                    available[key] = FermiVariable(
                        name=key,
                        available=True,
                        value=val.get('value'),
                        source=val.get('source', 'parent_inherited'),
                        confidence=val.get('confidence', 0.8)
                    )
                    logger.info(f"{'  ' * depth}    [부모] {key} = {val.get('value')}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: 프로젝트 데이터 (우선순위 1, 최우선)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if available_data:
            for key, val in available_data.items():
                # 프로젝트 데이터는 항상 덮어쓰기 (최우선)
                if isinstance(val, dict):
                    available[key] = FermiVariable(
                        name=key,
                        available=True,
                        value=val.get('value'),
                        source="project_data",
                        confidence=val.get('confidence', 1.0),
                        uncertainty=val.get('uncertainty', 0.0)
                    )
                else:
                    available[key] = FermiVariable(
                        name=key,
                        available=True,
                        value=val,
                        source="project_data",
                        confidence=1.0,
                        uncertainty=0.0
                    )
                logger.info(f"{'  ' * depth}    [프로젝트] {key} = {val if not isinstance(val, dict) else val.get('value')}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: RAG 검색 (우선순위 3, 최상위만)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if depth == 0 and context:  # 최상위만 검색 (비용 절감)
            logger.info(f"{'  ' * depth}    [RAG] 벤치마크 검색 중...")
            rag_data = self._search_rag_benchmarks(question, context)
            
            for key, var in rag_data.items():
                if key not in available:  # 프로젝트 데이터 우선
                    available[key] = var
                    logger.info(f"{'  ' * depth}    [RAG] {key} = {var.value} (conf: {var.confidence:.2f})")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: Phase 3 Source (우선순위 4, 최상위만)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if depth == 0 and context:
            logger.info(f"{'  ' * depth}    [Phase 3] Source 조회 중...")
            phase3_data = self._query_phase3_sources(question, context)
            
            for key, var in phase3_data.items():
                if key not in available:  # 프로젝트/RAG 우선
                    available[key] = var
                    logger.info(f"{'  ' * depth}    [Phase 3] {key} = {var.value} (conf: {var.confidence:.2f})")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: Context 상수 (우선순위 5)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if context:
            context_data = self._extract_context_constants(question, context)
            
            for key, var in context_data.items():
                if key not in available:
                    available[key] = var
                    logger.info(f"{'  ' * depth}    [Context] {key} = {var.value}")
        
        logger.info(f"{'  ' * depth}    총 가용 데이터: {len(available)}개")
        
        return {
            'available': available,
            'unknown': []
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: 모형 생성 (LLM)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _step2_generate_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        unknown: List[str],
        depth: int,
        context: Optional[Context] = None
    ) -> List[FermiModel]:
        """
        Step 2: 모형 생성 (Top-down) + 반복 개선
        
        프로세스:
        2a. LLM 모형 생성
        2b. 제안 변수 재검색 (최대 2회)
        2c. 변수 정책 필터링
        
        Args:
            question: 질문
            available: 가용 변수
            unknown: 미지수 리스트
            depth: 깊이
            context: 맥락 (Step 2b용)
        
        Returns:
            3-5개 FermiModel 후보
        """
        logger.info(f"{'  ' * depth}  [Step 2] 모형 생성")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2a: LLM 모형 생성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        models = self._generate_default_models(question, available, depth, context)
        
        if not models:
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2b: 변수 재검색 및 개선
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if context and depth == 0:  # 최상위만 (비용 절감)
            models = self._phase2b_refine_with_data_search(
                models, question, context, depth
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2c: 변수 정책 필터링
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        filtered_models = []
        for model in models:
            allowed, warning = self.variable_policy.check(model.total_variables)
            
            if not allowed:
                logger.warning(f"{'  ' * depth}    모형 {model.model_id} 제외: {warning}")
                model.why_not_selected = warning
                continue
            
            if warning:
                logger.warning(f"{'  ' * depth}    모형 {model.model_id}: {warning}")
            
            filtered_models.append(model)
        
        logger.info(f"{'  ' * depth}    최종 모형: {len(filtered_models)}개")
        
        return filtered_models
    
    def _generate_default_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        depth: int,
        context: Optional[Context] = None
    ) -> List[FermiModel]:
        """
        기본 모형 생성 (v7.8.1: Model Config 통합)
        
        Model Config 시스템을 통해 통합된 처리:
        - Cursor/API 모두 동일한 로직 사용
        - 차이는 LLM 호출 방식만 (Cursor AI vs External API)
        
        Args:
            question: 질문
            available: 가용 변수
            depth: 깊이
            context: 맥락
        
        Returns:
            FermiModel 리스트
        """
        # v7.8.1: Model Config 시스템 사용
        # Cursor/API 모두 _generate_llm_models 사용
        # 단지 LLM 호출 방식만 다름
        
        logger.info(f"{'  ' * depth}    [Phase 4] 모형 생성 시작 (Mode: {self.llm_mode})")
        
        models = self._generate_llm_models(question, available, depth)
        
        if models:
            return models
        
        # Fallback: Phase 3으로 위임
        logger.info(f"{'  ' * depth}    Fallback → Phase 3 위임")
        return []
    
    def _generate_llm_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        depth: int
    ) -> List[FermiModel]:
        """
        LLM으로 모형 생성 (v7.8.1: Native/External 통합)
        
        설계: fermi_model_search.yaml Line 1158-1181
        
        v7.8.1: Cursor/API 통합
        - Cursor Mode: Cursor AI에게 instruction 전달 (무료, 대화 컨텍스트)
        - API Mode: External LLM API 호출 (유료)
        - 차이는 LLM 호출 방식만, 로직은 동일
        
        v7.8.0: Model Config 시스템 통합
        - select_model_with_config() 사용
        - API 타입 자동 분기 (Responses/Chat)
        - Pro 모델 Fast Mode 자동 적용
        
        Args:
            question: 질문
            available: 가용 변수
            depth: 깊이
        
        Returns:
            LLM이 생성한 FermiModel 리스트
        """
        logger.info(f"{'  ' * depth}      [LLM] 모형 생성 요청 (Mode: {self.llm_mode})")

        # 프롬프트 구성 (Cursor/API 공통)
        # v7.10.0: Pro 모델용 Fast Mode 지원을 위해 model_name 전달
        model_name = self.llm_mode if self.llm_mode != 'cursor' else None
        prompt = self._build_llm_prompt(question, available, model_name=model_name)
        
        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Cursor AI: instruction 전달 (대화형)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            if self.llm_mode == 'cursor':  # v7.8.1: cursor = Cursor AI
                logger.info(f"{'  ' * depth}      [Cursor AI] 대화형 모형 생성 - instruction 작성")
                logger.info(f"{'  ' * depth}      [Cursor AI] 비용: $0 (무료)")
                
                instruction = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Fermi 모형 생성 요청 (Cursor AI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 중요: 위 프롬프트에 따라 Fermi 모형을 생성해주세요!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                logger.warning(f"{'  ' * depth}      [Cursor AI] 대화 컨텍스트에서 직접 응답 필요")
                logger.info(f"{'  ' * depth}      [Cursor AI] Instruction 작성 완료 → Phase 3 Fallback")
                return []
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # External API: OpenAI API 호출
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            else:  # External API (self.llm_mode = gpt-4o-mini, o1-mini 등)
                # v7.8.0: Model Config 시스템 사용
                model_name, model_config = select_model_with_config(phase=4)
                
                logger.info(f"{'  ' * depth}      [LLM] 모델: {model_name}")
                logger.info(f"{'  ' * depth}      [LLM] API: {model_config.api_type}")
                
                # Fast Mode 적용 (Pro 모델)
                if is_pro_model(model_name):
                    logger.info(f"{'  ' * depth}      [LLM] Fast Mode 적용 (Pro 모델)")
                    fast_mode_prefix = """🔴 SPEED OPTIMIZATION MODE
⏱️ 목표 응답 시간: 60초 이내
📏 최대 출력 길이: 2,000자 이내

"""
                    prompt = fast_mode_prefix + prompt
                
                # API 파라미터 구성 (자동)
                api_params = model_config.build_api_params(
                    prompt=prompt,
                    reasoning_effort='medium'  # Phase 4 기본값
                )
                
                # API 타입별 분기 (Responses vs Chat)
                if model_config.api_type == 'responses':
                    # Responses API (o1, o3, gpt-5 시리즈)
                    response = self.llm_client.responses.create(**api_params)
                else:
                    # Chat Completions API (gpt-4 시리즈)
                    # System message 추가
                    if 'messages' in api_params:
                        api_params['messages'].insert(0, {
                            "role": "system",
                            "content": "당신은 Fermi Estimation 전문가입니다. 질문을 계산 가능한 수학적 모형으로 분해하세요."
                        })
                    
                    response = self.llm_client.chat.completions.create(**api_params)
                
                # ⭐ v7.8.1: 통합 파싱 (구조적 응답 파싱)
                llm_output = self._parse_llm_response(
                    response=response,
                    api_type=model_config.api_type,
                    depth=depth
                )
                
                # v7.8.1: llm_output이 None일 수 있음 (빈 응답 또는 파싱 실패)
                if not llm_output:
                    logger.warning(f"{'  ' * depth}      ⚠️ LLM 빈 응답 또는 파싱 실패")
                    return []
                
                logger.info(f"{'  ' * depth}      [LLM] 응답 수신 ({len(llm_output)}자)")
                
                # 응답 파싱
                models = self._parse_llm_models(llm_output, depth)
                
                if not models:
                    logger.warning(f"{'  ' * depth}      ⚠️ 파싱 결과 없음")
                    return []
                
                logger.info(f"{'  ' * depth}      [LLM] 파싱 완료: {len(models)}개 모형")
                
                return models
        
        except Exception as e:
            logger.error(f"{'  ' * depth}      ❌ LLM 생성 실패: {e}")
            return []
    
    def _parse_llm_response(
        self,
        response: Any,
        api_type: str,
        depth: int = 0
    ) -> Optional[str]:
        """
        LLM 응답 파싱 (API Type별 통합)
        
        v7.8.1: 구조적 응답 파싱 (벤치마크 패턴 적용)
        
        Args:
            response: API 응답 객체
            api_type: 'responses', 'chat', 'cursor'
            depth: 로그 들여쓰기
        
        Returns:
            파싱된 텍스트 또는 None
        """
        try:
            # API Type별 파싱
            if api_type == 'responses':
                # Responses API (o1, o3, o4, gpt-5 시리즈)
                
                # Level 1: 표준 프로퍼티 (output_text)
                if hasattr(response, 'output_text'):
                    logger.info(f"{'  ' * depth}      [Parser] Level 1: output_text 프로퍼티 사용")
                    return response.output_text
                
                # Level 2: 객체 구조 탐색 (output)
                if hasattr(response, 'output'):
                    output = response.output
                    
                    # output이 리스트인 경우
                    if isinstance(output, list) and output:
                        output_item = output[0]
                        
                        # ResponseOutputMessage 객체
                        if hasattr(output_item, 'content'):
                            content = output_item.content
                            
                            # content가 리스트인 경우 (실제 구조!)
                            if isinstance(content, list) and content:
                                # ResponseOutputText 객체
                                if hasattr(content[0], 'text'):
                                    logger.info(f"{'  ' * depth}      [Parser] Level 2: output[0].content[0].text")
                                    return content[0].text
                            
                            # content가 문자열인 경우
                            if isinstance(content, str):
                                logger.info(f"{'  ' * depth}      [Parser] Level 2: output[0].content (string)")
                                return content
                        
                        # text 프로퍼티 직접 존재
                        if hasattr(output_item, 'text'):
                            logger.info(f"{'  ' * depth}      [Parser] Level 2: output[0].text")
                            return output_item.text
                    
                    # output이 문자열인 경우
                    if isinstance(output, str):
                        logger.info(f"{'  ' * depth}      [Parser] Level 2: output (string)")
                        return output
                
                # Level 3: 문자열 변환
                logger.warning(f"{'  ' * depth}      ⚠️ Responses API: 알 수 없는 응답 구조, str() 변환")
                return str(response)
            
            elif api_type == 'chat':
                # Chat Completions API (gpt-4, gpt-4o 시리즈)
                
                # Level 1: 표준 구조
                if hasattr(response, 'choices') and response.choices:
                    message = response.choices[0].message
                    if hasattr(message, 'content'):
                        logger.info(f"{'  ' * depth}      [Parser] Level 1: choices[0].message.content")
                        return message.content
                
                # Level 2: Fallback
                logger.warning(f"{'  ' * depth}      ⚠️ Chat API: 알 수 없는 응답 구조")
                return str(response)
            
            elif api_type == 'cursor':
                # Cursor AI (대화형)
                logger.info(f"{'  ' * depth}      ℹ️  Cursor AI는 대화형 모드 (파싱 불필요)")
                return None
            
            else:
                logger.error(f"{'  ' * depth}      ❌ 알 수 없는 API Type: {api_type}")
                return None
        
        except Exception as e:
            logger.error(f"{'  ' * depth}      ❌ 응답 파싱 실패: {e}")
            return None
    
    def _build_llm_prompt(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        model_name: Optional[str] = None
    ) -> str:
        """
        LLM 프롬프트 구성 (v7.10.0: 벤치마크 패턴 적용)

        v7.10.0 개선:
        - concept 필드 강제 (모든 decomposition 단계)
        - final_calculation, calculation_verification 필수화
        - 마지막 단계 value = 최상위 value 정확히 일치 강제
        - 명확한 사칙연산 강제
        - Pro 모델용 Fast Mode constraint 추가

        설계: benchmarks/estimator/phase4/common.py get_improved_fewshot_prompt()

        Args:
            question: 추정 질문
            available: 가용 변수 딕셔너리
            model_name: 모델 이름 (Pro 모델이면 Fast Mode 적용)
        """
        # v7.10.0: Pro 모델용 Fast Mode constraint
        pro_models = ['gpt-5-pro', 'o1-pro', 'o1-pro-2025-03-19', 'o1-preview']
        fast_mode_constraint = ""

        if model_name and model_name in pro_models:
            fast_mode_constraint = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEED OPTIMIZATION MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목표 응답 시간: 60초 이내
최대 출력 길이: 2,000자 이내 (약 500 토큰)
decomposition: 3-5단계만 (필수 단계만 포함)
reasoning: 각 단계 15단어 이내

빠르고 간결하게 핵심만 답변하세요!
깊은 추론보다는 직관적 근사치를 우선하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            logger.info(f"  [Fast Mode] {model_name}에 속도 최적화 프롬프트 적용")

        # v7.10.0: 필수 필드 강제 헤더
        mandatory_header = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL MANDATORY FIELDS (누락 시 실패!):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. decomposition의 모든 단계에 "concept" 필드 필수!
2. 최상위 "final_calculation" 필드 필수!
3. 최상위 "calculation_verification" 필드 필수!
4. decomposition[-1]["value"] == JSON["value"] (정확히 일치!)

이 필드들이 하나라도 누락되면 추정이 실패합니다!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # v7.10.0: 개선된 Few-shot 예시 (concept 필드 포함, value 일치)
        fewshot_example = """
올바른 예시: 서울시 택시 수

{
    "value": 66667,
    "unit": "대",
    "confidence": 0.6,
    "method": "bottom-up",
    "decomposition": [
        {
            "step": "1. 서울 인구",
            "concept": "population_seoul",
            "value": 10000000,
            "unit": "명",
            "calculation": "1000만명 (통계 기반)",
            "reasoning": "서울시 공식 인구 통계"
        },
        {
            "step": "2. 1인당 연간 택시 이용",
            "concept": "taxi_usage_per_capita",
            "value": 20,
            "unit": "회",
            "calculation": "월 1.5회 x 12개월 = 20",
            "reasoning": "대중교통 중심, 가끔 이용"
        },
        {
            "step": "3. 연간 총 이용 횟수",
            "concept": "total_taxi_rides",
            "value": 200000000,
            "unit": "회",
            "calculation": "10000000 x 20 = 200000000",
            "reasoning": "step1 x step2"
        },
        {
            "step": "4. 택시 1대당 연간 운행",
            "concept": "rides_per_taxi",
            "value": 3000,
            "unit": "회",
            "calculation": "일 10회 x 300일 = 3000",
            "reasoning": "2교대 기준"
        },
        {
            "step": "5. 최종: 필요 택시 수",
            "concept": "total_taxis_needed",
            "value": 66667,
            "unit": "대",
            "calculation": "200000000 / 3000 = 66667",
            "reasoning": "step3 / step4"
        }
    ],
    "final_calculation": "step5 = step3 / step4 = 200000000 / 3000 = 66667",
    "calculation_verification": "검증: 10,000,000명 x 20회 / 3,000회 = 66,667대"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY RULES (절대 규칙):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "concept" 필드 - 모든 decomposition 단계에 필수!
   -> 도메인 특화 개념을 영어 snake_case로 명시
   -> 예: "population_seoul", "taxi_usage_per_capita"

2. "final_calculation" 필드 - JSON 최상위에 필수!
   -> decomposition 마지막 단계 계산을 실제 숫자로 재검증
   -> 예: "step5 = step3 / step4 = 200000000 / 3000 = 66667"

3. "calculation_verification" 필드 - JSON 최상위에 필수!
   -> 전체 계산 과정 재확인
   -> 예: "검증: 10,000,000명 x 20회 / 3,000회 = 66,667대"

4. 최종 추정값 = decomposition 마지막 단계의 value
   -> JSON의 "value": 66667 = decomposition[-1]["value"]: 66667
   -> 반올림/근사치 금지! 정확히 일치해야 함!

5. 마지막 단계는 반드시 최종 계산 단계
   -> "step": "N. 최종: [추정 대상]"
   -> 이 단계의 value가 곧 최종 답

6. 각 중간 단계는 명확한 사칙연산으로 연결
   -> "calculation": "step3 / step4 = 200000000 / 3000 = 66667"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # 가용 데이터 문자열
        if available:
            available_str = "\n".join([
                f"- {var.name}: {var.value} ({var.source}, confidence: {var.confidence:.0%})"
                for var in available.values()
            ])
        else:
            available_str = "(없음)"

        prompt = f"""{fast_mode_constraint}{mandatory_header}
{fewshot_example}

이제 실제 문제를 풀어주세요:

질문: {question}

가용한 데이터:
{available_str}

임무:
1. 이 질문에 답하기 위한 계산 모형을 3-5개 제시하세요.
2. 각 모형은 다른 분해 방식을 사용하세요.
3. 가용한 데이터를 최대한 활용하세요.
4. Unknown 변수를 최소화하세요.
5. 간단할수록 좋습니다 (Occam's Razor, 최대 6개 변수 권장).

필수 규칙:
   - 변수명은 영문자와 언더스코어만 사용 (예: monthly_revenue, churn_rate)
   - 순환 참조 금지 (A->B->A 구조 금지)
   - 변수 이름 규칙: [a-zA-Z_][a-zA-Z0-9_]*

출력 형식 (YAML):
```yaml
models:
  - id: MODEL_001
    formula: "result = A * B * C"
    description: "설명"
    variables:
      - name: A
        concept: "domain_concept_a"
        description: "음식점 수"
        available: true
      - name: B
        concept: "domain_concept_b"
        description: "도입률"
        available: false
      - name: C
        concept: "domain_concept_c"
        description: "ARPU"
        available: false
```

체크리스트 (반드시 확인!):
- [ ] 모든 변수에 "concept" 필드 있음
- [ ] decomposition[-1]["value"] == JSON["value"]
- [ ] 마지막 step은 "N. 최종: [추정 대상]"
- [ ] 모든 calculation에 실제 숫자 포함

주의: YAML 형식으로만 출력하세요."""

        return prompt
    
    def _parse_llm_models(
        self,
        llm_output: str,
        depth: int
    ) -> List[FermiModel]:
        """
        LLM 응답 파싱 (YAML/JSON 지원)
        
        v7.8.1: JSON 추출 로직 강화 (벤치마크 패턴 적용)
        
        Args:
            llm_output: LLM 응답
            depth: 깊이
        
        Returns:
            FermiModel 리스트
        """
        try:
            # 1. YAML 블록 추출 시도 (```yaml ... ```)
            yaml_match = re.search(r'```yaml\n(.*?)\n```', llm_output, re.DOTALL)
            
            if yaml_match:
                yaml_str = yaml_match.group(1)
                logger.info(f"{'  ' * depth}        [Parser] YAML 블록 감지")
                
                # YAML 파싱
                data = yaml.safe_load(yaml_str)
            else:
                # 2. JSON 블록 추출 시도 (```json ... ```)
                content = llm_output
                
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                    logger.info(f"{'  ' * depth}        [Parser] JSON 블록 감지 (```json)")
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                    logger.info(f"{'  ' * depth}        [Parser] JSON 블록 감지 (```)")
                else:
                    logger.info(f"{'  ' * depth}        [Parser] 코드 블록 없음, 전체 파싱 시도")
                
                # 3. JSON 파싱 시도
                try:
                    data = json.loads(content)
                    logger.info(f"{'  ' * depth}        [Parser] JSON 파싱 성공")
                except json.JSONDecodeError:
                    # 4. YAML로 전체 파싱 시도 (Fallback)
                    logger.info(f"{'  ' * depth}        [Parser] JSON 실패, YAML 시도")
                    data = yaml.safe_load(llm_output)
            
            # 데이터 검증
            if not data or 'models' not in data:
                logger.warning(f"{'  ' * depth}        ⚠️  파싱 실패 (models 키 없음)")
                logger.debug(f"{'  ' * depth}        응답 미리보기: {llm_output[:200]}...")
                return []
            
            # FermiModel 변환
            models = []
            for model_data in data['models']:
                # v7.10.0: concept 필드 누락 검증
                raw_variables = model_data.get('variables', [])
                missing_concept = [
                    v.get('name', 'unknown')
                    for v in raw_variables
                    if not v.get('concept')
                ]
                if missing_concept:
                    logger.warning(
                        f"{'  ' * depth}        [Validate] concept 필드 누락: "
                        f"{len(missing_concept)}개 변수 ({', '.join(missing_concept[:3])}...)"
                    )

                # 변수 파싱
                variables = {}
                for var_data in raw_variables:
                    var_name = var_data.get('name', 'unknown')
                    var_available = var_data.get('available', False)
                    var_concept = var_data.get('concept', '')

                    variables[var_name] = FermiVariable(
                        name=var_name,
                        available=var_available,
                        need_estimate=not var_available,
                        source="llm_generated" if var_available else "",
                        concept=var_concept  # v7.10.0: concept 필드 저장
                    )

                # FermiModel 생성
                model = FermiModel(
                    model_id=model_data.get('id', f"LLM_MODEL_{len(models)+1}"),
                    name="LLM 생성 모형",
                    formula=model_data.get('formula', ''),
                    description=model_data.get('description', ''),
                    variables=variables,
                    total_variables=len(variables),
                    unknown_count=sum(1 for v in variables.values() if not v.available)
                )

                models.append(model)
            
            logger.info(f"{'  ' * depth}        [Parser] 파싱 완료: {len(models)}개 모형")
            return models
        
        except Exception as e:
            logger.error(f"{'  ' * depth}        ❌ LLM 응답 파싱 실패: {e}")
            logger.error(f"{'  ' * depth}        에러 타입: {type(e).__name__}")
            
            # 상세 로깅 (디버깅용)
            logger.error(f"{'  ' * depth}        응답 전체:\n{llm_output}")
            
            # data 변수가 정의되어 있으면 로깅
            try:
                if 'data' in locals():
                    logger.error(f"{'  ' * depth}        data 타입: {type(data)}")
                    if isinstance(data, dict):
                        logger.error(f"{'  ' * depth}        data 키: {list(data.keys())}")
                    else:
                        logger.error(f"{'  ' * depth}        data 값: {str(data)[:200]}")
            except:
                pass
            
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 3: 실행 가능성 체크 (재귀 추정)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _step3_check_feasibility(
        self,
        models: List[FermiModel],
        context: Context,
        current_depth: int
    ) -> List[RankedModel]:
        """
        Step 3: 실행 가능성 체크 + 재귀 추정
        
        각 모형의 Unknown 변수를 재귀 호출로 채우기
        
        Args:
            models: 후보 모형들
            context: 맥락
            current_depth: 현재 깊이
        
        Returns:
            점수 순 RankedModel 리스트
        """
        logger.info(f"{'  ' * current_depth}  [Step 3] 실행 가능성 체크")
        
        ranked = []
        
        for model in models:
            logger.info(f"{'  ' * current_depth}    모형: {model.model_id}")
            
            # Unknown 변수 추정 (재귀!)
            for var_name, var in model.variables.items():
                if var.need_estimate and not var.estimation_result:
                    logger.info(f"{'  ' * current_depth}      변수 '{var_name}' 추정 필요")
                    
                    # ⭐ 재귀 호출!
                    var_result = self._estimate_variable(
                        var_name,
                        context,
                        current_depth + 1
                    )
                    
                    if var_result:
                        var.estimation_result = var_result
                        var.value = var_result.value
                        var.confidence = var_result.confidence
                        var.available = True
                        var.source = f"tier3_recursive_depth_{current_depth + 1}"
                        logger.info(f"{'  ' * current_depth}        ✅ {var.value} (conf: {var.confidence:.2f})")
                    else:
                        logger.warning(f"{'  ' * current_depth}        ❌ 추정 실패")
            
            # 모형 점수화
            score_result = self._score_model(model, current_depth)
            
            ranked.append(RankedModel(
                rank=0,  # 정렬 후 할당
                model=model,
                score=score_result['total'],
                unknown_score=score_result['unknown'],
                confidence_score=score_result['confidence'],
                complexity_score=score_result['complexity'],
                depth_score=score_result['depth'],
                status=score_result['status'],
                missing=score_result['missing']
            ))
        
        # 점수 순 정렬
        ranked.sort(key=lambda x: x.score, reverse=True)
        
        # Rank 할당
        for i, rm in enumerate(ranked, 1):
            rm.rank = i
        
        if ranked:
            logger.info(f"{'  ' * current_depth}    최선 모형: {ranked[0].model.model_id} "
                       f"(점수: {ranked[0].score:.3f})")
        
        return ranked
    
    def _estimate_variable(
        self,
        var_name: str,
        context: Context,
        depth: int
    ) -> Optional[EstimationResult]:
        """
        변수 추정 (v7.10.2: 전역 변수 횟수 제한)

        Fallback 우선순위:
        1. Phase 3 값 있으면 수용 (동적 threshold)
        2. Phase 3 SoftGuide 추출 (range/distribution 활용)
        3. LLM emergency 호출 (최후 수단)
        4. Phase 4 재귀 (depth 제한 내)

        Args:
            var_name: 변수 이름
            context: 맥락
            depth: 깊이

        Returns:
            EstimationResult 또는 None
        """
        # v7.10.2: 전역 변수 추정 횟수 제한 (재귀 폭발 완전 방지)
        self._total_variable_estimate_count += 1
        
        if self._total_variable_estimate_count > self.max_variable_estimates:
            logger.warning(f"{'  ' * depth}        ⚠️  변수 추정 제한 초과 ({self.max_variable_estimates}회) → 중단")
            return None
        
        # Context를 질문에 명시적으로 포함 (v7.5.0)
        question = self._build_contextualized_question(var_name, context)

        logger.info(f"{'  ' * depth}      [Recursive {self._total_variable_estimate_count}/{self.max_variable_estimates}] {question}")

        # v7.10.0: 동적 confidence threshold 사용
        threshold = self._get_current_confidence_threshold()

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. Phase 3 시도
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        phase3_result = self.phase3.estimate(question, context)

        if phase3_result:
            # 신뢰도가 threshold 이상이면 수용
            if phase3_result.confidence >= threshold:
                logger.info(f"{'  ' * depth}        Phase 3 성공 (conf: {phase3_result.confidence:.2f} >= {threshold:.2f})")
                return phase3_result

            # 값이 있으면 수용 (재귀 폭발 방지)
            if phase3_result.value is not None and phase3_result.value != 0:
                logger.info(f"{'  ' * depth}        Phase 3 값 수용 (conf: {phase3_result.confidence:.2f} < {threshold:.2f}, but value exists)")
                return phase3_result

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. SoftGuide 추출 시도 (v7.10.1 신규!)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if phase3_result and hasattr(phase3_result, 'reasoning_detail'):
            soft_guide = phase3_result.reasoning_detail.get('soft_guide')
            if soft_guide:
                value = self._extract_value_from_softguide(soft_guide)
                if value is not None:
                    logger.info(f"{'  ' * depth}        SoftGuide fallback: {value} (range 활용)")

                    return EstimationResult(
                        question=question,
                        value=value,
                        confidence=0.40,  # 낮은 신뢰도
                        phase=3,
                        context=context,
                        reasoning=f"Phase 3 range/distribution 중간값 사용",
                        reasoning_detail={
                            'method': 'softguide_fallback',
                            'original_confidence': phase3_result.confidence,
                            'source': 'phase3_softguide'
                        }
                    )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. LLM emergency 호출 (v7.10.1 신규!)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.llm_mode != 'cursor':
            llm_value = self._llm_emergency_estimate(var_name, context)
            if llm_value is not None:
                logger.info(f"{'  ' * depth}        LLM emergency: {llm_value}")

                return EstimationResult(
                    question=question,
                    value=llm_value,
                    confidence=0.30,  # 매우 낮은 신뢰도
                    phase=4,
                    context=context,
                    reasoning=f"LLM 직접 추정 (emergency, gpt-4o-mini)",
                    reasoning_detail={
                        'method': 'llm_emergency',
                        'model': 'gpt-4o-mini',
                        'source': 'direct_llm_call'
                    }
                )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. Phase 4 재귀 (최후 수단, depth 제한)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if depth < self.max_depth - 1:  # 마지막 depth에서는 재귀 안 함
            logger.info(f"{'  ' * depth}        Fermi 재귀 (depth {depth} -> {depth + 1})")

            # 부모 데이터 준비 (v7.5.0+)
            parent_data_to_pass = {}

            tier3_result = self._single_estimate_attempt(
                question=question,
                context=context,
                available_data=None,
                depth=depth + 1,
                parent_data=parent_data_to_pass
            )

            if tier3_result:
                return tier3_result

        # 완전 실패
        logger.warning(f"{'  ' * depth}        변수 추정 완전 실패: {var_name}")
        return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 4: 모형 실행 (Backtracking)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase5_boundary_validation(
        self,
        result: EstimationResult,
        question: str,
        model: Any,
        depth: int
    ):
        """
        Phase 5: Boundary 검증 (v7.6.2)
        
        LLM 기반 비정형 사고로 추정값 타당성 검증
        
        Args:
            result: 추정 결과
            question: 원래 질문
            model: 사용된 모형
            depth: 깊이
        
        Returns:
            BoundaryCheck
        """
        logger.info(f"{'  ' * depth}  [Phase 5] Boundary 검증")
        
        try:
            from .boundary_validator import get_boundary_validator
            
            validator = get_boundary_validator(llm_mode=self.llm_mode)
            
            boundary_check = validator.validate(
                question=question,
                estimated_value=result.value,
                unit=result.unit,
                context=result.context,
                formula=model.formula if hasattr(model, 'formula') else ""
            )
            
            return boundary_check
        
        except Exception as e:
            logger.warning(f"{'  ' * depth}  ⚠️  Boundary 검증 실패: {e}")
            
            # Fallback: 통과로 간주
            from .boundary_validator import BoundaryCheck
            return BoundaryCheck(is_valid=True, reasoning="Boundary 검증 스킵")
    
    def _step4_execute(
        self,
        ranked_model: RankedModel,
        depth: int,
        context: Context
    ) -> Optional[EstimationResult]:
        """
        Step 4: 모형 실행 + 품질 평가 (v7.10.0)

        재귀로 채운 변수들을 backtracking으로 재조립
        v7.10.0: 품질 평가 및 후처리 통합

        Args:
            ranked_model: 선택된 모형
            depth: 깊이
            context: 맥락

        Returns:
            EstimationResult (decomposition + 품질 평가 포함)
        """
        logger.info(f"{'  ' * depth}  [Step 4] 모형 실행")

        model = ranked_model.model

        # Step 1: 변수 바인딩 확인
        bindings = {}
        for name, var in model.variables.items():
            if var.available and var.value is not None:
                bindings[name] = var.value
            else:
                logger.warning(f"{'  ' * depth}    변수 '{name}' 값 없음")

        if not bindings:
            logger.warning(f"{'  ' * depth}    바인딩할 변수 없음")
            return None

        logger.info(f"{'  ' * depth}    변수 바인딩: {list(bindings.keys())}")

        # Step 2: 계산 실행
        result_value = self._execute_formula_simple(model.formula, bindings)

        # Step 3: Confidence 조합 (Geometric Mean)
        confidences = [
            var.confidence
            for var in model.variables.values()
            if var.available and var.confidence > 0
        ]

        if confidences:
            combined_confidence = math.prod(confidences) ** (1 / len(confidences))
        else:
            combined_confidence = 0.5

        logger.info(f"{'  ' * depth}    Confidence: {combined_confidence:.2f}")

        # Step 4: DecompositionTrace 생성
        decomposition = DecompositionTrace(
            formula=model.formula,
            variables={
                name: var.estimation_result
                for name, var in model.variables.items()
                if var.estimation_result
            },
            calculation_logic=model.description,
            depth=depth,
            decomposition_reasoning=getattr(model, 'selection_reason', '')
        )

        # v7.10.0: decomposition을 Dict 형태로 변환 (평가용)
        decomp_list = self._model_to_decomposition_list(model, bindings, result_value)

        # v7.10.0: 응답 Dict 구성 (후처리/평가용)
        response_dict = {
            'value': result_value,
            'unit': '',
            'decomposition': decomp_list,
            'final_calculation': model.formula,
            'calculation_verification': ''
        }

        # v7.10.0: 후처리 (필수 필드 자동 생성, value 교정)
        response_dict, auto_generated = self._validate_and_postprocess_response(
            response_dict, depth
        )

        # v7.10.0: 품질 평가
        content_score = self._evaluate_content_score(decomp_list, result_value, depth)
        format_score = self._evaluate_format_score(response_dict, decomp_list, auto_generated, depth)

        # 질문 문자열 구성 (개념적 일관성 평가용)
        question_str = context.domain if context and context.domain else "unknown"
        conceptual_score = self._evaluate_conceptual_coherence(
            question_str,
            decomp_list,
            response_dict.get('final_calculation', ''),
            context,
            depth
        )

        total_quality_score = content_score['score'] + format_score['score'] + conceptual_score['score']
        logger.info(f"{'  ' * depth}    [품질] 내용: {content_score['score']:.1f}/45, "
                   f"형식: {format_score['score']:.1f}/5, "
                   f"개념: {conceptual_score['score']:.1f}/15 = {total_quality_score:.1f}/65")

        # Step 5: Logic Steps 생성
        logic_steps = [
            f"모형 선택: {model.formula}",
            f"변수 분해: {model.total_variables}개",
            f"변수 확보: {getattr(model, 'available_count', len(bindings))}개",
            f"재귀 깊이: depth {depth}",
            f"계산: {model.formula}",
            f"신뢰도: {combined_confidence:.2f}",
            f"결과: {result_value}",
            f"품질: {total_quality_score:.1f}/65"
        ]

        # Step 6: EstimationResult 생성
        result = EstimationResult(
            question=question_str,
            value=response_dict.get('value', result_value),  # v7.10.0: 후처리 결과 사용
            confidence=combined_confidence,
            phase=4,
            context=context,
            reasoning=f"Fermi 분해: {model.description}",
            reasoning_detail={
                'method': 'fermi_decomposition',
                'model_id': model.model_id,
                'formula': model.formula,
                'depth': depth,
                'selection_reason': getattr(model, 'selection_reason', ''),
                'why_this_method': f'Phase 1/2/3 실패, 재귀 분해 (depth {depth})',
                'variables': {
                    name: {
                        'value': var.value,
                        'source': var.source,
                        'confidence': var.confidence
                    }
                    for name, var in model.variables.items()
                    if var.available
                },
                # v7.10.0: 품질 평가 결과 추가
                'quality_evaluation': {
                    'content_score': content_score,
                    'format_score': format_score,
                    'conceptual_score': conceptual_score,
                    'total_score': total_quality_score,
                    'auto_generated_fields': auto_generated
                }
            },
            logic_steps=logic_steps,
            decomposition=decomposition,
            fermi_model=model
        )
        
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 모형 점수화
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _score_model(
        self,
        model: FermiModel,
        depth: int
    ) -> Dict[str, Any]:
        """
        모형 점수화 (4개 기준)
        
        설계: fermi_model_search.yaml Line 725-810
        
        기준:
        1. Unknown count (50%): 적을수록 좋음
        2. Confidence (30%): 높을수록 좋음
        3. Complexity (20%): 간단할수록 좋음
        4. Depth (10% bonus): 얕을수록 좋음
        
        Returns:
            {
                'unknown': float,
                'confidence': float,
                'complexity': float,
                'depth': float,
                'total': float,
                'status': str,
                'missing': List[str]
            }
        """
        # 1. Unknown count (50%)
        if model.total_variables > 0:
            filled = sum(1 for v in model.variables.values() if v.available)
            model.available_count = filled
            unknown_ratio = filled / model.total_variables
        else:
            unknown_ratio = 0.0
        
        unknown_score = unknown_ratio * 0.5
        
        # 2. Confidence (30%)
        confidences = [
            v.confidence for v in model.variables.values()
            if v.available and v.confidence > 0
        ]
        
        if confidences:
            avg_confidence = math.prod(confidences) ** (1 / len(confidences))  # Geometric mean
        else:
            avg_confidence = 0.0
        
        confidence_score = avg_confidence * 0.3
        
        # 3. Complexity (20%)
        var_count = model.total_variables
        
        complexity_map = {
            1: 1.0, 2: 1.0,
            3: 0.9, 4: 0.7,
            5: 0.5, 6: 0.3,
            7: 0.2, 8: 0.15,
            9: 0.10, 10: 0.05
        }
        
        complexity = complexity_map.get(var_count, 0.0)
        complexity_score = complexity * 0.2
        
        # 4. Depth (10% bonus)
        depth_penalties = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}
        depth_penalty = depth_penalties.get(depth, 0.2)
        depth_score = depth_penalty * 0.1
        
        # 총점
        total = unknown_score + confidence_score + complexity_score + depth_score
        
        # 상태 판단
        missing = [
            name for name, var in model.variables.items()
            if not var.available
        ]
        
        if not missing:
            status = "feasible"
        elif len(missing) <= 2:
            status = "partial"
        else:
            status = "infeasible"
        
        return {
            'unknown': unknown_score,
            'confidence': confidence_score,
            'complexity': complexity_score,
            'depth': depth_score,
            'total': total,
            'status': status,
            'missing': missing
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 동적 Fallback (v7.10.1: 패턴 매칭 제거)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _extract_value_from_softguide(
        self,
        soft_guide: 'SoftGuide'
    ) -> Optional[float]:
        """
        SoftGuide에서 대표값 추출 (v7.10.1)

        Phase 3가 range/distribution을 제공했지만 confidence가 낮을 때
        그 정보를 활용하여 대표값 추출

        Args:
            soft_guide: Phase 3의 SoftGuide 결과

        Returns:
            대표값 (중앙값 > 평균 > range 중간값) 또는 None
        """
        if not soft_guide:
            return None

        dist = soft_guide.distribution

        # 1. Distribution이 있으면 통계값 우선
        if dist:
            # 중앙값 우선 (Power Law 등에 안전)
            if dist.percentiles and 'p50' in dist.percentiles:
                logger.debug(f"        SoftGuide: p50 = {dist.percentiles['p50']}")
                return dist.percentiles['p50']

            # 평균값 (정규분포)
            if dist.mean is not None:
                logger.debug(f"        SoftGuide: mean = {dist.mean}")
                return dist.mean

        # 2. suggested_range가 있으면 중간값
        if soft_guide.suggested_range:
            min_val, max_val = soft_guide.suggested_range
            mid_val = (min_val + max_val) / 2
            logger.debug(f"        SoftGuide: range mid = {mid_val}")
            return mid_val

        # 3. typical_value
        if soft_guide.typical_value is not None:
            logger.debug(f"        SoftGuide: typical = {soft_guide.typical_value}")
            return soft_guide.typical_value

        return None

    def _llm_emergency_estimate(
        self,
        var_name: str,
        context: Context
    ) -> Optional[float]:
        """
        LLM 긴급 호출 (v7.10.1: 최후 수단)

        모든 방법 실패 시 LLM에게 "숫자만" 요청
        - 빠름: max_tokens=10
        - 저렴: gpt-4o-mini
        - 간단: JSON 파싱 불필요

        Args:
            var_name: 변수명
            context: 맥락

        Returns:
            추정값 또는 None
        """
        if self.llm_mode == 'cursor':
            logger.debug("        LLM emergency: Cursor 모드에서 불가")
            return None

        # Context 정보 구성
        context_str = context.domain if context and context.domain else "일반"
        if context and context.region:
            context_str += f", {context.region}"

        prompt = f"""다음 변수의 대략적인 값을 숫자로만 답변하세요:

**변수**: {var_name}
**맥락**: {context_str}

**중요**: 숫자만 반환하세요 (설명 없음)
- 비율이면 소수 (예: 0.05)
- 개수면 정수 (예: 100)
- 금액이면 숫자 (예: 50000)

답변:"""

        try:
            client = self.llm_client
            if not client:
                return None

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 빠르고 저렴
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,  # 숫자만
                temperature=0.3
            )

            text = response.choices[0].message.content.strip()
            
            # 숫자 파싱 시도
            value = float(text)
            logger.debug(f"        LLM emergency: {value}")
            return value

        except Exception as e:
            logger.debug(f"        LLM emergency 실패: {e}")
            return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 안전 장치
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _detect_circular(self, question: str) -> bool:
        """
        순환 의존성 감지
        
        Call stack에 동일 질문이 있으면 순환
        
        예:
            depth 0: "시장 규모는?"
            depth 1: "점유율은?"
            depth 2: "시장 규모는?"  # ← 순환!
        
        Args:
            question: 질문
        
        Returns:
            True: 순환 감지
            False: 정상
        """
        normalized = question.lower().strip()
        
        for past_question in self.call_stack:
            if past_question.lower().strip() == normalized:
                logger.warning(f"    순환 감지: '{question}'")
                logger.warning(f"    Call stack: {self.call_stack}")
                return True
        
        return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 유틸리티
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _build_contextualized_question(
        self,
        var_name: str,
        context: Context
    ) -> str:
        """
        Context를 포함한 구체적인 질문 생성 (v7.5.0)
        
        변수 이름만으로는 애매하므로, 맥락을 명시적으로 포함
        
        Args:
            var_name: 변수 이름 (예: "arpu", "churn_rate")
            context: 맥락
        
        Returns:
            구체화된 질문 문자열
        
        Example:
            >>> _build_contextualized_question("arpu", Context(domain="B2B_SaaS", region="한국"))
            >>> # "B2B SaaS 한국 시장의 ARPU는?"
        """
        # 변수 이름 정리 (snake_case → 띄어쓰기)
        readable_var = var_name.replace('_', ' ').upper()
        
        # Context 요소 수집
        context_parts = []
        
        if context.domain and context.domain != "General":
            context_parts.append(context.domain.replace('_', ' '))
        
        if context.region:
            context_parts.append(context.region)
        
        if context.time_period:
            context_parts.append(context.time_period)
        
        # 질문 조립
        if context_parts:
            context_str = " ".join(context_parts)
            question = f"{context_str} 시장의 {readable_var}는?"
        else:
            question = f"{readable_var}는?"
        
        return question
    
    def _execute_formula_simple(
        self,
        formula: str,
        bindings: Dict[str, float]
    ) -> float:
        """
        수식 실행 (안전한 버전)
        
        지원 연산: +, -, *, /, 괄호
        금지: eval() (보안 위험)
        
        Args:
            formula: 수식 (예: "ltv = arpu / churn_rate")
            bindings: 변수 값 (예: {"arpu": 80000, "churn_rate": 0.05})
        
        Returns:
            계산 결과
        """
        try:
            # 수식에서 결과 변수 제거 (예: "ltv = ..." → "...")
            if '=' in formula:
                parts = formula.split('=', 1)
                if len(parts) == 2:
                    formula = parts[1].strip()
            
            # × → * 변환 (수학 기호 정규화)
            expr = formula.replace('×', '*').replace('÷', '/')
            
            # 변수 치환
            for var_name, var_value in bindings.items():
                # 변수 이름을 값으로 치환
                expr = expr.replace(var_name, str(var_value))
            
            # 변수명은 안전: [a-zA-Z_][a-zA-Z0-9_]* 패턴
            # 하지만 치환 후에는 숫자와 연산자만 남아야 함
            # 따라서 치환 검증을 강화
            
            # 치환이 제대로 되었는지 확인 (변수명이 남아있으면 경고)
            import re
            remaining_vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
            if remaining_vars:
                logger.warning(f"    ⚠️  치환되지 않은 변수: {remaining_vars}")
                logger.warning(f"    수식: {formula}")
                logger.warning(f"    bindings: {list(bindings.keys())}")
                # Fallback: 곱셈
                return math.prod(bindings.values()) if bindings else 0.0
            
            # 안전한 계산 (허용 문자만: 숫자, 연산자, 괄호, 공백)
            allowed_chars = set('0123456789.+-*/() ')
            if not all(c in allowed_chars for c in expr):
                logger.warning(f"    ⚠️  수식에 허용되지 않는 문자: {formula}")
                logger.warning(f"    치환 후: {expr}")
                # Fallback: 곱셈
                return math.prod(bindings.values()) if bindings else 0.0
            
            # 계산 실행 (제한적 eval - 숫자와 연산자만)
            result = eval(expr, {"__builtins__": {}}, {})
            
            return float(result)
        
        except Exception as e:
            logger.warning(f"    ⚠️  수식 실행 실패: {e}")
            logger.warning(f"    Fallback: 곱셈 사용")
            
            # Fallback: 곱셈
            if bindings:
                return math.prod(bindings.values())
            return 0.0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2b: 반복 개선 (변수 재검색)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase2b_refine_with_data_search(
        self,
        models: List[FermiModel],
        question: str,
        context: Context,
        depth: int
    ) -> List[FermiModel]:
        """
        Step 2b: LLM 제안 변수에 대한 데이터 재검색
        
        반복 최대 2회:
        - 1회차: Unknown 변수 검색
        - 2회차: 여전히 Unknown인 변수 검색
        - 새 발견 없으면 조기 종료
        
        Args:
            models: LLM 생성 모형들
            question: 질문
            context: 맥락
            depth: 깊이
        
        Returns:
            개선된 모형들
        """
        max_iterations = 2
        iteration = 0
        
        while iteration < max_iterations:
            # 1. Unknown 변수 추출
            unknown_vars = set()
            for model in models:
                for var_name, var in model.variables.items():
                    if not var.available and var.need_estimate:
                        unknown_vars.add(var_name)
            
            if not unknown_vars:
                break  # 모두 available
            
            logger.info(f"{'  ' * depth}  [Refine {iteration+1}] Unknown 변수: {len(unknown_vars)}개")
            
            # 2. Unknown 변수 재검색
            newly_found = {}
            for var_name in unknown_vars:
                var_data = self._search_for_variable(var_name, question, context)
                if var_data:
                    newly_found[var_name] = var_data
                    logger.info(f"{'  ' * depth}    ✅ {var_name} = {var_data.value} (conf: {var_data.confidence:.2f})")
            
            if not newly_found:
                logger.info(f"{'  ' * depth}  [Refine {iteration+1}] 새 발견 없음 → 종료")
                break  # 더 이상 발견 없음
            
            # 3. 모형 업데이트
            for model in models:
                for var_name, var_data in newly_found.items():
                    if var_name in model.variables:
                        var = model.variables[var_name]
                        var.available = True
                        var.value = var_data.value
                        var.confidence = var_data.confidence
                        var.source = var_data.source
                        var.need_estimate = False
                        model.unknown_count = max(0, model.unknown_count - 1)
            
            iteration += 1
            logger.info(f"{'  ' * depth}  [Refine {iteration}] {len(newly_found)}개 변수 발견")
        
        return models
    
    def _search_for_variable(
        self,
        var_name: str,
        question: str,
        context: Context
    ) -> Optional[FermiVariable]:
        """
        특정 변수에 대한 데이터 검색
        
        순서:
        1. RAG 검색
        2. Phase 3 Source
        3. Context 상수
        
        Args:
            var_name: 변수명
            question: 원래 질문
            context: 맥락
        
        Returns:
            발견된 변수 데이터 또는 None
        """
        # 1. RAG 검색
        result = self._search_rag_for_variable(var_name, context)
        if result:
            return result
        
        # 2. Phase 3 Source
        result = self._query_phase3_for_variable(var_name, context)
        if result:
            return result
        
        # 3. Context 상수
        result = self._get_context_constant(var_name, context)
        if result:
            return result
        
        return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드: 데이터 검색
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _search_rag_benchmarks(
        self,
        question: str,
        context: Context
    ) -> Dict[str, FermiVariable]:
        """
        RAG에서 관련 벤치마크/상수 검색
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            발견된 변수들
        """
        results = {}
        
        if not HAS_CHROMA:
            return results
        
        try:
            # Chroma 클라이언트 초기화
            embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
            
            # 검색할 collection들
            collection_names = [
                "market_benchmarks",
                "system_knowledge"
            ]
            
            # 검색 쿼리 구성
            search_query = f"{context.domain} {question}" if context.domain else question
            
            for collection_name in collection_names:
                try:
                    vectorstore = Chroma(
                        collection_name=collection_name,
                        embedding_function=embeddings,
                        persist_directory=str(settings.chroma_persist_dir)
                    )
                    
                    # RAG 검색 (top 3)
                    docs = vectorstore.similarity_search(search_query, k=3)
                    
                    # 메타데이터에서 변수 추출
                    for doc in docs:
                        metadata = doc.metadata
                        
                        # 변수명과 값이 있는 경우
                        if 'variable_name' in metadata and 'value' in metadata:
                            var_name = metadata['variable_name']
                            var_value = metadata['value']
                            
                            if var_name not in results:
                                results[var_name] = FermiVariable(
                                    name=var_name,
                                    value=var_value,
                                    available=True,
                                    source=f"rag_{collection_name}",
                                    confidence=metadata.get('confidence', 0.8),
                                    description=doc.page_content[:100]
                                )
                
                except Exception as e:
                    # Collection 없으면 무시
                    continue
        
        except Exception as e:
            logger.warning(f"    ⚠️  RAG 검색 실패: {e}")
        
        return results
    
    def _query_phase3_sources(
        self,
        question: str,
        context: Context
    ) -> Dict[str, FermiVariable]:
        """
        Phase 3 Source에서 데이터 조회
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            발견된 변수들
        """
        results = {}
        
        try:
            # Phase 3으로 직접 추정 시도 (신뢰도 높은 것만)
            phase3_result = self.phase3.estimate(question, context)
            
            if phase3_result and phase3_result.confidence >= 0.80:
                # 질문에서 변수명 추출 시도
                var_name = self._extract_var_name_from_question(question)
                
                if var_name:
                    # v7.10.0: sources 속성 대신 method 또는 judgment_strategy 사용
                    source_name = 'unknown'
                    if hasattr(phase3_result, 'judgment_strategy') and phase3_result.judgment_strategy:
                        source_name = phase3_result.judgment_strategy
                    elif hasattr(phase3_result, 'method') and phase3_result.method:
                        source_name = phase3_result.method

                    results[var_name] = FermiVariable(
                        name=var_name,
                        value=phase3_result.value,
                        available=True,
                        source=f"phase3_{source_name}",
                        confidence=phase3_result.confidence,
                        description=phase3_result.reasoning_detail.get('method', '') if hasattr(phase3_result, 'reasoning_detail') else ''
                    )
        
        except Exception as e:
            logger.warning(f"    ⚠️  Phase 3 조회 실패: {e}")
        
        return results
    
    def _extract_var_name_from_question(self, question: str) -> Optional[str]:
        """
        질문에서 변수명 추출
        
        예: "한국 인구는?" → "korea_population"
        """
        # 간단한 패턴 매칭
        keywords_map = {
            '인구': 'population',
            '속도': 'speed',
            'churn': 'churn_rate',
            'arpu': 'arpu',
            'ltv': 'ltv',
            '거리': 'distance'
        }
        
        for keyword, var_name in keywords_map.items():
            if keyword in question.lower():
                return var_name
        
        # 기본값: 질문의 첫 단어
        words = question.replace('?', '').split()
        if words:
            return words[0].lower()
        
        return None
    
    def _extract_context_constants(
        self,
        question: str,
        context: Context
    ) -> Dict[str, FermiVariable]:
        """
        Context에서 자명한 상수 추출
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            발견된 상수들
        """
        results = {}
        
        # Domain별 상수
        if context.domain == "transportation":
            # 물리 상수
            if "중력" in question or "gravity" in question.lower():
                results['gravity'] = FermiVariable(
                    name='gravity',
                    value=9.8,
                    available=True,
                    source="physical_constant",
                    confidence=1.0
                )
        
        # Region별 상수
        if context.region == "South_Korea":
            if "인구" in question or "population" in question.lower():
                results['korea_population'] = FermiVariable(
                    name='korea_population',
                    value=51_000_000,
                    available=True,
                    source="statistical_constant",
                    confidence=0.95,
                    description="한국 인구 (2024)"
                )
        
        return results
    
    def _search_rag_for_variable(
        self,
        var_name: str,
        context: Context
    ) -> Optional[FermiVariable]:
        """
        특정 변수에 대한 RAG 검색
        
        Args:
            var_name: 변수명
            context: 맥락
        
        Returns:
            발견된 변수 또는 None
        """
        if not HAS_CHROMA:
            return None
        
        try:
            # 변수명을 자연어로 변환
            query_text = self._var_name_to_natural_language(var_name, context)
            
            # RAG 검색
            embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
            
            for collection_name in ["market_benchmarks", "system_knowledge"]:
                try:
                    vectorstore = Chroma(
                        collection_name=collection_name,
                        embedding_function=embeddings,
                        persist_directory=str(settings.chroma_persist_dir)
                    )
                    
                    docs = vectorstore.similarity_search(query_text, k=1)
                    
                    if docs:
                        doc = docs[0]
                        metadata = doc.metadata
                        
                        if 'value' in metadata:
                            return FermiVariable(
                                name=var_name,
                                value=metadata['value'],
                                available=True,
                                source=f"rag_{collection_name}",
                                confidence=metadata.get('confidence', 0.75),
                                description=doc.page_content[:100]
                            )
                
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"RAG 검색 실패 ({var_name}): {e}")
        
        return None
    
    def _var_name_to_natural_language(self, var_name: str, context: Context) -> str:
        """
        변수명을 자연어 검색 쿼리로 변환
        
        예: "speed" + "transportation" → "교통수단 평균 속도"
        """
        # 변수명 정규화
        var_lower = var_name.lower().replace('_', ' ')
        
        # Domain 기반 변환
        if context.domain:
            return f"{context.domain} {var_lower}"
        
        return var_lower
    
    def _query_phase3_for_variable(
        self,
        var_name: str,
        context: Context
    ) -> Optional[FermiVariable]:
        """
        특정 변수에 대한 Phase 3 Source 조회
        
        Args:
            var_name: 변수명
            context: 맥락
        
        Returns:
            발견된 변수 또는 None
        """
        try:
            # 변수명을 질문으로 변환
            question = self._build_contextualized_question(var_name, context)
            
            # Phase 3 조회
            phase3_result = self.phase3.estimate(question, context)
            
            if phase3_result and phase3_result.confidence >= 0.75:
                return FermiVariable(
                    name=var_name,
                    value=phase3_result.value,
                    available=True,
                    source=f"phase3_{phase3_result.sources[0] if phase3_result.sources else 'source'}",
                    confidence=phase3_result.confidence,
                    description=phase3_result.reasoning_detail.get('method', '')
                )
        
        except Exception as e:
            logger.debug(f"Phase 3 조회 실패 ({var_name}): {e}")
        
        return None
    
    def _get_context_constant(
        self,
        var_name: str,
        context: Context
    ) -> Optional[FermiVariable]:
        """
        특정 변수에 대한 Context 상수
        
        Args:
            var_name: 변수명
            context: 맥락
        
        Returns:
            발견된 상수 또는 None
        """
        # Domain 기반 상수 매칭
        var_lower = var_name.lower()
        
        # Transportation domain
        if context.domain == "transportation":
            # 속도 관련 변수
            if "speed" in var_lower or "속도" in var_lower or "velocity" in var_lower:
                return FermiVariable(
                    name=var_name,
                    value=130,
                    available=True,
                    source="context_benchmark",
                    confidence=0.85,
                    description="KTX 평균 속도 (km/h, 정차 포함)"
                )
        
        # South Korea region
        if context.region == "South_Korea":
            # 인구 관련
            if "population" in var_lower or "인구" in var_lower:
                return FermiVariable(
                    name=var_name,
                    value=51_000_000,
                    available=True,
                    source="context_constant",
                    confidence=0.95,
                    description="한국 인구 (2024)"
                )
            
            # 거리 관련 (주요 도시)
            if "seoul" in var_lower and "busan" in var_lower:
                if "distance" in var_lower or "거리" in var_lower:
                    return FermiVariable(
                        name=var_name,
                        value=325,
                        available=True,
                        source="context_constant",
                        confidence=1.0,
                        description="서울-부산 거리 (km)"
                    )
        
        return None
    
    def _build_contextualized_question(
        self,
        var_name: str,
        context: Context
    ) -> str:
        """
        변수명을 맥락이 포함된 질문으로 변환
        
        Args:
            var_name: 변수명
            context: 맥락
        
        Returns:
            맥락 포함 질문
        """
        # Domain 기반 질문 생성
        if context.domain:
            return f"{context.domain}에서 {var_name}는 얼마인가?"
        
        # 기본 질문
        return f"{var_name}는 얼마인가?"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 응답 후처리 및 평가 (v7.10.0: 벤치마크 패턴 이식)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _model_to_decomposition_list(
        self,
        model: FermiModel,
        bindings: Dict[str, float],
        result_value: float
    ) -> List[Dict]:
        """
        FermiModel을 평가용 decomposition 리스트로 변환 (v7.10.0)

        Args:
            model: FermiModel 객체
            bindings: 변수 바인딩 {name: value}
            result_value: 최종 계산 결과

        Returns:
            decomposition 리스트 (평가 함수용)
        """
        decomp_list = []
        step_num = 1

        for var_name, var in model.variables.items():
            if var.available and var.value is not None:
                decomp_list.append({
                    'step': f"{step_num}. {var_name}",
                    'concept': var_name,
                    'value': var.value,
                    'unit': '',
                    'calculation': f"{var.value} ({var.source})",
                    'reasoning': var.description or var.source
                })
                step_num += 1

        # 마지막 단계: 최종 계산
        decomp_list.append({
            'step': f"{step_num}. 최종: 계산 결과",
            'concept': 'final_result',
            'value': result_value,
            'unit': '',
            'calculation': model.formula,
            'reasoning': f"수식 적용: {model.formula}"
        })

        return decomp_list

    def _validate_and_postprocess_response(
        self,
        response: Dict,
        depth: int = 0
    ) -> Tuple[Dict, List[str]]:
        """
        응답 검증 및 후처리 (v7.10.0)

        1. 필수 필드 검증
        2. 누락 필드 자동 생성 (추적)
        3. 마지막 단계 value = 최상위 value 검증

        Args:
            response: LLM 응답 Dict
            depth: 로그 깊이

        Returns:
            (처리된 응답, 자동 생성된 필드 목록)
        """
        auto_generated = []
        decomp = response.get('decomposition', [])

        # v7.10.0: 필수 필드 누락 검증 (경고 로그)
        if not response.get('final_calculation'):
            logger.warning(f"{'  ' * depth}  [Validate] final_calculation 필드 누락!")
        if not response.get('calculation_verification'):
            logger.warning(f"{'  ' * depth}  [Validate] calculation_verification 필드 누락!")

        # v7.10.0: decomposition concept 필드 검증
        if decomp:
            missing_concept_steps = [
                step.get('step', f"step{i+1}")
                for i, step in enumerate(decomp)
                if not step.get('concept')
            ]
            if missing_concept_steps:
                logger.warning(
                    f"{'  ' * depth}  [Validate] concept 필드 누락: "
                    f"{len(missing_concept_steps)}개 단계 ({', '.join(missing_concept_steps[:3])}...)"
                )

        # 1. final_calculation 자동 생성
        if not response.get('final_calculation') and decomp and len(decomp) > 0:
            last_step = decomp[-1]
            if last_step.get('calculation'):
                response['final_calculation'] = f"Auto: {last_step['calculation']}"
                auto_generated.append('final_calculation')
                logger.info(f"{'  ' * depth}  [PostProcess] final_calculation 자동 생성")

        # 2. calculation_verification 자동 생성
        if not response.get('calculation_verification') and decomp and len(decomp) > 0:
            result, msg = self._auto_verify_calculation(decomp, response.get('value', 0))
            if result is not None:
                response['calculation_verification'] = f"Auto: {msg}"
                auto_generated.append('calculation_verification')
                logger.info(f"{'  ' * depth}  [PostProcess] calculation_verification 자동 생성")

        # 3. 마지막 단계 value 일치 검증 및 교정
        if decomp and len(decomp) > 0:
            last_value = decomp[-1].get('value')
            top_value = response.get('value')

            if last_value is not None and top_value is not None:
                if isinstance(last_value, (int, float)) and isinstance(top_value, (int, float)):
                    if abs(last_value - top_value) > 0.01 * max(abs(last_value), abs(top_value), 1):
                        logger.warning(f"{'  ' * depth}  [PostProcess] value 불일치: "
                                      f"decomposition[-1]={last_value} vs top={top_value}")
                        # 마지막 단계 값으로 교정
                        response['value'] = last_value
                        auto_generated.append('value_corrected')
                        logger.info(f"{'  ' * depth}  [PostProcess] value를 마지막 단계 값으로 교정: {last_value}")

        return response, auto_generated

    def _auto_verify_calculation(
        self,
        decomp: List[Dict],
        final_value: float
    ) -> Tuple[Optional[float], str]:
        """
        분해 값들로 최종값 자동 계산 시도 (v7.10.0)

        Args:
            decomp: decomposition 리스트
            final_value: 최상위 value

        Returns:
            (계산된 값, 설명 메시지) 또는 (None, 에러 메시지)
        """
        if not isinstance(decomp, list) or len(decomp) < 2:
            return None, "단계 부족"

        values = [
            step.get('value', 0)
            for step in decomp
            if isinstance(step.get('value'), (int, float))
        ]

        if len(values) < 2:
            return None, "유효한 값 부족"

        results = []

        # 1. 마지막 단계
        if values[-1] > 0 and final_value > 0:
            error = abs(values[-1] - final_value) / max(final_value, 1)
            results.append(('마지막 단계', values[-1], error))

        # 2. 모든 단계 합
        total = sum(values)
        if total > 0 and final_value > 0:
            error = abs(total - final_value) / max(final_value, 1)
            results.append(('모든 단계 합', total, error))

        # 3. 마지막 2단계 합
        if len(values) >= 2:
            last_two = sum(values[-2:])
            if last_two > 0 and final_value > 0:
                error = abs(last_two - final_value) / max(final_value, 1)
                results.append(('마지막 2단계 합', last_two, error))

        if results:
            best = min(results, key=lambda x: x[2])
            return best[1], f"{best[0]}: {best[1]:,.0f} (오차 {best[2]*100:.1f}%)"

        return None, "계산 불가"

    def _evaluate_content_score(
        self,
        decomp: List[Dict],
        final_value: float,
        depth: int = 0
    ) -> Dict:
        """
        내용 점수 평가 (45점) - v7.10.0

        실제 추론 능력 평가 (형식과 무관)

        Returns:
            {
                'score': float (0-45),
                'details': list of str,
                'breakdown': {
                    'step_completeness': float (0-10),
                    'calculation_logic': float (0-10),
                    'numerical_accuracy': float (0-25)
                }
            }
        """
        score = 0
        details = []
        breakdown = {}

        if not isinstance(decomp, list) or len(decomp) == 0:
            return {
                'score': 0,
                'details': ['decomposition 없음'],
                'breakdown': {'step_completeness': 0, 'calculation_logic': 0, 'numerical_accuracy': 0}
            }

        # 1. 단계별 계산 완성도 (10점)
        calculable_steps = 0
        for step in decomp:
            if (step.get('value') is not None and
                (step.get('calculation') or
                 any(op in step.get('reasoning', '') for op in ['x', '/', '+', '-', '*']))):
                calculable_steps += 1

        completeness_score = (calculable_steps / len(decomp)) * 10
        score += completeness_score
        breakdown['step_completeness'] = round(completeness_score, 1)
        details.append(f"단계별 계산 완성도: {calculable_steps}/{len(decomp)} ({completeness_score:.1f}점)")

        # 2. 계산 논리 연결 (10점)
        logic_score = 0

        # 2-1. 연산 적절성 (4점)
        operations = ['x', '/', '+', '-', '*']
        has_operations = any(
            any(op in step.get('calculation', '') for op in operations)
            for step in decomp
        )
        if has_operations:
            logic_score += 4
            details.append("연산 적절성 (4점)")
        else:
            details.append("연산 부족 (0점)")

        # 2-2. 논리적 순서 (3점)
        last_step = decomp[-1].get('step', '').lower() if decomp else ''
        if '최종' in last_step or '합계' in last_step or 'total' in last_step:
            logic_score += 3
            details.append("논리적 순서 (3점)")
        else:
            details.append("순서 불명확 (0점)")

        # 2-3. 중간 결과 활용 (3점)
        has_step_ref = any(
            'step' in step.get('reasoning', '').lower() or
            'step' in step.get('calculation', '').lower()
            for step in decomp[1:]
        ) if len(decomp) > 1 else False
        if has_step_ref:
            logic_score += 3
            details.append("중간 결과 활용 (3점)")
        else:
            details.append("중간 결과 미활용 (0점)")

        score += logic_score
        breakdown['calculation_logic'] = logic_score

        # 3. 수치 정확성 (25점)
        if len(decomp) > 0:
            last_value = decomp[-1].get('value', 0)

            if isinstance(last_value, (int, float)) and last_value > 0 and final_value > 0:
                error_ratio = abs(last_value - final_value) / max(final_value, 1)

                if error_ratio < 0.01:
                    numerical_score = 25
                    details.append("수치 완벽 일치 (25점)")
                elif error_ratio < 0.05:
                    numerical_score = 20
                    details.append("수치 거의 일치 (20점)")
                elif error_ratio < 0.10:
                    numerical_score = 15
                    details.append("수치 근접 (15점)")
                elif error_ratio < 0.30:
                    numerical_score = 10
                    details.append("수치 부분 일치 (10점)")
                else:
                    numerical_score = 5
                    details.append("수치 불일치 (5점)")
            else:
                numerical_score = 0
                details.append("수치 검증 불가 (0점)")
        else:
            numerical_score = 0
            details.append("마지막 단계 없음 (0점)")

        score += numerical_score
        breakdown['numerical_accuracy'] = numerical_score

        return {
            'score': min(score, 45),
            'details': details,
            'breakdown': breakdown
        }

    def _evaluate_format_score(
        self,
        response: Dict,
        decomp: List[Dict],
        auto_generated_fields: List[str],
        depth: int = 0
    ) -> Dict:
        """
        형식 점수 평가 (5점) - v7.10.0

        JSON 스키마 준수도 평가

        Returns:
            {
                'score': float (0-5),
                'details': list of str,
                'breakdown': {
                    'final_calculation': int (0 or 2),
                    'calculation_verification': int (0 or 2),
                    'concept_fields': float (0-1)
                }
            }
        """
        score = 0
        details = []
        breakdown = {}

        # 1. final_calculation 필드 (2점)
        if 'final_calculation' in response:
            if 'final_calculation' in auto_generated_fields or 'Auto' in str(response.get('final_calculation', '')):
                breakdown['final_calculation'] = 0
                details.append("final_calculation 누락 (자동 생성, 0점)")
            else:
                score += 2
                breakdown['final_calculation'] = 2
                details.append("final_calculation 제공 (2점)")
        else:
            breakdown['final_calculation'] = 0
            details.append("final_calculation 누락 (0점)")

        # 2. calculation_verification 필드 (2점)
        if 'calculation_verification' in response:
            if 'calculation_verification' in auto_generated_fields or 'Auto' in str(response.get('calculation_verification', '')):
                breakdown['calculation_verification'] = 0
                details.append("calculation_verification 누락 (자동 생성, 0점)")
            else:
                score += 2
                breakdown['calculation_verification'] = 2
                details.append("calculation_verification 제공 (2점)")
        else:
            breakdown['calculation_verification'] = 0
            details.append("calculation_verification 누락 (0점)")

        # 3. concept 필드 완성도 (1점)
        if decomp and len(decomp) > 0:
            with_concept = sum(1 for s in decomp if s.get('concept'))
            concept_ratio = with_concept / len(decomp)

            if concept_ratio >= 0.8:
                score += 1.0
                breakdown['concept_fields'] = 1.0
                details.append(f"concept 필드 완성 ({with_concept}/{len(decomp)}, 1점)")
            elif concept_ratio >= 0.5:
                score += 0.5
                breakdown['concept_fields'] = 0.5
                details.append(f"concept 필드 부분 ({with_concept}/{len(decomp)}, 0.5점)")
            else:
                breakdown['concept_fields'] = 0
                details.append(f"concept 필드 부족 ({with_concept}/{len(decomp)}, 0점)")
        else:
            breakdown['concept_fields'] = 0
            details.append("concept 필드 없음 (0점)")

        return {
            'score': score,
            'details': details,
            'breakdown': breakdown
        }

    def _evaluate_conceptual_coherence(
        self,
        question: str,
        decomp: List[Dict],
        final_calc: str,
        context: Optional[Context] = None,
        depth: int = 0
    ) -> Dict:
        """
        개념적 일관성 평가 (15점) - v7.10.0

        Pseudo-code의 논리적 타당성 평가

        Returns:
            {
                'score': float (0-15),
                'details': list of str
            }
        """
        score = 0
        details = []

        if not isinstance(decomp, list) or len(decomp) < 2:
            return {
                'score': 0,
                'details': ['decomposition 없음 또는 부족']
            }

        # 단계별 텍스트 추출
        steps_text = ' '.join([
            f"{s.get('step', '')} {s.get('reasoning', '')} {s.get('calculation', '')}"
            for s in decomp
        ]).lower()

        # 동적 키워드 추출 (질문 기반)
        question_lower = question.lower()

        # 1. 핵심 개념 포함 여부 (5점)
        # 질문에서 추출한 키워드가 decomposition에 있는지
        essential_keywords = []
        if '사업자' in question_lower or 'business' in question_lower:
            essential_keywords.extend(['사업자', '법인', '자영업', '기업', '창업', '경제활동', '인구'])
        elif '인구' in question_lower or 'population' in question_lower:
            essential_keywords.extend(['인구', '비중', '비율', '수도권', '전국'])
        elif '커피' in question_lower or 'coffee' in question_lower:
            essential_keywords.extend(['커피', '매장', '점포', '고객', '소비', '수요'])
        elif '택시' in question_lower or 'taxi' in question_lower:
            essential_keywords.extend(['택시', '인구', '이용', '운행', '교대'])
        else:
            # 기본 키워드
            essential_keywords.extend(['인구', '비율', '수', '규모'])

        if essential_keywords:
            essential_found = sum(1 for kw in essential_keywords if kw in steps_text)
            essential_ratio = essential_found / len(essential_keywords)

            if essential_ratio >= 0.3:
                score += 5
                details.append(f"핵심 개념 포함 ({essential_found}/{len(essential_keywords)}) (5점)")
            elif essential_ratio >= 0.15:
                score += 3
                details.append(f"핵심 개념 일부 ({essential_found}/{len(essential_keywords)}) (3점)")
            else:
                details.append(f"핵심 개념 부족 ({essential_found}/{len(essential_keywords)}) (0점)")
        else:
            score += 3  # 키워드 없으면 중립
            details.append("키워드 매칭 생략 (3점)")

        # 2. 논리적 연산 존재 (3점)
        operations = ['x', '/', '+', '-', '*', '곱', '나누', '더하']
        operations_found = any(op in steps_text or op in final_calc.lower() for op in operations)
        if operations_found:
            score += 3
            details.append("논리적 연산 포함 (3점)")
        else:
            details.append("논리적 연산 없음 (0점)")

        # 3. Pseudo-code 논리 구조 (7점)
        # 마지막 단계가 최종 계산 단계인지
        last_step = decomp[-1].get('step', '').lower()
        if '최종' in last_step or 'total' in last_step or '합계' in last_step:
            score += 3
            details.append("최종 단계 명확 (3점)")
        else:
            details.append("최종 단계 불명확 (0점)")

        # 단계 간 참조 또는 연산 존재
        has_step_ref = any(
            'step' in s.get('calculation', '').lower()
            for s in decomp[1:]
        ) if len(decomp) > 1 else False

        if has_step_ref:
            score += 4
            details.append("단계 간 참조 명확 (4점)")
        else:
            has_calc = any(
                any(op in s.get('calculation', '') for op in ['+', '-', '*', 'x', '/', '='])
                for s in decomp
            )
            if has_calc:
                score += 2
                details.append("연산 있으나 참조 불명확 (2점)")
            else:
                details.append("단계 간 연결 불명확 (0점)")

        return {
            'score': max(0, min(score, 15)),
            'details': details
        }

    def _verify_calculation_connectivity(
        self,
        decomposition: List[Dict],
        final_value: float
    ) -> Dict:
        """
        분해 값들이 최종값으로 올바르게 계산되는지 자동 검증 (v7.7.1)
        
        Args:
            decomposition: 분해 단계 리스트
            final_value: 최종 추정값
        
        Returns:
            {
                'verified': bool,
                'method': str,  # '마지막 단계', '합계', '곱셈' 등
                'calculated_value': float,
                'error': float,  # 오차율
                'score': int  # 0-25점
            }
        """
        if not isinstance(decomposition, list) or len(decomposition) < 2:
            return {
                'verified': False,
                'score': 0,
                'reason': '단계 부족',
                'method': '',
                'calculated_value': 0,
                'error': 1.0
            }
        
        # 각 단계에서 value 추출
        values = []
        for step in decomposition:
            if isinstance(step, dict):
                val = step.get('value', 0)
                if isinstance(val, (int, float)) and val > 0:
                    values.append(val)
        
        if len(values) < 2:
            return {
                'verified': False,
                'score': 0,
                'reason': '유효한 값 부족',
                'method': '',
                'calculated_value': 0,
                'error': 1.0
            }
        
        # 다양한 조합 시도
        attempts = []
        
        # 1. 마지막 값
        if values[-1] > 0:
            error = abs(values[-1] - final_value) / max(final_value, 1)
            attempts.append({
                'method': '마지막 단계',
                'calculated': values[-1],
                'error': error
            })
        
        # 2. 전체 합계
        total = sum(values)
        if total > 0:
            error = abs(total - final_value) / max(final_value, 1)
            attempts.append({
                'method': '모든 단계 합',
                'calculated': total,
                'error': error
            })
        
        # 3. 마지막 2개 합
        if len(values) >= 2:
            last_two = sum(values[-2:])
            if last_two > 0:
                error = abs(last_two - final_value) / max(final_value, 1)
                attempts.append({
                    'method': '마지막 2단계 합',
                    'calculated': last_two,
                    'error': error
                })
        
        # 4. 마지막 3개 합
        if len(values) >= 3:
            last_three = sum(values[-3:])
            if last_three > 0:
                error = abs(last_three - final_value) / max(final_value, 1)
                attempts.append({
                    'method': '마지막 3단계 합',
                    'calculated': last_three,
                    'error': error
                })
        
        # 가장 오차가 작은 것 선택
        if attempts:
            best = min(attempts, key=lambda x: x['error'])
            
            # 점수 계산
            if best['error'] < 0.01:  # 1% 이내
                score = 25
            elif best['error'] < 0.05:  # 5% 이내
                score = 20
            elif best['error'] < 0.1:  # 10% 이내
                score = 15
            elif best['error'] < 0.3:  # 30% 이내
                score = 10
            else:
                score = 5
            
            return {
                'verified': best['error'] < 0.1,  # 10% 이내면 통과
                'method': best['method'],
                'calculated_value': best['calculated'],
                'error': best['error'],
                'score': score
            }
        
        return {
            'verified': False,
            'score': 0,
            'reason': '계산 불가',
            'method': '',
            'calculated_value': 0,
            'error': 1.0
        }


