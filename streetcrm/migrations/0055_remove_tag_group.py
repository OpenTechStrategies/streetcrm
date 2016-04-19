# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0054_more_staff_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='group',
        ),
    ]
