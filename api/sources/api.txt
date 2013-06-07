API
===

Content:

Data structures
---------------

.. toctree::

   api/data


Networking API
---------------

.. toctree::

   api/net


Text processing API
-------------------

.. toctree::

   api/text


Logger
------

.. automodule:: golismero.api.logger
   :members:
   :show-inheritance:
   :inherited-members:

Configuration manager
---------------------

.. automodule:: golismero.api.config
   :members: Config, _Config
   :show-inheritance:
   :private-members:

Plugins interfaces
------------------

There is a general plugin interface. All sub classes implements and inherit their methods.

.. automodule:: golismero.api.plugin
   :members: Plugin, InformationPlugin, AdvancedPlugin, TestingPlugin, UIPlugin, ReportPlugin
   :show-inheritance:

