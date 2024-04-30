import json
import uuid
import os
import boto3
from datetime import datetime

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
            'body': json.dumps('An error occurred while creating the prompt')
        }

    try:
        authorizer = event.get('requestContext', {}).get('authorizer')
        if not authorizer:
            return return_error()

        prompt_data = json.loads(event.get('body', '{}'))
        project_id = event.get('queryStringParameters', {}).get('projectId')
        if not project_id:
            print("No projectId provided")
            return return_error()

        prompt_id = str(uuid.uuid4())
        prompt_data['id'] = prompt_id
        entity_id = f"#USER{authorizer['claims']['sub']}#PROJECT{project_id}"
        entity_context_id = f"#PROJECT{project_id}#PROMPT{prompt_id}"

        item = {
            'entityId': entity_id,
            'entityContextId': entity_context_id,
            'prompt': prompt_data,
            'publicEntity': prompt_data.get('publicPrompt', False),
            'comments': []
        }

        table.put_item(Item=item)

        system_comment = {
            'user': 'SYSTEM',
            'date': datetime.now().isoformat(),
            'message': f"Prompt created by user {authorizer['claims']['cognito:username']}.",
            'version': 0
        }
        table.update_item(
            Key={'entityId': entity_id, 'entityContextId': entity_context_id},
            UpdateExpression='SET comments = list_append(comments, :comment)',
            ExpressionAttributeValues={':comment': [system_comment]}
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Prompt created successfully')
        }
    except Exception as e:
        print(f"Error: {e}")
        return return_error()