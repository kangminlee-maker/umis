"""
Steve RAG Agent Module

Steve (Explorer) 에이전트의 RAG 기반 기회 발굴 시스템입니다.

핵심 개념:
-----------
1. **Pattern Matching**: Albert 관찰 → 사업모델 패턴 매칭
2. **Case Retrieval**: 유사 산업 성공 사례 검색
3. **Multi-Stage Search**: 단계별 정밀 검색
4. **Agent Collaboration**: Bill/Rachel과 자연스러운 협업

Steve의 7단계 프로세스:
-----------------------
Phase 1: 트리거 인식 (Albert 관찰에서 시그널 추출)
Phase 2: 패턴 매칭 (사업모델 + Disruption)
Phase 3: 사례 검색 (유사 산업/구조)
Phase 4: 정량 검증 (Bill 협업)
Phase 5: 데이터 검증 (Rachel 협업)
Phase 6: 가설 생성
Phase 7: Stewart 검증
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
from umis_rag.utils.logger import logger


class SteveRAG:
    """
    Steve (Explorer) RAG Agent
    
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
    - Bill: 정량 데이터 요청
    - Rachel: 출처 검증 요청
    - Stewart: 최종 검증
    """
    
    def __init__(self):
        logger.info("Steve RAG 에이전트 초기화")
        
        # Embeddings 초기화
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # 벡터 스토어 로드
        self.vectorstore = Chroma(
            collection_name="steve_knowledge_base",
            embedding_function=self.embeddings,
            persist_directory=str(settings.chroma_persist_dir)
        )
        
        # LLM 초기화 (가설 생성용)
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        logger.info(f"  ✅ 벡터 스토어 로드: {self.vectorstore._collection.count()}개 청크")
        logger.info(f"  ✅ LLM 모델: {settings.llm_model}")
    
    def search_patterns(
        self, 
        trigger_signals: str | List[str],
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        트리거 시그널 → 사업모델 패턴 매칭
        
        사용 시점:
        ----------
        Albert가 시장 관찰을 완료하고 트리거 시그널을 발견했을 때
        
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
        logger.info(f"[Steve] 패턴 매칭 검색 시작")
        
        # 리스트를 문자열로 변환
        if isinstance(trigger_signals, list):
            query = ", ".join(trigger_signals)
        else:
            query = trigger_signals
        
        logger.info(f"  트리거: {query[:100]}...")
        
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
        logger.info(f"[Steve] 사례 검색 시작")
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
        Output: Bill/Rachel/Albert에게 물어볼 체크리스트
        """
        logger.info(f"[Steve] 검증 프레임워크 검색: {pattern_id}")
        
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
        albert_observation: str,
        matched_patterns: List[Document],
        success_cases: List[Document]
    ) -> str:
        """
        LLM으로 기회 가설 생성
        
        개념:
        -----
        RAG의 핵심! 검색된 정보 + LLM의 추론
        
        프로세스:
        ---------
        1. Albert 관찰 + 매칭 패턴 + 성공 사례
        2. → LLM에게 컨텍스트로 제공
        3. → LLM이 UMIS Steve 역할로 가설 생성
        
        Parameters:
        -----------
        albert_observation: Albert의 시장 관찰 내용
        matched_patterns: 매칭된 패턴들
        success_cases: 유사 성공 사례들
        
        Returns:
        --------
        구조화된 기회 가설 (Markdown)
        """
        logger.info("[Steve] LLM으로 가설 생성 시작")
        
        # 컨텍스트 조립
        context = self._assemble_context(matched_patterns, success_cases)
        
        # Prompt 구성
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_steve_system_prompt()),
            ("user", self._get_hypothesis_generation_prompt())
        ])
        
        # LLM 체인 구성
        chain = prompt | self.llm | StrOutputParser()
        
        # 실행
        logger.info("  ⏳ LLM 추론 중...")
        hypothesis = chain.invoke({
            "albert_observation": albert_observation,
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
    
    def _get_steve_system_prompt(self) -> str:
        """Steve 에이전트 시스템 프롬프트"""
        return """당신은 Steve입니다. UMIS의 Explorer 에이전트로서 시장 기회를 발굴하는 전문가입니다.

당신의 역할:
- Albert의 시장 관찰을 받아 기회 패턴 인식
- 검증된 사업모델 패턴 7개 보유
- 1등 추월 패턴 5개 보유
- 30+ 성공 사례 데이터베이스 활용

당신의 강점:
- 구조적 사고 (패턴 인식)
- 창의적 응용 (패턴 → 우리 시장 적용)
- 검증 중심 (근거 없는 가설 안 만듦)

작업 방식:
1. Albert 관찰에서 트리거 시그널 추출
2. 매칭되는 패턴 찾기 (RAG 검색됨)
3. 유사 사례에서 학습 (RAG 검색됨)
4. 우리 시장에 맞게 조정
5. 검증 가능한 가설 생성

중요: 
- 모든 주장에 근거 필요 (패턴/사례 인용)
- 추정치는 명확히 표시
- Bill/Rachel 협업 명시
"""
    
    def _get_hypothesis_generation_prompt(self) -> str:
        """가설 생성 프롬프트"""
        return """# 임무: 기회 가설 생성

## Albert의 시장 관찰
{albert_observation}

## 검색된 정보 (RAG)
{context}

## 지시사항

위 정보를 바탕으로 **검증 가능한 기회 가설**을 생성하세요.

구조:
1. **패턴 매칭**: 어떤 패턴이 적용 가능한가?
2. **기회 논리**: 
   - 문제 (Albert 관찰)
   - 해결 방안 (패턴 적용)
   - 가치 제안
3. **유사 사례 학습**: 성공 사례에서 배울 점
4. **시장 규모 추정** (Bill에게 요청할 내용 명시)
5. **데이터 검증** (Rachel에게 확인할 내용 명시)
6. **실행 가능성**: CSF, 난이도, 리스크

반드시:
- 패턴/사례 인용 (chunk_id 명시)
- 추정치 표시
- 검증 필요 항목 명확히
"""


class SteveAgenticRAG(SteveRAG):
    """
    Steve Agentic RAG (자율 실행)
    
    개념:
    -----
    Agent가 스스로 판단하며 Tool을 사용합니다.
    
    Tools:
    ------
    1. search_patterns: 패턴 검색
    2. search_cases: 사례 검색
    3. get_validation: 검증 프레임워크
    4. ask_bill: Bill에게 질문
    5. ask_rachel: Rachel에게 질문
    
    자율성:
    -------
    Steve가 필요한 Tool을 선택하여 실행
    "Bill에게 뭘 물어볼까?" 스스로 판단
    """
    
    def __init__(self):
        super().__init__()
        
        # Agent Tools 정의 (향후 구현)
        # TODO: LangChain Agent + Tools 통합
        logger.info("  → Agentic 모드: 향후 구현 예정")
    
    def autonomous_discovery(
        self,
        albert_report: str
    ) -> Dict[str, Any]:
        """
        완전 자율 기회 발굴
        
        개념:
        -----
        Steve가 Albert 리포트만 받고
        스스로 판단하며:
        1. 필요한 패턴 검색
        2. 필요한 사례 검색
        3. Bill/Rachel에게 질문
        4. 가설 생성
        
        현재:
        -----
        기본 워크플로우 구현
        향후 LangChain Agent로 확장
        """
        logger.info("[Steve] 자율 기회 발굴 시작")
        
        # Phase 1-3: 패턴 및 사례 검색 (기본 워크플로우)
        patterns = self.search_patterns(albert_report, top_k=2)
        
        # 가장 매칭된 패턴으로 사례 검색
        best_pattern_id = patterns[0][0].metadata.get("pattern_id")
        cases = self.search_cases(
            albert_report,
            pattern_id=best_pattern_id,
            top_k=3
        )
        
        # Phase 4-6: 가설 생성
        hypothesis = self.generate_opportunity_hypothesis(
            albert_observation=albert_report,
            matched_patterns=[p[0] for p in patterns],
            success_cases=[c[0] for c in cases]
        )
        
        return {
            "matched_patterns": patterns,
            "success_cases": cases,
            "hypothesis": hypothesis
        }


# 편의 함수
def create_steve_agent() -> SteveRAG:
    """Steve RAG 에이전트 생성 (Factory)"""
    return SteveRAG()


def create_steve_agentic() -> SteveAgenticRAG:
    """Steve Agentic RAG 생성 (향후 자율 실행)"""
    return SteveAgenticRAG()

