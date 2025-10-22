import json
import boto3
import os
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_FEED'])
music_table = dynamodb.Table("MusicCatalog")
artists_table = dynamodb.Table("Artists")

@handle_lambda_exceptions
def handler(event, _context):
    
    for record in event.get('Records', []):
        
        body = json.loads(record['body'])
        user_id = body.get('userId')
        if not user_id:
            continue

        # TODO: implement algorithm for personalized feed
        music_resp = music_table.scan(Limit=5) 
        music_items = music_resp.get("Items", [])

        music_feed_items = [{"id": item["PK"].split("#")[1], "type": item["type"]} for item in music_items]

        artists = artists_table.scan(Limit=5)
        artist_items = artists.get("Items", [])
        artist_feed_items = [{"id": item["PK"], "type": 'artist'} for item in artist_items]

        feed_items = music_feed_items + artist_feed_items
        # ---------

        table.put_item(
            Item={
                "PK": f"USER#{user_id}",
                "SK": "FEED", 
                "feedItems": feed_items
                }
          )
        
        return {"message": f"Feed for user with id{user_id} succesfully created"}
