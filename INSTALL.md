# SWOPTACT deployment on Debian GNU/Linux

You need python 3.4 and python's virtualenv to use this.  In Debian
GNU/Linux ('Jessie' release) install these packages:

        $ sudo apt-get update
        $ sudo apt-get install apache2 git libapache2-mod-wsgi-py3 python3 python3-dev python3-virtualenv virtualenv postgresql postgresql-client postgres postgresql-server-dev-all gcc

Database
--------

For production use, we recommend PostgreSQL as the database (for development, SQLite3 is fine, and you don't need to do anything special here).  To set up PostgreSQL, first switch to the "postgres" user:

        $ su - postgres

Now create the user and db:

        $ createuser --pwprompt swoptact
        $ createdb --owner=swoptact swoptact

Now we need to reload PostgreSQL:

        $ systemctl restart postgresql

You then need to add PostgreSQL to automatically start on boot:

        $ systemctl enable postgresql

The SWOPTACT application
------------------------

In this document, we'll assume you're installing under `/var/www/`,
but these instructions should be pretty easy to adjust to any other
location.

First get the source tree:

        $ cd /var/www
        $ git clone https://github.com/OpenTechStrategies/swoptact.git

Build the virtual enviroment for the website:

        $ cd swoptact
        $ virtualenv --python=python3.4 .
        $ source bin/activate
        $ pip install -U -r requirements.txt
        $ pip install psycopg2

Make the config directory and copy the config file over:

        $ mkdir -p /var/www/.config/swoptact/
        $ cp /var/www/swoptact/config.example.ini /var/www/.config/swoptact/config.ini

(If you're somewhere other than `/var/www/swoptact/`, for example
under your home directory because you're doing a development
deployment rather than a production deployment, then you might put the
config file in a different location.  If so, just set the
`SWOPTACT_CONFIG` environment variable accordingly, e.g.,
`SWOPTACT_CONFIG=~/.config/swoptact/config.ini; export SWOPTACT_CONFIG`.  
If later on you get errors about swoptact being unable to find its
config file, failure to set that environment variable is probably why.)

Wherever you put the `config.ini` file, make sure to change its access
permissions to be readable only by the user the application will run
as, for example

        $ chmod go-rwx /var/www/.config/swoptact/config.ini

otherwise you will see a warning every time you launch the app.

Now edit the `config.ini` file and modify the contents to suit your
needs -- at a minimum you probably want something like this:

        [general]
        # The secret key is just a random string of characters that you
        # make up.  It is used by Django for cryptographic signing,
        # session management, etc.  For more information about it, see
        # https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key.
        secret_key = THIS_SHOULD_BE_CHANGED
        # If this is not a production instance, set `debug` to `true`:
        debug = false
        time_zone = "America/Chicago"
        # Set "allowed_hosts" to the domain of the URL people will access
        # the site on (only needed for PostgreSQL, not for SQLite3):
        allowed_hosts = ["example.com"]

        [database]
        # This is for PostgreSQL.  But for development purposes, it's
        # fine to use SQLite3 as the database back end.  In that case,
        # say `django.db.backends.sqlite3` here instead:
        engine = django.db.backends.postgresql_psycopg2
        # This is for PostgreSQL; for SQLite3, say `swoptact_db`:
        name = swoptact 
        # This is for PostgreSQL; for SQLite3, just comment this out:
        host = localhost 
        # This is for PostgreSQL; for SQLite3, just comment this out:
        user = swoptact 
        # This is for PostgreSQL; for SQLite3, just comment this out:
        password = DB_PASSWORD_HERE

Now create the tables in the database and setup the initial superuser:

        $ export SWOPTACT_CONFIG=/var/www/.config/swoptact/config.ini
        $ python manage.py makemigrations
        $ python manage.py migrate

If you encounter a "ProgrammingError" or similar error during
migrations, you probably have an old database interfering.  The
solution is just to drop the database (`drop database` in PostgreSQL,
or in SQLite just remove the database file) and run the
`makemigration` and `migrate` steps again.

Load sample data if necessary
-----------------------------

Optionally, you may load sample data too (but see the warning below):

        $ python manage.py loaddata sample_data.json

The sample data is located in `swoptact/fixtures/sample_data.json`,
but Django knows where to find it if you just say `sample_data.json`.

If you're loading sample data, you probably need to create a superuser
account too (it's something you should do the first time you
initialize or re-initialize the database).  Use a username that
represents you individually, such as "jrandom", not a generic role
name like "admin".  In the context of swoptact, a "superuser" is just
a user who has permission to do anything, and there can be multiple
such users -- you just happen to be creating the first one.

        $ python manage.py createsuperuser

NOTE: The sample data should have been created with this command:

        python manage.py dumpdata --natural-foreign --indent=4       \
                                  -e sessions -e admin               \
                                  -e contenttypes -e auth.Permission \
              > swoptact/fixtures/sample_data.json

as per
[these](http://stackoverflow.com/questions/27499030/integrity-error-when-loading-fixtures-for-selenium-testing-in-django)
[two](http://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django)
StackOverflow questions.  Otherwise, people may get ""UNIQUE
constraint failed" errors when trying to load the data.

Running swoptact
----------------

To run swoptact just for testing and development purposes, we
recommend you use Python's built-in web server:

        $ python manage.py runserver

Note that this assumes you are still in the `virtualenv` environment.
If you're not, you'll need to set that up again, which is done with
these two commands seen earlier:

        $ virtualenv --python=python3.4 .
        $ source ./bin/activate

Now you can invoke `python manage.py runserver` from the proper
environment.

To run swoptact for production use, see the "HTTP Server" section below.

HTTP Server
-----------

Copy the HTTPD configuration file from the repository to wherever your HTTPD
configuration lives.  We'll assume Debian-standard locations here:

        $ cp /var/www/swoptact/apache-24.conf /etc/apache2/sites-available/swoptact.conf

Then edit the file you've just copied with your favorite editor:

        $ favorite-editor /etc/apache2/sites-available/swoptact.conf

Edit these lines:

        ServerName      - This should be the URL of the site
        ServerAdmin     - This should be the email to contact you on

That should be all you need to edit.  Save the file and exit, then
enable the config you just created:

        $ a2ensite swoptact

Verify the config is still valid:

        $ apachectl configtest

Fix any errors or warnings it reports.

Reload the HTTPD config and tell systemd to start HTTPD on boot:

        $ systemctl restart apache2
        $ systemctl enable apache2

Updating swoptact
-----------------

When updating to a newer version of swoptact, run:

        $ pip install -r requirements -U
        $ python manage.py migrate
