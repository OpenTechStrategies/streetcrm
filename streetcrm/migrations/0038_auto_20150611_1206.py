# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0037_auto_20150610_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='date_created',
            field=models.DateField(null=True, default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='group',
            field=models.ForeignKey(to='auth.Group', verbose_name='Group Assignment'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
