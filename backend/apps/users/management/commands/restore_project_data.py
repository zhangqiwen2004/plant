from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction


CLEAR_ORDER = [
    'analytics.UserActivity',
    'analytics.DailyStatistics',
    'matching.MatchRequest',
    'matching.MatchRecord',
    'matching.TagWeight',
    'community.AnswerLike',
    'community.Answer',
    'community.QuestionImage',
    'community.Question',
    'community.CommentLike',
    'community.Comment',
    'community.PostLike',
    'community.PostImage',
    'community.Post',
    'community.TopicFollow',
    'community.Topic',
    'plants.CareRecord',
    'plants.UserPlant',
    'plants.PlantTagRelation',
    'plants.PlantTag',
    'plants.Plant',
    'plants.PlantCategory',
    'users.Notification',
    'users.ExpertApplication',
    'users.NotificationPreference',
    'users.UserTag',
    'users.User',
]


class Command(BaseCommand):
    help = '从 JSON 文件恢复项目核心数据'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True)
        parser.add_argument('--replace', action='store_true')

    def handle(self, *args, **options):
        input_path = Path(options['input'])
        if not input_path.is_absolute():
            input_path = Path(settings.BASE_DIR) / input_path
        if not input_path.exists():
            raise CommandError(f'备份文件不存在：{input_path}')

        with transaction.atomic():
            if options['replace']:
                self._clear_existing_data()
            call_command('loaddata', str(input_path))

        self.stdout.write(self.style.SUCCESS(f'恢复完成：{input_path}'))

    def _clear_existing_data(self):
        for model_label in CLEAR_ORDER:
            model = apps.get_model(model_label)
            model.objects.all().delete()
