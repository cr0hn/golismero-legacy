Data API
========

GoLismero has 3 types os data:

.. toctree::

   Information structures details<data/information>
   Resources structures details<data/resource>
   Vulnerabilities structures details<data/vulnerabilities>

Each type of data respresent a particular information.

Generic base types
==================

Each type of information has one of de follow common interface:

The base class: Data
--------------------

This class defines the base of all subtypes of data

.. automodule:: golismero.api.data
   :members: Data


Sub-type: Information
---------------------

The methods and params for general Information types are:

.. automodule:: golismero.api.data.information
   :members:
   :show-inheritance:

Sub-type: Resource
------------------

The methods and params for general Resources types are:

.. automodule:: golismero.api.data.resource
   :members:
   :show-inheritance:

Sub-type: Vulnerability
-----------------------

The methods and params for general vulnerabilities types are:

.. automodule:: golismero.api.data.vulnerability
   :members:
   :show-inheritance: