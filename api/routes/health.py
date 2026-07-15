from fastapi import APIRouter

from api.core.config import settings
from api.services.redis_service import redis_service
from api.services.cassandra_service import cassandra_service
from api.services.influx_service import influx_service
from api.services.mongo_service import mongo_service 

from solarmboa.database import get_db, close_connection, verifier_connexion
from solarmboa_influxdb.client import get_influx_client, close_influx_client, verifier_connexion as verifier_connexion_influx
from solarmboa_graph.client import get_session, close_driver, verify_connection as verify_neo4j_connection 
from cassandradb.client import get_session as get_cassandra_session, close_connection as close_cassandra_connection, verifier_connection as verify_cassandra_connection



router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    #---------------- verification de la connexion MongoDB locale ----------------
    """ Verification de la connexion aux base de donnees locale"""
    etat_mongo = verifier_connexion()
    etat_influx = verifier_connexion_influx()
    etat_neo4j = verify_neo4j_connection()
    etat_cassandra = verify_cassandra_connection()
    redis_ok = redis_service.ping()
    if etat_mongo["statut"] not in {"connecte", "connecting ... OK"} and etat_influx["statut"] not in {'connecte', 'ok'} and etat_neo4j["statut"] not in {'ok', 'connecte'} and etat_cassandra["statut"] not in {'ok', 'connecte'} :        
        raise HTTPException(status_code=503, detail="MongoDB local ou InfluxDB ou Neo4j ou Cassandra indisponible")    
    return {
        "api": "ok",
        "version": "1.0.0",
        "services":{
            "mongodb": "connecte ",
            "Redis" : redis_ok, 
            "influxdb": "connecte",
            "neo4j": etat_neo4j["statut"],
            "cassandra": etat_cassandra["statut"]
        }
    }
   
