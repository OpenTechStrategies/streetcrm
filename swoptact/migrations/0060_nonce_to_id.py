# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0059_add_leadership_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='nonce_to_id',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('nonce', models.CharField(max_length=12)),
                ('participant', models.IntegerField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
