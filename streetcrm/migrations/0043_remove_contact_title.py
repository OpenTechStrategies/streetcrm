# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0042_auto_20150708_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='title',
        ),
    ]
