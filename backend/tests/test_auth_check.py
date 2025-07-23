import pytest

from auth_check.auth_check import auth_check

def lambda_handler_200(event, context):
    return { 'statusCode': 200 }

wrapped_func = auth_check(lambda_handler_200)

def test_auth_check_no_request_context():
    event = {}

    response = wrapped_func(event, {})
    assert response['statusCode'] == 400

def test_auth_check_no_request_context_authorizer():
    event = {
        'requestContext': {}
    }
    response = wrapped_func(event, {})
    assert response['statusCode'] == 400

def test_auth_check_no_request_context_authorizer_jwt():
    event = {
        'requestContext': {
            'authorizer': {}
        }
    }
    response = wrapped_func(event, {})
    assert response['statusCode'] == 400

def test_auth_check_no_request_context_authorizer_jwt_claims():
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {}
            }
        }
    }
    response = wrapped_func(event, {})
    assert response['statusCode'] == 400

def test_auth_check_no_request_context_authorizer_jwt_claims_sub():
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {}
                }
            }
        }
    }
    response = wrapped_func(event, {})
    assert response['statusCode'] == 401


def test_auth_check_pass():
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': 'abc-123'
                    }
                }
            }
        }
    }
    response = wrapped_func(event, {})
    assert response['statusCode'] == 200