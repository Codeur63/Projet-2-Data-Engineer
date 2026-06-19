"""
Client MongoDB singleton = installation locale.
Connexion simple avec authentification pour le developpement
"""

import logging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
from .config import settings

logger = logging.getLogger(__name__)
_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """
    Retourne le client MongoDb singleton.
    Se connecte a MongoDB local (localhost:27017)
    """

    global _client
    if _client is None:
        _client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMs=3000,
            connectTimeoutMs=2000,
            socketTimeoutMs=10000,
            maxPoolSize=20,
            minPoolSize=2,
        )

        # Tester la connexion immediatement
        try:
            _client.admin.command("ping")
            logger.info(f"Connecte a MongoDB local - {settings.mongodb_uri}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(
                f"Impossible de se connecter a MongoDB.\n"
                f"------------------------------------------------------\n"
                f"---{e.__class__.__name__}---\n"
                f"URI : {settings.mongodb_uri}\n"
                f"Verifiez que MongoDB est demarre (mongod) .... \n"
                f"------------------------------------------------------\n\n\n"
            )
            raise
    return _client


def get_db(name: str = None) -> Database:
    """
    Retroune la base de donnees solarmboa.
    Par defaut, utilise le nom de base configure dans settings.mongodb_database
    """
    db_name = name or settings.mongodb_database

    try:
        logger.info(f"Acces a la base de donnees : {db_name}")
        print(f"Acces a la base de donnees : {db_name}")
    except Exception:
        logger.warning(f"Base de donnees non trouvee : {db_name}")
        print(f"Base de donnees non trouvee : {db_name}")
    return get_client()[db_name]


def close_connection():
    global _client

    if _client is not None:
        _client.close()
        _client = None
        logger.info("Connexion MongoDB ferme")


def verifier_connexion() -> dict:
    """
    Verifie et retourne l'etat de la connexion MongoDB locale.
    Utile pour le debug et les test de demrrage
    """
    try:
        client = get_client()
        info = client.server_info()
        return {
            "statut": "connecting ... OK",
            "version": info.get("version", "?"),
            "uri": settings.mongodb_uri,
            "base": settings.mongodb_database,
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e)}
