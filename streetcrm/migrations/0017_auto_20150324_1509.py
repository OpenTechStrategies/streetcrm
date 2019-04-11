# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0008_auto_20150317_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='address',
            field=models.ForeignKey(to='streetcrm.Address', blank=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(blank=True, to='streetcrm.Participant'),
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
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True),
        ),
    ]
