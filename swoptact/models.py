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
    TYPES = (
        ("St", "Street"),
        ("Av", "Avenue"),
        ("Blvd", "Boulevard"),
        ("Rd", "Road"),
    )

    DIRECTIONS = (
        ("N", "North"),
        ("E", "East"),
        ("S", "South"),
        ("W", "West"),
    )

    class Meta:
        verbose_name_plural = "Addresses"

    number = models.IntegerField()
    direction = models.CharField(max_length=1, choices=DIRECTIONS)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPES)

    def __str__(self):
        return "{number} {direction} {name} {type}".format(
            number=self.number,
            direction=self.direction,
            name=self.name,
            type=self.type
        )

class Participant(models.Model):
    """ Representation of a person who can participate in a Event """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    email = models.EmailField()
    address = models.ForeignKey(Address)

    def __str__(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name,
            last_name=self.last_name
        )

class Event(models.Model):

    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    site = models.CharField(max_length=255)
    address = models.ForeignKey(Address)
    participants = models.ManyToManyField(Participant)

    def __str__(self):
        return self.name
