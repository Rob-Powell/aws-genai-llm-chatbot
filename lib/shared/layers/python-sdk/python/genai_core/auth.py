from functools import wraps


def get_user_id(router):
    user_id = router.current_event.get("identity", {}).get("sub")

    return user_id


class UserPermissions:
    """Responsible for validating the user's permissions for API calls
    Args:
        router (aws_lambda_powertools.event_handler.api_gateway.Router): The lambda powertools router defined for the API endpoints
    Valid Roles:
        - `ADMIN_ROLE` = `chatbot_admin`
        - `WORKSPACES_MANAGER_ROLE` = `chatbot_workspaces_manager`
        - `WORKSPACES_USER_ROLE` = `chatbot_workspaces_user`
        - `CHATBOT_USER_ROLE` = `chatbot_user`
    """

    ADMIN_ROLE = "chatbot_admin"
    WORKSPACES_MANAGER_ROLE = "chatbot_workspaces_manager"
    WORKSPACES_USER_ROLE = "chatbot_workspaces_user"
    CHATBOT_USER_ROLE = "chatbot_user"

    VALID_ROLES = [
        ADMIN_ROLE,
        WORKSPACES_MANAGER_ROLE,
        WORKSPACES_USER_ROLE,
        CHATBOT_USER_ROLE,
    ]

    def __init__(self, router):
        self.router = router

    def __get_user_role(self, group_name=None):
        user_groups = (
            self.router.current_event.get("identity", {})
            .get("claims")
            .get("cognito:groups")
        )
        if user_groups is not None and len(user_groups) > 0:
            if group_name and group_name in user_groups:
                return group_name
            if self.ADMIN_ROLE in user_groups:
                return self.ADMIN_ROLE
            elif self.WORKSPACES_MANAGER_ROLE in user_groups:
                return self.WORKSPACES_MANAGER_ROLE
            elif self.WORKSPACES_USER_ROLE in user_groups:
                return self.WORKSPACES_USER_ROLE
            elif self.CHATBOT_USER_ROLE in user_groups:
                return self.CHATBOT_USER_ROLE
            else:
                return None

    def approved_roles(self, roles: []):
        """Validates the user calling the endpoint
        has a user role set that is approved for the endpoint
        Args:
            roles (list): list of roles that are approved for the endpoint
        Valid Roles:
            - `ADMIN_ROLE` = `chatbot_admin`
            - `WORKSPACES_MANAGER_ROLE` = `chatbot_workspaces_manager`
            - `WORKSPACES_USER_ROLE` = `chatbot_workspaces_user`
            - `CHATBOT_USER_ROLE` = `chatbot_user`
        Returns:
            function: If the user is approved, the function being called will be returned for execution
            dict: If the user is not approved, a response of `{"ok": False, "error": "Unauthorized"}` will be returned
            as the response.
        Examples:
        ```
            from aws_lambda_powertools.event_handler.api_gateway import Router
            from genai_core.auth import UserPermissions
            router = Router()
            permissions = UserPermissions(router)
            @router.get("/sample/endpoint")
            @permissions.approved_roles(
                [
                    permissions.ADMIN_ROLE,
                    permissions.WORKSPACES_MANAGER_ROLE
                ]
            )
            def sample_endpoint():
                pass
        ```
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kargs):
                user_role = self.__get_user_role()
                if user_role in roles:
                    return func(*args, **kargs)
                else:
                    return {"error": "Unauthorized"}

            return wrapper

        return decorator

    def admin_only(self, func):
        """Validates the user calling the endpoint is an admin
        and returns the function being called for execution
        Returns:
            function: If the user is an admin, the function being called will be returned for execution
            dict: If the user is not an admin, a response of `{"ok": False, "error": "Unauthorized"}` will be returned
            as the response.
        """
        return self.approved_roles([self.ADMIN_ROLE])(func)

    def workspace_group_member(self):
        """Validates the user calling the endpoint is a member of the specified workspace group
        Returns:
            function: If the user is a member of the group, the function being called will be returned for execution
            dict: If the user is not a member of the group, a response of `{"error": "Workspace Unauthorized"}` will be returned
            as the response.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kargs):
                workspace_id = getattr(func, 'workspaceId', None)
                if workspace_id is None:
                    workspace_id = kargs.get('workspaceId')
                if workspace_id is None:
                    if len(args) > 0 and isinstance(args[0], dict):
                        workspace_id = args[0].get('workspaceId')
                if workspace_id is None:
                    raise genai_core.types.CommonError("Missing workspaceId")

                user_role = self.__get_user_role(f"workspace-{workspace_id}")
                if user_role == f"workspace-{workspace_id}":
                    return func(*args, **kargs)
                else:
                    return {"error": "Workspace Unauthorized"}

            return wrapper

        return decorator