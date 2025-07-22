
import boto3
import os
import json
from auth_check import auth_check # this matches the deployed lambda path

FILE_METADATA_TABLE_NAME = os.environ.get('FILE_METADATA_TABLE_NAME')

dynamodb_client = boto3.client('dynamodb')

@auth_check
def lambda_handler(event, context):

    # Get claims for the authenticated user
    user_claims = event['requestContext']['authorizer']['jwt']['claims']
    sub = user_claims['sub']

    try:
        claims, continuationKey = get_claims(sub)
    except Exception as e:
        print(f"Error getting claims: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error: Could not retrieve uploads'
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'claims': claims,
            'continuationKey': continuationKey
        })
    }

def get_claims(user_id: str, startKey: str | None = None):
    props = {
        "TableName": FILE_METADATA_TABLE_NAME,
        "KeyConditionExpression": 'user_id = :user_id',
        "ExpressionAttributeValues":{
            ':user_id': {'S': user_id}
        },
        "ScanIndexForward":False 
    }

    if startKey:
        props['ExclusiveStartKey'] = {
            "S": startKey
        }

    response = dynamodb_client.query(**props)

    claims = [
        {
            'claim_id': item.get('claim_id', {}).get('S', ''),
            'filename': item.get('filename', {}).get('S', ''),
            'client': item.get('client', {}).get('S', ''),
            'created_at': item.get('created_at', {}).get('S', ''),
            'tags': item.get('tags', {}).get('SS', [])
        } for item in response.get('Items', [])
    ]

    return claims, response.get('LastEvaluatedKey', None)


