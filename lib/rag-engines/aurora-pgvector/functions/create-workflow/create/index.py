import genai_core.workspaces
import genai_core.aurora.create
import genai_core.admin_user_management
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context: LambdaContext):
    workspace_id = event["workspace_id"]
    logger.info(f"Creating workspace {workspace_id}")

    workspace = genai_core.workspaces.get_workspace(workspace_id)
    if not workspace:
        raise Exception(f"Workspace {workspace_id} does not exist")

    genai_core.admin_user_management.create_cognito_group(f"workspace-{workspace_id}")
    genai_core.aurora.create.create_workspace_table(workspace)

    return {"ok": True}
