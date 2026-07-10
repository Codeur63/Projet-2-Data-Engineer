import json, boto3, os
import pandas as pd
from sqlalchemy import create_engine, text

s3 = boto3.client('s3')
BUCKET = 'solarmboa-prod-data-lake'


def get_pipeline_status(event, context):
    """GET /pipeline/status — Liste les fichiers traités."""
    response = s3.list_objects_v2(
        Bucket=BUCKET, Prefix='silver/', MaxKeys=50
        )
    files = [
        {
            'key'    : obj['Key'],
            'size_kb'    : round(obj['Size'] / 1024, 1),
            'last_modified' : obj['LastModified'].isoformat()
        }
         for obj in response.get('Contents', [])
    ]
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'processed_files': files, 'count': len(files)})
    }
    
    
def trigger_reprocess(event, context):
    """POST /pipeline/reprocess — Redéclenche le traitement d'un fichier."""
    body    = json.loads(event.get('body', '{}'))
    src_key = body.get('source_key')
    if not src_key:
        return {'statusCode': 400,
        'body': json.dumps({'error': 'source_key requis'}) }
    # Copier l'objet sur lui-même pour re-déclencher l'événement S3
    s3.copy_object(
        Bucket=BUCKET, Key=src_key,
        CopySource={'Bucket': BUCKET, 'Key': src_key},
        MetadataDirective='REPLACE',
        Metadata={'reprocess': 'true'}
    )
    return {
    'statusCode': 200,
    'body': json.dumps({'message': f'Retraitement lancé pour {src_key}'})
    }