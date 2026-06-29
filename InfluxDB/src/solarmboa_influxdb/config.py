import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()



class Settings(BaseSettings):
    influxdb_url: str = "http://localhost:8086"
    # influxdb_token: str = "solarmboa_influx_token_2026"
    influxdb_token: str = os.getenv("INFLUXDB_TOKEN") 
    influxdb_org: str = "solarmboa"
    influxdb_bucket: str = "iot_telemetry"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()