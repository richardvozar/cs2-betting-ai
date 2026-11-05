from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = "postgresql+psycopg://cs2ai:password@localhost:5432/cs2_betting_ai"
    cs2_api_base_url: str = "https://api.citoapi.com/api/v1"
    cs2_api_key: str = ""
    cs2_api_timeout: int = 30
    cs2_page_size: int = 100
    cs2_max_pages: int = 5
    cs2_api_sample_dir: str = "data/api_samples"

    @property
    def api_headers(self):
        headers = {"Accept": "application/json"}
        if self.cs2_api_key:
            headers["x-api-key"] = self.cs2_api_key
        return headers

@lru_cache
def get_settings():
    return Settings()
