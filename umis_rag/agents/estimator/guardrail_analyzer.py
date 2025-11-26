"""
GuardrailAnalyzer - LLM 2단계 체인 (v7.10.0 Week 4)

유사 데이터와 타겟 질문 사이의 관계를 분석하여 적절한 Guardrail로 변환

2단계 체인:
1. 관계 판단: X > Y? X < Y? 무관?
2. Hard/Soft 판정: 논리적(Hard) vs 경험적(Soft)
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from langchain_openai import ChatOpenAI

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger
from umis_rag.core.llm_interface import LLMProvider
from umis_rag.core.llm_provider_factory import get_default_llm_provider
from .models import Guardrail, GuardrailType


class RelationshipType(Enum):
    """관계 유형"""
    UPPER_BOUND = "upper_bound"  # target <= similar (similar이 상한)
    LOWER_BOUND = "lower_bound"  # target >= similar (similar이 하한)
    UNRELATED = "unrelated"      # 관계 없음


@dataclass
class AnalysisResult:
    """분석 결과"""
    relationship: RelationshipType
    is_hard: bool
    confidence: float
    reasoning: str


class GuardrailAnalyzer:
    """
    GuardrailAnalyzer - LLM 2단계 체인
    
    v7.11.0 변경사항:
    ---------------
    - ❌ llm_mode property 제거
    - ✅ LLMProvider 기반
    - ✅ 분기 없음

    사용 예시:
        >>> analyzer = GuardrailAnalyzer()
        >>> guardrail = analyzer.analyze(
        ...     target_question="개인사업자 수는?",
        ...     similar_question="경제활동인구 수는?",
        ...     similar_value=28_000_000
        ... )
        >>> print(guardrail)
        # Guardrail(type=HARD_UPPER, value=28000000, confidence=0.95, ...)
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        초기화
        
        Args:
            llm_provider: LLMProvider (None이면 기본 Provider)
        
        Note:
            v7.11.0: llm_mode 파라미터 제거됨
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        self._llm = None

    def _get_llm(self) -> ChatOpenAI:
        """LLM 인스턴스 (Lazy 초기화)"""
        if self._llm is None:
            model = settings.llm_model
            self._llm = ChatOpenAI(
                model=model,
                temperature=0.1,  # 일관된 판단을 위해 낮은 temperature
                openai_api_key=settings.openai_api_key
            )
        return self._llm

    def analyze(
        self,
        target_question: str,
        similar_question: str,
        similar_value: float,
        target_context: Optional[str] = None,
        similar_context: Optional[str] = None
    ) -> Optional[Guardrail]:
        """
        유사 데이터를 분석하여 Guardrail로 변환

        Args:
            target_question: 추정 대상 질문
            similar_question: 유사 데이터 질문
            similar_value: 유사 데이터 값
            target_context: 타겟 맥락 (선택)
            similar_context: 유사 데이터 맥락 (선택)

        Returns:
            Guardrail 또는 None (무관한 경우)
        """
        logger.info(f"[GuardrailAnalyzer] 분석 시작")
        logger.info(f"  Target: {target_question}")
        logger.info(f"  Similar: {similar_question} = {similar_value:,.0f}")

        try:
            # Step 1: 관계 판단
            relationship = self._step1_relationship(
                target_question, similar_question,
                target_context, similar_context
            )

            if relationship == RelationshipType.UNRELATED:
                logger.info(f"  Step 1: 무관 → Guardrail 없음")
                return None

            # Step 2: Hard/Soft 판정
            is_hard, hardness_reasoning = self._step2_hardness(
                target_question, similar_question,
                relationship
            )

            # Guardrail 생성
            if relationship == RelationshipType.UPPER_BOUND:
                guard_type = GuardrailType.HARD_UPPER if is_hard else GuardrailType.SOFT_UPPER
            else:
                guard_type = GuardrailType.HARD_LOWER if is_hard else GuardrailType.SOFT_LOWER

            confidence = 0.95 if is_hard else 0.75

            guardrail = Guardrail(
                type=guard_type,
                value=similar_value,
                confidence=confidence,
                is_hard=is_hard,
                reasoning=hardness_reasoning,
                source="GuardrailAnalyzer",
                relationship=f"{target_question} {'<=' if relationship == RelationshipType.UPPER_BOUND else '>='} {similar_question}"
            )

            logger.info(f"  결과: {guard_type.value}, Hard={is_hard}, Conf={confidence}")
            return guardrail

        except Exception as e:
            logger.error(f"[GuardrailAnalyzer] 분석 실패: {e}")
            return None

    def _step1_relationship(
        self,
        target_question: str,
        similar_question: str,
        target_context: Optional[str] = None,
        similar_context: Optional[str] = None
    ) -> RelationshipType:
        """Step 1: 관계 판단 (LLM 1)"""

        prompt = f"""두 질문 사이의 수학적 관계를 판단하세요.

질문 A (추정 대상): {target_question}
{f'맥락: {target_context}' if target_context else ''}

질문 B (참조 데이터): {similar_question}
{f'맥락: {similar_context}' if similar_context else ''}

다음 중 하나를 선택하세요:
1. UPPER_BOUND: A의 값은 반드시 B의 값보다 작거나 같다 (A <= B)
   예: "개인사업자 수" <= "전체 사업자 수"
   예: "서울 인구" <= "한국 인구"

2. LOWER_BOUND: A의 값은 반드시 B의 값보다 크거나 같다 (A >= B)
   예: "전체 사업자 수" >= "개인사업자 수"

3. UNRELATED: 두 질문 사이에 명확한 수학적 관계가 없다
   예: "커피숍 수" vs "자동차 수"

JSON 형식으로 응답하세요:
{{"relationship": "UPPER_BOUND" | "LOWER_BOUND" | "UNRELATED", "reasoning": "이유"}}
"""

        try:
            llm = self._get_llm()
            response = llm.invoke(prompt)
            content = response.content.strip()

            # JSON 파싱
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            relationship_str = result.get("relationship", "UNRELATED").upper()

            if relationship_str == "UPPER_BOUND":
                logger.info(f"  Step 1: UPPER_BOUND ({result.get('reasoning', '')})")
                return RelationshipType.UPPER_BOUND
            elif relationship_str == "LOWER_BOUND":
                logger.info(f"  Step 1: LOWER_BOUND ({result.get('reasoning', '')})")
                return RelationshipType.LOWER_BOUND
            else:
                logger.info(f"  Step 1: UNRELATED ({result.get('reasoning', '')})")
                return RelationshipType.UNRELATED

        except Exception as e:
            logger.warning(f"  Step 1 파싱 실패: {e} → UNRELATED")
            return RelationshipType.UNRELATED

    def _step2_hardness(
        self,
        target_question: str,
        similar_question: str,
        relationship: RelationshipType
    ) -> Tuple[bool, str]:
        """Step 2: Hard/Soft 판정 (LLM 2)"""

        relation_desc = "작거나 같다" if relationship == RelationshipType.UPPER_BOUND else "크거나 같다"

        prompt = f"""이 제약 조건이 Hard인지 Soft인지 판정하세요.

제약: "{target_question}"의 값은 "{similar_question}"의 값보다 {relation_desc}.

Hard (논리적 제약):
- 논리적으로 100% 위반이 불가능
- 위반 시 정의 자체가 모순
- 예: "부분 <= 전체", "인구 >= 0"

Soft (경험적 제약):
- 통계적으로 대부분 성립하지만 예외 가능
- 특수한 상황에서 위반 가능
- 예: "평균 매출 < 업계 최대치"

JSON 형식으로 응답하세요:
{{"is_hard": true | false, "reasoning": "이유"}}
"""

        try:
            llm = self._get_llm()
            response = llm.invoke(prompt)
            content = response.content.strip()

            # JSON 파싱
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            is_hard = result.get("is_hard", False)
            reasoning = result.get("reasoning", "판정 완료")

            logger.info(f"  Step 2: {'Hard' if is_hard else 'Soft'} ({reasoning})")
            return is_hard, reasoning

        except Exception as e:
            logger.warning(f"  Step 2 파싱 실패: {e} → Soft")
            return False, f"파싱 실패로 Soft 판정: {e}"

    def analyze_batch(
        self,
        target_question: str,
        similar_items: list,  # List of (question, value, context)
        max_guardrails: int = 5
    ) -> list:
        """여러 유사 데이터를 배치로 분석"""
        guardrails = []

        for item in similar_items[:max_guardrails]:
            if len(item) == 3:
                question, value, context = item
            else:
                question, value = item[:2]
                context = None

            guardrail = self.analyze(
                target_question=target_question,
                similar_question=question,
                similar_value=value,
                similar_context=context
            )

            if guardrail:
                guardrails.append(guardrail)

        logger.info(f"[GuardrailAnalyzer] 배치 완료: {len(guardrails)}/{len(similar_items)} Guardrails")
        return guardrails
