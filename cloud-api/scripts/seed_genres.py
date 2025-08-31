import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table_name = 'MusicCatalog'
table = dynamodb.Table(table_name)

predefined_genres = [
    "Pop",
    "Rock",
    "Hip-Hop",
    "Jazz",
    "Classical",
    "Electronic",
    "Country",
    "Reggae",
    "Blues",
    "Metal",
    "Folk",
    "R&B",
    "Punk",
    "Disco",
    "Funk",
    "Gospel",
    "Ska",
    "Soul",
    "Techno",
    "House"
]

try:
  with table.batch_writer() as batch:
      for genre in predefined_genres:
          batch.put_item(
              Item={
                  'PK': "genre",
                  'SK': 'GENRE#' + genre,
                  'description': f'{genre} music genre',
                  'display_name': genre
              }
          )
  print("Genres seeded successfully.")
except ClientError as e:
  print(f"Error seeding genres: {e.response['Error']['Message']}")