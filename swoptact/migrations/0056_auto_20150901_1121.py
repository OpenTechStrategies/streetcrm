# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swoptact.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0055_remove_participant_display_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='cell',
            field=models.BooleanField(default=False, verbose_name='Is this a cell phone?'),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='phone_number',
            field=swoptact.modelfields.PhoneNumberField(max_length=128, verbose_name='Phone Number', null=True, blank=True),
        ),
    ]
