# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0054_phonenumber_date_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='display_phone',
        ),
    ]
