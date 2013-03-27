#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

__all__ = ["Data", "identity", "mergeable", "TempDataStorage"]

from ...common import pickle

from collections import defaultdict
from functools import partial
from hashlib import md5


#------------------------------------------------------------------------------
class identity(property):
    """
    Decorator that marks read-only properties as part of the object's identity.

    It may not be combined with any other decorator, and may not be subclassed.
    """

    def __init__(self, fget = None, doc = None):
        property.__init__(self, fget, doc = doc)

    def setter(self):
        raise AttributeError("can't set attribute")

    def deleter(self):
        raise AttributeError("can't delete attribute")

    @staticmethod
    def is_identity_property(other):

        # TODO: benchmark!!!
        ##return isinstance(other, identity)
        ##return getattr(other, "is_identity_property", None) is not None
        ##return hasattr(other, "is_identity_property")

        try:
            other.__get__
            other.is_identity_property
            return True
        except AttributeError:
            return False


#------------------------------------------------------------------------------
class mergeable(property):
    """
    Decorator that marks properties that can be merged safely.

    It may not be combined with any other decorator, and may not be subclassed.
    """

    @staticmethod
    def is_mergeable_property(other):

        # TODO: benchmark!!!
        ##return isinstance(other, mergeable) and other.fset is not None

        try:
            other.__get__
            other.is_mergeable_property
            return other.fset is not None
        except AttributeError:
            return False


#------------------------------------------------------------------------------
class Data(object):
    """
    Base class for all data.
    """


    #--------------------------------------------------------------------------
    #
    # Types of data
    #
    #--------------------------------------------------------------------------

    TYPE_ANY = 0      # not a real type! only used in get_accepted_info()

    TYPE_INFORMATION           = 1
    TYPE_VULNERABILITY         = 2
    TYPE_RESOURCE              = 3

    TYPE_FIRST   = TYPE_INFORMATION    # constant for the first valid type
    TYPE_LAST    = TYPE_RESOURCE       # constant for the last valid type

    data_type = TYPE_ANY


    #----------------------------------------------------------------------
    def __init__(self):

        # Linked Data objects.
        # + all links:                  None -> None -> set(identity)
        # + links by type:              type -> None -> set(identity)
        # + links by type and subtype:  type -> subtype -> set(identity)
        self.__linked = defaultdict(partial(defaultdict, set))

        # Identity hash cache.
        self.__identity = None

        # Tell the temporary storage about this instance.
        TempDataStorage.on_create(self)


    #----------------------------------------------------------------------
    @property
    def identity(self):
        """
        Get the identity hash of this object.
        """

        # If the hash is already in the cache, return it.
        if self.__identity is not None:
            return self.__identity

        # Build a dictionary of all properties
        # marked as part of the identity.
        collection = self._collect_identity_properties()

        # Pickle the data with the compatibility protocol.
        # This produces always the same result for the same input data.
        data = pickle.dumps(collection, protocol = 0)

        # Calculate the MD5 hash of the pickled data.
        hash_sum = md5(data)

        # Calculate the hexadecimal digest of the hash.
        hex_digest = hash_sum.hexdigest()

        # Store it in the cache.
        self.__identity = hex_digest

        # Return it.
        return self.__identity

    # Protected method, we don't want outsiders calling it.
    # Subclasses may need to override it, but let's hope not!
    def _collect_identity_properties(self):
        """
        Returns a dictionary of identity properties
        and their values for this data object.

        :returns: dict -- Collected property names and values.
        """
        is_identity_property = identity.is_identity_property
        clazz = self.__class__
        collection = {}
        for key in dir(self):
            if not key.startswith("_") and key != "identity":
                prop = getattr(clazz, key, None)
                if prop is not None and is_identity_property(prop):
                    # ASCII or UTF-8 is assumed for all strings!
                    value = prop.__get__(self)
                    if isinstance(value, unicode):
                        try:
                            value = value.encode("UTF-8")
                        except UnicodeError:
                            pass
                    collection[key] = value
        return collection


    #----------------------------------------------------------------------
    def merge(self, other):
        """
        Merge another data object with this one.
        """
        if type(self) is not type(other):
            raise TypeError("Can only merge data objects of the same type")
        if self.identity != other.identity:
            raise ValueError("Can only merge data objects of the same identity")

        # Merge the properties.
        for key in dir(other):
            if not key.startswith("_") and key != "identity":
                self._merge_property(other, key)

        # Merge the links.
        self._merge_links(other)

    def _merge_property(self, other, key):
        prop = getattr(other.__class__, key, None)
        if prop is None or mergeable.is_mergeable_property(prop):
            value = getattr(self, key, None)
            value = getattr(other, key, value)
            if value is not None:
                try:
                    setattr(self, key, value)
                except AttributeError:
                    pass    # attribute is read only, ignore

    def _merge_links(self, other):
        for data_type, subdict in other.__linked.iteritems():
            my_subdict = self.__linked[data_type]
            for data_subtype, identity_set in subdict.iteritems():
                my_subdict[data_subtype].update(identity_set)


    #----------------------------------------------------------------------
    @property
    def links(self):
        """set(str) -- Set of linked Data identities."""
        return self.__linked[None][None]


    #----------------------------------------------------------------------
    def get_links(self, data_type = None, data_subtype = None):
        """
        Get the linked Data identities of the given data type.

        :param data_type: Optional data type. One of the Data.TYPE_* values.
        :type data_type: int

        :param data_subtype: Optional data subtype.
        :type data_subtype: int | str

        :returns: set(str) -- Set of identities.
        :raises ValueError: Invalid data_type argument.
        """
        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
        return self.__linked[data_type][data_subtype]


    #----------------------------------------------------------------------
    def add_link(self, other):
        """
        Link two Data instances together.

        :param other: Another instance of Data.
        :type other: Data
        """
        if not isinstance(other, Data):
            raise TypeError("Expected Data, got %s instead" % type(other))
        other._add_link(self)
        self._add_link(other)

    def _add_link(self, other):
        """
        Internal method to link two Data instances together. Do not call!

        :param other: Another instance of Data.
        :type other: Data
        """
        identity = other.identity
        self.__linked[None][None].add(identity)
        self.__linked[other.data_type][None].add(identity)
        if data_type == self.TYPE_INFORMATION:
            self.__linked[other.data_type][other.information_type].add(identity)
        elif data_type == self.TYPE_RESOURCE:
            self.__linked[other.data_type][other.resource_type].add(identity)
        elif data_type == self.TYPE_VULNERABILITY:
            self.__linked[other.data_type][other.vulnerability_type].add(identity)
        else:
            raise ValueError("Internal error! Unknown data_type: %r" % data_type)


    #----------------------------------------------------------------------
    @property
    def discovered_resources(self):
        """
        Returns a list with the new resources discovered.

        :return: List with resources.
        :rtype: list(Resource)
        """
        return []


#----------------------------------------------------------------------
class _TempDataStorage(Singleton):
    """
    Temporary storage for newly created objects.
    """


    #----------------------------------------------------------------------
    def __init__(self):

        # Map of identities to instances.
        self.__new_data = {}

        # Set of identities of referenced new instances.
        self.__referenced = set()

        # List of fresh instances, not yet fully initialized.
        self.__fresh = list()


    #----------------------------------------------------------------------
    def on_run(self):
        """
        Called by the plugin bootstrap when a plugin is run.
        """
        self.__new_data = {}
        self.__referenced = set()
        self.__fresh = list()


    #----------------------------------------------------------------------
    def on_finish(self):
        """
        Called by the plugin bootstrap when a plugin finishes running.
        """
        self.__new_data = {}
        self.__referenced = set()
        self.__fresh = list()


    #----------------------------------------------------------------------
    def on_create(self, data):
        """
        Called by instances when being created.
        """
        self.__fresh.append(data)


    #----------------------------------------------------------------------
    def on_send(self, data):
        """
        Called by the OOP Observer when an instance
        is sent to the Orchestrator.
        """
        self.update()
        for ref in data.links:
            if ref in self.__new_data:
                self.__referenced.add(ref)
        identity = data.identity
        try:
            del self.__new_data[identity]
        except KeyError:
            pass
        try:
            self.__referenced.remove(identity)
        except KeyError:
            pass


    #----------------------------------------------------------------------
    def update(self):
        """
        Process the fresh instances.
        """
        while self.__fresh:
            data = self.__fresh.pop()
            self.__new_data[data.identity] = data


    #----------------------------------------------------------------------
    def get(self, identity):
        """
        Fetch an unsent instance given its identity.
        Returns None if the instance is not found.

        :param identity: Identity to look for.
        :type identity: str

        :returns: Data | None
        """
        self.update()
        return self.__new_data.get(identity, None)


    #----------------------------------------------------------------------
    @property
    def pending(self):
        """
        New instances pending to be sent.

        :returns: list(Data) -- List of instances.
        """
        self.update()
        return [self.__new_data[ref] for ref in self.__referenced]


    #----------------------------------------------------------------------
    @property
    def orphans(self):
        """
        Orphaned new instances.

        :returns: list(Data) -- List of instances.
        """
        self.update()
        return [data for data in self.__new_data.itervalues()
                     if data.identity not in self.__referenced]


#----------------------------------------------------------------------
# Temporary storage for newly created objects.
TempDataStorage = _TempDataStorage()
