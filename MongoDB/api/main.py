"""API REST SolarMboa — connexion MongoDB locale."""

from fastapi import FastAPI, HTTPException, Query, Path
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
from solarmboa.database import get_db, close_connection, verifier_connexion
from pydantic import BaseModel
from solarmboa.services.cache_bridge import (
    get_installation_cached,
    invalidate_installation_cache,
)


class StatusUpdate(BaseModel):
    status:str 
    reason:str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connexion au demarrage, fermeture a l'arret."""
    etat = verifier_connexion()
    if etat["statut"] not in {"connecte", "connecting ... OK"}:
        raise RuntimeError(f"MongoDB local indisponible : {etat}")
    print(f'API demarree — MongoDB {etat["version"]} sur {etat["uri"]}')
    yield 
    close_connection()
    print("API arretee — MongoDB deconnecte")


app = FastAPI(
    title="SolarMboa Data API",
    description="API de gestion des profils d'installation et communication — MongoDB local",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/health", tags=["Systeme"])
async def health_check():
    """Verification de la connexion MongoDB locale."""
    etat = verifier_connexion()
    if etat["statut"] not in {"connecte", "connecting ... OK"}:
        raise HTTPException(status_code=503, detail="MongoDB local indisponible")
    return {
        "api": "ok",
        "mongodb": "connecte (local)",
        "version": etat["version"],
        "uri": etat["uri"],
    }


# ── Endpoint 1 : Trouver une installation par ID ─────────────

@app.get(
    "/api/v1/installations/{installation_id}",
    summary="Profil complet d'une installation",
)

async def get_installation(installation_id: int = Path(gt=0)):
    col = get_db()["installations"]
    doc = get_installation_cached(col, installation_id)
    if not doc:
        raise HTTPException(404, f"Installation {installation_id} introuvable")
    return doc


# ── Endpoint 2 : Liste paginee avec filtres ──────────────────
# /api/v1/installations/?region=Est&status=active&plan=basic&client_type=individual
@app.get("/api/v1/installations/", summary="Recherche paginee avec filtres")
async def list_installations(
    region: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    plan: Optional[str] = Query(None),
    client_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    col = get_db()["installations"]
    filtre = {}
    # if region:
    #     filtre["location.region"] = region
    # if status:
    #     filtre["status"] = status
    # if plan:
    #     filtre["contract.plan"] = plan
    # if client_type:
    #     filtre["client_type"] = client_type
    total = col.count_documents(filtre)
    docs = list(
        col.find(
            filtre,
            {
                "installation_id": 1,
                "client_name": 1,
                "client_type": 1,
                "status": 1,
                "location.region": 1,
                # "location.city": 1,
                # "contract.plan": 1,
                # "contract.monthly_xaf": 1,
                "_id": 0,
            },
        )
        .sort("installation_id", 1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": docs,
    }


# ── Endpoint 3 : Recherche GPS ───────────────────────────────
@app.get("/api/v1/installations/near/gps", summary="Installations dans un rayon GPS")
async def find_near(
    longitude: float = Query(..., ge=8.0, le=16.0),
    latitude: float = Query(..., ge=2.0, le=13.0),
    radius_km: float = Query(20.0, gt=0, le=200),
):
    col = get_db()["installations"]
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "distance_m",
                "maxDistance": radius_km * 1000,
                "spherical": True,
                "query": {"status": {"$in": ["active", "maintenance"]}},
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "status": 1,
                "location.city": 1,
                "location.region": 1,
                "distance_km": {"$round": [{"$divide": ["$distance_m", 1000]}, 2]},
            }
        },
        {"$limit": 50},
    ]
    docs = list(col.aggregate(pipeline))
    return {
        "centre": {"longitude": longitude, "latitude": latitude},
        "radius_km": radius_km,
        "count": len(docs),
        "data": docs,
    }


# ── Endpoint 4 : Mettre a jour le statut ─────────────────────
@app.patch(
    "/api/v1/installations/{installation_id}/status", summary="Mettre a jour le statut"
)
async def update_status(installation_id: int = Path(gt=0), body: dict = None):
    STATUTS = {"active", "suspended", "maintenance", "churned", "pending"}
    new_status = (body or {}).get("status")
    if new_status not in STATUTS:
        raise HTTPException(422, f"Statut invalide : {new_status}")
    col = get_db()["installations"]
    result = col.update_one(
        {"installation_id": installation_id},
        {
            "$set": {"status": new_status, "updated_at": datetime.utcnow()},
            "$push": {
                "status_history": {
                    "status": new_status,
                    "date": datetime.utcnow(),
                    "reason": (body or {}).get("reason", ""),
                }
            },
        },
    )
    invalidate_installation_cache(installation_id)
    if result.matched_count == 0:
        raise HTTPException(404, f"Installation {installation_id} introuvable")
    return {
        "updated": True,
        "installation_id": installation_id,
        "new_status": new_status,
    }

@app.post(
    "api/v1/installations/{installation_id}/maintenance",
    summary="Lister maintenance de l'installation"
    )
async def get_maintenance(installation_id: int = Path(get=0)):
    col = get_db()['installations']
    filtre = {}
    docs = list(
        col.find(
            filtre,
            {
            "installation_id": 1,
                
            },            
        )
    )
    return {
        "data":docs
    }

# ── Endpoint 5 : Ajouter une intervention ────────────────────
# @app.post(
#     "/api/v1/installations/{installation_id}/maintenance",
#     summary="Enregistrer une intervention de maintenance",
# )
# async def add_maintenance(installation_id: int = Path(gt=0), body: dict = None):
#     if not body or "type" not in body:
#         raise HTTPException(422, "type de visite requis")
#     visit = {"date": datetime.utcnow(), **body}
#     col = get_db()["installations"]
#     result = col.update_one(
#         {"installation_id": installation_id},
#         {
#             "$push": {"maintenance_history": {"$each": [visit], "$slice": -50}},
#             "$set": {"updated_at": datetime.utcnow()},
#         },
#     )
#     invalidate_installation_cache(installation_id)
#     if result.matched_count == 0:
#         raise HTTPException(404, f"Installation {installation_id} introuvable")
#     return {"recorded": True, "installation_id": installation_id}
