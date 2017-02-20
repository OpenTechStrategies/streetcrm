# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0038_auto_20150611_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(null=True, blank=True, verbose_name='Date of Action'),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.CharField(null=True, verbose_name='Action Description', blank=True, help_text='Max length = 255 characters.<br> e.g."Met with housing stakeholders." ', max_length=255),
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
            field=models.ManyToManyField(to='streetcrm.Tag', blank=True, verbose_name='Action Tag(s)'),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(null=True, blank=True, verbose_name='Time of Action'),
        ),
    ]
