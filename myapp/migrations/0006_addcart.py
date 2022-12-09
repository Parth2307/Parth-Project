# Generated by Django 4.1.3 on 2022-11-25 10:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_wishlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Addcart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.user')),
                ('wishlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.wishlist')),
            ],
        ),
    ]
