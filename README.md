What's GoLismero 2.0?
=====================

GoLismero is an open source framework for security testing. It's currently geared towards web security, but it can easily be expanded to other kinds of scans.

The most interesting features of the framework are:

- Real platform independence. Tested on Windows, Linux, *BSD and OS X.
- No native library dependencies. All of the framework has been written in pure Python.
- Good performance when compared with other frameworks written in Python and other scripting languages.
- Very easy to use.
- Plugin development is extremely simple.
- The framework also collects and unifies the results of well known tools: sqlmap, xsser, openvas, dnsrecon, theharvester...
- Integration with standards: CWE, CVE and OWASP.
- Designed for cluster deployment in mind (not available yet).

Quick manual
============

Using GoLismero 2.0 is very easy. Below are some basic commands to start to using it:

How to install GoLismero 2.0?
-----------------------------

Currently GoLismero 2.0 is under active development so it isn't in the main branch of the github project. To download it, you must write the following:

```git clone -b 2.0.0 https://github.com/cr0hn/golismero.git golismero-2.0```

Basic usage
-----------

This command will launch GoLismero with all plugins enabled:

```python golismero.py http://mysite.com```

Available plugins
-----------------

If you want display the available plugins, you must write:

```python golismero.py --plugin-list```

Select a specific plugin
------------------------

Currently, the command line usage when you want to enable only some plugins is not very intuitive (we're working to improve that).

If you want to run only the dns transfer plugin, you must write:

```python golismero.py http://mysite.com -d all -e report -e dns_zone_transfer```

If you want to run only the plugin to discover hidden files in the web server, you must write:

```python golismero.py http://mysite.com -d all -e report -e bruteforcer_predictables_disclosure```

What will be the next features?
===============================

The next features of golismero will be:

- Ncurses UI
- Web UI
- Export results in HTML format
- Import results from external tools
- And more plugins of course!

Found a bug?
============

If you have found a bug, you can report it using the github issues system.

Support or Contact
==================

For any comment, suggestion or bug report you can send us a mail to: golismero.project@gmail.com.
