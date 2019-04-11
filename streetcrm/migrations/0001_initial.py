# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('number', models.IntegerField()),
                ('direction', models.CharField(choices=[('n', 'North'), ('e', 'East'), ('s', 'South'), ('w', 'West')], max_length=1)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('st', 'Street'), ('av', 'Avenue'), ('blvd', 'Boulevard'), ('rd', 'Road')], max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('site', models.CharField(max_length=255)),
                ('address', models.ForeignKey(to='streetcrm.Address', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone_number', models.IntegerField()),
                ('email', models.EmailField(max_length=75)),
                ('address', models.ForeignKey(to='streetcrm.Address', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(to='streetcrm.Participant'),
            preserve_default=True,
        ),
    ]
