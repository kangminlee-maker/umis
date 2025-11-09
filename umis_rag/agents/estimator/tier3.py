"""
Tier 3: Fermi Model Search

재귀 분해 추정 - 논리의 퍼즐 맞추기

설계: config/fermi_model_search.yaml (1,269줄)
원리: 가용 데이터(Bottom-up) + 개념 분해(Top-down) 반복
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
    ComponentEstimation, Tier3Config
)
from umis_rag.agents.estimator.tier2 import Tier2JudgmentPath
from umis_rag.utils.logger import logger
from umis_rag.core.config import settings

# LLM API
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("OpenAI 패키지 없음 (pip install openai)")

import yaml
import re


# ═══════════════════════════════════════════════════════
# 비즈니스 지표 템플릿 - REMOVED (v7.5.0)
# ═══════════════════════════════════════════════════════
# 
# v7.5.0 변경:
# - 비즈니스 지표 계산 공식은 Quantifier로 이동
# - Estimator는 순수 값 추정만 담당
# - Tier 3는 일반적 Fermi 분해에 집중
#
# 이전 위치: tier3.py BUSINESS_METRIC_TEMPLATES
# 신규 위치: data/raw/calculation_methodologies.yaml (Quantifier)
#
# ═══════════════════════════════════════════════════════

# v7.5.0: 비즈니스 지표 템플릿 제거됨
# Quantifier가 LTV, CAC, ARPU 등의 계산 공식 소유
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
# 데이터 모델 (Tier 3 전용)
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
# Tier 3 메인 클래스
# ═══════════════════════════════════════════════════════

class Tier3FermiPath:
    """
    Tier 3: Fermi Model Search
    
    재귀 분해 추정 - 논리의 퍼즐 맞추기
    
    프로세스:
    ---------
    Phase 1: 초기 스캔 (가용 데이터 파악, Bottom-up)
    Phase 2: 모형 생성 (LLM 3-5개 후보, Top-down)
    Phase 3: 실행 가능성 체크 (재귀 추정으로 퍼즐 맞추기)
    Phase 4: 모형 실행 (Backtracking으로 재조립)
    
    안전 장치:
    ----------
    - Max depth: 4 (무한 재귀 방지)
    - 순환 감지: Call stack 추적
    - 변수 제한: 6개 권장, 10개 절대
    
    Usage:
        >>> tier3 = Tier3FermiPath()
        >>> result = tier3.estimate(
        ...     "음식점 SaaS 시장은?",
        ...     context=Context(domain="Food_Service")
        ... )
        >>> result.decomposition.depth  # 2
        >>> result.value  # 20,160,000,000
    """
    
    def __init__(self, config: Tier3Config = None):
        """초기화"""
        self.config = config or Tier3Config()
        
        # Tier 2 의존성
        self.tier2 = Tier2JudgmentPath()
        
        # 재귀 추적
        self.call_stack: List[str] = []
        self.max_depth = self.config.max_depth  # 4
        
        # 변수 정책
        self.variable_policy = SimpleVariablePolicy()
        
        # LLM 모드 (config/llm_mode.yaml 준수)
        self.llm_mode = getattr(settings, 'llm_mode', 'native')  # 기본: native
        self.llm_client = None
        
        # External mode일 때만 API 초기화
        if self.llm_mode == 'external':
            if HAS_OPENAI and settings.openai_api_key:
                self.llm_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("  ✅ External LLM (OpenAI API) 준비")
            else:
                logger.warning("  ⚠️  External mode지만 OpenAI API 키 없음 (Fallback: 템플릿만)")
        else:
            logger.info("  ✅ Native Mode (Cursor LLM, 비용 $0)")
            logger.info("     LLM 모형 생성: 템플릿만 사용 (80-90% 커버)")
        
        logger.info("[Tier 3] Fermi Model Search 초기화")
        logger.info(f"  Max depth: {self.max_depth}")
        logger.info(f"  변수 정책: 권장 6개, 절대 10개")
        logger.info(f"  LLM 모드: {self.llm_mode}")
    
    def estimate(
        self,
        question: str,
        context: Context = None,
        available_data: Dict = None,
        depth: int = 0,
        parent_data: Dict = None
    ) -> Optional[EstimationResult]:
        """
        Fermi Decomposition 추정
        
        Args:
            question: 질문 (예: "음식점 SaaS 시장은?")
            context: 맥락 (domain, region, time)
            available_data: 가용 데이터 (프로젝트 제공)
            depth: 현재 재귀 깊이
            parent_data: 부모 데이터 (재귀 시 상속) v7.5.0+
        
        Returns:
            EstimationResult (decomposition 포함) 또는 None
        """
        start_time = time.time()
        
        logger.info(f"\n{'  ' * depth}[Tier 3] Fermi Estimation (depth {depth})")
        logger.info(f"{'  ' * depth}  질문: {question}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 안전 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 1. Max depth 체크
        if depth >= self.max_depth:
            logger.warning(f"{'  ' * depth}  ⚠️  Max depth {self.max_depth} 도달 → Tier 2 Fallback")
            # Fallback to Tier 2
            return self.tier2.estimate(question, context or Context())
        
        # 2. 순환 감지
        if self._detect_circular(question):
            logger.warning(f"{'  ' * depth}  ⚠️  순환 의존성 감지 (A→B→A) → 중단")
            return None
        
        # 3. Call stack 추가
        self.call_stack.append(question)
        
        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Phase 1: 초기 스캔 (데이터 상속 v7.5.0)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            scan_result = self._phase1_scan(question, context, available_data, depth, parent_data)
            
            if not scan_result:
                logger.warning(f"{'  ' * depth}  ❌ Phase 1 실패")
                return None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Phase 2: 모형 생성
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            candidate_models = self._phase2_generate_models(
                question,
                scan_result['available'],
                scan_result['unknown'],
                depth
            )
            
            if not candidate_models:
                logger.warning(f"{'  ' * depth}  ❌ Phase 2 실패 (모형 없음)")
                return None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Phase 3: 실행 가능성 체크 (재귀!)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            ranked_models = self._phase3_check_feasibility(
                candidate_models,
                context or Context(),
                depth
            )
            
            if not ranked_models:
                logger.warning(f"{'  ' * depth}  ❌ Phase 3 실패 (실행 불가능)")
                return None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Phase 4: 최선 모형 실행
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            result = self._phase4_execute(ranked_models[0], depth, context or Context())
            
            if result:
                execution_time = time.time() - start_time
                logger.info(f"{'  ' * depth}  ✅ Tier 3 완료: {result.value} ({execution_time:.2f}초)")
            
            return result
        
        except Exception as e:
            logger.error(f"{'  ' * depth}  ❌ Tier 3 에러: {e}")
            return None
        
        finally:
            # Call stack에서 제거 (중요!)
            if self.call_stack and self.call_stack[-1] == question:
                self.call_stack.pop()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 1: 초기 스캔 (가용 데이터 파악)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase1_scan(
        self,
        question: str,
        context: Optional[Context],
        available_data: Optional[Dict],
        depth: int,
        parent_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Phase 1: 초기 스캔 (Bottom-up)
        
        가용한 데이터 파악:
        1. 부모 데이터 상속 (재귀 시) v7.5.0+
        2. 프로젝트 데이터 (available_data)
        3. 맥락에서 자명한 데이터
        
        Args:
            question: 질문
            context: 맥락
            available_data: 프로젝트 데이터
            depth: 깊이
            parent_data: 부모 데이터 (v7.5.0+)
        
        Returns:
            {
                'available': Dict[str, FermiVariable],
                'unknown': List[str]
            }
        """
        logger.info(f"{'  ' * depth}  [Phase 1] 초기 스캔")
        
        available = {}
        
        # Step 0: 부모 데이터 상속 (v7.5.0+)
        if parent_data:
            for key, val in parent_data.items():
                if isinstance(val, FermiVariable):
                    # 부모 변수 그대로 상속
                    available[key] = val
                    logger.info(f"{'  ' * depth}    부모로부터 상속: {key} = {val.value}")
                elif isinstance(val, dict):
                    available[key] = FermiVariable(
                        name=key,
                        available=True,
                        value=val.get('value'),
                        source=val.get('source', 'parent_inherited'),
                        confidence=val.get('confidence', 0.8)
                    )
        
        # Step 1: 프로젝트 데이터
        if available_data:
            for key, val in available_data.items():
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
                    # 단순 값
                    available[key] = FermiVariable(
                        name=key,
                        available=True,
                        value=val,
                        source="project_data",
                        confidence=1.0,
                        uncertainty=0.0
                    )
        
        # Step 2: 맥락에서 자명한 데이터
        # (예: 시간 제약 등)
        if context:
            # TODO: context 기반 자명한 변수 추가
            pass
        
        logger.info(f"{'  ' * depth}    가용 데이터: {len(available)}개")
        
        return {
            'available': available,
            'unknown': []  # Phase 2에서 모형별로 파악
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 2: 모형 생성 (LLM)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase2_generate_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        unknown: List[str],
        depth: int
    ) -> List[FermiModel]:
        """
        Phase 2: 모형 생성 (Top-down)
        
        LLM에게 여러 후보 모형 요청
        
        현재: 기본 템플릿 사용 (LLM API 구현 대기)
        TODO: OpenAI/Anthropic API 통합
        
        Args:
            question: 질문
            available: 가용 변수
            unknown: 미지수 리스트
            depth: 깊이
        
        Returns:
            3-5개 FermiModel 후보
        """
        logger.info(f"{'  ' * depth}  [Phase 2] 모형 생성")
        
        # TODO: LLM API 통합
        # 현재는 기본 템플릿 사용
        models = self._generate_default_models(question, available, depth)
        
        # 변수 정책 필터링
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
        
        logger.info(f"{'  ' * depth}    생성된 모형: {len(filtered_models)}개")
        
        return filtered_models
    
    def _generate_default_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        depth: int
    ) -> List[FermiModel]:
        """
        기본 템플릿 모형 생성
        
        v7.5.0 변경:
        - 비즈니스 지표 템플릿 제거됨
        - LLM 기반 일반 분해만 수행 (External mode)
        - Native mode는 Cursor에게 위임
        
        Args:
            question: 질문
            available: 가용 변수
            depth: 깊이
        
        Returns:
            FermiModel 리스트
        """
        # v7.5.0: 비즈니스 지표 템플릿 제거
        # 비즈니스 지표(LTV, CAC 등)는 Quantifier가 처리
        # Tier 3는 일반적 Fermi 분해만 담당
        
        # 2. LLM 모형 생성 (External mode만)
        if self.llm_mode == 'external' and self.llm_client:
            logger.info(f"{'  ' * depth}    템플릿 없음 → External LLM 모형 생성")
            llm_models = self._generate_llm_models(question, available, depth)
            if llm_models:
                return llm_models
        elif self.llm_mode == 'native':
            logger.info(f"{'  ' * depth}    Native Mode → Cursor LLM에게 Fermi 분해 요청")
            logger.info(f"{'  ' * depth}    ℹ️  비즈니스 지표(LTV, CAC 등)는 Quantifier가 처리")
            logger.info(f"{'  ' * depth}    ℹ️  Tier 3는 일반 Fermi 분해만 담당")
            return []  # Native mode에서는 Cursor가 직접 Fermi 분해 수행
        
        # 3. Fallback: 기본 모형
        logger.warning(f"{'  ' * depth}    Fallback: 기본 모형")
        
        model = FermiModel(
            model_id="MODEL_DEFAULT",
            name="기본 모형",
            formula="result = value",
            description="단순 추정 (Tier 2 활용)",
            variables={
                "value": FermiVariable(
                    name="value",
                    available=False,
                    need_estimate=True
                )
            },
            total_variables=1,
            unknown_count=1
        )
        
        return [model]
    
    def _match_business_metric_template(
        self,
        question: str
    ) -> List[FermiModel]:
        """
        비즈니스 지표 템플릿 매칭 - DISABLED (v7.5.0)
        
        v7.5.0 변경:
        - 비즈니스 지표 템플릿 제거됨
        - Quantifier가 LTV, CAC 등의 계산 담당
        - Estimator Tier 3는 일반적 Fermi 분해만 수행
        
        Args:
            question: 질문
        
        Returns:
            빈 리스트 (항상 매칭 없음)
        """
        # v7.5.0: 비즈니스 지표 템플릿 제거
        # Quantifier가 비즈니스 지표 계산 담당
        return []
    
    def _generate_llm_models(
        self,
        question: str,
        available: Dict[str, FermiVariable],
        depth: int
    ) -> List[FermiModel]:
        """
        LLM API로 모형 생성
        
        설계: fermi_model_search.yaml Line 1158-1181
        
        Args:
            question: 질문
            available: 가용 변수
            depth: 깊이
        
        Returns:
            LLM이 생성한 FermiModel 리스트
        """
        logger.info(f"{'  ' * depth}      [LLM] 모형 생성 요청")
        
        # 프롬프트 구성
        prompt = self._build_llm_prompt(question, available)
        
        try:
            # OpenAI API 호출
            response = self.llm_client.chat.completions.create(
                model=self.config.llm_model,
                temperature=self.config.llm_temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 Fermi Estimation 전문가입니다. 질문을 계산 가능한 수학적 모형으로 분해하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            llm_output = response.choices[0].message.content
            logger.info(f"{'  ' * depth}      [LLM] 응답 수신 ({len(llm_output)}자)")
            
            # 응답 파싱
            models = self._parse_llm_models(llm_output, depth)
            
            logger.info(f"{'  ' * depth}      [LLM] 파싱 완료: {len(models)}개 모형")
            
            return models
        
        except Exception as e:
            logger.error(f"{'  ' * depth}      ❌ LLM API 실패: {e}")
            return []
    
    def _build_llm_prompt(
        self,
        question: str,
        available: Dict[str, FermiVariable]
    ) -> str:
        """
        LLM 프롬프트 구성
        
        설계: fermi_model_search.yaml Line 1163-1181
        """
        # 가용 데이터 문자열
        if available:
            available_str = "\n".join([
                f"- {var.name}: {var.value} ({var.source}, confidence: {var.confidence:.0%})"
                for var in available.values()
            ])
        else:
            available_str = "(없음)"
        
        prompt = f"""질문: {question}

가용한 데이터:
{available_str}

임무:
1. 이 질문에 답하기 위한 계산 모형을 3-5개 제시하세요.
2. 각 모형은 다른 분해 방식을 사용하세요.
3. 가용한 데이터를 최대한 활용하세요.
4. Unknown 변수를 최소화하세요.
5. 간단할수록 좋습니다 (Occam's Razor, 최대 6개 변수 권장).

출력 형식 (YAML):
```yaml
models:
  - id: MODEL_001
    formula: "result = A × B × C"
    description: "설명"
    variables:
      - name: A
        description: "음식점 수"
        available: true
      - name: B
        description: "도입률"
        available: false
      - name: C
        description: "ARPU"
        available: false
  
  - id: MODEL_002
    formula: "result = A × B × C × D"
    description: "설명"
    variables:
      - name: A
        description: "음식점 수"
        available: true
      - name: B
        description: "디지털율"
        available: true
      - name: C
        description: "전환율"
        available: true
      - name: D
        description: "ARPU"
        available: false
```

주의: YAML 형식으로만 출력하세요."""
        
        return prompt
    
    def _parse_llm_models(
        self,
        llm_output: str,
        depth: int
    ) -> List[FermiModel]:
        """
        LLM 응답 파싱 (YAML)
        
        Args:
            llm_output: LLM 응답
            depth: 깊이
        
        Returns:
            FermiModel 리스트
        """
        try:
            # YAML 블록 추출 (```yaml ... ```)
            yaml_match = re.search(r'```yaml\n(.*?)\n```', llm_output, re.DOTALL)
            
            if not yaml_match:
                # YAML 블록 없으면 전체 파싱 시도
                yaml_str = llm_output
            else:
                yaml_str = yaml_match.group(1)
            
            # YAML 파싱
            data = yaml.safe_load(yaml_str)
            
            if not data or 'models' not in data:
                logger.warning(f"{'  ' * depth}        ⚠️  YAML 파싱 실패 (models 키 없음)")
                return []
            
            # FermiModel 변환
            models = []
            for model_data in data['models']:
                # 변수 파싱
                variables = {}
                for var_data in model_data.get('variables', []):
                    var_name = var_data.get('name', 'unknown')
                    var_available = var_data.get('available', False)
                    
                    variables[var_name] = FermiVariable(
                        name=var_name,
                        available=var_available,
                        need_estimate=not var_available,
                        source="llm_generated" if var_available else ""
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
            
            return models
        
        except Exception as e:
            logger.error(f"{'  ' * depth}        ❌ LLM 응답 파싱 실패: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 3: 실행 가능성 체크 (재귀 추정)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase3_check_feasibility(
        self,
        models: List[FermiModel],
        context: Context,
        current_depth: int
    ) -> List[RankedModel]:
        """
        Phase 3: 실행 가능성 체크 + 재귀 추정
        
        각 모형의 Unknown 변수를 재귀 호출로 채우기
        
        Args:
            models: 후보 모형들
            context: 맥락
            current_depth: 현재 깊이
        
        Returns:
            점수 순 RankedModel 리스트
        """
        logger.info(f"{'  ' * current_depth}  [Phase 3] 실행 가능성 체크")
        
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
        변수 추정 (재귀)
        
        1. Tier 2 먼저 시도 (빠름, 재귀 피함)
        2. Tier 2 실패 → Tier 3 재귀 호출
        
        Args:
            var_name: 변수 이름
            context: 맥락
            depth: 깊이
        
        Returns:
            EstimationResult 또는 None
        """
        # Context를 질문에 명시적으로 포함 (v7.5.0)
        question = self._build_contextualized_question(var_name, context)
        
        logger.info(f"{'  ' * depth}      [Recursive] {question}")
        
        # 1. Tier 2 먼저 시도 (재귀 최소화)
        tier2_result = self.tier2.estimate(question, context)
        
        if tier2_result and tier2_result.confidence >= 0.80:  # v7.5.0: 0.7→0.8 강화
            logger.info(f"{'  ' * depth}        ✅ Tier 2 성공 (재귀 불필요)")
            return tier2_result
        
        # 2. Tier 2 실패 → Tier 3 재귀
        logger.info(f"{'  ' * depth}        🔄 Tier 2 실패 → Fermi 재귀")
        
        # 부모 데이터 준비 (v7.5.0+)
        parent_data_to_pass = {}
        # TODO: 현재 모형의 available 변수를 부모 데이터로 전달
        
        # ⭐ 재귀 호출 (부모 데이터 상속)
        return self.estimate(
            question=question,
            context=context,
            available_data=None,
            depth=depth,
            parent_data=parent_data_to_pass  # v7.5.0: 데이터 상속
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 4: 모형 실행 (Backtracking)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _phase4_execute(
        self,
        ranked_model: RankedModel,
        depth: int,
        context: Context
    ) -> Optional[EstimationResult]:
        """
        Phase 4: 모형 실행 (Backtracking)
        
        재귀로 채운 변수들을 backtracking으로 재조립
        
        Args:
            ranked_model: 선택된 모형
            depth: 깊이
            context: 맥락
        
        Returns:
            EstimationResult (decomposition 포함)
        """
        logger.info(f"{'  ' * depth}  [Phase 4] 모형 실행")
        
        model = ranked_model.model
        
        # Step 1: 변수 바인딩 확인
        bindings = {}
        for name, var in model.variables.items():
            if var.available and var.value is not None:
                bindings[name] = var.value
            else:
                logger.warning(f"{'  ' * depth}    ⚠️  변수 '{name}' 값 없음")
        
        if not bindings:
            logger.warning(f"{'  ' * depth}    ❌ 바인딩할 변수 없음")
            return None
        
        logger.info(f"{'  ' * depth}    변수 바인딩: {list(bindings.keys())}")
        
        # Step 2: 계산 실행
        # TODO: 수식 파싱 및 안전한 실행
        # 현재: 간단한 곱셈 가정
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
            decomposition_reasoning=model.selection_reason
        )
        
        # Step 5: ComponentEstimation 생성
        components = [
            ComponentEstimation(
                component_name=name,
                component_value=var.value or 0.0,
                estimation_method=var.source,
                reasoning=f"{var.source}에서 획득",
                confidence=var.confidence,
                sources=[var.source]
            )
            for name, var in model.variables.items()
            if var.available
        ]
        
        # Step 6: Estimation Trace 생성
        trace = [
            f"Step 1: 문제 정의 - {model.description}",
            f"Step 2: 모형 선택 - {model.formula}",
            f"Step 3: 분해 - {model.total_variables}개 변수",
            f"Step 4: 변수 추정 - {model.available_count}개 확보",
            f"Step 5: 재귀 깊이 - depth {depth}",
            f"Step 6: 계산 - {model.formula}",
            f"Step 7: Confidence - {combined_confidence:.2f}",
            f"Step 8: 결과 - {result_value}"
        ]
        
        # Step 7: EstimationResult 생성
        result = EstimationResult(
            value=result_value,
            confidence=combined_confidence,
            tier=3,
            sources=[var.source for var in model.variables.values() if var.available],
            reasoning_detail={
                'method': 'fermi_decomposition',
                'model_id': model.model_id,
                'formula': model.formula,
                'depth': depth,
                'selection_reason': model.selection_reason,
                'why_this_method': f'Tier 1/2 실패, 재귀 분해 필요 (depth {depth})'
            },
            component_estimations=components,
            estimation_trace=trace,
            decomposition=decomposition
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
            
            # 안전한 계산 (허용 문자만)
            allowed_chars = set('0123456789.+-*/() ')
            if not all(c in allowed_chars for c in expr):
                logger.warning(f"    ⚠️  수식에 허용되지 않는 문자: {formula}")
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


