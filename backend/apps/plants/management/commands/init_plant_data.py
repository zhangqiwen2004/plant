from datetime import date, timedelta

from django.core.management.base import BaseCommand
from apps.plants.models import PlantCategory, Plant, PlantTag, PlantTagRelation, UserPlant, CareRecord
from apps.plants.seed_data import CATEGORY_DEFS, PLANT_CATALOG, TAG_DEFS, USER_PLANT_SEEDS, CARE_RECORD_SEEDS
from apps.users.models import User


class Command(BaseCommand):
    help = '初始化植物养护数据'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true')

    def handle(self, *args, **options):
        refresh = options['refresh']
        self.stdout.write('开始初始化植物数据...')

        self.create_categories(refresh=refresh)
        self.create_tags(refresh=refresh)
        created_count, updated_count, skipped_count = self.create_plants(refresh=refresh)
        user_plant_count = self.create_user_plants()
        care_record_count = self.create_care_records()

        self.stdout.write(
            self.style.SUCCESS(
                f'植物数据初始化完成！created={created_count}, updated={updated_count}, skipped={skipped_count},'
                f' user_plants={user_plant_count}, care_records={care_record_count}'
            )
        )

    def create_categories(self, refresh=False):
        created_count = 0
        updated_count = 0

        for category_data in CATEGORY_DEFS:
            category, created = PlantCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data,
            )
            if created:
                created_count += 1
                continue

            if self.update_object(category, category_data, refresh=refresh):
                updated_count += 1

        self.stdout.write(f'分类完成：created={created_count}, updated={updated_count}')

    def create_tags(self, refresh=False):
        created_count = 0
        updated_count = 0

        for name, color in TAG_DEFS.items():
            tag, created = PlantTag.objects.get_or_create(
                name=name,
                defaults={'color': color},
            )
            if created:
                created_count += 1
                continue

            if refresh and tag.color != color:
                tag.color = color
                tag.save(update_fields=['color'])
                updated_count += 1

        self.stdout.write(f'标签完成：created={created_count}, updated={updated_count}')

    def create_plants(self, refresh=False):
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in PLANT_CATALOG:
            _, action = self.save_plant(item, refresh=refresh)
            if action == 'created':
                created_count += 1
            elif action == 'updated':
                updated_count += 1
            else:
                skipped_count += 1

        self.stdout.write(
            f'植物完成：created={created_count}, updated={updated_count}, skipped={skipped_count}'
        )
        return created_count, updated_count, skipped_count

    def save_plant(self, item, refresh=False):
        category = PlantCategory.objects.get(name=item['category'])
        defaults = {
            'scientific_name': item['scientific_name'],
            'alias': item['alias'],
            'category': category,
            'description': item['summary'],
            'difficulty': item['difficulty'],
            'light_requirement': item['light_requirement'],
            'water_requirement': item['water_requirement'],
            'temperature_min': item['temperature_min'],
            'temperature_max': item['temperature_max'],
            'humidity': item['humidity'],
            'soil_requirement': item['soil_requirement'],
            'fertilizer_tips': item['fertilizer_tips'],
            'pruning_tips': item['pruning_tips'],
            'propagation': item['propagation'],
            'common_problems': item['common_problems'],
            'care_tips': item['care_tips'],
            'is_active': True,
        }

        plant = Plant.objects.filter(name=item['name']).first()
        if plant is None:
            plant = Plant.objects.create(name=item['name'], **defaults)
            action = 'created'
        else:
            changed = self.update_existing_plant(plant, defaults, refresh=refresh)
            action = 'updated' if changed else 'skipped'

        self.sync_tags(plant, item['tags'], refresh=refresh)
        return plant, action

    def update_existing_plant(self, plant, defaults, refresh=False):
        changed = False

        for field, value in defaults.items():
            if field == 'category':
                current_value = plant.category_id
                target_value = value.id if value else None
                if refresh:
                    if current_value != target_value:
                        plant.category = value
                        changed = True
                else:
                    if current_value is None and target_value is not None:
                        plant.category = value
                        changed = True
                continue

            current_value = getattr(plant, field)
            if refresh:
                if current_value != value:
                    setattr(plant, field, value)
                    changed = True
            else:
                if current_value in [None, ''] and value not in [None, '']:
                    setattr(plant, field, value)
                    changed = True

        if changed:
            plant.save()

        return changed

    def update_object(self, instance, defaults, refresh=False):
        changed = False
        for field, value in defaults.items():
            if field == 'name':
                continue
            current_value = getattr(instance, field)
            if refresh:
                if current_value != value:
                    setattr(instance, field, value)
                    changed = True
            else:
                if current_value in [None, ''] and value not in [None, '']:
                    setattr(instance, field, value)
                    changed = True

        if changed:
            instance.save()

        return changed

    def sync_tags(self, plant, tag_names, refresh=False):
        current_names = set(
            plant.tag_relations.select_related('tag').values_list('tag__name', flat=True)
        )

        for tag in PlantTag.objects.filter(name__in=tag_names):
            if tag.name not in current_names:
                PlantTagRelation.objects.get_or_create(plant=plant, tag=tag)

        if refresh:
            plant.tag_relations.exclude(tag__name__in=tag_names).delete()

    def create_user_plants(self):
        created_count = 0
        users = {u.username: u for u in User.objects.all()}
        plants = {p.name: p for p in Plant.objects.all()}

        for item in USER_PLANT_SEEDS:
            user = users.get(item['user'])
            plant = plants.get(item['plant'])
            if not user or not plant:
                continue

            acquired_date = date.today() - timedelta(days=item['days_ago']) if item.get('days_ago') else None
            _, created = UserPlant.objects.get_or_create(
                user=user,
                plant=plant,
                defaults={
                    'nickname': item.get('nickname', ''),
                    'notes': item.get('notes', ''),
                    'acquired_date': acquired_date,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(f'用户植物收藏完成：created={created_count}')
        return created_count

    def create_care_records(self):
        created_count = 0
        users = {u.username: u for u in User.objects.all()}

        for item in CARE_RECORD_SEEDS:
            user = users.get(item['user'])
            if not user:
                continue

            user_plant = UserPlant.objects.filter(
                user=user,
                plant__name=item['plant'],
            ).first()
            if not user_plant:
                continue

            care_date = date.today() - timedelta(days=item['days_ago'])
            _, created = CareRecord.objects.get_or_create(
                user=user,
                user_plant=user_plant,
                care_type=item['care_type'],
                care_date=care_date,
                defaults={
                    'description': item.get('description', ''),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(f'养护记录完成：created={created_count}')
        return created_count
