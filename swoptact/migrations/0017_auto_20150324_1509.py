# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0016_auto_20150324_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='address',
            field=models.ForeignKey(to='swoptact.Address', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='geolocation',
            field=django_google_maps.fields.GeoLocationField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='map_display',
            field=django_google_maps.fields.AddressField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(blank=True, to='swoptact.Participant'),
        ),
        migrations.AlterField(
            model_name='event',
            name='site',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='geolocation',
            field=django_google_maps.fields.GeoLocationField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='map_display',
            field=django_google_maps.fields.AddressField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True),
        ),
    ]
