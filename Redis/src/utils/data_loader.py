"""Chargeur de données — simule la couche MySQL en chargeant installations.json."""
import json
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv



load_dotenv()
_installations_cache: Optional[Dict] = None

# Cache Python (RAM)
def load_installations(path: str = os.getenv("INSTALLATION_JSON")) -> Dict:
    """Charge installations.json en mémoire Python (une seule fois)."""
    global _installations_cache
    if _installations_cache is None:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Indexer par installation_id pour un accès O(1)
        _installations_cache = {str(inst['installation_id']): inst for inst in
    data}
    return _installations_cache



def get_installation_by_sensor(sensor_id: str) -> Optional[Dict]:
    """
    Simule une requête MySQL : SELECT * FROM installations JOIN sensors...
    sensor_id format : 'CAM-{installation_id}-S1'
    """
    # Extraire l'installation_id depuis le sensor_id
    try:
        inst_id = sensor_id.split('-')[1].lstrip('0') or '0'
    except (IndexError, ValueError):
        return None
    
    installations = load_installations()
    return installations.get(inst_id)