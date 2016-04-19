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

import json

from django import test
from django.contrib import auth
from django.core import urlresolvers

from streetcrm import models

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
        participant = models.Participant(
            name="John Smith"
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

        # Validate attributes in the JSON
        self.assertEqual(json_participant["name"], participant.name)

    def test_create_participant(self):
        """ Test that you can create a participant via the API """
        # Create the data to post
        participant = {
            "name": "Albert Einstein",
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
        self.assertEqual(participant_obj.name, participant["name"])

    def test_update_participant(self):
        """ Test that you can update a participant via the API """
        # Create a participant that can be modified later
        participant = models.Participant(
            name="John Smith"
        )
        participant.save()

        # Verify we have the data we thought we do (we should)
        self.assertEqual(participant.name, "John Smith")

        # Now provide some data to change it
        data = {
            "name": "Johan Smith"
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

        self.assertEqual(participant_json["name"], data["name"])

        # Finally look up the original objects and verify the changes
        # are reflected in the database.
        participant = models.Participant.objects.get(pk=participant.pk)

        # Check the participant in the DB with submitted data
        self.assertEqual(participant.name, data["name"])
