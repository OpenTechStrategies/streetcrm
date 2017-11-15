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

from django import http
from django.core import serializers
from django.conf import settings
from django.views import generic
from django.db.models.fields import related
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date, parse_time
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.models import (
    LogEntry, ADDITION, CHANGE, DELETION)
from django.utils.encoding import force_text

import csv
import codecs

from streetcrm import models
from streetcrm.decorators import streetcrm_login_required
from streetcrm.admin import STREETCRMAdminSite as streetcrm_admin

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

    @method_decorator(streetcrm_login_required)
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


        # manage institution
        if is_put:
            try:
                request.POST['institution'] = request.POST['institution']['id']
            except:
                request.POST['institution'] = request.POST['institution']

        try:
            new_object = super(APIMixin, self).post(request, *args, **kwrgs)
        except AttributeError:
            new_object = None
            # most likely an incorrect pk_url_kwarg
            context = self.get_context_data(
                error= { 'name': ["Sorry, there's a problem with your request.  Please try again."]}
            )
            # but the AttributeError makes this fail, too.
            return self.render_to_response(
                context,
                status=400
            )


        if is_put is None:
            object_json = self.process_json(new_object._container[0])
            new_id = object_json['id']
            # save new_id and nonce to the `streetcrm_nonce_to_id` table
            try:
                new_nonce = models.nonce_to_id(participant=new_id, nonce=request.POST['nonce'])
                new_nonce.save()
            except KeyError:
                print("DEBUG: No incoming nonce, so we can't save the nonce record")

        return new_object

    def find_id(self, incoming_fields):
        # function that takes the result of process_json and returns the
        # id or, if there's an error, the text of the error
        try:
            model_id = incoming_fields['id']
            del incoming_fields['id']
        except:
            model_id = None

        if incoming_fields['nonce'] and not model_id:
            #look up the id in the nonce_to_id table
            matching_queryset = models.nonce_to_id.objects.filter(
                nonce=incoming_fields['nonce'])
            if matching_queryset:
                matching_id = matching_queryset[0].participant
                model_id = matching_id
        elif model_id and incoming_fields['nonce']:
            #find and delete the matching rows from nonce_to_id
            removable_queryset = models.nonce_to_id.objects.filter(
                nonce=incoming_fields['nonce'],
                participant=model_id) 
            for obj in removable_queryset:
                obj.delete()
        elif not model_id and not incoming_fields['nonce']:
            model_id = "We weren't able to save this data.  Please try again."

        return model_id


    def put(self, request, *args, **kwrgs):
        incoming_fields = self.process_json(request.body)
        model_id = self.find_id(incoming_fields)
        try:
            # Can we assume it's a participant here?
            relevant_object = models.Participant.objects.get(
            id=model_id)
        except ValueError:
            # find_id failed to get an int
            # find fieldname to position error correctly
            for key in incoming_fields:
                if key is not 'nonce' and key is not 'id':
                    fieldname = key
                    break
            context = self.get_context_data(
                # error should be of form fieldname => Array(errortext1, ...)
                error= { fieldname: [model_id]}
            )
            return self.render_to_response(
                context,
                status=400
            )

        request.POST = relevant_object.serialize()
        
        for field in incoming_fields:
            # Check to see whether the object has such a field
            try:
                getattr(relevant_object, field)
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
                try:
                    existing_inst = server_field['id']
                except:
                    existing_inst = None
                if client_original == server_field or client_original == existing_inst: 
                    # update the field
                    request.POST[field] = incoming_fields[field]['new']
                else:
                    # error: client original value doesn't match what's on the server
                    context = self.get_context_data(
                        error= { field: ["Your data is out of date and must be updated.  Please refresh."]}
                    )
                    return self.render_to_response(
                        context,
                        status=400
                    )
            else:
                print("DEBUG: field " + field + " does not exist in this object")

        # use the model_id as the url pk in the request
        setattr(self, 'kwargs', {'pk': model_id})
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
        elif "error" in context:
            context["form"] = {
                "errors": context["error"]
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


class FileImportMixin:
    model = None
    field_processors = {}
    # Convert all empty strings to None, except for blank fields
    blank_fields = ['email', 'location']
    # Mapping of CSV header row names to model fields
    # Only fields listed in field_map will be queried, but if any
    # of these are missing in the data they will be ignored
    field_map = {}
    # Django query syntax for each field, used to determine if
    # an object already exists
    field_queries = {}

    def process_row(self, row):
        # Pull all fields identified in field_map
        row = {
            value: row[key] for key, value in self.field_map.items() if key in row
        }
        # If ID is in the row, that's the only thing that should be queried
        if isinstance(row.get('id'), str) and row.get('id').strip():
            return {'id': row['id']}
        for field, value in row.items():
            # Apply any applicable field_processors,
            # otherwise remove excess whitespace
            if self.field_processors.get(field):
                row[field] = self.field_processors[field](value)
            else:
                row[field] = value.strip()
                # If value not in blank_fields and is empty, convert to None
                if not value.strip() and field not in self.blank_fields:
                    row[field] = None
        return row

    def import_data(self, rows):
        # Create list of objects to create in bulk
        objects_to_create = []
        for row in rows:
            # Use field queries (with default of the key text) to check for
            # record existence
            object_query = self.model.objects.filter(
                **{self.field_queries.get(key, key): value for key, value in row.items()}
            )
            # If no objects are returned, add the object to the list to create
            if not object_query:
                # objects_to_create.append(self.model(**row))
                objects_to_create.append(row)

        # Create all new objects
        # FIXME: Would bulk create, but Django 1.8 doesn't return PKs
        # new_objects = self.model.objects.bulk_create(objects_to_create)
        new_objects = [self.model.objects.create(**o) for o in objects_to_create]
        return {"created_objects": [o.serialize() for o in new_objects]}

    # Skipping header row generated by export if present
    # Based on https://stackoverflow.com/a/26074856
    def create_dict_reader(self, csv_file):
        for line in csv_file:
            if not line.startswith('Exported') and len(line.strip()):
                return csv.DictReader(csv_file, fieldnames=line.strip().split(','))

    def post(self, request, *args, **kwargs):
        csv_file = codecs.iterdecode(request.FILES['file'], 'utf-8')
        import_reader = self.create_dict_reader(csv_file)
        import_results = self.import_data(
            [self.process_row(row) for row in import_reader]
        )
        return http.JsonResponse(import_results)


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

# Case-insensitive name lookup, with the option of
# creating an object if it doesn't exist
def process_object_name(model, name, create=False):
    if name is None or name == '':
        return None
    model_query = model.objects.filter(name__iexact=name)
    if model_query:
        return model_query[0]
    if create:
        return model.objects.create(name=name)
    return None

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


class EventImport(FileImportMixin, generic.View):
    model = models.Event
    field_processors = {
        "institution": lambda name: process_object_name(models.Institution, name, create=True),
        "date": parse_date,
        "time": parse_time,
        "organizer": lambda name: process_object_name(models.Participant, name),
        "major_action": lambda name: process_object_name(models.Event, name)
    }
    field_map = {
        "ID": "id",
        "Action name": "name",
        "Description": "description",
        "Date": "date",
        "Organizer": "organizer",
        "Location": "location",
        "Narrative": "narrative",
        "Major action": "major_action"
    }
    field_queries = {
        "name": "name__iexact",
        "date": "date",
        "time": "time",
        "location": "location__iexact"
    }


class ParticipantImport(FileImportMixin, generic.View):
    model = models.Participant
    field_processors = {
        "institution": lambda name: process_object_name(models.Institution, name, create=True)
    }
    field_map = {
        "ID": "id",
        "Participant name": "name",
        "Phone number": "primary_phone",
        "Email address": "email",
        "Address": "participant_street_address",
        "Institution": "institution"
    }
    field_queries = {
        "name": "name__iexact",
        "email": "email__iexact"
    }


class EventParticipantsImport(FileImportMixin, generic.View):
    field_processors = {
        "institution": lambda name: process_object_name(models.Institution, name, create=True)
    }
    field_map = {
        "ID": "id",
        "Participant name": "name",
        "Phone number": "primary_phone",
        "Email address": "email",
        "Address": "participant_street_address",
        "Institution": "institution"
    }
    field_queries = {
        "name": "name__iexact",
        "email": "email__iexact"
    }

    def import_data(self, rows):
        event = models.Event.objects.get(pk=self.kwargs['pk'])
        event_participant_ids = event.participants.all().values_list('id', flat=True)

        # Create list of participants to create and add for bulk
        # create/update operatiosn
        participants_to_create = []
        participants_to_add = []
        for row in rows:
            # Use field queries (with default of the key text) to check for
            # record existence
            participant_query = models.Participant.objects.filter(
                **{self.field_queries.get(key, key): value for key, value in row.items()}
            )
            # If a participant is found, add them to the event if not already
            if participant_query:
                participant = participant_query[0]
                if participant.id not in event_participant_ids:
                    participants_to_add.append(participant)
            # Otherwise add them to the list of participants to create
            else:
                # PENDING BULK_CREATE W/IDs
                # participants_to_create.append(models.Participant(**row))
                participants_to_create.append(row)

        # Create all new participants, then add them as well as existing
        # participants not associated with the event to its participants
        # FIXME: Would do bulk_create, but it doesn't return primary keys
        # new_participants = models.Participant.objects.bulk_create(
        #     participants_to_create
        # )
        new_participants = [models.Participant.objects.create(**p) for p in participants_to_create]

        participant_ids_to_add = (
            [p.pk for p in participants_to_add] +
            [np.pk for np in new_participants]
        )
        event.participants.add(*participant_ids_to_add)

        return {
            "created_objects": [o.serialize() for o in new_participants],
            "updated_objects": [o.serialize() for o in participants_to_add]
        }
