# Deploy on Debian stable

This assumes you have a clean Debian stable install. This should all be done as root
unless it specifies otherwise. The first thing that you need to do is install some
packages required:

     $ apt-get install apache2 git libapache2-mod-wsgi-py3 python3 python3-dev python3-virtualenv virtualenv postgresql postgresql-client postgres postgresql-server-dev-all gcc

Database
--------

We need to setup the PostgreSQL database, to do that first we need to switch to
the "psql" user:

    $ su - postgres

Now create the user and db:

    $ createuser --pwprompt swoptact
    $ createdb --owner=swoptact swoptact

Now we need to reload PostgreSQL:

    $ systemctl restart postgresql

You then need to add PostgreSQL to automatically start on boot:

    $ systemctl enable postgresql

SWOPTACT
--------

You should make a directory under the "www" directory and pull down the source
code:

    $ cd /var/www
    $ git clone https://github.com/OpenTechStrategies/swoptact.git

We then need to build the virtual enviroment for the website to use, you should ensure
you're still in "/var/www/swoptact" and then:

    $ virtualenv --python=python3.4 .
    $ source bin/activate
    $ pip install -r requirements.txt
    $ pip install psycopg2

Make the config directory and copy the config file over:

    $ mkdir -p /var/www/.config/swoptact/
    $ cp /var/www/swoptact/config.example.ini /var/www/.config/swoptact/config.ini

Then edit the file and modify the contents to suit your needs, they should at minimum
have this:

     [general]
     secret_key = THIS_SHOULD_BE_CHANGED
     debug = false
     time_zone = "America/Chicago"
     allowed_hosts = ["example.com"]

     [database]
     engine = django.db.backends.postgresql_psycopg2
     host = localhost
     name = swoptact
     user = swoptact
     password = DB_PASSWORD_HERE

The "allowed_hosts" must be set to the URL people will access the site on.

Now create the tables in the database and setup the initial superuser:

    $ export SWOPTACT_CONFIG=/var/www/.config/swoptact/config.ini
    $ python manage.py syncdb

HTTP Server
-----------

We need to copy the HTTPD configuration file from the repository to the HTTPD
directory:

    $ cp /var/www/swoptact/apache-24.conf /etc/apache2/sites-available/swoptact.conf

Then edit the file you've just copied with your favorite editor:

    $ favorite-editor /etc/apache2/sites-available/swoptact.conf

You're looking to edit the following lines:

       ServerName      - This should be the URL of the site
       ServerAdmin     - This should be the email to contact you on

That should be all, save the file and exit. You now should enable the config
you've just created:

    $ a2ensite swoptact

You then should verify the config is still valid:

    $ apachectl configtest

Fix any errors or warnings it reports.

Once you've done that we should reload the HTTPD config and tell systemd
to start HTTPD on boot:

    $ systemctl restart apache2
    $ systemctl enable apache2


# How to Deploy Swoptact

Installation
--------------------

You need python 3.4 and python's virtualenv to use this.  In Debian
GNU/Linux ('Jessie' release) this should set up virtualenv for you:

        $ sudo apt-get install python3 python-virtualenv

Ensure you're in the top directory of the swoptact project and run:

        $ virtualenv --python=python3.4 .
        $ source ./bin/activate
        $ pip install -U -r requirements.txt

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
application.  Use a username that represents you individually, such as
"jrandom", not a generic role name like "admin".  In the context of
this system, a "superuser" is just a user who has all permissions, and
there can be multiple such users -- you just happen to be creating the
first one.)

Optionally, you may load sample data too (but see the warning below):

        $ python manage.py loaddata sample_data.json

(The sample data is located in `swoptact/fixtures/sample_data.json`,
but Django knows where to find it if you just say `sample_data.json`.

WARNING: If you load sample data with the above command, any user you
created with `python manage.py syncdb` in a previous step will be
deleted, in which case you'll have to re-create the user with:

        $ python manage.py createsuperuser

WARNING 2: Note that the sample data should have been created with

        python manage.py dumpdata --natural-foreign --indent=4       \
                                  -e sessions -e admin               \
                                  -e contenttypes -e auth.Permission \
              > swoptact/fixtures/sample_data.json

as per
[these](http://stackoverflow.com/questions/27499030/integrity-error-when-loading-fixtures-for-selenium-testing-in-django)
[two](http://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django)
StackOverflow questions.  Otherwise, people may get ""UNIQUE
constraint failed" errors when trying to load the data.

Running
-------

You can now run the python server for testing & development:

        $ python manage.py runserver

Note that this assumes you are still in the `virtualenv` environment.
If you're not, you'll need to set that up again, which is done with
these two commands seen earlier:

        $ virtualenv --python=python3.4 .
        $ source ./bin/activate

Now you can invoke `python manage.py runserver` from the proper
environment.

Updating
--------

When you've updated you should run:

        $ pip install -r requirements -U
        $ python manage.py migrate
