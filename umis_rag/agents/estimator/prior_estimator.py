"""
PriorEstimator - 생성적 사전 추정기 (v7.11.0 Stage 2)

역할:
- LLM에게 직접 값을 요청 (Phase 3 재설계)
- "증명"이 아닌 "생성" - LLM의 내적 확신도 활용
- 범위 + Certainty 제공

설계 원칙:
- LLM은 "경험 데이터의 압축"으로 간주
- 확신 있게 말할 수 있는 값을 찍음
- Certainty: high/medium/low (내적 확신도)
- 재귀 금지 (절대적 원칙)

v7.11.0 완전 추상화:
- llm_mode property 제거
- LLMProvider 기반
- 분기 없음
"""

from typing import Optional, Tuple
import json
import time

from langchain_openai import ChatOpenAI

from umis_rag.utils.logger import logger
from umis_rag.core.config import settings
from umis_rag.core.llm_interface import LLMProvider, TaskType
from umis_rag.core.llm_provider_factory import get_default_llm_provider

from .common.budget import Budget
from .common.estimation_result import EstimationResult, create_prior_result, Evidence
from .models import Context


class PriorEstimator:
    """
    PriorEstimator - 생성적 사전 추정기 (v7.11.0)
    
    역할:
    -----
    - LLM에게 직접 값을 요청 (단일 호출)
    - 범위 + Certainty 반환
    - 재귀 금지 (절대적 원칙)
    
    v7.11.0 변경사항:
    ---------------
    - ❌ llm_mode property 제거
    - ✅ LLMProvider 기반
    - ✅ 분기 없음
    
    프롬프트 설계:
    -------------
    "당신이 확신 있게 말할 수 있는 값을 제시하세요"
    → LLM의 내적 확신도(certainty) 활용
    
    출력:
    -----
    - value: 추정 값
    - range: 값 범위 (min, max)
    - certainty: high/medium/low
    - reasoning: 추정 근거
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        model_name: Optional[str] = None
    ):
        """
        초기화
        
        Args:
            llm_provider: LLMProvider (None이면 기본 Provider)
            model_name: LLM 모델 이름 (None이면 Stage 2 기본값)
        
        Note:
            v7.11.0: llm_mode 파라미터 제거됨
        """
        self.llm_provider = llm_provider or get_default_llm_provider()
        self._model_name = model_name
        self._llm = None
        
        logger.info("[PriorEstimator] 초기화")
        logger.info(f"  Provider: {self.llm_provider.__class__.__name__}")
        logger.info(f"  Model: {self.model_name}")
    
    @property
    def model_name(self) -> str:
        """
        LLM 모델 이름 동적 읽기
        
        Stage 2 전용 모델 사용 (gpt-4.1-nano 또는 설정된 모델)
        """
        if self._model_name is None:
            # Stage 2 모델 선택
            from umis_rag.core.model_router import select_model_with_config
            
            model, config = select_model_with_config(phase=2)  # Stage 2
            return model
        return self._model_name
    
    def _get_llm(self) -> ChatOpenAI:
        """
        LLM 인스턴스 (Lazy 초기화)
        
        Note:
            현재는 직접 ChatOpenAI 생성하지만,
            향후 LLMProvider.get_llm()을 통해 받아올 수 있음
        """
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.3,  # 약간의 다양성 허용
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
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        Prior 추정 (v7.11.0)
        
        Args:
            question: 질문
            evidence: 수집된 증거 (Hard Bounds, Soft Hints)
            budget: 예산
            context: 맥락 (선택)
        
        Returns:
            EstimationResult or None
        
        Note:
            v7.11.0: 분기 없음 (Native/External 자동 처리)
        """
        logger.info(f"[PriorEstimator] 추정 시작: {question}")
        start_time = time.time()
        
        # 예산 체크
        if not budget.can_call_llm(1):
            logger.warning("  예산 부족 (LLM 호출)")
            return None
        
        # LLM 호출
        try:
            value, value_range, certainty, reasoning = self._call_llm(
                question, evidence, context
            )
            
            # 예산 소비
            budget.consume_llm_call(1)
            budget.consume_variable(1)
            
            elapsed = time.time() - start_time
            
            # 결과 생성
            result = create_prior_result(
                value=value,
                value_range=value_range,
                certainty=certainty,
                reasoning=reasoning,
                llm_calls=1
            )
            result.cost['time'] = elapsed
            result.cost['variables'] = 1
            result.used_evidence = [evidence]
            
            logger.info(f"  ✅ 완료: {value:,.0f} (certainty={certainty}, {elapsed:.2f}초)")
            
            return result
        
        except Exception as e:
            logger.error(f"  ❌ Prior 추정 실패: {e}")
            return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Private Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _call_llm(
        self,
        question: str,
        evidence: Evidence,
        context: Optional[Context]
    ) -> Tuple[float, Tuple[float, float], str, str]:
        """
        LLM 호출 (단일)
        
        Args:
            question: 질문
            evidence: 증거
            context: 맥락
        
        Returns:
            (value, range, certainty, reasoning)
        
        Note:
            v7.11.0: LLM 직접 호출 (프롬프트 커스터마이징 필요)
        """
        # 프롬프트 생성
        prompt = self._build_prompt(question, evidence, context)
        
        # LLM 호출 (직접)
        llm = self._get_llm()
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # JSON 파싱
        parsed = self._parse_response(content)
        
        value = parsed['value']
        value_range = (parsed['range'][0], parsed['range'][1])
        certainty = parsed['certainty']
        reasoning = parsed['reasoning']
        
        return value, value_range, certainty, reasoning
    
    def _build_prompt(
        self,
        question: str,
        evidence: Evidence,
        context: Optional[Context]
    ) -> str:
        """
        프롬프트 생성
        
        Args:
            question: 질문
            evidence: 증거
            context: 맥락
        
        Returns:
            프롬프트 문자열
        """
        prompt = f"""당신은 시장 분석 전문가입니다. 주어진 질문에 대해 **당신이 확신 있게 말할 수 있는 값**을 제시하세요.

질문: {question}
"""
        
        # 맥락 추가
        if context:
            prompt += f"\n맥락:\n"
            # Context 형식 처리: 객체 또는 딕셔너리
            domain = context.get('domain') if isinstance(context, dict) else getattr(context, 'domain', None)
            region = context.get('region') if isinstance(context, dict) else getattr(context, 'region', None)
            time_period = context.get('time_period') if isinstance(context, dict) else getattr(context, 'time_period', None)
            
            if domain:
                prompt += f"  - 도메인: {domain}\n"
            if region:
                prompt += f"  - 지역: {region}\n"
            if time_period:
                prompt += f"  - 시기: {time_period}\n"
        
        # Hard Bounds 추가
        if evidence.hard_bounds:
            min_val, max_val = evidence.hard_bounds
            prompt += f"\n논리적 제약:\n"
            if min_val is not None:
                prompt += f"  - 최소값: {min_val:,.0f} (절대 위반 불가)\n"
            if max_val is not None:
                prompt += f"  - 최대값: {max_val:,.0f} (절대 위반 불가)\n"
        
        # Soft Hints 추가
        if evidence.soft_hints:
            prompt += f"\n참고 정보:\n"
            for hint in evidence.soft_hints[:3]:  # 최대 3개
                if hint.get('type') == 'range':
                    prompt += f"  - 범위: {hint['min']:,.0f} ~ {hint['max']:,.0f} (출처: {hint['source']})\n"
        
        # 출력 형식
        prompt += """
당신의 판단:
1. **value**: 당신이 가장 확신하는 단일 값
2. **range**: 합리적인 범위 [min, max]
3. **certainty**: 당신의 확신도 (high/medium/low)
   - high: 매우 확신함 (거의 확실)
   - medium: 적당히 확신함 (일반적인 경우)
   - low: 약간 확신함 (불확실하지만 추측 가능)
4. **reasoning**: 왜 이 값을 선택했는지 (1-2문장)

**중요**: 
- Hard Constraints는 절대 위반하지 마세요.
- 모르면 범위를 넓게 잡고 certainty를 낮게 설정하세요.
- 추측이나 가정은 명시하세요.

JSON 형식으로 응답하세요:
```json
{
  "value": <숫자>,
  "range": [<min>, <max>],
  "certainty": "high|medium|low",
  "reasoning": "이유"
}
```
"""
        
        return prompt
    
    def _parse_response(self, content: str) -> dict:
        """
        LLM 응답 파싱
        
        Args:
            content: LLM 응답 (JSON)
        
        Returns:
            파싱된 딕셔너리
        """
        # JSON 블록 추출
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Underscore 제거 (51_700_000 → 51700000)
        import re
        content = re.sub(r'(\d)_(\d)', r'\1\2', content)
        
        # JSON 파싱
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"  JSON 파싱 실패: {e}")
            logger.error(f"  Content: {content}")
            raise
        
        # 필수 필드 체크
        required_fields = ['value', 'range', 'certainty', 'reasoning']
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # Certainty 검증
        if parsed['certainty'] not in ['high', 'medium', 'low']:
            logger.warning(f"  Invalid certainty: {parsed['certainty']} → medium")
            parsed['certainty'] = 'medium'
        
        return parsed
