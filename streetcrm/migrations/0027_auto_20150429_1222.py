# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0026_auto_20150429_1209'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='terminal_event',
            new_name='major_action',
        ),
        migrations.AlterField(
            model_name='event',
            name='is_prep',
            field=models.BooleanField(default=False, verbose_name='This meeting is part of a major action'),
        ),
    ]
