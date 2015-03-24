#How to Deploy Swoptact

Installation
--------------------

You need python 3.4 and python's virtualenv to use this. I believe you
should be able to install these in debian jessie via:

    sudo apt-get install python3 python-virtualenv

Then ensure you're in the top directory of the swoptact project and run:

    virtualenv --python=python3.4 .
    source ./bin/activate
    pip install -r requirements.txt

This will setup the virtual enviroment and install all the necessary
dependencies.

You then will want to copy the `config.example.ini` file at the root
directory of the project to `$XDG_CONFIG_PATH/swoptact/config.ini`
(if XDG_CONFIG_PATH is not set, it will default to ~/.config/). If you
would rather put the config file somewhere else, you can do so and set
the enviroment variable $SWOPTACT_CONFIG to indicate where.

Next, edit `config.ini` to add all the settings.  The minimum
configuration you need is:

    [general]
    secret_key = myverysecretkeyhere

(The secret key is used by Django for cryptographic signing, session
management, etc -- see
[here](https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key)
for more details.)

If this is not a production instance, you will also want to set:

   [general]
   debug = true

Next, make these changes to the default template:

In `lib/python3.4/site-packages/django_admin_bootstrapped/templates/admin/`,
change "Save and continue editing" to "Save and stay here" and change
"Save" to "Save and return to the list."  (Unfortunately this file is
not in version control because it is created when you start the django
project.)

Running
-------

You can run the python server for testing by running.

    python manage.py runserver
