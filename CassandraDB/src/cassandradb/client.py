"""
Client Cassandra singleton avec gestion de connexion robuste.
Pattern Singleton : une seule connexion partagée dans toute l'application.
"""

import os 
import logging 
import time
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy, RetryPolicy
from cassandra.auth import PlainTextAuthProvider
from typing import Optional


logger = logging.getLogger(__name__)   

_cluster: Optional[Cluster]=None
_session = None


def get_session():
    """
        Retroune la sessions Cassandra singleton.
        Crée si elle n'existe pas, sinon retourne l'instance existante.
    """
    
    global _cluster, _session
    if _session is None:
        hosts = os.getenv('CASSANDRA_HOSTS', 'localhost').split(',')
        keyspace = os.getenv('CASSANDRA_KEYSPACE', 'solarmboa')
        dc = os.getenv("CASSANDRA_DC", "datacenter1")
        
        _cluster = Cluster(
            hosts,
            port = int(os.getenv('CASSANDRA_PORT', 9042)),
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=dc),
            default_retry_policy=RetryPolicy(),
            connect_timeout=10,
            protocol_version=4            
            )
        
        _session = _cluster.connect(keyspace)
        logger.info( f"Connected to Cassandra cluster at {hosts} with keyspace '{keyspace}'")
        print( f"Connected to Cassandra cluster at {hosts} with keyspace '{keyspace}'")
        
    return _session

def close_connection():
    """
        Ferme la connexion Cassandra proprement.
    """
    global _cluster, _session
    if _session:
        _session.shutdown()
        logger.info("Cassandra session shutdown.")
        print("Cassandra cluster shutdown.")
        _session = None
    if _cluster:
        _cluster.shutdown()
        logger.info("Cassandra cluster shutdown.")
        print("Cassandra cluster shutdown.")
        _cluster = None


def verifier_connection():
    """
        Vérifie la connexion à Cassandra.
        Retourne un dictionnaire avec le statut et les détails.
    """
    try:
        session = get_session()
        # Exécuter une requête simple pour tester la connexion
        session.execute("SELECT release_version FROM system.local")
        return {"statut": "connecte", 
                "version": session.execute("SELECT release_version FROM system.local").one()[0]
                }
    except Exception as e:
        logger.error(f"Erreur de connexion à Cassandra : {e}")
        return {"statut": "erreur", "message": str(e)}
    
    

if __name__ == '__main__':
    print('=='*40)
    print('\n Test de connection a cassandra\n')
    time.sleep(3)
    try:
        conn = get_session()
        print("Connexion: ", conn)
    except Exception as e:  
        print(f"Vous avez une erreur de Connexion a CassandraDB :{e}")  
        