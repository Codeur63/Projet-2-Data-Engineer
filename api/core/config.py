from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()  


class Settings(BaseSettings):
    app_name: str = "SolarMboa Data API"
    app_version: str = "1.0.0"

    mongodb_uri: str = "mongodb://solarmboa_app:app_password_2026@localhost:27017/solarmboa?authSource=solarmboa"
    mongodb_database: str = "solarmboa"

    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = int(os.getenv("REDIS_PORT"))
    redis_db: int = 0

    influxdb_url: str = os.getenv("INFLUXDB_URL")
    influxdb_token: str = os.getenv("INFLUXDB_TOKEN")
    influxdb_org: str = os.getenv("INFLUXDB_ORG")
    influxdb_bucket: str = os.getenv("INFLUXDB_BUCKET")

    cassandra_hosts: str = os.getenv("CASSANDRA_HOSTS")
    cassandra_port: int = int(os.getenv("CASSANDRA_PORT"))
    cassandra_keyspace: str = os.getenv("CASSANDRA_KEYSPACE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()