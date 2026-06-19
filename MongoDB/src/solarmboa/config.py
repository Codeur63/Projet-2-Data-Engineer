"""
Configuration de l'application SolarMboa.
Connexion a MongoDB local
"""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    mongodb_uri: str = os.getenv("MONGO_URI")
    mongodb_database: str = "solarmboa"
    mongodb_test_db: str = "solarmboa_test"
    mongodb_auth_user: str = "authSource=admin"  # a completer si besoin
    mongodb_auth_pass: str = "app_password_2026"  # a completer si besoin

    mongo_uri_replica: str | None = None
    mongo_db: str | None = None
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  
    )


settings = Settings()
