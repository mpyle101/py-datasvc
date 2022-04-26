from typing import Mapping
from pydantic import BaseSettings

class Settings(BaseSettings):
    API_V1_PREFIX: str   = "/api/v1"
    PROJECT_NAME: str    = "Alteryx Data Catalog"
    DATAHUB_INGEST: str  = "http://localhost:8080/entities?action=ingest"
    DATAHUB_GRAPHQL: str = "http://localhost:8080/api/graphql"
    DATAHUB_HEADERS: Mapping[str, str] = {
        "X-DataHub-Actor": "urn:li:corpuser:datahub",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip"
    }

    class Config:
        env_file = ".env"

settings = Settings()