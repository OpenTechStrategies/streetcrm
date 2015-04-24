# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0024_auto_20150420_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='address',
            field=models.ForeignKey(null=True, blank=True, to='swoptact.Address'),
        ),
    ]
