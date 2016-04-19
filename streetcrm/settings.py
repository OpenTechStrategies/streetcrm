# StreetCRM is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Local Initiatives Support Corporation (LISC)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Django settings for streetcrm project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import stat
import warnings

import configobj
import validate

from django.core import exceptions, urlresolvers

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Find the configuration file.
CONFIG_PATH = os.path.join(
    os.path.expanduser(os.getenv("XDG_CONFIG_PATH", "~/.config")),
    "streetcrm",
    "config.ini"
)
CONFIG_PATH = os.getenv("STREETCRM_CONFIG", CONFIG_PATH)

if not os.path.exists(CONFIG_PATH):
    raise exceptions.ImproperlyConfigured("No config file provided")


# For security purposes other users shouldn't be able to edit the file
mode = os.stat(CONFIG_PATH).st_mode
if mode & stat.S_IRWXO != 0:
    warnings.warn(
        "Check permissions on settings file, it contains sensitive data."
    )

# Open config file
CONFIG_SPEC = os.path.join(BASE_DIR, "streetcrm", "config_spec.ini")

config = configobj.ConfigObj(CONFIG_PATH, configspec=CONFIG_SPEC)
config.validate(validate.Validator())

##
# Config settings.  Please alter these in the config file not this file
##

# This must exist for django to run.
SECRET_KEY = config["general"].get("secret_key", None)
if SECRET_KEY is None:
    raise exceptions.ImproperlyConfigured("Secret key must be defined.")

# This should never be True in production.
DEBUG = config["general"]["debug"]
TEMPLATE_DEBUG = DEBUG

# List of accepted hosts the site runs on.
ALLOWED_HOSTS = config["general"]["allowed_hosts"]


# Application definition
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "streetcrm", "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "streetcrm.context_processors.search_header",
)


INSTALLED_APPS = (
    'autocomplete_light',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'streetcrm',
    'watson',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'streetcrm.urls'

WSGI_APPLICATION = 'streetcrm.wsgi.application'

LOGIN_URL = urlresolvers.reverse_lazy("login")

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config["database"]["engine"],
        'NAME': config["database"]["name"],
        'USER': config["database"]["user"],
        'PASSWORD': config["database"]["password"],
        'HOST': config["database"]["host"],
        'PORT': config["database"]["port"],
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = config["general"]["language_code"]

TIME_ZONE = config["general"]["time_zone"]

USE_I18N = config["general"]["use_i18n"]

USE_L10N = config["general"]["use_l10n"]

USE_TZ = config["general"]["use_tz"]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = config["general"]["static_url"]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "streetcrm", "static"),
)

# Specify the hierarchy of the groups when a user is added the key should be
# the group name and the value should be a list which contains the values of
# the next level of groups. If no lower groups exist it can be omitted.
GROUP_HIERARCHY = {
    "admin": ["staff"],
    "staff": ["leader"],
}

# Specify the order in which models are present in the admin index page list.
ADMIN_ORDERING = (
    ("StreetCRM", ("Actions", "Institutions", "Participants", "Tags", "Activity Log",)),
)

# This setting controls how many participants/contacts can be linked at any
# given time to an institution.
CONTACT_LIMIT = config["contact"]["limit"]
