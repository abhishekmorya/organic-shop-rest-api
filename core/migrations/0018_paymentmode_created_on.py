# Generated by Django 2.2 on 2022-01-12 12:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_paymentmode_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmode',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 1, 12, 12, 28, 17, 615041, tzinfo=utc)),
            preserve_default=False,
        ),
    ]