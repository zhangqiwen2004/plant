from datetime import date, timedelta, datetime, timezone as dt_timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.models import User
from apps.analytics.models import DailyStatistics, UserActivity
from apps.analytics.seed_data import DAILY_STATISTICS_SEEDS, USER_ACTIVITY_SEEDS


class Command(BaseCommand):
    help = '初始化数据分析种子数据（每日统计 + 用户活动）'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true', help='清空旧数据后重新导入')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['refresh']:
            DailyStatistics.objects.all().delete()
            UserActivity.objects.all().delete()
            self.stdout.write('[OK] 已清空旧分析数据')

        self.seed_daily_statistics()
        self.seed_user_activities()
        self.stdout.write(self.style.SUCCESS('[OK] 分析数据初始化完成'))

    def seed_daily_statistics(self):
        today = date.today()
        created = 0
        for item in DAILY_STATISTICS_SEEDS:
            stat_date = today - timedelta(days=item['days_ago'])
            _, is_new = DailyStatistics.objects.get_or_create(
                date=stat_date,
                defaults={
                    'new_users': item['new_users'],
                    'active_users': item['active_users'],
                    'total_users': item['total_users'],
                    'new_posts': item['new_posts'],
                    'new_questions': item['new_questions'],
                    'new_answers': item['new_answers'],
                    'new_comments': item['new_comments'],
                    'total_interactions': item['total_interactions'],
                    'match_count': item['match_count'],
                    'match_success_count': item['match_success_count'],
                },
            )
            if is_new:
                created += 1
        self.stdout.write(f'  每日统计: 新增 {created} 条, 共 {len(DAILY_STATISTICS_SEEDS)} 条')

    def seed_user_activities(self):
        users = {u.username: u for u in User.objects.all()}
        created = 0
        skipped_users = set()
        now = datetime.now(dt_timezone.utc)

        for item in USER_ACTIVITY_SEEDS:
            username = item['user']
            if username not in users:
                skipped_users.add(username)
                continue
            activity_time = now - timedelta(days=item['days_ago'], hours=item.get('hours_ago', 0))
            UserActivity.objects.create(
                user=users[username],
                action=item['action'],
                target_type=item.get('target_type', ''),
                target_id=None,
                extra_data={},
                created_at=activity_time,
            )
            created += 1
        if skipped_users:
            self.stdout.write(f'  [WARN] 跳过不存在的用户: {", ".join(sorted(skipped_users))}')
        self.stdout.write(f'  用户活动: 新增 {created} 条')
