# Generated by Django 2.2 on 2022-01-09 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20220108_2012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.RemoveField(
            model_name='shoppingcart',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='cartItems',
            field=models.ManyToManyField(to='core.ShoppingCart'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='core.Product'),
            preserve_default=False,
        ),
    ]