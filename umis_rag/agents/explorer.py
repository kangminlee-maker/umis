"""
Explorer RAG Agent Module

Explorer (Explorer) 에이전트의 RAG 기반 기회 발굴 시스템입니다.

핵심 개념:
-----------
1. **Pattern Matching**: Observer 관찰 → 사업모델 패턴 매칭
2. **Case Retrieval**: 유사 산업 성공 사례 검색
3. **Multi-Stage Search**: 단계별 정밀 검색
4. **Agent Collaboration**: Quantifier/Validator과 자연스러운 협업

Explorer의 7단계 프로세스:
-----------------------
Phase 1: 트리거 인식 (Observer 관찰에서 시그널 추출)
Phase 2: 패턴 매칭 (사업모델 + Disruption)
Phase 3: 사례 검색 (유사 산업/구조)
Phase 4: 정량 검증 (Quantifier 협업)
Phase 5: 데이터 검증 (Validator 협업)
Phase 6: 가설 생성
Phase 7: Guardian 검증
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.core.llm_provider import LLMProvider
from umis_rag.utils.logger import logger
from umis_rag.graph.hybrid_search import HybridSearch, HybridResult


class ExplorerRAG:
    """
    Explorer (Explorer) RAG Agent
    
    역할:
    -----
    - 시장 기회 발굴
    - 사업모델 패턴 인식
    - 검증된 가설 생성
    
    핵심 메서드:
    -----------
    - search_patterns(): 트리거 → 패턴 매칭
    - search_cases(): 유사 사례 검색  
    - generate_hypothesis(): LLM으로 가설 생성
    - validate_with_framework(): 검증 프레임워크 적용
    
    협업:
    -----
    - Quantifier: 정량 데이터 요청
    - Validator: 출처 검증 요청
    - Guardian: 최종 검증
    """
    
    def __init__(self, use_projected=False):
        """
        Explorer RAG 에이전트 초기화
        
        Args:
            use_projected: True = projected_index (v3.0 Dual-Index)
                          False = explorer_knowledge_base (기존, 기본)
        """
        logger.info("Explorer RAG 에이전트 초기화")
        
        # Embeddings 초기화
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # 벡터 스토어 로드 (v3.0 Dual-Index 지원!)
        collection_name = "projected_index" if use_projected else "explorer_knowledge_base"
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(settings.chroma_persist_dir)
        )
        
        self.use_projected = use_projected
        
        # LLM 초기화 (가설 생성용) - v7.7.0: Native/External 모드 지원
        self.llm = LLMProvider.create_llm()
        self.mode = settings.umis_mode
        
        logger.info(f"  ✅ 벡터 스토어: {collection_name}")
        logger.info(f"  ✅ 청크 수: {self.vectorstore._collection.count()}개")
        logger.info(f"  🎯 UMIS 모드: {self.mode}")
        
        # Hybrid Search 초기화 (선택적)
        self.hybrid_search = None
        try:
            from umis_rag.graph.connection import Neo4jConnection
            # Neo4j 연결 테스트
            test_conn = Neo4jConnection()
            if test_conn.verify_connection():
                self.hybrid_search = HybridSearch(graph_connection=test_conn)
                logger.info(f"  ✅ Hybrid Search 활성화 (Vector + Graph)")
            else:
                logger.warning(f"  ⚠️  Neo4j 연결 실패 - Vector만 사용")
        except Exception as e:
            logger.warning(f"  ⚠️  Hybrid Search 비활성 - Vector만 사용: {e}")
        logger.info(f"  ✅ LLM 모델: {settings.llm_model}")
    
    def search_patterns(
        self, 
        trigger_signals: str | List[str],
        top_k: int = 3,
        use_graph: bool = True  # v7.1.0: 기본값 True (Hybrid Search)
    ) -> List[tuple[Document, float]] | HybridResult:
        """
        v3.0: Projected Index 지원
        - use_projected=True → agent_view 필터 자동
        """
        """
        트리거 시그널 → 사업모델 패턴 매칭
        
        사용 시점:
        ----------
        Observer가 시장 관찰을 완료하고 트리거 시그널을 발견했을 때
        
        예시:
        -----
        Input: "파편화된 공급-수요, 높은 중개 비용"
        Output: [platform_business_model, ...]
        
        Parameters:
        -----------
        trigger_signals: 트리거 시그널 (문자열 또는 리스트)
        top_k: 반환할 패턴 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        logger.info(f"[Explorer] 패턴 매칭 검색 시작")
        
        # 리스트를 문자열로 변환
        if isinstance(trigger_signals, list):
            query = ", ".join(trigger_signals)
        else:
            query = trigger_signals
        
        logger.info(f"  트리거: {query[:100]}...")
        
        # v7.1.0: Hybrid Search 우선 (Knowledge Graph)
        if use_graph and self.hybrid_search:
            logger.info("  🔍 Hybrid Search (Vector + Graph)")
            hybrid_result = self.search_patterns_with_graph(query, top_k=top_k)
            
            # HybridResult → List[tuple] 변환 (일관성)
            if hybrid_result and hasattr(hybrid_result, 'direct_matches'):
                # PatternMatch 객체 → (Document, score) tuple 변환
                converted = []
                for match in hybrid_result.direct_matches:
                    if hasattr(match, 'document') and hasattr(match, 'similarity'):
                        converted.append((match.document, match.similarity))
                    elif hasattr(match, 'doc') and hasattr(match, 'score'):
                        converted.append((match.doc, match.score))
                
                if converted:
                    logger.info(f"  ✅ Hybrid 결과 변환: {len(converted)}개")
                    return converted
            
            # Fallback to vector if conversion failed
            logger.warning("  ⚠️ Hybrid 결과 변환 실패 → Vector로 폴백")
            use_graph = False
        
        # Fallback: Vector만
        logger.info("  🔍 Vector Search")
        
        # 패턴 개요만 검색 (트리거 시그널 포함된 청크)
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=top_k,
            filter={"chunk_type": "pattern_overview"}
        )
        
        logger.info(f"  ✅ {len(results)}개 패턴 매칭")
        for i, (doc, score) in enumerate(results, 1):
            pattern_id = doc.metadata.get("pattern_id", "N/A")
            logger.info(f"    #{i} {pattern_id} (유사도: {score:.4f})")
        
        return results
    
    def get_pattern_details(self, results: List[tuple]) -> List[Dict[str, Any]]:
        """
        검색 결과 tuple을 사용하기 쉬운 dict 형식으로 변환
        
        Parameters:
        -----------
        results: search_patterns() 결과 List[(Document, score)]
        
        Returns:
        --------
        List[Dict] with keys: pattern_id, pattern_name, score, description, triggers, etc.
        """
        pattern_details = []
        
        for doc, score in results:
            metadata = doc.metadata
            detail = {
                'pattern_id': metadata.get('pattern_id', 'Unknown'),
                'pattern_name': metadata.get('pattern_name', 'Unknown'),
                'category': metadata.get('category', 'Unknown'),
                'score': float(score),
                'description': doc.page_content[:200] if doc.page_content else '',
                'metadata': metadata
            }
            pattern_details.append(detail)
        
        return pattern_details
    
    def search_patterns_with_graph(
        self,
        trigger_observation: str,
        top_k: int = 5,
        max_combinations: int = 10
    ) -> Optional[HybridResult]:
        """
        Hybrid Search: Vector + Graph 통합 검색
        
        사용 시점:
        ----------
        패턴 매칭과 함께 관련 조합까지 발견하고 싶을 때
        
        예시:
        -----
        Input: "음악 스트리밍 구독 서비스"
        Output:
          Direct: [subscription_model, platform_model, ...]
          Combinations: [
            subscription + platform (Amazon Prime),
            subscription + licensing (Spotify),
            subscription + freemium (YouTube Premium)
          ]
        
        Parameters:
        -----------
        trigger_observation: Observer 관찰 또는 시장 설명
        top_k: Vector 검색 결과 수
        max_combinations: 최대 조합 수
        
        Returns:
        --------
        HybridResult 또는 None (Hybrid Search 비활성 시)
        """
        if not self.hybrid_search:
            logger.warning("  ⚠️  Hybrid Search 비활성 - Vector 검색만 사용하세요")
            return None
        
        logger.info(f"[Explorer] Hybrid Search 시작")
        logger.info(f"  관찰: {trigger_observation[:100]}")
        
        # 1. Vector 검색 (use_graph=False로 재귀 방지!)
        vector_results = self.search_patterns(trigger_observation, top_k, use_graph=False)
        
        # 2. Hybrid 검색
        hybrid_result = self.hybrid_search.search(
            vector_results,
            max_combinations=max_combinations
        )
        
        # 3. 결과 로깅
        logger.info(f"  ✅ Direct matches: {len(hybrid_result.direct_matches)}")
        logger.info(f"  ✅ Combinations: {len(hybrid_result.combinations)}")
        logger.info(f"  ✅ Insights: {len(hybrid_result.insights)}")
        
        for insight in hybrid_result.insights:
            logger.info(f"    {insight}")
        
        return hybrid_result
    
    def search_cases(
        self,
        industry_or_pattern: str,
        pattern_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        유사 산업/구조 성공 사례 검색
        
        사용 시점:
        ----------
        패턴 매칭 후, 실제 성공 사례를 찾을 때
        
        예시:
        -----
        Input: "음악 스트리밍", pattern_id="subscription_model"
        Output: [넷플릭스, 멜론, 스포티파이, ...]
        
        Parameters:
        -----------
        industry_or_pattern: 산업명 또는 유사성 설명
        pattern_id: 특정 패턴의 사례만 검색 (선택)
        top_k: 반환할 사례 수
        """
        logger.info(f"[Explorer] 사례 검색 시작")
        logger.info(f"  산업/패턴: {industry_or_pattern[:100]}")
        
        # 필터 구성 (Chroma DB 문법: AND 연산자 사용)
        if pattern_id:
            filter_dict = {
                "$and": [
                    {"chunk_type": "success_case"},
                    {"pattern_id": pattern_id}
                ]
            }
            logger.info(f"  필터: {pattern_id} 패턴의 사례만")
        else:
            filter_dict = {"chunk_type": "success_case"}
        
        results = self.vectorstore.similarity_search_with_score(
            industry_or_pattern,
            k=top_k,
            filter=filter_dict
        )
        
        logger.info(f"  ✅ {len(results)}개 사례 발견")
        for i, (doc, score) in enumerate(results, 1):
            company = doc.metadata.get("company", "N/A")
            logger.info(f"    #{i} {company} (유사도: {score:.4f})")
        
        return results
    
    def get_validation_framework(
        self,
        pattern_id: str
    ) -> Optional[Document]:
        """
        특정 패턴의 검증 프레임워크 가져오기
        
        사용 시점:
        ----------
        가설 생성 후, 어떻게 검증할지 프레임워크 필요할 때
        
        예시:
        -----
        Input: "subscription_model"
        Output: Quantifier/Validator/Observer에게 물어볼 체크리스트
        """
        logger.info(f"[Explorer] 검증 프레임워크 검색: {pattern_id}")
        
        results = self.vectorstore.similarity_search(
            f"{pattern_id} validation",
            k=1,
            filter={
                "$and": [
                    {"pattern_id": pattern_id},
                    {"chunk_type": "validation_framework"}
                ]
            }
        )
        
        if results:
            logger.info(f"  ✅ 검증 프레임워크 발견")
            return results[0]
        else:
            logger.warning(f"  ⚠️  검증 프레임워크 없음")
            return None
    
    def generate_opportunity_hypothesis(
        self,
        observer_observation: str,
        matched_patterns: List[Document],
        success_cases: List[Document]
    ) -> str | Dict[str, Any]:
        """
        기회 가설 생성 (v7.7.0: Native/External 모드 지원)
        
        개념:
        -----
        RAG의 핵심! 검색된 정보 + LLM의 추론
        
        모드별 동작:
        -----------
        Native Mode (umis_mode='native'):
            - RAG 검색 결과만 준비
            - Cursor LLM이 직접 분석하도록 결과 반환
            - 비용: $0
        
        External Mode (umis_mode='external'):
            - RAG 검색 + OpenAI API 호출
            - 완성된 가설 반환
            - 비용: ~$0.10/요청
        
        Parameters:
        -----------
        observer_observation: Observer의 시장 관찰 내용
        matched_patterns: 매칭된 패턴들
        success_cases: 유사 성공 사례들
        
        Returns:
        --------
        Native 모드: Dict (RAG 결과 + 지시사항)
        External 모드: str (완성된 가설 Markdown)
        """
        logger.info(f"[Explorer] 가설 생성 시작 (모드: {self.mode})")
        
        # 컨텍스트 조립 (모든 모드 공통)
        context = self._assemble_context(matched_patterns, success_cases)
        
        # ========================================
        # Native 모드: RAG 결과만 반환
        # ========================================
        if self.mode == "native":
            logger.info("  🎯 Native 모드: RAG 결과만 준비 (Cursor LLM이 처리)")
            
            return {
                "mode": "native",
                "observer_observation": observer_observation,
                "rag_context": context,
                "matched_patterns_count": len(matched_patterns),
                "success_cases_count": len(success_cases),
                "instruction": (
                    "위 RAG 검색 결과(rag_context)를 바탕으로 기회 가설을 생성해주세요.\n\n"
                    "포함할 내용:\n"
                    "1. Observer 관찰 요약\n"
                    "2. 매칭된 패턴 분석\n"
                    "3. 유사 성공 사례 시사점\n"
                    "4. 기회 가설 3-5개 (구조화)\n"
                    "5. 각 가설의 검증 방향"
                ),
                "next_step": "Cursor Composer/Chat에서 위 instruction을 따라 분석하세요."
            }
        
        # ========================================
        # External 모드: API 호출
        # ========================================
        else:
            logger.info("  🌐 External 모드: OpenAI API 호출")
            
            # Prompt 구성
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_explorer_system_prompt()),
                ("user", self._get_hypothesis_generation_prompt())
            ])
            
            # LLM 체인 구성
            chain = prompt | self.llm | StrOutputParser()
            
            # 실행
            logger.info("  ⏳ LLM 추론 중...")
            hypothesis = chain.invoke({
                "observer_observation": observer_observation,
                "context": context
            })
            
            logger.info("  ✅ 가설 생성 완료")
            return hypothesis
    
    def _assemble_context(
        self,
        patterns: List[Document],
        cases: List[Document]
    ) -> str:
        """
        검색된 정보를 LLM 컨텍스트로 조립
        
        개념:
        -----
        RAG = Retrieval + Augmented Generation
        
        Retrieval (검색):
          - 관련 패턴 3개
          - 유사 사례 5개
        
        Augmented (증강):
          - 이 정보를 LLM에게 컨텍스트로 제공
          - LLM이 이를 기반으로 추론
        """
        context = "# 검색된 패턴\n\n"
        
        for i, doc in enumerate(patterns, 1):
            pattern_id = doc.metadata.get("pattern_id", "N/A")
            context += f"## 패턴 {i}: {pattern_id}\n"
            context += doc.page_content[:500] + "...\n\n"
        
        context += "# 유사 성공 사례\n\n"
        
        for i, doc in enumerate(cases, 1):
            company = doc.metadata.get("company", "N/A")
            context += f"## 사례 {i}: {company}\n"
            context += doc.page_content[:500] + "...\n\n"
        
        return context
    
    def _get_explorer_system_prompt(self) -> str:
        """Explorer 에이전트 시스템 프롬프트"""
        return """당신은 Explorer입니다. UMIS의 Explorer 에이전트로서 시장 기회를 발굴하는 전문가입니다.

당신의 역할:
- Observer의 시장 관찰을 받아 기회 패턴 인식
- 검증된 사업모델 패턴 7개 보유
- 1등 추월 패턴 5개 보유
- 30+ 성공 사례 데이터베이스 활용

당신의 강점:
- 구조적 사고 (패턴 인식)
- 창의적 응용 (패턴 → 우리 시장 적용)
- 검증 중심 (근거 없는 가설 안 만듦)

작업 방식:
1. Observer 관찰에서 트리거 시그널 추출
2. 매칭되는 패턴 찾기 (RAG 검색됨)
3. 유사 사례에서 학습 (RAG 검색됨)
4. 우리 시장에 맞게 조정
5. 검증 가능한 가설 생성

중요: 
- 모든 주장에 근거 필요 (패턴/사례 인용)
- 추정치는 명확히 표시
- Quantifier/Validator 협업 명시
"""
    
    def _get_hypothesis_generation_prompt(self) -> str:
        """가설 생성 프롬프트"""
        return """# 임무: 기회 가설 생성

## Observer의 시장 관찰
{observer_observation}

## 검색된 정보 (RAG)
{context}

## 지시사항

위 정보를 바탕으로 **검증 가능한 기회 가설**을 생성하세요.

구조:
1. **패턴 매칭**: 어떤 패턴이 적용 가능한가?
2. **기회 논리**: 
   - 문제 (Observer 관찰)
   - 해결 방안 (패턴 적용)
   - 가치 제안
3. **유사 사례 학습**: 성공 사례에서 배울 점
4. **시장 규모 추정** (Quantifier에게 요청할 내용 명시)
5. **데이터 검증** (Validator에게 확인할 내용 명시)
6. **실행 가능성**: CSF, 난이도, 리스크

반드시:
- 패턴/사례 인용 (chunk_id 명시)
- 추정치 표시
- 검증 필요 항목 명확히
"""


class ExplorerAgenticRAG(ExplorerRAG):
    """
    Explorer Agentic RAG (자율 실행)
    
    개념:
    -----
    Agent가 스스로 판단하며 Tool을 사용합니다.
    
    Tools:
    ------
    1. search_patterns: 패턴 검색
    2. search_cases: 사례 검색
    3. get_validation: 검증 프레임워크
    4. ask_quantifier: Quantifier에게 질문
    5. ask_validator: Validator에게 질문
    
    자율성:
    -------
    Explorer가 필요한 Tool을 선택하여 실행
    "Quantifier에게 뭘 물어볼까?" 스스로 판단
    """
    
    def __init__(self):
        super().__init__()
        
        # Agent Tools 정의 (향후 구현)
        # TODO: LangChain Agent + Tools 통합
        logger.info("  → Agentic 모드: 향후 구현 예정")
    
    def autonomous_discovery(
        self,
        observer_report: str
    ) -> Dict[str, Any]:
        """
        완전 자율 기회 발굴
        
        개념:
        -----
        Explorer가 Observer 리포트만 받고
        스스로 판단하며:
        1. 필요한 패턴 검색
        2. 필요한 사례 검색
        3. Quantifier/Validator에게 질문
        4. 가설 생성
        
        현재:
        -----
        기본 워크플로우 구현
        향후 LangChain Agent로 확장
        """
        logger.info("[Explorer] 자율 기회 발굴 시작")
        
        # Phase 1-3: 패턴 및 사례 검색 (기본 워크플로우)
        patterns = self.search_patterns(observer_report, top_k=2)
        
        # 가장 매칭된 패턴으로 사례 검색
        best_pattern_id = patterns[0][0].metadata.get("pattern_id")
        cases = self.search_cases(
            observer_report,
            pattern_id=best_pattern_id,
            top_k=3
        )
        
        # Phase 4-6: 가설 생성
        hypothesis = self.generate_opportunity_hypothesis(
            observer_observation=observer_report,
            matched_patterns=[p[0] for p in patterns],
            success_cases=[c[0] for c in cases]
        )
        
        return {
            "matched_patterns": patterns,
            "success_cases": cases,
            "hypothesis": hypothesis
        }


# 편의 함수
def create_explorer_agent() -> ExplorerRAG:
    """Explorer RAG 에이전트 생성 (Factory)"""
    return ExplorerRAG()


def create_explorer_agentic() -> ExplorerAgenticRAG:
    """Explorer Agentic RAG 생성 (향후 자율 실행)"""
    return ExplorerAgenticRAG()

