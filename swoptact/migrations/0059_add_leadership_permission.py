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

def add_admin_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    leadershipgrowth_ct = ContentType.objects.get(
        app_label="swoptact",
        model="leadershipgrowth"
    )

    admin = Group.objects.get(name="admin")
    
    # admin can view and change leader stages
    admin.permissions.add(Permission.objects.get(
        codename="add_leadershipgrowth",
    ))
    admin.permissions.add(Permission.objects.get(
        codename="change_leadershipgrowth",
    ))

def add_staff_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")

    leadershipgrowth_ct = ContentType.objects.get(
        app_label="swoptact",
        model="leadershipgrowth"
    )

    staff = Group.objects.get(name="staff")
    
    # staff can view and change leader stages
    staff.permissions.add(Permission.objects.get(
        codename="add_leadershipgrowth",
        content_type=leadershipgrowth_ct
    ))
    staff.permissions.add(Permission.objects.get(
        codename="change_leadershipgrowth",
        content_type=leadershipgrowth_ct
    ))

    
class Migration(migrations.Migration):    
    dependencies = [
        ("contenttypes", "__first__"),
        ("auth", "__first__"),
        ("swoptact", "0058_add_stages"),
    ]

    operations = [
        # Add the desired permissions to the admin group
        migrations.RunPython(add_admin_permissions),

        # Add the desired permissions to the staff group
        migrations.RunPython(add_staff_permissions),

    ]
