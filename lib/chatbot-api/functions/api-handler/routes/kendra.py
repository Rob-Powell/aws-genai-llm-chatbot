from common.validation import WorkspaceIdValidation
import genai_core.parameters
import genai_core.kendra
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from genai_core.auth import UserPermissions


tracer = Tracer()
router = Router()
logger = Logger()
permissions = UserPermissions(router)


@router.resolver(field_name="listKendraIndexes")
@tracer.capture_method
@permissions.approved_roles(
    [
        permissions.ADMIN_ROLE,
        permissions.WORKSPACES_MANAGER_ROLE,
        permissions.WORKSPACES_USER_ROLE,
    ]
)
def kendra_indexes():
    indexes = genai_core.kendra.get_kendra_indexes()

    return indexes


@router.resolver(field_name="startKendraDataSync")
@tracer.capture_method
@permissions.approved_roles(
    [permissions.ADMIN_ROLE, permissions.WORKSPACES_MANAGER_ROLE]
)
def kendra_data_sync(workspaceId: str):
    WorkspaceIdValidation(**{"workspaceId": workspaceId})
    genai_core.kendra.start_kendra_data_sync(workspace_id=workspaceId)

    return True


@router.resolver(field_name="isKendraDataSynching")
@tracer.capture_method
@permissions.approved_roles(
    [permissions.ADMIN_ROLE, permissions.WORKSPACES_MANAGER_ROLE]
)
def kendra_is_syncing(workspaceId: str):
    WorkspaceIdValidation(**{"workspaceId": workspaceId})
    result = genai_core.kendra.kendra_is_syncing(workspace_id=workspaceId)

    return result
