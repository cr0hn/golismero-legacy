#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fingerprint information for a particular operating system of a host.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
Golismero project mail: golismero.project<@>gmail.com

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

__all__ = ["OSFingerprint", "get_os_fingerprint"]

from . import Information
from .. import identity, keep_newer, keep_greater
from ...text.text_utils import to_utf8


#------------------------------------------------------------------------------
def get_os_fingerprint(data):
    """
    Get the most accurate OS fingerprint for the given Data object, if any.

    :param data: Data object to query.
    :type data: Data

    :returns: Most accurate OS fingerprint.
        If no fingerprint is found, returns None.
    :rtype: OSFingerprint | None
    """

    # Get all OS fingerprints associated with the given Data object.
    fingerprints = data.get_associated_informations_by_category(
        Information.INFORMATION_OS_FINGERPRINT)

    # If no fingerprints were found, return None.
    if not fingerprints:
        return None

    # Sort them by accuracy.
    accurate = sorted(fingerprints, key=(lambda x: x.accuracy))

    # Return the last one, that is, the one with the greater accuracy value.
    return accurate[-1]


#------------------------------------------------------------------------------
class OSFingerprint(Information):
    """
    Fingerprint information for a particular operating system.
    """

    information_type = Information.INFORMATION_OS_FINGERPRINT


    #--------------------------------------------------------------------------
    def __init__(self, cpe, accuracy,
                 name = None, vendor = None,
                 type = None, generation = None, family = None):
        """
        :param cpe: CPE (Common Platform Enumeration).
            Example: "/o:microsoft:windows_xp"
        :type cpe: str

        :param accuracy: Accuracy percentage (between 0.0 and 100.0).
        :type accuracy: float

        :param name: (Optional) OS name.
        :type name: str | None

        :param vendor: (Optional) Vendor name.
        :type vendor: str | None

        :param type: (Optional) OS type.
        :type type: str | None

        :param generation: (Optional) OS generation.
        :type generation: str | None

        :param family: (Optional) OS family.
        :type family: str | None
        """

        # Fix the naming problem.
        os_type = type
        type = __builtins__["type"]

        # Check the CPE parameter.
        cpe = to_utf8(cpe)
        if type(cpe) is not str:
            raise TypeError("Expected string, got %r instead" % type(cpe))
        if not cpe.startswith("cpe:"):
            raise ValueError("Not a CPE name: %r" % cpe)

        # Convert CPE <2.3 (URI binding) to CPE 2.3 (formatted string binding).
        if cpe.startswith("cpe:/"):
            cpe_parts = cpe[5:].split(":")
            if len(cpe_parts) < 11:
                cpe_parts.extend( "*" * (11 - len(cpe_parts)) )
            cpe = "cpe:2.3:" + ":".join(cpe_parts)

        # Save the CPE.
        self.__cpe = cpe

        # Save the rest of the properties.
        self.accuracy   = accuracy
        self.name       = name
        self.vendor     = vendor
        self.type       = os_type
        self.generation = generation
        self.family     = family

        # TODO: extract missing parameters from the CPE string.

        # Parent constructor.
        super(OSFingerprint, self).__init__()


    #--------------------------------------------------------------------------
    def __repr__(self):
        return "<OSFingerprint accuracy=%.2f%% cpe=%s>" % (
            self.__accuracy,
            self.__cpe,
        )


    #--------------------------------------------------------------------------
    def __str__(self):
        return self.__name if self.__name else self.__cpe


    #--------------------------------------------------------------------------
    @identity
    def cpe(self):
        """
        :return: CPE (Common Platform Enumeration).
            Example: "/o:microsoft:windows_xp"
        :rtype: str
        """
        return self.__cpe


    #--------------------------------------------------------------------------
    @keep_greater
    def accuracy(self):
        """
        :return: Accuracy percentage (between 0.0 and 100.0).
        :rtype: float
        """
        return self.__accuracy


    #--------------------------------------------------------------------------
    @accuracy.setter
    def accuracy(self, accuracy):
        """
        :param accuracy: Accuracy percentage (between 0.0 and 100.0).
        :type accuracy: float
        """
        if type(accuracy) is not float:
            accuracy = float(accuracy)
        if accuracy < 0.0 or accuracy > 100.0:
            raise ValueError(
                "Accuracy must be between 0.0 and 100.0, got %r" % accuracy)
        self.__accuracy = accuracy


    #--------------------------------------------------------------------------
    @keep_newer
    def name(self):
        """
        :return: OS name.
        :rtype: str | None
        """
        return self.__name


    #--------------------------------------------------------------------------
    @name.setter
    def name(self, name):
        """
        :param name: OS name.
        :type name: str
        """
        if name is not None:
            name = to_utf8(name)
            if type(name) is not str:
                raise TypeError("Expected string, got %r instead" % type(name))
        self.__name = name


    #--------------------------------------------------------------------------
    @keep_newer
    def vendor(self):
        """
        :return: Vendor name.
        :rtype: str | None
        """
        return self.__vendor


    #--------------------------------------------------------------------------
    @vendor.setter
    def vendor(self, vendor):
        """
        :param vendor: Vendor name.
        :type vendor: str
        """
        if vendor is not None:
            vendor = to_utf8(vendor)
            if type(vendor) is not str:
                raise TypeError("Expected string, got %r instead" % type(vendor))
        self.__vendor = vendor


    #--------------------------------------------------------------------------
    @keep_newer
    def type(self):
        """
        :return: OS type.
        :rtype: str | None
        """
        return self.__type


    #--------------------------------------------------------------------------
    @type.setter
    def type(self, os_type):
        """
        :param os_type: OS type.
        :type os_type: str
        """
        if os_type is not None:
            os_type = to_utf8(os_type)
            if type(os_type) is not str:
                raise TypeError("Expected string, got %r instead" % type(os_type))
        self.__type = os_type


    #--------------------------------------------------------------------------
    @keep_newer
    def generation(self):
        """
        :return: OS generation.
        :rtype: str | None
        """
        return self.__generation


    #--------------------------------------------------------------------------
    @generation.setter
    def generation(self, generation):
        """
        :param generation: OS generation.
        :type generation: str
        """
        if generation is not None:
            generation = to_utf8(generation)
            if type(generation) is not str:
                raise TypeError("Expected string, got %r instead" % type(generation))
        self.__generation = generation


    #--------------------------------------------------------------------------
    @keep_newer
    def family(self):
        """
        :return: OS family.
        :rtype: str | None
        """
        return self.__family


    #--------------------------------------------------------------------------
    @family.setter
    def family(self, family):
        """
        :param family: OS family.
        :type family: str
        """
        if family is not None:
            family = to_utf8(family)
            if type(family) is not str:
                raise TypeError("Expected string, got %r instead" % type(family))
        self.__family = family
