

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DailyStatistics",
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
                ("date", models.DateField(unique=True, verbose_name="日期")),
                ("new_users", models.IntegerField(default=0, verbose_name="新增用户数")),
                ("active_users", models.IntegerField(default=0, verbose_name="活跃用户数")),
                ("total_users", models.IntegerField(default=0, verbose_name="总用户数")),
                ("new_posts", models.IntegerField(default=0, verbose_name="新增帖子数")),
                ("new_questions", models.IntegerField(default=0, verbose_name="新增问题数")),
                ("new_answers", models.IntegerField(default=0, verbose_name="新增回答数")),
                ("new_comments", models.IntegerField(default=0, verbose_name="新增评论数")),
                (
                    "total_interactions",
                    models.IntegerField(default=0, verbose_name="总互动数"),
                ),
                ("match_count", models.IntegerField(default=0, verbose_name="匹配次数")),
                (
                    "match_success_count",
                    models.IntegerField(default=0, verbose_name="匹配成功次数"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "每日统计",
                "verbose_name_plural": "每日统计",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="UserActivity",
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
                    "action",
                    models.CharField(
                        choices=[
                            ("login", "登录"),
                            ("post", "发帖"),
                            ("comment", "评论"),
                            ("question", "提问"),
                            ("answer", "回答"),
                            ("like", "点赞"),
                            ("match", "匹配"),
                            ("view", "浏览"),
                        ],
                        max_length=20,
                        verbose_name="行为类型",
                    ),
                ),
                (
                    "target_type",
                    models.CharField(blank=True, max_length=50, verbose_name="目标类型"),
                ),
                (
                    "target_id",
                    models.IntegerField(blank=True, null=True, verbose_name="目标ID"),
                ),
                (
                    "extra_data",
                    models.JSONField(blank=True, default=dict, verbose_name="额外数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "用户活动",
                "verbose_name_plural": "用户活动",
                "ordering": ["-created_at"],
            },
        ),
    ]
