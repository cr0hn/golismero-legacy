Networking API
==============

.. automodule:: golismero.api.net
   :members: NetworkException, NetworkOutOfScope, ConnectionSlot, slot
   :show-inheritance:

Connecting to a web server
--------------------------

.. automodule:: golismero.api.net.web_utils
   :members: download, data_from_http_response, generate_user_agent, fix_url, check_auth, get_auth_obj, detect_auth_method, split_hostname, generate_error_page_url, ParsedURL, parse_url

.. automodule:: golismero.api.net.http
   :members: HTTP
   :show-inheritance:

.. automodule:: golismero.api.net.scraper
   :members: extract, extract_from_text, extract_from_html, is_link

Making DNS queries
------------------

.. automodule:: golismero.api.net.dns
   :members:
   :show-inheritance:

Network cache
-------------

.. automodule:: golismero.api.net.cache
   :members: NetworkCache
   :show-inheritance:
