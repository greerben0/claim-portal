import boto3
import os
import base64
import json
import uuid
import datetime
from typing import List
from auth_check.auth_check import auth_check # this matches the deployed lambda path

FILE_S3_BUCKET_NAME = os.environ.get('FILE_S3_BUCKET_NAME')
FILE_METADATA_TABLE_NAME = os.environ.get('FILE_METADATA_TABLE_NAME')

s3_client = boto3.client('s3')  
dynamodb_client = boto3.client('dynamodb')

@auth_check
def lambda_handler(event, context):
    # Get claims for the authenticated user
    user_claims = event['requestContext']['authorizer']['jwt']['claims']
    sub = user_claims['sub']

    body = event.get('body', '')
    body = json.loads(body)
    
    filename = body.get('filename')

    print(filename)
    if (not filename or not filename.lower().endswith(".txt")):
        return {
            'statusCode': 400,
            'body': f'Invalid file. Must be .txt'
        }
    
    try:
        file = base64.b64decode(body.get('file_base64', '')).decode('utf-8')
    except Exception as e:
       print(str(e))
       return {
            'statusCode': 500,
            'body': f'Error decoding file {str(e)}'
        }
    
    filename = body.get('filename', '')
    tags = body.get('tags', [])
    client = body.get('client', '')
    claim_id = str(uuid.uuid4())

    try:
        create_claim(claim_id, sub, file, filename, client, tags)
    except Exception as e:
       print(str(e))
       return {
            'statusCode': 500,
            'body': f'Error creating claim {claim_id}.'
        }
    
    print(f'Created Claim {claim_id}')

    response = {
        'statusCode': 200,
        'body': f'Claim received.  {str(claim_id)}'
    }
    
    return response


def create_claim(claim_id: str, user_id: str, file: str, filename: str, client: str, tags: List[str]):

    keypath = f'{user_id}/{claim_id}/{filename}'
    s3_client.put_object(
        Bucket=FILE_S3_BUCKET_NAME,
        Key=keypath,
        Body=file
    )

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    iso_utc = now_utc.isoformat()

    dynamodb_client.put_item(
        TableName=FILE_METADATA_TABLE_NAME,
        Item={
            'claim_id': {'S': claim_id},
            'user_id': {'S': user_id},
            'filename': {'S': filename},
            'client': {'S': client},
            'created_at': {'S': iso_utc},
            'tags': {'SS': tags},
        }
    )
    
