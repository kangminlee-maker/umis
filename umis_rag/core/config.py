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
    
    # Chat API (대화/생성용)
    # - gpt-4-turbo-preview: $10/1M 토큰 (최신, 빠름)
    # - gpt-4: $30/1M 토큰 (안정적)
    # - gpt-3.5-turbo: $0.5/1M 토큰 (저렴)
    # .env: LLM_MODEL=gpt-4-turbo-preview
    llm_model: str = Field(default="gpt-4-turbo-preview")
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
    # RAG Configuration
    # ========================================
    # .env: CHUNK_SIZE=800
    chunk_size: int = Field(default=800)
    # .env: CHUNK_OVERLAP=100
    chunk_overlap: int = Field(default=100)
    # .env: TOP_K_RESULTS=5
    top_k_results: int = Field(default=5)
    
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
    
    # ========================================
    # Agent Configuration
    # ========================================
    # .env: AGENT_TEMPERATURE=0.7
    agent_temperature: float = Field(default=0.7)
    # .env: AGENT_MAX_ITERATIONS=10
    agent_max_iterations: int = Field(default=10)
    # .env: AGENT_VERBOSE=true
    agent_verbose: bool = Field(default=True)
    
    # Logging
    # .env: LOG_LEVEL=INFO
    log_level: str = Field(default="INFO")
    # .env: LOG_FILE=./logs/umis_rag.log
    log_file: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs" / "umis_rag.log"
    )
    
    # Development
    # .env: DEV_MODE=true
    dev_mode: bool = Field(default=True)
    # .env: CACHE_ENABLED=true
    cache_enabled: bool = Field(default=True)
    
    # LangSmith (optional)
    # .env: LANGCHAIN_TRACING_V2=false
    langchain_tracing_v2: bool = Field(default=False)
    # .env: LANGCHAIN_API_KEY=your-key (선택)
    langchain_api_key: Optional[str] = Field(default=None)
    # .env: LANGCHAIN_PROJECT=umis-rag
    langchain_project: str = Field(default="umis-rag")
    
    # UMIS 전역 설정 (v7.2.1+)
    umis_mode: str = Field(default="native")  # native / external
    
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

