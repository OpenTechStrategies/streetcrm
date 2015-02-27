# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015
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

class Address(models.Model):
    """ Representation of an address in Chicago """
    STREET_TYPES = (
        ("st", "Street"),
        ("av", "Avenue"),
        ("blvd", "Boulevard"),
        ("rd", "Road"),
    )

    STREET_DIRECTIONS = (
        ("n", "North"),
        ("e", "East"),
        ("s", "South"),
        ("w", "West"),
    )

    street_number = models.IntegerField()
    street_direction = models.CharField(max_length=1, choices=STREET_DIRECTIONS)
    street_name = models.CharField(max_length=255)
    street_type = models.CharField(max_length=20, choices=STREET_TYPES)

class Participant(models.Model):
    """ Representation of a person who can participate in a Event """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    email = models.EmailField()
    address = models.ForeignKey(Address)

class Event(models.Model):

    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    site = models.CharField(max_length=255)
    address = models.ForeignKey(Address)
    participants = models.ManyToManyField(Participant)
