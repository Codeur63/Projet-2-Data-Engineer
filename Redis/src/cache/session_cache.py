"""
Cache des sessions de capteurs IoT — Hash Redis.
Pattern : Cache-Aside (lecture prioritaire depuis Redis,
fallback MySQL/JSON en cas de MISS).
"""
import os, time, logging
from dataclasses import dataclass
from typing import Optional
from src.cache.client import get_redis_client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
SESSION_TTL = int(os.getenv('SESSION_TTL', 300))

@dataclass
class SensorSession:
    sensor_id: str
    installation_id: int
    region: str 
    city: str
    tariff_plan: str
    status: str
    panel_capacity: int
    battery_capacity: int
    alert_threshold: float
    firmware_ver: str
    last_seen: str = '0'

    def is_active(self) -> bool:
        return self.status == 'active'

    def redis_key(self) -> str:
        # Convention de nommage : domaine:entité:id
        return f"session:sensor:{self.sensor_id}"
    
    
class SessionCache:
    """Gestionnaire du cache des sessions capteurs."""
    
    def __init__(self):
        self.r = get_redis_client()
        self.ttl = SESSION_TTL
        self.prefix = "session:sensor"
    
    def _get_key(self, sensor_id: str, TTL:int=300) -> str:
        """Génère la clé de manière unique pour toute la classe."""
        return f"{self.prefix}:{sensor_id}"     
        
    def set_session(self, s: SensorSession) -> None:        
        """Stocke ou met à jour une session. O(N) où N = nb de champs."""
        key = self._get_key(s.sensor_id)
        data = {
            'installation_id': s.installation_id,
            'region':    s.region,
            'city':  s.city,
            'tariff_plan':   s.tariff_plan,
            'status':  s.status,
            'panel_capacity': s.panel_capacity,
            'battery_capacity':s.battery_capacity,
            'alert_threshold': s.alert_threshold,
            'firmware_ver':  s.firmware_ver,
            'last_seen':  time.time()
            }
        pipe = self.r.pipeline() # 1 round-trip pour HSET + EXPIRE
        pipe.hset(key, mapping=data)
        pipe.expire(key, self.ttl)
        pipe.execute()
        logger.debug(f'Session stored: {key}')
        
        
    def get_session(self, sensor_id: str) -> Optional[SensorSession]:
        """Récupère une session. Retourne None si MISS."""
        key = f'session:sensor:{sensor_id}'
        data = self.r.hgetall(key) # Retourne {} si clé absente
        if not data:
            logger.debug(f'MISS: {key}')
            return None
        logger.debug(f'HIT: {key}')
        return SensorSession(
            sensor_id=sensor_id,
            installation_id=int(data.get('installation_id') or 0),
            region=str(data.get('region') or ''),
            city=str(data.get('city') or ''),
            tariff_plan=str(data.get('tariff_plan') or ''),
            status=str(data.get('status') or ''),
            panel_capacity=int(data.get('panel_capacity') or 0),
            battery_capacity=int(data.get('battery_capacity') or 0),
            alert_threshold=float(data.get('alert_threshold') or 0.0),
            firmware_ver=str(data.get('firmware_ver') or ''),
            last_seen=str(data.get('last_seen', 0)),
        )
        
    def update_status(self, sensor_id: str, status: str) -> None:
        """Met à jour un seul champ sans toucher aux autres. O(1)."""
        # Avantage Hash vs String JSON : mise à jour partielle possible
        self.r.hset(f'session:sensor:{sensor_id}', 'status', status)
        print(f"✅ Status du Capteur {sensor_id} mis à jour dans Redis.")
        
    def refresh_ttl(self, sensor_id: str) -> bool:
        """Renouvelle le TTL (keepalive). Retourne False si clé expirée."""
        result = self.r.expire(f'session:sensor:{sensor_id}', SESSION_TTL)
        return bool(result) # 1=clé existait, 0=clé absente
    
    def delete(self, sensor_id: str) -> None:
        self.r.delete(f'session:sensor:{sensor_id}')    

