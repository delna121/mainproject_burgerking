# Generated by Django 4.0.6 on 2023-03-14 09:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('burger', '0012_alter_coupon_valid_to_alter_orderplaced_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 13, 15, 6, 13, 955215)),
        ),
        migrations.CreateModel(
            name='PreBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]