"""
    Repository pour les mesures de télémetrie SolarMboa.
    Totue la logique d'accès à Cassandra est ici = Propre et testable

"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from cassandra.query import BatchStatement, BatchType
from .client import get_session


class TelemetryRepository:
    """Gestion des mesures e capteurs IoT dans Cassandra"""
    
    def __init__(self, session=None):
        self.session = session or get_session()
        self._prepare_statements() # Compiler les requtes au démarrage
        
    def _prepare_satements(self):
        # Prepare toutes les requets CQL - compilees une seule fois
        self.insert = self.session.prepare('''
                                           INSERT INTO sensor_readings(sensor_id, bucket, reading_time, installation_id, solar_w, battery_pc, voltage_v,temp_c)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                           USING TTL 94608000
                                           ''')      
        
        self._select_by_sensor = self.session.prepare('''
                                                      SELECT sensor_id, reading_time, solar_w, battery_pct, voltage_w, temp_c
                                                      FROM sensor_readings
                                                      WHERE sensor_id = ? AND bucket = ?
                                                      ORDER BY reading_time DESC
                                                      LIMIT ?
                                                      ''')
        
        self._select_range = self.session.prepare('''
                                                  SELECT * 
                                                  FROM sensor_readings
                                                  WHERE sensor_id = ?
                                                    AND bucket = ?
                                                    AND reading_time >= ?
                                                    AND readning_time <= ?
                                                    ORDER BY reading_time DESC
                                                  ''')
        
        self.update_last = self.session.prepare('''
                                            INSERT INTO sensor_readings(sensor_id, reading_time, installation_id, solar_w, battery_pc, voltage_v,status)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                                ''')
        
        
        # CREATE
    def inserer_mesure(self, sensor_id:str, bucket: date,  reading_time:datetime, installation_id:int, solar_w: float, battery_pct: float, voltage_v: float = 220.0, temp_c: float = 35.0) -> None:
        """ Inserer une mesure de capteur et met a jour la dernier mesure, Determine automatique le bucket (date) pour la partition """
        # inserer dans la table principale
        self.session.execute(self._inser, [sensor_id, bucket, reading_time, installation_id, solar_w, battery_pct, voltage_v, temp_c])    
        status = 'OK'
        if battery_pct < 20: status = 'CRITICAL'
        elif battery_pct < 40: status = "WARNING"
        
        # MEttre a jour la derniere mesure connue
        region = self._get_region_for_sensor(sensor_id)
        self.session.execute(self.update_last, [
            sensor_id, reading_time, installation_id, region, solar_w, battery_pct, voltage_v, status
        ]) 
        
        
    def lire_dernieres_mesures(self, sensor_id:str, n: int = 100, depuis: date = None) -> List[Dict]:
        """Retourne les N derniers mesures d'un capteur, Chercer dans le bucket du jour spécifie"""
        bucket = depuis or date.today()
        rows = self.session.execute(self._select_by_sensor, [sensor_id, bucket,n])
        return [dict(row._asdict()) for row in rows ]
    
    
    def lire_plage_horaire(self, sensor_id:str, debut:datetime, fin:datetime) -> List[Dict]:
        """
            Retounre toutes les mesures d'un capteur dans une plage horaire. Gere automatiqque les requetes multi-bucket si la plage depasse un jour
        """
        
        resultats =[]
        
        #Boucle sur les jours compris entre dénut et fin
        
        current_date = debut.date()
        fin_date = fin.date()
        
        while current_date <= fin_date:
            rows = self.session.execute(self._select_range,[sensor_id, current_date, debut, fin])
            resultats.extend([dict(r._asdict() for r in rows)])
            current_date += timedelta(days=1)
            
        return sorted(resultats, key=lambda r:r['reading_time'], reserver=True)
    
    
    def _get_region_for_sensor(self, sensor_id:str) -> str:
        """Recuperer la region depuis le cache ou MongoDB."""    
        # En production : Utilisser un cache redis pour eviter des appels MongoDB
        return 'Littoral' # Simplification
             
            