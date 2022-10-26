# References:
# - https://learn.acloud.guru/course/d15d3060-fa99-4dbd-90c1-c1b9abb70f53/dashboard

import json
import os
import tempfile
import traceback

import boto3
from PIL import Image

s3_client = boto3.client('s3')
DEST_BUCKET = os.environ['DEST_BUCKET']
SIZE = 256, 256


def handler(event, context):
  try:
    for record in event['Records']:
      source_bucket = record['s3']['bucket']['name']
      key = record['s3']['object']['key']
      thumb = 'thumb-' + key

      print('Saving thumbnail of {} from {} as {}'.format(key, source_bucket, thumb))
      with tempfile.TemporaryDirectory() as tmp_dir:
        download_path = os.path.join(tmp_dir, key)
        upload_path = os.path.join(tmp_dir, thumb)
        s3_client.download_file(source_bucket, key, download_path)
        generate_thumbnail(download_path, upload_path)
        s3_client.upload_file(upload_path, DEST_BUCKET, thumb)

        print('Thumbnail image saved to {} as {}'.format(DEST_BUCKET, thumb))

      return {
        'statusCode': 200,
        'body': json.dumps({'msg': 'Hello from containerized lambda'})
      }
  except Exception as e:
    traceback.print_exc()
    return {
      'statusCode': 500,
      'body': json.dumps(e.__str__())
    }



def generate_thumbnail(source_path, dest_path):
  print('generating thumbnail')
  with Image.open(source_path) as image:
    image.thumbnail(SIZE)
    image.save(dest_path)
