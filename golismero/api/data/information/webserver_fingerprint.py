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

from .information import Information
from ..data import identity


#------------------------------------------------------------------------------
class WebServerFingerprint(Information):
    """
    Fingerprint information for a concrete host and web server
    """

    information_type = Information.INFORMATION_WEB_SERVER_FINGERPRINT


    #----------------------------------------------------------------------
    def __init__(self, name, version, complete_desc, prob_list= None):
        """Constructor.

        :param name: Web server name. F.E: "Apache"
        :type name: str

        :param version: Web server sersion. F.E: "2.4"
        :type version: str

        :param complete_desc: Complete description for web server. F.E: "Apache 2.2.23 ((Unix) mod_ssl/2.2.23 OpenSSL/1.0.1e-fips)"
        :type complete_desc: str

        :param prob_list: List with other web servers detects and their probabilities.
        :type prob_list: list(server_name, prob)
        """

        # Server name
        self.__name          = name

        # Server version
        self.__version       = version

        # Server complete desc
        self.__complete_desc = complete_desc

        # Other servers
        self.__others        = prob_list

        # Parent constructor
        super(WebServerFingerprint, self).__init__()


    #----------------------------------------------------------------------
    @identity
    def name(self):
        """Web server name"""
        return self.__name


    #----------------------------------------------------------------------
    @identity
    def version(self):
        """Web server version"""
        return self.__version


    #----------------------------------------------------------------------
    @property
    def complete_desc(self):
        """Web server complete description"""
        return self.__complete_desc


    #----------------------------------------------------------------------
    @property
    def others(self):
        """Other web servers probabilites detected for this web server."""
        return self.__others

    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        m_return = "<WebServerFingerprint Web server='%s-%s' Complete desc='%s'>" % (
            self.__name,
            self.__version,
            self.__complete_desc
        )

        return m_return
