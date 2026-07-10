"""
    Repository pour les mesures de télémetrie SolarMboa.
    Totue la logique d'accès à Cassandra est ici = Propre et testable

"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from cassandra.query import BatchStatement, BatchType
from cassandradb.client import get_session


class TelemetryRepository:
    """Gestion des mesures de capteurs IoT dans Cassandra"""
    
    def __init__(self, session=None):
        self.session = session or get_session()
        self._region_cache = {}
        self._prepare_statements() # Compiler les requtes au démarrage
        
    def _prepare_statements(self):
        # Prepare toutes les requets CQL - compilees une seule fois
        self.insert = self.session.prepare('''
                                           INSERT INTO sensor_readings (
                                               sensor_id, bucket, timestamp, region, solar_output_w, battery_level_pct, consumption_w, installation_id, alert_code, signal_rssi, temp_c 
                                               
                                           )
                                           VALUES (?,?,?,?,?,?,?,?,?,?,?)
                                           USING TTL 94608000
                                           ''')      

        
        self._select_by_sensor = self.session.prepare('''
                                                      SELECT sensor_id, timestamp, solar_output_w, battery_level_pct, consumption_w, bucket
                                                      FROM sensor_readings_by_day
                                                      WHERE sensor_id = ? AND bucket = ?
                                                      ORDER BY timestamp DESC
                                                      LIMIT ?
                                                      ''')
        
        self._select_range = self.session.prepare('''
                                                  SELECT * 
                                                FROM sensor_readings
                                                WHERE sensor_id = ? AND bucket = ? AND timestamp >= ? AND timestamp <= ?
                                                ORDER BY timestamp DESC
                                                  ''')
        
        self._select_sensor_region = self.session.prepare('''
            SELECT region FROM sensors_registry WHERE sensor_id = ?
        ''')
        
        self.insert_sensor_region = self.session.prepare('''
                                                         INSERT INTO sensors_registry(sensor_id,region)
                                                         VALUES(?,?) 
                                                         ''')
        
        self._select_last_sensor = self.session.prepare('''
                                                        SELECT region, sensor_id, battery_level_pct, solar_output_w FROM sensor_last_reading WHERE sensor_id = ?
                                                        ''') 
        
        
        self.insert_alert = self.session.prepare('''
                                                 INSERT INTO sensor_alerts(sensor_id, bucket, timestamp,region,solar_output_w,alert_type,installation_id,severity,value,acknowledged)
                                                 VALUES (?,?,?,?,?,?,?,?,?,?)
                                                 ''')
        
        self.update_last = self.session.prepare('''
                                            INSERT INTO sensor_last_reading(sensor_id, timestamp, installation_id, region, solar_output_w, battery_level_pct, consumption_w, alert_code, status)
                                           VALUES (?,?,?,?,?,?,?,?,?)
                                                ''')  
        
        self.insert_daily_stats = self.session.prepare('''
                                                       INSERT INTO daily_stats (installation_id,start_date,sensor_id,avg_solar_w,max_battery_pct,max_solar_w, min_battery_pct, timestamp, total_kwh)   
                                                       VALUES (?,?,?,?,?,?,?,?,?)                                                    
                                                       ''')      
      
        self._select_region = self.session.prepare(
            '''
            SELECT * FROM sensor_readings_by_region where region=? and bucket=? ORDER BY bucket DESC limit=?
            '''
        )
      
    def compute_status(self, battery_level_pct: float) -> str:
        if battery_level_pct > 50:
            return "OK"
        elif battery_level_pct < 40:
            return "WARNING"        
        elif battery_level_pct < 20:
            return "CRITICAL"
        elif battery_level_pct <= 0:
            return "OFFLINE"
        return "UNKNOWN"
    
    
        # CREATE
    def inserer_mesure(self, sensor_id:str, timestamp:datetime,   installation_id:int, 
                       solar_output_w: float, battery_level_pct: float, consumption_w: float, 
                       alert_code: str, region: str, signal_rssi: int=20, temp_c: float=30,  ) -> None:
        """ Inserer une mesure de capteur et met à jour la dernière mesure. """
        bucket = timestamp.date()
        start_date = timestamp.date()
        
        # 1. Inserer dans la table principale (Les noms des variables DOIVENT être identiques aux noms dans le `VALUES (?)`) 
        self.session.execute(self.insert, [sensor_id, bucket, timestamp, region, solar_output_w, battery_level_pct, consumption_w, installation_id, alert_code, signal_rssi, temp_c])    
        
        
        
        # 2. Calcul du statut métier
        status = self.compute_status(battery_level_pct)
        severity = self.compute_status(battery_level_pct)
        
        if alert_code:
            self.session.execute(
                self.insert_alert,
                (
                    sensor_id, bucket, timestamp,region,solar_output_w,alert_code,installation_id,severity,battery_level_pct,False
                ),
            )
                
        # 3. Mettre à jour le cache
        self.session.execute(self.update_last, [
           sensor_id, timestamp, installation_id, region, solar_output_w, battery_level_pct, consumption_w, alert_code,status
        ]) 
        
        # 4. Sensore Id
        self.session.execute(self.insert_sensor_region, [sensor_id,region])
        
        min_battery_pct = 0
        total_kwh = consumption_w
        max_solar_w = solar_output_w
        avg_solar_w = solar_output_w
        max_battery_pct = battery_level_pct
        
        # Mettre dans le daily_stats capteur de la journée
        if timestamp:
            self.session.execute(
                self.insert_daily_stats,
                 [installation_id,start_date,sensor_id,avg_solar_w,max_battery_pct,max_solar_w, min_battery_pct, timestamp, total_kwh]
            ) 
            

    
    def lire_dernieres_mesures(self, sensor_id:str, n: int = 100, depuis: date = None) -> List[Dict]:
        """Retourne les N derniers mesures d'un capteur."""
        bucket = depuis or date.today()        
        rows = self.session.execute(self._select_by_sensor, [sensor_id, bucket, n])
        return [dict(row._asdict()) for row in rows ]
    
    def last_measure(self, sensor_id:str) -> List[Dict]:
        rows = self.session.execute(self._select_last_sensor, [sensor_id])
        return [dict(row._asdict())for row in rows] 
    
    def lire_plage_horaire(self, sensor_id: str, debut: datetime, fin: datetime) -> List[Dict]:
        """
            Retourne toutes les mesures d'un capteur dans une plage horaire. Gère automatiquement les requêtes multi-bucket si la plage dépasse un jour
        """
        resultats = []
        region = self._get_region_for_sensor(sensor_id) 
        
        current_date = debut.date()
        fin_date = fin.date()
        
        while current_date <= fin_date:
            start_dt = datetime.combine(current_date, datetime.min.time())
            end_dt = datetime.combine(current_date, datetime.max.time()) 
             
            rows = self.session.execute(self._select_range, [sensor_id, current_date, start_dt, end_dt])
                        
            resultats.extend([dict(r._asdict()) for r in rows])
            current_date += timedelta(days=1)
            
        # 3. CORRECTION : Remplacement de 'reserve=True' par 'reverse=True'
        return sorted(resultats, key=lambda r: r['timestamp'], reverse=True)

    

    
    def _get_region_for_sensor(self, sensor_id: str) -> str:
        """
        Récupère la région depuis le cache en mémoire ou depuis la table Cassandra sensors_registry.
        """
        # 1. Vérification dans le cache en mémoire (instantané)
        if sensor_id in self._region_cache:
            return self._region_cache[sensor_id]
            
        # 2. Si pas dans le cache, on interroge la table de référence Cassandra
        try:
            row = self.session.execute(self._select_sensor_region, [sensor_id]).one()
            if row and row.region:
                region = row.region
                self._region_cache[sensor_id] = region # Mise en cache
                return region
        except Exception as e:
            print(f"Erreur lors de la récupération de la région pour {sensor_id}: {e}")
                
        # 3. Valeur de secours (Fallback) si le capteur n'est pas encore enregistré
        valeur_par_defaut = 'Littoral'
        self._region_cache[sensor_id] = valeur_par_defaut
        return valeur_par_defaut
             
    