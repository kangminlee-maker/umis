"""
Multi-Dimensional Confidence Calculator

schema_registry.yaml 준수:
- similarity (Vector 임베딩, 질적)
- coverage (분포 분석, 양적)
- validation (체크리스트, 검증)
- overall (0-1 종합 신뢰도)
- reasoning (판단 근거)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SimilarityScore:
    """Similarity 차원 (질적 평가)"""
    method: str  # "vector_embedding"
    value: float  # 0-1
    note: Optional[str] = None


@dataclass
class CoverageScore:
    """Coverage 차원 (양적 평가)"""
    method: str  # "distribution"
    value: float  # 0-1 (pattern strength)
    note: Optional[str] = None


@dataclass
class ValidationScore:
    """Validation 차원 (검증 여부)"""
    method: str  # "checklist"
    value: bool
    criteria_met: Optional[List[str]] = None


@dataclass
class ConfidenceResult:
    """Multi-Dimensional Confidence 결과"""
    similarity: SimilarityScore
    coverage: CoverageScore
    validation: ValidationScore
    overall: float  # 0-1
    reasoning: List[str]


class ConfidenceCalculator:
    """
    Multi-Dimensional Confidence 계산기
    
    schema_registry.yaml 기반:
    - similarity: 질적 평가 (best case similarity)
    - coverage: 양적 평가 (pattern strength)
    - validation: 검증 여부 (checklist)
    - overall: 종합 신뢰도 (rule-based)
    """
    
    def __init__(self):
        """초기화"""
        logger.info("ConfidenceCalculator initialized")
    
    def calculate(
        self,
        similarity_value: float,
        coverage_value: float,
        validation_passed: bool,
        similarity_note: Optional[str] = None,
        coverage_note: Optional[str] = None,
        validation_criteria: Optional[List[str]] = None
    ) -> ConfidenceResult:
        """
        Multi-Dimensional Confidence 계산
        
        Args:
            similarity_value: Vector similarity (0-1)
            coverage_value: Pattern strength (0-1)
            validation_passed: Validation check result
            similarity_note: Similarity 설명
            coverage_note: Coverage 설명
            validation_criteria: 충족된 검증 기준
        
        Returns:
            ConfidenceResult 객체
        """
        # 1. Similarity 객체
        similarity = SimilarityScore(
            method="vector_embedding",
            value=similarity_value,
            note=similarity_note
        )
        
        # 2. Coverage 객체
        coverage = CoverageScore(
            method="distribution",
            value=coverage_value,
            note=coverage_note
        )
        
        # 3. Validation 객체
        validation = ValidationScore(
            method="checklist",
            value=validation_passed,
            criteria_met=validation_criteria
        )
        
        # 4. Overall confidence (rule-based)
        overall = self._calculate_overall(
            similarity_value,
            coverage_value,
            validation_passed
        )
        
        # 5. Reasoning 생성
        reasoning = self._generate_reasoning(
            similarity, coverage, validation, overall
        )
        
        return ConfidenceResult(
            similarity=similarity,
            coverage=coverage,
            validation=validation,
            overall=overall,
            reasoning=reasoning
        )
    
    def _calculate_overall(
        self,
        similarity: float,
        coverage: float,
        validation: bool
    ) -> float:
        """
        Overall Confidence 계산 (Rule-based)
        
        schema_registry.yaml 규칙:
        - High (0.80-1.00): similarity >= 0.90 AND validation OR coverage >= 0.10
        - Medium (0.60-0.79): similarity >= 0.70 OR coverage >= 0.05
        - Low (0.00-0.59): 그 외
        
        Args:
            similarity: Vector similarity
            coverage: Pattern strength
            validation: Validation result
        
        Returns:
            Overall confidence (0-1)
        """
        # High confidence (0.80-1.00)
        if (similarity >= 0.90 and validation) or coverage >= 0.10:
            # Fine-tune within high range
            base = 0.80
            
            # Similarity bonus
            if similarity >= 0.95:
                base += 0.10
            elif similarity >= 0.90:
                base += 0.05
            
            # Coverage bonus
            if coverage >= 0.20:
                base += 0.05
            elif coverage >= 0.15:
                base += 0.03
            elif coverage >= 0.10:
                base += 0.02
            
            return min(base, 1.0)
        
        # Medium confidence (0.60-0.79)
        elif similarity >= 0.70 or coverage >= 0.05:
            base = 0.65
            
            # Similarity contribution
            if similarity >= 0.85:
                base += 0.12
            elif similarity >= 0.75:
                base += 0.08
            elif similarity >= 0.70:
                base += 0.04
            
            # Coverage contribution
            if coverage >= 0.08:
                base += 0.07
            elif coverage >= 0.05:
                base += 0.03
            
            # Validation bonus
            if validation:
                base += 0.05
            
            return min(base, 0.79)
        
        # Low confidence (0.00-0.59)
        else:
            base = 0.40
            
            # Some similarity
            if similarity >= 0.60:
                base += 0.10
            elif similarity >= 0.50:
                base += 0.05
            
            # Some coverage
            if coverage >= 0.03:
                base += 0.05
            
            # Validation helps
            if validation:
                base += 0.08
            
            return min(base, 0.59)
    
    def _generate_reasoning(
        self,
        similarity: SimilarityScore,
        coverage: CoverageScore,
        validation: ValidationScore,
        overall: float
    ) -> List[str]:
        """
        Reasoning 자동 생성
        
        Args:
            similarity: Similarity 결과
            coverage: Coverage 결과
            validation: Validation 결과
            overall: Overall confidence
        
        Returns:
            Reasoning 문자열 리스트
        """
        reasoning = []
        
        # 1. Similarity reasoning
        if similarity.note:
            reasoning.append(similarity.note)
        else:
            if similarity.value >= 0.90:
                reasoning.append(f"Excellent similarity {similarity.value:.2f}")
            elif similarity.value >= 0.70:
                reasoning.append(f"Good similarity {similarity.value:.2f}")
            else:
                reasoning.append(f"Moderate similarity {similarity.value:.2f}")
        
        # 2. Coverage reasoning
        if coverage.note:
            reasoning.append(coverage.note)
        else:
            coverage_pct = coverage.value * 100
            if coverage.value >= 0.10:
                reasoning.append(f"{coverage_pct:.0f}% coverage - strong pattern")
            elif coverage.value >= 0.05:
                reasoning.append(f"{coverage_pct:.0f}% coverage - moderate")
            else:
                reasoning.append(f"{coverage_pct:.0f}% coverage - emerging")
        
        # 3. Validation reasoning
        if validation.value:
            if validation.criteria_met:
                criteria_str = ", ".join(validation.criteria_met)
                reasoning.append(f"Validated: {criteria_str}")
            else:
                reasoning.append("Validator verified")
        else:
            reasoning.append("Not yet validated")
        
        return reasoning
    
    def calculate_from_dict(self, confidence_dict: Dict[str, Any]) -> ConfidenceResult:
        """
        Dictionary에서 Confidence 계산
        
        Args:
            confidence_dict: Confidence 데이터 (YAML에서 로드)
        
        Returns:
            ConfidenceResult 객체
        """
        similarity_data = confidence_dict.get('similarity', {})
        coverage_data = confidence_dict.get('coverage', {})
        validation_data = confidence_dict.get('validation', {})
        
        return self.calculate(
            similarity_value=similarity_data.get('value', 0.5),
            coverage_value=coverage_data.get('value', 0.0),
            validation_passed=validation_data.get('value', False),
            similarity_note=similarity_data.get('note'),
            coverage_note=coverage_data.get('note'),
            validation_criteria=validation_data.get('criteria_met')
        )
    
    def to_dict(self, result: ConfidenceResult) -> Dict[str, Any]:
        """
        ConfidenceResult를 Dictionary로 변환 (Neo4j 저장용)
        
        Args:
            result: ConfidenceResult 객체
        
        Returns:
            Dictionary
        """
        return {
            'similarity': {
                'method': result.similarity.method,
                'value': result.similarity.value,
                'note': result.similarity.note
            },
            'coverage': {
                'method': result.coverage.method,
                'value': result.coverage.value,
                'note': result.coverage.note
            },
            'validation': {
                'method': result.validation.method,
                'value': result.validation.value,
                'criteria_met': result.validation.criteria_met
            },
            'overall': result.overall,
            'reasoning': result.reasoning
        }
    
    def classify_confidence(self, overall: float) -> str:
        """
        Overall confidence를 High/Medium/Low로 분류
        
        Args:
            overall: Overall confidence (0-1)
        
        Returns:
            "high" | "medium" | "low"
        """
        if overall >= 0.80:
            return "high"
        elif overall >= 0.60:
            return "medium"
        else:
            return "low"


def calculate_confidence(
    similarity: float,
    coverage: float,
    validation: bool,
    **kwargs
) -> ConfidenceResult:
    """
    편의 함수: Confidence 빠르게 계산
    
    Args:
        similarity: Vector similarity (0-1)
        coverage: Pattern strength (0-1)
        validation: Validation passed
        **kwargs: 추가 인자 (note, criteria)
    
    Returns:
        ConfidenceResult
    """
    calculator = ConfidenceCalculator()
    return calculator.calculate(
        similarity_value=similarity,
        coverage_value=coverage,
        validation_passed=validation,
        **kwargs
    )


# 예시 사용
if __name__ == "__main__":
    # Example 1: High confidence
    result1 = calculate_confidence(
        similarity=0.92,
        coverage=0.15,
        validation=True,
        similarity_note="Amazon Prime 사례와 매우 유사",
        coverage_note="전체 플랫폼의 15%가 구독 모델 채택"
    )
    
    print(f"\nExample 1: Platform + Subscription")
    print(f"  Overall: {result1.overall:.2f} ({ConfidenceCalculator().classify_confidence(result1.overall)})")
    print(f"  Reasoning:")
    for r in result1.reasoning:
        print(f"    - {r}")
    
    # Example 2: Medium confidence
    result2 = calculate_confidence(
        similarity=0.75,
        coverage=0.06,
        validation=True
    )
    
    print(f"\nExample 2: Medium Confidence")
    print(f"  Overall: {result2.overall:.2f} ({ConfidenceCalculator().classify_confidence(result2.overall)})")
    print(f"  Reasoning:")
    for r in result2.reasoning:
        print(f"    - {r}")
    
    # Example 3: Low confidence
    result3 = calculate_confidence(
        similarity=0.55,
        coverage=0.03,
        validation=False
    )
    
    print(f"\nExample 3: Low Confidence")
    print(f"  Overall: {result3.overall:.2f} ({ConfidenceCalculator().classify_confidence(result3.overall)})")
    print(f"  Reasoning:")
    for r in result3.reasoning:
        print(f"    - {r}")

