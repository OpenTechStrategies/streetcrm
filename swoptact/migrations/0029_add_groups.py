# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Open Tech Strategies, LLC
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

from django.db import migrations

def add_initial_groups(apps, schema_editor):
    """ This will add the 'admin', 'organizers' and 'leaders' groups """
    Group = apps.get_model("auth", "Group")

    # Make the groups
    admin_group = Group(name="admin")
    admin_group.save()

    organizer_group = Group(name="organizer")
    organizer_group.save()

    leader_group = Group(name="leader")
    leader_group.save()

class Migration(migrations.Migration):

    dependencies = [
        # I'm not sure why we need to have 0028_auto_20150429_1248 as a
        # dependency but it complains without so it's there.
        ('swoptact', '0028_auto_20150429_1248'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(add_initial_groups)
    ]