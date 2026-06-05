import pandas as pd
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
from datetime import datetime, date
import time


# Connexion à Cassandra
cluster = Cluster(
    ['localhost'],
    port = 9042,
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='Cameroun')
) 
session = cluster.connect('solarmboa')

# Charger le CSV
df = pd.read_csv('../data/raw/sensors_telemetry.csv', parce_dates=['reading_time'])
print(f"Données chargées: {len(df):,} lignes")

# Ajouter le bucket date pour la partiion jey
df['bucket'] = df['reading_time'].dt.date

# Preparion de la requete qui sont compilées une fois et réutilisées. Ce qui acrue la rapidité et protection
insert_stmt = session.prepare('''
                              INSERT INTO sensor_readings
                              (sensor_id, bucket, reading_time, installation_id, solar_w, battery_pct, volatage_v, temp_c)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                              USING TTL 94608000                            
                              ''')


# Inserer par lots
BATCH_SIZE = 500
total = len(df)
inserers = 0
debut = time.time()

for i, (_, row) in enumerate(df.iterrows()):
    session.execute_async(insert_stmt, [
        row['sensor_id'],
        row['bucket'],
        row['reading_time'].to_pydatetime(),
        int(row['installtion_id']),
        float(row['solar_output_w']),
        float(row['battery_pct']),
        float(row.get('voltage_v', 202.0)),
        float(row.get('temperature_c',35.0)) 
    ])
    inserers += 1
    if inserers % BATCH_SIZE == 0:
        durée = time.time() - debut
        taux = inserers / durée
        print(f'{inserers:,} / {total:,} ({inserers/total*100:1.f}%)- {taux:0.f} inserts/s')
        
print(f'Import terminé: {inserers:,} mesures en {time.time()-debut:1.f}s')
cluster.shutdown()        
         
