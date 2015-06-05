# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0015_auto_20150319_1546'),
    ]

    operations = [
        migrations.DeleteModel(
            name='mapTest',
        ),
        migrations.AddField(
            model_name='event',
            name='geolocation',
            field=django_google_maps.fields.GeoLocationField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='map_display',
            field=django_google_maps.fields.AddressField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
