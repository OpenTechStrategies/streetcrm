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

You then will want to edit a configuration file and add all the  
settings.  See our example config file at /config.example.ini.  You'll  
need to change the secret_key to one of your creation.  

The minimum configuration you need is:  

    [general]
    secret_key = myverysecretkeyhere

This configuration file is referenced in /settings.py.  You can set
the path to it in CONFIG_SPEC.  The path of that configuration file is
set by default to ~/.config/swoptact/, but you can change it to
wherever you'd like to keep the file.

You also might want to set the debug flag to true. 

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
