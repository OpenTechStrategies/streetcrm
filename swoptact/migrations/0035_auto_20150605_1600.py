# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.admin.models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
        ('swoptact', '0034_auto_20150529_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
            ],
            options={
                'verbose_name': 'Activity Log',
                'proxy': True,
                'verbose_name_plural': 'Activity Log',
            },
            bases=('admin.logentry',),
            managers=[
                ('objects', django.contrib.admin.models.LogEntryManager()),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='swoptact.Tag'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(blank=True, to='swoptact.Tag'),
        ),
    ]
