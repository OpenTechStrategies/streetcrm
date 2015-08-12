# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0049_add_permissions_to_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institution',
            name='address',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='address',
        ),
        migrations.AddField(
            model_name='institution',
            name='inst_city_address',
            field=models.CharField(blank=True, null=True, verbose_name='Institution City', max_length=255),
        ),
        migrations.AddField(
            model_name='institution',
            name='inst_state_address',
            field=models.CharField(blank=True, null=True, verbose_name='Institution State', max_length=255),
        ),
        migrations.AddField(
            model_name='institution',
            name='inst_street_address',
            field=models.CharField(blank=True, null=True, verbose_name='Institution Street Address', max_length=1000),
        ),
        migrations.AddField(
            model_name='institution',
            name='inst_zipcode_address',
            field=models.CharField(blank=True, null=True, verbose_name='Institution Zipcode', max_length=10),
        ),
        migrations.AddField(
            model_name='participant',
            name='participant_city_address',
            field=models.CharField(blank=True, null=True, verbose_name='Participant City', max_length=255),
        ),
        migrations.AddField(
            model_name='participant',
            name='participant_state_address',
            field=models.CharField(blank=True, null=True, verbose_name='Participant State', max_length=255),
        ),
        migrations.AddField(
            model_name='participant',
            name='participant_street_address',
            field=models.CharField(blank=True, null=True, verbose_name='Participant Street Address', max_length=1000),
        ),
        migrations.AddField(
            model_name='participant',
            name='participant_zipcode_address',
            field=models.CharField(blank=True, null=True, verbose_name='Participant Zipcode', max_length=10),
        ),
    ]
