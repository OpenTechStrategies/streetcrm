# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0005_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='direction',
            field=models.CharField(choices=[('N', 'North'), ('E', 'East'), ('S', 'South'), ('W', 'West')], max_length=1),
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(choices=[('St', 'Street'), ('Av', 'Avenue'), ('Blvd', 'Boulevard'), ('Rd', 'Road')], max_length=20),
        ),
    ]
