import os, json, uuid
from util.s3 import generate_presigned_url


audio_bucket = os.environ.get("AUDIO_BUCKET")
image_bucket = os.environ.get("IMAGE_BUCKET")

def handler(event, context):

  data = json.loads(event['body']) 

  song_id = f"SONG{str(uuid.uuid4())}"


  presigned_audio_url = generate_presigned_url(f"songs/{song_id}",
                                              audio_bucket,
                                              3600,
                                              data['audio_type'])
  

  presigned_audio_cover_url = generate_presigned_url(f"images/{song_id}",
                                                    image_bucket,
                                                    3600,
                                                    data['cover_type']                
  )


  return {
          'statusCode': 201,
          "headers": {
              "Access-Control-Allow-Origin": "*", 
              "Access-Control-Allow-Credentials": "true",
          },
          'body': json.dumps({
              'coverUploadPresignedUrl': presigned_audio_cover_url,
              'audioUploadPresignedUrl': presigned_audio_url
          })
      }

  

  


