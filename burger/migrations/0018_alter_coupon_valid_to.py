# Generated by Django 4.1.2 on 2023-03-24 04:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burger', '0017_alter_coupon_valid_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 23, 10, 20, 30, 934226)),
        ),
    ]