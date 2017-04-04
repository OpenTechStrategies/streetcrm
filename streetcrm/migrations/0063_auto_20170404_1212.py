# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import streetcrm.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0062_archive_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='phone_number',
            field=streetcrm.modelfields.PhoneNumberField(verbose_name='Institution Phone', max_length=128, blank=True, null=True),
        ),
    ]
