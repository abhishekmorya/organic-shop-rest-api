# Generated by Django 2.2 on 2022-01-11 07:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20220109_1935'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionSoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aUser', models.CharField(max_length=255)),
                ('count', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
        ),
    ]
