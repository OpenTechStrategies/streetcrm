# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0025_auto_20150424_1026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='phone_number',
            new_name='primary_phone',
        ),
    ]
