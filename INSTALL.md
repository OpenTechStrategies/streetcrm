#How to Install Swoptact

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
the path to it in CONFIG_SPEC.  

You also might want to set the debug flag to true. 

  
