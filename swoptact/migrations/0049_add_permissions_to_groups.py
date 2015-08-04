# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Local Initiatives Support Corporation (LISC)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.core import exceptions
from django.db import models, migrations
from django.contrib.contenttypes.models import ContentType

def add_leader_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Look up the ContentTypes for the models we're using
    event_ct = ContentType.objects.get(
        app_label="swoptact",
        model="event"
    )
    institution_ct = ContentType.objects.get(
        app_label="swoptact",
        model="institution"
    )
    participant_ct = ContentType.objects.get(
        app_label="swoptact",
        model="participant"
    )

    # Find the leader group
    leader = Group.objects.get(name="leader")

    # Leaders can add events
    leader.permissions.add(Permission.objects.get(
        codename="add_event",
        content_type=event_ct
    ))

    # Leaders can change events
    leader.permissions.add(Permission.objects.get(
        codename="change_event",
        content_type=event_ct
    ))

    # Leaders can add institutions
    leader.permissions.add(Permission.objects.get(
        codename="add_institution",
        content_type=institution_ct
    ))

    # Leaders can change institution
    leader.permissions.add(Permission.objects.get(
        codename="change_institution",
        content_type=institution_ct
    ))

    # Leaders can add participant
    leader.permissions.add(Permission.objects.get(
        codename="add_participant",
        content_type=participant_ct
    ))

    # Leaders can change participant
    leader.permissions.add(Permission.objects.get(
        codename="change_participant",
        content_type=participant_ct
    ))

def add_admin_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Lookup admin group
    admin = Group.objects.get(name="admin")

    # Look up the ContentTypes for the models we're using
    event_ct = ContentType.objects.get(
        app_label="swoptact",
        model="event"
    )
    institution_ct = ContentType.objects.get(
        app_label="swoptact",
        model="institution"
    )
    participant_ct = ContentType.objects.get(
        app_label="swoptact",
        model="participant"
    )

    tag_ct = ContentType.objects.get(
        app_label="swoptact",
        model="tag"
    )

    contact_ct = ContentType.objects.get(
        app_label="swoptact",
        model="contact"
    )

    user_ct = ContentType.objects.get(
        app_label="auth",
        model="user"
    )

    # Admins can archive an event
    admin.permissions.add(Permission.objects.get(
        codename="delete_event",
        content_type=event_ct
    ))

    # Admins can archive an institution
    admin.permissions.add(Permission.objects.get(
        codename="delete_institution",
        content_type=institution_ct
    ))

    # Admin can archive a participant
    admin.permissions.add(Permission.objects.get(
        codename="delete_participant",
        content_type=participant_ct
    ))

    # Admins can add a tag
    admin.permissions.add(Permission.objects.get(
        codename="add_tag",
        content_type=tag_ct
    ))

    # Admins can change a tag
    admin.permissions.add(Permission.objects.get(
        codename="change_tag",
        content_type=tag_ct
    ))

    # Admins can archive a tag
    admin.permissions.add(Permission.objects.get(
        codename="delete_tag",
        content_type=tag_ct
    ))

    # Admin can add a contact
    admin.permissions.add(Permission.objects.get(
        codename="add_contact",
        content_type=contact_ct
    ))

    # Admin can change a contact
    admin.permissions.add(Permission.objects.get(
        codename="change_contact",
        content_type=contact_ct
    ))

    # Admins can archive a contact
    admin.permissions.add(Permission.objects.get(
        codename="delete_contact",
        content_type=contact_ct
    ))

    # Admin can change their password
    admin.permissions.add(Permission.objects.get(
        codename="can_change_password",
        content_type=user_ct
    ))

    # Admin can add users
    admin.permissions.add(Permission.objects.get(
        codename="add_user",
        content_type=user_ct
    ))

    # Admin can change users
    admin.permissions.add(Permission.objects.get(
        codename="change_user",
        content_type=user_ct
    ))

    # Admin can delete users (this is NOT archive)
    admin.permissions.add(Permission.objects.get(
        codename="delete_user",
        content_type=user_ct
    ))


def create_password_change_permission(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Find the ContentType for the user model
    user_ct = ContentType.objects.get(app_label="auth", model="user")

    # Create the permission for changing password
    change_pw_permission = Permission(
        codename="can_change_password",
        name="Can change password",
        content_type=user_ct
    )
    change_pw_permission.save()

class Migration(migrations.Migration):
    """
    Adds permissions to the "leader" group and creates the password change
    permission.

    This requires that the "auth" app migrations are run first on fresh
    installs:

        $ python manage.py migrate auth

    This is because the ContentTypes which are used to create permissions
    are created on the "post_migrate" Django signal. This is only fired once
    all migrations have been run in the command. Migrating auth creates the
    Permission, Group and User models (and migrates the "contenttypes" app)
    which are required for this migration as well as triggering the ContentType
    objects to be made for those models.

    If the user forgets to run the auth migrations there is no damage done, they
    simply have to just re-run the command and it'll finish as the ContentType
    objects will exist then. Once this migration has been run there is no need to
    continue running the "auth" migrations individually, the general "migrate"
    command can be used as normal.
    """
    dependencies = [
        ("contenttypes", "__first__"),
        ("auth", "__first__"),
        ("swoptact", "0048_auto_20150720_1822"),
    ]

    operations = [
        # Add a change password permission
        migrations.RunPython(create_password_change_permission),

        # Add the desired permissions to the leader group
        migrations.RunPython(add_leader_permissions),

        # Add the desired permissions to the admin group
        migrations.RunPython(add_admin_permissions),
    ]

    def apply(self, *args, **kwargs):
        # Verify that contenttype has been migrated first
        if len(ContentType.objects.all()) <= 0:
            raise exceptions.DjangoRuntimeWarning("You must run \"python manage.py migrate auth\" first.")
        return super(Migration, self).apply(*args, **kwargs)
