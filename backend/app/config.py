from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    postgres_user: str = "rag"
    postgres_password:str = "rag"
    postgres_db: str = "cinedb"
    postgres_host:str = "localhost"
    postgres_port:str = 5432

    groq_api_key:str = ""
    tmdb_api_key:str = ""

    llm_model:str = "llama-3.1-8b-instant"

    embedding_model_name:str = "all-MiniLM-L6-V2"

    secret_key:str = ""
    access_token_expire_minutes:int = 60
    skip_db_init: bool = False
    

settings = Settings()
