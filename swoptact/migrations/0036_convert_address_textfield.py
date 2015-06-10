# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

ADDRESS_FORMAT = "{number} {direction} {name} {type} #{apartment} {city}, {state} {zipcode}"

ADDRESS_TYPES = {
    "St": "Street",
    "Av": "Avenue",
    "Blvd": "Boulevard",
    "Rd": "Road",
}

ADDRESS_DIRECTIONS = {
    "N": "North",
    "E": "East",
    "S": "South",
    "W": "West",
}

def address_to_string(address):
    """
        Convert address object into a python string

        This is largely based off the Address.__str__ method
        that won't be accessable when this migration is being
        run.
    """
    return ADDRESS_FORMAT.format(
        number=address.number,
        direction=ADDRESS_DIRECTIONS[address.direction],
        name=address.name,
        type=ADDRESS_TYPES[address.type],
        apartment=address.apartment,
        city=address.city,
        state=address.state,
        zipcode=address.zipcode
    )

def migrate_addresses(apps, schema_editor):
    """ Migrates the addresses over to the new fields. """
    Institution = apps.get_model("swoptact", "Institution")
    for institution in Institution.objects.all():
        # Skip institutions which don't have addresses
        if institution.address is None:
            continue

        institution.new_address = address_to_string(institution.address)
        institution.save()

    Participant = apps.get_model("swoptact", "Participant")
    for participant in Participant.objects.all():
        # Skip participants which don't have addresses
        if participant.address is None:
            continue

        participant.new_address = address_to_string(participant.address)
        participant.save()

def remove_address_contenttype(apps, schema_editor):
    """
        Removes stale ContentType object for Address

        The ContentType app tracks the models for apps in Django, however when
        models are removed they can leave stake ContentTypes. We have migrated
        everything over so we and removed the model so we can safely remove it.

        Failure to remove this would produce a message after this migration
        asking the user if they would like to remove the ContentType, this can
        be confused and avoidable.
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    address_ct = ContentType.objects.filter(
        app_label="swoptact",
        model="address"
    )

    if address_ct.exists():
        address_ct.delete()

class Migration(migrations.Migration):

    dependencies = [
        ("swoptact", "0035_auto_20150605_1600"),
    ]

    operations = [
        # Add new temp fields
        migrations.AddField(
            model_name="institution",
            name="new_address",
            field=models.TextField(null=True, blank=True)
        ),
        migrations.AddField(
            model_name="participant",
            name="new_address",
            field=models.TextField(null=True, blank=True)
        ),

        # Run the data migration
        migrations.RunPython(migrate_addresses),

        # Remove the fields and models
        migrations.RemoveField(
            model_name="institution",
            name="address",
        ),
        migrations.RemoveField(
            model_name="participant",
            name="address",
        ),
        migrations.DeleteModel(
            name="Address",
        ),

        # Remove ContentType for the old Address model
        migrations.RunPython(remove_address_contenttype),

        # Rename temp fields to the correct name ("new_address" -> "address")
        migrations.RenameField(
            model_name="institution",
            old_name="new_address",
            new_name="address"
        ),
        migrations.RenameField(
            model_name="participant",
            old_name="new_address",
            new_name="address"
        ),
    ]
