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

import json

from django import test
from django.contrib import auth
from django.core import urlresolvers

from swoptact import models

class APITest(test.TestCase):
    """ Test for API endpoints """

    def setUp(self):
        """ Setup user account and self.client """
        username = "test_admin"
        password = "a-really-good-password!"
        email = "admin@example.com"

        # Create super user to use for testing
        self.UserModel = auth.get_user_model()
        self.UserModel._default_manager.db_manager().create_superuser(
            username=username,
            password=password,
            email=email
        )

        # Authenticate self.client as this user
        self.client.login(
            username=username,
            password=password
        )


    def test_get_participant(self):
        """ Tests a participant that exists can be fetched """
        # Create a participant to fetch
        address = models.Address(
            number=72,
            direction=models.Address.DIRECTIONS[0][0],
            name="Main",
            type=models.Address.TYPES[0][0],
        )
        address.save()
        participant = models.Participant(
            first_name="John",
            last_name="Smith",
            address=address
        )
        participant.save()

        # Try to fetch participant
        endpoint = urlresolvers.reverse(
            "api-participants",
            kwargs={"pk": participant.pk}
        )
        response = self.client.get(endpoint)

        # Validate request returned 200
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response we should have recieved
        json_participant = json.loads(response.content.decode("utf-8"))
        json_address = json_participant["address"]

        # Validate attributes in the JSON
        self.assertEqual(json_participant["first_name"], participant.first_name)
        self.assertEqual(json_participant["last_name"], participant.last_name)

        self.assertEqual(json_address["number"], address.number)
        self.assertEqual(json_address["direction"], address.direction)
        self.assertEqual(json_address["name"], address.name)
        self.assertEqual(json_address["type"], address.type)

    def test_create_participant(self):
        """ Test that you can create a participant via the API """
        # Create the data to post
        participant = {
            "first_name": "Albert",
            "last_name": "Einstein",
            "address": {
                "number": 27,
                "direction": models.Address.DIRECTIONS[0][0],
                "name": "Union",
                "type": models.Address.TYPES[0][0],
            }
        }

        # Post the participant
        endpoint = urlresolvers.reverse("api-create-participants")
        response = self.client.post(
            endpoint,
            content_type="application/json",
            data=json.dumps(participant)
        )

        # Check that the response is okay
        self.assertEqual(response.status_code, 200)

        # Parse data we're sent back and look up participant
        json_response = json.loads(response.content.decode("utf-8"))
        participant_obj = models.Participant.objects.get(
            id=json_response["id"]
        )

        self.assertTrue(participant_obj is not None)
        self.assertEqual(participant_obj.first_name, participant["first_name"])
        self.assertEqual(participant_obj.last_name, participant["last_name"])

        address = participant["address"]
        address_obj = participant_obj.address

        self.assertTrue(address_obj is not None)
        self.assertEqual(address_obj.number, address["number"])
        self.assertEqual(address_obj.direction, address["direction"])
        self.assertEqual(address_obj.name, address["name"])
        self.assertEqual(address_obj.type, address["type"])

    def test_update_participant(self):
        """ Test that you can update a participant via the API """
        # Create a participant that can be modified later
        address = models.Address(
            number=72,
            direction=models.Address.DIRECTIONS[0][0],
            name="Main",
            type=models.Address.TYPES[0][0],
        )
        address.save()
        participant = models.Participant(
            first_name="John",
            last_name="Smith",
            address=address
        )
        participant.save()

        # Verify we have the data we thought we do (we should)
        self.assertEqual(participant.first_name, "John")
        self.assertEqual(address.number, 72)

        # Now provide some data to change it
        data = {
            "first_name": "Johan",
            "last_name": "Smith",
            "address": {
                "id": address.id,
                "number": 27,
                "direction": address.direction,
                "name": address.name,
                "type": address.type,
            }
        }

        # Submit it via a PUT
        endpoint = urlresolvers.reverse(
            "api-participants",
            kwargs={"pk": participant.pk}
        )

        response = self.client.put(
            endpoint,
            content_type="application/json",
            data=json.dumps(data)
        )

        # Check the response
        self.assertEqual(response.status_code, 200)

        # Verify I get back the JSON I expect
        participant_json = json.loads(response.content.decode("utf-8"))

        self.assertEqual(participant_json["first_name"], data["first_name"])
        self.assertEqual(participant_json["last_name"], data["last_name"])

        address_json = participant_json["address"]
        address_data = data["address"]

        self.assertEqual(address_json["number"], address_data["number"])
        self.assertEqual(address_json["direction"], address_data["direction"])
        self.assertEqual(address_json["name"], address_data["name"])
        self.assertEqual(address_json["type"], address_data["type"])

        # Finally look up the original objects and verify the changes
        # are reflected in the database.
        address = models.Address.objects.get(pk=address.pk)
        participant = models.Participant.objects.get(pk=participant.pk)

        # Check the address in the DB with the submitted data
        self.assertEqual(address.number, address_data["number"])
        self.assertEqual(address.direction, address_data["direction"])
        self.assertEqual(address.name, address_data["name"])
        self.assertEqual(address.type, address_data["type"])

        # Check the participant in the DB with submitted data
        self.assertEqual(participant.first_name, data["first_name"])
        self.assertEqual(participant.last_name, data["last_name"])
        self.assertEqual(participant.address.pk, address.pk)
