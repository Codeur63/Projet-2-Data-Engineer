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
        
def verifier_connexion():
    """
    Verifie la connexion a InfluxDB.
    Retourne un dictionnaire avec le statut et la version.
    """
    try:
        client = get_influx_client()
        if client.ping():
            version = client.version()
            return {"statut": "connecte", "version": version}
        else:
            return {"statut": "non connecte", "version": None}
    except Exception as e:
        return {"statut": f"erreur: {str(e)}", "version": None}        