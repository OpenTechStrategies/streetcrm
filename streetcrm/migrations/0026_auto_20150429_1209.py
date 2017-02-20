# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0023_auto_20150407_1358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='phone_number',
            new_name='primary_phone',
        ),
    ]
