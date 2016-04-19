# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0020_participant_institution'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.CharField(blank=True, max_length=255, default='Chicago', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=2, default='IL', null=True),
            preserve_default=True,
        ),
    ]
