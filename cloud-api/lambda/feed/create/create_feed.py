import json, boto3, os
from datetime import datetime
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger
from typing import Dict
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_FEED'])
music_table = dynamodb.Table("MusicCatalog")
artists_table = dynamodb.Table("Artists")
subscriptions_table = dynamodb.Table("Subscriptions")
listening_table = dynamodb.Table("ListeningHistory")
genres_table = dynamodb.Table("Genres")
ratings_table = dynamodb.Table("Ratings")
genre_relations = dynamodb.Table("GenreRelations")

TIME_SLOTS = ["morning", "afternoon", "evening", "night"]

WEIGHTS = {
    "subscription_genre": 8,
    "subscription_artist": 10,
    "positive_rating_song": 7,
    "positive_rating_album": 5,
    "neutral_rating": 0,
    "negative_rating": -6,
    "listen_same_slot": 6,
    "listen_other_slot": 2,
}

predefined_genres = [
    "Pop", "Rock", "Hip-Hop", "Jazz", "Classical",
    "Electronic", "Country", "Reggae", "Blues", "Metal",
    "Folk", "R&B", "Punk", "Disco", "Funk",
    "Gospel", "Ska", "Soul", "Techno", "House"
]

@handle_lambda_exceptions
def handler(event, _context):
    for record in event.get('Records', []):
        body = json.loads(record['body'])
        user_id = body.get('userId')
        if not user_id:
            continue

        genre_scores = get_genres_time_scores()
        logger.info(f"genre scores {genre_scores}")
        artist_scores = get_artists_time_scores()
        logger.info(f"artist scores {artist_scores}")
        slot = get_time_of_day()

        analyze_user_listening(user_id, genre_scores, artist_scores)
        analyze_user_subscriptions(user_id, genre_scores, artist_scores)
        analyze_user_ratings(user_id, genre_scores, artist_scores)

        logger.info(f"genre scores updated {genre_scores}")
        logger.info(f"artist scores updated {artist_scores}")

        current_slot_genre_scores = scores_for_current_slot(genre_scores, slot)
        top_genres = sorted(current_slot_genre_scores, key=current_slot_genre_scores.get, reverse=True)[:5]

        current_artist_scores = scores_for_current_slot(artist_scores, slot)
        top_artists = sorted(current_artist_scores, key=current_artist_scores.get, reverse=True)[:5]

        logger.info(f"current slot genre scores {current_slot_genre_scores}")
        logger.info(f"current artist scores {current_artist_scores}")

        songs = []
        albums = []
        feed_items = []

        for genre in top_genres:
           
            songs_albums = genre_relations.query(KeyConditionExpression=Key("PK").eq(genre)).get("Items", [])
            for item in songs_albums:
                
                sk = item.get('SK', '')
                id = sk.split('#')[1] if '#' in sk else sk
                entity_type = item.get('EntityType')

                if entity_type in ('song', 'album') and id:  
                    target_list = songs if entity_type == 'song' else albums
                    target_list.append({
                      "type": entity_type,
                      "id": id,
                      "score": current_slot_genre_scores[genre]
                    })

        for artist in top_artists:
            artists_content = artists_table.query(KeyConditionExpression=Key("PK").eq(artist)).get("Items", [])
            for item in artists_content:

                sk = item.get('SK', '')
                id = sk.split('#')[1] if '#' in sk else sk
                entity_type = item.get('EntityType')

                if sk == 'METADATA':
                  feed_items.append({
                      "type": 'artist',
                      "id": item.get('PK')
                  })

                elif entity_type in ('song', 'album') and id:
                  target_list = songs if entity_type == 'song' else albums
                  target_list.append({
                      "type": entity_type,
                      "id": id,
                      "score": current_artist_scores[artist]
                  })

        songs = remove_duplicates(songs)
        albums = remove_duplicates(albums)

        top_albums = sorted(albums, key=lambda a: a["score"], reverse=True)[:5]
        top_albums = [{k: v for k, v in a.items() if k != "score"} for a in top_albums]

        top_songs = sorted(songs, key=lambda s: s["score"], reverse=True)[:5]
        top_songs = [{k: v for k, v in s.items() if k != "score"} for s in top_songs]

        feed_items.extend(top_albums)
        feed_items.extend(top_songs)    

        table.put_item(
            Item={
                "PK": f"USER#{user_id}",
                "SK": f"FEED#{slot}",
                "feedItems": feed_items
            }
        )

    return {"message": f"Feed for user {user_id} successfully created"}


def get_genres_time_scores() -> Dict[str, Dict[str, int]]:
    return {g: {slot: 0 for slot in TIME_SLOTS} for g in predefined_genres}

def remove_duplicates(items):
    unique = {}
    for item in items:
        key = (item["type"], item["id"]) 
        if key not in unique:
            unique[key] = item
    return list(unique.values())


def get_artists_time_scores() -> Dict[str, Dict[str, int]]:
    artists = artists_table.scan().get("Items", [])
    return {a["PK"]: {slot: 0 for slot in TIME_SLOTS} for a in artists}


def analyze_user_subscriptions(user_id, genre_scores, artist_scores):
    user_subscriptions = subscriptions_table.query(
        KeyConditionExpression=Key("PK").eq(user_id)
    ).get("Items", [])

    for sub in user_subscriptions:
        type_ = sub['type']
        sk = sub.get("SK")
        if type_ == "artist" and sk in artist_scores:
            for slot in TIME_SLOTS:
                artist_scores[sk][slot] += WEIGHTS["subscription_artist"]
        elif type_ == "genre" and sk in genre_scores:
            for slot in TIME_SLOTS:
                genre_scores[sk][slot] += WEIGHTS["subscription_genre"]


def analyze_user_ratings(user_id, genre_scores, artist_scores):
    user_ratings = ratings_table.query(KeyConditionExpression=Key("PK").eq(user_id)).get("Items", [])

    for rating in user_ratings:
        rating_type = rating['type']
        value = rating.get('rating', 3)
        delta = WEIGHTS["neutral_rating"]

        if value >= 4:
            if rating_type == "SONG":
                delta = WEIGHTS["positive_rating_song"]
            elif rating_type == "ALBUM":
                delta = WEIGHTS["positive_rating_album"]
            elif rating_type == "ARTIST":
                delta = WEIGHTS["subscription_artist"]
        elif value <= 2:
            delta = WEIGHTS["negative_rating"]

        if rating_type == "ARTIST":
            sk = rating.get("SK")
            if sk in artist_scores:
                for slot in TIME_SLOTS:
                    artist_scores[sk][slot] += delta
        else:  # SONG or ALBUM
            for g in rating.get("genres", []):
                if g in genre_scores:
                    for slot in TIME_SLOTS:
                        genre_scores[g][slot] += delta
            for a in rating.get("artistIds", []):
                if a in artist_scores:
                    for slot in TIME_SLOTS:
                        artist_scores[a][slot] += delta


def analyze_user_listening(user_id, genre_scores, artist_scores):
    user_listenings = listening_table.query(KeyConditionExpression=Key("PK").eq(user_id)).get("Items", [])

    for listen in user_listenings:
        listen_slot = listen.get("timeOfDay")
        for genre in listen.get("genres", []):
            if genre in genre_scores:
                for slot in TIME_SLOTS:
                    genre_scores[genre][slot] += WEIGHTS["listen_same_slot"] if slot == listen_slot else WEIGHTS["listen_other_slot"]
        for artist_id in listen.get("artist_ids", []):
            if artist_id in artist_scores:
                for slot in TIME_SLOTS:
                    artist_scores[artist_id][slot] += WEIGHTS["listen_same_slot"] if slot == listen_slot else WEIGHTS["listen_other_slot"]


def scores_for_current_slot(score_dict, current_slot): #returns score for current time slot
    return {entity: slots.get(current_slot, 0) for entity, slots in score_dict.items()}


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
