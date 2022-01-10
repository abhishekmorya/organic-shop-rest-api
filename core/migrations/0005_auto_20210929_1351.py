# Generated by Django 2.2 on 2021-09-29 08:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210928_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='pincode',
            field=models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^[1-9]{1}[0-9]{5}$')]),
        ),
    ]