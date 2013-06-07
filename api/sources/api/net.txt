Networking API
==============

Here the Networking API functions:


Making web connections
----------------------

Functions to make connections to a web server.

The connections are classified by type:

- Web: Make HTTP connections
- Ftp (currently not available): Make FTP connections
- ...

.. automodule:: golismero.api.net.protocol
   :members: NetworkException, NetworkOutOfScope, NetworkAPI, Web
   :show-inheritance:


Structures to handle HTTP
-------------------------

Structured sended and received when you need to use HTTP connections.

.. automodule:: golismero.api.net.http
   :members:


Links utilities
---------------

Utilities for extract Urls from links into HTML page and a plain text.

.. automodule:: golismero.api.net.scraper
   :members:

Utils for web
-------------

.. automodule:: golismero.api.net.web_utils
   :members:

