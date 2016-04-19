# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0045_auto_20150720_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='archived',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='archived',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='archived',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='archived',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
