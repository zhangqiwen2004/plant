

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Answer",
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
                ("content", models.TextField(verbose_name="回答内容")),
                (
                    "images",
                    models.JSONField(blank=True, default=list, verbose_name="图片列表"),
                ),
                (
                    "is_accepted",
                    models.BooleanField(default=False, verbose_name="是否被采纳"),
                ),
                ("like_count", models.IntegerField(default=0, verbose_name="点赞数")),
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
                "verbose_name": "问题回答",
                "verbose_name_plural": "问题回答",
                "ordering": ["-is_accepted", "-like_count", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AnswerLike",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="点赞时间"),
                ),
            ],
            options={
                "verbose_name": "回答点赞",
                "verbose_name_plural": "回答点赞",
            },
        ),
        migrations.CreateModel(
            name="Comment",
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
                ("content", models.TextField(verbose_name="内容")),
                ("like_count", models.IntegerField(default=0, verbose_name="点赞数")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "评论",
                "verbose_name_plural": "评论",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="CommentLike",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="点赞时间"),
                ),
            ],
            options={
                "verbose_name": "评论点赞",
                "verbose_name_plural": "评论点赞",
            },
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(max_length=200, verbose_name="标题")),
                ("content", models.TextField(verbose_name="内容")),
                (
                    "images",
                    models.JSONField(blank=True, default=list, verbose_name="图片列表"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "待审核"),
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
                    "reviewed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="审核时间"),
                ),
                ("view_count", models.IntegerField(default=0, verbose_name="浏览数")),
                ("like_count", models.IntegerField(default=0, verbose_name="点赞数")),
                ("comment_count", models.IntegerField(default=0, verbose_name="评论数")),
                ("is_top", models.BooleanField(default=False, verbose_name="是否置顶")),
                ("is_essence", models.BooleanField(default=False, verbose_name="是否精华")),
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
                "verbose_name": "帖子",
                "verbose_name_plural": "帖子",
                "ordering": ["-is_top", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PostImage",
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
                ("image", models.ImageField(upload_to="posts/", verbose_name="图片")),
                ("order", models.IntegerField(default=0, verbose_name="排序")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "帖子图片",
                "verbose_name_plural": "帖子图片",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="PostLike",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="点赞时间"),
                ),
            ],
            options={
                "verbose_name": "帖子点赞",
                "verbose_name_plural": "帖子点赞",
            },
        ),
        migrations.CreateModel(
            name="Question",
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
                ("title", models.CharField(max_length=200, verbose_name="问题标题")),
                ("content", models.TextField(verbose_name="问题描述")),
                (
                    "images",
                    models.JSONField(blank=True, default=list, verbose_name="图片列表"),
                ),
                (
                    "plant_type",
                    models.CharField(blank=True, max_length=100, verbose_name="植物类型"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "待解答"),
                            ("answered", "已解答"),
                            ("closed", "已关闭"),
                        ],
                        default="open",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                ("view_count", models.IntegerField(default=0, verbose_name="浏览数")),
                ("answer_count", models.IntegerField(default=0, verbose_name="回答数")),
                ("is_urgent", models.BooleanField(default=False, verbose_name="是否紧急")),
                ("bounty", models.IntegerField(default=0, verbose_name="悬赏积分")),
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
                "verbose_name": "养护问题",
                "verbose_name_plural": "养护问题",
                "ordering": ["-is_urgent", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="QuestionImage",
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
                ("image", models.ImageField(upload_to="questions/", verbose_name="图片")),
                ("order", models.IntegerField(default=0, verbose_name="排序")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "问题图片",
                "verbose_name_plural": "问题图片",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Topic",
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
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="话题名称"),
                ),
                ("description", models.TextField(blank=True, verbose_name="话题描述")),
                (
                    "icon",
                    models.ImageField(
                        blank=True, null=True, upload_to="topics/", verbose_name="话题图标"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("post_count", models.IntegerField(default=0, verbose_name="帖子数")),
                ("follower_count", models.IntegerField(default=0, verbose_name="关注数")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "话题圈",
                "verbose_name_plural": "话题圈",
                "ordering": ["-follower_count"],
            },
        ),
        migrations.CreateModel(
            name="TopicFollow",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="关注时间"),
                ),
            ],
            options={
                "verbose_name": "话题关注",
                "verbose_name_plural": "话题关注",
            },
        ),
    ]
