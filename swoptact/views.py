import json
import urllib.parse

from django import http
from django.views import generic

from swoptact import models

class APIMixin:
    """
    Provides a JSON based to be used by the API
    """

    def post(self, request, *args, **kwrgs):
        request.POST = json.load(request.body)
        return super(APIMixin, self).post(request, *args, **kwrgs)

    def put(self, request, *args, **kwrgs):
        request.POST = json.load(request.body)
        return super(APIMixin, self).put(request, *args, **kwrgs)

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
    Provides the endpoint to retrive, create and update a participant

    If called with the PUT verb this expects a JSON serialized participant
    object which is the updated participant that will be saved.
    """
   
    model = models.Participant

    def get(self, request, *args, **kwargs):
        """ Retrival of an existing participant """
        # Lookup the object that we want to return
        self.object = self.get_object()

        # Serialize the object to JSON
        json_object = self.object.serialize()

        # Serialize the output and use that as the context
        return self.render_to_response(self.get_context_data(**json_object))

