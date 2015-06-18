import autocomplete_light

from swoptact import models

class BaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    attrs = {
        "placeholder": "",
        "data-autocomplete-minimum-characters": 1,
    }

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

# Also first name / last name variations
class ContactFirstNameAutocomplete(BaseAutocomplete):
    search_fields = ["first_name"]
    model = models.Participant

class ContactLastNameAutocomplete(BaseAutocomplete):
    search_fields = ["last_name"]
    model = models.Participant

autocomplete_light.register(ContactAutocomplete)
autocomplete_light.register(ContactFirstNameAutocomplete)
autocomplete_light.register(ContactLastNameAutocomplete)

