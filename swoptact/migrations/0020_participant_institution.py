# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0019_auto_20150402_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, to='streetcrm.Institution'),
            preserve_default=True,
        ),
    ]
