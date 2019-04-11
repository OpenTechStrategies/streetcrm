import dal
from django.db.models import Q

from streetcrm import models

class BaseAutocomplete(dal.AutocompleteModelBase):
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

dal.register(InstitutionAutocomplete)

# Register the Tag
class TagAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Tag

dal.register(TagAutocomplete)

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
dal.register(ContactAutocomplete)

class EventAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Event
dal.register(EventAutocomplete)

##
# Advanced search autocompletes
##
class ASInstitutionAutocomplete(InstitutionAutocomplete):
    attrs = {
        "placeholder": "Institution",
    }
dal.register(ASInstitutionAutocomplete)

class ASTagAutocomplete(TagAutocomplete):
    attrs = {
        "placeholder": "Tags",
    }
dal.register(ASTagAutocomplete)

class ASContactAutocomplete(ContactAutocomplete):
    attrs = {
        "placeholder": "Participant",
    }
dal.register(ASContactAutocomplete)

class ASEventAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Event
    attrs = {
        "placeholder": "Action",
    }
dal.register(ASEventAutocomplete)
