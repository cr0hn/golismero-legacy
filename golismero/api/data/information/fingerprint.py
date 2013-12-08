#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fingerprint information.

 - OSFingerprint: for a particular operating system of a host.
 - WebServerFingerprint: for a particular host and web server.
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

__all__ = [
    "OSFingerprint", "get_os_fingerprint", "get_all_os_fingerprints",
    "WebServerFingerprint",
]

from . import Information
from .. import identity, merge, keep_newer
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
    fingerprints = get_all_os_fingerprints(data)

    # If no fingerprints were found, return None.
    if not fingerprints:
        return None

    # Return the first one, that is, the one with the greater accuracy value.
    return fingerprints[0]


#------------------------------------------------------------------------------
def get_all_os_fingerprints(data):
    """
    Get all OS fingerprints for the given Data object, if any, sorted by level
    of accuracy (more accurate fingerprints first).

    :param data: Data object to query.
    :type data: Data

    :returns: OS fingerprints.
    :rtype: list(OSFingerprint)
    """

    # Get all OS fingerprints associated with the given Data object.
    fingerprints = data.get_associated_informations_by_category(
        Information.INFORMATION_OS_FINGERPRINT)

    # Sort them by accuracy, more accurate fingerprints first.
    return sorted(fingerprints, key=(lambda x: 100.0 - x.accuracy))


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

        # Validate the accuracy value.
        if type(accuracy) is not float:
            accuracy = float(accuracy)
        if accuracy < 0.0 or accuracy > 100.0:
            raise ValueError(
                "Accuracy must be between 0.0 and 100.0, got %r" % accuracy)

        # Save the CPE and accuracy.
        self.__cpe      = cpe
        self.__accuracy = accuracy

        # Save the rest of the properties.
        # TODO: extract missing parameters from the CPE string.
        self.name       = name
        self.vendor     = vendor
        self.type       = os_type
        self.generation = generation
        self.family     = family

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
        name = self.__name if self.__name else self.__cpe
        if self.__type:
            name = "[%s] %s" % (self.__type, name)
        return "%.2f%% - %s" % (self.accuracy, name)


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
    @identity
    def accuracy(self):
        """
        :return: Accuracy percentage (between 0.0 and 100.0).
        :rtype: float
        """
        return self.__accuracy


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


#------------------------------------------------------------------------------
class WebServerFingerprint(Information):
    """
    Fingerprint information for a particular host and web server.
    """

    information_type = Information.INFORMATION_WEB_SERVER_FINGERPRINT


    #----------------------------------------------------------------------
    def __init__(self, name, version, banner, canonical_name, related = None, others = None):
        """
        :param name: Web server name as raw format. The name is taken from a raw banner with internal filters, and It can has errors with unusual servers. If you want to ensure that this is correct, use name_canonical instead. I.E: "Ricoh Aficio 1045 5.23 Web-Server 3.0" -> name = "Ricoh Aficio 1045 5.23 Web-Server"
        :type name: str

        :param version: Web server version. Example: "2.4"
        :type version: str

        :param banner: Complete description for web server. Example: "Apache 2.2.23 ((Unix) mod_ssl/2.2.23 OpenSSL/1.0.1e-fips)"
        :type banner: str

        :param canonical_name: Web server name, at lowcase. The name will be one of the the file: 'wordlist/fingerprint/webservers_keywords.txt'. Example: "Apache"
        :type canonical_name: str

        :param related: Alternative brands for this web server.
        :type related: set(str)

        :param others: Map of other possible web servers by name and their probabilities of being correct [0.0 ~ 1.0].
        :type others: dict( str -> float )
        """

        # Sanitize the strings.
        name           = to_utf8(name)
        version        = to_utf8(version)
        banner         = to_utf8(banner)
        canonical_name = to_utf8(canonical_name)

        # Check the data types.
        if not isinstance(name, str):
            raise TypeError("Expected str, got %r instead" % type(name))
        if not isinstance(version, str):
            raise TypeError("Expected str, got %r instead" % type(version))
        if not isinstance(banner, str):
            raise TypeError("Expected str, got %r instead" % type(banner))
        if not isinstance(canonical_name, str):
            raise TypeError("Expected str, got %r instead" % type(canonical_name))

        # Save the identity properties.
        self.__name           = name
        self.__version        = version
        self.__banner         = banner
        self.__canonical_name = canonical_name

        # Save the mergeable properties.
        self.related          = related
        self.others           = others

        # Parent constructor.
        super(WebServerFingerprint, self).__init__()


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<WebServerFingerprint server='%s-%s' banner='%s'>" % (
            self.__name,
            self.__version,
            self.__banner,
        )


    #----------------------------------------------------------------------
    def __str__(self):
        return self.__banner


    #----------------------------------------------------------------------
    def to_dict(self):
        related = list(self.related)
        others = { k: list(v) for (k,v) in self.others.iteritems() }
        return {
            "_class":         self.__class__.__name__,
            "identity":       self.identity,
            "depth":          self.depth,
            "data_type":      self.data_type,
            "data_subtype":   self.data_subtype,
            "name":           self.name,
            "version":        self.version,
            "banner":         self.banner,
            "canonical_name": self.canonical_name,
            "related":        related,
            "others":         others,
        }


    #----------------------------------------------------------------------
    @identity
    def name(self):
        """
        :return: Web server name.
        :rtype: str
        """
        return self.__name


    #----------------------------------------------------------------------
    @identity
    def version(self):
        """
        :return: Web server version.
        :rtype: str
        """
        return self.__version


    #----------------------------------------------------------------------
    @identity
    def banner(self):
        """
        :return: Web server banner.
        :rtype: str
        """
        return self.__banner


    #----------------------------------------------------------------------
    @identity
    def canonical_name(self):
        """
        :return: Web server name, at lowcase. The name will be one of the the file: 'wordlist/fingerprint/webservers_keywords.txt'. Example: "apache"
        :rtype: str
        """
        return self.__canonical_name


    #----------------------------------------------------------------------
    @merge
    def others(self):
        """
        :return: Map of other possible web servers by name and their probabilities of being correct [0.0 ~ 1.0].
        :rtype: dict( str -> float )
        """
        return self.__others


    #----------------------------------------------------------------------
    @others.setter
    def others(self, others):
        """
        :param others: Map of other possible web servers by name and their probabilities of being correct [0.0 ~ 1.0].
        :type others: dict( str -> float )
        """
        if others:
            if not isinstance(others, dict):
                raise TypeError("Expected dict, got %r instead" % type(others))
            others = {
                to_utf8(k): float(v)
                for k,v in others.iteritems()
            }
            for k, v in others.iteritems():
                if not isinstance(k, str):
                    raise TypeError("Expected str, got %r instead" % type(k))
        else:
            others = {}
        self.__others = others


    #----------------------------------------------------------------------
    @merge
    def related(self):
        """
        :return: Alternative brands for this web server.
        :rtype: set(str)
        """
        return self.__related


    #----------------------------------------------------------------------
    @related.setter
    def related(self, related):
        """
        :param related: Alternative brands for this web server.
        :type related: set(str)
        """
        if related:
            if not isinstance(related, set):
                raise TypeError("Expected set, got %r instead" % type(related))
            related = { to_utf8(v) for v in related }
            for v in related:
                if not isinstance(v, str):
                    raise TypeError("Expected str, got %r instead" % type(v))
        else:
            related = {}
        self.__related = related
