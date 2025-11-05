"""
Multi-Layer Guestimation Engine
v2.1 - 2025-11-05

8개 데이터 출처를 계층화하여 순차적으로 시도하는 Fallback 구조
글로벌 설정 파일 (config/multilayer_config.yaml) 통합
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import re
import os
from pathlib import Path

# 기존 GuestimationEngine 재사용
from umis_rag.utils.guestimation import (
    GuestimationEngine,
    BenchmarkCandidate,
    ComparabilityResult
)

# 글로벌 설정 로더
from umis_rag.core.multilayer_config import get_multilayer_config


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
        config_override: Optional[Dict] = None,  # 설정 오버라이드
    ):
        """
        초기화
        
        Args:
            project_context: 프로젝트 데이터 (확정된 값들)
            config_override: 설정 오버라이드 (옵션, 기본은 글로벌 설정 사용)
        """
        self.project_context = project_context or {}
        
        # 글로벌 설정 로드
        self.config_loader = get_multilayer_config()
        self.global_modes = self.config_loader.get_global_modes()
        
        # 설정 오버라이드 적용
        if config_override:
            if 'llm_mode' in config_override:
                self.global_modes.llm_mode = config_override['llm_mode']
            if 'web_search_mode' in config_override:
                self.global_modes.web_search_mode = config_override['web_search_mode']
            if 'interactive_mode' in config_override:
                self.global_modes.interactive_mode = config_override['interactive_mode']
        
        # 기존 GuestimationEngine 활용 (Layer 7용)
        self.benchmark_engine = GuestimationEngine()
        
        # 레이어별 활성화 상태 (글로벌 설정 기반)
        self.layer_enabled = {
            DataSource.PROJECT_DATA: True,  # 항상 활성
            DataSource.LLM_DIRECT: self.global_modes.llm_mode != 'skip',
            DataSource.WEB_CONSENSUS: self.global_modes.web_search_mode != 'skip',
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
        글로벌 설정(llm_mode)에 따라 Native/External 자동 선택
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.LLM_DIRECT
        )
        
        # 간단한 사실 질문인지 판단
        if not self._is_simple_fact(question):
            result.logic_steps.append("❌ Layer 2: 복잡한 질문 → LLM 직접 답변 부적합 → Layer 3으로")
            return result
        
        # 글로벌 설정에 따라 분기
        llm_mode = self.global_modes.llm_mode
        
        if llm_mode == 'native':
            return self._llm_native_mode(question, result)
        elif llm_mode == 'external':
            return self._llm_external_mode(question, result)
        else:  # skip
            result.logic_steps.append("⚠️ Layer 2: LLM 모드 'skip' → Layer 3으로")
            return result
    
    def _llm_native_mode(self, question: str, result: EstimationResult) -> EstimationResult:
        """Layer 2 - Native Mode (Cursor LLM 활용)"""
        
        # Interactive 모드: 사용자 입력
        if self.global_modes.interactive_mode:
            result.logic_steps.append("💡 Layer 2: LLM 직접 답변 (Native Interactive)")
            print(f"\n❓ LLM에게 질문하세요: {question}")
            print("   (Cursor Composer/Chat에서 질문 후 답변만 입력)")
            user_input = input("   답변 (숫자만 입력, 건너뛰려면 Enter): ")
            
            if user_input.strip():
                value = self._extract_number(user_input)
                if value:
                    result.value = value
                    result.confidence = self.config_loader.get_llm_config('native').get('confidence', 0.7)
                    result.logic_steps.append(f"✅ Layer 2: 사용자 입력 = {value}")
                    result.used_data.append({
                        'source': 'Native LLM (사용자 입력)',
                        'value': value
                    })
                    return result
        
        # 비-Interactive: 안내만
        result.logic_steps.append("💡 Layer 2: Native LLM 권장")
        result.logic_steps.append(f"   질문: \"{question}\"")
        result.logic_steps.append("   → Cursor Composer에서 직접 질문하세요")
        result.logic_steps.append("⚠️ Layer 2: Interactive 모드 비활성 → Layer 3으로")
        return result
    
    def _llm_external_mode(self, question: str, result: EstimationResult) -> EstimationResult:
        """Layer 2 - External Mode (OpenAI API)"""
        
        llm_config = self.config_loader.get_llm_config('external')
        
        if not llm_config.get('enabled', False):
            result.logic_steps.append("⚠️ Layer 2: External API 비활성 → Layer 3으로")
            return result
        
        try:
            from openai import OpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                result.logic_steps.append("❌ Layer 2: OPENAI_API_KEY 없음 → Layer 3으로")
                return result
            
            client = OpenAI(api_key=api_key)
            
            # Prompt 생성
            prompt = llm_config.get('prompt_template', '').format(question=question)
            
            # API 호출
            response = client.chat.completions.create(
                model=llm_config.get('model', 'gpt-4o-mini'),
                messages=[{"role": "user", "content": prompt}],
                temperature=llm_config.get('temperature', 0.1),
                max_tokens=llm_config.get('max_tokens', 50)
            )
            
            answer = response.choices[0].message.content
            
            # 숫자 추출
            value = self._extract_number(answer)
            
            if value:
                result.value = value
                result.confidence = llm_config.get('confidence', 0.7)
                result.logic_steps.append(f"✅ Layer 2: LLM API 답변 = {answer}")
                result.logic_steps.append(f"   추출값: {value}")
                result.used_data.append({
                    'source': f"LLM API ({llm_config.get('model')})",
                    'raw_answer': answer,
                    'extracted': value
                })
                return result
            else:
                result.logic_steps.append(f"⚠️ Layer 2: 숫자 추출 실패 '{answer}' → Layer 3으로")
        
        except Exception as e:
            result.logic_steps.append(f"❌ Layer 2: API 에러 ({str(e)[:50]}) → Layer 3으로")
        
        return result
    
    def _try_web_consensus(self, question: str) -> EstimationResult:
        """
        Layer 3: 웹 검색 공통 맥락
        
        상위 20개 결과의 공통값 추출 (이상치 제외, 유사도 0.7 이상)
        글로벌 설정(web_search_mode)에 따라 Native/API/Scraping 자동 선택
        """
        result = EstimationResult(
            question=question,
            source_layer=DataSource.WEB_CONSENSUS
        )
        
        # 글로벌 설정에 따라 분기
        web_mode = self.global_modes.web_search_mode
        
        if web_mode == 'native':
            return self._web_native_mode(question, result)
        elif web_mode == 'api':
            return self._web_api_mode(question, result)
        elif web_mode == 'scraping':
            return self._web_scraping_mode(question, result)
        else:  # skip
            result.logic_steps.append("⚠️ Layer 3: 웹 검색 모드 'skip' → Layer 4로")
            return result
    
    def _web_native_mode(self, question: str, result: EstimationResult) -> EstimationResult:
        """Layer 3 - Native Mode (사용자가 직접 검색)"""
        
        # Interactive 모드: 사용자 입력
        if self.global_modes.interactive_mode:
            result.logic_steps.append("💡 Layer 3: 웹 검색 (Native Interactive)")
            print(f"\n🔍 웹 검색하세요: {question}")
            print("   권장: Google, Naver에서 검색 후 상위 5-10개 공통값 확인")
            user_input = input("   공통값 (숫자 입력, 건너뛰려면 Enter): ")
            
            if user_input.strip():
                value = self._extract_number(user_input)
                if value:
                    result.value = value
                    web_config = self.config_loader.get_web_search_config('native')
                    result.confidence = 0.75
                    result.logic_steps.append(f"✅ Layer 3: 사용자 입력 (웹 검색 결과) = {value}")
                    result.used_data.append({
                        'source': '웹 검색 (사용자 확인)',
                        'value': value
                    })
                    return result
        
        # 비-Interactive: 안내만
        result.logic_steps.append("💡 Layer 3: 웹 검색 권장")
        result.logic_steps.append(f"   질문: \"{question}\"")
        result.logic_steps.append("   → Google/Naver에서 검색 후 상위 20개 공통값 확인")
        result.logic_steps.append("⚠️ Layer 3: Interactive 모드 비활성 → Layer 4로")
        return result
    
    def _web_api_mode(self, question: str, result: EstimationResult) -> EstimationResult:
        """Layer 3 - API Mode (SerpAPI 또는 Google Custom Search)"""
        
        web_config = self.config_loader.get_web_search_config('api')
        
        if not web_config.get('enabled', False):
            result.logic_steps.append("⚠️ Layer 3: API 모드 비활성 → Layer 4로")
            return result
        
        # SerpAPI 사용
        serpapi_config = web_config.get('serpapi', {})
        api_key = os.getenv(serpapi_config.get('api_key_env', 'SERPAPI_KEY'))
        
        if not api_key:
            result.logic_steps.append("❌ Layer 3: SERPAPI_KEY 없음 → Layer 4로")
            return result
        
        try:
            import requests
            
            # 검색 실행
            params = {
                'q': question,
                'api_key': api_key,
                'num': serpapi_config.get('results_count', 20),  # 상위 20개
                'gl': 'kr',  # 한국
                'hl': 'ko',  # 한국어
            }
            
            response = requests.get(
                serpapi_config.get('endpoint', 'https://serpapi.com/search'),
                params=params,
                timeout=10
            )
            
            data = response.json()
            results = data.get('organic_results', [])
            
            # 각 결과에서 숫자 추출
            numbers = []
            for r in results[:20]:  # 상위 20개
                snippet = r.get('snippet', '') + ' ' + r.get('title', '')
                num = self._extract_number(snippet)
                if num:
                    numbers.append(num)
            
            # 공통값 추출 (이상치 제외, 유사도 0.7 기반)
            if len(numbers) >= 3:
                consensus_value = self._find_web_consensus(numbers)
                
                if consensus_value:
                    result.value = consensus_value
                    result.confidence = self._calculate_web_confidence(len(numbers))
                    result.logic_steps.append(f"✅ Layer 3: 웹 검색 {len(results)}개 결과")
                    result.logic_steps.append(f"   추출된 숫자: {len(numbers)}개")
                    result.logic_steps.append(f"   공통값 (이상치 제외): {consensus_value}")
                    result.used_data.append({
                        'source': 'SerpAPI 웹 검색',
                        'results_count': len(results),
                        'numbers_found': len(numbers),
                        'consensus': consensus_value,
                        'all_numbers': numbers[:10]  # 상위 10개만 저장
                    })
                    return result
                else:
                    result.logic_steps.append(f"⚠️ Layer 3: 공통값 찾기 실패 ({len(numbers)}개 값) → Layer 4로")
            else:
                result.logic_steps.append(f"⚠️ Layer 3: 충분한 결과 없음 ({len(numbers)}개) → Layer 4로")
        
        except Exception as e:
            result.logic_steps.append(f"❌ Layer 3: API 에러 ({str(e)[:50]}) → Layer 4로")
        
        return result
    
    def _web_scraping_mode(self, question: str, result: EstimationResult) -> EstimationResult:
        """Layer 3 - Scraping Mode (직접 스크래핑, 사용 비권장)"""
        
        result.logic_steps.append("⚠️ Layer 3: Scraping 모드는 불안정 → 건너뜀 → Layer 4로")
        # 실제 구현은 복잡하고 불안정하므로 생략
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
    
    def _is_simple_fact(self, question: str) -> bool:
        """
        간단한 사실 질문인지 판단
        
        간단한 사실: "한국 인구는?", "평균 식사 시간은?"
        복잡한 질문: "왜 ~한가?", "어떻게 비교하면?"
        """
        # 설정에서 패턴 로드
        llm_config = self.config_loader.get_layer_config('layer_2')
        native_config = llm_config.get('native', {})
        
        simple_patterns = native_config.get('simple_fact_patterns', [
            r'인구',
            r'평균.*시간',
            r'일반적',
            r'보통',
            r'통상',
            r'몇\s*(명|개|시간|일)',
        ])
        
        complex_patterns = native_config.get('complex_patterns', [
            r'왜',
            r'어떻게',
            r'~한다면',
            r'비교',
            r'분석',
        ])
        
        has_simple = any(re.search(p, question) for p in simple_patterns)
        has_complex = any(re.search(p, question) for p in complex_patterns)
        
        return has_simple and not has_complex
    
    def _extract_number(self, text: str) -> Optional[float]:
        """
        텍스트에서 숫자 추출 (설정 기반 패턴)
        
        지원: "5200만", "27억", "15%", "52,000,000" 등
        """
        if not text:
            return None
        
        # 설정에서 패턴 로드
        patterns = self.config_loader.get_number_extraction_patterns()
        
        # 기본 패턴 (설정 없을 경우)
        if not patterns:
            patterns = [
                {'pattern': r'([\d,]+\.?\d*)\s*억', 'multiplier': 100000000},
                {'pattern': r'([\d,]+\.?\d*)\s*천만', 'multiplier': 10000000},
                {'pattern': r'([\d,]+\.?\d*)\s*만', 'multiplier': 10000},
                {'pattern': r'([\d,]+\.?\d*)\s*천', 'multiplier': 1000},
                {'pattern': r'([\d,]+\.?\d*)\s*%', 'multiplier': 0.01},
                {'pattern': r'([\d,]+\.?\d*)', 'multiplier': 1},
            ]
        
        for p in patterns:
            pattern = p.get('pattern', p) if isinstance(p, dict) else p
            multiplier = p.get('multiplier', 1) if isinstance(p, dict) else 1
            
            match = re.search(pattern, text)
            if match:
                num_str = match.group(1).replace(',', '')
                try:
                    value = float(num_str) * multiplier
                    return value
                except:
                    continue
        
        return None
    
    def _find_web_consensus(self, numbers: List[float]) -> Optional[float]:
        """
        웹 검색 결과에서 공통값 추출
        
        방법:
        1. 이상치 제거 (IQR 방법)
        2. 클러스터링 (±20% 범위, 유사도 0.7 적용)
        3. 가장 큰 클러스터의 중앙값
        """
        if len(numbers) < 3:
            return None
        
        # 설정 로드
        consensus_config = self.config_loader.get_consensus_config()
        outlier_config = consensus_config.get('outlier_removal', {})
        clustering_config = consensus_config.get('clustering', {})
        
        # 1. 이상치 제거 (IQR 방법)
        if outlier_config.get('enabled', True):
            numbers = self._remove_outliers_iqr(
                numbers,
                threshold=outlier_config.get('threshold', 1.5)
            )
            
            if len(numbers) < 3:
                return None
        
        # 2. 클러스터링 (유사도 0.7 반영)
        if clustering_config.get('enabled', True):
            tolerance = clustering_config.get('tolerance', 0.2)  # ±20%
            clusters = self._cluster_numbers(numbers, tolerance)
            
            # 가장 큰 클러스터 선택
            if clusters:
                largest_cluster = max(clusters, key=len)
                
                # 최소 크기 체크
                min_size = clustering_config.get('min_cluster_size', 3)
                if len(largest_cluster) >= min_size:
                    # 중앙값 반환
                    largest_cluster.sort()
                    return largest_cluster[len(largest_cluster) // 2]
        
        # 3. Fallback: 전체 중앙값
        numbers.sort()
        return numbers[len(numbers) // 2]
    
    def _remove_outliers_iqr(self, numbers: List[float], threshold: float = 1.5) -> List[float]:
        """
        IQR 방법으로 이상치 제거
        
        Args:
            numbers: 숫자 리스트
            threshold: IQR 배수 (기본 1.5)
        """
        if len(numbers) < 4:
            return numbers
        
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        
        q1 = sorted_nums[n // 4]
        q3 = sorted_nums[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        # 범위 내 값만 유지
        filtered = [num for num in numbers if lower_bound <= num <= upper_bound]
        
        return filtered if filtered else numbers  # 모두 제거되면 원본 반환
    
    def _cluster_numbers(self, numbers: List[float], tolerance: float = 0.2) -> List[List[float]]:
        """
        숫자들을 유사도 기반으로 클러스터링
        
        Args:
            numbers: 숫자 리스트
            tolerance: 허용 오차 (0.2 = ±20%, 유사도 0.8 = 1-0.2)
        
        Returns:
            클러스터 리스트
        """
        if not numbers:
            return []
        
        sorted_nums = sorted(numbers)
        clusters = []
        current_cluster = [sorted_nums[0]]
        
        for num in sorted_nums[1:]:
            # 현재 클러스터의 중앙값
            cluster_median = current_cluster[len(current_cluster) // 2]
            
            # 유사도 계산 (0.2 tolerance = 0.8 similarity)
            similarity = 1 - abs(num - cluster_median) / max(num, cluster_median)
            
            # 유사도 임계값 (설정에서 로드)
            consensus_config = self.config_loader.get_consensus_config()
            similarity_config = consensus_config.get('similarity_based', {})
            threshold = similarity_config.get('threshold', 0.7)  # 기본 0.7
            
            # 유사도가 임계값 이상이면 같은 클러스터
            if similarity >= threshold:
                current_cluster.append(num)
            else:
                clusters.append(current_cluster)
                current_cluster = [num]
        
        clusters.append(current_cluster)
        return clusters
    
    def _calculate_web_confidence(self, count: int) -> float:
        """
        웹 검색 결과 개수에 따른 신뢰도
        
        3-5개: 0.6
        6-10개: 0.75
        11개 이상: 0.8
        """
        consensus_config = self.config_loader.get_consensus_config()
        confidence_config = self.config_loader.get_layer_config('layer_3').get('confidence', {})
        
        if count >= 11:
            return confidence_config.get('consensus_high', 0.8)
        elif count >= 6:
            return 0.75
        else:
            return confidence_config.get('consensus_low', 0.6)
    
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

