# StreetCRM is a list of contacts with a history of their event attendance
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

def add_staff_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Look up the ContentTypes for the models we're using
    tag_ct = ContentType.objects.get(
        app_label="streetcrm",
        model="tag"
    )


    # Find the staff group
    staff = Group.objects.get(name="staff")


    # Staff can add a tag
    staff.permissions.add(Permission.objects.get(
        codename="add_tag",
        content_type=tag_ct
    ))

    # Staff can change a tag
    staff.permissions.add(Permission.objects.get(
        codename="change_tag",
        content_type=tag_ct
    ))



class Migration(migrations.Migration):
    """
    Adds permissions to the "staff" group, based on migration
    0049_add_permissions_to_groups.py.  See further documentation there.

    """
    dependencies = [
        ("contenttypes", "__first__"),
        ("auth", "__first__"),
        ('streetcrm', '0051_auto_20150810_0513'),
        ('streetcrm', '0053_auto_20150923_1723'),
    ]

    operations = [
        # Add the desired permissions to the staff group
        migrations.RunPython(add_staff_permissions),
    ]

    def apply(self, *args, **kwargs):
        # Verify that contenttype has been migrated first
        if len(ContentType.objects.all()) <= 0:
            raise exceptions.DjangoRuntimeWarning("You must run \"python manage.py migrate auth\" first.")
        return super(Migration, self).apply(*args, **kwargs)
