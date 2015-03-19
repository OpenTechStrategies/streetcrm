# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0012_auto_20150318_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='address_new',
            field=django_google_maps.fields.AddressField(max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='participant',
            name='geolocation',
            field=django_google_maps.fields.GeoLocationField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]
