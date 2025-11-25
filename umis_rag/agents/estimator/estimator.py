"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가 (v7.10.0 Hybrid Architecture)

주요 변경:
- v7.6.0: 5-Phase 재설계, Validator 우선 검색, Built-in 제거
- v7.6.1: 단위 자동 변환, Relevance 검증
- v7.6.2: Boundary 검증, 하드코딩 제거, Web Search 추가
- v7.10.0: Hybrid Architecture (Thread Pool 병렬화)
  - Stage 1: Phase 1-2 병렬 수집
  - Stage 2: Phase 3-4 병렬 추정
  - Stage 3: Synthesis (교차 검증 + 융합)
"""

from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

from .phase1_direct_rag import Phase1DirectRAG
from .phase3_guestimation import Phase3Guestimation
from .learning_writer import LearningWriter, UserContribution
from .models import Context, EstimationResult, GuardrailCollector, Guardrail, GuardrailType


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
    - Phase 1: Direct RAG (학습 규칙, <0.5초, 0.95+)
    - Phase 2: Validator (확정 데이터 검색, <1초, 1.0) ⭐ 85% 처리!
    - Phase 3: Guestimation (추정, 3-8초, 0.80+)
    - Phase 4: Fermi Decomposition (분해, 10-30초) 💎
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
        
        >>> # Phase 1-3 (대부분 - 증거 기반)
        >>> result = estimator.estimate("B2B SaaS Churn Rate는?", domain="B2B_SaaS")
        >>> print(f"{result.value} (Phase {result.phase})")
        
        >>> # Phase 4 (Fermi 분해)
        >>> result = estimator.estimate("서울 음식점 수는?")
        >>> # → Fermi 분해: 인구 × 음식점 밀도
        
        >>> # 비즈니스 지표는 Quantifier가 처리 (v7.5.0)
        >>> from umis_rag.agents.quantifier import get_quantifier_rag
        >>> quantifier = get_quantifier_rag()
        >>> ltv = quantifier.calculate_ltv(...)  # Quantifier가 LTV 계산
    """
    
    def __init__(self):
        """Estimator RAG Agent 초기화 (v7.9.0)"""
        logger.info("[Estimator] Fermi Agent 초기화")
        
        # v7.9.0: llm_mode를 Property로 변경 (동적 읽기)
        # self.llm_mode 제거 → @property로 대체
        logger.info(f"  📌 LLM Mode: {self.llm_mode}")
        
        # Phase 1: Direct RAG
        self.phase1 = Phase1DirectRAG()
        logger.info("  ✅ Phase 1 (Direct RAG)")
        
        # Validator: 확정 데이터 검색 (v7.6.0 추가, Phase 2)
        self.validator = None  # Lazy 초기화
        
        # Phase 2 Enhanced: 컨텍스트 기반 검색 (v7.9.0 추가)
        self.phase2_enhanced = None  # Lazy 초기화
        
        # Phase 3: Guestimation (Lazy 초기화)
        self.phase3 = None
        self.learning_writer = None
        
        # Phase 4: Fermi Decomposition (Lazy 초기화)
        self.phase4 = None
        
        # RAG Collections (Lazy)
        self.canonical_store = None
        self.projected_store = None
        
        logger.info("  ✅ Estimator Agent 준비 완료")
    
    @property
    def llm_mode(self) -> str:
        """
        LLM 모드 동적 읽기 (v7.9.0)
        
        Property 패턴으로 구현하여 settings 변경 시 즉시 반영
        
        Returns:
            현재 설정된 LLM 모드 (cursor, gpt-4o-mini, o1-mini 등)
        """
        return settings.llm_mode
    
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
        - Phase 1: Direct RAG (학습, <0.5초, 0.95+)
        - Phase 2: Validator (확정 데이터, <1초, 1.0) ⭐ 85% 처리!
        - Phase 3: Guestimation (추정, 3-8초, 0.80+)
        - Phase 4: Fermi Decomposition (분해, 10-30초) 💎
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
            
            >>> # Phase 1-3 (증거 기반 추정)
            >>> result = estimator.estimate(
            ...     "B2B SaaS Churn Rate는?",
            ...     domain="B2B_SaaS",
            ...     region="한국"
            ... )
            >>> print(f"값: {result.value}%, Phase: {result.phase}")
            
            >>> # Phase 4 (Fermi 분해)
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
        # Phase 1: Direct RAG (학습 규칙, v7.7.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result = self.phase1.estimate(question, context)
        
        if result:
            logger.info(f"  ⚡ Phase 1 (Direct RAG) 성공: {result.value} ({result.execution_time:.2f}초)")
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
        # v7.9.0: Cursor 모드 자동 Fallback
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 3-4는 LLM API 호출 필요
        # Cursor 모드는 대화형이므로 자동 추정 불가
        # → gpt-4o-mini로 자동 Fallback
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        cursor_fallback_active = False
        if self.llm_mode == "cursor":
            logger.info("  🔄 Cursor 모드 → API 모드 자동 Fallback")
            logger.info("     Phase 3-4는 LLM API 필요 → gpt-4o-mini 사용")
            
            # settings 임시 변경
            from umis_rag.core.config import settings
            original_mode = settings.llm_mode
            settings.llm_mode = "gpt-4o-mini"
            cursor_fallback_active = True
        
        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Phase 3: Guestimation (추정 시작, v7.7.0)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            self._ensure_phase3_initialized()
            result = self.phase3.estimate(question, context)
            
            if result:
                logger.info(f"  🧠 Phase 3 완료: {result.value} ({result.execution_time:.2f}초)")
                
                if result.should_learn:
                    logger.info(f"  📚 학습됨 (다음엔 Phase 1로 빠름!)")
                
                return result
        
        finally:
            # Cursor Fallback 복원
            if cursor_fallback_active:
                settings.llm_mode = original_mode
                logger.debug(f"  Cursor 모드 복원: {original_mode}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 4: Fermi Decomposition (v7.7.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 💎 가장 가치있는 작업!
        # 없는 숫자를 만드는 창조적 추정
        # 시간(10-30초), 비용($0) 투자 정당화됨
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # v7.9.0: Cursor Fallback (Phase 4도 동일)
        if self.llm_mode == "cursor" and not cursor_fallback_active:
            logger.info("  🔄 Cursor 모드 → API 모드 자동 Fallback (Phase 4)")
            from umis_rag.core.config import settings
            original_mode = settings.llm_mode
            settings.llm_mode = "gpt-4o-mini"
            cursor_fallback_active = True
        
        try:
            self._ensure_phase4_initialized()
            
            logger.info("  💎 Phase 4 시도: 가치있는 작업!")
            result = self.phase4.estimate(question, context, project_data, depth=0)
            
            if result:
                logger.info(f"  🧩 Phase 4 완료: {result.value} ({result.execution_time:.2f}초)")
                if result.decomposition:
                    logger.info(f"     모형: {result.decomposition.formula}")
                    logger.info(f"     Depth: {result.decomposition.depth}")
                return result
        
        finally:
            # Cursor Fallback 복원
            if cursor_fallback_active:
                settings.llm_mode = original_mode
                logger.debug(f"  Cursor 모드 복원: {original_mode}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 모든 Phase 실패 → 실패 결과 반환 (v7.9.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.warning("  ❌ 모든 Phase 실패")
        
        # v7.9.0: None 대신 실패 결과 반환
        return EstimationResult(
            question=question,
            phase=-1,
            value=None,
            confidence=0.0,
            error="모든 Phase(0-4)에서 추정 실패",
            failed_phases=[0, 1, 2, 3, 4],
            reasoning="추정 불가: 프로젝트 데이터, 학습 규칙, Validator, Guestimation, Fermi 모두 실패",
            context=context,
            execution_time=0.0
        )
    
    def _ensure_phase3_initialized(self):
        """Phase 3 Lazy 초기화 (v7.9.0)"""
        if self.phase3 is None:
            # llm_mode=None으로 전달 → Phase 3이 동적으로 settings 읽음
            self.phase3 = Phase3Guestimation(
                llm_mode=None,  # v7.9.0: 동적 읽기
                learning_writer=self.learning_writer
            )
            logger.info("  ✅ Phase 3 (Guestimation) 로드")
    
    def _ensure_phase4_initialized(self):
        """Phase 4 Lazy 초기화"""
        if self.phase4 is None:
            from .phase4_fermi import Phase4FermiDecomposition
            self.phase4 = Phase4FermiDecomposition()
            logger.info("  ✅ Phase 4 (Fermi Decomposition) 로드")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # v7.10.0: Hybrid Architecture (Thread Pool 병렬화)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _stage1_collect(
        self,
        question: str,
        context: Context,
        project_data: Optional[Dict] = None
    ) -> Tuple[GuardrailCollector, Optional[EstimationResult]]:
        """
        Stage 1: 검증 & 가드레일 수집 (Phase 0-2 병렬)

        Returns:
            (GuardrailCollector, definite_result or None)
        """
        start_time = time.time()
        collector = GuardrailCollector()

        # Phase 0: Project Data (동기, Ultra-fast)
        if project_data:
            result = self._check_project_data(question, project_data, context)
            if result and result.confidence >= 0.95:
                collector.add_definite(result)
                logger.info(f"  [Stage 1] Phase 0 확정값: {result.value}")

        # Fast Path: 이미 확정값 있으면 Stage 2-3 스킵
        if collector.has_definite_value():
            return collector, collector.get_best_definite()

        # Phase 1-2: 병렬 실행 (Thread Pool)
        phase1_result = None
        phase2_result = None

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}

            # Phase 1: Direct RAG
            futures[executor.submit(self.phase1.estimate, question, context)] = "phase1"

            # Phase 2: Validator 검색
            futures[executor.submit(self._search_validator, question, context)] = "phase2"

            for future in as_completed(futures):
                phase_name = futures[future]
                try:
                    result = future.result(timeout=5.0)
                    if phase_name == "phase1":
                        phase1_result = result
                    else:
                        phase2_result = result
                except Exception as e:
                    logger.warning(f"  [Stage 1] {phase_name} 실패: {e}")

        # 결과 처리
        if phase1_result and phase1_result.confidence >= 0.95:
            collector.add_definite(phase1_result)
            logger.info(f"  [Stage 1] Phase 1 확정값: {phase1_result.value}")

        if phase2_result and phase2_result.confidence >= 0.95:
            collector.add_definite(phase2_result)
            logger.info(f"  [Stage 1] Phase 2 확정값: {phase2_result.value}")
        elif phase2_result and phase2_result.confidence >= 0.60:
            # Soft Guardrail로 추가
            guardrail = Guardrail(
                type=GuardrailType.EXPECTED_RANGE,
                value=phase2_result.value,
                confidence=phase2_result.confidence,
                is_hard=False,
                reasoning=f"Validator 유사 데이터: {phase2_result.reasoning or ''}",
                source="Phase2_Validator"
            )
            collector.add_guardrail(guardrail)
            logger.info(f"  [Stage 1] Phase 2 가드레일: {phase2_result.value} (conf={phase2_result.confidence:.2f})")

        elapsed = time.time() - start_time
        logger.info(f"  [Stage 1] 완료: {elapsed:.2f}초, 확정값={collector.has_definite_value()}")

        # 확정값 있으면 반환
        if collector.has_definite_value():
            return collector, collector.get_best_definite()

        return collector, None

    def _stage2_estimate(
        self,
        question: str,
        context: Context,
        collector: GuardrailCollector,
        project_data: Optional[Dict] = None
    ) -> Tuple[Optional[EstimationResult], Optional[EstimationResult]]:
        """
        Stage 2: 병렬 추정 (Phase 3-4)

        Returns:
            (phase3_result, phase4_result)
        """
        start_time = time.time()

        # Lazy 초기화
        self._ensure_phase3_initialized()
        self._ensure_phase4_initialized()

        phase3_result = None
        phase4_result = None

        # Cursor Fallback 설정
        original_mode = None
        if self.llm_mode == "cursor":
            logger.info("  [Stage 2] Cursor → gpt-4o-mini Fallback")
            original_mode = settings.llm_mode
            settings.llm_mode = "gpt-4o-mini"

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {}

                # Phase 3: Guestimation
                futures[executor.submit(self.phase3.estimate, question, context)] = "phase3"

                # Phase 4: Fermi Decomposition
                futures[executor.submit(
                    self.phase4.estimate, question, context, project_data, 0
                )] = "phase4"

                for future in as_completed(futures):
                    phase_name = futures[future]
                    try:
                        result = future.result(timeout=30.0)
                        if phase_name == "phase3":
                            phase3_result = result
                        else:
                            phase4_result = result
                    except Exception as e:
                        logger.warning(f"  [Stage 2] {phase_name} 실패: {e}")

        finally:
            if original_mode:
                settings.llm_mode = original_mode

        elapsed = time.time() - start_time
        logger.info(f"  [Stage 2] 완료: {elapsed:.2f}초")
        if phase3_result:
            logger.info(f"    Phase 3: {phase3_result.value} (conf={phase3_result.confidence:.2f})")
        if phase4_result:
            logger.info(f"    Phase 4: {phase4_result.value} (conf={phase4_result.confidence:.2f})")

        return phase3_result, phase4_result

    def _stage3_synthesize(
        self,
        question: str,
        context: Context,
        collector: GuardrailCollector,
        phase3_result: Optional[EstimationResult],
        phase4_result: Optional[EstimationResult]
    ) -> EstimationResult:
        """
        Stage 3: Enhanced Synthesis (v7.10.0 Week 3)

        기능:
        1. Cross-Validation: Phase 3 Range가 Phase 4 Point 포함 시 +15%
        2. Soft Guardrail: 일치도에 따라 Confidence 조정 (+5% ~ -10%)
        3. Hard Guardrail: Range 강제 적용
        4. Weighted Fusion: Uncertainty 기반 가중 평균
        5. 95% CI: Confidence Interval 계산

        Returns:
            최종 EstimationResult (value, value_range, uncertainty, confidence)
        """
        start_time = time.time()
        logger.info("  [Stage 3] Synthesis 시작...")

        # 결과 없으면 실패
        if not phase3_result and not phase4_result:
            logger.error("  [Stage 3] Phase 3-4 모두 실패")
            return EstimationResult(
                question=question,
                phase=-1,
                value=None,
                confidence=0.0,
                error="Stage 2 (Phase 3-4) 모두 실패",
                context=context,
                execution_time=time.time() - start_time
            )

        # Phase 4만 있으면 그대로 반환
        if not phase3_result:
            logger.info("  [Stage 3] Phase 3 없음 → Phase 4 결과 반환")
            phase4_result.execution_time = time.time() - start_time
            return phase4_result

        # Phase 3만 있으면 그대로 반환
        if not phase4_result:
            logger.info("  [Stage 3] Phase 4 없음 → Phase 3 결과 반환")
            phase3_result.execution_time = time.time() - start_time
            return phase3_result

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: Cross-Validation (Phase 3 Range vs Phase 4 Point)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        cross_validated = False
        cross_validation_bonus = 0.0

        if phase3_result.value_range and phase4_result.value:
            range_min, range_max = phase3_result.value_range
            point_value = phase4_result.value

            if range_min <= point_value <= range_max:
                cross_validated = True
                cross_validation_bonus = 0.15
                logger.info(f"  [Stage 3] Step 1: 교차 검증 성공 (+15%)")
                logger.info(f"            Range [{range_min:,.0f}, {range_max:,.0f}] contains {point_value:,.0f}")
            else:
                logger.warning(f"  [Stage 3] Step 1: 교차 검증 실패")
                logger.warning(f"            {point_value:,.0f} not in [{range_min:,.0f}, {range_max:,.0f}]")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: Soft Guardrail Confidence 조정
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        soft_adjustment = 0.0
        soft_matches = 0
        soft_total = len(collector.soft_guardrails)

        if soft_total > 0 and phase4_result.value:
            for guard in collector.soft_guardrails:
                # Soft Guardrail과의 일치 여부 확인
                if guard.type == GuardrailType.EXPECTED_RANGE:
                    # Expected Range: 값이 가드레일 근처인지 확인 (20% 이내)
                    tolerance = guard.value * 0.2
                    if abs(phase4_result.value - guard.value) <= tolerance:
                        soft_matches += 1

                elif guard.type == GuardrailType.SOFT_UPPER:
                    if phase4_result.value <= guard.value:
                        soft_matches += 1

                elif guard.type == GuardrailType.SOFT_LOWER:
                    if phase4_result.value >= guard.value:
                        soft_matches += 1

            # 일치율에 따른 Confidence 조정
            match_rate = soft_matches / soft_total
            if match_rate >= 0.8:
                soft_adjustment = 0.05  # 80%+ 일치: +5%
                logger.info(f"  [Stage 3] Step 2: Soft 일치 {soft_matches}/{soft_total} (+5%)")
            elif match_rate >= 0.5:
                soft_adjustment = 0.0   # 50-80%: 변화 없음
                logger.info(f"  [Stage 3] Step 2: Soft 일치 {soft_matches}/{soft_total} (0%)")
            else:
                soft_adjustment = -0.10  # 50% 미만: -10%
                logger.warning(f"  [Stage 3] Step 2: Soft 불일치 {soft_matches}/{soft_total} (-10%)")
        else:
            logger.info(f"  [Stage 3] Step 2: Soft Guardrail 없음 (스킵)")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: Hard Guardrail 적용 (Range 강제)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        bounds = collector.get_hard_bounds()
        final_value = phase4_result.value
        hard_adjusted = False

        if bounds['min'] > 0 and final_value < bounds['min']:
            logger.warning(f"  [Stage 3] Step 3: Hard 하한 적용: {final_value:,.0f} → {bounds['min']:,.0f}")
            final_value = bounds['min']
            hard_adjusted = True

        if bounds['max'] < float('inf') and final_value > bounds['max']:
            logger.warning(f"  [Stage 3] Step 3: Hard 상한 적용: {final_value:,.0f} → {bounds['max']:,.0f}")
            final_value = bounds['max']
            hard_adjusted = True

        if not hard_adjusted:
            logger.info(f"  [Stage 3] Step 3: Hard Guardrail 통과")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: Weighted Fusion (Uncertainty 기반)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 3 (Range 중앙값)과 Phase 4 (Point)의 가중 평균
        if phase3_result.value and phase4_result.value:
            # Weight = Confidence (높을수록 비중 높음)
            w3 = phase3_result.confidence
            w4 = phase4_result.confidence
            total_weight = w3 + w4

            if total_weight > 0:
                weighted_value = (phase3_result.value * w3 + phase4_result.value * w4) / total_weight
                # 가중 평균과 Phase 4 값의 차이가 크면 Phase 4 유지
                if abs(weighted_value - phase4_result.value) / phase4_result.value < 0.1:
                    final_value = weighted_value
                    logger.info(f"  [Stage 3] Step 4: Weighted Fusion 적용 (P3:{w3:.2f}, P4:{w4:.2f})")
                else:
                    logger.info(f"  [Stage 3] Step 4: Phase 4 값 유지 (차이 > 10%)")
        else:
            logger.info(f"  [Stage 3] Step 4: Weighted Fusion 스킵 (값 없음)")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 5: 95% CI 계산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        final_range = phase3_result.value_range
        uncertainty = 0.3  # 기본 불확실성 30%

        if final_range and final_value:
            range_min, range_max = final_range
            range_width = range_max - range_min
            uncertainty = range_width / (2 * final_value) if final_value > 0 else 0.3
            uncertainty = min(0.5, max(0.1, uncertainty))  # 10% ~ 50% 범위

            # 95% CI 계산 (정규분포 가정, z=1.96)
            ci_half = final_value * uncertainty * 1.96
            ci_lower = max(0, final_value - ci_half)
            ci_upper = final_value + ci_half
            logger.info(f"  [Stage 3] Step 5: 95% CI = [{ci_lower:,.0f}, {ci_upper:,.0f}]")
        else:
            ci_lower, ci_upper = None, None
            logger.info(f"  [Stage 3] Step 5: 95% CI 계산 불가")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Final: Confidence 종합
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        base_confidence = phase4_result.confidence
        final_confidence = base_confidence + cross_validation_bonus + soft_adjustment
        final_confidence = min(0.99, max(0.10, final_confidence))  # 10% ~ 99% 범위

        elapsed = time.time() - start_time
        logger.info(f"  [Stage 3] 완료: {elapsed:.3f}초")
        logger.info(f"            값: {final_value:,.0f}")
        logger.info(f"            신뢰도: {base_confidence:.2f} → {final_confidence:.2f}")
        logger.info(f"              Cross: +{cross_validation_bonus:.2f}, Soft: {soft_adjustment:+.2f}")

        return EstimationResult(
            question=question,
            value=final_value,
            value_range=final_range,
            unit=phase4_result.unit if phase4_result.unit else "",
            confidence=final_confidence,
            uncertainty=uncertainty,
            phase=4,  # Synthesis 결과는 API phase=4
            reasoning=f"Hybrid Synthesis: Cross={cross_validated}, Soft={soft_matches}/{soft_total}",
            reasoning_detail={
                "method": "enhanced_synthesis_v7.10.0",
                "steps": {
                    "cross_validation": {
                        "passed": cross_validated,
                        "bonus": cross_validation_bonus
                    },
                    "soft_guardrail": {
                        "matches": soft_matches,
                        "total": soft_total,
                        "adjustment": soft_adjustment
                    },
                    "hard_guardrail": {
                        "adjusted": hard_adjusted,
                        "bounds": bounds
                    },
                    "weighted_fusion": {
                        "phase3_weight": phase3_result.confidence if phase3_result.value else 0,
                        "phase4_weight": phase4_result.confidence
                    },
                    "confidence_interval": {
                        "ci_95_lower": ci_lower,
                        "ci_95_upper": ci_upper,
                        "uncertainty": uncertainty
                    }
                },
                "phase3_range": final_range,
                "phase4_value": phase4_result.value,
                "base_confidence": base_confidence,
                "final_confidence": final_confidence
            },
            decomposition=phase4_result.decomposition,
            context=context,
            execution_time=elapsed
        )

    def estimate_hybrid(
        self,
        question: str,
        context: Optional[Context] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None,
        project_data: Optional[Dict[str, Any]] = None
    ) -> EstimationResult:
        """
        v7.10.0 Hybrid Architecture 추정 (3-Stage Pipeline)

        Stage 1: Phase 0-2 병렬 수집 (확정값 Fast Path)
        Stage 2: Phase 3-4 병렬 추정 (Range + Point)
        Stage 3: Synthesis (교차 검증 + 융합)

        Example:
            >>> estimator = EstimatorRAG()
            >>> result = estimator.estimate_hybrid("서울 음식점 수는?")
            >>> print(f"값: {result.value}, 범위: {result.value_range}")
        """
        total_start = time.time()

        # Context 생성
        if context is None:
            context = Context(
                domain=domain or "General",
                region=region,
                time_period=time_period or "2024",
                project_data=project_data or {}
            )

        logger.info(f"[Estimator] Hybrid 추정: {question}")

        # Stage 1: 수집 (Phase 0-2)
        collector, definite_result = self._stage1_collect(question, context, project_data)

        # Fast Path: 확정값 있으면 즉시 반환
        if definite_result:
            logger.info(f"  ⚡ Fast Path: Phase {definite_result.phase} 확정값 반환")
            definite_result.execution_time = time.time() - total_start
            return definite_result

        # Stage 2: 추정 (Phase 3-4)
        phase3_result, phase4_result = self._stage2_estimate(
            question, context, collector, project_data
        )

        # Stage 3: Synthesis
        final_result = self._stage3_synthesize(
            question, context, collector, phase3_result, phase4_result
        )

        final_result.execution_time = time.time() - total_start
        logger.info(f"[Estimator] Hybrid 완료: {final_result.value} ({final_result.execution_time:.2f}초)")

        return final_result

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
            >>> # → Phase 1에서 즉시 리턴 (<0.5초)
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
                            phase=0,
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
        Phase 2: Validator 확정 데이터 검색 (v7.9.0 Enhanced)
        
        추정하기 전 확정 데이터 존재 여부 확인
        
        v7.9.0 개선:
        - Phase 2 Enhanced (컨텍스트 기반) 우선 시도
        - 100개 벤치마크 활용
        - 산업/규모/모델별 조정
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult(phase=2) or None
        """
        import time
        start_time = time.time()
        
        # Validator Lazy 초기화
        if self.validator is None:
            from umis_rag.agents.validator import get_validator_rag
            self.validator = get_validator_rag()
            logger.info("  ✅ Validator 연결")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2 Enhanced 시도 (v7.9.0)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Context에 산업 정보가 있으면 Enhanced 사용
        if context and context.project_data:
            context_dict = context.project_data
            
            # 필수 정보 확인 (industry)
            if 'industry' in context_dict:
                # Phase2Enhanced Lazy 초기화
                if self.phase2_enhanced is None:
                    try:
                        from .phase2_validator_search_enhanced import Phase2ValidatorSearchEnhanced
                        self.phase2_enhanced = Phase2ValidatorSearchEnhanced(
                            validator_rag=self.validator
                        )
                        # Benchmark store 초기화
                        self.phase2_enhanced.initialize_benchmark_store()
                        logger.info("  ✅ Phase 2 Enhanced 초기화")
                    except Exception as e:
                        logger.warning(f"  Phase 2 Enhanced 초기화 실패: {e}")
                        self.phase2_enhanced = None
                
                # Phase2Enhanced 검색 시도
                if self.phase2_enhanced:
                    try:
                        enhanced_result = self.phase2_enhanced.search_with_context(
                            query=question,
                            context=context_dict
                        )
                        
                        if enhanced_result and enhanced_result.confidence >= 0.75:
                            execution_time = time.time() - start_time
                            enhanced_result.execution_time = execution_time
                            logger.info(f"  ✅ Phase 2 Enhanced 성공: {enhanced_result.value:.1%} (Confidence: {enhanced_result.confidence:.2f})")
                            return enhanced_result
                        
                    except Exception as e:
                        logger.warning(f"  Phase 2 Enhanced 오류: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2 Basic (기존)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Validator 검색
        validator_result = self.validator.search_definite_data(question, context)
        
        if validator_result:
            execution_time = time.time() - start_time
            
            return EstimationResult(
                question=question,
                value=validator_result['value'],
                unit=validator_result.get('unit', ''),
                confidence=1.0,
                phase=2,
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
                    f"1. Phase 1 학습 규칙 없음",
                    f"2. Validator 검색 시작",
                    f"3. 출처: {validator_result['source']}",
                    f"4. 값: {validator_result['value']}",
                    f"5. 신뢰도: 1.0 (확정 데이터)"
                ],
                execution_time=execution_time
            )
        
        return None
    
    def _ensure_tier2_initialized(self):
        """Phase 3 Lazy 초기화 (호환성 유지)"""
        if self.phase3 is not None:
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
        
        # Phase 3 초기화
        self.phase3 = Phase3Guestimation(
            learning_writer=self.learning_writer
        )
        logger.info("  ✅ Phase 3 초기화")


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

