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
import json

from django import http
from django.views import generic
from django.db.models.fields import related
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from swoptact import models
from swoptact.decorators import swoptact_login_required

class APIMixin:
    """
    Provides a JSON based to be used by the API
    """

    def __init__(self, *args, **kwargs):
        self._objects_created = []
        # Special processors for certain fields for the process_json method
        # @@: ... could be a class level attribute, though that make
        #   stuff a bit messy when it comes to mapping to instance level
        #   methods :P
        self.field_processors = {}

        return super(APIMixin, self).__init__(*args, **kwargs)

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
        pairs = [p for p in ["{}={}".format(k, v) for k, v in data.items()]]
        return "&".join(pairs)

    def _process_field_general(self, body, model, field_name, value):
        # Find the field that the model is on.
        field = model._meta.get_field(field_name)

        if isinstance(field, related.RelatedField):
            if value is None:
                return

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
        for field_name, value in body.items():
            field_processor = self.field_processors.get(
                field_name, self._process_field_general)
            field_processor(body, model, field_name, value)

        return body

    def post(self, request, *args, **kwrgs):
        request.POST = self.process_json(request.body)
        return super(APIMixin, self).post(request, *args, **kwrgs)

    def put(self, request, *args, **kwrgs):
        request.POST = self.process_json(request.body)
        return super(APIMixin, self).put(request, *args, **kwrgs)

    def form_invalid(self, form, *args, **kwargs):
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

        return self.render_to_response(
            context=self.get_context_data(form=form),
            status=400
        )

    def get_context_data(self, *args, **context):
        """
        Provides the context data - This MUST be JSON serializable

        This is provided as ContextMixin.get_context_data adds in the view
        object which is not JSON serializable and will raise exceptions.
        """
        if args and context:
            raise Exception("Only pass either positional or kwargs")

        # If there is the "form" element in the context convert it into a dict
        if "form" in context:
            context["form"] = {
                "errors": context["form"].errors,
                "cleaned_data": context["form"].cleaned_data,
                "has_changed": context["form"].has_changed(),
            }

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
    fields = ["id", "name", "primary_phone",
              "secondary_phone", "email", "address"]

    def __init__(self, *args, **kwargs):
        super(ParticipantAPI, self).__init__(*args, **kwargs)
        self.field_processors = {
            "institution": self._process_institution_field}

    def _process_institution_field(self, body, model, field_name, value):
        if value == "" or value is None:
            # Nah, nothing to do
            return

        # Try to see if we have an institution with this name
        try:
            result = models.Institution.objects.get(name__iexact=value)
            body[field_name] = result.id
            return

        except models.Institution.DoesNotExist:
            # Nope!  Let's make a new one.
            new_institution = models.Institution(name=value)
            new_institution.save()
            self._objects_created.append(new_institution)
            body[field_name] = new_institution.id
            return

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
    fields = ["name", "primary_phone", "secondary_phone",
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

        # Iterate over participants and serialize
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

        # Add to the event
        self.object.participants.add(self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

class ContactUnlinking(APIMixin, generic.DetailView):
    """
    Provides a mechanism to unlink Contacts from Institutions
    """
    model = models.Institution

    @property
    def contact(self):
        """ Looks up and returns Participant """
        participant_pk = self.kwargs.get("participant_id")
        self.object = self.get_object()
        contact_id = models.Contact.objects.filter(institution=self.object.id).filter(participant=participant_pk)
        return models.Contact.objects.get(pk=contact_id[0].id)

    def delete(self, request, *args, **kwargs):
        """ Unlink a participant """
        self.object = self.get_object()
        # Remove the contact entry entirely
        if self.contact:
            self.contact.delete()

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

class AvailableTagsAPI(APIMixin, generic.ListView):
    """
    Provides a list of tags which the user has access to
    """

    model = models.Tag

    def get_queryset(self):
        """ Gets all tags that the user is able to access """
        tags = []
        for group in self.user.groups.all():
            tags += list(self.model.objects.filter(group=group))
        return tags

    def get(self, request, *args, **kwargs):
        self.user = get_user_model().objects.get(pk=request.user.pk)
        return self.render_to_response(self.get_context_data())


    def get_context_data(self, **context):
        context = super(AvailableTagsAPI, self).get_context_data(**context)
        context["available"] = [t.serialize() for t in self.get_queryset()]
        return context
