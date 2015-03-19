# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0002_auto_20150302_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='direction',
            field=models.CharField(choices=[('N', 'north'), ('E', 'east'), ('S', 'south'), ('W', 'west')], max_length=1),
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(choices=[('St', 'street'), ('Av', 'avenue'), ('Blvd', 'boulevard'), ('Rd', 'road')], max_length=20),
        ),
    ]
