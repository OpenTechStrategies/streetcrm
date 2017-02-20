from streetcrm import forms
import os.path

def search_header(request):
    """ Add the SearchForm to the context for all templates """
    search_query = request.POST.get("query", None)
    if request.method == "POST" and search_query is not None:
        # There has been a search that has been submitted.
        form = forms.SearchForm(request.POST)
    else:
        form = forms.SearchForm()

    # Special case where we want to add a CSS class to the input widget
    form.fields["query"].widget.attrs.update({"class": "form-control"})

    # Warning: don't call this a generic "form" as it might clash with others.
    return {"header_search_form": form}

def for_logo(request):
    """ Note whether there is a logo file for all templates """
    has_logo = os.path.exists("streetcrm/static/images/logo.png")
        
    return {"logo": has_logo}
