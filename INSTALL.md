#How to Deploy Swoptact

Installation
--------------------

You need python 3.4 and python's virtualenv to use this. I believe you
should be able to install these in debian jessie via:

    `sudo apt-get install python3 python-virtualenv`

Then ensure you're in the top directory of the swoptact project and run:

    virtualenv --python=python3.4 .
    source ./bin/activate
    pip install -r requirements.txt

This will setup the virtual enviroment and install all the necessary
dependencies.

You then will want to copy the config.example.ini file at the root
directory of the project to $XDG_CONFIG_PATH/swoptact/config.ini
(if XDG_CONFIG_PATH is not set, it will default to ~/.config/). If you
would rather put the config file in another directory you can by
setting the enviroment variable $SWOPTACT_CONFIG. You'll then need to
edit a configuration file and add all the settings.

The minimum configuration you need is:

    [general]
    secret_key = myverysecretkeyhere

If this is not a production instance you will also want to set:

   [general]
   debug = true

Notes for a change to the default template: -------------------

In
lib/python3.4/site-packages/django_admin_bootstrapped/templates/admin/,
change "Save and continue editing" to "Save and stay here" and change
"Save" to "Save and return to the list."  Unfortunately this file is
not in version control because it is created when you start the django
project.

Running
--------------------
You can run the python server for testing by running.

    python manage.py runserver
