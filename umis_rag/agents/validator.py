"""
Validator RAG Agent Module

Validator (Rachel) 에이전트의 RAG 기반 데이터 검증 시스템입니다.

핵심 개념:
-----------
1. **Data Source Discovery**: 데이터 소스 자동 검색 및 추천
2. **Definition Validation**: 정의 검증 사례 참조
3. **Gap Analysis**: 정의 불일치 분석 가이드
4. **Creative Sourcing**: 창의적 데이터 소싱 방법

Validator의 핵심 역할:
----------------------
1. 데이터 정의 검증 (가장 중요!)
2. 신뢰도 평가
3. 창의적 데이터 소싱
4. Gap 분석 및 조정

RAG Collections:
----------------
- data_sources_registry: 데이터 소스 목록 (50개)
- definition_validation_cases: 정의 검증 사례 (100개)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


class ValidatorRAG:
    """
    Validator (Rachel) RAG Agent
    
    역할:
    -----
    - 데이터 소스 발견
    - 정의 검증
    - 신뢰도 평가
    - Gap 분석
    
    핵심 메서드:
    -----------
    - search_data_source(): 데이터 소스 검색
    - search_definition_case(): 정의 검증 사례 검색
    - search_gap_analysis(): Gap 분석 가이드 검색
    
    협업:
    -----
    - Quantifier: 모든 계산의 데이터 정의 검증 (필수!)
    - Observer, Explorer: 데이터 출처 확인
    """
    
    def __init__(self):
        """Validator RAG 에이전트 초기화"""
        logger.info("Validator RAG 에이전트 초기화")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Vector Stores
        try:
            # 1. 데이터 소스
            self.source_store = Chroma(
                collection_name="data_sources_registry",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 데이터 소스: {self.source_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  데이터 소스 Collection 없음 (구축 필요): {e}")
            self.source_store = None
        
        try:
            # 2. 정의 검증 사례
            self.definition_store = Chroma(
                collection_name="definition_validation_cases",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 정의 사례: {self.definition_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  정의 검증 Collection 없음 (구축 필요): {e}")
            self.definition_store = None
    
    def search_data_source(
        self,
        data_type: str,
        top_k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        데이터 소스 검색
        
        사용 시점:
        ----------
        필요한 데이터를 어디서 구할지 모를 때
        
        예시:
        -----
        Input: "한국 SaaS 시장 규모"
        Output: [Gartner (85% 신뢰도), IDC Korea, ...]
        
        Parameters:
        -----------
        data_type: 찾는 데이터 유형
        top_k: 반환할 소스 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.source_store:
            logger.warning("  ⚠️  데이터 소스 RAG 미구축")
            return []
        
        logger.info(f"[Validator] 데이터 소스 검색")
        logger.info(f"  데이터 유형: {data_type}")
        
        results = self.source_store.similarity_search_with_score(
            data_type,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 소스 발견")
        for doc, score in results:
            source_name = doc.metadata.get('source_name', 'Unknown')
            reliability = doc.metadata.get('reliability', 'N/A')
            logger.info(f"    - {source_name} (신뢰도: {reliability}, 유사도: {score:.2f})")
        
        return results
    
    def search_definition_case(
        self,
        term: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        정의 검증 사례 검색
        
        사용 시점:
        ----------
        데이터 정의가 애매하거나, 산업별 차이가 있을 때
        
        예시:
        -----
        Input: "MAU (월간 활성 사용자)"
        Output: [Google 정의 vs Facebook 정의, Gap 20-30%, ...]
        
        Parameters:
        -----------
        term: 검증할 용어
        top_k: 반환할 사례 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.definition_store:
            logger.warning("  ⚠️  정의 검증 RAG 미구축")
            return []
        
        logger.info(f"[Validator] 정의 검증 사례 검색")
        logger.info(f"  용어: {term}")
        
        results = self.definition_store.similarity_search_with_score(
            term,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 사례 발견")
        for doc, score in results:
            case_term = doc.metadata.get('term', 'Unknown')
            gap_level = doc.metadata.get('gap_level', 'N/A')
            logger.info(f"    - {case_term} (Gap: {gap_level}, 유사도: {score:.2f})")
        
        return results
    
    def search_gap_analysis(
        self,
        data_point: str,
        original_def: str,
        needed_def: str
    ) -> List[tuple[Document, float]]:
        """
        Gap 분석 가이드 검색
        
        사용 시점:
        ----------
        원본 정의와 필요한 정의가 다를 때, 조정 방법 찾기
        
        예시:
        -----
        Input: 
          - data: "낚시인구 750만"
          - original: "연 1회 이상, 바다낚시만"
          - needed: "월 1회 이상, 전체 낚시"
        
        Output: [유사 Gap 사례, 조정 방법, ...]
        """
        if not self.definition_store:
            return []
        
        logger.info(f"[Validator] Gap 분석 가이드 검색")
        
        # Gap 설명 조합
        gap_query = f"{data_point}: 원본({original_def}) vs 필요({needed_def})"
        
        results = self.definition_store.similarity_search_with_score(
            gap_query,
            k=3,
            filter={"type": "gap_analysis"}
        )
        
        logger.info(f"  ✅ {len(results)}개 조정 가이드 발견")
        
        return results
    
    def validate_with_rag(
        self,
        data_point: str,
        claimed_value: Any,
        source_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        RAG 기반 데이터 검증
        
        프로세스:
        ---------
        1. 데이터 소스 검색 → 어디서 구할지
        2. 정의 사례 검색 → 정의 확인 방법
        3. 종합 검증 리포트
        
        Returns:
        --------
        검증 결과 + 추천 소스 + 정의 주의사항
        """
        logger.info(f"[Validator] RAG 기반 검증: {data_point}")
        
        result = {
            'data_point': data_point,
            'value': claimed_value,
            'recommended_sources': [],
            'definition_warnings': [],
            'validation_status': 'pending'
        }
        
        # 1. 데이터 소스 검색
        sources = self.search_data_source(data_point, top_k=3)
        if sources:
            result['recommended_sources'] = [
                {
                    'name': doc.metadata.get('source_name'),
                    'reliability': doc.metadata.get('reliability'),
                    'access': doc.metadata.get('access_method'),
                    'confidence': score
                }
                for doc, score in sources
            ]
        
        # 2. 정의 검증 사례
        definitions = self.search_definition_case(data_point, top_k=2)
        if definitions:
            result['definition_warnings'] = [
                {
                    'case': doc.metadata.get('term'),
                    'gap': doc.metadata.get('gap_description'),
                    'adjustment': doc.metadata.get('adjustment_method')
                }
                for doc, score in definitions
            ]
        
        # 3. 검증 상태
        if sources and sources[0][1] > 0.8:  # 높은 유사도
            result['validation_status'] = 'recommended'
        elif sources:
            result['validation_status'] = 'caution'
        else:
            result['validation_status'] = 'no_source_found'
        
        return result
    
    def load_kpi_library(self) -> Dict:
        """
        KPI 정의 라이브러리 로드
        
        Returns:
            KPI 라이브러리 dict
        """
        import yaml
        
        kpi_path = Path("data/raw/kpi_definitions.yaml")
        
        if not kpi_path.exists():
            logger.warning(f"KPI 라이브러리 파일 없음: {kpi_path}")
            return {}
        
        with open(kpi_path, 'r', encoding='utf-8') as f:
            library = yaml.safe_load(f)
        
        total = library.get('_meta', {}).get('total_kpis', 0)
        logger.info(f"✅ KPI 라이브러리 로드: {total}개")
        
        return library
    
    def validate_kpi_definition(
        self,
        metric_name: str,
        provided_definition: Dict
    ) -> Dict[str, Any]:
        """
        KPI 정의 검증 (s10 Industry KPI Library)
        
        Args:
            metric_name: KPI 이름
            provided_definition: {
                'numerator': str,
                'denominator': str,
                'unit': str,
                'scope': {
                    'includes': [...],
                    'excludes': [...]
                }
            }
        
        Returns:
            {
                'status': 'match' | 'partial_match' | 'mismatch' | 'not_found',
                'kpi_id': str,
                'standard_definition': {...},
                'gaps': [...],
                'recommendation': str,
                'comparability_score': float (0-1)
            }
        """
        
        logger.info(f"[Validator] KPI 정의 검증: {metric_name}")
        
        # KPI 라이브러리 로드
        library = self.load_kpi_library()
        
        if not library:
            return {
                'status': 'library_not_found',
                'message': 'KPI 라이브러리 파일 없음',
                'recommendation': 'scripts/build_kpi_library.py 실행 필요'
            }
        
        # KPI 검색
        kpi = self._search_kpi(metric_name, library)
        
        if not kpi:
            return {
                'status': 'not_found',
                'message': f"KPI '{metric_name}'가 라이브러리에 없습니다",
                'recommendation': 'manual_review',
                'create_new': True
            }
        
        logger.info(f"  ✅ KPI 발견: {kpi['kpi_id']}")
        
        # 정의 비교
        gaps = []
        
        # 1. 분자 비교
        provided_numerator = provided_definition.get('numerator', '')
        standard_numerator = kpi.get('formula', {}).get('numerator', '')
        
        if provided_numerator and provided_numerator != standard_numerator:
            gaps.append({
                'field': 'numerator',
                'provided': provided_numerator,
                'standard': standard_numerator,
                'severity': 'high'
            })
            logger.warning(f"  ⚠️  분자 불일치")
        
        # 2. 분모 비교
        provided_denominator = provided_definition.get('denominator', '')
        standard_denominator = kpi.get('formula', {}).get('denominator', '')
        
        if provided_denominator and standard_denominator != 'N/A' and provided_denominator != standard_denominator:
            gaps.append({
                'field': 'denominator',
                'provided': provided_denominator,
                'standard': standard_denominator,
                'severity': 'high'
            })
            logger.warning(f"  ⚠️  분모 불일치")
        
        # 3. 단위 비교
        provided_unit = provided_definition.get('unit', '')
        standard_unit = kpi.get('unit', '')
        
        if provided_unit and provided_unit != standard_unit:
            gaps.append({
                'field': 'unit',
                'provided': provided_unit,
                'standard': standard_unit,
                'severity': 'medium'
            })
            logger.warning(f"  ⚠️  단위 불일치")
        
        # 4. Scope 비교
        scope_gaps = self._compare_scope(
            provided_definition.get('scope', {}),
            kpi.get('scope', {})
        )
        gaps.extend(scope_gaps)
        
        # 상태 결정
        if len(gaps) == 0:
            status = 'match'
            logger.info(f"  ✅ 완전 일치")
        elif any(g['severity'] == 'high' for g in gaps):
            status = 'mismatch'
            logger.warning(f"  ❌ 불일치 (high severity)")
        else:
            status = 'partial_match'
            logger.info(f"  ⚠️  부분 일치")
        
        # 비교 가능성 점수
        comparability_score = 1.0 - (len(gaps) * 0.2)
        comparability_score = max(0, comparability_score)
        
        # 권고사항
        if status == 'match':
            recommendation = '✅ 표준 정의와 일치. 비교 가능'
        elif status == 'mismatch':
            recommendation = '❌ 정의 불일치. 비교 불가 → 표준화 필요'
        else:
            recommendation = '⚠️  부분 일치. 주의하여 비교'
        
        logger.info(f"  비교 가능성: {comparability_score*100:.0f}%")
        
        return {
            'status': status,
            'kpi_id': kpi['kpi_id'],
            'standard_definition': kpi,
            'gaps': gaps,
            'recommendation': recommendation,
            'comparability_score': comparability_score
        }
    
    def _search_kpi(self, metric_name: str, library: Dict) -> Optional[Dict]:
        """KPI 검색"""
        
        metric_lower = metric_name.lower()
        
        # 모든 카테고리 검색
        for key in library:
            if key.endswith('_kpis'):
                for kpi in library[key]:
                    kpi_name_lower = kpi['metric_name'].lower()
                    
                    # 정확한 매칭
                    if kpi_name_lower == metric_lower:
                        return kpi
                    
                    # 부분 매칭
                    if metric_lower in kpi_name_lower or kpi_name_lower in metric_lower:
                        return kpi
        
        return None
    
    def _compare_scope(
        self,
        provided_scope: Dict,
        standard_scope: Dict
    ) -> List[Dict]:
        """Scope 비교"""
        
        gaps = []
        
        # Includes 비교
        provided_includes = set(provided_scope.get('includes', []))
        standard_includes = set(standard_scope.get('includes', []))
        
        missing_includes = standard_includes - provided_includes
        extra_includes = provided_includes - standard_includes
        
        if missing_includes:
            gaps.append({
                'field': 'scope.includes',
                'provided': list(provided_includes),
                'standard': list(standard_includes),
                'missing': list(missing_includes),
                'severity': 'medium'
            })
        
        # Excludes 비교
        provided_excludes = set(provided_scope.get('excludes', []))
        standard_excludes = set(standard_scope.get('excludes', []))
        
        missing_excludes = standard_excludes - provided_excludes
        
        if missing_excludes:
            gaps.append({
                'field': 'scope.excludes',
                'provided': list(provided_excludes),
                'standard': list(standard_excludes),
                'missing': list(missing_excludes),
                'severity': 'high'  # 제외 항목 중요
            })
        
        return gaps


# Validator RAG 인스턴스 (싱글톤)
_validator_rag_instance = None

def get_validator_rag() -> ValidatorRAG:
    """Validator RAG 싱글톤 인스턴스 반환"""
    global _validator_rag_instance
    if _validator_rag_instance is None:
        _validator_rag_instance = ValidatorRAG()
    return _validator_rag_instance

