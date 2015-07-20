# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import swoptact.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0044_auto_20150714_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='address',
            field=models.TextField(verbose_name='Institution Address', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Institution'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(verbose_name='Institution Tags', blank=True, to='swoptact.Tag'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='address',
            field=models.TextField(verbose_name='Participant Address', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Participant Email', blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='institution',
            field=models.ForeignKey(verbose_name="Participant's Institution", to='swoptact.Institution', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Participant Name'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='primary_phone',
            field=swoptact.modelfields.PhoneNumberField(max_length=128, verbose_name='Participant Phone', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='secondary_phone',
            field=swoptact.modelfields.PhoneNumberField(max_length=128, verbose_name='Secondary\n                                                   Participant Phone', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='title',
            field=models.CharField(help_text='e.g. Pastor, Director', max_length=255, verbose_name="Participant's Title", blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='date_created',
            field=models.DateField(verbose_name='Date Tag Created', null=True, blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=models.CharField(max_length=255, verbose_name='Tag Description', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=10, unique=True, verbose_name='Tag'),
        ),
    ]
