

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("plants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="carerecord",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="care_records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="plantcategory",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="plants.plantcategory",
                verbose_name="父分类",
            ),
        ),
        migrations.AddField(
            model_name="plant",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="plants",
                to="plants.plantcategory",
                verbose_name="分类",
            ),
        ),
        migrations.AddField(
            model_name="planttagrelation",
            name="plant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tag_relations",
                to="plants.plant",
            ),
        ),
        migrations.AddField(
            model_name="planttagrelation",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="plant_relations",
                to="plants.planttag",
            ),
        ),
        migrations.AddField(
            model_name="userplant",
            name="plant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collectors",
                to="plants.plant",
            ),
        ),
        migrations.AddField(
            model_name="userplant",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collected_plants",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="carerecord",
            name="user_plant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="care_records",
                to="plants.userplant",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="planttagrelation",
            unique_together={("plant", "tag")},
        ),
        migrations.AlterUniqueTogether(
            name="userplant",
            unique_together={("user", "plant")},
        ),
    ]
