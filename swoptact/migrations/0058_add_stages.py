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

from django.db import migrations

def add_initial_stages(apps, schema_editor):
    """This will add the 'primary,' 'secondary,' 'tertiary,' and 'not
applicable' stages of leader growth. """
    Stage = apps.get_model("swoptact", "LeaderStage")

    # Make the groups
    primary_stage = Stage(name="Primary")
    primary_stage.save()

    secondary_stage = Stage(name="Secondary")
    secondary_stage.save()

    tertiary_stage = Stage(name="Tertiary")
    tertiary_stage.save()

    not_applicable_stage = Stage(name="Not applicable")
    not_applicable_stage.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0057_auto_20151019_1254'),
    ]

    operations = [
        migrations.RunPython(add_initial_stages)
    ]
