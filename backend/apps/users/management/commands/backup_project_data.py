from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.utils import timezone


CORE_APP_LABELS = ['users', 'plants', 'community', 'matching', 'analytics']


class Command(BaseCommand):
    help = '备份项目核心数据到 JSON 文件'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='')
        parser.add_argument('--indent', type=int, default=2)

    def handle(self, *args, **options):
        backup_dir = Path(options['output']) if options['output'] else Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)

        filename = f"plant_community_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = backup_dir / filename

        with output_path.open('w', encoding='utf-8') as output_file:
            call_command(
                'dumpdata',
                *CORE_APP_LABELS,
                indent=options['indent'],
                stdout=output_file,
            )

        self.stdout.write(self.style.SUCCESS(f'备份完成：{output_path}'))
