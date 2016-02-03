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
from django.core import serializers
from django.conf import settings
from django.views import generic
from django.db.models.fields import related
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.models import (
    LogEntry, ADDITION, CHANGE, DELETION)
from django.utils.encoding import force_text

from swoptact import models
from swoptact.decorators import swoptact_login_required

# Needed for reporting validation errors. Otherwise execution will
# stumble when trying to serialize one of our models (e.g., Institution)
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.SerializeableMixin):
            return obj.serialize()
        return json.JSONEncoder.default(self, obj)

def process_field_general(api_view, body, model, field_name, value):
    """
    General field processor converting json representation
    to something to attach to the model
    """
    # Find the field that the model is on.
    try:
        field = model._meta.get_field(field_name)
    # the field does not exist on the model (in practice, this should only be "nonce")
    except Exception:
        field = None
        body[field_name] = value

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
            api_view._objects_created.append(value)

        # The ID of the object should be stored as the value
        body[field.name] = value.id



class APIMixin:
    """
    Provides a JSON based to be used by the API
    """

    field_processors = {}

    def __init__(self, *args, **kwargs):
        self._objects_created = []

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
                field_name, process_field_general)
            field_processor(self, body, model, field_name, value)

        return body

    def post(self, request, *args, **kwrgs):
        # If this is not a PUT
        try:
            # this is a PUT
            is_put = request.POST['id']
        except:
            request.POST = self.process_json(request.body)
            is_put = None

        try:
            sent_nonce = request.POST['nonce']
        except KeyError:
            sent_nonce = None
        
        if not sent_nonce:
            print("DEBUG: nope on the nonce -- this should send an error")

        # by the way, super looks for APIMixin's parent class and calls
        # the post() method of *that* class (probably Models.model, or
        # something like that)
        if is_put:
            try:
                request.POST['institution'] = request.POST['institution']['id']
            except:
                request.POST['institution'] = request.POST['institution']
        
        new_object = super(APIMixin, self).post(request, *args, **kwrgs)
        if is_put is None:
            object_json = self.process_json(new_object._container[0])
            new_id = object_json['id']
            # save new_id and nonce to the `swoptact_nonce_to_id` table :)
            new_nonce = models.nonce_to_id(participant=new_id, nonce=sent_nonce)
            new_nonce.save()

        return new_object

    def put(self, request, *args, **kwrgs):
        incoming_fields = self.process_json(request.body)
        # we manage the nonce -> id transition here
        if incoming_fields['nonce'] and not incoming_fields['id']:
            #look up the id in the nonce_to_id table
            matching_queryset = models.nonce_to_id.objects.filter(
                nonce=incoming_fields['nonce'])
            matching_id = matching_queryset[0].participant
            incoming_fields['id'] = matching_id
        elif incoming_fields['id'] and incoming_fields['nonce']:
            #find and delete the matching rows from nonce_to_id
            removable_queryset = models.nonce_to_id.objects.filter(
                nonce=incoming_fields['nonce'],
                participant=incoming_fields['id']) 
            for obj in removable_queryset:
                obj.delete()
        elif not incoming_fields['id'] and not incoming_fields['nonce']:
            print("send an error")

        # get the db's record for this object, using the incoming (or
        # produced above) ID
        #
        # compare the old values of the fields in incoming_fields to the
        # values of the fields in the database
        #
        # if they match, update the request with the new values
        #
        # create a new request.POST from the db object, with all fields
        # and updated values, and send that to the post() function.
        #
        # CAN'T ASSUME IT'LL BE A PARTICIPANT!
        relevant_participant = models.Participant.objects.get(
            id=incoming_fields['id'])
        request.POST = relevant_participant.serialize()
        #get rid of id and nonce before this for loop
        del incoming_fields['nonce']
        del incoming_fields['id']
        
        for field in incoming_fields:
            # Check to see whether the object has such a field
            try:
                getattr(relevant_participant, field)
                field_exists = True
            except AttributeError:
                field_exists = False
            
            if field_exists:
                # then whether it has a value
                if request.POST[field]:
                    server_field = request.POST[field]
                else:
                    server_field = None

                # should check whether the "old" exists
                client_original = incoming_fields[field]['old']
                if client_original == server_field or client_original == server_field.id:
                    # update the field
                    request.POST[field] = incoming_fields[field]['new']
                else:
                    print("send error: old doesn't match what's on the server")
            else:
                print("DEBUG: field " + field + " does not exist in this object")

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
            context = json.dumps(context, cls=MyEncoder)

        return http.HttpResponse(
            context,
            content_type="application/json",
            **response_kwargs
        )


class LogChangeMixin:
    """
    Log a successful POST as a change of fields
    """
    def _log_change(self, request):
        object = self.get_object()
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=CHANGE,
            change_message="Changed fields",
        )

    def post(self, request, *args, **kwargs):
        response = super(LogChangeMixin, self).post(
            request, *args, **kwargs)
        self._log_change(request)
        return response

    def put(self, request, *args, **kwargs):
        response = super(LogChangeMixin, self).put(
            request, *args, **kwargs)
        self._log_change(request)
        return response


# not used yet..
def log_create(self, request, new_object):
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(new_object).pk,
        object_id=new_object.pk,
        object_repr=force_text(new_object),
        action_flag=ADDITION
    )

def log_linking(request, main_object, linking_object):
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(main_object).pk,
        object_id=main_object.pk,
        object_repr=force_text(main_object),
        action_flag=CHANGE,
        change_message="Linked \"%s\"" % force_text(linking_object),
    )

def log_unlinking(request, main_object, linking_object):
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(main_object).pk,
        object_id=main_object.pk,
        object_repr=force_text(main_object),
        action_flag=CHANGE,
        change_message="Unlinked \"%s\"" % force_text(linking_object),
    )


def process_institution_field(api_view, body, model, field_name, value):
    if value == "" or value is None:
        # Nah, nothing to do
        return
    # account for the old and new values, now

    body[field_name] = {'old': None, 'new': None}
    
    # Find the id of the old institution
    if value['old']:
        result = models.Institution.objects.get(name__iexact=value['old'])
        body[field_name]['old'] = result.id
    else:
        body[field_name]['old'] = None
    
    # Try to see if we have an institution with this name (for the new institution)
    try:
        result = models.Institution.objects.get(name__iexact=value['new'])
        body[field_name]['new'] = result.id

    except models.Institution.DoesNotExist:
        # Nope!  Let's make a new one.
        new_institution = models.Institution(name=value['new'])
        new_institution.save()
        api_view._objects_created.append(new_institution)
        body[field_name]['new'] = new_institution.id

    return


class ParticipantAPI(LogChangeMixin, APIMixin, generic.UpdateView):
    """
    Provides the view to retrieve, create and update a participant

    If called with the PUT verb this expects a JSON serialized participant
    object which is the updated participant that will be saved.
    """

    model = models.Participant
    fields = ["id", "name", "primary_phone",
              "secondary_phone", "email", "participant_street_address",
              "institution", "title"]
    field_processors = {
            "institution": process_institution_field}

    def get(self, request, *args, **kwargs):
        """ Retrieval of an existing participant """
        # Lookup the object that we want to return
        self.object = self.get_object()
        return self.produce_response()

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save()
        return self.produce_response()


class ContactParticipantAPI(ParticipantAPI):
    """
    Surprise!  This is also the ParticipantAPI but for different fields.
    We don't want to have to do this but since the contact page doesn't
    represent all fields, and because of various other complexities
    (see comment in saveInlinedModel in inline_ajax.js) we need to strip
    out all fields we aren't using here.
    """

    model = models.Participant
    fields = ["id", "name", "primary_phone", "title"]
    field_processors = {}


class CreateParticipantAPI(APIMixin, generic.CreateView):
    """
    Creates a participant from a JSON API
    """

    model = models.Participant
    fields = ["name", "primary_phone", "secondary_phone",
              "email", "participant_street_address", "institution"]
    field_processors = {
            "institution": process_institution_field}

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save()
        LogEntry.objects.log_action(
            user_id=self.pk,
            content_type_id=get_content_type_for_model(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_text(self.object),
            action_flag=ADDITION
        )
        return self.produce_response()

    def post(self, request, *args, **kwargs):
        # terrible hack to make sure we can log properly
        # basically multiple inheritance + method dispatch == the devil
        self.pk = request.user.pk
        response = super(CreateParticipantAPI, self).post(
            request, *args, **kwargs)
        return response

    def put(self, request, *args, **kwargs):
        # terrible hack to make sure we can log properly, again
        self.pk = request.user.pk
        response = super(CreateParticipantAPI, self).put(
            request, *args, **kwargs)
        return response

class CreateContactAPI(CreateParticipantAPI):
    """
    Creates a participant, but from the instituions page...
    """
    fields = ["name", "title", "primary_phone"]
    field_processors = {}


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


class InstitutionContactsAPI(APIMixin, generic.DetailView):
    """
    Provides a list of all contacts linked to a institution
    """

    model = models.Institution

    def get(self, request, *args, **kwargs):
        """ Retrival of an existing institution """
        self.object = self.get_object()

        # Iterate over contacts and serialize
        contacts = [p.serialize() for p in self.object.contacts.all()]

        return self.render_to_response(context=contacts)


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

        log_unlinking(request, self.object, self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """ Links a participant """
        self.object = self.get_object()

        # Add to the event
        self.object.participants.add(self.participant)

        log_linking(request, self.object, self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

class ContactLinking(APIMixin, generic.DetailView):
    """
    Provides a mechanism to unlink Contacts from Institutions
    """
    model = models.Institution

    # The amount of contacts that can be linked at any given time
    limit = settings.CONTACT_LIMIT
    error_messages = {
        "limit_reached": _("You have reached the limit of "
                           "{limit} contacts.")
    }

    @property
    def participant(self):
        """ Looks up and returns Participant """
        participant_pk = self.kwargs.get("participant_id")
        return models.Participant.objects.get(pk=participant_pk)

    def delete(self, request, *args, **kwargs):
        """ Unlink a participant """
        # Find institution (self.object)
        self.object = self.get_object()

        # Remove the participant as a contact
        self.object.contacts.remove(self.participant)

        log_unlinking(request, self.object, self.participant)

        # Just return a successful status code
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """ Links a participant """
        # Find institution (self.object)
        self.object = self.get_object()
        # Check we've not reached the limit of contacts
        if len(self.object.contacts.all()) >= self.limit:
            context = self.get_context_data(
                error=self.error_messages["limit_reached"].format(
                    limit=self.limit
                )
            )
            return self.render_to_response(
                context,
                status=400
            )

        # Add the participant as a contact
        self.object.contacts.add(self.participant)

        log_linking(request, self.object, self.participant)

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
