"""
Guestimation Framework - 비교 가능성 검증 및 추정 로직
v1.0 - 2025-11-04

핵심 원칙:
  1. 비교 가능성이 전제조건
  2. 논리 > 데이터
  3. 명시적 기각
  4. 보수적 추정
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ComparabilityScore(Enum):
    """비교 가능성 점수"""
    IDENTICAL = 4  # 완전 동일
    HIGHLY_SIMILAR = 3  # 매우 유사 (비교 가능)
    SOMEWHAT_SIMILAR = 2  # 약간 유사 (참고만)
    DIFFERENT = 1  # 다름 (기각)
    INCOMPARABLE = 0  # 비교 불가


@dataclass
class BenchmarkCandidate:
    """
    RAG에서 검색된 벤치마크 후보
    
    Attributes:
        name: 벤치마크 이름
        value: 값
        product_type: 제품 유형 (물리적/디지털/서비스)
        consumer_type: 소비 주체 (B2C/B2B/B2G)
        price: 가격
        is_essential: 필수재 여부
        source: 출처
        context: 추가 맥락
    """
    name: str
    value: float
    product_type: str = "unknown"  # physical, digital, service
    consumer_type: str = "unknown"  # B2C, B2B, B2G
    price: Optional[float] = None
    is_essential: bool = False  # True: 필수재, False: 선택재
    source: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComparabilityResult:
    """
    비교 가능성 검증 결과
    
    Attributes:
        candidate: 검증 대상 벤치마크
        score: 비교 가능성 점수 (0-4)
        decision: 채택/기각 판단
        reasons: 판단 근거 리스트
        details: 세부 평가
    """
    candidate: BenchmarkCandidate
    score: int  # 0-4
    decision: str  # adopt, reference, reject
    reasons: List[str] = field(default_factory=list)
    details: Dict[str, str] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"ComparabilityResult({self.candidate.name}: {self.score}/4, {self.decision})"


class GuestimationEngine:
    """
    Guestimation 엔진
    
    기능:
      - 비교 가능성 자동 검증
      - 후보 데이터 필터링
      - 추정 로직 지원
    """
    
    def __init__(self):
        """초기화"""
        self.comparability_threshold = 3  # 4점 만점에 3점 이상
    
    def check_comparability(
        self,
        target: BenchmarkCandidate,
        candidate: BenchmarkCandidate
    ) -> ComparabilityResult:
        """
        비교 가능성 4대 기준 체크
        
        Args:
            target: 추정 대상
            candidate: 비교 후보
        
        Returns:
            ComparabilityResult
        """
        
        score = 0
        reasons = []
        details = {}
        
        # 1. 제품/서비스 속성
        if target.product_type == candidate.product_type:
            score += 1
            reasons.append("제품 속성 동일")
            details['product_type'] = "동일 ✓"
        elif self._is_similar_product_type(target.product_type, candidate.product_type):
            score += 0.5
            reasons.append("제품 속성 유사")
            details['product_type'] = "유사 △"
        else:
            details['product_type'] = f"다름 ✗ ({target.product_type} vs {candidate.product_type})"
        
        # 2. 소비 주체
        if target.consumer_type == candidate.consumer_type:
            score += 1
            reasons.append("소비 주체 동일")
            details['consumer_type'] = "동일 ✓"
        else:
            details['consumer_type'] = f"다름 ✗ ({target.consumer_type} vs {candidate.consumer_type})"
        
        # 3. 가격대 (±3배 이내)
        if target.price and candidate.price:
            price_ratio = max(target.price, candidate.price) / min(target.price, candidate.price)
            if price_ratio <= 1.5:
                score += 1
                reasons.append("가격대 동일")
                details['price'] = "동일 ✓"
            elif price_ratio <= 3:
                score += 0.5
                reasons.append("가격대 유사")
                details['price'] = f"유사 △ ({price_ratio:.1f}배)"
            else:
                details['price'] = f"다름 ✗ ({price_ratio:.1f}배 차이)"
        else:
            details['price'] = "정보 없음"
        
        # 4. 구매 맥락 (필수재 vs 선택재)
        if target.is_essential == candidate.is_essential:
            score += 1
            reasons.append("구매 맥락 동일")
            details['purchase_context'] = "동일 ✓"
        else:
            essential_str = "필수재" if candidate.is_essential else "선택재"
            target_str = "필수재" if target.is_essential else "선택재"
            details['purchase_context'] = f"다름 ✗ ({target_str} vs {essential_str})"
        
        # 판단
        if score >= 3.5:
            decision = "adopt"  # 주 비교군
        elif score >= 2.5:
            decision = "reference"  # 참고용
        else:
            decision = "reject"  # 기각
        
        return ComparabilityResult(
            candidate=candidate,
            score=int(score),
            decision=decision,
            reasons=reasons,
            details=details
        )
    
    def _is_similar_product_type(self, type1: str, type2: str) -> bool:
        """
        제품 유형 유사성 판단
        
        Args:
            type1, type2: 제품 유형
        
        Returns:
            유사 여부
        """
        similar_groups = [
            {'physical', 'hardware', 'device'},
            {'digital', 'software', 'app'},
            {'service', 'platform'}
        ]
        
        for group in similar_groups:
            if type1 in group and type2 in group:
                return True
        
        return False
    
    def filter_candidates(
        self,
        target: BenchmarkCandidate,
        candidates: List[BenchmarkCandidate]
    ) -> Dict[str, List[ComparabilityResult]]:
        """
        후보 데이터 필터링 (비교 가능성 기준)
        
        Args:
            target: 추정 대상
            candidates: 후보 목록
        
        Returns:
            {
                'adopt': [...],      # 채택 (score >= 3.5)
                'reference': [...],  # 참고 (score >= 2.5)
                'reject': [...]      # 기각 (score < 2.5)
            }
        """
        
        results = {
            'adopt': [],
            'reference': [],
            'reject': []
        }
        
        for candidate in candidates:
            result = self.check_comparability(target, candidate)
            results[result.decision].append(result)
        
        return results
    
    def generate_estimation_doc(
        self,
        est_id: str,
        description: str,
        target: BenchmarkCandidate,
        candidates: List[BenchmarkCandidate],
        logic_steps: List[str],
        final_value: float,
        confidence: str = 'Medium',
        error_range: str = '±20%'
    ) -> Dict[str, Any]:
        """
        추정 문서 자동 생성
        
        Args:
            est_id: EST_ID
            description: 추정 항목 설명
            target: 추정 대상
            candidates: RAG 검색 결과
            logic_steps: 추정 논리 단계
            final_value: 최종 추정값
            confidence: 신뢰도
            error_range: 오차 범위
        
        Returns:
            Estimation Details 7개 섹션 데이터
        """
        
        # 비교 가능성 검증
        filtered = self.filter_candidates(target, candidates)
        
        # Base Data 구성
        base_data = []
        for result in filtered['adopt']:
            base_data.append({
                'name': result.candidate.name,
                'value': result.candidate.value,
                'source': result.candidate.source
            })
        
        # 기각 이유 문서화
        rejected_info = []
        for result in filtered['reject']:
            rejected_info.append(
                f"{result.candidate.name}: {', '.join(result.details.values())}"
            )
        
        # 문서 생성
        return {
            'id': est_id,
            'description': description,
            'value': final_value,
            'confidence': confidence,
            'error_range': error_range,
            'used_in': '',  # 나중에 채움
            
            # 7개 섹션
            'reason': '직접 데이터 없음',
            'base_data': base_data,
            'logic_steps': logic_steps,
            'calculation': f"최종: {final_value}",
            'verification': f"범위 체크 필요 (±{error_range})",
            'alternatives': [f"기각: {r}" for r in rejected_info[:3]],
            
            # 메타데이터
            'comparability_check': {
                'adopted': len(filtered['adopt']),
                'referenced': len(filtered['reference']),
                'rejected': len(filtered['reject']),
                'total_candidates': len(candidates)
            }
        }


# 유틸리티 함수

def create_target_profile(
    name: str,
    product_type: str,
    consumer_type: str,
    price: float,
    is_essential: bool = False
) -> BenchmarkCandidate:
    """
    타겟 프로필 생성 (추정 대상)
    
    Args:
        name: 이름
        product_type: 제품 유형 (physical, digital, service)
        consumer_type: 소비 주체 (B2C, B2B, B2G)
        price: 가격
        is_essential: 필수재 여부
    
    Returns:
        BenchmarkCandidate
    """
    return BenchmarkCandidate(
        name=name,
        value=0,  # 추정할 값
        product_type=product_type,
        consumer_type=consumer_type,
        price=price,
        is_essential=is_essential
    )


# 테스트 예시

if __name__ == '__main__':
    # 타겟: 피아노 구독 전환율
    target = create_target_profile(
        name="피아노 구독 서비스",
        product_type="physical",
        consumer_type="B2C",
        price=50000,
        is_essential=False
    )
    
    # 후보 데이터 (RAG 검색 결과)
    candidates = [
        BenchmarkCandidate(
            name="정수기 구독",
            value=0.25,
            product_type="physical",
            consumer_type="B2C",
            price=40000,
            is_essential=True,
            source="SRC_20250104_001"
        ),
        BenchmarkCandidate(
            name="공기청정기 렌탈",
            value=0.18,
            product_type="physical",
            consumer_type="B2C",
            price=45000,
            is_essential=False,
            source="SRC_20250104_002"
        ),
        BenchmarkCandidate(
            name="음악 앱 구독",
            value=0.30,
            product_type="digital",
            consumer_type="B2C",
            price=10000,
            is_essential=False,
            source="SRC_20250104_003"
        ),
        BenchmarkCandidate(
            name="SaaS B2B",
            value=0.04,
            product_type="software",
            consumer_type="B2B",
            price=200000,
            is_essential=False,
            source="SRC_20250104_004"
        )
    ]
    
    # 비교 가능성 검증
    engine = GuestimationEngine()
    filtered = engine.filter_candidates(target, candidates)
    
    print("\n" + "="*70)
    print("Guestimation Framework - 비교 가능성 검증")
    print("="*70)
    
    print(f"\n타겟: {target.name}")
    print(f"  - 제품: {target.product_type}")
    print(f"  - 소비자: {target.consumer_type}")
    print(f"  - 가격: {target.price:,}원")
    print(f"  - 필수재: {target.is_essential}")
    
    print(f"\n후보 데이터: {len(candidates)}개")
    
    print(f"\n✅ 채택 (주 비교군): {len(filtered['adopt'])}개")
    for result in filtered['adopt']:
        print(f"  - {result.candidate.name}: {result.candidate.value*100:.0f}% (score: {result.score}/4)")
        print(f"    이유: {', '.join(result.reasons)}")
    
    print(f"\n△ 참고용: {len(filtered['reference'])}개")
    for result in filtered['reference']:
        print(f"  - {result.candidate.name}: {result.candidate.value*100:.0f}% (score: {result.score}/4)")
    
    print(f"\n❌ 기각: {len(filtered['reject'])}개")
    for result in filtered['reject']:
        print(f"  - {result.candidate.name}: {result.candidate.value*100:.0f}%")
        print(f"    이유: {list(result.details.values())[0]}")
    
    print("\n" + "="*70)
    print("✅ 비교 가능성 검증 완료")
    print("="*70)

