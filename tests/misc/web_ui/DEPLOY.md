Intro
=====

This document explains how to generate a release package of GoLismero in a production server.

To run the script you must have the "fabric" library installed in your system.


Requirements
============

Run this command to install the required system packages:

  sudo apt-get install python2.7 python2.7-dev python-pip git screen

Afterwards, to install the dependencies run this command:

  sudo pip install -r requirements.txt


Manual
======


Intro
-----

** You must run these commands in the same directory of fabfile.py

### List commands

You can list all available commands with:

```fab -l```

### Commands information

You can display information about a command with:

```fab -d run_server```

### Fabric useful options

It's advisable to run fab with these parameters:

```fab -t 1000 -T 1000 ...```

These parameters specifiy an high connection timeout.

Also you should indicate the remote host in the command line:

```fab -t 1000 -T 1000 -H user@myremotehost.com ...```

* All commands have an optional parameter for specifing the installation path:*

```fab command:INSTALLATION_FOLDER=PATH```


Create initial repo
-------------------

First you must download the git repositories and generate a deploy folder. To do that, run:

```fab user@myremotehost.com myremotehost.com init```


Create the virtualenv
---------------------

To create the virtualenv, you must run:

```fab user@myremotehost.com myremotehost.com start```


Updating
--------

If you want update an existent installation, you must run:

```fab -H user@myremotehost.com update```


Running debug web server
------------------------

If you want to run a debug web server, in port 9000, you can run:

```fab -H myremotehost.com run_devel```

If you want to run another instance in another port:

```fab -H my.com run_devel:port=9999```
