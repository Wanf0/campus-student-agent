from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 大模型
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 数据
    database_url: str = "sqlite:///./campus_agent.db"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    rerank_model: str = "BAAI/bge-reranker-base"
    chroma_dir: str = "./chroma_data"

    # 检索
    retrieval_top_k: int = 8
    final_top_k: int = 4
    rerank_score_threshold: float = 0.3  # 相关性分级阈值

    # Agent
    agent_max_steps: int = 6          # 最大步数
    agent_max_rewrite_retries: int = 2  # 改写重试上限

    # 服务
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"


settings = Settings()
