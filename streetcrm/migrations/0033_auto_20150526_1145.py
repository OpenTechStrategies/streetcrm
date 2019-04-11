# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models, migrations
import streetcrm.modelfields

TIMES = {
    "10am": datetime.time(hour=10),
    "12pm": datetime.time(hour=12),
    "3pm": datetime.time(hour=15),
    "7pm": datetime.time(hour=19),
}

def migrate_time(apps, schema_editor):
    """ Migrates the time from a text/choice field to datetime.time field """
    Event = apps.get_model("streetcrm", "Event")
    for event in Event.objects.all():
        # Skip if the time is None
        if event.time is None:
            continue

        event.new_time = TIMES[event.time]
        event.save()

class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0032_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='streetcrm.Tag', null=True, blank=True),
        ),

        # Add the temp field to migrate the data to
        migrations.AddField(
            model_name='event',
            name='new_time',
            field=models.TimeField(null=True, blank=True)
        ),

        # Run the python migration to the new field
        migrations.RunPython(migrate_time),

        # Remove the old field
        migrations.RemoveField(
            model_name='event',
            name='time'
        ),

        # Rename the new field to the old name
        migrations.RenameField(
            model_name='event',
            old_name='new_time',
            new_name='time'
        ),

        # Other migrations
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='address',
            field=models.ForeignKey(to='streetcrm.Address', blank=True, null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='streetcrm.Tag', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='primary_phone',
            field=streetcrm.modelfields.PhoneNumberField(null=True, blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='participant',
            name='secondary_phone',
            field=streetcrm.modelfields.PhoneNumberField(null=True, blank=True, max_length=128),
        ),
    ]
