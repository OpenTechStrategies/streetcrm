# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0063_auto_20170404_1212'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participant',
            options={'ordering': ['name']},
        ),
    ]
