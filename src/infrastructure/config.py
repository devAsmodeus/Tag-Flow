from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mode: Literal["LOCAL", "TEST", "PROD"] = Field(default="LOCAL", alias="MODE")

    database_url: str = Field(alias="DATABASE_URL")

    wb_token: str = Field(alias="WB_API_TOKEN")
    ozon_client_id: str = Field(alias="OZON_CLIENT_ID")
    ozon_api_key: str = Field(alias="OZON_API_KEY")
    ym_token: str = Field(alias="YM_API_TOKEN")
    ym_business_id: str = Field(alias="YM_BUSINESS_ID")

    ollama_url: str = Field(default="http://localhost:11434", alias="OLLAMA_URL")
    tagger_model: str = Field(default="qwen3:8b", alias="TAGGER_MODEL")
    responder_model: str = Field(default="qwen3:8b", alias="RESPONDER_MODEL")

    poll_interval_minutes: int = Field(default=30, alias="POLL_INTERVAL_MINUTES")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    batch_size: int = Field(default=100, alias="BATCH_SIZE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def is_test(self) -> bool:
        return self.mode == "TEST"
