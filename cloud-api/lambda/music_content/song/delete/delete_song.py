import boto3, os

from util.http_response import http_response
from util.auth import require_role

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client("s3")
music_catalog_table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

@require_role('admin')
def handler(event, _context): 
    song_id = event['pathParameters']['id']
    pk = f'SONG#{song_id}'

    response = music_catalog_table.get_item(
        Key={
            'PK': pk,
            'SK': 'METADATA'
        }
    )

    if 'Item' not in response:
        return http_response(404, {'message': 'Song not found'})
    
    song_item = response['Item']
    genres = song_item.get("genres", [])
    audio_path = song_item.get("audioPath")
    cover_path = song_item.get("coverPath")

    music_catalog_table.delete_item(
        Key={
            'PK': pk,
            'SK': 'METADATA'
        }
    )

    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            batch.delete_item(
                Key={
                    'PK': genre,
                    'SK': song_id
                }
            )

    objects_to_delete = []
    
    if audio_path:
        objects_to_delete.append({'Key': audio_path})
    if cover_path:
        objects_to_delete.append({'Key': cover_path})

    if objects_to_delete:
        s3.delete_objects(
            Bucket=MEDIA_BUCKET,
            Delete={'Objects': objects_to_delete}
        )

    return http_response(200, {'message': 'Song successfully deleted'})
