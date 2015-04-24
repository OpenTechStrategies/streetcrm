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

from django import http
from django.views import generic
from django.db.models.fields import related
from django.utils.decorators import method_decorator
from django.forms.models import modelform_factory
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required


from swoptact import models
from swoptact.decorators import swoptact_login_required

class APIMixin:
    """
    Provides a JSON based to be used by the API
    """

    def __init__(self, *args, **kwargs):
        self._objects_created = []

    @method_decorator(swoptact_login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(APIMixin, self).dispatch(*args, **kwargs)

    def produce_response(self):
        """ Produces a HTTPResponse object with the serialized object """
        # Serialize the object to JSON
        json_object = self.object.serialize()

        # Serialize the output and use that as the context
        return self.render_to_response(self.get_context_data(**json_object))

    def dict_to_formencoded(self, data):
        """ Produces form-encoded data from a python dictionary """
        pairs =  [p for p in ["{}={}".format(k, v) for k, v in data.items()]]
        return "&".join(pairs)

    def process_json(self, body, model=None):
        """
        Produces value for request.POST from a JSON encoded body

        This initially decodes the body to UTF-8 into JSON, then looks for
        attributes which present a relationship (ForeignKey) that needs to be
        mapped to an ID for that object. If an ID does NOT exist then a new
        object will be created and the newly created object's ID will be used.
        """
        body = json.loads(body.decode("utf-8"))

        # If the model isn't specified use the self.model value
        if model is None:
            model = self.model

        # Look for relations
        for field, value in body.items():
            # Find the field that the model is on.
            field = model._meta.get_field(field)

            if isinstance(field, related.RelatedField):
                if value is None:
                    continue

                # Check if the object needs to be created.
                if "id" in value or "pk" in value:
                    # Object already exists - just look it up.
                    pk = value["pk"] if "pk" in value else value["id"]
                    instance = field.rel.to.objects.get(pk=pk)

                    # Save the values onto the model
                    for k, v in value.items():
                        setattr(instance, k, v)

                    # Save the object back
                    instance.save()

                    value = instance
                else:
                    # Create the object.
                    value = field.rel.to(**value)
                    value.save()

                    # we need to keep track we made it
                    self._objects_created.append(value)

                # The ID of the object should be stored as the value
                body[field.name] = value.id

        return body

    def post(self, request, *args, **kwrgs):
        request.POST = self.process_json(request.body)
        return super(APIMixin, self).post(request, *args, **kwrgs)

    def put(self, request, *args, **kwrgs):
        request.POST = self.process_json(request.body)
        return super(APIMixin, self).put(request, *args, **kwrgs)

    def form_invalid(self, *args, **kwargs):
        """
        Removes all created models from nested JSON

        The self.process_json method can create models that are defined in the
        JSON prior to knowing if the form is valid, this is because to validate
        the form, it needs to have the models created. The method helpfully
        builds up a list of any and all created models for this purpose and
        they are deleted to prevent objects being created not associated or used
        by anything.

        If you subclass and don't call this parent method make sure you also
        clean up these objects!
        """
        for obj in self._objects_created:
            obj.delete()

        return super(APIMixin, self).form_invalid(*args, **kwargs)

    def get_context_data(self, *args, **context):
        """
        Provides the context data - This MUST be JSON serializable

        This is provided as ContextMixin.get_context_data adds in the view
        object which is not JSON serializable and will raise exceptions.
        """
        if args and context:
            raise Exception("Only pass either positional or kwargs")

        return args or context

    def render_to_response(self, context, **response_kwargs):
        """ Provides a JSON response based on the context provided """
        if isinstance(context, (dict, list, tuple)):
            context = json.dumps(context)

        return http.HttpResponse(
            context,
            content_type="application/json",
            **response_kwargs
        )

class ParticipantAPI(APIMixin, generic.UpdateView):
    """
    Provides the view to retrive, create and update a participant

    If called with the PUT verb this expects a JSON serialized participant
    object which is the updated participant that will be saved.
    """

    model = models.Participant
    fields = ["id", "first_name", "last_name", "phone_number", "secondary_phone",
              "email", "address"]

    def get(self, request, *args, **kwargs):
        """ Retrival of an existing participant """
        # Lookup the object that we want to return
        self.object = self.get_object()
        return self.produce_response()

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save()
        return self.produce_response()

class CreateParticipantAPI(APIMixin, generic.CreateView):
    """
    Creates a participant from a JSON API
    """

    model = models.Participant
    fields = ["first_name", "last_name", "phone_number", "secondary_phone",
              "email", "address"]

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save()
        return self.produce_response()

class EventParticipantsAPI(APIMixin, generic.DetailView):
    """
    Provides a list of all participants linked to a event
    """

    model = models.Event

    def get(self, request, *args, **kwargs):
        """ Retrival of an existing event """
        self.object = self.get_object()

        # Iterate over pariticipants and serialize
        participants = [p.serialize() for p in self.object.participants.all()]

        return self.render_to_response(context=participants)

class EventAvailableAPI(APIMixin, generic.DetailView):
    """
    Provides a list of all participants that are not linked to an event
    """
    model = models.Event

    def get(self, request, *args, **kwargs):
        """ Retrival of an existing event """
        self.object = self.get_object()

        # Iterate over participants so we can exclude from available list.
        linked = [p.id for p in self.object.participants.all()]
        available = models.Participant.objects.all().exclude(id__in=linked)
        available = [a.serialize() for a in available]

        return self.render_to_response(context=available)

class EventLinking(APIMixin, generic.DetailView):
    """
    Provides a mechanism to link and unlink Participants from Events
    """
    model = models.Event

    @property
    def participant(self):
        """ Looks up and returns Participant """
        participant_pk = self.kwargs.get("participant_id")
        return models.Participant.objects.get(pk=participant_pk)

    def delete(self, request, *args, **kwargs):
        """ Unlink a participant """
        self.object = self.get_object()

        # Remove from the event
        self.object.participants.remove(self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """ Links a participant """
        self.object = self.get_object()

        # Remove from the event
        self.object.participants.add(self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())
