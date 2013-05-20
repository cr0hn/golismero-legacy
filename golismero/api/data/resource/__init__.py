#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
  Mario Vilas | mvilas@gmail.com

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

__all__ = ["Resource"]

from .. import Data
from ..information import Information
##from ..vulnerability import Vulnerability


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
    RESOURCE_UNKNOWN       = 0    # Not a real value!
    RESOURCE_URL           = 1    # URLs
    RESOURCE_BASE_URL      = 2    # Base URLs
    RESOURCE_DOMAIN        = 3    # Domain names


    RESOURCE_FIRST = RESOURCE_URL
    RESOURCE_LAST  = RESOURCE_DOMAIN


    #----------------------------------------------------------------------

    data_type = Data.TYPE_RESOURCE
    resource_type = RESOURCE_UNKNOWN


    #----------------------------------------------------------------------
    @property
    def associated_vulnerabilities(self):
        """
        Get a list with vulnerabilities associated to this resource.

        :return: List with vulnerabilities.
        :rtype: list
        """
        return self.get_linked_data(Data.TYPE_VULNERABILITY)


    #----------------------------------------------------------------------
    @property
    def associated_informations(self):
        """
        Get a list with informations associated to this resource.

        :return: List with informations.
        :rtype: list
        """
        return self.get_linked_data(Data.TYPE_INFORMATION)


    #----------------------------------------------------------------------
    def add_information(self, info):
        """
        Add information elements associated to a resource.

        :param info: Information element.
        :type info: Information
        """
        if not isinstance(info, Information):
            raise TypeError("Expected Information, got %s instead" % type(info))
        self.add_link(info)


    #----------------------------------------------------------------------
    def add_vulnerability(self, vuln):
        """
        Add vulnerability elements associated to a resource.

        :param info: Vulnerability element.
        :type info: Vulnerability
        """
##        if isinstance(vuln, Vulnerability):
##            raise TypeError("Expected Vulnerability, got %s instead" % type(vuln))
        self.add_link(vuln)


    #----------------------------------------------------------------------
    def associated_vulnerabilities_by_category(self, cat_name = None):
        """
        Get accociated vulnerabilites by category.

        :param cat_name: category name
        :type cat_name: str

        :return: set(Data) -- Set of associated informations. Returns an empty set if the category doesn't exist.
        """
        return self.get_linked_data(self.TYPE_VULNERABILITY, cat_name)


    #----------------------------------------------------------------------
    def associated_informations_by_category(self, information_type = None):
        """
        Get accociated information by category.

        :param information_type: One of the Information.INFORMATION_* constants.
        :type information_type: int

        :return: set(Data) -- Set of associated informations.
        :raises ValueError: The specified information type is invalid.
        """
        if type(information_type) is not int:
            raise TypeError("Expected int, got %r instead" % type(information_type))
        if not Information.INFORMATION_FIRST >= information_type >= Information.INFORMATION_LAST:
            raise ValueError("Invalid information_type: %r" % information_type)
        return self.get_linked_data(self.TYPE_INFORMATION, information_type)
