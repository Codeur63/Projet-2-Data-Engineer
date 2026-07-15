from fastapi import APIRouter, HTTPException

from api.schemas.installation import InstallationCreate, InstallationStatusUpdate
from api.services.mongo_service import mongo_service
from api.services.redis_service import redis_service

router = APIRouter(
    prefix="/api/v1/installations",
    tags=["Installations"],
)


@router.post("")
def create_installation(payload: InstallationCreate):
    data = payload.model_dump()

    result = mongo_service.create_installation(data)

    redis_service.cache_installation(
        installation_id=data["installation_id"],
        installation=result["installation"],
    )

    return {
        "status": "success",
        "created": result["created"],
        "data": result["installation"],
    }

@router.delete("/{installation_id}")
def delete_installation(installation_id: int):
    delete = redis_service.delete(installation_id)
    suppr = mongo_service.delete_installation(installation_id)
    
    if suppr:
        return {
            "source": "mongoDB",
            "delete": "True" 
        }
    
    print(suppr)    
    


@router.get("/{installation_id}")
def get_installation(installation_id: int):
    cached = redis_service.get_cached_installation(installation_id)

    if cached is not None:
        return {
            "status": "success",
            "source": "redis",
            "data": cached,
        }

    installation = mongo_service.get_installation(installation_id)

    if installation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Installation {installation_id} introuvable",
        )

    redis_service.cache_installation(installation_id, installation)

    return {
        "status": "success",
        "source": "mongodb",
        "data": installation,
    }


@router.patch("/{installation_id}/status")
def update_installation_status(
    installation_id: int,
    payload: InstallationStatusUpdate,
):
    updated = mongo_service.update_status(
        installation_id=installation_id,
        status=payload.status,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Installation {installation_id} introuvable",
        )

    redis_service.invalidate_installation(installation_id)

    return {
        "status": "success",
        "message": "Statut mis à jour",
        "data": updated,
    }

@router.post("/{installation_id}/maintenance")
def add_maintenance_to_installation(
    installation_id: int,
    payload: MaintenanceCreate,
):
    maintenance_data = payload.model_dump()

    updated_installation = mongo_service.add_maintenance(
        installation_id=installation_id,
        maintenance_payload=maintenance_data,
    )

    if updated_installation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Installation {installation_id} introuvable",
        )

    redis_service.invalidate_installation(installation_id)

    return {
        "status": "success",
        "message": "Intervention de maintenance ajoutée",
        "data": updated_installation,
    }