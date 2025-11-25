"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가 (v7.11.0 Fusion Architecture)

v7.11.0 주요 변경:
- 재귀 완전 제거 (Recursion FORBIDDEN)
- 증거/생성 레이어 분리 (Evidence vs Generative Prior)
- 예산 기반 탐색 (Budget-based Exploration)
- Fermi는 "설명 엔진"으로 재정의
- Fusion Layer로 결과 통합

Architecture:
- Stage 1: Evidence Collection (Phase 0-2, Guardrails)
- Stage 2: Generative Prior (Phase 3 재설계)
- Stage 3: Structural Explanation (Phase 4 재설계, 재귀 금지)
- Stage 4: Fusion & Validation (Sensor Fusion)
"""

from typing import Optional, Dict, Any
from pathlib import Path
import time

import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

from .common.budget import Budget, create_standard_budget, create_fast_budget, create_thorough_budget
from .common.estimation_result import EstimationResult, Evidence
from .evidence_collector import EvidenceCollector
from .prior_estimator import PriorEstimator
from .fermi_estimator import FermiEstimator
from .fusion_layer import FusionLayer
from .models import Context


class EstimatorRAG:
    """
    Estimator (Fermi) RAG Agent (v7.11.0 Fusion Architecture)
    
    역할:
    -----
    - 값 추정 전문 (Single Source of Truth for Estimation)
    - 재귀 없는 Fermi 분해 (Recursion FORBIDDEN)
    - 증거 + 생성 + 구조 융합
    
    v7.11.0 아키텍처:
    -----------------
    - Stage 1: Evidence Collection
      → Phase 0-2 (Literal, Direct RAG, Validator Search)
      → Guardrail Engine (Hard/Soft Constraints)
      → 확정 값 있으면 즉시 반환
    
    - Stage 2: Generative Prior
      → LLM 직접 값 요청 (단일 호출)
      → Certainty: high/medium/low
      → 재귀 금지
    
    - Stage 3: Structural Explanation (Fermi)
      → 2-4개 변수로 분해
      → 각 변수 = PriorEstimator로 직접 추정
      → max_depth = 2 (강제)
      → 재귀 금지
    
    - Stage 4: Fusion
      → Evidence + Prior + Fermi 융합
      → 가중 평균 + Hard Bounds 클리핑
      → 최종 결과 반환
    
    사용법:
    -------
        >>> from umis_rag.agents.estimator import EstimatorRAG
        >>> estimator = EstimatorRAG()
        
        >>> # 기본 추정
        >>> result = estimator.estimate("B2B SaaS Churn Rate는?")
        >>> print(f"{result.value} (source={result.source})")
        
        >>> # 예산 제한
        >>> from umis_rag.agents.estimator.common import create_fast_budget
        >>> budget = create_fast_budget()
        >>> result = estimator.estimate("서울 음식점 수는?", budget=budget)
    """
    
    def __init__(self):
        """Estimator RAG Agent 초기화 (v7.11.0)"""
        logger.info("[Estimator] v7.11.0 Fusion Architecture 초기화")
        
        logger.info(f"  📌 LLM Mode: {self.llm_mode}")
        
        # Stage 1: Evidence Collector
        self.evidence_collector = EvidenceCollector(llm_mode=self.llm_mode)
        logger.info("  ✅ Stage 1: Evidence Collector")
        
        # Stage 2: Prior Estimator
        self.prior_estimator = PriorEstimator(llm_mode=self.llm_mode)
        logger.info("  ✅ Stage 2: Prior Estimator")
        
        # Stage 3: Fermi Estimator
        self.fermi_estimator = FermiEstimator(
            llm_mode=self.llm_mode,
            prior_estimator=self.prior_estimator
        )
        logger.info("  ✅ Stage 3: Fermi Estimator (재귀 금지)")
        
        # Stage 4: Fusion Layer
        self.fusion_layer = FusionLayer()
        logger.info("  ✅ Stage 4: Fusion Layer")
        
        logger.info("  ⚠️  v7.11.0: 재귀 완전 제거 (Recursion FORBIDDEN)")
        logger.info("  ✅ Estimator Agent 준비 완료")
    
    @property
    def llm_mode(self) -> str:
        """
        LLM 모드 동적 읽기
        
        Returns:
            현재 설정된 LLM 모드
        """
        return settings.llm_mode
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 인터페이스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None,
        budget: Optional[Budget] = None,
        use_fermi: bool = True
    ) -> Optional[EstimationResult]:
        """
        통합 추정 (v7.11.0 Fusion Architecture)
        
        Args:
            question: 질문
            context: Context 객체 (선택)
            domain: 도메인 (예: "B2B_SaaS")
            region: 지역 (예: "한국")
            time_period: 시점 (예: "2024")
            budget: 예산 (None이면 표준 예산 사용)
            use_fermi: Fermi 분해 사용 여부
        
        Returns:
            EstimationResult or None
        
        Example:
            >>> estimator = EstimatorRAG()
            
            >>> # 기본 추정
            >>> result = estimator.estimate("B2B SaaS Churn Rate는?")
            >>> print(f"{result.value} (source={result.source})")
            
            >>> # 빠른 추정 (예산 제한)
            >>> budget = create_fast_budget()
            >>> result = estimator.estimate("서울 음식점 수는?", budget=budget)
        """
        logger.info("=" * 80)
        logger.info(f"[Estimator v7.11.0] 추정 시작: {question}")
        logger.info("=" * 80)
        start_time = time.time()
        
        # Context 생성
        if context is None:
            context = Context(
                domain=domain or "General",
                region=region,
                time_period=time_period or "2024"
            )
        
        # Budget 생성
        if budget is None:
            budget = create_standard_budget()
            logger.info(f"  예산: 표준 (LLM={budget.max_llm_calls}, Vars={budget.max_variables}, Time={budget.max_runtime_seconds}s)")
        else:
            logger.info(f"  예산: 사용자 정의 (LLM={budget.max_llm_calls}, Vars={budget.max_variables})")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 1: Evidence Collection
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 1] Evidence Collection")
        logger.info("-" * 80)
        
        definite_result, evidence = self.evidence_collector.collect(
            question=question,
            context=context,
            collect_guardrails=True
        )
        
        # 확정 값이 있으면 즉시 반환
        if definite_result:
            elapsed = time.time() - start_time
            definite_result.cost['time'] = elapsed
            
            logger.info("\n" + "=" * 80)
            logger.info(f"⚡ 확정 값 발견 → 추정 불필요")
            logger.info(f"결과: {definite_result.value:,.0f} (source={definite_result.source}, {elapsed:.2f}초)")
            logger.info("=" * 80)
            
            return definite_result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 2: Generative Prior
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 2] Generative Prior")
        logger.info("-" * 80)
        
        prior_result = None
        
        if budget.can_call_llm(1):
            prior_result = self.prior_estimator.estimate(
                question=question,
                evidence=evidence,
                budget=budget,
                context=context
            )
            
            if prior_result:
                logger.info(f"  ✅ Prior: {prior_result.value:,.0f} (certainty={prior_result.certainty})")
            else:
                logger.warning("  ❌ Prior 실패")
        else:
            logger.warning("  예산 부족 (Prior 스킵)")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 3: Structural Explanation (Fermi)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        fermi_result = None
        
        if use_fermi and budget.can_call_llm(1) and not budget.is_exhausted():
            logger.info("\n[Stage 3] Structural Explanation (Fermi)")
            logger.info("-" * 80)
            
            fermi_result = self.fermi_estimator.estimate(
                question=question,
                evidence=evidence,
                budget=budget,
                context=context,
                depth=0
            )
            
            if fermi_result:
                logger.info(f"  ✅ Fermi: {fermi_result.value:,.0f} (certainty={fermi_result.certainty})")
                if fermi_result.decomposition:
                    logger.info(f"  분해식: {fermi_result.decomposition.get('formula', 'N/A')}")
            else:
                logger.warning("  ❌ Fermi 실패 또는 스킵")
        else:
            if not use_fermi:
                logger.info("\n[Stage 3] Fermi 사용 안 함 (use_fermi=False)")
            else:
                logger.warning("\n[Stage 3] Fermi 스킵 (예산 부족 또는 소진)")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Stage 4: Fusion
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n[Stage 4] Fusion")
        logger.info("-" * 80)
        
        final_result = self.fusion_layer.synthesize(
            evidence=evidence,
            prior_result=prior_result,
            fermi_result=fermi_result
        )
        
        # 총 시간 업데이트
        elapsed = time.time() - start_time
        final_result.cost['time'] = elapsed
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 결과 출력
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info("\n" + "=" * 80)
        logger.info("✅ 추정 완료")
        logger.info(f"결과: {final_result.value:,.0f}")
        logger.info(f"Source: {final_result.source}")
        logger.info(f"Certainty: {final_result.certainty}")
        logger.info(f"비용: {final_result.get_cost_summary()}")
        logger.info(f"예산 상태: {budget.get_status_summary()}")
        
        if final_result.fusion_weights:
            logger.info(f"Fusion Weights: {final_result.fusion_weights}")
        
        logger.info("=" * 80)
        
        return final_result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 편의 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def estimate_fast(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        빠른 추정 (10초 이내)
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult
        """
        budget = create_fast_budget()
        return self.estimate(question, context=context, budget=budget, use_fermi=False)
    
    def estimate_thorough(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        정밀 추정 (최대 2분)
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult
        """
        budget = create_thorough_budget()
        return self.estimate(question, context=context, budget=budget, use_fermi=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Factory Function
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_estimator() -> EstimatorRAG:
    """
    Estimator Agent 싱글톤 인스턴스
    
    Returns:
        EstimatorRAG 인스턴스
    """
    return EstimatorRAG()
