# Generated by Django 2.2 on 2022-01-08 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20220108_1854'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcart',
            name='product',
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='products',
            field=models.ManyToManyField(to='core.Product'),
        ),
        migrations.RemoveField(
            model_name='order',
            name='offers_applied',
        ),
        migrations.AddField(
            model_name='order',
            name='offers_applied',
            field=models.ManyToManyField(to='core.Offer'),
        ),
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(to='core.Product'),
        ),
    ]