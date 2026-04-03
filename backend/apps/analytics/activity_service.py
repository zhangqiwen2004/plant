from .models import UserActivity


def log_user_activity(user, action, target=None, extra_data=None):
    if not getattr(user, 'is_authenticated', False):
        return None

    return UserActivity.objects.create(
        user=user,
        action=action,
        target_type=target.__class__.__name__.lower() if target is not None else '',
        target_id=getattr(target, 'pk', None),
        extra_data=extra_data or {},
    )
