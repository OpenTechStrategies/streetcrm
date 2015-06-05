# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0029_auto_20150506_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='is_member',
            field=models.BooleanField(verbose_name='This institution is a member of SWOP:', default=False),
            preserve_default=True,
        ),
    ]
