"""
Boundary Validator (v7.6.2)

LLM 기반 비정형 사고로 추정값의 타당성 검증

Hard Boundaries (절대 한계):
- 물리적 한계 (시공간, 보존법칙, 수학)
- 법적 한계 (법률, 규정)
- 논리적 한계 (상위개념 > 하위개념)

Soft Boundaries (참고 범위):
- 통계적 범위 (p10-p90)
- 업계 관행
- 경험적 범위
"""

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from umis_rag.utils.logger import logger
from umis_rag.core.config import settings

# LLM
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class BoundaryCheck:
    """Boundary 검증 결과"""
    
    is_valid: bool
    
    # Hard Boundaries
    hard_violations: list = None
    hard_min: Optional[float] = None
    hard_max: Optional[float] = None
    
    # Soft Boundaries
    soft_warnings: list = None
    soft_min: Optional[float] = None
    soft_max: Optional[float] = None
    
    # 권장 범위
    recommended_range: Optional[Tuple[float, float]] = None
    
    # 근거
    reasoning: str = ""
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.hard_violations is None:
            self.hard_violations = []
        if self.soft_warnings is None:
            self.soft_warnings = []


class BoundaryValidator:
    """
    LLM 기반 Boundary 검증기
    
    역할:
    -----
    Tier 3 추정 결과의 타당성을 비정형적 사고로 검증
    
    검증 단계:
    ----------
    1. Hard Boundaries (절대 한계)
       - 물리적: 속도 < 광속, 확률 [0,1] 등
       - 법적: 최저임금 이상, 근로시간 < 52시간 등
       - 논리적: 부분 < 전체, 세부 < 총합 등
    
    2. Soft Boundaries (참고 범위)
       - 통계적: p10-p90 범위
       - 업계: 일반적 범위
       - 경험적: 상식선
    
    Usage:
        >>> validator = BoundaryValidator()
        >>> check = validator.validate(
        ...     question="한국 음식점 수는?",
        ...     estimated_value=51_000_000,
        ...     context=Context(domain="Food_Service")
        ... )
        >>> if not check.is_valid:
        ...     print("비현실적:", check.hard_violations)
    """
    
    def __init__(self, llm_mode: str = "native"):
        """
        초기화
        
        Args:
            llm_mode: "native" (Cursor) or "external" (API)
        """
        self.llm_mode = llm_mode
        self.llm_client = None
        
        if llm_mode == "external" and HAS_OPENAI:
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
        
        logger.info(f"[Boundary Validator] 초기화 (mode: {llm_mode})")
    
    def validate(
        self,
        question: str,
        estimated_value: float,
        unit: str = "",
        context: Optional[Any] = None,
        formula: str = ""
    ) -> BoundaryCheck:
        """
        추정값 Boundary 검증
        
        Args:
            question: 질문
            estimated_value: 추정값
            unit: 단위
            context: 맥락
            formula: 사용된 공식
        
        Returns:
            BoundaryCheck (is_valid, violations, reasoning)
        """
        logger.info(f"[Boundary Check] {question} = {estimated_value:,.0f} {unit}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 1: Hard Boundaries (절대 한계)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        hard_check = self._check_hard_boundaries(
            question, estimated_value, unit, context
        )
        
        if hard_check['violations']:
            logger.warning(f"  ❌ Hard Boundary 위반: {hard_check['violations']}")
            
            return BoundaryCheck(
                is_valid=False,
                hard_violations=hard_check['violations'],
                hard_min=hard_check.get('min'),
                hard_max=hard_check.get('max'),
                reasoning=hard_check['reasoning']
            )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 2: Soft Boundaries (참고 범위)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        soft_check = self._check_soft_boundaries(
            question, estimated_value, unit, context
        )
        
        if soft_check['warnings']:
            logger.info(f"  ⚠️  Soft Boundary 경고: {soft_check['warnings']}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 3: LLM Reasoning (Native Mode)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Native Mode: Cursor가 직접 판단
        # External Mode: GPT API 호출
        
        llm_check = self._llm_boundary_check(
            question, estimated_value, unit, context, formula
        )
        
        if llm_check:
            if llm_check.get('violations'):
                return BoundaryCheck(
                    is_valid=False,
                    hard_violations=llm_check['violations'],
                    reasoning=llm_check['reasoning']
                )
            
            if llm_check.get('warnings'):
                soft_check['warnings'].extend(llm_check['warnings'])
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 통과
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.info(f"  ✅ Boundary 검증 통과")
        
        return BoundaryCheck(
            is_valid=True,
            soft_warnings=soft_check['warnings'],
            soft_min=soft_check.get('min'),
            soft_max=soft_check.get('max'),
            recommended_range=soft_check.get('range'),
            reasoning="Boundary 검증 통과",
            confidence=0.90 if not soft_check['warnings'] else 0.75
        )
    
    def _check_hard_boundaries(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Hard Boundaries 검증 (개념 기반 동적 추론)
        
        열거형 하드코딩 대신 LLM이 개념을 분석하여
        논리적 상한/하한 도출
        
        프로세스:
        1. 질문에서 추정 대상 개념 추출
        2. 개념의 상위 개념 찾기
        3. 상위 개념 기반 논리적 상한 계산
        4. 하위 개념 기반 논리적 하한 계산
        5. 추정값이 범위 내인지 검증
        
        Returns:
            {
                'violations': [],
                'min': float,  # 논리적 하한
                'max': float,  # 논리적 상한
                'reasoning': str
            }
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Native Mode: Cursor가 개념 기반 추론
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 1. 개념 추출 및 분석
        concept_analysis = self._analyze_concept(question, context)
        
        if not concept_analysis:
            # 개념 분석 실패 → 기본 검증만
            return self._basic_hard_check(value, unit)
        
        # 2. 논리적 상한/하한 도출
        boundary = self._derive_logical_boundary(
            concept_analysis, value, context
        )
        
        # 3. 검증
        violations = []
        
        if boundary['min'] is not None and value < boundary['min']:
            violations.append(
                f"{value:,.0f} < 논리적 하한 {boundary['min']:,.0f} "
                f"({boundary['min_reasoning']})"
            )
        
        if boundary['max'] is not None and value > boundary['max']:
            violations.append(
                f"{value:,.0f} > 논리적 상한 {boundary['max']:,.0f} "
                f"({boundary['max_reasoning']})"
            )
        
        return {
            'violations': violations,
            'min': boundary['min'],
            'max': boundary['max'],
            'reasoning': boundary.get('reasoning', '')
        }
    
    def _analyze_concept(
        self,
        question: str,
        context: Optional[Any]
    ) -> Optional[Dict]:
        """
        개념 분석 (Native Mode - Cursor 추론)
        
        질문에서 추정 대상의 개념을 추출하고 분석
        
        Args:
            question: "한국 음식점 수는?"
            context: Context(domain="Food_Service", region="한국")
        
        Returns:
            {
                'concept': '음식점 수',
                'type': 'count',  # count, rate, amount, size
                'scope': '한국',
                'super_concepts': ['한국 인구', '한국 사업체 수'],
                'sub_concepts': ['강남 음식점', '서울 음식점']
            }
        """
        # 개념 타입 분류
        concept_type = None
        concept_name = None
        
        # 개수/수량
        if '수' in question or '개수' in question or 'count' in question.lower():
            concept_type = 'count'
            
            # 무엇의 개수?
            if '음식점' in question:
                concept_name = '음식점 수'
            elif '카페' in question:
                concept_name = '카페 수'
            elif '담배' in question:
                concept_name = '담배 판매량'
            elif '인구' in question:
                concept_name = '인구'
        
        # 비율
        elif '비율' in question or '률' in question or 'rate' in question.lower():
            concept_type = 'rate'
            concept_name = '비율'
        
        # 규모/금액
        elif '규모' in question or '시장' in question:
            concept_type = 'market_size'
            concept_name = '시장 규모'
        
        if not concept_name:
            return None
        
        # 스코프 (지역)
        scope = context.region if context and context.region else '한국'
        
        # 상위 개념 추론 (Native Mode - Cursor가 직접)
        super_concepts = self._infer_super_concepts(
            concept_name, scope, context
        )
        
        return {
            'concept': concept_name,
            'type': concept_type,
            'scope': scope,
            'super_concepts': super_concepts
        }
    
    def _infer_super_concepts(
        self,
        concept: str,
        scope: str,
        context: Optional[Any]
    ) -> list:
        """
        상위 개념 추론 (Native Mode - 일반화)
        
        열거형 최소화, 개념 계층 구조 활용
        
        Args:
            concept: '음식점 수', '펜션 수' 등 (미정의 개념도 OK)
            scope: '한국', '서울', '제주' 등
        
        Returns:
            [(super_name, super_value, unit), ...]
        """
        super_concepts = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 지역 계층 (스코프 기반, 일반화됨)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        region_hierarchy = self._get_region_hierarchy(scope)
        
        # 모든 'count' 타입은 인구가 상위 개념
        for region_name, population in region_hierarchy:
            super_concepts.append((f'{region_name} 인구', population, '명'))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 업종/도메인 계층 (개념 기반)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 사업체 관련 (음식점, 카페, 펜션, 학원, 병원 등)
        if any(kw in concept for kw in ['음식점', '카페', '식당', '펜션', '학원', '병원', '가게', '매장']):
            # 모든 사업체는 자영업 < 전체 사업체 < 인구
            super_concepts.extend([
                ('한국 사업체 수', 5_000_000, '개'),
                ('한국 자영업자', 3_000_000, '명')
            ])
        
        # 흡연 관련
        elif '담배' in concept or '흡연' in concept:
            super_concepts.extend([
                ('한국 성인 인구', 43_000_000, '명'),
                ('흡연자 추정', 8_170_000, '명')
            ])
        
        # 시장 규모 관련
        elif '시장' in concept:
            super_concepts.extend([
                ('한국 GDP', 1_800_000_000_000_000, '원')
            ])
            
            # 디지털/콘텐츠 시장이면
            if context and ('digital' in context.domain.lower() or 'content' in context.domain.lower()):
                super_concepts.append(
                    ('디지털 경제', 500_000_000_000_000, '원')
                )
        
        return super_concepts
    
    def _get_region_hierarchy(self, scope: str) -> list:
        """
        지역 계층 구조 (일반화)
        
        Args:
            scope: '강남', '서울', '제주' 등
        
        Returns:
            [(region_name, population), ...]
            상위로 갈수록 뒤에 (한국이 마지막)
        """
        hierarchy = []
        
        # 기본 상수 (Native Mode - Cursor가 알고 있는 값)
        POPULATIONS = {
            '한국': 51_000_000,
            '서울': 9_500_000,
            '부산': 3_400_000,
            '제주': 670_000,
            '강남': 550_000,
            '강남구': 550_000,
        }
        
        # 지역 계층 정의 (필요시 확장)
        HIERARCHIES = {
            '강남': ['강남', '서울', '한국'],
            '강남구': ['강남구', '서울', '한국'],
            '서울': ['서울', '한국'],
            '부산': ['부산', '한국'],
            '제주': ['제주', '한국'],
        }
        
        # 계층 찾기
        region_chain = HIERARCHIES.get(scope, [scope, '한국'])
        
        # 인구 값 매핑
        for region in region_chain:
            if region in POPULATIONS:
                hierarchy.append((region, POPULATIONS[region]))
        
        return hierarchy
    
    def _derive_logical_boundary(
        self,
        concept_analysis: Dict,
        value: float,
        context: Optional[Any]
    ) -> Dict:
        """
        논리적 Boundary 도출 (Native Mode - Cursor 추론)
        
        개념과 상위 개념을 바탕으로 논리적 상한/하한 계산
        
        Args:
            concept_analysis: 개념 분석 결과
            value: 추정값
            context: 맥락
        
        Returns:
            {
                'min': float,  # 논리적 하한
                'max': float,  # 논리적 상한
                'min_reasoning': str,
                'max_reasoning': str
            }
        """
        concept_type = concept_analysis['type']
        super_concepts = concept_analysis['super_concepts']
        
        min_val = None
        max_val = None
        min_reasoning = ""
        max_reasoning = ""
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 개수 타입 (count)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if concept_type == 'count':
            # 하한: 0 (개수는 음수 불가)
            min_val = 0
            min_reasoning = "개수는 0 이상"
            
            # 상한: 상위 개념 활용
            if super_concepts:
                # 가장 제약적인 상위 개념 사용
                for super_name, super_value, super_unit in super_concepts:
                    if '인구' in super_name:
                        # 음식점 < 인구 (1인 1음식점 불가능)
                        # 극단적 밀도: 10명/점
                        max_val = super_value / 10
                        max_reasoning = f"{super_name}({super_value:,.0f}) / 극단적 밀도(10명/점)"
                        break
                    elif '사업체' in super_name:
                        # 음식점 < 전체 사업체
                        max_val = super_value
                        max_reasoning = f"{super_name} 이하"
                        break
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 비율 타입 (rate)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif concept_type == 'rate':
            # 수학적 정의
            min_val = 0.0
            max_val = 1.0
            min_reasoning = "비율 하한 (수학적 정의)"
            max_reasoning = "비율 상한 (수학적 정의)"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 시장 규모 타입
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif concept_type == 'market_size':
            # 하한: 0 (시장은 음수 불가)
            min_val = 0
            min_reasoning = "시장 규모 하한"
            
            # 상한: GDP 또는 상위 시장
            if super_concepts:
                for super_name, super_value, super_unit in super_concepts:
                    if 'GDP' in super_name:
                        # 개별 시장 < GDP
                        max_val = super_value
                        max_reasoning = f"{super_name} 이하"
                        break
                    elif '경제' in super_name:
                        max_val = super_value
                        max_reasoning = f"{super_name} 이하"
                        break
        
        return {
            'min': min_val,
            'max': max_val,
            'min_reasoning': min_reasoning,
            'max_reasoning': max_reasoning,
            'reasoning': f"상한: {max_reasoning}, 하한: {min_reasoning}"
        }
    
    def _basic_hard_check(self, value: float, unit: str) -> Dict:
        """
        기본 Hard Check (개념 분석 실패 시)
        
        최소한의 검증만
        """
        violations = []
        
        # 음수 체크
        if value < 0:
            violations.append(f"음수 값: {value}")
        
        # 비율 체크
        if '비율' in unit or '%' in unit:
            if value < 0 or value > 1:
                violations.append(f"비율 범위 위반: {value}")
        
        return {
            'violations': violations,
            'reasoning': "; ".join(violations) if violations else ""
        }
    
    def _check_soft_boundaries(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Soft Boundaries 검증 (참고 범위)
        
        Returns:
            {
                'warnings': [],
                'min': float,
                'max': float,
                'range': (min, max)
            }
        """
        warnings = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 경험적 범위 (상식선)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 음식점 수 (한국)
        if '음식점' in question and '한국' in question:
            if value < 100_000 or value > 2_000_000:
                warnings.append(f"음식점 {value:,.0f}개 (일반 범위: 10만-200만)")
        
        # 시장 규모 (한국 디지털)
        if '시장' in question and '규모' in question:
            if context and 'digital' in context.domain.lower():
                if value < 100_000_000_000 or value > 10_000_000_000_000:
                    warnings.append(f"디지털 시장 {value:,.0f}원 (일반 범위: 1000억-10조)")
        
        return {
            'warnings': warnings
        }
    
    def _llm_boundary_check(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any],
        formula: str
    ) -> Optional[Dict]:
        """
        LLM 기반 Boundary 검증 (비정형 사고)
        
        Native Mode: Cursor가 직접 판단
        External Mode: GPT API 호출
        
        Returns:
            {
                'violations': [],  # Hard boundary 위반
                'warnings': [],    # Soft boundary 경고
                'reasoning': str
            } or None
        """
        if self.llm_mode == "native":
            # Native Mode: 템플릿 기반 (빠름, 비용 $0)
            return self._native_boundary_check(question, value, unit, context)
        
        elif self.llm_mode == "external" and self.llm_client:
            # External Mode: GPT 호출 (정교, 비용 $0.001)
            return self._external_boundary_check(question, value, unit, context, formula)
        
        return None
    
    def _native_boundary_check(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any]
    ) -> Dict:
        """
        Native Mode Boundary Check (v7.6.2)
        
        개념 기반 동적 추론은 _check_hard_boundaries에서 수행
        여기서는 추가 검증만
        """
        violations = []
        warnings = []
        
        # Hard Boundaries는 이미 체크됨
        # 여기서는 추가적인 도메인 특화 검증만
        
        return {
            'violations': violations,
            'warnings': warnings,
            'reasoning': "Native Mode (개념 기반 검증 완료)"
        }
    
    def _external_boundary_check(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any],
        formula: str
    ) -> Dict:
        """
        External Mode: GPT API로 정교한 검증
        
        LLM에게 비정형적 사고 요청:
        - 상위/하위 개념
        - 물리적/법적 한계
        - 경험적 타당성
        """
        prompt = self._build_boundary_prompt(question, value, unit, context, formula)
        
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.llm_model,
                temperature=0.1,  # 낮은 temperature (객관적 판단)
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 추정값의 타당성을 검증하는 전문가입니다. 물리적, 법적, 논리적 한계를 고려하여 판단하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            llm_output = response.choices[0].message.content
            
            # 파싱
            return self._parse_boundary_response(llm_output)
        
        except Exception as e:
            logger.error(f"LLM Boundary check 실패: {e}")
            return None
    
    def _build_boundary_prompt(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Any],
        formula: str
    ) -> str:
        """LLM Boundary 검증 프롬프트"""
        
        context_str = ""
        if context:
            if context.domain and context.domain != "General":
                context_str += f"도메인: {context.domain}\n"
            if context.region:
                context_str += f"지역: {context.region}\n"
        
        prompt = f"""추정값의 타당성을 검증하세요.

질문: {question}
추정값: {value:,.0f} {unit}
{context_str}
사용 공식: {formula}

검증 항목:

1. Hard Boundaries (절대 한계):
   - 물리적 한계 (불가능한 값)
   - 법적 한계 (법률 위반)
   - 논리적 한계 (부분 > 전체 등)

2. Soft Boundaries (참고 범위):
   - 통계적 범위 (일반적 범위)
   - 업계 관행
   - 경험적 상식

3. 상위/하위 개념:
   - 부분 < 전체
   - 세부 < 총합
   - 지역 < 국가

출력 형식 (YAML):
```yaml
hard_violations: []  # 절대 한계 위반 (있으면 리스트)
soft_warnings: []    # 참고 범위 이탈 (있으면 리스트)
recommended_range: [min, max]  # 권장 범위
reasoning: "판단 근거"
```

비현실적이면 violations에 이유를 명시하세요.
타당하면 빈 리스트를 반환하세요."""
        
        return prompt
    
    def _parse_boundary_response(self, llm_output: str) -> Dict:
        """LLM 응답 파싱"""
        import yaml
        import re
        
        try:
            # YAML 블록 추출
            yaml_match = re.search(r'```yaml\n(.*?)\n```', llm_output, re.DOTALL)
            
            if yaml_match:
                yaml_str = yaml_match.group(1)
            else:
                yaml_str = llm_output
            
            data = yaml.safe_load(yaml_str)
            
            return {
                'violations': data.get('hard_violations', []),
                'warnings': data.get('soft_warnings', []),
                'reasoning': data.get('reasoning', '')
            }
        
        except Exception as e:
            logger.error(f"LLM 응답 파싱 실패: {e}")
            return {'violations': [], 'warnings': []}


# ================================================================
# 싱글톤
# ================================================================

_boundary_validator_instance = None


def get_boundary_validator(llm_mode: str = "native") -> BoundaryValidator:
    """Boundary Validator 싱글톤"""
    global _boundary_validator_instance
    
    if _boundary_validator_instance is None:
        _boundary_validator_instance = BoundaryValidator(llm_mode)
    
    return _boundary_validator_instance

