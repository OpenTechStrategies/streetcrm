import autocomplete_light

from swoptact import models

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
    search_fields = ["first_name", "last_name"]
    model = models.Participant

    @classmethod
    def create(cls, data):
        model = cls.model(
            first_name=" ".join(data.split()[:-1]),
            last_name=data.split()[-1]
        )

        return model

autocomplete_light.register(ContactAutocomplete)

class EventAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Event

autocomplete_light.register(EventAutocomplete)