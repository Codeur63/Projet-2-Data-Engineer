import boto3, pandas as pd, os
import pyarrow 
from pathlib import Path 
from dotenv import load_dotenv

load_dotenv()

BUCKET = 'solarmboa-prod-data-lake'
s3 = boto3.client('s3')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"

DESTINATION_FOLDER = "gold/dashboards/" 

# s3.upload_file('../../data/raw/sensors_telemetry.csv', BUCKET, 'bronze/iot/sensors_telemetry.csv')
# s3.upload_file('../../data/raw/network_graph.csv', BUCKET, 'bronze/networks/network_graph.csv')
# s3.upload_file('../../data/raw/network_nodes_distributors.csv', BUCKET, 'bronze/networks/network_nodes_distributors.csv')
# s3.upload_file('../../data/raw/network_nodes_technicians.csv', BUCKET, 'bronze/networks/network_nodes_technicians.csv')
# s3.upload_file('../../data/raw/payments.csv', BUCKET, 'bronze/payments/payments.csv')
# s3.upload_file('../../data/raw/installations.json', BUCKET, 'bronze/installations/installations.json')

# print('Fichier upload avec success '+BUCKET)

# def upload_silver():
#     s3.upload_file('../../data/raw/installations.json', BUCKET, 'silver/installations_clean/installations.parquet', )
#     s3.upload_file('../../data/processed/network_graph.csv', BUCKET, 'silver/network_clean/network_graph.parquet')
#     s3.upload_file('../../data/processed/network_nodes_distributors.csv', BUCKET, 'silver/network_clean/network_nodes_distributors.parquet')
#     s3.upload_file('../../data/processed/payments.csv', BUCKET, 'silver/payments_clean/payments.parquet')
#     s3.upload_file('../../data/processed/network_nodes_technicians.csv', BUCKET, 'silver/network_clean/network_nodes_technicians.parquet')
#     s3.upload_file('../../data/processed/sensors_telemetry.csv', BUCKET, 'silver/iot_clean/sensors_telemetry.parquet')    

# upload_silver()    

# df = pd.read_csv('../../data/raw/installations.json') 
# df.to_parquet('../../data/parquet/installations.json', compression='snappy', index=False, engine='pyarrow')

# df = pd.read_csv('../../data/processed/network_graph.csv') 
# df.to_parquet('../../data/parquet/network_graph.csv', compression='snappy', index=False, engine='pyarrow')

# df = pd.read_csv('../../data/processed/network_nodes_distributors.csv') 
# df.to_parquet('../../data/parquet/network_nodes_distributors.csv', compression='snappy', index=False, engine='pyarrow')

# df = pd.read_csv('../../data/processed/network_nodes_technicians.csv') 
# df.to_parquet('../../data/parquet/network_nodes_technicians.csv', compression='snappy', index=False, engine='pyarrow')

# df = pd.read_csv('../../data/processed/payments.csv') 
# df.to_parquet('../../data/parquet/payments.csv', compression='snappy', index=False, engine='pyarrow')

# df = pd.read_csv('../../data/processed/sensors_telemetry.csv') 
# df.to_parquet('../../data/parquet/sensors_telemetry.csv', compression='snappy', index=False, engine='pyarrow')


print('Fichiers Uploadé uploadé')


print('\n📦 Contenu du Data Lake :')
response = s3.list_objects_v2(Bucket=BUCKET)

for obj in response.get('Contents', []):
    size_kb = obj['Size'] / 1024
    print(f" {obj['Key']:<50} {size_kb:.1f} KB")


def upload_warehouse_to_s3():  
    
    if not WAREHOUSE_DIR.exists():
        print(f"Erreur : Le dossier {WAREHOUSE_DIR} n'existe pas.")
        return


    files = list(WAREHOUSE_DIR.glob("*.csv"))

    if not files:
        print("Aucun fichier .csv trouvé dans le dossier warehouse.")
        return

    print(f"Début de l'upload de {len(files)} fichiers vers s3://{BUCKET}/{DESTINATION_FOLDER}...\n")

    for file_path in files:
        table_name = file_path.stem  
        parquet_path = file_path.with_suffix('.parquet')
        s3_key = f"{DESTINATION_FOLDER}{parquet_path.name}"
        
        try:
            df = pd.read_csv(file_path, low_memory=False)
            df.to_parquet(parquet_path, index=False, engine="pyarrow")
            s3.upload_file(
                Filename=str(parquet_path),
                Bucket=BUCKET,
                Key=s3_key
            )
            print(f"✅ Succès : {file_path.name} -> {s3_key}")
        except Exception as e:
            print(f"❌ Erreur lors de l'upload de {file_path.name} : {e}")

    print("\nUpload terminé !")    
    

upload_warehouse_to_s3()
