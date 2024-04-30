import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMO_TABLE'])

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

    if 'queryStringParameters' not in event or 'projectId' not in event['queryStringParameters']:
        print("No projectId provided")
        return return_error()

    project_id = event['queryStringParameters']['projectId']
    authorizer = event['requestContext']['authorizer']

    # Query for public prompts
    public_prompts_query = table.query(
        IndexName='publicEntityContextIndex',
        KeyConditionExpression=Key('publicEntity').eq('PUBLIC_PROMPT') & Key('entityContextId').begins_with('#PROJECT{}#PROMPT'.format(project_id)),
        ProjectionExpression='#publicEntity, #entityContextId',
        ExpressionAttributeNames={
            '#publicEntity': 'publicEntity',
            '#entityContextId': 'entityContextId'
        }
    )

    # Query for user prompts
    user_prompts_query = table.query(
        IndexName='publicEntityIndex',
        KeyConditionExpression=Key('publicEntity').eq(' ') & Key('entityId').eq('#USER{}#PROJECT{}'.format(authorizer['claims']['sub'], project_id)),
        ProjectionExpression='#entityId, #publicEntity',
        ExpressionAttributeNames={
            '#entityId': 'entityId',
            '#publicEntity': 'publicEntity'
        }
    )

    try:
        prompt_entity_list = public_prompts_query['Items'] + user_prompts_query['Items']
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(prompt_entity_list)
        }
    except Exception as e:
        print("Error:", e)
        return return_error()