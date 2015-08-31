# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0053_auto_20150831_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='date_created',
            field=models.DateField(null=True, default=django.utils.timezone.now, verbose_name='Date Linked', blank=True),
        ),
    ]
