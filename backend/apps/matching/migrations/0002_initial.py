

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("matching", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="matchrecord",
            name="matched_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matched_by_records",
                to=settings.AUTH_USER_MODEL,
                verbose_name="匹配用户",
            ),
        ),
        migrations.AddField(
            model_name="matchrecord",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="match_records",
                to=settings.AUTH_USER_MODEL,
                verbose_name="发起用户",
            ),
        ),
        migrations.AddField(
            model_name="matchrequest",
            name="from_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_match_requests",
                to=settings.AUTH_USER_MODEL,
                verbose_name="发起用户",
            ),
        ),
        migrations.AddField(
            model_name="matchrequest",
            name="to_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_match_requests",
                to=settings.AUTH_USER_MODEL,
                verbose_name="目标用户",
            ),
        ),
    ]
