"""
Validator RAG Agent Module

Validator (Rachel) 에이전트의 RAG 기반 데이터 검증 시스템입니다.

핵심 개념:
-----------
1. **Data Source Discovery**: 데이터 소스 자동 검색 및 추천
2. **Definition Validation**: 정의 검증 사례 참조
3. **Gap Analysis**: 정의 불일치 분석 가이드
4. **Creative Sourcing**: 창의적 데이터 소싱 방법
5. **Definite Data Search**: 확정 데이터 우선 검색 (v7.6.0+)

Validator의 핵심 역할:
----------------------
1. 확정 데이터 검색 (Estimator Phase 2, v7.6.0+) ⭐ 최우선!
2. 데이터 정의 검증
3. 단위 자동 변환 (v7.6.1+)
4. Relevance 검증 (v7.6.1+)
5. 신뢰도 평가

RAG Collections:
----------------
- data_sources_registry: 데이터 소스 목록 (24개, v7.6.0+)
- definition_validation_cases: 정의 검증 사례 (100개)

v7.6.0+ 주요 변경:
------------------
- search_definite_data(): Estimator 추정 전 확정 데이터 검색
- 단위 자동 변환 (갑/년 → 갑/일 등)
- Relevance 검증 (GDP 오류 방지)
- 94.7% 커버리지 달성
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

# v7.3.2: Estimator 통합 (추정치 검증용)
from umis_rag.agents.estimator import get_estimator_rag


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
        
        # v7.3.2: Estimator 연결 (교차 검증용)
        self.estimator = None  # Lazy 초기화
        
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
    
    def search_definite_data(
        self,
        question: str,
        context: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        확정 데이터 검색 (추정 전 필수 확인!)
        
        역할:
        -----
        - Estimator 추정 전 확정 데이터 존재 여부 확인
        - 공식 통계, 정부 데이터, 벤치마크 검색
        - 값이 있으면 즉시 반환 (추정 불필요)
        
        검색 범위:
        ----------
        1. data_sources_registry (공식 통계)
        2. 메타데이터에서 값 추출
        3. 신뢰도 높은 것만 (0.85+)
        
        Args:
            question: 질문 (예: "한국 담배 판매량은?")
            context: 맥락 (domain, region 등)
        
        Returns:
            {
                'value': 87671233,
                'unit': '갑/일',
                'source': '기획재정부',
                'confidence': 1.0,
                'definition': '주민등록 기준',
                'last_updated': '2023'
            } 또는 None
        
        Example:
            >>> validator = ValidatorRAG()
            >>> result = validator.search_definite_data("한국 인구는?")
            >>> if result:
            ...     print(f"{result['value']}명 (출처: {result['source']})")
        """
        if not self.source_store:
            logger.warning("  ⚠️  data_sources_registry 없음 (구축 필요)")
            return None
        
        logger.info(f"[Validator] 확정 데이터 검색: {question}")
        
        # Context 정보 추출
        domain_str = ""
        if context and hasattr(context, 'domain'):
            domain_str = f"{context.domain} " if context.domain != "General" else ""
        
        # 검색 쿼리 구성
        search_query = f"{domain_str}{question}".strip()
        logger.info(f"  검색: {search_query}")
        
        # data_sources_registry 검색 (top 3)
        results = self.source_store.similarity_search_with_score(
            search_query,
            k=3
        )
        
        if not results:
            logger.info("  → 확정 데이터 없음")
            return None
        
        # 높은 유사도 & 값이 있는 것만
        for doc, score in results:
            logger.info(f"  후보: {doc.metadata.get('source_name', 'Unknown')} (유사도: {score:.2f})")
            
            # v7.6.0: threshold 0.75
            if score > 0.75:
                metadata = doc.metadata
                
                # 메타데이터에서 값 추출
                if 'value' in metadata and metadata['value'] is not None:
                    # ⭐ v7.6.1: Relevance 검증 추가!
                    if not self._is_relevant(question, doc, context):
                        logger.warning(f"  ⚠️  유사도 높지만 관련성 낮음 → 스킵")
                        continue
                    
                    logger.info(f"  ✅ 확정 데이터 발견! (relevance 검증 통과)")
                    
                    # ⭐ v7.6.1: 단위 변환 추가!
                    result_data = {
                        'value': metadata['value'],
                        'unit': metadata.get('unit', ''),
                        'source': metadata.get('source_name', 'Unknown'),
                        'confidence': 1.0,
                        'definition': metadata.get('definition', ''),
                        'last_updated': metadata.get('year', ''),
                        'access_method': metadata.get('access_method', ''),
                        'reliability': metadata.get('reliability', 'high'),
                        'document': doc.page_content
                    }
                    
                    # 단위 변환 시도
                    converted = self._convert_unit_if_needed(question, result_data, doc)
                    if converted:
                        result_data = converted
                    
                    return result_data
        
        logger.info("  → 확정 데이터 없음 (유사도 낮거나 값 없음)")
        return None
    
    def _is_relevant(
        self,
        question: str,
        doc: Any,
        context: Optional[Any] = None
    ) -> bool:
        """
        Relevance 검증 (v7.6.1)
        
        유사도가 높아도 실제로 관련 없는 데이터 필터링
        예: "시장 규모" → GDP (X)
        
        검증 항목:
        1. 비호환 조합 체크 (시장≠GDP 등)
        2. 핵심 키워드 매칭
        3. Scale 검증
        """
        metadata = doc.metadata
        doc_content = doc.page_content.lower()
        question_lower = question.lower()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 비호환 조합 체크
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        INCOMPATIBLE_PAIRS = [
            # (질문 키워드, 데이터 카테고리) = 비호환
            (['시장', '규모'], ['gdp', '국내총생산']),
            (['수업료', '학원'], ['최저임금', '법정']),
            (['음식점', '카페'], ['인구통계']),
            (['판매량', '소비'], ['인구', '가구']),
        ]
        
        data_point = metadata.get('data_point', '').lower()
        category = metadata.get('category', '').lower()
        
        for q_keywords, d_keywords in INCOMPATIBLE_PAIRS:
            # 질문에 키워드 있고
            has_q = any(kw in question_lower for kw in q_keywords)
            # 데이터에 비호환 키워드 있으면
            has_d = any(kw in data_point or kw in category or kw in doc_content for kw in d_keywords)
            
            if has_q and has_d:
                logger.info(f"    비호환: {q_keywords} vs {d_keywords}")
                return False
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 핵심 키워드 필수 매칭
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 질문의 핵심 명사 추출
        core_keywords = self._extract_core_keywords(question_lower)
        
        if core_keywords:
            # 핵심 키워드 중 최소 1개는 있어야
            matched = any(kw in doc_content for kw in core_keywords)
            
            if not matched:
                logger.info(f"    키워드 불일치: {core_keywords}")
                return False
        
        # 통과
        logger.info(f"    ✅ Relevance 검증 통과")
        return True
    
    def _extract_core_keywords(self, question: str) -> list:
        """질문에서 핵심 키워드 추출"""
        
        # 주요 명사 키워드 매핑
        keyword_map = {
            '담배': ['담배', '흡연'],
            '음악': ['음악', '음원'],
            '스트리밍': ['스트리밍', '구독'],
            '음식점': ['음식점', '식당', '레스토랑'],
            '카페': ['카페', '커피'],
            '학원': ['학원', '교육'],
            '수업료': ['수업료', '학비'],
        }
        
        keywords = []
        for key, variants in keyword_map.items():
            if any(v in question for v in variants):
                keywords.extend(variants)
        
        return keywords
    
    def _convert_unit_if_needed(
        self,
        question: str,
        result_data: dict,
        doc: Any
    ) -> Optional[dict]:
        """
        단위 변환 (v7.6.1)
        
        질문에서 요청 단위를 추출하고
        필요 시 자동 변환
        
        예: "하루에 판매되는" → 갑/일 필요
            데이터: 32,000,000,000 갑/년
            변환: 32,000,000,000 / 365 = 87,671,233 갑/일
        """
        current_unit = result_data.get('unit', '')
        
        # 질문에서 요청 단위 추출
        requested_unit = self._extract_requested_unit(question)
        
        if not requested_unit or not current_unit:
            return None
        
        # 단위 변환 필요 여부
        if current_unit == requested_unit:
            return None  # 변환 불필요
        
        # 변환 규칙
        CONVERSIONS = {
            ('갑/년', '갑/일'): ('divide', 365),
            ('원/년', '원/월'): ('divide', 12),
            ('개/년', '개/일'): ('divide', 365),
            
            ('갑/일', '갑/년'): ('multiply', 365),
            ('원/월', '원/년'): ('multiply', 12),
        }
        
        conversion_key = (current_unit, requested_unit)
        
        if conversion_key in CONVERSIONS:
            operation, factor = CONVERSIONS[conversion_key]
            
            original_value = result_data['value']
            
            if operation == 'divide':
                converted_value = original_value / factor
            else:  # multiply
                converted_value = original_value * factor
            
            logger.info(f"  🔄 단위 변환: {original_value:,.0f} {current_unit} → {converted_value:,.0f} {requested_unit}")
            
            # 변환된 결과 반환
            converted_data = result_data.copy()
            converted_data['value'] = converted_value
            converted_data['unit'] = requested_unit
            converted_data['original_value'] = original_value
            converted_data['original_unit'] = current_unit
            converted_data['conversion_applied'] = True
            converted_data['conversion_formula'] = f"{operation} {factor}"
            
            return converted_data
        
        # 변환 규칙 없음
        return None
    
    def _extract_requested_unit(self, question: str) -> Optional[str]:
        """
        질문에서 요청 단위 추출
        
        예: "하루에 판매되는" → "갑/일"
            "연간 판매량은" → "갑/년"
            "월평균 매출은" → "원/월"
        """
        question_lower = question.lower()
        
        # 시간 단위
        if '하루' in question or '일일' in question or '매일' in question:
            if '갑' in question:
                return '갑/일'
            elif '개' in question:
                return '개/일'
            else:
                return '일'
        
        if '연간' in question or '년간' in question or '1년' in question:
            if '갑' in question:
                return '갑/년'
            elif '원' in question or '매출' in question:
                return '원/년'
        
        if '월' in question or '한 달' in question:
            if '원' in question or '매출' in question:
                return '원/월'
        
        return None
    
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


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # v7.7.0: Estimator 교차 검증 (5-Phase)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def validate_estimation(
        self,
        question: str,
        claimed_value: float,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        추정값의 합리성 검증 (Estimator 5-Phase 교차 검증)
        
        원칙 (v7.7.0):
        -------------
        1. 직접 추정 금지 ❌
        2. Estimator에게 교차 검증 요청 ✅ (Phase 0→1→2→3→4 자동)
        3. 비교 및 판단
        
        Args:
            question: 질문 (예: "B2B SaaS Churn Rate는?")
            claimed_value: 주장된 값 (예: 0.08)
            context: 맥락 (domain, region 등)
        
        Returns:
            {
                'claimed_value': 0.08,
                'estimator_value': 0.06,
                'estimator_phase': 2,  # v7.7.0: Phase 0-4
                'estimator_confidence': 0.85,
                'estimator_reasoning': {...},
                'difference_pct': 0.33,
                'validation_result': 'caution'
            }
        
        Example:
            >>> validator = ValidatorRAG()
            >>> result = validator.validate_estimation(
            ...     "B2B SaaS Churn Rate는?",
            ...     claimed_value=0.08,
            ...     context={'domain': 'B2B_SaaS'}
            ... )
            >>> print(result['validation_result'])  # 'caution'
        """
        logger.info(f"[Validator] 추정값 검증: {question} = {claimed_value}")
        
        # Estimator Lazy 초기화
        if self.estimator is None:
            self.estimator = get_estimator_rag()
            logger.info("  ✅ Estimator 연결 (5-Phase)")
        
        # Estimator에게 교차 검증 요청 (Phase 0→1→2→3→4 자동 시도)
        est_result = self.estimator.estimate(
            question=question,
            domain=context.get('domain') if context else None,
            region=context.get('region') if context else None
        )
        
        if not est_result:
            return {
                'validation': 'unable',
                'reason': 'Estimator 추정 실패'
            }
        
        # 비교
        diff_pct = abs(claimed_value - est_result.value) / est_result.value if est_result.value else 0
        
        validation = {
            'claimed_value': claimed_value,
            'estimator_value': est_result.value,
            'estimator_confidence': est_result.confidence,
            'estimator_phase': est_result.phase,  # v7.7.0: tier → phase
            
            # v7.7.0: 상세 근거 포함
            'estimator_reasoning': est_result.reasoning_detail,
            'estimator_components': est_result.component_estimations,
            'estimator_trace': est_result.estimation_trace,
            
            'difference_pct': diff_pct,
            
            'validation_result': (
                'pass' if diff_pct < 0.30 else
                'caution' if diff_pct < 0.50 else
                'fail'
            ),
            
            'recommendation': self._generate_recommendation(
                claimed_value, est_result, diff_pct
            )
        }
        
        logger.info(f"  검증: {validation['validation_result']} (차이 {diff_pct:.0%})")
        
        return validation
    
    def _generate_recommendation(
        self,
        claimed: float,
        est_result,
        diff_pct: float
    ) -> str:
        """검증 결과 기반 권장사항"""
        
        lines = []
        lines.append(f"주장값: {claimed}")
        lines.append(f"Estimator 추정: {est_result.value} (Phase {est_result.phase}, 신뢰도 {est_result.confidence:.0%})")
        lines.append(f"차이: {diff_pct:.0%}")
        lines.append(f"")
        
        if diff_pct < 0.30:
            lines.append("✅ 검증 통과: 합리적 범위")
        elif diff_pct < 0.50:
            lines.append("⚠️  주의: 차이가 다소 큼")
            lines.append(f"Estimator 근거 확인 권장:")
            if est_result.reasoning_detail:
                lines.append(f"  - 전략: {est_result.reasoning_detail.get('method')}")
                lines.append(f"  - 증거: {est_result.reasoning_detail.get('evidence_count')}개")
        else:
            lines.append("❌ 검증 실패: 차이가 매우 큼")
            lines.append(f"Estimator 추정 재검토 필요")
        
        return "\n".join(lines)


    def search_historical_data(
        self,
        market: str,
        years: range
    ) -> Dict[str, Any]:
        """
        과거 데이터 탐색 및 수집 (v7.8.0 신규)
        
        Observer Timeline 분석을 위한 과거 데이터 수집.
        Estimator 협업으로 누락 데이터 추정.
        
        Args:
            market: 시장 이름
            years: range(2015, 2026) → 2015-2025
        
        Returns:
            {
                'market_size_by_year': {year: {value, source, reliability}, ...},
                'players_by_year': {year: {player: {share, source}, ...}, ...},
                'events': [Event, ...],
                'hhi_by_year': {year: hhi, ...},
                'player_count_by_year': {year: count, ...},
                'data_quality': {verified_ratio, avg_confidence, ...}
            }
        """
        logger.info(f"[Validator] 과거 데이터 수집: {market} ({years.start}-{years.stop-1})")
        
        result = {
            'market_size_by_year': {},
            'players_by_year': {},
            'events': [],
            'hhi_by_year': {},
            'player_count_by_year': {},
            'data_gaps': {'missing_years': [], 'estimator_requests': []}
        }
        
        # Step 1: 공식 통계 검색
        logger.info("  Step 1: 공식 통계 검색")
        official_data = self._search_official_statistics(market, years)
        result['market_size_by_year'].update(official_data.get('market_size', {}))
        
        # Step 2: 산업 리포트 검색 (RAG)
        logger.info("  Step 2: 산업 리포트 검색 (RAG)")
        industry_data = self._search_industry_reports_rag(market, years)
        result['market_size_by_year'].update(industry_data.get('market_size', {}))
        
        # Step 3: 공시 데이터 (상장사)
        logger.info("  Step 3: 공시 데이터 검색")
        public_data = self._search_public_filings(market, years)
        result['players_by_year'].update(public_data.get('players', {}))
        
        # Step 4: 뉴스/사건
        logger.info("  Step 4: 주요 사건 검색")
        events = self._search_news_events(market, years)
        result['events'] = events
        
        # Step 5: Gap 식별
        logger.info("  Step 5: 데이터 Gap 식별")
        gaps = self._identify_data_gaps(result, years)
        result['data_gaps'] = gaps
        
        # Step 6: Estimator 협업 (Gap 채우기)
        if gaps['missing_years']:
            logger.info(f"  Step 6: Estimator 협업 ({len(gaps['missing_years'])}개 누락 연도)")
            result = self._fill_gaps_with_estimator(result, gaps)
        
        # Step 7: 데이터 품질 평가
        result['data_quality'] = self._assess_data_quality(result, years)
        
        logger.info(f"  ✅ 과거 데이터 수집 완료 (품질: {result['data_quality'].get('grade', 'N/A')})")
        
        return result
    
    def _search_official_statistics(self, market: str, years: range) -> Dict:
        """공식 통계 검색 (통계청, 한국은행 등)"""
        # TODO: 실제 API 연동 또는 웹 검색
        # 현재는 placeholder
        logger.info("    (구현 예정: 통계청 API)")
        return {'market_size': {}}
    
    def _search_industry_reports_rag(self, market: str, years: range) -> Dict:
        """산업 리포트 검색 (RAG 활용)"""
        # data_sources_registry에서 검색
        if self.source_store:
            results = self.source_store.similarity_search(
                f"{market} market size historical data",
                k=5
            )
            logger.info(f"    ✅ RAG: {len(results)}개 소스 발견")
        
        # TODO: 실제 리포트에서 데이터 추출
        return {'market_size': {}}
    
    def _search_public_filings(self, market: str, years: range) -> Dict:
        """공시 데이터 검색 (DART API 등)"""
        # TODO: DART API 연동
        logger.info("    (구현 예정: DART API)")
        return {'players': {}}
    
    def _search_news_events(self, market: str, years: range) -> List[Dict]:
        """뉴스에서 주요 사건 추출"""
        # TODO: 뉴스 검색 및 사건 추출
        logger.info("    (구현 예정: 뉴스 검색)")
        return []
    
    def _identify_data_gaps(self, collected_data: Dict, years: range) -> Dict:
        """데이터 Gap 식별"""
        gaps = {'missing_years': [], 'estimator_requests': []}
        
        # 누락 연도 파악
        for year in years:
            if year not in collected_data['market_size_by_year']:
                gaps['missing_years'].append(year)
                
                # Estimator 요청 준비
                gaps['estimator_requests'].append({
                    'type': 'market_size_interpolation',
                    'year': year,
                    'market': collected_data.get('market'),
                    'known_data': collected_data['market_size_by_year']
                })
        
        logger.info(f"    Gap: {len(gaps['missing_years'])}개 누락 연도")
        return gaps
    
    def _fill_gaps_with_estimator(self, data: Dict, gaps: Dict) -> Dict:
        """Estimator 협업으로 Gap 채우기"""
        try:
            from umis_rag.agents.estimator import get_estimator_rag
            estimator = get_estimator_rag()
            
            for request in gaps['estimator_requests']:
                if request['type'] == 'market_size_interpolation':
                    # 보간 요청
                    # TODO: Estimator.estimate() 호출
                    logger.info(f"      Estimator: {request['year']}년 추정 중...")
                    
                    # Placeholder
                    # result = estimator.estimate(...)
                    # data['market_size_by_year'][request['year']] = result
        
        except Exception as e:
            logger.warning(f"    ⚠️ Estimator 협업 실패: {e}")
        
        return data
    
    def _assess_data_quality(self, data: Dict, years: range) -> Dict:
        """데이터 품질 평가"""
        total_years = len(list(years))
        verified_years = sum(
            1 for y, d in data['market_size_by_year'].items()
            if d.get('reliability') == 'high'
        )
        estimated_years = sum(
            1 for y, d in data['market_size_by_year'].items()
            if d.get('reliability') == 'estimated'
        )
        
        verified_ratio = verified_years / total_years if total_years > 0 else 0
        
        # 등급 판정
        if verified_ratio >= 0.5:
            grade = 'A (High)'
        elif verified_ratio >= 0.3:
            grade = 'B (Medium)'
        else:
            grade = 'C (Low)'
        
        return {
            'total_years': total_years,
            'verified_years': verified_years,
            'estimated_years': estimated_years,
            'verified_ratio': verified_ratio,
            'grade': grade
        }


# Validator RAG 인스턴스 (싱글톤)
_validator_rag_instance = None

def get_validator_rag() -> ValidatorRAG:
    """Validator RAG 싱글톤 인스턴스 반환"""
    global _validator_rag_instance
    if _validator_rag_instance is None:
        _validator_rag_instance = ValidatorRAG()
    return _validator_rag_instance

