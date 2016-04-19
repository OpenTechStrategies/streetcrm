# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0002_auto_20150302_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128),
#            preserve_default=True,
        ),
    ]
