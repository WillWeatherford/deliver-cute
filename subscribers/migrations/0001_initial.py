# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 08:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('send_hour', models.IntegerField(choices=[(0, '0:00'), (1, '1:00'), (2, '2:00'), (3, '3:00'), (4, '4:00'), (5, '5:00'), (6, '6:00'), (7, '7:00'), (8, '8:00'), (9, '9:00'), (10, '10:00'), (11, '11:00'), (12, '12:00'), (13, '13:00'), (14, '14:00'), (15, '15:00'), (16, '16:00'), (17, '17:00'), (18, '18:00'), (19, '19:00'), (20, '20:00'), (21, '21:00'), (22, '22:00'), (23, '23:00')], default=8)),
            ],
        ),
    ]
