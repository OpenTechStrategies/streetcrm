from django.core import urlresolvers

class AdminURLMixin:
    """ Provides Django's Admin URLs for a model managed by the admin app """

    def __admin_url(self, url):
        """
        Finds the Admin url for a URL

        This will only work for the URLs which are called on a object rather
        than the model (e.g. not adding) this also needs to be for URLs which
        take the ID of the object. If you wanted to extend this in the future
        you would have to look up the ContentType yourself instead of using the
        _meta information prvovided by initialised objects.
        """
        url_name = "admin:{app_label}_{model_name}_{url}".format(
            app_label=self._meta.app_label,
            model_name=self._meta.model_name,
            url=url
        )
        return urlresolvers.reverse(url_name, args=(self.pk,))

    @property
    def admin_change_url(self):
        """ Admin page to edit the object """
        return self.__admin_url("change")

    @property
    def admin_delete_url(self):
        """ Admin page to delete the object """
        return self.__admin_url("delete")

    @property
    def admin_history_url(self):
        """ Admin page to see the history of the object """
        return self.__admin_url("history")
