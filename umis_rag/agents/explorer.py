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
from umis_rag.core.openai_validation import require_openai_api_key
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
        openai_api_key = require_openai_api_key(
            settings.openai_api_key,
            component="ExplorerRAG(OpenAIEmbeddings)"
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=openai_api_key
        )
        
        # 벡터 스토어 로드 (v3.0 Dual-Index 지원!)
        collection_name = "projected_index" if use_projected else "explorer_knowledge_base"
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(settings.chroma_persist_dir)
        )
        
        self.use_projected = use_projected
        
        # LLM 초기화 (가설 생성용) - v7.8.1: llm_mode 지원
        self.llm = LLMProvider.create_llm()
        self.mode = settings.llm_mode
        
        logger.info(f"  ✅ 벡터 스토어: {collection_name}")
        logger.info(f"  ✅ 청크 수: {self.vectorstore._collection.count()}개")
        logger.info(f"  🎯 LLM 모드: {self.mode}")
        
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
        
        # Agent Tools 정의
        self.agent_tools = self._initialize_agent_tools()
        
        if self.agent_tools:
            logger.info(f"  → Agentic 모드: {len(self.agent_tools)}개 도구 활성화")
        else:
            logger.info("  → Agentic 모드: 향후 구현 예정 (LangChain 통합)")
    
    def _initialize_agent_tools(self) -> Optional[List]:
        """
        LangChain Agent Tools 초기화
        
        Returns:
            List of LangChain tools or None if not available
        
        Tools:
            - search_patterns: RAG에서 패턴 검색
            - search_cases: RAG에서 사례 검색
            - ask_quantifier: Quantifier에게 질문
            - ask_validator: Validator에게 질문
            - generate_hypothesis: 가설 생성
        """
        
        try:
            from langchain.tools import Tool
            from langchain.agents import initialize_agent, AgentType
            
            tools = []
            
            # Tool 1: Pattern Search
            tools.append(Tool(
                name="search_patterns",
                func=self._tool_search_patterns,
                description="Search for business patterns in RAG database. Input: pattern description"
            ))
            
            # Tool 2: Case Search
            tools.append(Tool(
                name="search_cases",
                func=self._tool_search_cases,
                description="Search for case studies in RAG database. Input: case description"
            ))
            
            # Tool 3: Ask Quantifier
            tools.append(Tool(
                name="ask_quantifier",
                func=self._tool_ask_quantifier,
                description="Ask Quantifier agent to estimate a value. Input: estimation question"
            ))
            
            # Tool 4: Ask Validator
            tools.append(Tool(
                name="ask_validator",
                func=self._tool_ask_validator,
                description="Ask Validator agent to verify data. Input: validation question"
            ))
            
            # Tool 5: Generate Hypothesis
            tools.append(Tool(
                name="generate_hypothesis",
                func=self._tool_generate_hypothesis,
                description="Generate business hypothesis. Input: hypothesis context"
            ))
            
            return tools
        
        except ImportError:
            logger.debug("  ℹ️  LangChain 미설치 (pip install langchain)")
            return None
        except Exception as e:
            logger.warning(f"  ⚠️ Agent Tools 초기화 실패: {e}")
            return None
    
    def _tool_search_patterns(self, query: str) -> str:
        """Tool: RAG 패턴 검색"""
        try:
            if hasattr(self, 'pattern_store') and self.pattern_store:
                results = self.pattern_store.similarity_search(query, k=3)
                return "\n".join([r.page_content for r in results[:3]])
        except Exception:
            pass
        return "No patterns found"
    
    def _tool_search_cases(self, query: str) -> str:
        """Tool: RAG 사례 검색"""
        try:
            if hasattr(self, 'case_store') and self.case_store:
                results = self.case_store.similarity_search(query, k=3)
                return "\n".join([r.page_content for r in results[:3]])
        except Exception:
            pass
        return "No cases found"
    
    def _tool_ask_quantifier(self, question: str) -> str:
        """Tool: Quantifier 협업"""
        try:
            from umis_rag.agents.quantifier import get_quantifier_rag
            quantifier = get_quantifier_rag()
            result = quantifier.estimate(question)
            if result:
                return f"Estimate: {result.value} {result.unit}"
        except Exception:
            pass
        return "Quantifier unavailable"
    
    def _tool_ask_validator(self, question: str) -> str:
        """Tool: Validator 협업"""
        try:
            from umis_rag.agents.validator import get_validator_rag
            validator = get_validator_rag()
            result = validator.validate(question)
            if result:
                return f"Validation: {result}"
        except Exception:
            pass
        return "Validator unavailable"
    
    def _tool_generate_hypothesis(self, context: str) -> str:
        """Tool: 가설 생성"""
        # 간단한 패턴 기반 가설 생성
        return f"Hypothesis: Based on {context}, consider market dynamics and trends."
    
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
    
    # ========================================
    # Strategy Playbook (v7.10.0 Gap #3)
    # ========================================
    
    def generate_strategy_playbook(
        self,
        validated_opportunity: Dict[str, Any],
        market_context: Dict[str, Any],
        quantified_market: Dict[str, Any],
        project_name: str = "default_project"
    ) -> Dict[str, Any]:
        """
        검증된 기회 → 실행 가능한 전략 Playbook 생성 (v7.10.0)
        
        Q14 (어떻게 뚫어야하는데?): 85% → 95%+
        Q15 (뭘 해야하는데?): 60% → 80%+
        
        Args:
            validated_opportunity: 7-Step 완료된 기회
                {
                    'opportunity_id': 'OPP_XXX',
                    'title': '구독 모델 피아노 서비스',
                    'value_proposition': '초기 부담 없이 피아노 시작',
                    'target_customer': '피아노 입문자 (20-40대)',
                    'core_features': [기능 리스트],
                    'revenue_model': '월 구독',
                    'unit_economics': {
                        'arpu': 120000,
                        'cac': 180000,
                        'ltv': 2400000,
                        'churn': 0.05
                    }
                }
            
            market_context: Observer 구조 분석
                {
                    'market_structure': {...},
                    'inefficiencies': [...],
                    'competitors': [...]
                }
            
            quantified_market: Quantifier SAM 계산
                {
                    'sam': 1300,  # 억원
                    'target_share': 0.05,
                    'unit_economics': {...}
                }
            
            project_name: 프로젝트 이름 (파일명 생성용)
        
        Returns:
            {
                'gtm_strategy': {...},
                'product_roadmap': {...},
                'resource_plan': {...},
                'execution_milestones': {...},
                'risk_mitigation': {...},
                'markdown_path': 'strategy_playbook.md',
                'excel_path': 'strategy_playbook.xlsx'
            }
        """
        
        logger.info(f"[Explorer] Strategy Playbook 생성: {validated_opportunity.get('title')}")
        
        # Step 1: GTM Strategy
        logger.info("  Step 1/7: GTM Strategy")
        gtm = self._design_gtm_strategy(
            validated_opportunity, market_context, quantified_market
        )
        
        # Step 2: Product Roadmap
        logger.info("  Step 2/7: Product Roadmap (RICE)")
        roadmap = self._prioritize_features(
            validated_opportunity, market_context, quantified_market
        )
        
        # Step 3: Resource Plan
        logger.info("  Step 3/7: Resource Plan")
        resources = self._plan_resources(
            quantified_market, validated_opportunity
        )
        
        # Step 4: Execution Milestones
        logger.info("  Step 4/7: Execution Milestones")
        milestones = self._set_milestones(
            roadmap, resources, quantified_market, validated_opportunity
        )
        
        # Step 5: Risk Mitigation
        logger.info("  Step 5/7: Risk Assessment")
        risks = self._assess_and_mitigate_risks(
            validated_opportunity, market_context, quantified_market
        )
        
        # Step 6: Markdown 생성
        logger.info("  Step 6/7: Markdown 생성")
        markdown_path = self._generate_playbook_markdown(
            validated_opportunity, gtm, roadmap, resources, 
            milestones, risks, project_name
        )
        
        # Step 7: Excel 생성
        logger.info("  Step 7/7: Excel 생성")
        excel_path = self._generate_playbook_excel(
            validated_opportunity, gtm, roadmap, resources,
            milestones, risks, project_name
        )
        
        logger.info(f"  ✅ Strategy Playbook 완료!")
        logger.info(f"    - Markdown: {markdown_path}")
        logger.info(f"    - Excel: {excel_path}")
        
        return {
            'gtm_strategy': gtm,
            'product_roadmap': roadmap,
            'resource_plan': resources,
            'execution_milestones': milestones,
            'risk_mitigation': risks,
            'markdown_path': markdown_path,
            'excel_path': excel_path
        }
    
    def _design_gtm_strategy(
        self,
        opportunity: Dict,
        market_context: Dict,
        quantified: Dict
    ) -> Dict[str, Any]:
        """GTM (Go-to-Market) 전략 설계"""
        
        sam = quantified['sam']
        target_share = quantified.get('target_share', 0.05)
        target_revenue = sam * target_share
        
        arpu = opportunity['unit_economics'].get('arpu', 100000)
        cac = opportunity['unit_economics'].get('cac', 150000)
        ltv = opportunity['unit_economics'].get('ltv', 2000000)
        
        # Target customers 계산
        target_customers_annual = int((target_revenue * 100000000) / (arpu * 12))
        
        # Customer Acquisition Channels
        channels = [
            {
                'channel': 'Direct Sales',
                'priority': 1,
                'cac_estimate': cac,
                'rationale': '초기 고객 밀착, 피드백 수집',
                'timeline': 'Month 1-6'
            },
            {
                'channel': 'Digital Marketing',
                'priority': 2,
                'cac_estimate': int(cac * 0.7),
                'rationale': '스케일업, 자동화 가능',
                'timeline': 'Month 3+'
            }
        ]
        
        # Funnel
        monthly_target = target_customers_annual // 12
        funnel = {
            'awareness': int(monthly_target / 0.03),
            'consideration': int(monthly_target / 0.03 * 0.30),
            'conversion': monthly_target,
            'target_cac': cac
        }
        
        # Distribution
        distribution = {
            'primary_channel': 'Direct (온라인)',
            'channel_mix': {'direct': '70%', 'partnership': '30%'},
            'partnerships': []
        }
        
        # Pricing
        competitors = market_context.get('competitors', [])
        competitor_comparison = []
        for comp in competitors[:3]:
            competitor_comparison.append({
                'competitor': comp.get('name', 'Competitor'),
                'price': f'월 {arpu * 1.25 / 10000:.0f}만원',
                'our_price': f'월 {arpu / 10000:.0f}만원',
                'differential': '-20%'
            })
        
        pricing = {
            'pricing_model': opportunity.get('revenue_model', '구독'),
            'price_point': arpu,
            'pricing_strategy': 'Value-based',
            'competitor_comparison': competitor_comparison
        }
        
        # Marketing
        marketing = {
            'positioning': opportunity['value_proposition'],
            'key_message': opportunity['value_proposition'],
            'content_strategy': ['Blog', 'YouTube', 'SNS'],
            'budget_allocation': {
                'digital_ads': '40%',
                'content': '30%',
                'partnership': '20%',
                '기타': '10%'
            }
        }
        
        return {
            'customer_acquisition': {
                'target_segment': opportunity['target_customer'],
                'segment_size': target_customers_annual,
                'channels': channels,
                'funnel': funnel
            },
            'distribution': distribution,
            'pricing': pricing,
            'marketing_approach': marketing
        }
    
    def _prioritize_features(
        self,
        opportunity: Dict,
        market_context: Dict,
        quantified: Dict
    ) -> Dict[str, Any]:
        """Product Roadmap 생성 (RICE Framework)"""
        
        features = opportunity.get('core_features', [])
        
        if not features:
            # 기본 features 제안
            features = [
                {'name': '사용자 가입/인증', 'type': 'core', 'complexity': 'simple'},
                {'name': '핵심 기능 #1', 'type': 'core', 'complexity': 'medium'},
                {'name': '핵심 기능 #2', 'type': 'core', 'complexity': 'medium'},
                {'name': '결제 시스템', 'type': 'core', 'complexity': 'medium'},
                {'name': '대시보드', 'type': 'frequent', 'complexity': 'simple'}
            ]
        
        prioritized = []
        sam = quantified['sam']
        target_share = quantified.get('target_share', 0.05)
        arpu = opportunity['unit_economics'].get('arpu', 100000)
        
        total_customers = int((sam * target_share * 100000000) / (arpu * 12))
        monthly_users = total_customers // 12
        
        for feature in features:
            # RICE 계산
            feature_type = feature.get('type', 'core')
            
            # Reach
            if feature_type == 'core':
                reach = monthly_users
            elif feature_type == 'frequent':
                reach = int(monthly_users * 0.70)
            else:
                reach = int(monthly_users * 0.30)
            
            # Impact (간단 버전)
            if feature_type == 'core':
                impact = 3
            elif feature.get('name') and '결제' in feature.get('name'):
                impact = 3
            else:
                impact = 2
            
            # Confidence
            confidence = 80  # Default
            if feature.get('validated'):
                confidence = 95
            
            # Effort
            complexity = feature.get('complexity', 'medium')
            effort_map = {'simple': 0.5, 'medium': 1.5, 'complex': 3.0}
            effort = effort_map.get(complexity, 1.5)
            
            # RICE Score
            rice_score = (reach * impact * (confidence / 100)) / effort
            
            prioritized.append({
                'feature': feature.get('name', f'Feature {len(prioritized)+1}'),
                'description': feature.get('description', ''),
                'reach': reach,
                'impact': impact,
                'confidence': confidence,
                'effort': effort,
                'rice_score': round(rice_score, 1),
                'priority': 0
            })
        
        # 점수순 정렬
        prioritized.sort(key=lambda x: x['rice_score'], reverse=True)
        for idx, item in enumerate(prioritized, 1):
            item['priority'] = idx
        
        # MVP / Phase 2 / Phase 3 분류
        mvp = prioritized[:3]
        phase2 = prioritized[3:7] if len(prioritized) > 3 else []
        phase3 = prioritized[7:] if len(prioritized) > 7 else []
        
        return {
            'mvp': {
                'features': mvp,
                'timeline': '3개월',
                'total_effort': sum([f['effort'] for f in mvp]),
                'description': 'Must-have 핵심 기능'
            },
            'phase_2': {
                'features': phase2,
                'timeline': '6개월',
                'total_effort': sum([f['effort'] for f in phase2]),
                'description': '확장 기능'
            },
            'phase_3': {
                'features': phase3,
                'timeline': '12개월',
                'total_effort': sum([f['effort'] for f in phase3]),
                'description': '성숙 기능'
            },
            'all_features': prioritized
        }
    
    def _plan_resources(
        self,
        quantified: Dict,
        opportunity: Dict
    ) -> Dict[str, Any]:
        """Resource Plan 생성"""
        
        target_revenue = quantified['sam'] * quantified.get('target_share', 0.05)
        
        # Team Structure
        team_3 = [
            {'role': 'CEO/Founder', 'count': 1, 'salary': 0},
            {'role': '개발', 'count': 2, 'salary': 6000000},
            {'role': '디자인', 'count': 1, 'salary': 5000000},
            {'role': '마케팅', 'count': 1, 'salary': 5500000}
        ]
        
        team_6 = [
            {'role': 'CEO/Founder', 'count': 1, 'salary': 0},
            {'role': '개발', 'count': 4, 'salary': 6000000},
            {'role': '디자인', 'count': 1, 'salary': 5000000},
            {'role': '마케팅/영업', 'count': 3, 'salary': 5500000},
            {'role': 'CS', 'count': 1, 'salary': 4500000}
        ]
        
        team_12 = [
            {'role': 'Executive', 'count': 2, 'salary': 0},
            {'role': '개발', 'count': 8, 'salary': 6000000},
            {'role': '마케팅/영업', 'count': 6, 'salary': 5500000},
            {'role': 'CS/운영', 'count': 3, 'salary': 4500000},
            {'role': '데이터/분석', 'count': 2, 'salary': 6500000}
        ]
        
        # Budget 계산
        def calc_budget(team):
            salary = sum([t['count'] * t['salary'] for t in team])
            opex = salary * 0.50
            return {'salary': salary, 'opex': opex, 'total': salary + opex}
        
        budget_3 = calc_budget(team_3)
        budget_6 = calc_budget(team_6)
        budget_12 = calc_budget(team_12)
        
        # Key Hires
        key_hires = [
            {'role': 'CTO/Tech Lead', 'priority': 1, 'timing': 'Month 1'},
            {'role': 'Product Manager', 'priority': 2, 'timing': 'Month 3'},
            {'role': 'Sales Lead', 'priority': 3, 'timing': 'Month 6'},
            {'role': 'Marketing Lead', 'priority': 4, 'timing': 'Month 6'}
        ]
        
        return {
            'team_structure': {
                'month_3': team_3,
                'month_6': team_6,
                'month_12': team_12
            },
            'budget': {
                'month_3': budget_3,
                'month_6': budget_6,
                'month_12': budget_12,
                'cumulative_burn': {
                    'to_3': budget_3['total'] * 3,
                    'to_6': budget_3['total'] * 3 + budget_6['total'] * 3,
                    'to_12': budget_3['total'] * 3 + budget_6['total'] * 3 + budget_12['total'] * 6
                }
            },
            'key_hires': key_hires
        }
    
    def _set_milestones(
        self,
        roadmap: Dict,
        resources: Dict,
        quantified: Dict,
        opportunity: Dict
    ) -> Dict[str, Any]:
        """3/6/12개월 Milestone 설정"""
        
        sam = quantified['sam']
        target_share = quantified.get('target_share', 0.05)
        target_revenue_annual = sam * target_share
        arpu = opportunity['unit_economics'].get('arpu', 100000)
        
        # Month 3: MVP
        customers_3 = max(100, int((target_revenue_annual * 0.01 * 100000000) / (arpu * 12)))
        mrr_3 = customers_3 * arpu
        
        # Month 6: PMF
        customers_6 = customers_3 * 5
        mrr_6 = customers_6 * arpu
        
        # Month 12: Scale
        customers_12 = customers_6 * 6
        arr_12 = int(target_revenue_annual * 0.30)
        
        return {
            'month_3': {
                'milestone': 'MVP 런칭',
                'metrics': {
                    'customers': customers_3,
                    'mrr': f'{mrr_3/100000000:.1f}억',
                    'churn': '< 10%'
                },
                'key_activities': [
                    'MVP 개발 완료',
                    f'Beta 테스트 ({customers_3//2}명)',
                    f'첫 {customers_3}명 고객 확보'
                ],
                'success_criteria': [
                    'Product-Market Fit 초기 검증',
                    'Churn < 10%',
                    'NPS > 40'
                ]
            },
            'month_6': {
                'milestone': 'PMF 검증',
                'metrics': {
                    'customers': customers_6,
                    'mrr': f'{mrr_6/100000000:.1f}억',
                    'churn': '< 7%'
                },
                'key_activities': [
                    'Phase 2 기능 출시',
                    '파트너십 3개 확보',
                    f'{customers_6}명 돌파'
                ],
                'success_criteria': [
                    'PMF 확정 (재구매 > 60%)',
                    'LTV/CAC > 2.0',
                    'Churn < 7%'
                ]
            },
            'month_12': {
                'milestone': '스케일업 준비',
                'metrics': {
                    'customers': customers_12,
                    'arr': f'{arr_12:.0f}억',
                    'churn': '< 5%'
                },
                'key_activities': [
                    'Phase 3 기능 출시',
                    '시리즈 A 투자 유치',
                    '팀 확장 (20명)'
                ],
                'success_criteria': [
                    f'ARR {arr_12:.0f}억 달성',
                    'Rule of 40 > 40%',
                    '시장 점유율 1%'
                ]
            }
        }
    
    def _assess_and_mitigate_risks(
        self,
        opportunity: Dict,
        market_context: Dict,
        quantified: Dict
    ) -> Dict[str, Any]:
        """리스크 평가 및 대응"""
        
        risks = []
        
        # Risk 1: 경쟁사 가격 인하
        competitors = market_context.get('competitors', [])
        if len(competitors) >= 3:
            risks.append({
                'risk_id': 'RISK_001',
                'category': 'market',
                'risk': '경쟁사 가격 인하',
                'probability': 'high',
                'impact': 'high',
                'severity': 'critical',
                'mitigation': [
                    '차별화 강화 (서비스 품질)',
                    '전환 비용 구축',
                    '브랜드 구축'
                ],
                'contingency': '가격 10% 추가 인하 가능'
            })
        
        # Risk 2: Churn 목표 미달
        target_churn = opportunity['unit_economics'].get('churn', 0.05)
        if target_churn <= 0.05:
            risks.append({
                'risk_id': 'RISK_002',
                'category': 'execution',
                'risk': 'Churn Rate 목표 미달성',
                'probability': 'medium',
                'impact': 'high',
                'severity': 'high',
                'mitigation': [
                    '온보딩 강화',
                    '고객 성공 팀',
                    '정기 피드백'
                ],
                'contingency': 'Churn 10% 초과 시 기능 개선'
            })
        
        # Risk 3: Unit Economics
        ltv = opportunity['unit_economics'].get('ltv', 0)
        cac = opportunity['unit_economics'].get('cac', 1)
        ltv_cac = ltv / cac if cac > 0 else 0
        
        if ltv_cac < 3:
            risks.append({
                'risk_id': 'RISK_003',
                'category': 'financial',
                'risk': 'Unit Economics 악화',
                'probability': 'medium',
                'impact': 'critical',
                'severity': 'critical',
                'mitigation': [
                    'CAC 최적화',
                    'LTV 증대 (Churn 개선)',
                    '가격 조정 검토'
                ],
                'contingency': 'Burn rate 감소'
            })
        
        # Critical Assumptions
        assumptions = [
            {
                'assumption_id': 'ASM_001',
                'assumption': f'Churn Rate {target_churn:.0%} 유지',
                'basis': 'Validator 벤치마크',
                'test_method': '첫 3개월 Beta 모니터링',
                'success_criteria': f'Beta Churn < {target_churn * 1.4:.0%}'
            },
            {
                'assumption_id': 'ASM_002',
                'assumption': f'가격 수용성',
                'basis': '경쟁사 대비 할인',
                'test_method': 'Beta 가격 테스트',
                'success_criteria': '전환율 > 10%'
            }
        ]
        
        return {
            'key_risks': risks,
            'critical_assumptions': assumptions
        }
    
    def _generate_playbook_markdown(
        self,
        opportunity: Dict,
        gtm: Dict,
        roadmap: Dict,
        resources: Dict,
        milestones: Dict,
        risks: Dict,
        project_name: str
    ) -> str:
        """Markdown 파일 생성"""
        
        from datetime import datetime
        
        # 저장 경로
        project_dir = Path(f"projects/{project_name}/02_analysis/explorer")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        md_path = project_dir / "strategy_playbook.md"
        
        # 현재 날짜
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Markdown 내용 생성
        content = f"""# Strategy Playbook: {opportunity.get('title')}

**생성일**: {today}
**Agent**: Explorer
**버전**: 1.0

---

## Executive Summary

### 기회 개요
- **제목**: {opportunity.get('title')}
- **가치 제안**: {opportunity.get('value_proposition')}
- **타겟 고객**: {opportunity.get('target_customer')}
- **SAM**: {quantified.get('sam')}억원
- **목표 점유율**: {quantified.get('target_share', 0.05):.1%}

### 핵심 Milestone
- **3개월**: {milestones['month_3']['milestone']} - MRR {milestones['month_3']['metrics']['mrr']}
- **6개월**: {milestones['month_6']['milestone']} - MRR {milestones['month_6']['metrics']['mrr']}
- **12개월**: {milestones['month_12']['milestone']} - ARR {milestones['month_12']['metrics']['arr']}

---

## GTM Strategy

### Customer Acquisition
- **Target Segment**: {gtm['customer_acquisition']['target_segment']}
- **Segment Size**: {gtm['customer_acquisition']['segment_size']:,}명/년

**Acquisition Channels**:
"""
        
        for ch in gtm['customer_acquisition']['channels']:
            content += f"\n{ch['priority']}. **{ch['channel']}** ({ch['timeline']})\n"
            content += f"   - CAC: {ch['cac_estimate']/10000:.0f}만원\n"
            content += f"   - Rationale: {ch['rationale']}\n"
        
        content += f"""

### Pricing
- **Model**: {gtm['pricing']['pricing_model']}
- **Price**: {gtm['pricing']['price_point']/10000:.0f}만원/월
- **Strategy**: {gtm['pricing']['pricing_strategy']}

---

## Product Roadmap

### MVP (3개월)
"""
        
        for feat in roadmap['mvp']['features']:
            content += f"- **{feat['feature']}** (RICE: {feat['rice_score']})\n"
        
        content += f"""

### Phase 2 (6개월)
"""
        
        for feat in roadmap['phase_2']['features']:
            content += f"- **{feat['feature']}** (RICE: {feat['rice_score']})\n"
        
        content += f"""

---

## Milestones

### Month 3: {milestones['month_3']['milestone']}
- **Metrics**: {milestones['month_3']['metrics']}
- **Activities**:
"""
        
        for act in milestones['month_3']['key_activities']:
            content += f"  - {act}\n"
        
        content += """

---

## Risk Register

"""
        
        for risk in risks['key_risks']:
            content += f"### {risk['risk_id']}: {risk['risk']}\n"
            content += f"- **Severity**: {risk['severity'].title()}\n"
            content += f"- **Mitigation**:\n"
            for mit in risk['mitigation']:
                content += f"  - {mit}\n"
            content += "\n"
        
        # 파일 저장
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"    ✅ Markdown 저장: {md_path}")
        
        return str(md_path)
    
    def _generate_playbook_excel(
        self,
        opportunity: Dict,
        gtm: Dict,
        roadmap: Dict,
        resources: Dict,
        milestones: Dict,
        risks: Dict,
        project_name: str
    ) -> str:
        """Excel 파일 생성 (openpyxl)"""
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            logger.warning("    ⚠️ openpyxl 없음, Excel 생성 스킵")
            return ""
        
        wb = Workbook()
        
        # Sheet 1: Executive Summary
        ws1 = wb.active
        ws1.title = "Executive Summary"
        ws1['A1'] = '항목'
        ws1['B1'] = '내용'
        ws1['A2'] = '기회 제목'
        ws1['B2'] = opportunity.get('title')
        ws1['A3'] = '가치 제안'
        ws1['B3'] = opportunity.get('value_proposition')
        ws1['A4'] = 'SAM'
        ws1['B4'] = f"{quantified.get('sam')}억원"
        
        # Sheet 2: GTM Strategy
        ws2 = wb.create_sheet("GTM Strategy")
        headers = ['영역', '전략', '세부 내용', '예산']
        for col, h in enumerate(headers, 1):
            ws2.cell(1, col, h)
        
        row = 2
        for ch in gtm['customer_acquisition']['channels']:
            ws2.cell(row, 1, '고객 획득')
            ws2.cell(row, 2, ch['channel'])
            ws2.cell(row, 3, ch['rationale'])
            ws2.cell(row, 4, f"{ch['cac_estimate']/10000:.0f}만원")
            row += 1
        
        # Sheet 3: Product Roadmap
        ws3 = wb.create_sheet("Product Roadmap")
        headers = ['Feature', 'RICE Score', 'Priority', 'Timeline']
        for col, h in enumerate(headers, 1):
            ws3.cell(1, col, h)
        
        row = 2
        for feat in roadmap['all_features']:
            ws3.cell(row, 1, feat['feature'])
            ws3.cell(row, 2, feat['rice_score'])
            ws3.cell(row, 3, feat['priority'])
            
            if feat['priority'] <= 3:
                timeline = 'MVP'
            elif feat['priority'] <= 7:
                timeline = 'Phase 2'
            else:
                timeline = 'Phase 3'
            ws3.cell(row, 4, timeline)
            row += 1
        
        # Sheet 4: Milestones
        ws4 = wb.create_sheet("Milestones")
        headers = ['Milestone', '타이밍', 'Metrics', 'Success Criteria']
        for col, h in enumerate(headers, 1):
            ws4.cell(1, col, h)
        
        for idx, (key, timing) in enumerate([('month_3', 'Month 3'), ('month_6', 'Month 6'), ('month_12', 'Month 12')], 2):
            ms = milestones[key]
            ws4.cell(idx, 1, ms['milestone'])
            ws4.cell(idx, 2, timing)
            ws4.cell(idx, 3, str(ms['metrics']))
            ws4.cell(idx, 4, '\n'.join(ms['success_criteria']))
        
        # Sheet 5: Risk Register
        ws5 = wb.create_sheet("Risk Register")
        headers = ['Risk ID', 'Risk', 'Severity', 'Mitigation']
        for col, h in enumerate(headers, 1):
            ws5.cell(1, col, h)
        
        for idx, risk in enumerate(risks['key_risks'], 2):
            ws5.cell(idx, 1, risk['risk_id'])
            ws5.cell(idx, 2, risk['risk'])
            ws5.cell(idx, 3, risk['severity'].title())
            ws5.cell(idx, 4, '\n'.join(risk['mitigation']))
        
        # Header 스타일
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        for ws in wb.worksheets:
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
        
        # 저장
        project_dir = Path(f"projects/{project_name}/02_analysis/explorer")
        project_dir.mkdir(parents=True, exist_ok=True)
        excel_path = project_dir / "strategy_playbook.xlsx"
        
        wb.save(excel_path)
        
        logger.info(f"    ✅ Excel 저장: {excel_path}")
        
        return str(excel_path)


# 편의 함수
def create_explorer_agent() -> ExplorerRAG:
    """Explorer RAG 에이전트 생성 (Factory)"""
    return ExplorerRAG()


def create_explorer_agentic() -> ExplorerAgenticRAG:
    """Explorer Agentic RAG 생성 (향후 자율 실행)"""
    return ExplorerAgenticRAG()

