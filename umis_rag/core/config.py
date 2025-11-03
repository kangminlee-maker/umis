"""
Configuration management for UMIS RAG system.
"""

from pathlib import Path
from typing import Literal

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
    openai_api_key: str
    openai_org_id: str | None = None
    
    # Embeddings API (벡터 변환용)
    # - text-embedding-3-small: $0.02/1M 토큰 (저렴, 기본 품질)
    # - text-embedding-3-large: $0.13/1M 토큰 (고품질, 미묘한 차이 인식) ⭐ 추천
    # - text-embedding-ada-002: $0.10/1M 토큰 (구버전, 비추천)
    # 
    # UMIS 권장: text-embedding-3-large
    # 이유: 향후 대용량 비정형 데이터, 미묘한 문맥 차이 중요, 비용 차이 미미
    embedding_model: str = "text-embedding-3-large"
    embedding_dimension: int = 3072  # large는 3072 차원
    
    # Chat API (대화/생성용)
    # - gpt-4-turbo-preview: $10/1M 토큰 (최신, 빠름)
    # - gpt-4: $30/1M 토큰 (안정적)
    # - gpt-3.5-turbo: $0.5/1M 토큰 (저렴)
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    
    # ========================================
    # Vector Database
    # ========================================
    vector_db: Literal["chroma", "pinecone"] = "chroma"
    chroma_persist_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data" / "chroma"
    )
    
    # Pinecone (optional)
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None
    pinecone_index_name: str = "umis-rag"
    
    # ========================================
    # Graph Database (Knowledge Graph)
    # ========================================
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "umis_password"
    neo4j_database: str = "neo4j"
    
    # ========================================
    # RAG Configuration
    # ========================================
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_results: int = 5
    
    # ========================================
    # Agent Configuration
    # ========================================
    agent_temperature: float = 0.7
    agent_max_iterations: int = 10
    agent_verbose: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs" / "umis_rag.log"
    )
    
    # Development
    dev_mode: bool = True
    cache_enabled: bool = True
    
    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "umis-rag"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

