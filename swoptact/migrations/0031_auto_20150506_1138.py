# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0030_institution_is_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
