# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0051_auto_20150810_0513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='contacts',
            field=models.ManyToManyField(to='swoptact.Participant', related_name='main_contact'),
        ),
    ]
