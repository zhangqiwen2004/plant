from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.models import User, UserTag, ExpertApplication
from apps.community.models import Topic


class Command(BaseCommand):
    help = '初始化用户和话题数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化用户和话题数据...')
        
        self.create_admin()
        self.create_experts()
        self.create_users()
        self.create_expert_applications()
        self.create_topics()
        
        self.stdout.write(self.style.SUCCESS('用户和话题数据初始化完成！'))

    def create_admin(self):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@plantcommunity.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'bio': '平台管理员',
            }
        )
        if created:
            admin.set_password('admin123456')
            admin.save()
            self.stdout.write('创建管理员账号: admin / admin123456')

    def create_experts(self):
        experts_data = [
            {
                'username': 'expert_succulent',
                'email': 'succulent@example.com',
                'bio': '多肉植物养护专家，10年养护经验，擅长景天科、仙人掌科植物',
                'experience_level': 'expert',
                'region': 'east',
                'expert_specialty': '多肉植物、仙人掌、景天科',
                'tags': [
                    ('plant_type', '多肉植物'),
                    ('plant_type', '仙人掌'),
                    ('interest', '多肉造景'),
                    ('care_environment', '阳台'),
                ]
            },
            {
                'username': 'expert_foliage',
                'email': 'foliage@example.com',
                'bio': '观叶植物达人，专注室内绿植养护，擅长解决黄叶、病虫害问题',
                'experience_level': 'expert',
                'region': 'south',
                'expert_specialty': '观叶植物、室内绿植、病虫害防治',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('plant_type', '蕨类植物'),
                    ('interest', '室内绿化'),
                    ('problem', '黄叶问题'),
                    ('problem', '病虫害'),
                ]
            },
            {
                'username': 'expert_flower',
                'email': 'flower@example.com',
                'bio': '花卉养护专家，擅长各类开花植物的养护和催花技巧',
                'experience_level': 'expert',
                'region': 'central',
                'expert_specialty': '开花植物、月季、兰花',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('plant_type', '月季'),
                    ('plant_type', '兰花'),
                    ('interest', '阳台花园'),
                ]
            },
            {
                'username': 'expert_herbs',
                'email': 'herbs@example.com',
                'bio': '香草种植专家，阳台和庭院种植8年经验，擅长食用香草和芳香植物',
                'experience_level': 'expert',
                'region': 'east',
                'expert_specialty': '香草植物、芳香植物、食用植物',
                'tags': [
                    ('plant_type', '香草植物'),
                    ('plant_type', '食用植物'),
                    ('interest', '阳台种菜'),
                    ('care_environment', '阳台'),
                    ('care_environment', '庭院'),
                ]
            },
            {
                'username': 'expert_hydro',
                'email': 'hydro@example.com',
                'bio': '水培技术专家，6年水培和半水培经验，擅长营养液配比和水培系统搭建',
                'experience_level': 'expert',
                'region': 'south',
                'expert_specialty': '水培技术、营养液配比、无土栽培',
                'tags': [
                    ('plant_type', '水培植物'),
                    ('interest', '水培技术'),
                    ('interest', '无土栽培'),
                    ('care_environment', '室内'),
                ]
            },
            {
                'username': 'expert_bonsai',
                'email': 'bonsai@example.com',
                'bio': '盆景艺术专家，15年盆景造型经验，擅长微型盆景和苔藓景观',
                'experience_level': 'expert',
                'region': 'east',
                'expert_specialty': '盆景艺术、微型盆景、苔藓景观',
                'tags': [
                    ('plant_type', '盆景植物'),
                    ('interest', '盆景造型'),
                    ('interest', '微景观'),
                    ('care_environment', '庭院'),
                ]
            },
            {
                'username': 'expert_pest',
                'email': 'pest@example.com',
                'bio': '植物病虫害防治专家，农学专业背景，擅长有机防治和综合管理',
                'experience_level': 'expert',
                'region': 'central',
                'expert_specialty': '病虫害防治、有机农业、植物诊断',
                'tags': [
                    ('problem', '病虫害'),
                    ('problem', '真菌感染'),
                    ('interest', '有机防治'),
                    ('interest', '植物诊断'),
                ]
            },
        ]
        
        for expert_data in experts_data:
            tags = expert_data.pop('tags')
            expert, created = User.objects.get_or_create(
                username=expert_data['username'],
                defaults={
                    **expert_data,
                    'role': 'expert',
                    'is_expert_verified': True,
                    'expert_apply_status': 'approved',
                }
            )
            if created:
                expert.set_password('expert123456')
                expert.save()
                
                for tag_type, tag_value in tags:
                    UserTag.objects.create(user=expert, tag_type=tag_type, tag_value=tag_value)
                
                self.stdout.write(f'创建达人账号: {expert.username}')

    def create_users(self):
        users_data = [
            {
                'username': 'plant_lover1',
                'email': 'lover1@example.com',
                'bio': '植物新手，刚开始养多肉，希望学习更多养护知识',
                'experience_level': 'beginner',
                'region': 'east',
                'tags': [
                    ('plant_type', '多肉植物'),
                    ('care_environment', '室内'),
                    ('problem', '浇水问题'),
                ]
            },
            {
                'username': 'green_thumb',
                'email': 'green@example.com',
                'bio': '养了3年绿植，家里有绿萝、吊兰、龟背竹等',
                'experience_level': 'intermediate',
                'region': 'north',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('plant_type', '藤蔓植物'),
                    ('care_environment', '室内'),
                    ('interest', '空气净化'),
                ]
            },
            {
                'username': 'balcony_garden',
                'email': 'balcony@example.com',
                'bio': '阳台党，喜欢在阳台种花种菜',
                'experience_level': 'intermediate',
                'region': 'south',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('plant_type', '香草植物'),
                    ('care_environment', '阳台'),
                    ('interest', '阳台花园'),
                ]
            },
            {
                'username': 'succulent_fan',
                'email': 'succulent@example.com',
                'bio': '多肉爱好者，收集了100多种多肉',
                'experience_level': 'advanced',
                'region': 'east',
                'tags': [
                    ('plant_type', '多肉植物'),
                    ('plant_type', '仙人掌'),
                    ('care_environment', '阳台'),
                    ('interest', '多肉造景'),
                    ('interest', '品种收集'),
                ]
            },
            {
                'username': 'office_plant',
                'email': 'office@example.com',
                'bio': '办公室养植物，想找些好养的桌面绿植',
                'experience_level': 'beginner',
                'region': 'central',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('care_environment', '办公室'),
                    ('problem', '光照不足'),
                ]
            },
            {
                'username': 'herb_garden',
                'email': 'herb@example.com',
                'bio': '阳台香草种植爱好者，薄荷、罗勒、迷迭香养了一整排',
                'experience_level': 'intermediate',
                'region': 'north',
                'tags': [
                    ('plant_type', '香草植物'),
                    ('care_environment', '阳台'),
                    ('interest', '食用植物'),
                ]
            },
            {
                'username': 'fern_lover',
                'email': 'fern@example.com',
                'bio': '热带雨林风格爱好者，家里养了各种蕨类和天南星科',
                'experience_level': 'intermediate',
                'region': 'south',
                'tags': [
                    ('plant_type', '蕨类植物'),
                    ('plant_type', '观叶植物'),
                    ('care_environment', '室内'),
                    ('interest', '雨林造景'),
                ]
            },
            {
                'username': 'flower_mama',
                'email': 'flowermama@example.com',
                'bio': '带娃之余养花，阳台上种了绣球和月季',
                'experience_level': 'beginner',
                'region': 'central',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('care_environment', '阳台'),
                    ('problem', '花期管理'),
                ]
            },
            {
                'username': 'weekend_gardener',
                'email': 'weekend@example.com',
                'bio': '周末才有时间打理植物，偏爱耐旱好养的品种',
                'experience_level': 'advanced',
                'region': 'east',
                'tags': [
                    ('plant_type', '多肉植物'),
                    ('plant_type', '仙人掌'),
                    ('care_environment', '阳台'),
                    ('interest', '盆景造型'),
                ]
            },
            {
                'username': 'cactus_king',
                'email': 'cactus@example.com',
                'bio': '仙人掌和多肉的忠实粉丝，阳台全是刺',
                'experience_level': 'intermediate',
                'region': 'north',
                'tags': [
                    ('plant_type', '仙人掌'),
                    ('plant_type', '多肉植物'),
                    ('care_environment', '阳台'),
                    ('interest', '品种收集'),
                ]
            },
            {
                'username': 'tropical_fan',
                'email': 'tropical@example.com',
                'bio': '热带植物控，家里温度常年25度以上，养了不少天南星科',
                'experience_level': 'intermediate',
                'region': 'south',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('plant_type', '藤蔓植物'),
                    ('care_environment', '室内'),
                    ('interest', '雨林造景'),
                    ('problem', '湿度控制'),
                ]
            },
            {
                'username': 'garden_dad',
                'email': 'gardendad@example.com',
                'bio': '有个小院子，带孩子一起种菜种花',
                'experience_level': 'intermediate',
                'region': 'north',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('plant_type', '香草植物'),
                    ('care_environment', '庭院'),
                    ('interest', '亲子种植'),
                ]
            },
            {
                'username': 'tiny_garden',
                'email': 'tiny@example.com',
                'bio': '微型盆景爱好者，喜欢在小空间里做出大景观',
                'experience_level': 'advanced',
                'region': 'east',
                'tags': [
                    ('plant_type', '多肉植物'),
                    ('plant_type', '蕨类植物'),
                    ('care_environment', '室内'),
                    ('interest', '盆景造型'),
                    ('interest', '微景观'),
                ]
            },
            {
                'username': 'water_garden',
                'email': 'water@example.com',
                'bio': '水培养护达人，家里十几个水培瓶',
                'experience_level': 'advanced',
                'region': 'east',
                'tags': [
                    ('plant_type', '水培植物'),
                    ('plant_type', '观叶植物'),
                    ('care_environment', '室内'),
                    ('interest', '水培实验'),
                ]
            },
            {
                'username': 'night_grower',
                'email': 'night@example.com',
                'bio': '上夜班的植物爱好者，白天睡觉时植物陪着我',
                'experience_level': 'beginner',
                'region': 'central',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('care_environment', '室内'),
                    ('problem', '光照不足'),
                    ('problem', '浇水问题'),
                ]
            },
            {
                'username': 'rooftop_girl',
                'email': 'rooftop@example.com',
                'bio': '天台花园主人，几十平的天台变成了小花园',
                'experience_level': 'advanced',
                'region': 'south',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('plant_type', '藤蔓植物'),
                    ('care_environment', '天台'),
                    ('interest', '造景设计'),
                ]
            },
            {
                'username': 'plant_doctor',
                'email': 'doctor@example.com',
                'bio': '喜欢研究植物病害，经常帮邻居诊断植物问题',
                'experience_level': 'advanced',
                'region': 'north',
                'tags': [
                    ('plant_type', '观叶植物'),
                    ('plant_type', '开花植物'),
                    ('interest', '病虫害研究'),
                    ('problem', '病虫害'),
                    ('problem', '黄叶问题'),
                ]
            },
            {
                'username': 'orchid_lover',
                'email': 'orchid@example.com',
                'bio': '兰花爱好者，养了十几盆蝴蝶兰和国兰',
                'experience_level': 'intermediate',
                'region': 'south',
                'tags': [
                    ('plant_type', '开花植物'),
                    ('care_environment', '室内'),
                    ('interest', '品种收集'),
                ]
            },
        ]
        
        for user_data in users_data:
            tags = user_data.pop('tags')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={**user_data, 'role': 'user'}
            )
            if created:
                user.set_password('user123456')
                user.save()
                
                for tag_type, tag_value in tags:
                    UserTag.objects.create(user=user, tag_type=tag_type, tag_value=tag_value)
                
                self.stdout.write(f'创建用户账号: {user.username}')

    def create_expert_applications(self):
        admin = User.objects.filter(username='admin').first()
        if not admin:
            self.stdout.write(self.style.WARNING('未找到管理员账号，跳过达人申请初始化'))
            return

        # 为直接创建的达人用户补充申请记录（已通过）
        expert_users = User.objects.filter(role='expert', is_expert_verified=True).exclude(
            id__in=ExpertApplication.objects.values_list('user_id', flat=True)
        )
        for expert in expert_users:
            ExpertApplication.objects.create(
                user=expert,
                specialty=expert.expert_specialty or '综合植物养护',
                experience_desc=expert.bio or '资深植物养护达人',
                status='approved',
                reviewer=admin,
                review_comment='种子数据导入，直接通过认证',
                reviewed_at=timezone.now() - timedelta(days=7),
            )
            self.stdout.write(f'补充达人申请: {expert.username} (已通过)')

        application_data = [
            {
                'username': 'rooftop_girl',
                'specialty': '天台花园造景、铁线莲与月季盆栽管理',
                'experience_desc': '有多年天台盆栽与立体花园实践经验，擅长高光照环境下的开花植物配置、修剪和季节轮换。',
                'status': 'pending',
                'review_comment': '',
                'reviewed_at': None,
            },
            {
                'username': 'water_garden',
                'specialty': '水培植物、水培营养液与遮光控藻',
                'experience_desc': '长期维护家庭水培系统，熟悉绿萝、铜钱草、白掌等常见水培植物的换水、控藻和营养液管理。',
                'status': 'pending',
                'review_comment': '',
                'reviewed_at': None,
            },
            {
                'username': 'plant_doctor',
                'specialty': '病虫害识别、观叶植物诊断、家庭应急处理',
                'experience_desc': '经常为邻里和社群成员诊断植物问题，能够结合黄叶、虫咬、真菌感染等现象给出处理建议。',
                'status': 'approved',
                'review_comment': '养护经验清晰，擅长领域明确，符合达人认证要求。',
                'reviewed_at': timezone.now() - timedelta(days=2),
            },
            {
                'username': 'night_grower',
                'specialty': '弱光环境植物养护、补光灯使用',
                'experience_desc': '主要在室内与夜班生活场景下养护植物，积累了一些弱光和补光经验，但案例材料较少。',
                'status': 'rejected',
                'review_comment': '当前案例与经验描述仍偏少，建议补充更完整的养护案例后再次申请。',
                'reviewed_at': timezone.now() - timedelta(days=1),
            },
        ]

        for item in application_data:
            user = User.objects.filter(username=item['username']).first()
            if not user:
                self.stdout.write(self.style.WARNING(f"未找到用户 {item['username']}，跳过申请初始化"))
                continue

            if ExpertApplication.objects.filter(user=user).exists():
                continue

            application = ExpertApplication.objects.create(
                user=user,
                specialty=item['specialty'],
                experience_desc=item['experience_desc'],
                status=item['status'],
                review_comment=item['review_comment'],
                reviewer=admin if item['status'] != 'pending' else None,
                reviewed_at=item['reviewed_at'],
            )

            update_fields = ['expert_apply_status']
            if item['status'] == 'approved':
                user.role = 'expert'
                user.is_expert_verified = True
                user.expert_apply_status = 'approved'
                user.expert_specialty = item['specialty']
                update_fields.extend(['role', 'is_expert_verified', 'expert_specialty'])
            elif item['status'] == 'rejected':
                user.expert_apply_status = 'rejected'
            else:
                user.expert_apply_status = 'pending'

            user.save(update_fields=update_fields)
            self.stdout.write(f'创建达人申请: {application.user.username} ({application.get_status_display()})')

    def create_topics(self):
        topics = [
            {'name': '多肉养护', 'description': '多肉植物养护技巧、品种分享、造景交流'},
            {'name': '观叶植物', 'description': '绿萝、龟背竹、虎皮兰等观叶植物养护交流'},
            {'name': '开花植物', 'description': '月季、绣球、长寿花等开花植物养护分享'},
            {'name': '新手入门', 'description': '植物养护新手问答、入门知识分享'},
            {'name': '病虫害防治', 'description': '植物病虫害识别与防治方法'},
            {'name': '阳台花园', 'description': '阳台种植、空间利用、造景分享'},
            {'name': '水培养护', 'description': '水培植物养护技巧与经验分享'},
            {'name': '香草种植', 'description': '薄荷、罗勒等香草植物种植交流'},
            {'name': '植物摄影', 'description': '分享你的植物美照'},
            {'name': '二手交换', 'description': '植物、花盆、工具交换与赠送'},
        ]
        
        for topic_data in topics:
            Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
        
        self.stdout.write(f'创建了 {len(topics)} 个话题圈')
