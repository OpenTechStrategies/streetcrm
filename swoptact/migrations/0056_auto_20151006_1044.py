# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0055_remove_tag_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='inst_city_address',
            field=models.CharField(null=True, blank=True, verbose_name='City', max_length=255),
        ),
        migrations.AlterField(
            model_name='institution',
            name='inst_state_address',
            field=models.CharField(null=True, blank=True, verbose_name='State', max_length=255),
        ),
        migrations.AlterField(
            model_name='institution',
            name='inst_zipcode_address',
            field=models.CharField(null=True, blank=True, verbose_name='Zip', max_length=10),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='swoptact.Tag', verbose_name='Tags', blank=True, help_text='Note that new tags added here are not created.'),
        ),
    ]
