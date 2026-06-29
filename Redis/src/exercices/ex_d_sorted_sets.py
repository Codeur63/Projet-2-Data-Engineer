import time
import os
import pandas as pd
from dotenv import load_dotenv 
from src.cache.leaderboard import ProductionLeaderboard


load_dotenv()

# Charger le CSV (adapter le chemin selon votre machine)
df = pd.read_csv(os.getenv("SENSOR_TELEMETRY"))
print("CSV chargé, aperçu des données :")
print(df.head(5))

time.sleep(1)
print(f"Total mesures chargées : {len(df)}")

# Filtrer sur la date 2025-06-15 et les mesures diurnes (solar > 0)
df_day = df[
    (df['solar_output_w'].notna()) &
    (df['solar_output_w'] > 0)
].copy()

print(df_day.head(5))
print(f'Nouvelle données : {len(df_day)}')

lb = ProductionLeaderboard('2025-06-15')

# Ingérer toutes les mesures dans le leaderboard

for _, row in df_day.iterrows():
    lb.add_reading(row['sensor_id'], row['solar_output_w'])
    
print('=== TOP 10 PRODUCTION SOLAIRE ===',)

for i, (sensor, score) in enumerate(lb.get_top_n(10), 1):
    print(f'{i:2}. {sensor} → {score/1000:.2f} kWh ')

print(f'\nInstallations > 1 kWh : {lb.count_above(5000)}')
