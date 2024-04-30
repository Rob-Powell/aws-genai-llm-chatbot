import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from genai_core.models import list_models

# Initialize DynamoDB and Bedrock clients
dynamodb = boto3.resource('dynamodb')
bedrock_client = boto3.client('bedrock', region_name='us-east-1')

# Get the DynamoDB table name from the environment variable
table_name = os.environ['DYNAMO_TABLE']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    def return_error():
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': 'An error occurred while reading the prompts'
        }

    def return_forbidden():
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': "You're trying to access a private prompt"
        }

    path_parameters = event.get('pathParameters')
    if not path_parameters or 'projectId' not in path_parameters or 'promptId' not in path_parameters:
        print("No projectId or promptId provided")
        return return_error()

    project_id = path_parameters['projectId']
    prompt_id = path_parameters['promptId']
    authorizer = event.get('requestContext', {}).get('authorizer')

    if not authorizer:
        return return_forbidden()


    get_prompt_details_query = {
        'KeyConditionExpression': Key('entityId').eq(f"#PROJECT#{project_id}#PROMPTDETAIL#{prompt_id}"),
        'IndexName': 'promptDetailVersionIndex',
        'ScanIndexForward': False,
        'TableName': table_name
    }

    get_private_prompt_query = {
        'KeyConditionExpression': Key('entityId').eq(f"#USER{user_id}#PROJECT{project_id}") & Key('entityContextId').eq(f"#PROJECT{project_id}#PROMPT{prompt_id}"),
        'TableName': table_name
    }

    get_public_prompt_query = {
        'KeyConditionExpression': Key('publicEntity').eq('PUBLIC_PROMPT') & Key('entityContextId').eq(f"#PROJECT{project_id}#PROMPT{prompt_id}"),
        'IndexName': 'publicEntityContextIndex',
        'ProjectionExpression': 'publicEntity, entityContextId',
        'TableName': table_name
    }

    try:
        prompt_response = table.query(**get_public_prompt_query)
        if not prompt_response['Items']:
            prompt_response = table.query(**get_private_prompt_query)
            if not prompt_response['Items']:
                return return_forbidden()

        prompt_details_response = table.query(**get_prompt_details_query)
        available_models = list_models()

        prompt_detail_dto = {
            'promptEntity': prompt_response['Items'][0],
            'promptDetailEntity': prompt_details_response['Items'],
            'models': available_models
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(prompt_detail_dto)
        }
    except Exception as e:
        print(f"Error: {e}")
        return return_error()
