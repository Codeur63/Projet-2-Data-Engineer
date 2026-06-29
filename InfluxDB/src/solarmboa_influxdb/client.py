from influxdb_client import InfluxDBClient
from .config import settings


_client = None


def get_influx_client() -> InfluxDBClient:
    global _client

    if _client is None:
        _client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
            timeout=60_000
        )

    return _client


def ping() -> bool:
    return get_influx_client().ping()


def close_influx_client():
    global _client

    if _client is not None:
        _client.close()
        _client = None