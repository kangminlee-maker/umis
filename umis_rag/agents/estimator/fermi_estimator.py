"""
FermiEstimator - 구조적 설명 엔진 (v7.11.0 Stage 3)

역할:
- Fermi 분해를 통한 "구조적 설명" 제공
- 재귀 금지 (절대적 원칙)
- 예산 기반 제어

설계 원칙:
- Fermi는 "정밀 추정"이 아닌 "설명 + 약간의 튜닝"
- 재귀 대신 PriorEstimator 호출 (depth 1-2 제한)
- 모든 변수는 PriorEstimator로 직접 추정
- 예산 초과 시 즉시 중단

핵심 변경 (v7.11.0):
- NO RECURSION (재귀 완전 금지)
- 모든 변수 추정 = PriorEstimator 호출
- max_depth = 2 (강제)
- 예산 소진 시 즉시 반환
"""

from typing import Optional, Dict, Any, List, Tuple
import json
import time

from langchain_openai import ChatOpenAI

from umis_rag.utils.logger import logger
from umis_rag.core.config import settings
from umis_rag.core.model_router import select_model_with_config

from .common.budget import Budget
from .common.estimation_result import EstimationResult, create_fermi_result, Evidence
from .prior_estimator import PriorEstimator
from .models import Context


class FermiEstimator:
    """
    FermiEstimator - 구조적 설명 엔진 (v7.11.0)
    
    역할:
    -----
    - Fermi 분해로 "구조 설명" 제공
    - 재귀 금지 (절대적 원칙)
    - 모든 변수 = PriorEstimator로 직접 추정
    
    제약:
    -----
    - max_depth: 2 (강제)
    - max_variables: Budget에서 제어
    - max_llm_calls: Budget에서 제어
    - 재귀 호출 = FORBIDDEN
    
    프로세스:
    ---------
    1. LLM이 분해식 제안 (예: LTV = ARPU / Churn)
    2. 각 변수를 PriorEstimator로 직접 추정 (재귀 X)
    3. 공식 계산
    4. 결과 반환 (decomposition 포함)
    """
    
    def __init__(
        self,
        llm_mode: Optional[str] = None,
        model_name: Optional[str] = None,
        prior_estimator: Optional[PriorEstimator] = None
    ):
        """
        초기화
        
        Args:
            llm_mode: LLM 모드
            model_name: LLM 모델 이름 (None이면 Phase 4 기본값)
            prior_estimator: Prior Estimator (None이면 생성)
        """
        self._llm_mode = llm_mode
        self._model_name = model_name
        self._llm = None
        
        # Prior Estimator (변수 추정용)
        self.prior_estimator = prior_estimator or PriorEstimator(llm_mode=llm_mode)
        
        logger.info("[FermiEstimator] 초기화")
        logger.info(f"  LLM Mode: {self.llm_mode}")
        logger.info(f"  Model: {self.model_name}")
        logger.info("  ⚠️  재귀 금지 (Recursion FORBIDDEN)")
    
    @property
    def llm_mode(self) -> str:
        """LLM 모드 동적 읽기"""
        if self._llm_mode is None:
            return settings.llm_mode
        return self._llm_mode
    
    @property
    def model_name(self) -> str:
        """
        LLM 모델 이름 동적 읽기
        
        Phase 4 전용 모델 사용 (gpt-4o 권장)
        """
        if self._model_name is None:
            model, config = select_model_with_config(phase=4)
            return model
        return self._model_name
    
    def _get_llm(self) -> ChatOpenAI:
        """LLM 인스턴스 (Lazy 초기화)"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.2,
                openai_api_key=settings.openai_api_key
            )
        return self._llm
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 인터페이스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def estimate(
        self,
        question: str,
        evidence: Evidence,
        budget: Budget,
        context: Optional[Context] = None,
        depth: int = 0
    ) -> Optional[EstimationResult]:
        """
        Fermi 분해 추정 (v7.11.0)
        
        Args:
            question: 질문
            evidence: 수집된 증거
            budget: 예산
            context: 맥락
            depth: 현재 깊이 (0부터 시작)
        
        Returns:
            EstimationResult or None
        """
        logger.info(f"[FermiEstimator] 추정 시작 (depth={depth}): {question}")
        start_time = time.time()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 깊이 제한 (max_depth = 2)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if depth >= budget.max_depth:
            logger.warning(f"  깊이 제한 초과 (depth={depth} >= max={budget.max_depth})")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 예산 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if budget.is_exhausted():
            logger.warning("  예산 소진")
            return None
        
        if not budget.can_call_llm(1):
            logger.warning("  LLM 호출 예산 부족")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: LLM이 분해식 제안
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            formula, variables = self._generate_decomposition(question, evidence, context)
            budget.consume_llm_call(1)
            
            logger.info(f"  분해식: {formula}")
            logger.info(f"  변수: {list(variables.keys())}")
        
        except Exception as e:
            logger.error(f"  분해식 생성 실패: {e}")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: 각 변수 추정 (PriorEstimator만 사용, 재귀 금지)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        variable_results = {}
        
        for var_name, var_description in variables.items():
            # 예산 체크
            if budget.is_exhausted():
                logger.warning(f"  예산 소진 (변수 {var_name} 추정 중단)")
                break
            
            if not budget.can_call_llm(1) or not budget.can_estimate_variable(1):
                logger.warning(f"  변수 {var_name} 추정 불가 (예산 부족)")
                break
            
            logger.info(f"  변수 추정: {var_name} = {var_description}")
            
            # PriorEstimator로 직접 추정 (재귀 금지!)
            var_question = f"{var_name}은/는?"
            
            try:
                var_result = self.prior_estimator.estimate(
                    question=var_question,
                    evidence=evidence,  # 동일한 증거 사용
                    budget=budget,
                    context=context
                )
                
                if var_result:
                    variable_results[var_name] = var_result
                    logger.info(f"    ✅ {var_name} = {var_result.value:,.0f} (certainty={var_result.certainty})")
                else:
                    logger.warning(f"    ❌ {var_name} 추정 실패")
                    # Fallback: 기본값 사용 (0이 아닌 1로)
                    from .common.estimation_result import create_prior_result
                    variable_results[var_name] = create_prior_result(
                        value=1.0,
                        value_range=(0.1, 10.0),
                        certainty='low',
                        reasoning=f"{var_name} 추정 실패 → Fallback 기본값",
                        llm_calls=0
                    )
            
            except Exception as e:
                logger.error(f"    ❌ {var_name} 추정 오류: {e}")
                continue
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: 공식 계산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if not variable_results:
            logger.warning("  변수 추정 결과 없음")
            return None
        
        try:
            final_value = self._evaluate_formula(formula, variable_results)
            logger.info(f"  계산 결과: {final_value:,.0f}")
        
        except Exception as e:
            logger.error(f"  공식 계산 실패: {e}")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: 결과 생성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elapsed = time.time() - start_time
        
        # Decomposition 구조
        decomposition = {
            'formula': formula,
            'variables': {
                var_name: {
                    'value': var_result.value,
                    'certainty': var_result.certainty,
                    'reasoning': var_result.reasoning
                }
                for var_name, var_result in variable_results.items()
            },
            'depth': depth
        }
        
        # Certainty 종합 (변수들의 평균)
        certainties = [r.get_certainty_score() for r in variable_results.values()]
        avg_certainty_score = sum(certainties) / len(certainties) if certainties else 0.5
        
        if avg_certainty_score >= 0.8:
            certainty = 'high'
        elif avg_certainty_score >= 0.5:
            certainty = 'medium'
        else:
            certainty = 'low'
        
        # 비용 집계
        total_llm_calls = 1 + sum(r.cost.get('llm_calls', 0) for r in variable_results.values())
        total_variables = len(variable_results)
        
        cost = {
            'llm_calls': total_llm_calls,
            'variables': total_variables,
            'time': elapsed
        }
        
        reasoning = f"Fermi 분해: {formula} (depth={depth}, {total_variables}개 변수)"
        
        result = create_fermi_result(
            value=final_value,
            decomposition=decomposition,
            certainty=certainty,
            reasoning=reasoning,
            cost=cost
        )
        result.used_evidence = [evidence]
        
        logger.info(f"  ✅ Fermi 완료: {final_value:,.0f} (certainty={certainty}, {elapsed:.2f}초)")
        
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Private Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _generate_decomposition(
        self,
        question: str,
        evidence: Evidence,
        context: Optional[Context]
    ) -> Tuple[str, Dict[str, str]]:
        """
        LLM이 분해식 생성
        
        Args:
            question: 질문
            evidence: 증거
            context: 맥락
        
        Returns:
            (formula, variables)
            - formula: "LTV = ARPU / Churn"
            - variables: {'ARPU': 'B2B SaaS 월평균 매출', 'Churn': '월 해지율'}
        """
        prompt = f"""당신은 Fermi 추정 전문가입니다. 주어진 질문을 **2-4개의 변수**로 분해하세요.

질문: {question}
"""
        
        if context:
            prompt += f"\n맥락:\n"
            # Context 형식 처리: 객체 또는 딕셔너리
            domain = context.get('domain') if isinstance(context, dict) else getattr(context, 'domain', None)
            region = context.get('region') if isinstance(context, dict) else getattr(context, 'region', None)
            
            if domain:
                prompt += f"  - 도메인: {domain}\n"
            if region:
                prompt += f"  - 지역: {region}\n"
        
        prompt += """
분해 원칙:
1. **간결함**: 2-4개 변수만 사용 (최대 4개)
2. **직접 추정 가능**: 각 변수는 LLM이 직접 추정 가능해야 함
3. **명확한 공식**: 단순한 사칙연산 (×, ÷, +, -)
4. **재귀 금지**: 변수는 더 이상 분해하지 않음

출력 형식 (JSON):
```json
{
  "formula": "공식 (예: LTV = ARPU / Churn)",
  "variables": {
    "변수1": "설명",
    "변수2": "설명"
  }
}
```

예시:
```json
{
  "formula": "시장규모 = 사업자수 * 평균매출 * 도입률",
  "variables": {
    "사업자수": "한국 전체 사업자 수",
    "평균매출": "사업자 평균 연매출",
    "도입률": "해당 서비스 도입 비율"
  }
}
```
"""
        
        llm = self._get_llm()
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # JSON 파싱
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        parsed = json.loads(content)
        
        formula = parsed['formula']
        variables = parsed['variables']
        
        # 변수 개수 제한 (최대 4개)
        if len(variables) > 4:
            logger.warning(f"  변수 개수 제한: {len(variables)}개 → 4개로 축소")
            variables = dict(list(variables.items())[:4])
        
        return formula, variables
    
    def _evaluate_formula(
        self,
        formula: str,
        variable_results: Dict[str, EstimationResult]
    ) -> float:
        """
        공식 계산
        
        Args:
            formula: 공식 문자열 (예: "LTV = ARPU / Churn")
            variable_results: 변수 추정 결과
        
        Returns:
            계산된 값
        """
        # "=" 기준으로 우변만 추출
        if "=" in formula:
            expression = formula.split("=")[1].strip()
        else:
            expression = formula.strip()
        
        # 변수 값 치환
        for var_name, var_result in variable_results.items():
            expression = expression.replace(var_name, str(var_result.value))
        
        # × → *, ÷ → / 변환
        expression = expression.replace('×', '*').replace('÷', '/')
        
        # 계산 (eval 사용, 보안 주의)
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            logger.error(f"  공식 계산 오류: {e}")
            logger.error(f"  Expression: {expression}")
            raise
