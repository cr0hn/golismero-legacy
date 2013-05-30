#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/cr0hn/golismero/
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

__all__ = ["WebServerFingerprint"]

from . import Information
from .. import identity


#------------------------------------------------------------------------------
class WebServerFingerprint(Information):
    """
    Fingerprint information for a concrete host and web server.
    """

    information_type = Information.INFORMATION_WEB_SERVER_FINGERPRINT

    #----------------------------------------------------------------------
    # TODO: we may want to add a list of default servers and descriptions.
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    def __init__(self, name, version, banner, others = None):
        """
        :param name: Web server name. Example: "Apache"
        :type name: str

        :param version: Web server sersion. Example: "2.4"
        :type version: str

        :param banner: Complete description for web server. Example: "Apache 2.2.23 ((Unix) mod_ssl/2.2.23 OpenSSL/1.0.1e-fips)"
        :type banner: str

        :param others: Map of other possible web servers by name and their probabilities of being correct [0.0 ~ 1.0].
        :type others: dict( str -> float )
        """

        # Check the data types.
        # XXX this should probably be removed later, or only used in debug mode
        if not isinstance(name, str):
            raise TypeError("Expected str, got %s instead" % type(name))
        if not isinstance(version, str):
            raise TypeError("Expected str, got %s instead" % type(version))
        if not isinstance(banner, str):
            raise TypeError("Expected str, got %s instead" % type(banner))
        if others is not None:
            if not isinstance(others, dict):
                raise TypeError("Expected dict, got %s instead" % type(others))
            for k, v in others.iteritems():
                if not isinstance(k, str):
                    raise TypeError("Expected str, got %s instead" % type(k))
                if not isinstance(v, float):
                    raise TypeError("Expected float, got %s instead" % type(v))

        # Web server name.
        self.__name    = name

        # Web server version.
        self.__version = version

        # Web server banner.
        self.__banner  = banner

        # Other possibilities for this web server.
        self.__others  = others

        # Parent constructor.
        super(WebServerFingerprint, self).__init__()


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
        :rtype: str """
        return self.__version


    #----------------------------------------------------------------------
    @identity
    def banner(self):
        """
        :return: Web server banner.
        :rtype: str"""
        return self.__banner


    #----------------------------------------------------------------------
    @identity
    def others(self):
        """
        :return: Dict with other possibilities for this web server. The format for this parameter is: { SERVER_NAME : PROBABILITY }
        :rtype: dict
        """
        return self.__others


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<WebServerFingerprint server='%s-%s' banner='%s'>" % (
            self.__name,
            self.__version,
            self.__banner,
        )
