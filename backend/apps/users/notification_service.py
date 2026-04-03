from django.conf import settings
from django.core.mail import send_mail

from .models import Notification, NotificationPreference


TYPE_FIELD_MAP = {
    'match': 'receive_match',
    'answer': 'receive_answer',
    'system': 'receive_system',
    'interaction': 'receive_interaction',
}


def get_notification_preference(user):
    preference, _ = NotificationPreference.objects.get_or_create(user=user)
    return preference


def _allows_channel(preference, notification_type, channel):
    field_name = TYPE_FIELD_MAP.get(notification_type)
    if field_name and not getattr(preference, field_name, True):
        return False
    if channel == 'in_app':
        return preference.in_app_enabled
    if channel == 'email':
        return preference.email_enabled
    return False


def build_related_link(related_url=''):
    if not related_url:
        return ''
    if related_url.startswith('http://') or related_url.startswith('https://'):
        return related_url
    return f"{settings.FRONTEND_BASE_URL.rstrip('/')}/{related_url.lstrip('/')}"


def send_user_notification(user, notification_type, title, content, related_url=''):
    preference = get_notification_preference(user)
    notification = None
    full_link = build_related_link(related_url)

    if _allows_channel(preference, notification_type, 'in_app'):
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            content=content,
            related_url=related_url,
        )

    if _allows_channel(preference, notification_type, 'email') and user.email:
        body = content if not full_link else f"{content}\n\n查看详情：{full_link}"
        send_mail(
            subject=title,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    return notification
