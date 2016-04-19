# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0007_auto_20150310_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(to='streetcrm.Participant'),
        ),
    ]
