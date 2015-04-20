# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0023_auto_20150407_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='address',
            field=models.CharField(null=True, max_length=500, blank=True),
        ),
    ]
