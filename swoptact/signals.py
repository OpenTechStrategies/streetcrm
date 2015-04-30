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

from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group

def group_hierarchy_maintainer(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Maintains the hierarchy: adds a user to "lower" groups in the hierarchy.

    There is a dict defined in the settings file which specifes the hierarchy
    of the groups. When the user is added to the group it will iterate through
    level of lower groups and add those, this signal will be re-trigged on those
    adds to add them to the levels below those.
    """
    # Only do this once the user has been added to the group
    if action != "post_add":
        return

    # Only do this for groups
    if isinstance(model, Group):
        return

    # Lookup all the groups
    groups = [Group.objects.get(pk=pk) for pk in pk_set]

    # Iterate over the groups and find "lower" ranking groups
    # I wonder if this could be simplified to a list (set) comprehension
    lower_groups = set()
    for group in groups:
        if group.name in settings.GROUP_HIERARCHY:
            lower = settings.GROUP_HIERARCHY[group.name]

            # Lookup all group objects
            lower_groups |= {Group.objects.get(name=name) for name in lower}

    # Add user to groups
    for group in lower_groups:
        instance.groups.add(group)


signals.m2m_changed.connect(
    group_hierarchy_maintainer
)