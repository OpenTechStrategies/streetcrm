# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0038_auto_20150611_1206'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'action', 'verbose_name_plural': 'actions'},
        ),
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(verbose_name='Date of Action', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.CharField(verbose_name='Action Description', blank=True, null=True, max_length=255, help_text='Max length = 255 characters.<br> e.g."Met with housing stakeholders." '),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(verbose_name='Action Location', blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(verbose_name='Action Name', help_text='The name includes an issue area and a topic.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(verbose_name='Action Tag(s)', blank=True, to='swoptact.Tag'),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(verbose_name='Time of Action', blank=True, null=True),
        ),
    ]
