# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0013_auto_20150319_1246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='address_new',
            new_name='new_address',
        ),
    ]
