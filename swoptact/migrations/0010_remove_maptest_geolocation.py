# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0009_maptest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maptest',
            name='geolocation',
        ),
    ]
