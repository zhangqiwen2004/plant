

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CareRecord",
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
                    "care_type",
                    models.CharField(
                        choices=[
                            ("water", "浇水"),
                            ("fertilize", "施肥"),
                            ("prune", "修剪"),
                            ("repot", "换盆"),
                            ("pest_control", "病虫害防治"),
                            ("other", "其他"),
                        ],
                        max_length=20,
                        verbose_name="养护类型",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="描述")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="care_records/",
                        verbose_name="图片",
                    ),
                ),
                ("care_date", models.DateField(verbose_name="养护日期")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "养护记录",
                "verbose_name_plural": "养护记录",
                "ordering": ["-care_date"],
            },
        ),
        migrations.CreateModel(
            name="Plant",
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
                ("name", models.CharField(max_length=100, verbose_name="植物名称")),
                (
                    "scientific_name",
                    models.CharField(blank=True, max_length=200, verbose_name="学名"),
                ),
                (
                    "alias",
                    models.CharField(blank=True, max_length=200, verbose_name="别名"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="plants/", verbose_name="图片"
                    ),
                ),
                ("description", models.TextField(verbose_name="简介")),
                (
                    "difficulty",
                    models.CharField(
                        choices=[("easy", "容易"), ("medium", "中等"), ("hard", "困难")],
                        default="medium",
                        max_length=20,
                        verbose_name="养护难度",
                    ),
                ),
                (
                    "light_requirement",
                    models.CharField(
                        choices=[
                            ("full_sun", "全日照"),
                            ("partial_sun", "半日照"),
                            ("shade", "阴凉"),
                            ("indirect", "散射光"),
                        ],
                        default="indirect",
                        max_length=20,
                        verbose_name="光照需求",
                    ),
                ),
                (
                    "water_requirement",
                    models.CharField(
                        choices=[("low", "少量"), ("medium", "适中"), ("high", "大量")],
                        default="medium",
                        max_length=20,
                        verbose_name="浇水需求",
                    ),
                ),
                (
                    "temperature_min",
                    models.IntegerField(default=10, verbose_name="最低温度(℃)"),
                ),
                (
                    "temperature_max",
                    models.IntegerField(default=30, verbose_name="最高温度(℃)"),
                ),
                (
                    "humidity",
                    models.CharField(blank=True, max_length=100, verbose_name="湿度要求"),
                ),
                ("soil_requirement", models.TextField(blank=True, verbose_name="土壤要求")),
                ("fertilizer_tips", models.TextField(blank=True, verbose_name="施肥建议")),
                ("pruning_tips", models.TextField(blank=True, verbose_name="修剪建议")),
                ("propagation", models.TextField(blank=True, verbose_name="繁殖方式")),
                ("common_problems", models.TextField(blank=True, verbose_name="常见问题")),
                ("care_tips", models.TextField(blank=True, verbose_name="养护要点")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("view_count", models.IntegerField(default=0, verbose_name="浏览次数")),
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
                "verbose_name": "植物",
                "verbose_name_plural": "植物",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PlantCategory",
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
                    models.CharField(max_length=50, unique=True, verbose_name="分类名称"),
                ),
                ("description", models.TextField(blank=True, verbose_name="分类描述")),
                (
                    "icon",
                    models.CharField(blank=True, max_length=50, verbose_name="图标"),
                ),
                ("order", models.IntegerField(default=0, verbose_name="排序")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "植物分类",
                "verbose_name_plural": "植物分类",
                "ordering": ["order", "name"],
            },
        ),
        migrations.CreateModel(
            name="PlantTag",
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
                    models.CharField(max_length=50, unique=True, verbose_name="标签名称"),
                ),
                (
                    "color",
                    models.CharField(
                        default="#4CAF50", max_length=20, verbose_name="标签颜色"
                    ),
                ),
            ],
            options={
                "verbose_name": "植物标签",
                "verbose_name_plural": "植物标签",
            },
        ),
        migrations.CreateModel(
            name="PlantTagRelation",
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
            ],
            options={
                "verbose_name": "植物标签关联",
                "verbose_name_plural": "植物标签关联",
            },
        ),
        migrations.CreateModel(
            name="UserPlant",
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
                    "nickname",
                    models.CharField(blank=True, max_length=50, verbose_name="昵称"),
                ),
                ("notes", models.TextField(blank=True, verbose_name="备注")),
                (
                    "acquired_date",
                    models.DateField(blank=True, null=True, verbose_name="获得日期"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "用户植物",
                "verbose_name_plural": "用户植物",
            },
        ),
    ]
