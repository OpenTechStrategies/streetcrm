# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0018_auto_20150324_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.ForeignKey(blank=True, to='swoptact.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='event',
            old_name='site',
            new_name='location',
        ),
        migrations.RemoveField(
            model_name='event',
            name='address',
        ),
        migrations.RemoveField(
            model_name='event',
            name='geolocation',
        ),
        migrations.RemoveField(
            model_name='event',
            name='map_display',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='geolocation',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='map_display',
        ),
        migrations.AddField(
            model_name='address',
            name='apartment',
            field=models.CharField(blank=True, max_length=20, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='zipcode',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='is_prep',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participant',
            name='secondary_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='participant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
    ]
