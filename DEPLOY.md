Intro
=====

This document explains how to generate a release package of GoLismero in a production server.

To run the script you must to be installed "fabric" library in your system.

Requirements
============

To run the script ensure that you have installed python 2.7 or above.

To install dependences run this command:

sudo pip install -r requirements.txt

Required system packages:

- python2.7-dev
- git
- screen


Manual
======

Intro
-----

** You must run these commands in the same directory of fabfile.py

### List commands

You can list all available command writing:

```fab -l```

### Commands information

You cand display information about some command writing:

```fab -d run_server```

### Fabric useful options

It's advisable to run fab command with params:

```fab -t 1000 -T 1000 ...```

These params specifies an high timeout connection.

Also you should indicate remote host in command line:

```fab -t 1000 -T 1000 -H user@myremotehost.com ...```

* All commands has an optional parameters for specifing the installation path:*

```fab command:INSTALLATION_FOLDER=PATH```

Create initial repo
-------------------

First you must download git repositories and generate a deploy folder. To do that, run:

```fab user@myremotehost.com myremotehost.com init```


Create the virtualenv
---------------------

For create the virtualenv, you must run:

```fab user@myremotehost.com myremotehost.com start```


Updating
--------

If you want update an existent installation, you must write:

```fab -H user@myremotehost.com update```


Running debug web server
------------------------

If you want to run a debug web server, in port 9000, you can write:

```fab -H myremotehost.com run_devel```

If you want to run other instance in other port:

```fab -H my.com run_devel:port=9999```