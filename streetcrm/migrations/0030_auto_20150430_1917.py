# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0029_add_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=255)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[('10am', 'Morning'), ('12pm', 'Noon'), ('3pm', 'Afternoon'), ('7pm', 'Evening')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='streetcrm.Tag'),
        ),
        migrations.AddField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='streetcrm.Tag'),
        ),
    ]
