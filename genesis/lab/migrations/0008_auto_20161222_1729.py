# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0007_setting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='code',
            field=models.CharField(max_length=30, verbose_name='Setting code name'),
        ),
    ]
