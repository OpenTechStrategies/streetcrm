# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0061_rename_tables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='is_member',
            field=models.BooleanField(verbose_name="Is this institution a member of Third time's the charm?", default=False),
        ),
        migrations.AlterModelTable(
            name='event',
            table='streetcrm_event',
        ),
        migrations.AlterModelTable(
            name='institution',
            table='streetcrm_institution',
        ),
        migrations.AlterModelTable(
            name='leadershipgrowth',
            table='streetcrm_leadershipgrowth',
        ),
        migrations.AlterModelTable(
            name='leaderstage',
            table='streetcrm_leaderstage',
        ),
        migrations.AlterModelTable(
            name='nonce_to_id',
            table='streetcrm_nonce_to_id',
        ),
        migrations.AlterModelTable(
            name='participant',
            table='streetcrm_participant',
        ),
        migrations.AlterModelTable(
            name='tag',
            table='streetcrm_tag',
        ),
    ]
