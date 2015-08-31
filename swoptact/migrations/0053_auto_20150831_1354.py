# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swoptact.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0052_auto_20150831_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('phone_number', swoptact.modelfields.PhoneNumberField(null=True, verbose_name='Participant Phone', blank=True, max_length=128)),
                ('cell', models.BooleanField(default=False, verbose_name='This is a cell phone')),
            ],
        ),
        migrations.RemoveField(
            model_name='participant',
            name='primary_phone',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='secondary_phone',
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, related_name='Caller', to='swoptact.Participant'),
        ),
        migrations.AddField(
            model_name='participant',
            name='display_phone',
            field=models.ForeignKey(blank=True, null=True, verbose_name='Participant Phone', to='swoptact.PhoneNumber'),
        ),
    ]
