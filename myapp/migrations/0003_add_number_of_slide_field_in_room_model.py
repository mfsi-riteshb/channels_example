# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-04 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_add_active_user_room_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='number_of_slides',
            field=models.IntegerField(default=1),
        ),
    ]
