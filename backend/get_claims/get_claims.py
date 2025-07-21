
import boto3
import os
import json
from functools import wraps

FILE_METADATA_TABLE_NAME = os.environ.get('FILE_METADATA_TABLE_NAME')

dynamodb_client = boto3.client('dynamodb')

def auth_check(func):
    @wraps(func)
    def wrapper(event, context, *args, **kwargs):
        # Confirm event is from API Gateway and user is authenticated
        if 'requestContext' not in event or 'authorizer' not in event['requestContext']:
            return {
                'statusCode': 400,
                'body': 'Bad Request: Missing request context or authorizer'
            }
        
        if 'jwt' not in event['requestContext']['authorizer'] or 'claims' not in event['requestContext']['authorizer']['jwt']:
            return {
                'statusCode': 400,
                'body': 'Bad Request: Missing JWT claims'
            }
        
        user_claims = event['requestContext']['authorizer']['jwt']['claims']
        if not user_claims or 'sub' not in user_claims:
            return {
                'statusCode': 401,
                'body': 'Unauthorized'
            }
        
        # Attach user_claims to event for downstream use
        event['user_claims'] = user_claims
        return func(event, context, *args, **kwargs)
    return wrapper

@auth_check
def lambda_handler(event, context):

    # Get claims for the authenticated user
    user_claims = event['user_claims']
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

def get_claims(user_id, startKey = None):
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
            'created_at': item.get('created_at', {}).get('S', ''),
            'tags': item.get('tags', {}).get('SS', [])
        } for item in response.get('Items', [])
    ]

    return claims, response.get('LastEvaluatedKey', None)


