# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0010_remove_maptest_geolocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='maptest',
            name='location',
            field=django_google_maps.fields.GeoLocationField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
