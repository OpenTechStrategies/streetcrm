# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0060_nonce_to_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='is_member',
            field=models.BooleanField(default=False, verbose_name='Is this institution a member of StreetCRM Default Org?'),
        ),
    ]
