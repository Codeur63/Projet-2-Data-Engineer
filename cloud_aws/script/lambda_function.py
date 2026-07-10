import json, boto3, io, os, logging
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
DEST_BUCKET = os.environ.get('DEST_BUCKET', 'solarmboa-prod-data-lake')

def lambda_handler(event, context):
    """Point d'entrée Lambda — déclenché par un événement S3."""
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key    = record['s3']['object']['key']
        size  = record['s3']['object']['size']
        logger.info(f'Traitement : s3://{bucket}/{key} ({size} bytes)')
        
        if not key.endswith('.csv'):
            logger.warning(f'Fichier ignoré (pas un CSV) : {key}')
        continue
    
        result = transform_csv_to_parquet(bucket, key, size)
        logger.info(f'Pipeline terminé : {json.dumps(result)}')
        
    return {'statusCode': 200, 'body': 'Pipeline ETL terminé'}


def transform_csv_to_parquet(bucket: str, key: str, size: int) -> dict:
    """Transformation CSV → Parquet avec nettoyage et partitionnement."""
    
    # ── 1. Lecture du CSV depuis S3 ───────────────────────────────────
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    logger.info(f'CSV lu : {df.shape[0]} lignes × {df.shape[1]} colonnes')
    
    # ── 2. Transformations ────────────────────────────────────────────
    # Nettoyage des noms de colonnes
    df.columns = [
        c.strip().lower().replace(' ', '_').replace('(cm)', '').strip()
        for c in df.columns
        ]
    # Suppression des doublons et lignes vides
    before = len(df)
    df = df.drop_duplicates().dropna(how='all')
    after = len(df)
    logger.info(f'Nettoyage : {before - after} lignes supprimées')
    # Ajout de métadonnées de traitement
    now = datetime.now(timezone.utc)
    df['_ingestion_date'] = now.strftime('%Y-%m-%d')
    df['_source_file']    = key
    
    # ── 3. Construction du chemin de sortie partitionné par date ─────
    # raw/dataset/iris.csv → processed/dataset/year=2024/month=01/iris.parquet
    parts  = key.replace('raw/', '').rsplit('/', 1)
    dataset_name = parts[0] if len(parts) > 1 else 'unknown'
    filename   = parts[-1].replace('.csv', '.parquet')
    output_key = (
        f'processed/{dataset_name}/'
        f'year={now.year}/month={now.month:02d}/'
        f'{filename}'
    )
    
    # ── 4. Sérialisation en Parquet et upload vers S3 ─────────────────
    buffer = io.BytesIO()
    df.to_parquet(buffer, compression='snappy', index=False)
    buffer.seek(0)
    s3.put_object(
    Bucket = DEST_BUCKET,
    Key = output_key,
    Body = buffer.getvalue(),
    ContentType = 'application/octet-stream',
    Metadata = {
        'source-file' : key,
        'rows'        : str(len(df)),
        'columns'     : str(len(df.columns)),
        'processed-at' : now.isoformat()
        }
    )
    logger.info(f'Parquet écrit : s3://{DEST_BUCKET}/{output_key}')
    return {
        'source'     : f's3://{bucket}/{key}',
        'destination' : f's3://{DEST_BUCKET}/{output_key}',
        'rows'       : len(df),
        'columns'    : len(df.columns),
        'size_input' : size,
        'processed_at': now.isoformat()
    }