# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='direction',
            field=models.CharField(max_length=1, choices=[('N', 'North'), ('E', 'East'), ('S', 'South'), ('W', 'West')]),
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(max_length=20, choices=[('St', 'Street'), ('Av', 'Avenue'), ('Blvd', 'Boulevard'), ('Rd', 'Road')]),
        ),
    ]
