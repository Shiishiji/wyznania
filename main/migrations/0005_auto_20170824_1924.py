# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-24 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20170824_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wyznanie',
            name='code',
            field=models.CharField(default='aaaaaaaaaaaa', max_length=12),
        ),
    ]
