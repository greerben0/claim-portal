import pytest
import json
import os
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import uuid

from unittest import mock
import base64
from typing import List

from create_claim.create_claim import lambda_handler, create_claim

def test_handler(monkeypatch):
    expected_sub = 'abc-123'
    input_file = ""
    expected_filename = 'filename.txt'
    expected_tags = ['tag1', 'tag2']
    expected_client = 'Client123'
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': expected_sub
                    }
                }
            }
        },
        'body': json.dumps({
            'file_base64': input_file,
            'filename': expected_filename,
            'client': expected_client,
            'tags': expected_tags
        })
    }
     
    def mock_create_claim(claim_id: str, user_id: str, file: str, filename: str, client: str, tags: List[str]):
       assert user_id == expected_sub
       assert file
       assert filename == expected_filename
       assert client == expected_client
       assert tags == expected_tags
    
    monkeypatch.setattr("create_claim.create_claim.create_claim", mock_create_claim)
    
    def mock_decode(args):
        return b'test'
    
    monkeypatch.setattr("base64.b64decode", mock_decode)

    response = lambda_handler(event, {})
    assert response['body'].startswith('Claim received')
    assert response['statusCode'] == 200

def test_handler_bad_filename():
    expected_sub = 'abc-123'
    expected_file = base64.b64encode("test".encode('utf-8'))
    expected_filename = 'filename'
    expected_tags = ['tag1', 'tag2']
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': expected_sub
                    }
                }
            }
        },
        'body': json.dumps({
            'file_base64': str(expected_file),
            'filename': expected_filename,
            'tags': expected_tags
        })
    }

    response = lambda_handler(event, {})

    assert response['statusCode'] == 400


def test_handler_bad_file():
    expected_sub = 'abc-123'
    expected_file = ""
    expected_filename = 'filename.txt'
    expected_tags = ['tag1', 'tag2']
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': expected_sub
                    }
                }
            }
        },
        'body': json.dumps({
            'file_base64': str(expected_file),
            'filename': expected_filename,
            'tags': expected_tags
        })
    }

    response = lambda_handler(event, {})

    assert response['statusCode'] == 500

def test_handler_error_creating_claim(monkeypatch):
    expected_sub = 'abc-123'
    expected_file = "test".encode('utf-8')
    expected_filename = 'filename.txt'
    expected_tags = ['tag1', 'tag2']
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': expected_sub
                    }
                }
            }
        },
        'body': json.dumps({
            'file_base64': str(expected_file),
            'filename': expected_filename,
            'tags': expected_tags
        })
    }
     
    def mock_create_claim(claim_id, sub, file, filenamme, tags): 
        raise Exception('Error')
    
    monkeypatch.setattr("create_claim.create_claim.create_claim", mock_create_claim)
    
    response = lambda_handler(event, {})

    assert response['statusCode'] == 500


def test_create_claim_stored_under_user_sub(monkeypatch):
        
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # Arrange
    user_sub = "user-123"
    s3_bucket = "test-bucket"
    monkeypatch.setenv("FILE_S3_BUCKET_NAME", s3_bucket)
    claim_id = str(uuid.uuid4())
    filename = 'test.txt'
    file_contents = ''
    client = 'Reckless Ron'

    # Patch S3 and DynamoDB clients
    mock_s3 = mock.Mock()
    mock_dynamodb = mock.Mock()
    monkeypatch.setattr("create_claim.create_claim.s3_client", mock_s3)
    monkeypatch.setattr("create_claim.create_claim.dynamodb_client", mock_dynamodb)

    # Act
    result = create_claim(
        claim_id=claim_id,
        user_id=user_sub,
        file=file_contents,
        filename=filename,
        client=client,
        tags=['tag1']
    )

    expected_s3_key = f"{user_sub}/{claim_id}/{filename}"
    mock_s3.put_object.assert_called_once_with(
        Bucket=mock.ANY,
        Key=expected_s3_key,
        Body=file_contents
    )

    # Assert DynamoDB field values
    mock_dynamodb.put_item.assert_called_once()
    args, kwargs = mock_dynamodb.put_item.call_args
    item = kwargs["Item"]
    assert item["user_id"]["S"] == user_sub
    assert item["claim_id"]["S"] == claim_id
    assert item["filename"]["S"] == filename
    assert item['client']["S"] == client


