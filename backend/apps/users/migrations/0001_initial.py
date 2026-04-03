

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "管理员"),
                            ("expert", "养护达人"),
                            ("user", "普通用户"),
                        ],
                        default="user",
                        max_length=20,
                        verbose_name="角色",
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True, null=True, upload_to="avatars/", verbose_name="头像"
                    ),
                ),
                (
                    "bio",
                    models.TextField(blank=True, max_length=500, verbose_name="个人简介"),
                ),
                (
                    "experience_level",
                    models.CharField(
                        choices=[
                            ("beginner", "新手"),
                            ("intermediate", "有一定经验"),
                            ("advanced", "资深玩家"),
                            ("expert", "专业级"),
                        ],
                        default="beginner",
                        max_length=20,
                        verbose_name="养护经验等级",
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("north", "华北"),
                            ("northeast", "东北"),
                            ("east", "华东"),
                            ("central", "华中"),
                            ("south", "华南"),
                            ("southwest", "西南"),
                            ("northwest", "西北"),
                        ],
                        max_length=20,
                        verbose_name="所在地区",
                    ),
                ),
                (
                    "is_expert_verified",
                    models.BooleanField(default=False, verbose_name="达人认证状态"),
                ),
                (
                    "expert_apply_status",
                    models.CharField(
                        choices=[
                            ("none", "未申请"),
                            ("pending", "审核中"),
                            ("approved", "已通过"),
                            ("rejected", "已拒绝"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="达人申请状态",
                    ),
                ),
                ("expert_specialty", models.TextField(blank=True, verbose_name="擅长领域")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "用户",
                "verbose_name_plural": "用户",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="ExpertApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("specialty", models.TextField(verbose_name="擅长领域")),
                ("experience_desc", models.TextField(verbose_name="养护经验描述")),
                (
                    "certification",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="certifications/",
                        verbose_name="资质证明",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "审核中"),
                            ("approved", "已通过"),
                            ("rejected", "已拒绝"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="审核状态",
                    ),
                ),
                ("review_comment", models.TextField(blank=True, verbose_name="审核意见")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="申请时间"),
                ),
                (
                    "reviewed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="审核时间"),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="审核人",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expert_applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="申请用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "达人认证申请",
                "verbose_name_plural": "达人认证申请",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("match", "匹配提醒"),
                            ("answer", "答疑回复"),
                            ("system", "系统通知"),
                            ("interaction", "互动通知"),
                        ],
                        max_length=20,
                        verbose_name="通知类型",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="标题")),
                ("content", models.TextField(verbose_name="内容")),
                ("is_read", models.BooleanField(default=False, verbose_name="是否已读")),
                (
                    "related_url",
                    models.CharField(blank=True, max_length=500, verbose_name="相关链接"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="接收用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "通知",
                "verbose_name_plural": "通知",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tag_type",
                    models.CharField(
                        choices=[
                            ("plant_type", "植物类型"),
                            ("care_environment", "养护环境"),
                            ("interest", "兴趣方向"),
                            ("problem", "常见问题"),
                        ],
                        max_length=30,
                        verbose_name="标签类型",
                    ),
                ),
                ("tag_value", models.CharField(max_length=100, verbose_name="标签值")),
                ("weight", models.FloatField(default=1.0, verbose_name="权重")),
                ("is_auto", models.BooleanField(default=False, verbose_name="是否自动生成")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tags",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "用户标签",
                "verbose_name_plural": "用户标签",
                "unique_together": {("user", "tag_type", "tag_value")},
            },
        ),
    ]
