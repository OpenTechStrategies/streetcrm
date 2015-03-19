# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0003_auto_20150305_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128),
        ),
    ]
