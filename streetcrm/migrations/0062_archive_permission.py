# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def change_staff_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    staff = Group.objects.get(name="staff")
    
    participant_ct = ContentType.objects.get(
        app_label="streetcrm",
        model="participant"
    )

    staff.permissions.remove(Permission.objects.get(
        codename="delete_participant",
        content_type=participant_ct
    ))

    staff.permissions.add(Permission.objects.get(
        codename="archive_participant",
        content_type=participant_ct
    ))


def create_participant_archive_permission(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Find the ContentType for the user model
    participant_ct = ContentType.objects.get(app_label="streetcrm", model="participant")

    # Create the permission for changing password
    archive_permission = Permission(
        codename="archive_participant",
        name="Can archive participant",
        content_type=participant_ct
    )
    archive_permission.save()


    
class Migration(migrations.Migration):
    dependencies = [
        ('streetcrm', '0061_auto_20160420_1340'),
    ]

    operations = [
        # Add an archive participant permission
        migrations.RunPython(create_participant_archive_permission),

        # Disallow staff from deleting participants
        migrations.RunPython(change_staff_permissions),
    ]
