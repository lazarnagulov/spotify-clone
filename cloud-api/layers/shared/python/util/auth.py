from functools import wraps

def require_role(*allowed_groups):
    def decorator(func):
        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
            groups = claims.get("cognito:groups", [])

            if isinstance(groups, str):
                groups = [groups]

            if not any(group in allowed_groups for group in groups):
                raise PermissionError(f"Access denied. Required: {allowed_groups}, got: {groups}")

            return func(event, context, *args, **kwargs)
        return wrapper
    return decorator
