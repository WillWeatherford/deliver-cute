# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-06 20:26
from __future__ import unicode_literals

from django.db import migrations, models
import subscribers.models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0007_auto_20160805_0143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='unsubscribe_hash',
            field=models.CharField(default=subscribers.models._hash, max_length=255, unique=True),
        ),
    ]
