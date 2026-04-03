from django.db.models import NOT_PROVIDED
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.constants import TREND_PRESETS
from apps.analytics.models import UserActivity
from apps.community.models import Post, Question
from apps.matching.constants import MATCH_MODE_OPTIONS
from apps.matching.models import MatchRecord, MatchRequest
from apps.plants.models import Plant, CareRecord
from apps.users.constants import TAG_OPTION_GROUPS
from apps.users.models import ExpertApplication, Notification, User, UserTag


def serialize_choices(choices):
    return [{'value': value, 'label': label} for value, label in choices]


def get_field_default(model, field_name, fallback=''):
    field = model._meta.get_field(field_name)
    return fallback if field.default is NOT_PROVIDED else field.default


class MetadataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'users': {
                'roles': serialize_choices(User.ROLE_CHOICES),
                'experience_levels': serialize_choices(User.EXPERIENCE_CHOICES),
                'regions': serialize_choices(User.REGION_CHOICES),
                'tag_types': serialize_choices(UserTag.TAG_TYPE_CHOICES),
                'tag_option_groups': TAG_OPTION_GROUPS,
                'expert_application_statuses': serialize_choices(ExpertApplication.STATUS_CHOICES),
                'notification_types': serialize_choices(Notification.TYPE_CHOICES),
                'defaults': {
                    'experience_level': get_field_default(User, 'experience_level', 'beginner'),
                    'region': get_field_default(User, 'region', ''),
                },
            },
            'community': {
                'post_statuses': serialize_choices(Post.STATUS_CHOICES),
                'question_statuses': serialize_choices(Question.STATUS_CHOICES),
            },
            'plants': {
                'difficulties': serialize_choices(Plant.DIFFICULTY_CHOICES),
                'light_requirements': serialize_choices(Plant.LIGHT_CHOICES),
                'water_requirements': serialize_choices(Plant.WATER_CHOICES),
                'care_types': serialize_choices(CareRecord.CARE_TYPE_CHOICES),
            },
            'matching': {
                'match_record_types': serialize_choices(MatchRecord.MATCH_TYPE_CHOICES),
                'request_statuses': serialize_choices(MatchRequest.STATUS_CHOICES),
                'match_modes': MATCH_MODE_OPTIONS,
            },
            'analytics': {
                'activity_actions': serialize_choices(UserActivity.ACTION_CHOICES),
                'trend_presets': TREND_PRESETS,
            },
        })
