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
        """Constructor.

        :param name: Web server name. F.E: "Apache"
        :type name: str

        :param version: Web server sersion. F.E: "2.4"
        :type version: str

        :param banner: Complete description for web server. F.E: "Apache 2.2.23 ((Unix) mod_ssl/2.2.23 OpenSSL/1.0.1e-fips)"
        :type banner: str

        :param others: List of tuples with other possible web servers and their probabilities of being correct.
        :type others: list( tuple(str, float) )
        """

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
        """Web server name."""
        return self.__name


    #----------------------------------------------------------------------
    @identity
    def version(self):
        """Web server version."""
        return self.__version


    #----------------------------------------------------------------------
    @identity
    def banner(self):
        """Web server banner."""
        return self.__banner


    #----------------------------------------------------------------------
    @identity
    def others(self):
        """Other possibilities for this web server."""
        return self.__others


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<WebServerFingerprint server='%s-%s' banner='%s'>" % (
            self.__name,
            self.__version,
            self.__banner,
        )
