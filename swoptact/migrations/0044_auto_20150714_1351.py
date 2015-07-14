# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swoptact.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0043_remove_contact_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=swoptact.modelfields.TwelveHourTimeField(verbose_name='Time of Action', blank=True, null=True),
        ),
    ]
