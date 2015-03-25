#How to Deploy Swoptact

Installation
--------------------

You need python 3.4 and python's virtualenv to use this.  In Debian
GNU/Linux ('Jessie' release) this should set up virtualenv for you:

        $ sudo apt-get install python3 python-virtualenv

Ensure you're in the top directory of the swoptact project and run:

        $ virtualenv --python=python3.4 .
        $ source ./bin/activate
        $ pip install -r requirements.txt

This will setup the virtual enviroment and install all the necessary
dependencies.

Then copy `config.example.ini` file from the root directory of the
project to `$XDG_CONFIG_PATH/swoptact/config.ini`.  If `XDG_CONFIG_PATH`
is not set, it will default to `~/.config/`, so that command probably
looks like this for you:

        $ mkdir -p ~/.config/swoptact
        $ cp config.example.ini ~/.config/swoptact/config.ini

If you would rather put the config file somewhere else, you can do so
and set the enviroment variable `$SWOPTACT_CONFIG` to indicate where.
Wherever you put the `config.ini` file, make sure to change its access
permissions to be readable only by the user the application will run
as, for example

        $ chmod go-rwx ~/.config/swoptact/config.ini

(otherwise you will see a warning every time you launch the app).

Next, edit the settings in `config.ini`.  The minimum configuration
you need is:

        [general]
        secret_key = myverysecretkeyhere

(The secret key is just a random string of characters that you make
up.  It is used by Django for cryptographic signing, session
management, etc -- see
[here](https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key)
for details.)

If this is not a production instance, you will also want to turn on
debugging:

        [general]
        debug = true

For development purposes, it's fine to use SQLite3 as the database
back end.  In the 'database' section of `config.ini`, put this:

        [database]
        engine = django.db.backends.sqlite3
        name = swoptact_db

(For SQLite3, you don't need the 'host', 'user', or 'password' fields,
but you would need them if you use PostgreSQL as the database.)

Now initialize the database with this command:

        $ python manage.py syncdb

(If this is the first time you've initialized Django's database, you
may be asked _"You have installed Django's auth system, and don't have
any superusers defined.  Would you like to create one now?"_.  Answer
"yes", and then create a user account with which to log in to the
application -- a reasonable default username will usually be offered.)

Optionally, you may load sample data too (but see the warning below):

        $ python manage.py loaddata sample_data.json

(The sample data is located in `swoptact/fixtures/sample_data.json`,
but Django knows where to find it if you just say `sample_data.json`.)

WARNING: If you load sample data with the above command, any user you
created with `python manage.py syncdb` in a previous step will be
deleted, in which case you'll have to re-create the user with:

        $ python manage.py createsuperuser

Running
-------

You can now run the python server for testing & development:

        $ python manage.py runserver
