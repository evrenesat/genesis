# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0004_auto_20161222_1120'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=30, verbose_name='Setting name')),
                ('value', models.CharField(max_length=255, verbose_name='Setting value')),
                ('code', models.CharField(max_length=30, verbose_name='Setting value')),
            ],
            options={
                'verbose_name_plural': 'Application Settings',
                'verbose_name': 'Application Setting',
            },
        ),
    ]
