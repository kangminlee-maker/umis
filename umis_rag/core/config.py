"""
Configuration management for UMIS RAG system.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='allow',  # .env에 추가 필드 허용
    )
    
    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    
    # ========================================
    # OpenAI API (하나의 키로 모든 모델 사용 가능)
    # ========================================
    # .env: OPENAI_API_KEY=sk-...
    openai_api_key: str
    # .env: OPENAI_ORG_ID=org-... (선택)
    openai_org_id: Optional[str] = Field(default=None)
    
    # Anthropic API (선택, v7.7.0+)
    # .env: ANTHROPIC_API_KEY=sk-ant-...
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # Embeddings API (벡터 변환용)
    # - text-embedding-3-small: $0.02/1M 토큰 (저렴, 기본 품질)
    # - text-embedding-3-large: $0.13/1M 토큰 (고품질, 미묘한 차이 인식) ⭐ 추천
    # - text-embedding-ada-002: $0.10/1M 토큰 (구버전, 비추천)
    # 
    # UMIS 권장: text-embedding-3-large
    # 이유: 향후 대용량 비정형 데이터, 미묘한 문맥 차이 중요, 비용 차이 미미
    # .env: EMBEDDING_MODEL=text-embedding-3-large
    embedding_model: str = Field(default="text-embedding-3-large")
    # .env: EMBEDDING_DIMENSION=3072
    embedding_dimension: int = Field(default=3072)  # large는 3072 차원
    
    # ========================================
    # LLM 최적화 전략 (v7.7.0+)
    # ========================================
    # Phase별 최적 모델 자동 선택
    # 기반: UMIS_LLM_OPTIMIZATION_FINAL.md
    # 효과: 98% 비용 절감 ($15 → $0.30/1,000회)
    #
    # Phase 0-2 (45%): gpt-4.1-nano ($0.000033/작업)
    #   - Literal, Inferred, Formula
    #   - 100% 정확도, 1.02초
    #
    # Phase 3 (48%): gpt-4o-mini ($0.000121/작업)
    #   - Guestimation (템플릿 있음/없음)
    #   - 100% 정확도, 4.61초
    #
    # Phase 4 (7%): o1-mini ($0.0033/작업)
    #   - Fermi Decomposition
    #   - 90-95% 정확도, 5-15초
    # ========================================

    # Legacy 설정 (하위 호환성)
    # .env: LLM_MODEL=gpt-4-turbo-preview
    llm_model: str = Field(default="gpt-4-turbo-preview")

    # Phase별 최적 모델 (v7.7.0+)
    # .env: LLM_MODEL_PHASE0_2=gpt-4.1-nano
    llm_model_phase0_2: str = Field(default="gpt-4.1-nano")
    # .env: LLM_MODEL_PHASE3=gpt-4o-mini
    llm_model_phase3: str = Field(default="gpt-4o-mini")
    # .env: LLM_MODEL_PHASE4=o1-mini
    llm_model_phase4: str = Field(default="o1-mini")

    # 모델 자동 선택 활성화
    # .env: USE_PHASE_BASED_ROUTING=true
    use_phase_based_routing: bool = Field(default=True)

    # .env: LLM_TEMPERATURE=0.7
    llm_temperature: float = Field(default=0.7)
    # .env: LLM_MAX_TOKENS=4096
    llm_max_tokens: int = Field(default=4096)
    
    # ========================================
    # Vector Database
    # ========================================
    # .env: VECTOR_DB=chroma (chroma / pinecone)
    vector_db: Literal["chroma", "pinecone"] = Field(default="chroma")
    # .env: CHROMA_PERSIST_DIR=./data/chroma
    chroma_persist_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data" / "chroma"
    )
    
    # Pinecone (optional)
    # .env: PINECONE_API_KEY=your-key (선택)
    pinecone_api_key: Optional[str] = Field(default=None)
    # .env: PINECONE_ENVIRONMENT=your-env (선택)
    pinecone_environment: Optional[str] = Field(default=None)
    # .env: PINECONE_INDEX_NAME=umis-rag (선택)
    pinecone_index_name: str = Field(default="umis-rag")
    
    # ========================================
    # Graph Database (Knowledge Graph)
    # ========================================
    # .env: NEO4J_URI=bolt://localhost:7687
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    # .env: NEO4J_USER=neo4j
    neo4j_user: str = Field(default="neo4j")
    # .env: NEO4J_PASSWORD=umis_password
    neo4j_password: str = Field(default="umis_password")
    # .env: NEO4J_DATABASE=neo4j
    neo4j_database: str = Field(default="neo4j")
    
    # ========================================
    # RAG Configuration (시스템 파라미터 - 코드에서 관리)
    # ========================================
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_results: int = 5
    
    # ========================================
    # Web Search Configuration (v7.6.2)
    # ========================================
    # 검색 엔진 선택: "duckduckgo" (무료) or "google" (유료, 고품질)
    # .env: WEB_SEARCH_ENGINE=duckduckgo
    web_search_engine: str = Field(default="google")
    
    # Google Custom Search (선택적)
    # - API 키: https://console.cloud.google.com/apis/credentials
    # - Search Engine ID: https://programmablesearchengine.google.com/
    # .env: GOOGLE_API_KEY=your-key
    # .env: GOOGLE_SEARCH_ENGINE_ID=your-id
    google_api_key: Optional[str] = Field(default=None)
    google_search_engine_id: Optional[str] = Field(default=None)
    
    # Web Search 활성화 여부
    # .env: WEB_SEARCH_ENABLED=true
    web_search_enabled: bool = Field(default=True)

    # 전체 페이지 크롤링 여부 (v7.7.0+)
    # true: 검색 결과 URL을 방문해서 실제 페이지 내용 크롤링 (정확도 향상)
    # false: snippet만 사용 (빠르지만 정보 제한적)
    # .env: WEB_SEARCH_FETCH_FULL_PAGE=true
    web_search_fetch_full_page: bool = Field(default=True)

    # 페이지당 최대 추출 문자 수 (기본 5000자)
    # .env: WEB_SEARCH_MAX_CHARS=5000
    web_search_max_chars: int = Field(default=5000)

    # 페이지 크롤링 타임아웃 (초)
    # .env: WEB_SEARCH_TIMEOUT=10
    web_search_timeout: int = Field(default=10)
    
    # ========================================
    # Agent Configuration (시스템 파라미터 - 코드에서 관리)
    # ========================================
    agent_temperature: float = 0.7
    agent_max_iterations: int = 10
    agent_verbose: bool = True
    
    # Logging
    # .env: LOG_LEVEL=INFO (변경 가능)
    log_level: str = Field(default="INFO")
    log_file: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs" / "umis_rag.log"
    )
    
    # Development
    dev_mode: bool = True
    cache_enabled: bool = True
    
    # LangSmith (optional)
    # .env: LANGCHAIN_TRACING_V2=false
    langchain_tracing_v2: bool = Field(default=False)
    # .env: LANGCHAIN_API_KEY=your-key (선택)
    langchain_api_key: Optional[str] = Field(default=None)
    # .env: LANGCHAIN_PROJECT=umis-rag
    langchain_project: str = Field(default="umis-rag")
    
    # UMIS 전역 설정 (v7.2.1+)
    # ========================================
    # LLM 모드 (v7.8.1: 직접 모델명 사용)
    # ========================================
    # .env: LLM_MODE=cursor (또는 gpt-4o-mini, o1-mini 등)
    # 
    # - cursor: Cursor AI 사용 (무료, 대화형)
    # - 기타: External API 사용 (model_configs.yaml 참조)
    llm_mode: str = Field(default="cursor")
    
    # ========================================
    # 한국 공공 데이터 API (v7.9.0)
    # ========================================
    # DART 전자공시 API
    # 발급: https://opendart.fss.or.kr → 인증키 신청/관리
    # .env: DART_API_KEY=your-key
    dart_api_key: Optional[str] = Field(default=None)
    
    # KOSIS 통계청 API
    # 발급: https://kosis.kr/openapi/index/index.jsp
    # .env: KOSIS_API_KEY=your-key
    kosis_api_key: Optional[str] = Field(default=None)
    
    # API Keys (선택)
    serpapi_key: Optional[str] = Field(default=None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

