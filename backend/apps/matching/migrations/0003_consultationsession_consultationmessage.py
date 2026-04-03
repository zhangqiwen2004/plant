

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("matching", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsultationSession",
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
                    "match_type",
                    models.CharField(
                        choices=[
                            ("expert", "需求用户-养护达人"),
                            ("peer", "需求用户-同好用户"),
                        ],
                        default="peer",
                        max_length=20,
                        verbose_name="匹配类型",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "进行中"), ("completed", "已完成")],
                        default="active",
                        max_length=20,
                        verbose_name="会话状态",
                    ),
                ),
                (
                    "last_message_preview",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="最新消息摘要"
                    ),
                ),
                (
                    "last_message_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="最新消息时间"
                    ),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="完成时间"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "consultant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultant_consultations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="接受用户",
                    ),
                ),
                (
                    "match_request",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultation",
                        to="matching.matchrequest",
                        verbose_name="来源请求",
                    ),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requested_consultations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="发起用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "咨询会话",
                "verbose_name_plural": "咨询会话",
                "ordering": ["-last_message_at", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ConsultationMessage",
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
                    "message_type",
                    models.CharField(
                        choices=[("system", "系统消息"), ("user", "用户消息")],
                        default="user",
                        max_length=20,
                        verbose_name="消息类型",
                    ),
                ),
                ("content", models.TextField(verbose_name="消息内容")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="发送时间"),
                ),
                (
                    "consultation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="matching.consultationsession",
                        verbose_name="所属会话",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultation_messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="发送者",
                    ),
                ),
            ],
            options={
                "verbose_name": "咨询消息",
                "verbose_name_plural": "咨询消息",
                "ordering": ["created_at"],
            },
        ),
    ]
