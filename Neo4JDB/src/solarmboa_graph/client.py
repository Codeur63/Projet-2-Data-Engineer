from neo4j import GraphDatabase
from .config import settings

_driver = None


def get_driver():
    global _driver

    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    return _driver


def get_session():
    return get_driver().session(
        database=settings.neo4j_database
    )
    

def verify_connection() -> dict:
    
    try:
        driver = get_driver()
        driver.verify_connectivity()
        
        return {
            "statut": "connecte",
            "uri": settings.neo4j_uri,
            "user": settings.neo4j_user,
            "version": "N/A (Driver OK)"
        }
        
    except Exception as e:
        return {
            "statut": "error",
            "message": str(e),
            "uri": settings.neo4j_uri,
            "user": settings.neo4j_user,
            "version": "inconnue"
        }


def close_driver():    
    global _driver

    if _driver is not None:
        _driver.close()
        _driver = None