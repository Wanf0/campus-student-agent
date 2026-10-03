from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./campus_agent.db"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    chroma_dir: str = "./chroma_data"

    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
