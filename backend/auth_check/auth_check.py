from functools import wraps

def auth_check(func):
    @wraps(func)
    def wrapper(event, context, *args, **kwargs):
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
        
        return func(event, context, *args, **kwargs)
    return wrapper