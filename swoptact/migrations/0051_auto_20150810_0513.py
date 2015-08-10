# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_own_contact(apps, schema_editor):
    Institution = apps.get_model("swoptact", "Institution")

    for institution in Institution.objects.all():
        # Iterate over each contact and write them onto the contacts many to many
        for contact in institution.contact.all():
            institution.contacts.add(contact)

def remove_stale_contact_content_type(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    contact_ct = ContentType.objects.filter(
        app_label="swoptact",
        model="contact"
    )

    if contact_ct.exists():
        contact_ct.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0050_auto_20150807_1436'),
    ]

    operations = [
        # Add new many to many field
        migrations.AddField(
            model_name="institution",
            name="contacts",
            field=models.ManyToManyField(to="swoptact.Participant")
        ),

        # Run the data migration
        migrations.RunPython(migrate_own_contact),

        # Remove the old many to many field.
        migrations.RemoveField(
            model_name="institution",
            name="contact"
        ),

        # Remove the old Contact model
        migrations.DeleteModel(
            name="contact"
        ),

        # Remove stale ContentType for "contact" model
        migrations.RunPython(remove_stale_contact_content_type),
    ]
