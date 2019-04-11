# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0021_auto_20150407_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='terminal',
            field=models.ForeignKey(blank=True, null=True, to='streetcrm.Event', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
