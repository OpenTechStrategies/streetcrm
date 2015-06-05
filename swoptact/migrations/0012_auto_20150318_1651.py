# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0011_maptest_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='maptest',
            old_name='geo_address',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='maptest',
            old_name='location',
            new_name='geolocation',
        ),
    ]
