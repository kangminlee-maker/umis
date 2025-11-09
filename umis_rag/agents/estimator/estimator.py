"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가 (v7.5.0)
"""

from typing import Optional, Dict, Any
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

from .tier1 import Tier1FastPath
from .tier2 import Tier2JudgmentPath
from .learning_writer import LearningWriter, UserContribution
from .models import Context, EstimationResult


class EstimatorRAG:
    """
    Estimator (Fermi) RAG Agent (v7.5.0 완성)
    
    역할:
    -----
    - 값 추정 전문 (Single Source of Truth for Estimation)
    - 데이터 없을 때 창의적 추정
    - 11개 Source 통합 (Physical, Soft, Value)
    - 학습하는 시스템 (사용할수록 6-16배 빨라짐)
    
    ⚠️  역할 명확화 (v7.5.0):
    - Estimator: 값 추정만 담당 (예: "B2B SaaS ARPU는?" → 80,000원)
    - Quantifier: 계산 공식 소유 (예: LTV = ARPU / Churn)
    - 비즈니스 지표(LTV, CAC 등) 계산은 Quantifier가 담당!
    
    3-Tier 아키텍처 (v7.5.0):
    ---------------------------------
    - Tier 1: Built-in + 학습 규칙 (<0.5초, 임계값 0.95+)
    - Tier 2: 11개 Source 수집 + 종합 판단 (3-8초, confidence 0.80+)
    - Tier 3: 일반 Fermi Decomposition (10-30초) ⭐
      * 물리적/수학적 분해 (예: 여객기 부피, 음식점 수)
      * 재귀 추정 (max depth 4)
      * 데이터 상속 및 Context 전달
      * 순환 감지
      * LLM 모드 (Native/External)
      * 비즈니스 지표 템플릿 제거됨 (→ Quantifier)
    
    협업 (모든 Agent):
    ------------------
    - Quantifier: 필요한 값 요청 (예: "ARPU는?", "Churn은?")
    - Observer: 비율 추정 (가치사슬 마진, 시장 집중도)
    - Explorer: 시장 크기 감 잡기 (Order of Magnitude)
    - Validator: 추정치 교차 검증
    - Guardian: 프로젝트 리소스 추정
    
    Usage:
        >>> from umis_rag.agents.estimator import EstimatorRAG
        >>> estimator = EstimatorRAG()
        
        >>> # Tier 1/2 (대부분 - 증거 기반)
        >>> result = estimator.estimate("B2B SaaS Churn Rate는?", domain="B2B_SaaS")
        >>> print(f"{result.value} (Tier {result.tier})")
        
        >>> # Tier 3 (일반 Fermi 분해)
        >>> result = estimator.estimate("서울 음식점 수는?")
        >>> # → Fermi 분해: 인구 × 음식점 밀도
        
        >>> # 비즈니스 지표는 Quantifier가 처리 (v7.5.0)
        >>> from umis_rag.agents.quantifier import get_quantifier_rag
        >>> quantifier = get_quantifier_rag()
        >>> ltv = quantifier.calculate_ltv(...)  # Quantifier가 LTV 계산
    """
    
    def __init__(self):
        """Estimator RAG Agent 초기화"""
        logger.info("[Estimator] Fermi Agent 초기화")
        
        # Tier 1: Fast Path
        self.tier1 = Tier1FastPath()
        logger.info("  ✅ Tier 1 (Built-in + 학습)")
        
        # Tier 2: Judgment Path (Lazy 초기화)
        self.tier2 = None
        self.learning_writer = None
        
        # Tier 3: Fermi Decomposition (v7.5.0 완성)
        self.tier3 = None  # Lazy 초기화
        
        # RAG Collections (Lazy)
        self.canonical_store = None
        self.projected_store = None
        
        logger.info("  ✅ Estimator Agent 준비 완료")
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None,
        project_data: Optional[Dict] = None
    ) -> Optional[EstimationResult]:
        """
        통합 추정 메서드 (v7.5.0)
        
        자동으로 Tier 1 → 2 → 3 시도
        - Tier 1: 학습된 규칙 (<0.5초, 유사도 0.95+)
        - Tier 2: 11개 Source 판단 (3-8초, confidence 0.80+)
        - Tier 3: Fermi 분해 (10-30초, 일반적 분해만)
        
        ⚠️  v7.5.0 변경:
        - 비즈니스 지표(LTV, CAC 등) 템플릿 제거
        - Quantifier가 비즈니스 지표 계산 담당
        - Estimator는 순수 값 추정만 수행
        
        Args:
            question: 질문 (구체적일수록 좋음!)
                예: "B2B SaaS 한국 시장 ARPU는?" (✅)
                예: "ARPU는?" (❌ 너무 애매)
            context: Context 객체 (선택)
            domain: 도메인 (예: "B2B_SaaS", "Food_Service")
            region: 지역 (예: "한국", "서울")
            time_period: 시점 (예: "2024")
            project_data: 프로젝트 확정 데이터
        
        Returns:
            EstimationResult or None
        
        Example:
            >>> estimator = EstimatorRAG()
            
            >>> # Tier 1/2 (증거 기반 추정)
            >>> result = estimator.estimate(
            ...     "B2B SaaS Churn Rate는?",
            ...     domain="B2B_SaaS",
            ...     region="한국"
            ... )
            >>> print(f"값: {result.value}%, Tier: {result.tier}")
            
            >>> # Tier 3 (Fermi 분해)
            >>> result = estimator.estimate("서울 음식점 수는?")
            >>> # → Fermi: 인구 × 음식점 밀도
            >>> # → 재귀 추정으로 하위 변수 채우기
            
            >>> # Context 명시
            >>> from umis_rag.agents.estimator.models import Context
            >>> ctx = Context(domain="B2B_SaaS", region="한국")
            >>> result = estimator.estimate("ARPU는?", context=ctx)
        """
        # Context 생성
        if context is None:
            context = Context(
                domain=domain or "General",
                region=region,
                time_period=time_period or "2024",
                project_data=project_data or {}
            )
        
        logger.info(f"[Estimator] 추정: {question}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Tier 1: Fast Path (Built-in + 학습)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result = self.tier1.estimate(question, context)
        
        if result:
            logger.info(f"  ⚡ Tier 1 성공: {result.value} ({result.execution_time:.2f}초)")
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Tier 2: Judgment Path (11개 Source)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        self._ensure_tier2_initialized()
        result = self.tier2.estimate(question, context)
        
        if result:
            logger.info(f"  🧠 Tier 2 완료: {result.value} ({result.execution_time:.2f}초)")
            
            if result.should_learn:
                logger.info(f"  📚 학습됨 (다음엔 Tier 1로 빠름!)")
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Tier 3: Fermi Decomposition (v7.5.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 일반적 Fermi 분해 (물리적/수학적)
        # 재귀 추정 (max depth 4)
        # 데이터 상속 및 Context 전달
        # LLM 모드 (Native/External)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.tier3 is None:
            from .tier3 import Tier3FermiPath
            self.tier3 = Tier3FermiPath()
            logger.info("  ✅ Tier 3 (Fermi Decomposition) 로드")
        
        logger.info("  🔄 Tier 3 시도 (일반 Fermi 분해)")
        result = self.tier3.estimate(question, context, project_data, depth=0)
        
        if result:
            logger.info(f"  🧩 Tier 3 완료: {result.value} ({result.execution_time:.2f}초)")
            if result.decomposition:
                logger.info(f"     모형: {result.decomposition.formula}")
                logger.info(f"     Depth: {result.decomposition.depth}")
            return result
        
        logger.warning("  ❌ 모든 Tier 실패")
        return None
    
    def contribute(
        self,
        question: str,
        value: float,
        unit: str = "",
        context: Optional[Context] = None,
        contribution_type: str = "definite_fact"
    ) -> str:
        """
        사용자 기여 (확정 사실, 업계 상식 등)
        
        Args:
            question: 질문
            value: 값
            unit: 단위
            context: 맥락
            contribution_type: 기여 타입
                - "definite_fact": 확정 사실 (confidence=1.0)
                - "domain_knowledge": 업계 상식 (confidence=0.90)
                - "personal_experience": 개인 경험 (confidence=0.40)
        
        Returns:
            rule_id: 저장된 규칙 ID
        
        Example:
            >>> estimator = EstimatorRAG()
            >>> rule_id = estimator.contribute(
            ...     question="우리 회사 직원 수는?",
            ...     value=150,
            ...     unit="명"
            ... )
            >>> # 즉시 사용 가능!
            >>> result = estimator.estimate("우리 회사 직원 수는?")
            >>> # → Tier 1에서 즉시 리턴 (<0.5초)
        """
        self._ensure_tier2_initialized()
        
        contribution = UserContribution(self.learning_writer)
        
        if contribution_type == "definite_fact":
            return contribution.add_definite_fact(
                question=question,
                value=value,
                unit=unit,
                context=context
            )
        elif contribution_type == "domain_knowledge":
            return contribution.add_domain_knowledge(
                question=question,
                value=value,
                context=context or Context()
            )
        elif contribution_type == "personal_experience":
            return contribution.add_personal_experience(
                question=question,
                value=value,
                context_description=str(context) if context else ""
            )
        else:
            raise ValueError(f"Unknown contribution_type: {contribution_type}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        학습 통계 조회
        
        Returns:
            {
                'total_rules': int,
                'by_domain': dict,
                'avg_confidence': float
            }
        """
        if self.learning_writer:
            return self.learning_writer.get_learning_stats()
        return {
            'total_rules': 0,
            'by_domain': {},
            'avg_confidence': 0.0
        }
    
    def _ensure_tier2_initialized(self):
        """Tier 2 Lazy 초기화"""
        if self.tier2 is not None:
            return
        
        # Learning Writer 초기화
        if self.learning_writer is None:
            # Canonical Collection 로드 (Lazy)
            try:
                embeddings = OpenAIEmbeddings(
                    model=settings.embedding_model,
                    openai_api_key=settings.openai_api_key
                )
                
                canonical_store = Chroma(
                    collection_name="canonical_index",
                    embedding_function=embeddings,
                    persist_directory=str(settings.chroma_persist_dir)
                )
                
                self.learning_writer = LearningWriter(
                    canonical_collection=canonical_store._collection
                )
                logger.info("  ✅ Learning Writer 초기화")
                
            except Exception as e:
                logger.warning(f"  ⚠️  Learning Writer 초기화 실패: {e}")
                self.learning_writer = None
        
        # Tier 2 초기화
        self.tier2 = Tier2JudgmentPath(
            learning_writer=self.learning_writer
        )
        logger.info("  ✅ Tier 2 초기화")


# ================================================================
# 싱글톤 인스턴스
# ================================================================

_estimator_rag_instance = None


def get_estimator_rag() -> EstimatorRAG:
    """
    Estimator RAG 싱글톤 인스턴스 반환
    
    Returns:
        EstimatorRAG 인스턴스
    
    Example:
        >>> estimator = get_estimator_rag()
        >>> result = estimator.estimate("Churn Rate는?")
    """
    global _estimator_rag_instance
    if _estimator_rag_instance is None:
        _estimator_rag_instance = EstimatorRAG()
    return _estimator_rag_instance

