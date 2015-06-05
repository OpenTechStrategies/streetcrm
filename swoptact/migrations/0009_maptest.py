# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0008_auto_20150317_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='mapTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('geo_address', django_google_maps.fields.AddressField(max_length=200)),
                ('geolocation', django_google_maps.fields.GeoLocationField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
