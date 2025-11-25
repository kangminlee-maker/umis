"""
Fermi Model Search Engine
v1.0 - 2025-11-05

Fermi 추정의 본질 구현: "논리의 퍼즐 맞추기"
- 모형 만들기 (Model Building)
- Bottom-up ⟷ Top-down 반복
- 재귀 구조 (변수도 Guestimation 대상, max depth 4)

기반: config/fermi_model_search.yaml
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import re
import os


@dataclass
class FermiVariable:
    """모형의 변수"""
    name: str
    value: Optional[float] = None
    available: bool = False
    source: Optional[str] = None  # "project", "recursive", "estimated"
    confidence: float = 0.0
    depth: int = 0  # 재귀 깊이


@dataclass
class FermiModel:
    """Fermi 모형"""
    id: str
    formula: str  # "market = customers × rate × arpu × 12"
    description: str
    variables: List[FermiVariable]
    
    def variable_count(self) -> int:
        """변수 개수 (상수 제외)"""
        return len([v for v in self.variables if not v.available or v.value is None])
    
    def unknown_count(self) -> int:
        """Unknown 변수 개수"""
        return len([v for v in self.variables if not v.available])
    
    def is_feasible(self) -> bool:
        """모든 변수가 채워졌는가?"""
        return all(v.value is not None for v in self.variables)
    
    def calculate(self) -> float:
        """모형 계산 (eval)"""
        # 변수명 → 값 매핑
        context = {v.name: v.value for v in self.variables}
        
        # 수식 파싱 (= 제거)
        formula = self.formula
        if '=' in formula:
            # "result = A × B" → "A × B"
            formula = formula.split('=')[1].strip()
        
        # 수식 평가
        try:
            # × → * 변환
            formula = formula.replace('×', '*').replace('÷', '/')
            result = eval(formula, {"__builtins__": {}}, context)
            return float(result)
        except Exception as e:
            # 단일 변수인 경우
            if formula in context:
                return float(context[formula])
            raise ValueError(f"모형 계산 실패: {e}\nFormula: {formula}\nContext: {context}")


@dataclass
class FermiResult:
    """Fermi 추정 결과"""
    question: str
    value: Optional[float] = None
    
    # Fermi 핵심!
    model: Optional[FermiModel] = None
    components: List[FermiVariable] = field(default_factory=list)
    calculation_steps: List[str] = field(default_factory=list)
    
    # 메타데이터
    confidence: float = 0.0
    max_depth_used: int = 0
    total_models_tried: int = 0
    selection_reason: str = ""
    
    # 추적
    logic_trace: List[str] = field(default_factory=list)
    alternative_models: List[Dict] = field(default_factory=list)


class FermiModelSearch:
    """
    Fermi Model Search Engine
    
    핵심: 가용한 숫자(Bottom-up)와 개념 분해(Top-down)를 반복하며
         "채울 수 있는 모형" 찾기 (논리의 퍼즐)
    
    Usage:
        fermi = FermiModelSearch()
        result = fermi.estimate("음식점 SaaS 시장 규모는?")
    """
    
    MAX_DEPTH = 4
    MAX_VARIABLES = 6
    
    def __init__(self, project_context: Optional[Dict] = None):
        """
        초기화
        
        Args:
            project_context: 프로젝트 데이터 (확정된 값들)
        """
        self.project_context = project_context or {}
        self.call_stack = []  # 순환 감지용
        
        # LLM 모드
        import umis_rag
        self.llm_mode = umis_rag.LLM_MODE
    
    def estimate(
        self,
        question: str,
        depth: int = 0
    ) -> FermiResult:
        """
        Fermi 추정 (재귀 함수)
        
        Args:
            question: 추정 질문
            depth: 재귀 깊이 (0-4)
        
        Returns:
            FermiResult
        """
        
        result = FermiResult(question=question)
        result.logic_trace.append(f"[Depth {depth}] 질문: {question}")
        
        # Base Case 1: Depth 한계
        if depth >= self.MAX_DEPTH:
            result.logic_trace.append(f"⚠️ Depth {depth} 도달 → 추정값 사용")
            result.value = self._get_estimated_value(question)
            result.confidence = 0.4
            result.max_depth_used = depth
            return result
        
        # Base Case 2: 순환 감지
        if self._detect_circular(question):
            result.logic_trace.append(f"🚨 순환 감지: {question} → 중단")
            result.value = self._get_estimated_value(question)
            result.confidence = 0.3
            return result
        
        # Call stack 추가
        self.call_stack.append(question)
        
        try:
            # Phase 1: 초기 스캔
            available, unknown = self._initial_scan(question)
            result.logic_trace.append(f"Phase 1: 가용 {len(available)}개, Unknown {len(unknown)}개")
            
            # Phase 2: 모형 생성
            models = self._generate_models(question, available, unknown)
            result.total_models_tried = len(models)
            result.logic_trace.append(f"Phase 2: {len(models)}개 모형 생성")
            
            if not models:
                # 모형 불필요 (단순 질문)
                result.logic_trace.append("→ 단순 질문 (모형 불필요)")
                result.value = self._get_estimated_value(question)
                result.confidence = 0.5
                result.max_depth_used = depth
                return result
            
            # Phase 3: 실행 가능성 체크
            feasible_models = []
            for model in models:
                feasibility = self._check_feasibility(model, depth)
                
                if feasibility['feasible']:
                    feasible_models.append((model, feasibility))
            
            # Phase 4: 최선 모형 실행
            if feasible_models:
                best_model, best_values = self._select_best_model(feasible_models)
                
                # 재조립
                result.model = best_model
                result.components = best_model.variables
                result.value = best_model.calculate()
                result.confidence = self._calculate_confidence(best_model.variables)
                result.max_depth_used = max((v.depth for v in best_model.variables), default=depth)
                result.selection_reason = f"Unknown {best_model.unknown_count()}개, 점수 최고"
                
                # 계산 단계 기록
                result.calculation_steps = self._trace_calculation(best_model)
                result.logic_trace.append(f"Phase 4: {best_model.id} 실행 → {result.value}")
                
                return result
            else:
                # 모든 모형 실행 불가
                result.logic_trace.append("❌ 모든 모형 실행 불가")
                result.value = self._get_estimated_value(question)
                result.confidence = 0.3
                result.max_depth_used = depth
                return result
        
        finally:
            # Call stack 제거
            if self.call_stack and self.call_stack[-1] == question:
                self.call_stack.pop()
    
    # =========================================
    # Phase 1: 초기 스캔
    # =========================================
    
    def _initial_scan(self, question: str) -> Tuple[List[str], List[str]]:
        """
        가용 데이터 파악
        
        Returns:
            (available_data, unknown_data)
        """
        available = []
        unknown = []
        
        # Project context 확인
        for key in self.project_context.keys():
            available.append(key)
        
        # 향후: LLM Quick scan, 명백한 출처 등
        
        return available, unknown
    
    # =========================================
    # Phase 2: 모형 생성 (LLM)
    # =========================================
    
    def _generate_models(
        self,
        question: str,
        available: List[str],
        unknown: List[str]
    ) -> List[FermiModel]:
        """
        LLM으로 후보 모형 생성
        
        Args:
            question: 질문
            available: 가용 데이터
            unknown: 모르는 데이터
        
        Returns:
            3-5개 후보 모형
        """
        
        # LLM 모드 체크
        if self.llm_mode == 'cursor':
            # Cursor: 사용자에게 안내
            print(f"\n💡 [Fermi Phase 2] 모형 생성 필요")
            print(f"   질문: {question}")
            print(f"   가용 데이터: {available}")
            print(f"   → Cursor에서 LLM에게 모형 3-5개 요청하세요")
            print(f"   → 각 모형의 formula와 variables를 입력하세요")
            
            # 현재: 기본 모형 사용 (테스트용)
            return self._get_default_models(question)
        
        else:
            # External LLM: OpenAI API 호출
            return self._generate_models_with_llm(question, available, unknown)
    
    def _generate_models_with_llm(
        self,
        question: str,
        available: List[str],
        unknown: List[str]
    ) -> List[FermiModel]:
        """LLM API로 모형 생성"""
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = f"""질문: {question}

가용한 데이터:
{available}

임무:
1. 이 질문에 답하기 위한 계산 모형을 3-5개 제시하세요.
2. 각 모형은 다른 분해 방식을 사용하세요.
3. 가용 데이터를 최대한 활용하세요.
4. Unknown 변수는 최소화하세요.
5. 변수는 2-6개로 제한하세요.

출력 형식:
Model 1:
  formula: "목표 = A × B × C"
  variables: ["A", "B", "C"]
  description: "설명"

Model 2:
  ...
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 파싱 (간소화)
            return self._parse_llm_models(response.choices[0].message.content)
        
        except Exception as e:
            print(f"⚠️ LLM 모형 생성 실패: {e}")
            return self._get_default_models(question)
    
    def _get_default_models(self, question: str) -> List[FermiModel]:
        """
        기본 모형 템플릿 (LLM 없을 때)
        
        비즈니스 지표별 여러 모형 제공
        """
        
        # 시장 규모 (TAM, SAM, SOM)
        if "시장" in question or "TAM" in question or "SAM" in question:
            return [
                FermiModel(
                    id="MODEL_001",
                    formula="market = customers * adoption_rate * arpu * 12",
                    description="시장 = 고객 수 × 도입률 × ARPU × 12",
                    variables=[
                        FermiVariable(name="customers", available=False),
                        FermiVariable(name="adoption_rate", available=False),
                        FermiVariable(name="arpu", available=False),
                        FermiVariable(name="12", value=12, available=True, confidence=1.0),
                    ]
                ),
                FermiModel(
                    id="MODEL_002",
                    formula="market = customers * digital_rate * conversion_rate * arpu * 12",
                    description="시장 = 고객 × 디지털율 × 전환율 × ARPU × 12",
                    variables=[
                        FermiVariable(name="customers", available=False),
                        FermiVariable(name="digital_rate", available=False),
                        FermiVariable(name="conversion_rate", available=False),
                        FermiVariable(name="arpu", available=False),
                        FermiVariable(name="12", value=12, available=True, confidence=1.0),
                    ]
                ),
            ]
        
        # LTV (고객 생애 가치)
        elif "LTV" in question or "생애가치" in question or "고객가치" in question:
            return [
                FermiModel(
                    id="MODEL_LTV_001",
                    formula="ltv = arpu * (1 / churn)",
                    description="LTV = ARPU / Churn Rate",
                    variables=[
                        FermiVariable(name="arpu", available=False),
                        FermiVariable(name="churn", available=False),
                    ]
                ),
                FermiModel(
                    id="MODEL_LTV_002",
                    formula="ltv = arpu * average_lifetime",
                    description="LTV = ARPU × 평균 생애 (개월)",
                    variables=[
                        FermiVariable(name="arpu", available=False),
                        FermiVariable(name="average_lifetime", available=False),
                    ]
                ),
            ]
        
        # CAC (고객 획득 비용)
        elif "CAC" in question or "획득.*비용" in question or "획득.*단가" in question:
            return [
                FermiModel(
                    id="MODEL_CAC_001",
                    formula="cac = marketing_cost / new_customers",
                    description="CAC = 마케팅 비용 / 신규 고객",
                    variables=[
                        FermiVariable(name="marketing_cost", available=False),
                        FermiVariable(name="new_customers", available=False),
                    ]
                ),
                FermiModel(
                    id="MODEL_CAC_002",
                    formula="cac = cpc * (1 / cvr)",
                    description="CAC = CPC / CVR",
                    variables=[
                        FermiVariable(name="cpc", available=False),
                        FermiVariable(name="cvr", available=False),
                    ]
                ),
            ]
        
        # Unit Economics (LTV/CAC)
        elif "LTV/CAC" in question or "Unit.*Economics" in question:
            return [
                FermiModel(
                    id="MODEL_UE_001",
                    formula="ratio = ltv / cac",
                    description="비율 = LTV / CAC",
                    variables=[
                        FermiVariable(name="ltv", available=False),
                        FermiVariable(name="cac", available=False),
                    ]
                ),
            ]
        
        # Churn Rate (해지율)
        elif "churn" in question.lower() or "해지율" in question or "이탈률" in question:
            return [
                FermiModel(
                    id="MODEL_CHURN_001",
                    formula="churn = churned / total",
                    description="Churn = 해지 고객 / 전체 고객",
                    variables=[
                        FermiVariable(name="churned", available=False),
                        FermiVariable(name="total", available=False),
                    ]
                ),
            ]
        
        # Conversion Rate (전환율)
        elif "전환율" in question or "conversion" in question.lower():
            return [
                FermiModel(
                    id="MODEL_CVR_001",
                    formula="cvr = converted / total",
                    description="전환율 = 전환 고객 / 전체 방문자",
                    variables=[
                        FermiVariable(name="converted", available=False),
                        FermiVariable(name="total", available=False),
                    ]
                ),
            ]
        
        # ARPU (상세 분해)
        elif "ARPU" in question or "객단가" in question:
            return [
                FermiModel(
                    id="MODEL_ARPU_001",
                    formula="arpu = base_fee + extra_fee",
                    description="ARPU = 기본료 + 추가료",
                    variables=[
                        FermiVariable(name="base_fee", available=False),
                        FermiVariable(name="extra_fee", available=False),
                    ]
                ),
                FermiModel(
                    id="MODEL_ARPU_002",
                    formula="arpu = (tier1_price * tier1_ratio) + (tier2_price * tier2_ratio)",
                    description="ARPU = Tier별 가중 평균",
                    variables=[
                        FermiVariable(name="tier1_price", available=False),
                        FermiVariable(name="tier1_ratio", available=False),
                        FermiVariable(name="tier2_price", available=False),
                        FermiVariable(name="tier2_ratio", available=False),
                    ]
                ),
            ]
        
        # 성장률
        elif "성장률" in question or "growth" in question.lower():
            return [
                FermiModel(
                    id="MODEL_GROWTH_001",
                    formula="growth = (this_year - last_year) / last_year",
                    description="성장률 = (올해 - 작년) / 작년",
                    variables=[
                        FermiVariable(name="this_year", available=False),
                        FermiVariable(name="last_year", available=False),
                    ]
                ),
            ]
        
        # 기본 모형 (단순 질문 - 모형 불필요)
        else:
            return []
    
    def _parse_llm_models(self, llm_response: str) -> List[FermiModel]:
        """LLM 응답 파싱 (간소화)"""
        # 실제 구현은 정교한 파싱 필요
        return self._get_default_models("")
    
    def _extract_var_name(self, question: str) -> str:
        """질문에서 변수명 추출"""
        # "ARPU는?" → "arpu"
        # "고객 수는?" → "customers"
        
        if "ARPU" in question:
            return "arpu"
        elif "고객" in question:
            return "customers"
        elif "churn" in question.lower() or "해지" in question:
            return "churn"
        else:
            return "value"
    
    # =========================================
    # Phase 3: 실행 가능성 체크
    # =========================================
    
    def _check_feasibility(
        self,
        model: FermiModel,
        parent_depth: int
    ) -> Dict[str, Any]:
        """
        모형 실행 가능성 체크
        
        각 변수를 채울 수 있는지 확인 (재귀)
        
        Returns:
            {
                'feasible': bool,
                'filled_values': Dict,
                'max_depth': int
            }
        """
        
        filled_values = {}
        max_depth = parent_depth
        
        for var in model.variables:
            # Available → 즉시 사용
            if var.available and var.value is not None:
                filled_values[var.name] = var.value
                var.source = "available"
                var.depth = parent_depth
                continue
            
            # Project context 확인
            if var.name in self.project_context:
                var.value = self.project_context[var.name]
                var.available = True
                var.source = "project"
                var.confidence = 1.0
                var.depth = parent_depth
                filled_values[var.name] = var.value
                continue
            
            # Unknown → 즉시 재귀 호출!
            if parent_depth + 1 < self.MAX_DEPTH:
                # 재귀 호출
                recursive_question = f"{var.name}은(는)?"
                recursive_result = self.estimate(
                    recursive_question,
                    depth=parent_depth + 1
                )
                
                if recursive_result.value is not None:
                    var.value = recursive_result.value
                    var.available = True
                    var.source = "recursive"
                    var.confidence = recursive_result.confidence
                    var.depth = recursive_result.max_depth_used
                    filled_values[var.name] = var.value
                    max_depth = max(max_depth, recursive_result.max_depth_used)
                else:
                    # 재귀도 실패
                    var.value = self._get_estimated_value(recursive_question)
                    var.available = True
                    var.source = "estimated"
                    var.confidence = 0.3
                    var.depth = parent_depth + 1
                    filled_values[var.name] = var.value
            else:
                # Depth 한계 → 추정값
                var.value = self._get_estimated_value(f"{var.name}은?")
                var.available = True
                var.source = "estimated"
                var.confidence = 0.3
                var.depth = parent_depth + 1
                filled_values[var.name] = var.value
        
        return {
            'feasible': len(filled_values) == len(model.variables),
            'filled_values': filled_values,
            'max_depth': max_depth
        }
    
    def _select_best_model(
        self,
        feasible_models: List[Tuple[FermiModel, Dict]]
    ) -> Tuple[FermiModel, Dict]:
        """
        최선의 모형 선택
        
        기준:
        1. Unknown 개수 (50%)
        2. Confidence (30%)
        3. 복잡도 (20%)
        4. Depth (10% 보너스)
        """
        
        scored = []
        
        for model, feasibility in feasible_models:
            # 점수 계산
            unknown_score = self._score_unknown(model)
            confidence_score = self._calculate_confidence(model.variables)
            complexity_score = self._score_complexity(model.variable_count())
            depth_score = self._score_depth(feasibility['max_depth'])
            
            total_score = (
                unknown_score * 0.5 +
                confidence_score * 0.3 +
                complexity_score * 0.2 +
                depth_score * 0.1
            )
            
            scored.append((model, feasibility, total_score))
        
        # 최고 점수 선택
        scored.sort(key=lambda x: x[2], reverse=True)
        best = scored[0]
        
        return best[0], best[1]
    
    def _score_unknown(self, model: FermiModel) -> float:
        """Unknown 개수 점수"""
        unknown = model.unknown_count()
        total = model.variable_count()
        
        if total == 0:
            return 1.0
        
        return (total - unknown) / total
    
    def _score_complexity(self, var_count: int) -> float:
        """복잡도 점수 (2-6개)"""
        scores = {
            1: 1.0,
            2: 1.0,
            3: 0.9,
            4: 0.7,
            5: 0.5,
            6: 0.3,
        }
        return scores.get(var_count, 0.0)
    
    def _score_depth(self, depth: int) -> float:
        """Depth 점수"""
        scores = {
            0: 1.0,
            1: 0.8,
            2: 0.6,
            3: 0.4,
            4: 0.2,
        }
        return scores.get(depth, 0.0)
    
    def _calculate_confidence(self, variables: List[FermiVariable]) -> float:
        """변수들의 confidence 조합 (geometric mean)"""
        if not variables:
            return 0.0
        
        confidences = [v.confidence for v in variables if v.confidence > 0]
        
        if not confidences:
            return 0.5
        
        # Geometric mean
        product = 1.0
        for c in confidences:
            product *= c
        
        return product ** (1 / len(confidences))
    
    def _trace_calculation(self, model: FermiModel) -> List[str]:
        """계산 단계 추적"""
        steps = []
        steps.append(f"모형: {model.formula}")
        
        for var in model.variables:
            steps.append(f"  {var.name} = {var.value} ({var.source})")
        
        result = model.calculate()
        steps.append(f"결과: {result}")
        
        return steps
    
    # =========================================
    # 유틸리티
    # =========================================
    
    def _detect_circular(self, question: str) -> bool:
        """순환 의존성 감지"""
        return question in self.call_stack
    
    def _get_estimated_value(self, question: str) -> float:
        """
        추정값 반환 (Fallback)
        
        향후: Layer 6 (통계 기본값) 등 활용
        현재: 간단한 기본값
        """
        
        # 간단한 기본값 (업계 평균)
        if "arpu" in question.lower():
            return 80000  # 8만원
        elif "churn" in question.lower() or "해지" in question:
            return 0.05  # 5%
        elif "전환" in question or "conversion" in question.lower():
            return 0.10  # 10%
        elif "도입" in question:
            return 0.20  # 20%
        elif "고객" in question or "customers" in question.lower():
            return 100000  # 10만
        else:
            return 1.0  # 기본값


# =========================================
# 편의 함수
# =========================================

def fermi_estimate(
    question: str,
    project_context: Optional[Dict] = None
) -> FermiResult:
    """
    빠른 Fermi 추정
    
    Usage:
        result = fermi_estimate("음식점 SaaS 시장은?")
    """
    fermi = FermiModelSearch(project_context=project_context)
    return fermi.estimate(question)

