# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swoptact.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0032_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='swoptact.Tag', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='address',
            field=models.ForeignKey(to='swoptact.Address', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='swoptact.Tag', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='primary_phone',
            field=swoptact.modelfields.PhoneNumberField(null=True, blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='participant',
            name='secondary_phone',
            field=swoptact.modelfields.PhoneNumberField(null=True, blank=True, max_length=128),
        ),
    ]
