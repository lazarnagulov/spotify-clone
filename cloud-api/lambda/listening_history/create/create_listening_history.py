import json, boto3, os
from datetime import datetime, timezone
from decimal import Decimal

from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
table = dynamodb.Table(os.environ["LISTENING_HISTORY"])

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))

    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]

    song_id = body.get("songId")
    if not song_id:
        return http_response(400, {"message": "Missing song id"})

    time_of_day = get_time_of_day()

    item = {
        "PK": f"USER#{user_id}",
        "SK": Decimal(datetime.now(timezone.utc).timestamp()),
        "song_id": song_id,
        "album_id": body.get("albumId"),
        "artist_ids": body.get("artists"),
        "genre": body.get("genres"),
        "timeOfDay": time_of_day
    }

    table.put_item(Item=item)

    return http_response(201, {"message": "Listening history record added."})

def get_time_of_day():
    hour = datetime.utcnow().hour  

    if 5 <= hour < 12:
        return "morning"    
    elif 12 <= hour < 17:
        return "afternoon"  
    elif 17 <= hour < 21:
        return "evening"    
    else:
        return "night"
