"""
Multi-Layer Guestimation Engine
v2.0 - 2025-11-05

8개 데이터 출처를 계층화하여 순차적으로 시도하는 Fallback 구조
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import re

# 기존 GuestimationEngine 재사용
from umis_rag.utils.guestimation import (
    GuestimationEngine,
    BenchmarkCandidate,
    ComparabilityResult
)


class DataSource(Enum):
    """데이터 출처 (Layer)"""
    PROJECT_DATA = 1      # 프로젝트 데이터 (100% 신뢰)
    LLM_DIRECT = 2        # LLM 직접 답변 (70% 신뢰)
    WEB_CONSENSUS = 3     # 웹 검색 공통 맥락 (80% 신뢰)
    LAW = 4               # 법칙 (물리/법률) (100% 신뢰)
    BEHAVIORAL = 5        # 행동경제학 (70% 신뢰)
    STATISTICAL = 6       # 통계 패턴 (60% 신뢰)
    RULE_OF_THUMB = 7     # RAG + 비교 검증 (30-80% 신뢰)
    CONSTRAINT = 8        # 시공간 제약 (50% 신뢰)


@dataclass
class EstimationResult:
    """추정 결과"""
    question: str
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None  # (min, max)
    source_layer: Optional[DataSource] = None
    confidence: float = 0.0  # 0.0 ~ 1.0
    logic_steps: List[str] = field(default_factory=list)
    used_data: List[Dict] = field(default_factory=list)
    rejected_data: List[Dict] = field(default_factory=list)
    error_range: str = "±30%"
    
    def is_successful(self) -> bool:
        """추정 성공 여부"""
        return self.value is not None or self.value_range is not None
    
    def get_display_value(self) -> str:
        """표시용 값"""
        if self.value is not None:
            return f"{self.value:,.0f}"
        elif self.value_range:
            return f"{self.value_range[0]:,.0f} ~ {self.value_range[1]:,.0f}"
        return "추정 불가"


class MultiLayerGuestimation:
    """
    멀티레이어 Guestimation 엔진
    
    8개 데이터 출처를 계층적으로 시도하여
    최적의 추정 방법 자동 선택
    
    Usage:
        estimator = MultiLayerGuestimation(project_context={...})
        result = estimator.estimate("한국 음식점 재방문 주기는?")
        print(f"결과: {result.value} (출처: {result.source_layer.name})")
    """
    
    def __init__(
        self,
        project_context: Optional[Dict] = None,
        enable_web_search: bool = False,  # 웹 검색 활성화 (기본 비활성)
        enable_llm: bool = True,  # LLM 활성화
    ):
        """
        초기화
        
        Args:
            project_context: 프로젝트 데이터 (확정된 값들)
            enable_web_search: 웹 검색 활성화 여부
            enable_llm: LLM 사용 여부
        """
        self.project_context = project_context or {}
        self.enable_web_search = enable_web_search
        self.enable_llm = enable_llm
        
        # 기존 GuestimationEngine 활용 (Layer 7용)
        self.benchmark_engine = GuestimationEngine()
        
        # 레이어별 활성화 상태
        self.layer_enabled = {
            DataSource.PROJECT_DATA: True,  # 항상 활성
            DataSource.LLM_DIRECT: enable_llm,
            DataSource.WEB_CONSENSUS: enable_web_search,
            DataSource.LAW: True,
            DataSource.BEHAVIORAL: True,
            DataSource.STATISTICAL: True,
            DataSource.RULE_OF_THUMB: True,  # RAG 항상 활성
            DataSource.CONSTRAINT: True,
        }
    
    def estimate(
        self,
        question: str,
        target_profile: Optional[BenchmarkCandidate] = None,
        rag_candidates: Optional[List[BenchmarkCandidate]] = None
    ) -> EstimationResult:
        """
        멀티레이어 추정
        
        Args:
            question: 추정 질문 (예: "한국 음식점 재방문 주기는?")
            target_profile: 타겟 프로필 (비교 기준)
            rag_candidates: RAG에서 검색한 벤치마크 후보들
        
        Returns:
            EstimationResult
        """
        
        # 초기화
        result = EstimationResult(question=question)
        
        # Layer 1: 프로젝트 데이터
        if self.layer_enabled[DataSource.PROJECT_DATA]:
            layer_result = self._try_project_data(question)
            if layer_result.is_successful():
                return layer_result
        
        # Layer 2: LLM 직접 답변
        if self.layer_enabled[DataSource.LLM_DIRECT]:
            layer_result = self._try_llm_direct(question)
            if layer_result.is_successful() and layer_result.confidence >= 0.7:
                return layer_result
        
        # Layer 3: 웹 검색 (옵션)
        if self.layer_enabled[DataSource.WEB_CONSENSUS]:
            layer_result = self._try_web_consensus(question)
            if layer_result.is_successful() and layer_result.confidence >= 0.8:
                return layer_result
        
        # Layer 4: 법칙 기반
        if self.layer_enabled[DataSource.LAW]:
            layer_result = self._try_law_based(question)
            if layer_result.is_successful():
                return layer_result
        
        # Layer 5: 행동경제학
        if self.layer_enabled[DataSource.BEHAVIORAL]:
            layer_result = self._try_behavioral(question, target_profile)
            if layer_result.is_successful() and layer_result.confidence >= 0.6:
                return layer_result
        
        # Layer 6: 통계 패턴
        if self.layer_enabled[DataSource.STATISTICAL]:
            layer_result = self._try_statistical(question)
            if layer_result.is_successful() and layer_result.confidence >= 0.5:
                return layer_result
        
        # Layer 7: RAG 벤치마크 (핵심!)
        if self.layer_enabled[DataSource.RULE_OF_THUMB] and rag_candidates:
            layer_result = self._try_rag_benchmark(question, target_profile, rag_candidates)
            if layer_result.is_successful() and layer_result.confidence >= 0.5:
                return layer_result
        
        # Layer 8: 제약조건 (최후 수단)
        if self.layer_enabled[DataSource.CONSTRAINT]:
            layer_result = self._try_constraint_boundary(question)
            if layer_result.is_successful():
                return layer_result
        
        # 모든 레이어 실패
        result.logic_steps.append("❌ 모든 레이어에서 추정 실패")
        result.confidence = 0.0
        return result
    
    # ===========================================
    # Layer 구현
    # ===========================================
    
    def _try_project_data(self, question: str) -> EstimationResult:
        """
        Layer 1: 프로젝트 데이터
        
        프로젝트 컨텍스트에서 확정된 값 검색
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.PROJECT_DATA
        )
        
        # 키워드 추출 (간단한 매칭)
        keywords = self._extract_keywords(question)
        
        # 프로젝트 데이터 검색
        for key, value in self.project_context.items():
            if any(kw in key.lower() for kw in keywords):
                result.value = value
                result.confidence = 1.0
                result.logic_steps.append(f"✅ Layer 1: 프로젝트 데이터 '{key}' 사용")
                result.used_data.append({
                    'source': '프로젝트 데이터',
                    'key': key,
                    'value': value
                })
                return result
        
        result.logic_steps.append("❌ Layer 1: 프로젝트 데이터 없음 → Layer 2로")
        return result
    
    def _try_llm_direct(self, question: str) -> EstimationResult:
        """
        Layer 2: LLM 직접 답변
        
        간단한 사실 질문 (인구, 상식 등)
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.LLM_DIRECT
        )
        
        # 간단한 사실 질문인지 판단
        simple_fact_patterns = [
            r'인구',
            r'평균.*시간',
            r'일반적',
            r'보통',
            r'통상',
        ]
        
        is_simple = any(re.search(pattern, question) for pattern in simple_fact_patterns)
        
        if not is_simple:
            result.logic_steps.append("❌ Layer 2: 복잡한 질문 → LLM 직접 답변 부적합 → Layer 3으로")
            return result
        
        # LLM 직접 답변은 Native Mode에서 사용자가 직접 실행
        # 여기서는 가능성만 표시
        result.logic_steps.append("💡 Layer 2: LLM 직접 답변 가능")
        result.logic_steps.append("   → Native Mode: Cursor에서 직접 질문")
        result.logic_steps.append("   → External Mode: API 호출 필요")
        result.confidence = 0.7
        
        # 실제 구현은 Native/External Mode에서
        result.logic_steps.append("⚠️ Layer 2: 자동 실행 비활성 → Layer 3으로")
        result.confidence = 0.0  # 자동 실행 불가
        
        return result
    
    def _try_web_consensus(self, question: str) -> EstimationResult:
        """
        Layer 3: 웹 검색 공통 맥락
        
        상위 5-10개 결과의 공통값 추출
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.WEB_CONSENSUS
        )
        
        if not self.enable_web_search:
            result.logic_steps.append("❌ Layer 3: 웹 검색 비활성화 → Layer 4로")
            return result
        
        # 웹 검색은 Native Mode에서 사용자가 직접 또는 web_search tool 사용
        result.logic_steps.append("💡 Layer 3: 웹 검색 권장")
        result.logic_steps.append("   → 질문을 웹 검색하여 상위 5-10개 공통값 확인")
        result.confidence = 0.0  # 수동 실행 필요
        
        return result
    
    def _try_law_based(self, question: str) -> EstimationResult:
        """
        Layer 4: 법칙 기반 (물리/법률)
        
        절대적 제약조건 확인
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.LAW
        )
        
        # 시간 제약 (정확한 패턴 매칭)
        time_laws = {
            r'\b하루\b': (24, '시간'),
            r'\b일주일\b|\b1주\b': (7, '일'),
            r'\b한 달\b|\b1개월\b': (30, '일'),
            r'\b1년\b|\b년간\b': (365, '일'),
        }
        
        for pattern, (value, unit) in time_laws.items():
            if re.search(pattern, question):
                result.value = value
                result.confidence = 1.0
                result.logic_steps.append(f"✅ Layer 4: 법칙 '{pattern}' = {value} {unit}")
                result.used_data.append({
                    'source': '물리 법칙',
                    'law': f'{pattern} = {value} {unit}',
                    'reliability': '절대적'
                })
                return result
        
        result.logic_steps.append("❌ Layer 4: 적용 가능한 법칙 없음 → Layer 5로")
        return result
    
    def _try_behavioral(
        self,
        question: str,
        target_profile: Optional[BenchmarkCandidate]
    ) -> EstimationResult:
        """
        Layer 5: 행동경제학
        
        예측 가능한 비합리성 활용
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.BEHAVIORAL
        )
        
        # Loss Aversion 패턴
        if '손실' in question or '해지' in question or '이탈' in question:
            if '가입' in question or '구독' in question:
                # Loss Aversion: 손실 회피가 이득 추구보다 2배 강함
                result.logic_steps.append("💡 Layer 5: Loss Aversion 적용 가능")
                result.logic_steps.append("   → 손실 회피 > 이득 추구 (2배)")
                result.confidence = 0.7
                result.used_data.append({
                    'source': '행동경제학',
                    'principle': 'Loss Aversion',
                    'multiplier': 2.0
                })
                # 하지만 구체적인 값은 다른 레이어 필요
                result.logic_steps.append("⚠️ Layer 5: 구체적 값 필요 → Layer 6으로")
                result.confidence = 0.0
        else:
            result.logic_steps.append("❌ Layer 5: 행동경제학 패턴 미발견 → Layer 6으로")
        
        return result
    
    def _try_statistical(self, question: str) -> EstimationResult:
        """
        Layer 6: 통계 패턴
        
        파레토 80-20, 정규분포 등
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.STATISTICAL
        )
        
        # 파레토 패턴 (80-20 법칙)
        if '상위' in question or '주요' in question or '핵심' in question:
            if '비율' in question or '%' in question or '점유' in question:
                result.value = 0.20  # 파레토: 상위 20%
                result.confidence = 0.6
                result.logic_steps.append("✅ Layer 6: 파레토 법칙 (80-20)")
                result.logic_steps.append("   → 상위 20%가 80% 차지")
                result.used_data.append({
                    'source': '통계 패턴',
                    'pattern': 'Pareto Principle',
                    'value': '20%'
                })
                return result
        
        # 정규분포 (평균 ±1SD = 68%)
        if '대부분' in question or '보통' in question:
            result.logic_steps.append("💡 Layer 6: 정규분포 적용 가능")
            result.logic_steps.append("   → 평균 ±1SD (68% 범위)")
            result.confidence = 0.5
            # 하지만 평균값이 필요함
            result.logic_steps.append("⚠️ Layer 6: 평균값 필요 → Layer 7로")
            result.confidence = 0.0
        else:
            result.logic_steps.append("❌ Layer 6: 통계 패턴 미발견 → Layer 7로")
        
        return result
    
    def _try_rag_benchmark(
        self,
        question: str,
        target_profile: Optional[BenchmarkCandidate],
        rag_candidates: Optional[List[BenchmarkCandidate]]
    ) -> EstimationResult:
        """
        Layer 7: RAG 벤치마크 + 비교 가능성 검증
        
        기존 GuestimationEngine 활용
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.RULE_OF_THUMB
        )
        
        if not rag_candidates:
            result.logic_steps.append("❌ Layer 7: RAG 후보 없음 → Layer 8로")
            return result
        
        if not target_profile:
            result.logic_steps.append("⚠️ Layer 7: 타겟 프로필 없음 (비교 불가) → Layer 8로")
            return result
        
        # 비교 가능성 검증 (기존 엔진 활용)
        filtered = self.benchmark_engine.filter_candidates(target_profile, rag_candidates)
        
        # 채택 가능한 벤치마크
        if filtered['adopt']:
            adopted = filtered['adopt'][0]  # 최고 점수
            result.value = adopted.candidate.value
            result.confidence = adopted.score / 4.0  # 4점 만점 → 0-1.0
            result.logic_steps.append(f"✅ Layer 7: RAG 벤치마크 '{adopted.candidate.name}' 채택")
            result.logic_steps.append(f"   → 비교 가능성: {adopted.score}/4")
            result.logic_steps.append(f"   → 근거: {', '.join(adopted.reasons)}")
            result.used_data.append({
                'source': 'RAG 벤치마크',
                'name': adopted.candidate.name,
                'value': adopted.candidate.value,
                'comparability': adopted.score
            })
            
            # 기각된 후보 기록
            for rejected in filtered['reject']:
                result.rejected_data.append({
                    'name': rejected.candidate.name,
                    'reason': ', '.join(rejected.details.values())
                })
            
            return result
        
        # 참고만 가능
        elif filtered['reference']:
            ref = filtered['reference'][0]
            result.value = ref.candidate.value
            result.confidence = ref.score / 4.0
            result.logic_steps.append(f"⚠️ Layer 7: RAG 벤치마크 '{ref.candidate.name}' 참고만")
            result.logic_steps.append(f"   → 비교 가능성 낮음: {ref.score}/4")
            result.logic_steps.append(f"   → 주의: 오차 클 수 있음 (±50%)")
            result.error_range = "±50%"
            result.used_data.append({
                'source': 'RAG 벤치마크 (참고)',
                'name': ref.candidate.name,
                'value': ref.candidate.value,
                'comparability': ref.score
            })
            return result
        
        # 모두 기각
        else:
            result.logic_steps.append("❌ Layer 7: 모든 RAG 벤치마크 기각 (비교 불가) → Layer 8로")
            for rejected in filtered['reject'][:3]:
                result.rejected_data.append({
                    'name': rejected.candidate.name,
                    'reason': ', '.join(rejected.details.values())
                })
            return result
    
    def _try_constraint_boundary(self, question: str) -> EstimationResult:
        """
        Layer 8: 제약조건 기반 경계 추정
        
        최소/최대 경계만 제시
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.CONSTRAINT
        )
        
        # 비율 질문 (0-100%)
        if '비율' in question or '%' in question or '점유율' in question:
            result.value_range = (0.0, 1.0)
            result.confidence = 0.5
            result.logic_steps.append("✅ Layer 8: 비율 제약 (0-100%)")
            result.logic_steps.append("   → 최소: 0%, 최대: 100%")
            result.used_data.append({
                'source': '논리적 제약',
                'constraint': '비율은 0-100%'
            })
            return result
        
        # 시간 제약
        if '시간' in question or '분' in question or '주기' in question:
            if '하루' in question:
                result.value_range = (0, 24)
                result.logic_steps.append("✅ Layer 8: 시간 제약 (하루 0-24시간)")
            elif '주' in question:
                result.value_range = (0, 7)
                result.logic_steps.append("✅ Layer 8: 시간 제약 (주 0-7일)")
            elif '월' in question or '재방문' in question:
                result.value_range = (0, 90)
                result.logic_steps.append("✅ Layer 8: 시간 제약 (재방문 0-90일)")
                result.confidence = 0.4
            
            if result.value_range:
                result.confidence = 0.5
                result.used_data.append({
                    'source': '시간적 제약',
                    'range': result.value_range
                })
                return result
        
        # 추정 불가능
        result.logic_steps.append("❌ Layer 8: 제약조건 미발견 → 추정 실패")
        return result
    
    # ===========================================
    # 유틸리티
    # ===========================================
    
    def _extract_keywords(self, question: str) -> List[str]:
        """질문에서 키워드 추출"""
        # 간단한 키워드 추출 (stopwords 제거)
        stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '?', '얼마', '몇'}
        keywords = []
        for word in question.split():
            cleaned = word.strip('?.,!')
            if cleaned and cleaned not in stopwords and len(cleaned) > 1:
                keywords.append(cleaned.lower())
        return keywords
    
    def get_layer_sequence(self) -> List[str]:
        """활성화된 레이어 순서 반환"""
        sequence = []
        for source in DataSource:
            if self.layer_enabled[source]:
                sequence.append(f"{source.value}. {source.name}")
        return sequence
    
    def estimate_with_trace(
        self,
        question: str,
        target_profile: Optional[BenchmarkCandidate] = None,
        rag_candidates: Optional[List[BenchmarkCandidate]] = None,
        verbose: bool = True
    ) -> EstimationResult:
        """
        추정 + 전체 레이어 시도 과정 추적
        
        verbose=True 시 모든 레이어 시도 기록
        """
        result = self.estimate(question, target_profile, rag_candidates)
        
        if verbose:
            print("=" * 80)
            print(f"🎯 질문: {question}")
            print("=" * 80)
            print()
            print("📊 레이어 시도 과정:")
            for step in result.logic_steps:
                print(f"   {step}")
            print()
            
            if result.is_successful():
                print("✅ 추정 성공!")
                print(f"   출처: {result.source_layer.name}")
                print(f"   값: {result.get_display_value()}")
                print(f"   신뢰도: {result.confidence:.0%}")
            else:
                print("❌ 추정 실패")
                print("   → 모든 레이어에서 데이터 없음")
            print("=" * 80)
        
        return result


# ===========================================
# 편의 함수
# ===========================================

def quick_estimate(
    question: str,
    project_data: Optional[Dict] = None,
    rag_candidates: Optional[List[BenchmarkCandidate]] = None
) -> float:
    """
    빠른 추정 (단일 값 반환)
    
    Usage:
        value = quick_estimate("한국 음식점 재방문 주기는?")
    """
    estimator = MultiLayerGuestimation(project_context=project_data or {})
    result = estimator.estimate(question, rag_candidates=rag_candidates)
    
    if result.value is not None:
        return result.value
    elif result.value_range:
        # 범위의 중간값 반환
        return (result.value_range[0] + result.value_range[1]) / 2
    else:
        return None


def estimate_with_details(
    question: str,
    project_data: Optional[Dict] = None,
    target_profile: Optional[BenchmarkCandidate] = None,
    rag_candidates: Optional[List[BenchmarkCandidate]] = None
) -> Dict[str, Any]:
    """
    상세 추정 (문서화용)
    
    Returns:
        Estimation Details 7개 섹션 호환 형식
    """
    estimator = MultiLayerGuestimation(project_context=project_data or {})
    result = estimator.estimate(question, target_profile, rag_candidates)
    
    return {
        'id': f'EST_{question[:20]}',
        'description': question,
        'value': result.value or result.get_display_value(),
        'confidence': f"{result.confidence:.0%}",
        'error_range': result.error_range,
        'used_in': '',
        
        # 7개 섹션
        'reason': '직접 데이터 없음',
        'base_data': result.used_data,
        'logic_steps': result.logic_steps,
        'calculation': f"최종: {result.get_display_value()}",
        'verification': f"출처: {result.source_layer.name if result.source_layer else 'None'}",
        'alternatives': [f"{r['name']}: {r['reason']}" for r in result.rejected_data[:3]],
        
        # 메타데이터
        'source_layer': result.source_layer.name if result.source_layer else None,
        'layer_sequence': result.logic_steps,
    }

