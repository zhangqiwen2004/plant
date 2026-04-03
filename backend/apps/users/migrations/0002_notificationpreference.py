from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_app_enabled', models.BooleanField(default=True, verbose_name='站内通知开关')),
                ('email_enabled', models.BooleanField(default=False, verbose_name='邮件通知开关')),
                ('receive_match', models.BooleanField(default=True, verbose_name='接收匹配提醒')),
                ('receive_answer', models.BooleanField(default=True, verbose_name='接收答疑回复')),
                ('receive_system', models.BooleanField(default=True, verbose_name='接收系统通知')),
                ('receive_interaction', models.BooleanField(default=True, verbose_name='接收互动通知')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preference', to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '通知偏好',
                'verbose_name_plural': '通知偏好',
            },
        ),
    ]
