# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0022_event_terminal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='terminal',
            new_name='terminal_event',
        ),
    ]
