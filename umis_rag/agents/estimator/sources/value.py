"""
Value Sources

구체적 값 제시
- 확정 데이터
- LLM 추정
- 웹 검색
- RAG 벤치마크
- 통계 패턴 값
"""

from typing import Optional, List, Dict, Any
import os

from umis_rag.utils.logger import logger
from ..models import ValueEstimate, SourceType, Context, DistributionType, SoftGuide


class ValueSourceBase:
    """Value Source Base Class"""
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """값 수집"""
        raise NotImplementedError


class DefiniteDataSource(ValueSourceBase):
    """
    확정 데이터
    
    역할:
    -----
    - 프로젝트 데이터에서 확정값
    - confidence 0.95-1.0
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """확정 데이터 수집"""
        
        if not context or not context.project_data:
            return []
        
        estimates = []
        
        # 키워드 매칭 (간단히)
        keywords = self._extract_keywords(question)
        
        for key, value in context.project_data.items():
            # 키 매칭
            if any(kw in key.lower() for kw in keywords):
                estimate = ValueEstimate(
                    source_type=SourceType.DEFINITE_DATA,
                    value=float(value) if isinstance(value, (int, float)) else 0.0,
                    confidence=0.98,  # 완전 확정은 드묾
                    reasoning=f"프로젝트 확정 데이터: {key}",
                    source_detail=f"project_data.{key}",
                    raw_data=value
                )
                
                estimates.append(estimate)
        
        return estimates
    
    def _extract_keywords(self, question: str) -> List[str]:
        """키워드 추출 (간단히)"""
        # 불용어 제거
        stopwords = {'은', '는', '이', '가', '를', '의', '에', '와'}
        words = question.split()
        keywords = [w.lower() for w in words if w not in stopwords and len(w) >= 2]
        return keywords


class LLMEstimationSource(ValueSourceBase):
    """
    LLM 추정
    
    역할:
    -----
    - LLM에게 직접 질문
    - Native Mode (Cursor) or External (API)
    - confidence 0.60-0.90
    """
    
    def __init__(self, llm_mode: str = "native"):
        self.llm_mode = llm_mode
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """LLM 추정"""
        
        if self.llm_mode == "skip":
            return []
        
        # 간단한 사실 질문만 (복잡한 건 Tier 2에서)
        if not self._is_simple_factual(question):
            return []
        
        # TODO: 실제 LLM 호출
        # 현재는 스킵
        logger.info(f"  [LLM] 스킵 (Native Mode는 interactive 필요)")
        
        return []
    
    def _is_simple_factual(self, question: str) -> bool:
        """간단한 사실 질문인가?"""
        factual_keywords = ['인구', '면적', 'gdp', '수도']
        return any(kw in question.lower() for kw in factual_keywords)


class WebSearchSource(ValueSourceBase):
    """
    웹 검색
    
    역할:
    -----
    - 웹에서 최신 데이터
    - consensus 알고리즘
    - confidence 0.70
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """웹 검색"""
        
        # TODO: 실제 웹 검색 구현
        # 현재는 스킵
        logger.info(f"  [Web] 스킵 (구현 필요)")
        
        return []


class RAGBenchmarkSource(ValueSourceBase):
    """
    RAG 벤치마크
    
    역할:
    -----
    - Quantifier.market_benchmarks 활용
    - 도메인 지표 검색
    - confidence 0.50-0.80
    """
    
    def __init__(self):
        """초기화 (Lazy)"""
        self.quantifier = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy 초기화"""
        if self._initialized:
            return
        
        try:
            from umis_rag.agents.quantifier import QuantifierRAG
            self.quantifier = QuantifierRAG()
            logger.info(f"  [RAG] QuantifierRAG 연결 완료")
            self._initialized = True
        except Exception as e:
            logger.warning(f"  [RAG] QuantifierRAG 로드 실패: {e}")
            self._initialized = True
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """RAG 벤치마크 검색"""
        
        self._initialize()
        
        if not self.quantifier:
            return []
        
        # 도메인 지표 질문만
        if not self._is_domain_metric(question):
            return []
        
        logger.info(f"  [RAG] Quantifier 벤치마크 검색")
        
        try:
            # Quantifier.search_benchmark() 호출
            results = self.quantifier.search_benchmark(
                market=question,
                top_k=3
            )
            
            if not results:
                return []
            
            estimates = []
            
            for doc, score in results:
                # 메타데이터에서 값 추출 (다양한 필드 시도)
                value = self._extract_value_from_metadata(doc.metadata, doc.page_content)
                
                if value:
                    estimate = ValueEstimate(
                        source_type=SourceType.RAG_BENCHMARK,
                        value=value,
                        confidence=score * 0.8,  # 유사도 기반, 약간 할인
                        reasoning=f"RAG 벤치마크 (유사도 {score:.2f})",
                        source_detail=doc.metadata.get('metric', 'market_benchmarks'),
                        raw_data=doc.metadata
                    )
                    
                    estimates.append(estimate)
            
            logger.info(f"  [RAG] {len(estimates)}개 벤치마크 발견")
            return estimates
            
        except Exception as e:
            logger.error(f"  [RAG] 검색 실패: {e}")
            return []
    
    def _is_domain_metric(self, question: str) -> bool:
        """도메인 지표 질문인가?"""
        # SaaS, 비즈니스 지표 키워드
        domain_metrics = [
            'churn', 'ltv', 'cac', 'arpu', 'mrr', 'arr',
            '해지율', '이탈률', '전환율', 'conversion',
            '점유율', '성장률', '마진'
        ]
        
        question_lower = question.lower()
        return any(metric in question_lower for metric in domain_metrics)
    
    def _extract_value_from_metadata(self, metadata: Dict, content: str) -> Optional[float]:
        """메타데이터에서 값 추출"""
        
        # 시도 1: global_benchmark.median
        if 'global_benchmark' in metadata:
            global_bench = metadata['global_benchmark']
            if isinstance(global_bench, dict):
                median = global_bench.get('median')
                if median:
                    return self._parse_value(median)
        
        # 시도 2: value 필드
        if 'value' in metadata:
            return self._parse_value(metadata['value'])
        
        # 시도 3: content에서 추출 (간단히)
        # "5-7%" 같은 패턴
        import re
        patterns = [
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%',  # "5-7%"
            r'(\d+(?:\.\d+)?)\s*%',  # "6%"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                if len(match.groups()) == 2:  # range
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    return (min_val + max_val) / 2 / 100  # % → 소수
                else:  # single value
                    return float(match.group(1)) / 100
        
        return None
    
    def _parse_value(self, value_raw) -> Optional[float]:
        """값 파싱"""
        # 숫자면 그대로
        if isinstance(value_raw, (int, float)):
            return float(value_raw)
        
        # 문자열이면 파싱 시도
        if isinstance(value_raw, str):
            # "5-7%" → 중앙값 6
            if '-' in value_raw:
                parts = value_raw.replace('%', '').split('-')
                try:
                    min_val = float(parts[0])
                    max_val = float(parts[1])
                    return (min_val + max_val) / 2 / 100  # % → 소수
                except:
                    pass
            
            # "6%" → 0.06
            try:
                val_str = value_raw.replace('%', '').replace(',', '').strip()
                val = float(val_str)
                # % 형태면 100으로 나누기
                if '%' in value_raw:
                    return val / 100
                return val
            except:
                pass
        
        return None


class StatisticalValueSource(ValueSourceBase):
    """
    통계 패턴 값
    
    역할:
    -----
    - 통계 패턴의 대표값 (median or mean)
    - 다른 Value 없을 때만 사용
    - confidence 0.50-0.65
    """
    
    def collect(
        self,
        question: str,
        context: Optional[Context] = None,
        statistical_guide: Optional['SoftGuide'] = None
    ) -> List[ValueEstimate]:
        """통계값 추출"""
        
        if not statistical_guide or not statistical_guide.distribution:
            return []
        
        estimates = []
        
        dist = statistical_guide.distribution
        
        # 분포 타입별 대표값 선택
        if dist.distribution_type == DistributionType.NORMAL:
            # 정규분포 → mean
            if dist.mean:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.mean,
                    confidence=0.70 if (dist.cv and dist.cv < 0.20) else 0.60,
                    reasoning="정규분포 평균값"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.POWER_LAW:
            # Power Law → median (평균 금지!)
            if dist.percentiles and 'p50' in dist.percentiles:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.percentiles['p50'],
                    confidence=0.60,
                    reasoning="Power Law 중앙값 (평균 사용 금지)"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.EXPONENTIAL:
            # 지수분포 → median
            if dist.percentiles and 'p50' in dist.percentiles:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.percentiles['p50'],
                    confidence=0.65,
                    reasoning="지수분포 중앙값"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.BIMODAL:
            # 이봉분포 → 값 제시 못함
            logger.info("  [통계값] 이봉분포 → 세분화 필요")
            return []
        
        return estimates

