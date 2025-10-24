from functools import wraps


def require_role(*allowed_groups):
    def decorator(func):
        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
            groups_raw = claims.get("cognito:groups", [])

            groups = []
            if isinstance(groups_raw, list):
                for item in groups_raw:
                    groups.extend([g.strip() for g in str(item).split(',')])
            else:
                groups = [g.strip() for g in str(groups_raw).split(',')]

            groups = [g for g in groups if g]

            if not any(group in allowed_groups for group in groups):
                raise PermissionError(f"Access denied. Required: {allowed_groups}, got: {groups}")

            return func(event, context, *args, **kwargs)

        return wrapper

    return decorator
