

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MatchRecord",
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
                        choices=[("expert", "需求用户-养护达人"), ("peer", "需求用户-同好用户")],
                        max_length=20,
                        verbose_name="匹配类型",
                    ),
                ),
                (
                    "similarity_score",
                    models.FloatField(default=0.0, verbose_name="相似度分数"),
                ),
                ("match_reason", models.TextField(blank=True, verbose_name="匹配依据")),
                ("matched_tags", models.JSONField(default=list, verbose_name="匹配的标签")),
                (
                    "is_contacted",
                    models.BooleanField(default=False, verbose_name="是否已联系"),
                ),
                (
                    "feedback",
                    models.IntegerField(blank=True, null=True, verbose_name="反馈评分"),
                ),
                ("feedback_comment", models.TextField(blank=True, verbose_name="反馈评论")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="匹配时间"),
                ),
            ],
            options={
                "verbose_name": "匹配记录",
                "verbose_name_plural": "匹配记录",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="MatchRequest",
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
                ("message", models.TextField(blank=True, verbose_name="请求消息")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "待处理"),
                            ("accepted", "已接受"),
                            ("rejected", "已拒绝"),
                            ("expired", "已过期"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "responded_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="响应时间"),
                ),
            ],
            options={
                "verbose_name": "匹配请求",
                "verbose_name_plural": "匹配请求",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TagWeight",
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
                    models.CharField(max_length=30, unique=True, verbose_name="标签类型"),
                ),
                ("weight", models.FloatField(default=1.0, verbose_name="权重")),
                ("description", models.TextField(blank=True, verbose_name="描述")),
            ],
            options={
                "verbose_name": "标签权重",
                "verbose_name_plural": "标签权重",
            },
        ),
    ]
