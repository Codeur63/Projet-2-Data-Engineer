# """ API REST Solarmboa - ingestion de données  """

# from fastapi import FastAPI, HTTPException, Query, Path
# from typing import Optional
# from datetime import datetime
# from solarmboa.database import get_db, close_connection, verifier_connexion
# from solarmboa_influxdb.client import get_influx_client, close_influx_client, verifier_connexion as verifier_connexion_influx
# from solarmboa_graph.client import get_session, close_driver, verify_connection as verify_neo4j_connection 
# from cassandradb.client import get_session as get_cassandra_session, close_connection as close_cassandra_connection, verifier_connection as verify_cassandra_connection

# app = FastAPI(
#     title="SolarMboa Data API",
#     description="API REST d'ingestion et de consultation des données SolarMboa.",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
# )
     
# @app.get("/api/v1/health", tags=["Systeme"])
# async def health_check():
#     #---------------- verification de la connexion MongoDB locale ----------------
#     """ Verification de la connexion aux base de donnees locale"""
#     etat_mongo = verifier_connexion()
#     etat_influx = verifier_connexion_influx()
#     etat_neo4j = verify_neo4j_connection()
#     etat_cassandra = verify_cassandra_connection()
#     if etat_mongo["statut"] not in {"connecte", "connecting ... OK"} and etat_influx["statut"] not in {'connecte', 'ok'} and etat_neo4j["statut"] not in {'ok', 'connecte'} and etat_cassandra["statut"] not in {'ok', 'connecte'}:        
#         raise HTTPException(status_code=503, detail="MongoDB local ou InfluxDB ou Neo4j ou Cassandra indisponible")    
#     return {
#         "api": "ok",
#         "version": "1.0.0",
#         "services":{
#             "mongodb": "connecte (local)",
#             "version": etat_mongo["version"],
#             "uri": etat_mongo["uri"],
#             "influxdb": "connecte",
#             "version_influx": etat_influx.get("version", "N/A"),
#             "neo4j": etat_neo4j["statut"],
#             "version_neo4j": etat_neo4j.get("version", "N/A"),
#             "uri_neo4j": etat_neo4j["uri"],
#             "user": etat_neo4j["user"],
#             "cassandra": etat_cassandra["statut"],
#             "version_cassandra": etat_cassandra.get("version", "N/A")
#         }
#     }
    
# @app.post("/api/v1/installations", summary="Ajoutez un profil d'installation")
# async def add_installation(body: dict):
#     if not body or "installation_id" not in body:
#         raise HTTPException(422, "installation_id requis")
#     col = get_db()["installations"]
#     result = col.insert_one({**body, "created_at": datetime.utcnow()})
#     return {"inserted_id": str(result.inserted_id)}    

     
# @app.get("/api/v1/installations/{installation_id}", summary="Récupérez un profil d'installation par ID")
# def get_installation(installation_id:int = Path(..., description="ID de l'installation")):
#     col = get_db()["installations"]
#     installation = col.find_one({"installation_id": installation_id})
#     if not installation:
#         raise HTTPException(404, "Installation non trouvée")  
#     return InstallationResponse.from_mongo(installation)
 
 
# @app.get("/api/v1/telemetry", summary="Récupérez les données de télémétrie pour une installation")
# def get_telemetry(installation_id:int = Query(..., description="ID de l'installation"), start_time: Optional[datetime] = Query(None, description="Heure de début (format ISO)"), end_time: Optional[datetime] = Query(None, description="Heure de fin (format ISO)")):
#     col = get_db()["telemetry"]
#     query = {"installation_id": installation_id}
#     if start_time:
#         query["timestamp"] = {"$gte": start_time}
#     if end_time:
#         query.setdefault("timestamp", {})["$lte"] = end_time
#     telemetry_data = list(col.find(query).sort("timestamp", 1))
#     return [TelemetryResponse.from_mongo(data) for data in telemetry_data]


from fastapi import FastAPI
from api.core.config import settings
from api.routes.health import router as health_router
from api.routes.installations import router as installations_router
from api.routes.telemetry import router as telemetry_router
from api.routes.installations import router as installations_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST d'ingestion et de consultation des données SolarMboa.",
)

app.include_router(health_router)
app.include_router(installations_router)
app.include_router(telemetry_router)
app.include_router(installations_router)

@app.get("/")
def root():
    return {
        "message": "SolarMboa Data API",
        "docs": "/docs",
        "health": "/health",
    }