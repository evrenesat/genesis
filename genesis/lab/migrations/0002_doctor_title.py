# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-21 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='title',
            field=models.CharField(default='Dr.', max_length=20, verbose_name='Title'),
            preserve_default=False,
        ),
    ]