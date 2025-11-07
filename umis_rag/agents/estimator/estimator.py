"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가
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
    Estimator (Fermi) RAG Agent
    
    역할:
    -----
    - 값 추정 및 지능적 판단
    - 11개 Source 통합 (Physical, Soft, Value)
    - 학습하는 시스템 (사용할수록 6-16배 빨라짐)
    
    3-Tier 아키텍처:
    ---------------
    - Tier 1: Built-in + 학습 규칙 (<0.5초)
    - Tier 2: 11개 Source 수집 + 종합 판단 (3-8초)
    - Tier 3: Fermi Decomposition (미래)
    
    협업:
    -----
    - Observer: 비율 추정
    - Explorer: 시장 크기 감 잡기  
    - Quantifier: 데이터 부족 시
    - Validator: 추정치 검증
    
    Usage:
        >>> from umis_rag.agents.estimator import EstimatorRAG
        >>> estimator = EstimatorRAG()
        >>> result = estimator.estimate(
        ...     "B2B SaaS Churn Rate는?",
        ...     domain="B2B_SaaS"
        ... )
        >>> print(f"{result.value} (Tier {result.tier})")
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
        
        # Tier 3: Fermi Decomposition (미래)
        self.tier3 = None
        
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
        통합 추정 메서드
        
        자동으로 Tier 1 → 2 → 3 시도
        
        Args:
            question: 질문 (예: "B2B SaaS Churn Rate는?")
            context: Context 객체 (선택)
            domain: 도메인 (예: "B2B_SaaS", "Food_Service")
            region: 지역 (예: "한국", "서울")
            time_period: 시점 (예: "2024")
            project_data: 프로젝트 확정 데이터
        
        Returns:
            EstimationResult or None
        
        Example:
            >>> estimator = EstimatorRAG()
            >>> result = estimator.estimate(
            ...     "B2B SaaS Churn Rate는?",
            ...     domain="B2B_SaaS"
            ... )
            >>> print(f"값: {result.value}")
            >>> print(f"Tier: {result.tier} (1=빠름, 2=정확)")
            >>> print(f"신뢰도: {result.confidence:.0%}")
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
        # Tier 3: Fermi Decomposition (미래)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TODO: Fermi Model Search 통합
        
        logger.warning("  ❌ 추정 실패")
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

