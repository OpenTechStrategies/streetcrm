from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from .views import index

urlpatterns = patterns("",
    url(r"^$", index.LoginView.as_view(), name="home"),
    url(r"^success/", index.SuccessView.as_view(), name="success"),
    url(r"^admin/", include(admin.site.urls)),
)
