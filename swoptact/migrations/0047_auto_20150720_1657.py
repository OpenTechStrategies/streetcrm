# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0046_auto_20150720_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='issue_area',
            field=models.CharField(verbose_name='Action Issue Area', max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(blank=True, null=True, related_name='Organizer', to='swoptact.Participant'),
        ),
    ]
