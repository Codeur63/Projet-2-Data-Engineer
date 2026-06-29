import pandas as pd
import time
import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy, WhiteListRoundRobinPolicy
from cassandra.query import BatchStatement, ConsistencyLevel
from datetime import datetime, date
from cassandra.query import BatchType # N'oubliez pas l'import en haut
from cassandradb.telemetry_repository import TelemetryRepository

load_dotenv()

repo = TelemetryRepository()

CSV_PATH = os.getenv("SENSOR_TELEMETRY")

print(f"\n[1/4] Connexion à Cassandra...")


# On utilise WhiteListRoundRobinPolicy pour INTERDIRE à Python d'aller voir les IP internes
policy = WhiteListRoundRobinPolicy(['127.0.0.1','127.0.0.2', '127.0.0.3'])

# Connexion à Cassandra
cluster = Cluster(
    ['localhost'],
    port = 9042,
    load_balancing_policy=policy
) 
try:
    session = cluster.connect("solarmboa")
    print(f"  ✅ Connecté au keyspace solarmboa ")
except Exception as e:
    print(f"  ❌ Erreur de connexion : {e}")
    exit(1)

print("\n[2/4] Chargement des données...")

# Charger le CSV
df = pd.read_csv(CSV_PATH, parse_dates=['timestamp'])
print(f"Données chargées: {len(df):,} lignes")

# Ajouter le bucket date pour la partiion jey
df['bucket'] = df['timestamp'].dt.date


print("\n[3/4] Préparation de la requête...")

# Preparion de la requete qui sont compilées une fois et réutilisées. Ce qui acrue la rapidité et protection
insert_stmt = session.prepare('''
    INSERT INTO sensor_readings
    (sensor_id, bucket, timestamp, region, solar_output_w, battery_level_pct, consumption_w, installation_id, alert_code, signal_rssi, temp_c )
    VALUES (?,?,?,?,?,?,?,?,?,?,?)                      
''')


# Inserer par lots
BATCH_SIZE = 100
total = len(df)
inserers = 0
debut = time.time()

print(f"\n[4/4] Début de l'insertion ({total:,} lignes)...")
for i in range(0, total, BATCH_SIZE):
    
    # prendre un morceau du Dataframe
    chunk = df.iloc[i:i + BATCH_SIZE]
    
    # On crée un batch
    batch = BatchStatement(
    batch_type=BatchType.UNLOGGED, 
    consistency_level=ConsistencyLevel.LOCAL_QUORUM
    )
    try:
        
        for _, row in chunk.iterrows():
            # On mapping exactement les colonnes du CSV avec la requête CQL
            # batch.add(insert_stmt, (
            #     row['sensor_id'],
            #     row['bucket'],
            #     row['timestamp'].to_pydatetime(),
            #     str(row['alert_code']) if pd.notna(row['alert_code']) else None,
            #     float(row['battery_level_pct']),
            #     float(row['consumption_w']),
            #     int(row['installation_id']) if pd.notna(row['installation_id']) else None,  
            #     row['region'],
            #     float(row['solar_output_w']),           
            # ))
            
            repo.inserer_mesure(
                sensor_id=row['sensor_id'],
                timestamp=row['timestamp'].to_pydatetime(),
                alert_code=str(row['alert_code']) if pd.notna(row['alert_code']) else None,
                battery_level_pct=float(row['battery_level_pct']),
                consumption_w=float(row['consumption_w']),
                installation_id=int(row['installation_id']) if pd.notna(row['installation_id']) else None,  
                region=row['region'],
                solar_output_w=float(row['solar_output_w']),           
            )
            
            
    except Exception as e:
        print(f"\n Insertion n'as pas reussi : {e} ")    
        break    
        
    try:
        session.execute(batch)
        inserers += len(chunk)
    except Exception as e:
        print(f"\n  ❌ Erreur sur le batch {i//BATCH_SIZE} : {e}")
        
    if inserers % 5000 < BATCH_SIZE and inserers > 0:
        duree = time.time() - debut
        taux = inserers / duree
        print(f'  ⏳ {inserers:,} / {total:,} ({inserers/total*100:.1f}%) - {taux:.0f} inserts/s')        
        
    # inserers += 1
    # if inserers % BATCH_SIZE == 0:
    #     durée = time.time() - debut
    #     taux = inserers / durée
    #     print(f'{inserers:,} / {total:,} ({inserers/total*100:1.f}%)- {taux:0.f} inserts/s')
        
# print(f'Import terminé: {inserers:,} mesures en {time.time()-debut:1.f}s')
# cluster.shutdown()        
         
duree_totale = time.time() - debut
print(f'\n✅ Import terminé : {inserers:,} mesures en {duree_totale:.1f}s')
print(f'🚀 Vitesse moyenne : {inserers/duree_totale:.0f} lignes/seconde')
cluster.shutdown()