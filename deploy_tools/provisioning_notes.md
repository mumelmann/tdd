Provisioning a new site
=======================

## Required packages:

* nginx
* Python 3
* Git
* pip
* virtualenvwrapper
* supervisor

eg, on Linux:

    sudo apt-get install nginx git python3 python3-pip
    sudo pip3 install virtualenvwrapper

## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME with, eg, staging.my-domain.com

## Supervisor

[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10           ; (num of main logfile rotation backups;default 10)
loglevel=info                ; (log level;default info; others: debug,warn,trace)
pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=true               ; (start in foreground if true;default false)
minfds=1024                  ; (min. avail startup file descriptors;default 1024)
minprocs=200                 ; (min. avail process descriptors;default 200)


akshar
9th May, 2014
0
Comments
Supervisor with Django and Gunicorn
By : Akshar Raaj

Supervisor with Django: A starter guide

This post assumes that you have used gunicorn and know what it does. I will try everything inside a virtual environment and hope you do the same.
What is supervisor.

Supervisor is a monitoring tool that can monitor your processes. It can restart the process if the process dies or gets killed for some reason.
Use of supervisor: Why I started using it.

In production, I use gunicorn as web server. I started a gunicorn process as a daemon and logged out from the server. My site ran as expected for few days. All of a sudden, we started getting '502 Bad Gateway' and I had no idea why. I had to ssh to the server to find out what went wrong. After ps aux | grep gunicorn, I found out gunicorn wasn't running anymore. My gunicorn process died on its own, and I had no idea when and why. Had I used supervisor, supervisor would have been controlling the gunicorn process. It must have recieved a signal when gunicorn died and it would have created a new gunicorn process in such scenario. And my site would have kept running as expected.
Other scenario

We want to run a process which doesn't allow deamonizing. eg: I wanted to keep celery, a Python worker, running on the production server. I could not run it in the foreground because I had to logout from the server. I did not find an easy way to run celery as a daemon. Here too, supervisor came handy.
Project setup

I am setting up a new Django project so you will have proper idea of the path and how to use paths in supervisor configuration file.

We will use Django 1.6.

Create a new Django project:

(PythonEnv)/tmp $ django-admin.py startproject testproj
(PythonEnv)/tmp $ cd testproj/

Project structure looks like:

(PythonEnv)/tmp/testproj $ tree
manage.py
testproj
    __init__.py
    settings.py
    urls.py
    wsgi.py

Run syncdb and runserver. Hereafter, we will run all our commands from directory /tmp/testproj/ with PythonEnv activated.

python manage.py syncdb
python manage.py runserver

And then access the '/admin/'. You should be able to see django admin.

Let's use gunicorn instead of using runserver.

pip install gunicorn

gunicorn testproj.wsgi:application --bind 127.0.0.1:8000

Make sure you can still see /admin/. You will not be able to view static files now, because we aren't using Django development server anymore. Read this post if you want to know how to serve static files using nginx. Though you don't need to do this now, our motive is not to see static files.

Let's run gunicorn as a daemon. Also, we will tell gunicorn to use a file to keep track of process id, so that we can use that process id to kill gunicorn whenever we want.

gunicorn testproj.wsgi:application --bind 127.0.0.1:8000 --pid /tmp/gunicorn.pid --daemon

The problem with this approach is, gunicorn might die at any moment and you will not know about it immediately. Since we are working on dev environment, it is acceptable but gunicorn dying on a server is not acceptable. Your site will loose too many users/customers.

Kill this gunicorn process, we will let supervisor handle gunicorn hereafter.

(PythonEnv)/tmp/testproj $ cat /tmp/gunicorn.pid
19363
(PythonEnv)/tmp/testproj $ kill -9 19363

Using supervisor

Let's install supervisor inside our virtual environment.

(PythonEnv)/tmp/testproj $ pip install supervisor

With this, you should have a echo_supervisord_conf command available. Get a stub supervisor file in your current directory using it.

echo_supervisord_conf > ./supervisord.conf

With this, your directory structure should look like:

db.sqlite3
manage.py
supervisord.conf
testproj
    __init__.py
    settings.py
    urls.py
    wsgi.py

You can remove most of the sections of this supervisor configuration file if you want. Initially we can only keep:

[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10           ; (num of main logfile rotation backups;default 10)
loglevel=info                ; (log level;default info; others: debug,warn,trace)
pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=true               ; (start in foreground if true;default false)
minfds=1024                  ; (min. avail startup file descriptors;default 1024)
minprocs=200                 ; (min. avail process descriptors;default 200)

[inet_http_server]
port=127.0.0.1:9001   ;

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=http://127.0.0.1:9001 ;

[program:gunicorn]
command=/home/akshar/.virtualenvs/PythonEnv/bin/gunicorn testproj.wsgi:application --bind 127.0.0.1:8000 --pid /tmp/gunicorn.pid ;
directory=/tmp/testproj/ ;


## Folder structure:
Assume we have a user account at /home/username

/home/username
└── sites
    └── SITENAME
         ├── database
         ├── source
         ├── static
         └── virtualenv