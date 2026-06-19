"""
Bridge MongoDB <-> Redis.

Rôle :
- Lire d'abord Redis
- Si MISS, lire MongoDB
- Mettre le résultat MongoDB en cache Redis
"""

import json
import os
import time
from typing import Optional

import redis
from pymongo.collection import Collection

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_TTL = int(os.getenv("INSTALLATION_CACHE_TTL", 300))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def cache_key_installation(installation_id: int) -> str:
    return f"mongo:installation:{installation_id}"


def get_installation_cached(
    col: Collection,
    installation_id: int,
) -> Optional[dict]:
    key = cache_key_installation(installation_id)

    start = time.perf_counter()

    cached = redis_client.get(key)

    if cached:
        elapsed_ms = (time.perf_counter() - start) * 1000
        doc = json.loads(cached)
        doc["_cache"] = {
            "status": "HIT",
            "source": "redis",
            "latency_ms": round(elapsed_ms, 3),
        }
        return doc

    doc = col.find_one({"installation_id": installation_id}, {"_id": 0})

    if not doc:
        return None

    redis_client.setex(key, CACHE_TTL, json.dumps(doc, default=str))

    elapsed_ms = (time.perf_counter() - start) * 1000
    doc["_cache"] = {
        "status": "MISS",
        "source": "mongodb",
        "latency_ms": round(elapsed_ms, 3),
        "cached_key": key,
        "ttl_seconds": CACHE_TTL,
    }

    return doc


def invalidate_installation_cache(installation_id: int) -> int:
    key = cache_key_installation(installation_id)
    return redis_client.delete(key)