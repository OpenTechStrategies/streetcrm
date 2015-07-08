# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0041_auto_20150629_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='title',
            field=models.CharField(blank=True, help_text='e.g. Pastor, Director', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='is_member',
            field=models.BooleanField(verbose_name='Is this institution a member of SWOP?', default=False),
        ),
    ]
