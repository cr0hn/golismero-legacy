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

__all__ = ["Data", "identity"]

from ...common import pickle

import hashlib


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
        hash_sum = hashlib.md5(data)

        # Calculate the hexadecimal digest of the hash.
        hex_digest = hash_sum.hexdigest()

        # Store it in the cache.
        self.__identity = hex_digest

        # Return it.
        return self.__identity

    # Identity hash cache.
    __identity = None

    # Protected method, we don't want outsiders calling it.
    # Subclasses may need to override it, but let's hope not!
    def _collect_identity_properties(self):
        """
        Returns a dictionary of identity properties
        and their values for this data object.

        Subclasses may override this method if very
        special circumstances require it, but it's
        generally discouraged.
        """
        is_identity_property = identity.is_identity_property
        clazz = self.__class__
        collection = {}
        for key in dir(self):
            if not key.startswith("_") and key != "identity":
                prop = getattr(clazz, key, None)
                if prop is not None and is_identity_property(prop):
                    collection[key] = prop.__get__(self)
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

        # Generic implementation using None as a sentinel value.
        # Subclasses may need to override this with a custom implementation.
        for key in dir(other):
            if not key.startswith("_") and key != "identity":
                self._merge_property(other, key)

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


#------------------------------------------------------------------------------
class ExtraData(Data):
    """
    Superclass for Information and Vulnerability types.
    It adds methods to link resouces to this data types.
    """


    #----------------------------------------------------------------------
    @mergeable
    def associated_resource(self):
        "Resource associated with this information."
        try:
            return self.__associated_resource
        except AttributeError:
            self.__associated_resource = None


    #----------------------------------------------------------------------
    @associated_resource.setter
    def associated_resource(self, value):
        if not isinstance(value, Resource):
            raise TypeError("Expected Resource, got %s instead" % type(value))
        self.__associated_resource = value


    #----------------------------------------------------------------------
    @property
    def discovered_resources(self):
        """
        Returns a list with the new resources discovered.

        :return: List with resources.
        :rtype: list(Resource)
        """
        return []
