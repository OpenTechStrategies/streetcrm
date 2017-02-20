# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0036_convert_address_textfield'),
    ]

    # If we were working with real data at the time this migration was
    # created, we could add code here to append the values from
    # last_name onto name.  But there shouldn't be any need to do
    # that, since the sample data is already updated and we don't have
    # any production data to worry about as of yet.

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='first_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='last_name',
        ),
    ]
