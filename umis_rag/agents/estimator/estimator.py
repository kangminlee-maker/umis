"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가 (v7.6.2 재설계)

주요 변경 (v7.6.0 → v7.6.2):
- v7.6.0: 5-Phase 재설계, Validator 우선 검색, Built-in 제거
- v7.6.1: 단위 자동 변환, Relevance 검증
- v7.6.2: Boundary 검증, 하드코딩 제거, Web Search 추가
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
    Estimator (Fermi) RAG Agent (v7.6.0 재설계)
    
    역할:
    -----
    - 값 추정 전문 (Single Source of Truth for Estimation)
    - 데이터 없을 때 창의적 추정
    - Validator 우선 검색 → 없으면 추정
    - 학습하는 시스템 (사용할수록 빨라짐)
    
    ⚠️  역할 명확화:
    - Estimator: 값 추정만 담당 (예: "B2B SaaS ARPU는?" → 80,000원)
    - Quantifier: 계산 공식 소유 (예: LTV = ARPU / Churn)
    - Validator: 확정 데이터 검색 (추정 전 필수!)
    
    5-Phase 아키텍처 (v7.7.0):
    ---------------------------------
    - Phase 0: Literal (프로젝트 데이터, <0.1초, confidence 1.0)
    - Phase 1: Direct RAG (Tier 1 학습 규칙, <0.5초, 0.95+)
    - Phase 2: Validator (확정 데이터 검색, <1초, 1.0) ⭐ 85% 처리!
    - Phase 3: Guestimation (Tier 2 추정, 3-8초, 0.80+)
    - Phase 4: Fermi Decomposition (Tier 3 분해, 10-30초) 💎
        └─ Step 1-4: 스캔 → 모형 생성 → 체크 → 실행
    
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
        logger.info("  ✅ Tier 1 (학습)")
        
        # Validator: 확정 데이터 검색 (v7.6.0 추가)
        self.validator = None  # Lazy 초기화
        
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
        통합 추정 메서드 (v7.6.0 재설계)
        
        5-Phase 프로세스 (v7.7.0):
        - Phase 0: Literal (프로젝트 데이터, 즉시, confidence 1.0)
        - Phase 1: Direct RAG (Tier 1 학습, <0.5초, 0.95+)
        - Phase 2: Validator (확정 데이터, <1초, 1.0) ⭐ 85% 처리!
        - Phase 3: Guestimation (Tier 2 추정, 3-8초, 0.80+)
        - Phase 4: Fermi Decomposition (Tier 3 분해, 10-30초) 💎
            └─ Step 1: 초기 스캔
            └─ Step 2: 모형 생성
            └─ Step 3: 실행 가능성 체크
            └─ Step 4: 모형 실행 (Backtracking)
        
        ⚠️  v7.7.0 용어 변경:
        - 3-Tier → 5-Phase (Estimator 전체)
        - Fermi 내부: Step 1-4 (명확성 향상)
        
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
        # Phase 0: Project Data (v7.6.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if project_data:
            result = self._check_project_data(question, project_data, context)
            if result:
                logger.info(f"  ✅ Phase 0 (Project Data): {result.value}")
                return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 1: Tier 1 (학습 규칙만, v7.6.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result = self.tier1.estimate(question, context)
        
        if result:
            logger.info(f"  ⚡ Phase 1 (Tier 1) 성공: {result.value} ({result.execution_time:.2f}초)")
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2: Validator 검색 (v7.6.0) ⭐
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 추정하기 전 마지막 확인!
        # 확정 데이터가 정말 없는지 Validator에게 확인
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result = self._search_validator(question, context)
        if result:
            logger.info(f"  ✅ Phase 2 (Validator) 발견: {result.value} ({result.execution_time:.2f}초)")
            return result
        
        logger.info("  → Validator에도 없음 → 추정 시작")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 3: Tier 2 (추정 시작, v7.6.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        self._ensure_tier2_initialized()
        result = self.tier2.estimate(question, context)
        
        if result:
            logger.info(f"  🧠 Tier 2 완료: {result.value} ({result.execution_time:.2f}초)")
            
            if result.should_learn:
                logger.info(f"  📚 학습됨 (다음엔 Tier 1로 빠름!)")
            
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 4: Tier 3 (Fermi Decomposition, v7.6.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 💎 가장 가치있는 작업!
        # 없는 숫자를 만드는 창조적 추정
        # 시간(10-30초), 비용($0.01-0.05) 투자 정당화됨
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.tier3 is None:
            from .tier3 import Tier3FermiPath
            self.tier3 = Tier3FermiPath()
            logger.info("  ✅ Tier 3 (Fermi Decomposition) 로드")
        
        logger.info("  💎 Phase 4 (Tier 3) 시도: 가치있는 작업!")
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
    
    def _check_project_data(
        self,
        question: str,
        project_data: Dict,
        context: Context
    ) -> Optional[EstimationResult]:
        """
        Phase 0: 프로젝트 확정 데이터 확인 (v7.6.0)
        
        프로젝트에서 명시적으로 제공한 데이터 우선 확인
        
        Args:
            question: 질문
            project_data: 프로젝트 데이터
            context: 맥락
        
        Returns:
            EstimationResult or None
        
        Example:
            >>> project_data = {
            ...     "total_users": 10000,
            ...     "churn_rate": 0.05
            ... }
            >>> result = estimator._check_project_data(
            ...     "이탈률은?", project_data, context
            ... )
            >>> # → 0.05 (즉시)
        """
        import time
        start_time = time.time()
        
        # 질문에서 키워드 추출
        question_lower = question.lower()
        
        # 키워드 매핑
        keyword_map = {
            'churn': ['churn_rate', 'monthly_churn', 'annual_churn'],
            '이탈': ['churn_rate', 'monthly_churn'],
            '해지': ['churn_rate'],
            'arpu': ['arpu', 'average_revenue'],
            '평균매출': ['arpu', 'average_revenue'],
            '매출': ['arpu', 'revenue', 'average_revenue'],
            'user': ['total_users', 'active_users'],
            '사용자': ['total_users', 'active_users', 'users'],
            '고객': ['total_users', 'customers'],
            'ltv': ['ltv', 'lifetime_value'],
            'cac': ['cac', 'customer_acquisition_cost'],
            '획득비용': ['cac']
        }
        
        # 매칭 시도
        for keyword, possible_keys in keyword_map.items():
            if keyword in question_lower:
                for key in possible_keys:
                    if key in project_data:
                        value = project_data[key]
                        execution_time = time.time() - start_time
                        
                        return EstimationResult(
                            question=question,
                            value=value,
                            confidence=1.0,
                            tier=0,
                            context=context,
                            reasoning=f"프로젝트 확정 데이터: {key}",
                            reasoning_detail={
                                'method': 'project_data',
                                'key': key,
                                'why_this_method': '프로젝트에서 명시적으로 제공한 확정 값'
                            },
                            execution_time=execution_time
                        )
        
        return None
    
    def _search_validator(
        self,
        question: str,
        context: Context
    ) -> Optional[EstimationResult]:
        """
        Phase 2: Validator 확정 데이터 검색 (v7.6.0)
        
        추정하기 전 확정 데이터 존재 여부 확인
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult(tier=1.5) or None
        """
        import time
        start_time = time.time()
        
        # Validator Lazy 초기화
        if self.validator is None:
            from umis_rag.agents.validator import get_validator_rag
            self.validator = get_validator_rag()
            logger.info("  ✅ Validator 연결")
        
        # Validator 검색
        validator_result = self.validator.search_definite_data(question, context)
        
        if validator_result:
            execution_time = time.time() - start_time
            
            return EstimationResult(
                question=question,
                value=validator_result['value'],
                unit=validator_result.get('unit', ''),
                confidence=1.0,
                tier=1.5,
                context=context,
                reasoning=f"확정 데이터 (Validator): {validator_result['source']}",
                reasoning_detail={
                    'method': 'validator_search',
                    'source': validator_result['source'],
                    'definition': validator_result.get('definition', ''),
                    'last_updated': validator_result.get('last_updated', ''),
                    'reliability': validator_result.get('reliability', 'high'),
                    'why_this_method': 'Validator가 공식 통계/벤치마크에서 확정 데이터 발견'
                },
                logic_steps=[
                    f"1. Tier 1 학습 규칙 없음",
                    f"2. Validator 검색 시작",
                    f"3. 출처: {validator_result['source']}",
                    f"4. 값: {validator_result['value']}",
                    f"5. 신뢰도: 1.0 (확정 데이터)"
                ],
                execution_time=execution_time
            )
        
        return None
    
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


