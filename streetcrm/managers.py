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

from django.db import models

class ArchiveManager(models.Manager):
    """
    Model manager for archiable objects.

    This queryset is to allow you to easily search through unarchived or
    archived objects. There are several different queries that can be done
    to get different QuerySets containing both unarchived and archived objects.

    Examples
    --------

    Unarchived objects:
    >>> Model.objects.unarchived()

    Archived objects:
    >>> Model.objects.archived()

    Both unarchived and archived objects:
    >>> Models.objects.all()

    Filter for archived objects that were archived after a date:
    >>> some_date = datetime.datetime(day=20, month=7, year=2015)
    >>> Models.objects.filter(archived__gte=some_date)
    """

    def archived(self):
        return self.filter(archived=True)

    def unarchived(self):
        return self.filter(archived=False)

    def filter(self, *args, **kwargs):
        archived = kwargs.pop("archived", False)
        qs = super(ArchiveManager, self).filter(*args, **kwargs)

        # If archive is False, exclude archived results.
        if archived is False:
            qs = qs.filter(archived__isnull=True)

        # If archive is True, only return archived results.
        elif archived is True:
            qs = qs.exclude(archived__isnull=True)

        return qs
