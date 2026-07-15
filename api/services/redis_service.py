import json
from typing import Optional, Dict, Any

import redis

from api.core.config import settings


class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )

    def ping(self) -> bool:
        return bool(self.client.ping())

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int = 300) -> None:
        self.client.setex(
            key,
            ttl_seconds,
            json.dumps(value, ensure_ascii=False, default=str),
        )

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self.client.get(key)

        if raw is None:
            return None

        return json.loads(raw)

    def delete(self, installation_id :int) -> None:
        self.client.delete(f"mongo:installation:{installation_id}")

    def cache_installation(self, installation_id: int, installation: Dict[str, Any]) -> None:
        self.set_json(
            key=f"mongo:installation:{installation_id}",
            value=installation,
            ttl_seconds=600,
        )

    def get_cached_installation(self, installation_id: int) -> Optional[Dict[str, Any]]:
        return self.get_json(f"mongo:installation:{installation_id}")

    def invalidate_installation(self, installation_id: int) -> None:
        self.delete(f"mongo:installation:{installation_id}")

    def set_latest_telemetry(self, installation_id: int, telemetry: Dict[str, Any]) -> None:
        self.set_json(
            key=f"telemetry:latest:{installation_id}",
            value=telemetry,
            ttl_seconds=900,
        )

    def get_latest_telemetry(self, installation_id: int) -> Optional[Dict[str, Any]]:
        return self.get_json(f"telemetry:latest:{installation_id}")


redis_service = RedisService()