"""
Leaderboard de production solaire — Sorted Set Redis.
Chaque installation est un élément du Sorted Set,
son score est la production cumulée en kWh.
"""
import os
import time
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from src.cache.client import get_redis_client

load_dotenv()

class ProductionLeaderboard:
    
    def __init__(self, date: str):
        self.r = get_redis_client()
        self.key = f'leaderboard:prod:{date}'


    def add_reading(self, sensor_id: str, solar_output_w: float) -> None:
        """
        Ajoute la production d'une mesure IoT au classement.
        Formule : puissance (W) × durée (30s) / 3600 = Wh
        ZINCRBY incrémente le score atomiquement.
        """
        wh = (solar_output_w * 30) / 3600 # Wh sur 30 secondes
        self.r.zincrby(self.key, wh, sensor_id)
        self.r.expire(self.key, os.getenv("LEADERBOARD_TTL"))
        
    def get_top_n(self, n: int = 10) -> List[Tuple[str, float]]:
        """Retourne les N meilleures installations (décroissant). O(log N)."""
        # ZREVRANGE = tri décroissant (du meilleur au moins bon)
        return self.r.zrevrange(self.key, 0, n - 1, withscores=True)
    
    def get_rank(self, sensor_id: str) -> Optional[int]:
        """Rang d'une installation (0 = meilleur). O(log N)."""
        return self.r.zrevrank(self.key, sensor_id)
    
    def get_score(self, sensor_id: str) -> float:
        """Production totale en Wh pour une installation."""
        score = self.r.zscore(self.key, sensor_id)
        return float(score) if score else 0.0
    
    def count_above(self, min_wh: float) -> int:
        """Combien d'installations ont produit plus de min_wh ? O(log N)."""
        return self.r.zcount(self.key, min_wh, '+inf')
    
# ── Script de test ──
if __name__ == '__main__':
    print("\n--- Simulation d'un boost de production pour CAM-0001 ---")
    time.sleep(2)
    lb = ProductionLeaderboard('2025-06-15')
    # Simuler des mesures
    lb.add_reading('CAM-0042', 450.0) # 450W × 30s = 3.75 Wh
    lb.add_reading('CAM-0001', 380.0)
    lb.add_reading('CAM-0099', 520.0)
    lb.add_reading('CAM-0042', 460.0)  # 2ème mesure de CAM-0042
    lb.add_reading('CAM-0001', 2000.0) 
    print('Top 3 :')
    print("Research ...") 
    time.sleep(1)
    for sensor, score in lb.get_top_n(3):
        print(f' {sensor} : {score:.2f} Wh')
        print(f'Rank of {sensor} : {lb.get_rank(sensor)}')
    
    print("\n--- Après un boost de production pour CAM-0001 ---")
    time.sleep(2)
    a = lb.add_reading('CAM-0201', 500.0) 
    print(a)
    b = lb.get_rank('CAM-0042')
    print( f'rank : {b}') 
    print("-------------- Count Above ------------" )
    time.sleep(1)
    lb.count_above(5)
    print(f'Rang CAM-0042 : {lb.get_rank("CAM-0042")}')   
    print('\n Leaderboard ---- \n') 
    print(lb)