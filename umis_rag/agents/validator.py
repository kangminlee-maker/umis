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
        
        # v7.9.0: API 데이터 소스 (DART, KOSIS)
        self.dart_api_key = settings.dart_api_key
        self.kosis_api_key = settings.kosis_api_key
        
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
        
        역할 (v7.8.1 엄격화):
        ---------------------
        - 이미 확인된 데이터를 재사용 (캐싱)
        - 100% 매칭 또는 95% 이상 유사도만 허용
        - 핵심 키워드 완전 일치 필수
        
        원칙:
        -----
        1. Phase 2는 "재사용"이 목적 (새로운 추정 X)
        2. 거의 완벽하게 매칭될 때만 사용
        3. 의심스러우면 Phase 3/4로 넘김
        
        검색 범위:
        ----------
        1. data_sources_registry (공식 통계)
        2. 메타데이터에서 값 추출
        3. 엄격한 Relevance 검증
        
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
        region_str = ""
        if context and hasattr(context, 'domain'):
            domain_str = f"{context.domain} " if context.domain != "General" else ""
        if context and hasattr(context, 'region'):
            region_str = f"{context.region} " if context.region else ""
        
        # v7.9.0: 검색 쿼리 구성 (정규화 없이 원본 사용)
        # 이유: 데이터베이스에 정규화되지 않은 원본이 저장되어 있음
        # 향후: 데이터베이스 재구축 시 정규화 적용 예정
        search_query = f"{region_str}{domain_str}{question}".strip()
        logger.info(f"  검색: {search_query}")
        
        # data_sources_registry 검색 (top 3)
        results = self.source_store.similarity_search_with_score(
            search_query,
            k=3
        )
        
        if not results:
            logger.info("  → 확정 데이터 없음")
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # v7.9.0: Phase 2 임계값 강화 (과도 매칭 방지)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ChromaDB L2 distance (실제 측정값):
        #   - 0.70~0.90: 거의 동일한 질문 ("한국 인구" vs "한국 총인구")
        #   - 0.90~1.10: 매우 유사 ("한국 인구" vs "담배 판매량")
        #   - 1.10~1.30: Registry 내 다른 항목 ("한국 인구" vs "서울 인구")
        #   - 1.30+: 완전히 다른 개념
        # 
        # Phase 2 목적: 이미 확인한 데이터 재사용 (캐싱)
        # 
        # v7.9.0 변경:
        # - v7.8.1: < 0.90 (100%), < 1.10 (95%)
        # - v7.9.0: < 0.85 (100%), 0.85~0.95 제거됨
        # 
        # 이유:
        # - "SaaS 서비스 ARPU" (0.979) → "B2B SaaS ARPU" 매칭은 부적절
        # - Phase 2는 "거의 완벽한 매칭"만 허용 (재사용 목적)
        # - 애매한 케이스는 Phase 3/4로 위임 (추정 필요)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        for doc, score in results:
            logger.info(f"  후보: {doc.metadata.get('source_name', 'Unknown')} (distance: {score:.3f})")
            
            # v7.9.0: 엄격한 임계값 (거의 완벽한 매칭만)
            if score < 0.85:
                confidence_level = "perfect"
                confidence = 1.0
                logger.info(f"    → 거의 완벽한 매칭 (100%)")
            else:
                # v7.9.0: 0.85 이상은 모두 스킵 → Phase 3/4로 위임
                logger.info(f"    → 유사도 불충분 ({score:.3f}) → Phase 3/4로 위임")
                continue
            
            metadata = doc.metadata
            
            # 메타데이터에서 값 추출
            if 'value' not in metadata or metadata['value'] is None:
                logger.info(f"    → 값 없음 → 스킵")
                continue
            
            # ⭐ 엄격한 Relevance 검증!
            relevance_result = self._is_relevant_strict(question, doc, context)
            
            if not relevance_result['is_relevant']:
                logger.warning(f"    ⚠️  Relevance 검증 실패: {relevance_result['reason']}")
                continue
            
            logger.info(f"    ✅ Relevance 검증 통과: {relevance_result['matched_keywords']}")
            logger.info(f"  ✅ 확정 데이터 발견! (신뢰도: {confidence:.0%})")
            
            # 결과 반환
            result_data = {
                'value': metadata['value'],
                'unit': metadata.get('unit', ''),
                'source': metadata.get('source_name', 'Unknown'),
                'confidence': confidence,
                'confidence_level': confidence_level,
                'similarity_score': score,
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
        
        logger.info("  → 확정 데이터 없음 (유사도 낮거나 관련성 없음)")
        return None
    
    def _normalize_question(self, question: str) -> str:
        """
        질문 정규화 (v7.9.0)
        
        목적:
        - 동일한 의미의 다양한 표현을 통일
        - 유사도 매칭 정확도 향상
        
        정규화 규칙:
        1. 대소문자 통일 (소문자)
        2. 불필요한 공백 제거
        3. 조사 제거 ("은?", "는?", "의", "를" 등)
        4. 불필요한 수식어 제거 ("평균", "대략", "약" 등)
        5. 질문 형식 제거 ("?", "인가", "입니까" 등)
        
        Args:
            question: 원본 질문
        
        Returns:
            정규화된 질문
        
        Example:
            >>> self._normalize_question("B2B SaaS의 평균 ARPU는?")
            "b2b saas arpu"
            >>> self._normalize_question("한국  음식점  수는  몇 개?")
            "한국 음식점 수"
        """
        import re
        
        # 1. 소문자 변환
        normalized = question.lower()
        
        # 2. 조사 제거 (한국어)
        # "은?", "는?", "의", "를", "을", "가", "이" 등
        normalized = re.sub(r'[은는의를을가이]\??', '', normalized)
        
        # 3. 불필요한 수식어 제거
        # "평균", "대략", "약", "정도" 등
        remove_words = ['평균', '대략', '약', '정도', '보통', '일반적', '일반적으로']
        for word in remove_words:
            normalized = normalized.replace(word, '')
        
        # 4. 질문 형식 제거
        # "?", "인가", "입니까", "인지", "몇" 등
        normalized = re.sub(r'\?+', '', normalized)
        normalized = re.sub(r'(인가|입니까|인지|몇|개)', '', normalized)
        
        # 5. 여러 공백을 하나로
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 6. 앞뒤 공백 제거
        normalized = normalized.strip()
        
        return normalized
    
    def _is_relevant_strict(
        self,
        question: str,
        doc: Any,
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        엄격한 Relevance 검증 (v7.8.1)
        
        Phase 2는 "재사용"이 목적이므로
        핵심 키워드가 거의 완벽하게 일치해야 함
        
        검증 항목:
        1. 핵심 명사 완전 일치 (필수)
        2. 도메인 키워드 일치
        3. 단위 호환성
        4. 비호환 조합 차단
        
        Returns:
            {
                'is_relevant': bool,
                'reason': str,
                'matched_keywords': List[str],
                'confidence': float
            }
        """
        metadata = doc.metadata
        doc_content = doc.page_content.lower()
        question_lower = question.lower()
        
        data_point = metadata.get('data_point', '').lower()
        category = metadata.get('category', '').lower()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 핵심 명사 추출 (엄격)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        question_nouns = self._extract_core_nouns_strict(question_lower)
        data_nouns = self._extract_core_nouns_strict(data_point)
        
        if not question_nouns:
            return {
                'is_relevant': False,
                'reason': '질문에서 핵심 명사 추출 실패',
                'matched_keywords': [],
                'confidence': 0.0
            }
        
        # 교집합 계산
        matched_nouns = set(question_nouns) & set(data_nouns)
        match_ratio = len(matched_nouns) / len(question_nouns) if question_nouns else 0
        
        # ⭐ 핵심: 최소 60% 이상 매칭 필요
        if match_ratio < 0.6:
            return {
                'is_relevant': False,
                'reason': f'핵심 명사 일치율 낮음 ({match_ratio:.0%}): 질문 {question_nouns} vs 데이터 {data_nouns}',
                'matched_keywords': list(matched_nouns),
                'confidence': match_ratio
            }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 비호환 조합 차단
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        INCOMPATIBLE_PAIRS = [
            # (질문 키워드, 데이터 키워드) = 비호환
            (['양자', '양자컴퓨터'], ['가구', '인구']),
            (['메타버스', '가상'], ['이탈률', '비율']),
            (['화성', '우주', '식민지'], ['인구', '서울']),
            (['ai', '에이전트', '인공지능'], ['음악', '스트리밍']),
            (['드론', '배송'], ['인구']),
            (['수직농장', '농장'], ['담배', '흡연']),
            (['블록체인', '암호화폐'], ['샴푸', '담배']),
            
            # 기존
            (['시장', '규모'], ['gdp', '국내총생산']),
            (['수업료', '학원'], ['최저임금']),
            (['음식점', '카페'], ['인구통계']),
        ]
        
        for q_keywords, d_keywords in INCOMPATIBLE_PAIRS:
            has_q = any(kw in question_lower for kw in q_keywords)
            has_d = any(kw in data_point or kw in category or kw in doc_content for kw in d_keywords)
            
            if has_q and has_d:
                return {
                    'is_relevant': False,
                    'reason': f'비호환 조합: 질문({q_keywords}) vs 데이터({d_keywords})',
                    'matched_keywords': [],
                    'confidence': 0.0
                }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. 단위 호환성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        unit_compatible = self._check_unit_compatibility(question, metadata.get('unit', ''))
        
        if not unit_compatible:
            return {
                'is_relevant': False,
                'reason': f'단위 비호환: 질문 vs 데이터 {metadata.get("unit")}',
                'matched_keywords': list(matched_nouns),
                'confidence': match_ratio * 0.5
            }
        
        # 통과!
        return {
            'is_relevant': True,
            'reason': 'OK',
            'matched_keywords': list(matched_nouns),
            'confidence': match_ratio
        }
    
    def _extract_core_nouns_strict(self, text: str) -> List[str]:
        """
        핵심 명사 엄격 추출 (v7.8.1)
        
        목적: 거의 완벽한 매칭 판단용
        """
        # 주요 명사 사전
        NOUN_DICT = {
            # 인구/가구
            '인구', '총인구', '서울', '성인',
            '가구', '가구수',
            
            # 경제
            'gdp', '국내총생산', '소득',
            
            # 산업
            '담배', '샴푸', '음식점', '카페',
            '판매', '판매량', '소비', '소비량',
            
            # SaaS
            'saas', '이탈', '이탈률', 'churn',
            'ltv', 'cac', '전환율',
            
            # 시장
            '시장', '규모', '음악', '스트리밍',
            
            # 기타
            '흡연', '흡연율', '최저임금',
            
            # 미래/가상
            '양자', '양자컴퓨터', '메타버스', '화성',
            '식민지', 'ai', '에이전트', '드론',
            '수직농장', '블록체인',
        }
        
        # 텍스트에서 명사 추출
        found_nouns = []
        for noun in NOUN_DICT:
            if noun in text:
                found_nouns.append(noun)
        
        return found_nouns
    
    def _check_unit_compatibility(self, question: str, data_unit: str) -> bool:
        """
        단위 호환성 체크 (v7.8.1)
        
        질문과 데이터 단위가 합리적으로 연결되는지
        """
        if not data_unit:
            return True  # 단위 없으면 통과
        
        question_lower = question.lower()
        data_unit_lower = data_unit.lower()
        
        # 단위 그룹
        COMPATIBLE_GROUPS = [
            # 인구 관련
            {'명', 'people', '인구', '가구'},
            
            # 돈 관련
            {'원', 'usd', 'won', '달러'},
            
            # 수량 관련
            {'개', '갑', '잔', 'kg', '리터'},
            
            # 비율 관련
            {'비율', 'ratio', '%', '퍼센트'},
            
            # 시간 관련
            {'시간', '일', '개월', '년'},
        ]
        
        # 질문에서 요구하는 단위 그룹 찾기
        question_group = None
        for group in COMPATIBLE_GROUPS:
            if any(unit_kw in question_lower for unit_kw in group):
                question_group = group
                break
        
        # 데이터 단위 그룹 찾기
        data_group = None
        for group in COMPATIBLE_GROUPS:
            if any(unit_kw in data_unit_lower for unit_kw in group):
                data_group = group
                break
        
        # 둘 다 그룹이 있으면 같은 그룹이어야 함
        if question_group and data_group:
            return question_group == data_group
        
        # 그룹 없으면 통과
        return True
    
    def _is_relevant(
        self,
        question: str,
        doc: Any,
        context: Optional[Any] = None
    ) -> bool:
        """
        Relevance 검증 (v7.6.1, deprecated)
        
        ⚠️ v7.8.1부터 _is_relevant_strict 사용
        
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
        """
        공식 통계 검색 (통계청, 한국은행 등)
        
        Args:
            market: 시장명
            years: 연도 범위
        
        Returns:
            Dict with market_size data
        
        Note:
            현재는 KOSIS API 연동 준비 중
            수동 수집 데이터 사용 권장
        """
        
        result = {'market_size': {}}
        
        # KOSIS API가 설정되어 있다면
        if hasattr(self, 'kosis_api_key') and self.kosis_api_key:
            try:
                # KOSIS search_kosis_data() 메서드 활용
                kosis_result = self.search_kosis_data(
                    search_term=market,
                    data_type='market_size'
                )
                
                if kosis_result:
                    logger.info(f"    ✅ KOSIS API: 데이터 발견")
                    result['market_size'] = kosis_result.get('data', {})
                    return result
            except Exception as e:
                logger.warning(f"    ⚠️ KOSIS API 호출 실패: {e}")
        
        # Fallback: RAG에서 통계 데이터 검색
        if self.source_store:
            try:
                query = f"{market} official statistics 시장 규모 통계청"
                search_results = self.source_store.similarity_search(query, k=3)
                
                if search_results:
                    logger.info(f"    ✅ RAG 통계 소스: {len(search_results)}개 발견")
                    # 메타데이터에서 데이터 추출
                    for res in search_results:
                        if hasattr(res, 'metadata') and 'year' in res.metadata:
                            year = res.metadata['year']
                            if 'market_size' in res.metadata:
                                result['market_size'][str(year)] = res.metadata['market_size']
            except Exception as e:
                logger.warning(f"    ⚠️ RAG 검색 실패: {e}")
        
        logger.info("    ℹ️  대안: https://kosis.kr 수동 확인")
        return result
    
    def _search_industry_reports_rag(self, market: str, years: range) -> Dict:
        """
        산업 리포트 검색 (RAG 활용)
        
        Args:
            market: 시장명
            years: 연도 범위
        
        Returns:
            Dict with market_size data extracted from reports
        """
        
        result = {'market_size': {}}
        
        # data_sources_registry에서 검색
        if self.source_store:
            try:
                query = f"{market} market size historical data {min(years)}-{max(years)}"
                results = self.source_store.similarity_search(query, k=5)
                logger.info(f"    ✅ RAG: {len(results)}개 소스 발견")
                
                # 각 결과에서 데이터 추출
                for res in results:
                    try:
                        # 메타데이터에서 연도별 데이터 추출
                        if hasattr(res, 'metadata'):
                            metadata = res.metadata
                            year = metadata.get('year')
                            market_size = metadata.get('market_size')
                            
                            if year and market_size:
                                year_str = str(year)
                                if year_str not in result['market_size']:
                                    result['market_size'][year_str] = {
                                        'value': market_size,
                                        'unit': metadata.get('unit', 'USD'),
                                        'source': metadata.get('source_name', 'Industry Report'),
                                        'reliability': metadata.get('reliability', 'medium')
                                    }
                        
                        # page_content에서 숫자 추출 시도
                        if hasattr(res, 'page_content'):
                            # 간단한 패턴 매칭 (확장 가능)
                            import re
                            content = res.page_content
                            # "2023: $100M" 같은 패턴
                            year_value_pattern = r'(\d{4}):\s*\$?([\d,\.]+)\s*([MB])'
                            matches = re.findall(year_value_pattern, content)
                            
                            for year, value, unit in matches:
                                if int(year) in years:
                                    multiplier = 1_000_000 if unit == 'M' else 1_000_000_000
                                    numeric_value = float(value.replace(',', '')) * multiplier
                                    
                                    if year not in result['market_size']:
                                        result['market_size'][year] = {
                                            'value': numeric_value,
                                            'unit': 'USD',
                                            'source': 'Report extraction',
                                            'reliability': 'medium'
                                        }
                    except Exception as extract_error:
                        logger.debug(f"    추출 실패: {extract_error}")
                        continue
                
            except Exception as e:
                logger.warning(f"    ⚠️ RAG 검색 실패: {e}")
        
        return result
    
    def _search_public_filings(self, market: str, years: range) -> Dict:
        """
        공시 데이터 검색 (DART API 등)
        
        Args:
            market: 시장명
            years: 연도 범위
        
        Returns:
            Dict with players data from public filings
        """
        
        result = {'players': {}}
        
        # DART API 연동 (utils.dart_api 활용)
        try:
            if hasattr(self, 'dart_api') and self.dart_api:
                # DART API 검색
                # 시장 관련 주요 기업 추출
                from umis_rag.utils.dart_api import DartAPI
                
                dart = DartAPI()
                
                # 키워드 기반 기업 검색
                companies = dart.search_companies(keyword=market, limit=10)
                
                if companies:
                    logger.info(f"    ✅ DART API: {len(companies)}개 기업 발견")
                    
                    for company in companies:
                        corp_code = company.get('corp_code')
                        corp_name = company.get('corp_name')
                        
                        # 연도별 재무 데이터 수집
                        for year in years:
                            try:
                                financial_data = dart.get_financial_statement(
                                    corp_code=corp_code,
                                    year=year
                                )
                                
                                if financial_data:
                                    result['players'][corp_name] = {
                                        'year': year,
                                        'revenue': financial_data.get('revenue'),
                                        'source': 'DART',
                                        'reliability': 'high'
                                    }
                            except Exception:
                                continue
                
                return result
                
        except ImportError:
            logger.debug("    ℹ️  DART API 모듈 없음")
        except Exception as e:
            logger.warning(f"    ⚠️ DART API 연동 실패: {e}")
        
        logger.info("    ℹ️  대안: https://dart.fss.or.kr 수동 확인")
        return result
    
    def _search_news_events(self, market: str, years: range) -> List[Dict]:
        """
        뉴스에서 주요 사건 추출
        
        Args:
            market: 시장명
            years: 연도 범위
        
        Returns:
            List of event dicts
        """
        
        events = []
        
        # Web Search를 활용한 뉴스 검색
        try:
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            
            # 연도별 주요 사건 검색
            for year in years:
                query = f"{market} market {year} major events news"
                
                try:
                    results = ddgs.text(query, max_results=5)
                    
                    for res in results:
                        events.append({
                            'year': year,
                            'title': res.get('title', ''),
                            'snippet': res.get('body', ''),
                            'url': res.get('href', ''),
                            'source': 'news_search'
                        })
                    
                    if results:
                        logger.info(f"    ✅ 뉴스: {year}년 {len(results)}개 사건")
                    
                except Exception as search_error:
                    logger.debug(f"    검색 실패 ({year}): {search_error}")
                    continue
            
        except ImportError:
            logger.info("    ℹ️  duckduckgo_search 미설치 (pip install duckduckgo-search)")
        except Exception as e:
            logger.warning(f"    ⚠️ 뉴스 검색 실패: {e}")
        
        logger.info(f"    총 {len(events)}개 사건 추출")
        return events
    
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
        """
        Estimator 협업으로 Gap 채우기
        
        Args:
            data: 수집된 데이터
            gaps: 식별된 Gap
        
        Returns:
            Gap이 채워진 데이터
        """
        
        try:
            from umis_rag.agents.estimator import get_estimator_rag
            from umis_rag.agents.estimator.common.estimation_result import Context
            
            estimator = get_estimator_rag()
            
            for request in gaps['estimator_requests']:
                if request['type'] == 'market_size_interpolation':
                    year = request['year']
                    market = request.get('market', 'Unknown')
                    
                    logger.info(f"      🤖 Estimator: {year}년 추정 요청...")
                    
                    # Context 준비
                    estimation_context = Context(
                        industry=request.get('industry'),
                        time_period=str(year),
                        region=request.get('region', 'Global')
                    )
                    
                    # Estimator 호출
                    question = f"What was the {market} market size in {year}?"
                    result = estimator.estimate(
                        question=question,
                        context=estimation_context
                    )
                    
                    if result and hasattr(result, 'value'):
                        # 추정 결과 저장
                        data['market_size_by_year'][str(year)] = {
                            'value': result.value,
                            'unit': result.unit,
                            'source': 'Estimator',
                            'reliability': 'estimated',
                            'certainty': getattr(result, 'certainty', 'medium')
                        }
                        logger.info(f"      ✅ {year}년: {result.value} {result.unit} (추정)")
                    else:
                        logger.warning(f"      ⚠️ {year}년 추정 실패")
        
        except ImportError as ie:
            logger.warning(f"    ⚠️ Estimator import 실패: {ie}")
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
    
    # ========================================
    # API 기반 데이터 검색 (v7.9.0)
    # ========================================
    
    def search_dart_company_financials(
        self,
        company_name: str,
        year: int = 2024
    ) -> Optional[Dict]:
        """
        DART API로 상장사 재무제표 검색 (v7.9.0)
        
        Args:
            company_name: 회사명 (예: "스타벅스코리아")
            year: 사업연도
        
        Returns:
            {
                'value': 0.148,
                'unit': 'ratio',
                'source': 'DART 2024년 사업보고서',
                'reliability': 'verified',
                'company': '스타벅스코리아'
            } or None
        """
        
        if not self.dart_api_key or self.dart_api_key == 'your-dart-api-key-here':
            logger.warning("[Validator] DART API Key 없음 (.env 설정 필요)")
            return None
        
        logger.info(f"[Validator] DART API 검색: {company_name} ({year})")
        
        try:
            from umis_rag.utils.dart_api import DARTClient
            
            client = DARTClient(self.dart_api_key)
            
            # Step 1: 기업 코드
            corp_code = client.get_corp_code(company_name)
            
            if not corp_code:
                logger.warning(f"  {company_name} 찾을 수 없음")
                return None
            
            logger.info(f"  ✓ corp_code: {corp_code}")
            
            # Step 2: 재무제표 조회 (개별재무제표 우선!)
            financials = client.get_financials(corp_code, year, fs_div='OFS')
            
            if not financials:
                logger.warning(f"  개별재무제표(OFS) 없음, 연결(CFS) 시도...")
                financials = client.get_financials(corp_code, year, fs_div='CFS')
                fs_div_used = 'CFS'
            else:
                fs_div_used = 'OFS'
            
            if not financials:
                logger.warning(f"  재무제표 없음")
                return None
            
            # Step 3: 주요 계정 추출
            revenue = 0
            operating_profit = 0
            cost_of_sales = 0
            sga = 0
            
            for item in financials:
                account = item.get('account_nm', '')
                amount_str = item.get('thstrm_amount', '0')
                
                try:
                    amount = float(amount_str.replace(',', ''))
                except:
                    amount = 0
                
                if '매출액' in account and '매출원가' not in account:
                    revenue = amount
                elif '매출원가' in account:
                    cost_of_sales = amount
                elif '판매비' in account or '관리비' in account:
                    sga = amount
                elif '영업이익' in account:
                    operating_profit = amount
            
            if revenue > 0:
                opm = operating_profit / revenue
                gross_margin = (revenue - cost_of_sales) / revenue if cost_of_sales > 0 else 0
                
                logger.info(f"  ✓ {company_name} 재무 ({fs_div_used}, 억원):")
                logger.info(f"    매출액: {revenue/100_000_000:,.0f}")
                logger.info(f"    영업이익률: {opm:.1%}")
                logger.info(f"    매출총이익률: {gross_margin:.1%}")
                
                return {
                    'value': round(opm, 4),
                    'unit': 'ratio',
                    'source': f'DART {year}년 사업보고서 ({fs_div_used})',
                    'reliability': 'verified',
                    'data_type': 'actual',
                    'company': company_name,
                    'year': year,
                    'fs_div': fs_div_used,
                    'revenue_billion': round(revenue / 100000000, 1),
                    'cost_of_sales_billion': round(cost_of_sales / 100000000, 1),
                    'sga_billion': round(sga / 100000000, 1),
                    'operating_profit_billion': round(operating_profit / 100000000, 1),
                    'gross_margin': round(gross_margin, 4),
                    'operating_margin': round(opm, 4),
                    'verification_url': f'https://dart.fss.or.kr/dsaf001/main.do'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"  DART API 오류: {e}")
            return None
    
    def search_kosis_industry_average(
        self,
        industry_name: str,
        ksic_code: str = None
    ) -> Optional[Dict]:
        """
        KOSIS API로 산업 평균 마진율 검색 (v7.9.0)
        
        Args:
            industry_name: 산업명 (예: "음식점업")
            ksic_code: KSIC 코드 (예: "56")
        
        Returns:
            {
                'value': 0.089,
                'unit': 'ratio',
                'source': '통계청 기업경영분석 2024',
                'reliability': 'verified',
                'sample_size': 15234
            } or None
        """
        
        # ⚠️ KOSIS API는 구조가 복잡하여 수동 수집 권장
        logger.info(f"[Validator] KOSIS 검색: {industry_name}")
        
        if not self.kosis_api_key or self.kosis_api_key == 'your-kosis-api-key-here':
            logger.warning("[Validator] KOSIS API Key 없음")
            logger.info("  대안: https://kosis.kr 수동 확인")
            return None
        
        # KOSIS API 파싱 로직
        try:
            import requests
            
            # KOSIS OpenAPI 엔드포인트
            base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
            
            params = {
                'method': 'getList',
                'apiKey': self.kosis_api_key,
                'format': 'json',
                'jsonVD': 'Y',
                'itmId': search_term,  # 통계표 ID (실제로는 매핑 필요)
                'objL1': 'ALL'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 데이터 파싱 (KOSIS 응답 구조에 맞게)
                if isinstance(data, list) and len(data) > 0:
                    parsed_data = {}
                    
                    for item in data:
                        # 연도와 값 추출
                        year = item.get('PRD_DE')  # 시점
                        value = item.get('DT')  # 데이터값
                        
                        if year and value:
                            try:
                                parsed_data[year] = float(value.replace(',', ''))
                            except ValueError:
                                continue
                    
                    logger.info(f"  ✅ KOSIS API: {len(parsed_data)}개 데이터 포인트")
                    return {
                        'data': parsed_data,
                        'source': 'KOSIS',
                        'reliability': 'high'
                    }
            else:
                logger.warning(f"  ⚠️ KOSIS API 응답 실패: {response.status_code}")
                
        except ImportError:
            logger.warning("  ⚠️ requests 라이브러리 필요 (pip install requests)")
        except Exception as e:
            logger.warning(f"  ⚠️ KOSIS API 파싱 실패: {e}")
        
        logger.info("  ℹ️  대안: https://kosis.kr 수동 수집 권장")
        return None
    
    def search_api_sources(
        self,
        query: str,
        company_name: str = None,
        industry: str = None
    ) -> Optional[Dict]:
        """
        API 데이터 소스 통합 검색 (v7.9.0)
        
        DART와 KOSIS를 자동으로 검색하여 확정 데이터 반환
        
        Args:
            query: 검색 질문
            company_name: 회사명 (DART 검색용)
            industry: 산업명 (KOSIS 검색용)
        
        Returns:
            검색 결과 또는 None
        """
        
        logger.info(f"[Validator] API 통합 검색: {query}")
        
        # DART 검색 (회사명 있을 때)
        if company_name:
            logger.info(f"  DART 검색 시도: {company_name}")
            result = self.search_dart_company_financials(company_name)
            if result:
                logger.info(f"  ✓ DART에서 발견!")
                return result
        
        # KOSIS 검색 (산업명 있을 때)
        if industry:
            logger.info(f"  KOSIS 검색 시도: {industry}")
            result = self.search_kosis_industry_average(industry)
            if result:
                logger.info(f"  ✓ KOSIS에서 발견!")
                return result
        
        logger.info("  API 소스에서 찾지 못함")
        return None


# Validator RAG 인스턴스 (싱글톤)
_validator_rag_instance = None

def get_validator_rag() -> ValidatorRAG:
    """Validator RAG 싱글톤 인스턴스 반환"""
    global _validator_rag_instance
    if _validator_rag_instance is None:
        _validator_rag_instance = ValidatorRAG()
    return _validator_rag_instance

