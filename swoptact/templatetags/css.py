from django import template
register = template.Library()

@register.filter(name="addclass")
def addclass(value, klass):
    """ Add `klass` to the CSS `class` attribute """
    return value.as_widget(attrs={"class": klass})
