# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-11 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20170911_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='komentarz',
            name='code',
            field=models.CharField(default='aaaaaaaaaaaa', max_length=12, unique=True),
        ),
    ]