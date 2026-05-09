from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI / HuggingFace
    openai_api_key: str
    openai_base_url: str
    model_name: str
    hf_token: str

    # Database
    database_url: str

    # JWT
    secret_key: str
    jwt_algorithm: str
    jwt_expiry_minutes: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
