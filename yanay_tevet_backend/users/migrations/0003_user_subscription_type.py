from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_campaigns_limit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='campaigns_limit',
        ),
        migrations.AddField(
            model_name='user',
            name='subscription_type',
            field=models.CharField(
                blank=True,
                choices=[('basic', 'basic'), ('pro', 'pro'), ('max', 'max')],
                default='basic',
                max_length=20,
            ),
        ),
    ]
