#!/usr/bin/python
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

__all__ = ["Resource"]

from ..data import Data
from ..information.information import Information
from ..vulnerability.vulnerability import Vulnerability


#------------------------------------------------------------------------------
class Resource(Data):
    """
    Base class resources.
    """

    #--------------------------------------------------------------------------
    #
    # Types of Infomation results
    #
    #--------------------------------------------------------------------------
    RESOURCE_UNKNOWN       = 0
    RESOURCE_URL           = 1
    RESOURCE_DOMAIN        = 2    # Domain names


    RESOURCE_FIRST = RESOURCE_UNKNOWN
    RESOURCE_LAST  = RESOURCE_DOMAIN


    #----------------------------------------------------------------------

    data_type = Data.TYPE_RESOURCE
    resource_type = RESOURCE_UNKNOWN


    #----------------------------------------------------------------------
    def __init__(self):
        super(Resource, self).__init__()

        # Identities of associated information elements.
        self.__info_elements = set()

        # Identities of associated vulnerability elements.
        self.__vuln_elements = set()


    #----------------------------------------------------------------------
    def add_information(self, info):
        """
        Add information elements associated to an resource.

        :param info: information subclass
        :type info: Information
        """
        if not isinstance(info, Information):
            raise TypeError("Expected Information, got %s instead" % type(info))
        self.__info_elements.add(info.identity)


    #----------------------------------------------------------------------
    def add_vulnerability(self, vuln):
        """
        Add vulnerability elements associated to an resource.

        :param info: vulnerability subclass
        :type info: Vulnerability
        """
        if isinstance(vuln, Vulnerability):
            raise TypeError("Expected Vulnerability, got %s instead" % type(vuln))
        self.__vuln_elements.add(vuln.identity)


    #----------------------------------------------------------------------
    @property
    def associated_vulnerabilities(self):
        """
        Get a list with vulnerabilities associated to this resource.

        :return: List with vulnerabilities
        :rtype: list
        """
        return self.__vuln_elements


    #----------------------------------------------------------------------
    @property
    def associated_informations(self):
        """
        Get a list with informations associated to this resource.

        :return: List with informations
        :rtype: list
        """
        return self.__info_elements


    #----------------------------------------------------------------------
    def merge(self, other):
        """
        Merge another data object with this one.
        """

        # Merge all but the associations.
        super(Resource, self).merge(other)

        # Merge the associations.
        for identity in other.associated_vulnerabilities:
            self.add_vulnerability(identity)
        for identity in other.associated_informations:
            self.add_information(identity)
