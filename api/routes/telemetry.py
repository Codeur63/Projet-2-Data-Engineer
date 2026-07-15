from fastapi import APIRouter, HTTPException

from api.schemas.telemetry import TelemetryIn, TelemetryBatchIn
from api.services.influx_service import influx_service
from api.services.cassandra_service import cassandra_service
from api.services.redis_service import redis_service
from api.services.mongo_service import mongo_service

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["Telemetry"],
)


def ingest_one(payload: TelemetryIn) -> dict:
    data = payload.model_dump()

    installation = mongo_service.get_installation(data["installation_id"])

    if installation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Installation {data['installation_id']} introuvable dans MongoDB",
        )

    influx_service.write_telemetry(data)
    cassandra_service.write_telemetry(data)
    redis_service.set_latest_telemetry(data["installation_id"], data)

    return {
        "installation_id": data["installation_id"],
        "sensor_id": data["sensor_id"],
        "written_to": ["influxdb", "cassandra", "redis"],
    }


@router.post("")
def ingest_telemetry(payload: TelemetryIn):
    try:
        
        result = ingest_one(payload)

        return {
            "status": "success",
            "message": "Télémétrie ingérée",
            "data": result,
        }
    except:
        return {
            "status": "False",
            "message": "Ingestion échoué"
        }   


@router.post("/batch")
def ingest_telemetry_batch(payload: TelemetryBatchIn):
    results = []

    for item in payload.items:
        results.append(ingest_one(item))

    return {
        "status": "success",
        "message": f"{len(results)} mesures ingérées",
        "data": results,
    }


@router.get("/latest/{installation_id}")
def get_latest_telemetry(installation_id: int):
    latest = redis_service.get_latest_telemetry(installation_id)

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune télémétrie récente pour installation {installation_id}",
        )

    return {
        "status": "success",
        "source": "redis",
        "data": latest,
    }

@router.get("/{installation_id}")
def get_telemetry(installation_id:int):
    telemetry = cassandra_service.get_telemetry(installation_id)
    
    return {
        "status": "success",
        "source": "Cassandra",
        "data": telemetry
    } 