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
import requests
from bs4 import BeautifulSoup

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


class AIAugmentedEstimationSource(ValueSourceBase):
    """
    AI 증강 추정 (v7.8.0)
    
    역할:
    -----
    - LLM + Web 통합 (기존 LLMEstimationSource + WebSearchSource)
    - LLM 지식 우선 → 불확실하면 웹 검색
    - Cursor: instruction 반환 (AI가 실행)
    - API: External LLM API 호출 (자동 실행)
    - confidence 0.55-0.90
    
    통합 이유:
    ----------
    - LLM과 Web 모두 "외부에서 값 가져오기"
    - 웹 검색은 LLM이 불확실할 때 보조 수단
    - Cursor 모드에서 LLM Source 활용도 0% 문제 해결 (v7.8.1)
    """
    
    def __init__(self, llm_mode: str = "native"):
        self.llm_mode = llm_mode
        
        from umis_rag.core.config import settings
        self.web_search_enabled = settings.web_search_enabled
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """AI 증강 추정"""
        
        if self.llm_mode == "skip":
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Cursor AI: instruction 생성 (Phase 3에서는 사용 불가)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.llm_mode == "cursor":  # v7.8.1: cursor = Cursor AI
            logger.info(f"  [AI+Web] Cursor AI: instruction 생성 (Phase 3 스킵)")
            
            instruction = self._build_native_instruction(question, context)
            
            # v7.8.1: Cursor AI에서는 빈 리스트 반환
            # 이유: value=0.0은 False로 평가되어 판단 실패 발생
            # instruction은 Phase 4에서만 사용
            logger.info(f"  [AI+Web] Cursor AI: Phase 3에서 사용 불가 → 빈 값 반환")
            return []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # API Mode: External LLM API 호출 (v7.8.1)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        else:  # External LLM
            logger.info(f"  [AI+Web] API Mode (모델: {self.llm_mode})")
            
            try:
                # Instruction 생성 (Native 로직 재사용)
                instruction = self._build_native_instruction(question, context)
                
                # LLM API 호출
                from umis_rag.core.model_configs import get_model_config
                from openai import OpenAI
                
                model_config = get_model_config(self.llm_mode)
                api_params = model_config.build_api_params(instruction)
                
                # OpenAI 클라이언트
                import os
                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                
                # API 호출 (api_type에 따라 분기)
                if model_config.api_type == 'responses':
                    response = client.responses.create(**api_params)
                    # 응답 파싱
                    llm_output = response.output_text if hasattr(response, 'output_text') else str(response.output[0].content[0].text)
                
                elif model_config.api_type == 'chat':
                    # System message 추가
                    if 'messages' in api_params:
                        api_params['messages'].insert(0, {
                            "role": "system",
                            "content": "당신은 시장 분석 전문가입니다. 항상 JSON 형식으로만 답변하세요."
                        })
                    response = client.chat.completions.create(**api_params)
                    llm_output = response.choices[0].message.content
                
                else:
                    logger.warning(f"  [AI+Web] 지원하지 않는 api_type: {model_config.api_type}")
                    return []
                
                logger.info(f"  [AI+Web] LLM 응답 수신 ({len(llm_output)}자)")
                
                # JSON 파싱 (벤치마크 패턴 활용)
                parsed_data = self._parse_llm_json_response(llm_output)
                
                if not parsed_data:
                    logger.warning(f"  [AI+Web] JSON 파싱 실패")
                    return []
                
                # ValueEstimate 생성
                if 'value' not in parsed_data:
                    logger.warning(f"  [AI+Web] 'value' 키 없음")
                    return []
                
                estimate = ValueEstimate(
                    source_type=SourceType.AI_AUGMENTED,
                    value=float(parsed_data['value']),
                    confidence=parsed_data.get('confidence', 0.70),
                    reasoning=parsed_data.get('reasoning', 'AI 증강 추정'),
                    source_detail=f"LLM: {self.llm_mode}",
                    raw_data=parsed_data
                )
                
                logger.info(f"  [AI+Web] 추정 완료: {estimate.value} (신뢰도: {estimate.confidence:.2f})")
                
                return [estimate]
            
            except Exception as e:
                logger.error(f"  [AI+Web] API 호출 실패: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return []
    
    def _parse_llm_json_response(self, llm_output: str) -> Optional[Dict]:
        """
        LLM 응답에서 JSON 추출 및 파싱
        
        벤치마크 패턴 적용:
        1. ```json ... ``` 블록 추출
        2. ``` ... ``` 일반 블록 추출
        3. Raw JSON 파싱
        
        Args:
            llm_output: LLM 응답 텍스트
        
        Returns:
            파싱된 Dict 또는 None
        """
        import json
        
        try:
            content = llm_output
            
            # 1. JSON 코드 블록 추출 (```json ... ```)
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
                logger.debug("  [Parser] JSON 블록 감지 (```json)")
            
            # 2. 일반 코드 블록 추출 (``` ... ```)
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
                logger.debug("  [Parser] 코드 블록 감지 (```)")
            
            else:
                logger.debug("  [Parser] 코드 블록 없음, Raw JSON 파싱 시도")
            
            # 3. JSON 파싱
            parsed = json.loads(content)
            logger.debug(f"  [Parser] JSON 파싱 성공")
            
            return parsed
        
        except json.JSONDecodeError as e:
            logger.debug(f"  [Parser] JSON 파싱 실패: {e}")
            logger.debug(f"  [Parser] 응답 미리보기: {llm_output[:200]}...")
            return None
        
        except Exception as e:
            logger.debug(f"  [Parser] 예외 발생: {e}")
            return None
    
    def _build_native_instruction(
        self,
        question: str,
        context: Optional[Context]
    ) -> str:
        """
        Cursor AI instruction 생성 (v7.8.1)
        
        AI에게 제공할 상세한 로직
        """
        
        # Context 정보
        domain_info = f"도메인: {context.domain}" if context and context.domain else ""
        region_info = f"지역: {context.region}" if context and context.region else ""
        time_info = f"시점: {context.time_period}" if context and context.time_period else ""
        
        context_block = "\n".join([info for info in [domain_info, region_info, time_info] if info])
        
        instruction = f"""# AI Augmented Estimation

**질문**: {question}
{context_block}

---

## 📋 임무

값을 추정하세요. 다음 프로세스를 따르세요:

### Step 1: 지식 기반 추정 (우선)

먼저 **당신의 지식**(학습 데이터)으로 답변을 시도하세요.

**자가 평가**:
- 확신도 **≥ 80%**: 즉시 값 반환 (Step 2 스킵) ✅
- 확신도 **< 80%**: Step 2로 진행 (웹 검색 필요)

**반환 형식** (확신도 ≥ 80%):
```json
{{
    "value": 추정값,
    "confidence": 0.80,
    "reasoning": "지식 기반 추정 (출처: ...)",
    "web_searched": false
}}
```

---

### Step 2: 웹 검색 수행 (확신도 < 80%인 경우만)

구글 또는 네이버에서 검색을 수행하세요.

**검색어 구성**:
```
기본: "{question}"
"""
        
        if context:
            if context.region:
                instruction += f'\n지역 추가: "{context.region} {question}"'
            if context.time_period:
                instruction += f'\n시점 추가: "{question} {context.time_period}"'
        
        instruction += """
통계/데이터 키워드 추가: "statistics", "data", "통계"
```

**검색 범위**:
- 상위 **5-10개** 결과 확인
- 신뢰 출처 우선 (정부, 통계청, 위키피디아, 학술 논문)

---

### Step 3: 숫자 추출 및 변환

각 검색 결과에서 **관련 숫자**를 찾으세요.

**단위 변환 규칙**:
```
영어 약자:
  51.7M → 51,700,000
  2.3B → 2,300,000,000
  850K → 850,000

한국어 단위:
  5170만 → 51,700,000
  2조 3000억 → 2,300,000,000,000
  85만 → 850,000

비율:
  5.2% → 0.052
  6-8% → 0.07 (중간값)
```

**관련성 필터링**:
- 질문과 관련 있는 숫자만 추출
- 예: "인구" 질문에 "GDP" 숫자는 제외

---

### Step 4: Consensus 계산

추출된 숫자들의 **합의값**을 계산하세요.

**이상치 제거**:
1. 모든 숫자의 **중앙값(median)** 계산
2. 중앙값의 **±50% 범위** 벗어난 값 제거
3. 남은 숫자들의 **평균** 계산

**예시**:
```
추출: [51.7M, 51.5M, 52.1M, 120M, 51.8M]
      ↓
중앙값: 51.8M
±50% 범위: [25.9M, 77.7M]
      ↓
이상치: 120M (범위 벗어남) → 제거
      ↓
최종 평균: (51.7 + 51.5 + 52.1 + 51.8) / 4 = 51.775M
```

**Confidence 규칙**:
```
일치 출처 개수에 따라:
- 5개 이상: 0.80
- 4개: 0.75
- 3개: 0.70
- 2개: 0.65
- 1개만: 0.55

신뢰 출처 보너스:
- 정부/통계청: +0.05
- 최신 데이터(2024): +0.03
```

---

### Step 5: 결과 반환

다음 JSON 형식으로 반환하세요:

```json
{{
    "value": 51775000,
    "confidence": 0.75,
    "reasoning": "웹 검색 4개 출처 평균 (Wikipedia 51.7M, 통계청 51.5M, 네이버 52.1M, CIA 51.8M). 이상치 1개(120M) 제거.",
    "sources_count": 4,
    "source_detail": "Google 검색",
    "web_searched": true,
    "extracted_numbers": [
        {{"value": 51700000, "source": "Wikipedia"}},
        {{"value": 51500000, "source": "통계청"}},
        {{"value": 52100000, "source": "네이버"}},
        {{"value": 51800000, "source": "CIA"}}
    ]
}}
```

---

## ✅ 체크리스트

- [ ] Step 1: 지식 기반 추정 (확신도 평가)
- [ ] Step 2: 웹 검색 (필요시만)
- [ ] Step 3: 숫자 추출 및 단위 변환
- [ ] Step 4: Consensus 계산 (이상치 제거)
- [ ] Step 5: 결과 반환 (JSON 형식)

**중요**: 
- 웹 검색은 **선택적** (LLM이 불확실할 때만)
- 확실하면 지식만으로 답변 (빠름, $0)
- 불확실할 때만 웹 검색 (느림, but 정확)
"""
        
        return instruction


class LLMEstimationSource(ValueSourceBase):
    """
    ⚠️ DEPRECATED (v7.8.0)
    
    → AIAugmentedEstimationSource로 통합됨
    
    LLM 추정
    
    역할:
    -----
    - LLM에게 직접 질문
    - Cursor Mode (Cursor AI) or API Mode (External LLM)
    - confidence 0.60-0.90
    """
    
    def __init__(self, llm_mode: str = "native"):
        self.llm_mode = llm_mode
        logger.warning("⚠️ LLMEstimationSource는 deprecated. AIAugmentedEstimationSource 사용 권장")
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """LLM 추정 (deprecated)"""
        
        if self.llm_mode == "skip":
            return []
        
        # 간단한 사실 질문만 (복잡한 건 Tier 2에서)
        if not self._is_simple_factual(question):
            return []
        
        # TODO: 실제 LLM 호출
        # 현재는 스킵
        logger.info(f"  [LLM] 스킵 (deprecated → AIAugmented 사용)")
        
        return []
    
    def _is_simple_factual(self, question: str) -> bool:
        """간단한 사실 질문인가?"""
        factual_keywords = ['인구', '면적', 'gdp', '수도']
        return any(kw in question.lower() for kw in factual_keywords)


class WebSearchSource(ValueSourceBase):
    """
    ⚠️ DEPRECATED (v7.8.0)
    
    → AIAugmentedEstimationSource로 통합됨
    
    웹 검색 (v7.6.2)
    
    역할:
    -----
    - 웹에서 최신 데이터 검색
    - 여러 결과에서 숫자 추출
    - consensus 알고리즘 (다수 일치)
    - confidence 0.60-0.80
    
    구현:
    -----
    - DuckDuckGo (무료, API 키 불필요)
    - Google Custom Search (유료, 고품질)
    - 페이지 크롤링 (v7.7.0)
    
    v7.8.0: AIAugmentedEstimationSource 사용 권장
    """
    
    def __init__(self):
        """
        초기화 (v7.6.2 - 동적 엔진 선택)
        
        .env 설정:
          WEB_SEARCH_ENGINE=duckduckgo (기본, 무료)
          또는
          WEB_SEARCH_ENGINE=google
          GOOGLE_API_KEY=your-key
          GOOGLE_SEARCH_ENGINE_ID=your-id
          WEB_SEARCH_FETCH_FULL_PAGE=true (페이지 크롤링, v7.7.0+)
        """
        from umis_rag.core.config import settings
        
        self.enabled = settings.web_search_enabled
        self.engine = settings.web_search_engine.lower()
        self.fetch_full_page = settings.web_search_fetch_full_page
        self.max_chars = settings.web_search_max_chars
        self.timeout = settings.web_search_timeout
        
        # 검색 엔진별 초기화
        if self.engine == "google":
            self._init_google()
        else:  # duckduckgo (기본)
            self._init_duckduckgo()
    
    def _init_duckduckgo(self):
        """DuckDuckGo 초기화"""
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.has_search = True
            fetch_status = "크롤링 활성화" if self.fetch_full_page else "snippet만"
            logger.info(f"  [Web] DuckDuckGo 준비 (무료, {fetch_status})")
        except ImportError:
            logger.warning("  [Web] duckduckgo-search 패키지 없음 (pip install ddgs)")
            self.has_search = False
    
    def _init_google(self):
        """Google Custom Search 초기화"""
        from umis_rag.core.config import settings
        
        try:
            from googleapiclient.discovery import build
            
            if not settings.google_api_key or not settings.google_search_engine_id:
                logger.warning("  [Web] Google API 키 또는 Search Engine ID 없음")
                logger.warning("  [Web] .env에 GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID 설정 필요")
                self.has_search = False
                return
            
            self.google_service = build(
                "customsearch",
                "v1",
                developerKey=settings.google_api_key
            )
            self.google_engine_id = settings.google_search_engine_id
            self.has_search = True
            
            fetch_status = "크롤링 활성화" if self.fetch_full_page else "snippet만"
            logger.info(f"  [Web] Google Custom Search 준비 (유료, 고품질, {fetch_status})")
        
        except ImportError:
            logger.warning("  [Web] google-api-python-client 패키지 없음")
            logger.warning("  [Web] pip install google-api-python-client")
            self.has_search = False
        
        except Exception as e:
            logger.warning(f"  [Web] Google 초기화 실패: {e}")
            self.has_search = False
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """
        웹 검색
        
        프로세스:
        1. 검색 쿼리 구성
        2. DuckDuckGo 검색 (top 5)
        3. 결과에서 숫자 추출
        4. consensus 확인 (여러 출처 일치)
        5. ValueEstimate 반환
        """
        if not self.has_search or not self.enabled:
            logger.info(f"  [Web] 비활성화")
            return []
        
        # 사실 질문만 (수치 질문)
        if not self._is_numerical_question(question):
            logger.info(f"  [Web] 수치 질문 아님 → 스킵")
            return []
        
        logger.info(f"  [Web] 검색 시작 (엔진: {self.engine})")
        
        try:
            # 검색 쿼리 구성
            search_query = self._build_search_query(question, context)
            logger.info(f"    쿼리: {search_query}")
            
            # 엔진별 검색 실행
            if self.engine == "google":
                results = self._search_google(search_query)
            else:  # duckduckgo
                results = self._search_duckduckgo(search_query)
            
            if not results:
                logger.info(f"    검색 결과 없음")
                return []
            
            logger.info(f"    {len(results)}개 결과 발견")
            
            # 숫자 추출
            extracted_numbers = self._extract_numbers_from_results(
                results, question
            )
            
            if not extracted_numbers:
                logger.info(f"    숫자 추출 실패 (패턴 매칭 안됨)")
                # 디버깅: 결과 샘플 출력
                if results:
                    sample = results[0]
                    logger.info(f"    샘플: {sample.get('title', '')[:50]}...")
                return []
            
            logger.info(f"    {len(extracted_numbers)}개 숫자 추출됨")
            
            # Consensus 확인 (여러 출처에서 유사한 값)
            consensus = self._find_consensus(extracted_numbers, question)
            
            if consensus:
                logger.info(f"    Consensus: {consensus['value']} (신뢰도: {consensus['confidence']:.2f})")
                
                return [ValueEstimate(
                    source_type=SourceType.AI_AUGMENTED,  # v7.8.1: WEB_SEARCH deprecated
                    value=consensus['value'],
                    confidence=consensus['confidence'],
                    reasoning=f"웹 검색 consensus ({consensus['count']}개 출처 일치)",
                    source_detail=f"DuckDuckGo: {search_query}",
                    raw_data={'sources': consensus['sources']}
                )]
            else:
                logger.info(f"    Consensus 없음 (값 분산)")
                return []
        
        except Exception as e:
            logger.warning(f"  [Web] 검색 실패: {e}")
            return []
    
    def _fetch_page_content(self, url: str) -> Optional[str]:
        """
        웹 페이지 크롤링 (v7.7.0+)

        Args:
            url: 크롤링할 URL

        Returns:
            페이지 텍스트 (최대 max_chars), 실패 시 None
        """
        try:
            # User-Agent 헤더 (일부 사이트는 봇 차단)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # 페이지 가져오기 (타임아웃 적용)
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(response.content, 'html.parser')

            # 불필요한 태그 제거 (스크립트, 스타일, 네비게이션 등)
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                tag.decompose()

            # 텍스트 추출
            text = soup.get_text(separator=' ', strip=True)

            # 공백 정리
            text = ' '.join(text.split())

            # 최대 문자 수 제한
            if len(text) > self.max_chars:
                text = text[:self.max_chars]

            logger.debug(f"    크롤링 성공: {url[:50]}... ({len(text)}자)")
            return text

        except requests.Timeout:
            logger.debug(f"    타임아웃: {url[:50]}...")
            return None

        except requests.RequestException as e:
            logger.debug(f"    요청 실패: {url[:50]}... ({e})")
            return None

        except Exception as e:
            logger.debug(f"    파싱 실패: {url[:50]}... ({e})")
            return None

    def _search_duckduckgo(self, query: str) -> list:
        """
        DuckDuckGo 검색 실행

        Returns:
            [{'title': str, 'body': str, 'href': str}, ...]
        """
        try:
            results = self.ddgs.text(
                keywords=query,
                max_results=5
            )

            if not results:
                return []

            # 페이지 크롤링 활성화된 경우
            if self.fetch_full_page:
                logger.info(f"    페이지 크롤링 시작 ({len(results)}개)")

                enriched_results = []
                for result in results:
                    url = result.get('href', '')

                    if url:
                        # 페이지 크롤링 시도
                        full_content = self._fetch_page_content(url)

                        if full_content:
                            # 크롤링 성공: snippet 대신 전체 내용 사용
                            result['body'] = full_content
                        # 크롤링 실패: 기존 snippet 유지

                    enriched_results.append(result)

                return enriched_results
            else:
                # snippet만 사용
                return results

        except Exception as e:
            logger.warning(f"    DuckDuckGo 검색 실패: {e}")
            return []
    
    def _search_google(self, query: str) -> list:
        """
        Google Custom Search 실행

        Returns:
            [{'title': str, 'body': str, 'href': str}, ...]
            (DuckDuckGo와 동일한 형식으로 변환)
        """
        try:
            response = self.google_service.cse().list(
                q=query,
                cx=self.google_engine_id,
                num=5
            ).execute()

            items = response.get('items', [])

            # DuckDuckGo 형식으로 변환
            results = []
            for item in items:
                result = {
                    'title': item.get('title', ''),
                    'body': item.get('snippet', ''),
                    'href': item.get('link', '')
                }
                results.append(result)

            # 페이지 크롤링 활성화된 경우
            if self.fetch_full_page and results:
                logger.info(f"    페이지 크롤링 시작 ({len(results)}개)")

                enriched_results = []
                for result in results:
                    url = result.get('href', '')

                    if url:
                        # 페이지 크롤링 시도
                        full_content = self._fetch_page_content(url)

                        if full_content:
                            # 크롤링 성공: snippet 대신 전체 내용 사용
                            result['body'] = full_content
                            logger.debug(f"    ✓ {url[:40]}... → {len(full_content)}자")
                        else:
                            # 크롤링 실패: snippet 유지
                            logger.debug(f"    ✗ {url[:40]}... → snippet 유지")

                    enriched_results.append(result)

                return enriched_results
            else:
                # snippet만 사용
                return results

        except Exception as e:
            logger.warning(f"    Google 검색 실패: {e}")
            return []
    
    def _is_numerical_question(self, question: str) -> bool:
        """수치 질문인지 확인"""
        numerical_keywords = [
            '수', '개수', '몇', '얼마', '평균', '비율', '률', '규모', '인구',
            'count', 'how many', 'average', 'rate', 'size', 'population'
        ]
        
        # "얼마인가", "몇인가" 등 질문 형태도 포함
        if '?' in question or '인가' in question:
            return True
        
        return any(kw in question.lower() for kw in numerical_keywords)
    
    def _build_search_query(
        self,
        question: str,
        context: Optional[Context]
    ) -> str:
        """검색 쿼리 구성"""
        
        # Context 추가 (중복 방지)
        if context:
            parts = []
            
            # Region이 이미 질문에 포함되어 있지 않으면 추가
            if context.region and context.region.lower() not in question.lower():
                parts.append(context.region)
            
            # Domain도 중복 체크
            if context.domain and context.domain != "General":
                domain_text = context.domain.replace('_', ' ')
                if domain_text.lower() not in question.lower():
                    parts.append(domain_text)
            
            parts.append(question)
            
            query = " ".join(parts)
        else:
            query = question
        
        # "statistics" 추가 (영어 쿼리만, 정확도 향상)
        # 한국어 쿼리에는 추가하지 않음 (영어 검색 엔진에서 혼란)
        has_korean = any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in query)
        
        if not has_korean and 'statistics' not in query.lower():
            query += " statistics"
        
        return query
    
    def _extract_numbers_from_results(
        self,
        results: list,
        question: str
    ) -> list:
        """
        검색 결과에서 숫자 추출 (개선)
        
        Returns:
            [{'value': float, 'source': str, 'context': str}, ...]
        """
        import re
        
        extracted = []
        
        for result in results:
            title = result.get('title', '')
            body = result.get('body', '')
            text = f"{title} {body}"
            source = result.get('href', 'unknown')
            
            # 숫자 패턴 (개선 - 영어 단위 약자 추가)
            patterns = [
                # 영어 단위 약자 (51.7M, 3.5B, 100K) - 최우선!
                (r'(\d+(?:\.\d+)?)\s*([MBK])\b', 'english_abbreviation'),
                
                # 한국어 큰 숫자 (51,740,000명)
                (r'(\d{1,3}(?:,\d{3})+)', r'([조억만천백십]?[원명개갑점호대%]|명|개|원|조|억|만)'),
                
                # 일반 숫자 + 단위
                (r'(\d+(?:\.\d+)?)', r'\s*([조억만천]?[원명개갑점호대%]|%)'),
                
                # 백분율
                (r'(\d+(?:\.\d+)?)', r'%'),
            ]
            
            for num_pattern, unit_pattern in patterns:
                # 영어 약자는 특별 처리
                if unit_pattern == 'english_abbreviation':
                    matches = re.findall(num_pattern, text, re.IGNORECASE)
                else:
                    # 숫자와 단위를 함께 찾기
                    combined_pattern = num_pattern + r'\s*' + unit_pattern
                    matches = re.findall(combined_pattern, text)
                
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        num_str = match[0]
                        unit = match[1] if len(match) > 1 else ""
                    else:
                        num_str = str(match)
                        unit = ""
                    
                    try:
                        # 쉼표 제거
                        num_str = num_str.replace(',', '')
                        
                        # 숫자 변환
                        value = float(num_str)
                        
                        # 영어 단위 약자 변환
                        if unit.upper() == 'M':
                            value *= 1_000_000
                        elif unit.upper() == 'B':
                            value *= 1_000_000_000
                        elif unit.upper() == 'K':
                            value *= 1_000
                        
                        # 한국어 단위 변환
                        elif '조' in unit and '억' not in unit:  # 조 단독
                            value *= 1_000_000_000_000
                        elif '억' in unit and '조' not in unit:  # 억 단독
                            value *= 100_000_000
                        elif '만' in unit and '억' not in unit:  # 만 단독
                            value *= 10_000
                        
                        # 백분율 → 비율
                        if '%' in unit or '%' in text[text.find(num_str):text.find(num_str)+20]:
                            if value > 1:  # 백분율 형태
                                value = value / 100
                        
                        # 너무 작거나 너무 큰 값 필터링
                        if value <= 0 or value > 1e18:
                            continue
                        
                        # 맥락 추출
                        num_pos = text.find(num_str)
                        if num_pos >= 0:
                            context_start = max(0, num_pos - 50)
                            context_end = min(len(text), num_pos + 100)
                            context_text = text[context_start:context_end]
                        else:
                            context_text = title[:100] if title else body[:100]
                        
                        extracted.append({
                            'value': value,
                            'unit': unit,
                            'source': source,
                            'context': context_text,
                            'original': f"{num_str} {unit}"
                        })
                    
                    except Exception as e:
                        # 숫자 변환 실패는 무시
                        continue
        
        # 중복 제거 (같은 값)
        unique = []
        seen_values = set()
        
        for item in extracted:
            val = item['value']
            # ±5% 범위로 중복 체크 (division by zero 방지)
            is_duplicate = False
            for seen in seen_values:
                if seen == 0 and val == 0:
                    is_duplicate = True
                    break
                max_val = max(abs(seen), abs(val))
                if max_val > 0 and abs(val - seen) / max_val < 0.05:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(item)
                seen_values.add(val)
        
        return unique
    
    def _find_consensus(self, extracted_numbers: list, question: str = "") -> Optional[Dict]:
        """
        Consensus 찾기 (여러 출처에서 유사한 값)
        
        Args:
            extracted_numbers: [{'value': ..., 'source': ...}, ...]
            question: 질문 (관련성 필터링용)
        
        Returns:
            {
                'value': float,
                'confidence': float,
                'count': int,
                'sources': [...]
            } or None
        """
        if len(extracted_numbers) < 1:
            return None
        
        # 관련성 필터링: 값들을 크기별로 그룹화
        # 예: 인구(51M)와 성장률(2.4%)이 섞이면 분리
        if len(extracted_numbers) > 1:
            values = [item['value'] for item in extracted_numbers]
            max_val = max(values)
            min_val = min([v for v in values if v > 0], default=0)
            
            # 최대값과 최소값의 차이가 1000배 이상이면
            # 큰 값들만 사용 (인구 같은 절대값 질문으로 추정)
            if max_val / max(min_val, 0.001) > 1000:
                extracted_numbers = [item for item in extracted_numbers if item['value'] > max_val / 100]
        
        if len(extracted_numbers) < 2:
            # 값이 1개뿐이면 그대로 반환 (신뢰도 낮춤)
            if len(extracted_numbers) == 1:
                return {
                    'value': extracted_numbers[0]['value'],
                    'confidence': 0.50,  # 낮은 신뢰도
                    'count': 1,
                    'sources': [extracted_numbers[0]['source']]
                }
            return None
        
        # 값들을 그룹화 (±30% 범위 내면 같은 그룹)
        groups = []
        
        for item in extracted_numbers:
            value = item['value']
            
            # 기존 그룹에 속하는지 확인
            found_group = False
            
            for group in groups:
                group_avg = sum(g['value'] for g in group) / len(group)
                
                # ±30% 범위 내
                if abs(value - group_avg) / group_avg < 0.30:
                    group.append(item)
                    found_group = True
                    break
            
            if not found_group:
                groups.append([item])
        
        # 가장 큰 그룹 찾기
        if not groups:
            return None
        
        largest_group = max(groups, key=len)
        
        # 2개 이상 일치해야 consensus
        if len(largest_group) < 2:
            return None
        
        # 평균 계산
        avg_value = sum(item['value'] for item in largest_group) / len(largest_group)
        
        # Confidence: 일치하는 출처 개수에 비례
        # 2개: 0.60, 3개: 0.70, 4개+: 0.80
        confidence_map = {2: 0.60, 3: 0.70, 4: 0.80, 5: 0.85}
        confidence = confidence_map.get(len(largest_group), 0.85)
        
        return {
            'value': avg_value,
            'confidence': confidence,
            'count': len(largest_group),
            'sources': [item['source'] for item in largest_group]
        }


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

