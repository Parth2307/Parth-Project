# Generated by Django 4.1.3 on 2022-11-30 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_addcart_product_price_addcart_product_qty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='addcart',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='addcart',
            name='total_price',
            field=models.PositiveIntegerField(),
        ),
    ]
