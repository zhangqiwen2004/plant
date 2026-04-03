

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("analytics", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="useractivity",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activities",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="useractivity",
            index=models.Index(
                fields=["user", "action"], name="analytics_u_user_id_b287be_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="useractivity",
            index=models.Index(
                fields=["created_at"], name="analytics_u_created_775113_idx"
            ),
        ),
    ]
