"""
    Client Redis sigleton avec pool de connexions.
    Pattern : Instance unique partagées par toute l'application.
"""

import os 
import sys
import redis
import logging
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_pool: Optional[redis.ConnectionPool] = None
_client: Optional[redis.Redis] = None

def get_redis_pool() -> redis.Redis:
    
    global _pool, _client 
    
    if _pool is None:
        get_redis_client()
        
    return _pool,_client    

def get_redis_client() -> redis.Redis:
    """
        Retourne le client Redis singleton.
        rée le pool et le client uniquement au premier appel (lazy init).
        Tous les appels suivants retournent la meme instance.
    """ 
    
    global _pool, _client
    
    if _client is None:
        try:
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", 6379))
            
            logger.info(f"Initialisation du pool Redis sur {host}:{port}")
            
            # Créer le pool de connexions Redis
            _pool = redis.ConnectionPool(
                host=host,
                port=port,
                db=int(os.getenv("REDIS_DB", 0)),
                password=os.getenv("REDIS_PASSWORD", None),
                max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 20)),
                decode_responses=True,  # Pour obtenir des chaînes de caractères au lieu de bytes
                socket_connect_timeout=2,  # Timeout de connexion en secondes
                socket_timeout=1,  # Timeout de connexion en secondes
                retry_on_timeout=True  # Réessayer en cas de timeout
            )        
            
            # Créer le client Redis en utilisant le pool
            _client = redis.Redis(connection_pool=_pool)
        except KeyError as e:
            logger.exception(f"Erreur lors de la création du client Redis. : {e}")
            raise    # Propagation de l'erreur
        
    return _client  


def close_redis_client():
    # Docstring: Ferme le pool de connexions Redis et réinitialise les variables globales
    global _pool, _client
    
    if _pool is not None:
        _pool.disconnect()
        _client = None
        _pool = None
        logger.info("Pool de connexions Redis fermé.")
        

def test_connection() -> bool:
    """
        Teste la connexion à Redis en envoyant une commande PING.
        Retourne True si la connexion est réussie, sinon False.
    """
    try:
        client = get_redis_client()
        return client.ping()
    except redis.RedisError as e:
        logging.error(f"Erreur de connexion à Redis: {e}")
        return False
 
 
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "close":
        # On initialise le client juste pour pouvoir le fermer (test de sécurité)
        get_redis_client() 
        close_redis_client()
        print("Opération de fermeture demandée et exécutée.")
        
    else:            
        if test_connection():
            print("✅ Connexion à Redis réussie !")
            r = get_redis_client()
            r.set("test_key", "Hello Redis")
            print(f"Donnée récupérée : {r.get('test_key')}")
            logging.info("Connexion à Redis réussie !")
        else:
            logging.error("Échec de la connexion à Redis.") 
