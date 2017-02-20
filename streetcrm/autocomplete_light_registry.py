import autocomplete_light
from django.db.models import Q

from streetcrm import models

class BaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    attrs = {
        "placeholder": "",
        "data-autocomplete-minimum-characters": 1,
    }

    @classmethod
    def create(cls, data):
        """
        Creates a model based on data submitted

        If there are multiple fields in search_fields this method must be
        overriden, failing to do so will result in an Exception being raised.
        """
        if len(cls.search_fields) != 1:
            raise Exception("Override create method for multiple fields.")

        model = cls.model(**{
            cls.search_fields[0]: data
        })
        return model



# Register the Institution
class InstitutionAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Institution

autocomplete_light.register(InstitutionAutocomplete)

# Register the Tag
class TagAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Tag

autocomplete_light.register(TagAutocomplete)

# Register the Contact
class ContactAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Participant

    def choices_for_request(self):
        self.choices = models.Participant.objects.filter(archived__isnull=True)
        return super(ContactAutocomplete, self).choices_for_request()
    
    @classmethod
    def create(cls, data):
        model = cls.model(name=data)
        return model
autocomplete_light.register(ContactAutocomplete)

class EventAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Event
autocomplete_light.register(EventAutocomplete)

##
# Advanced search autocompletes
##
class ASInstitutionAutocomplete(InstitutionAutocomplete):
    attrs = {
        "placeholder": "Institution",
    }
autocomplete_light.register(ASInstitutionAutocomplete)

class ASTagAutocomplete(TagAutocomplete):
    attrs = {
        "placeholder": "Tags",
    }
autocomplete_light.register(ASTagAutocomplete)

class ASContactAutocomplete(ContactAutocomplete):
    attrs = {
        "placeholder": "Participant",
    }
autocomplete_light.register(ASContactAutocomplete)

class ASEventAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Event
    attrs = {
        "placeholder": "Action",
    }
autocomplete_light.register(ASEventAutocomplete)
