# Generated by Django 2.2 on 2021-09-29 10:06

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210929_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='pincode',
            field=models.CharField(max_length=6, validators=[core.models.validate_pincode]),
        ),
    ]
