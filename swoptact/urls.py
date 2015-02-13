from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import index

urlpatterns = patterns("",
    url(r"^$", index.LoginView.as_view(), name="login"),
    url(r"^success/", index.SuccessView.as_view(), name="success"),
    url(r"^admin/", include(admin.site.urls)),
)
