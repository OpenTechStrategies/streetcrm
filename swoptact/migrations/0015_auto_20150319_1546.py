# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0014_auto_20150319_1453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='new_address',
            new_name='map_display',
        ),
    ]
