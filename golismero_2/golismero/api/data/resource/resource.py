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
        """"""

        # List of information elements associated
        self.__info_elements = dict()
        self.__info_elements_by_category = dict()

        # List of vulnerability elements associated
        self.__vuln_elements = dict()
        self.__vuln_elements_by_category = dict()

        super(Resource, self).__init__()


    #----------------------------------------------------------------------
    def add_information(self, info):
        """
        Add information elements associated to an resource.

        :param info: information subclass
        :type info: Information
        """
        # Store info
        m_category = None
        try:
            m_category = info.information_type
        except AttributeError:
            raise TypeError("Expected Information, got %s instead" % type(info))

        # Add information
        self.__info_elements[info.identity] = True

        # New category?
        if m_category not in self.__info_elements_by_category:
            self.__info_elements_by_category[m_category] = []

        # Add information to their category
        self.__info_elements_by_category[m_category].append(info.identity)


    #----------------------------------------------------------------------
    def add_vulnerability(self, vuln):
        """
        Add vulnerability elements associated to an resource.

        :param info: vulnerability subclass
        :type info: Vulnerability
        """
        m_category = None
        try:
            m_category = vuln.vulnerability_type
        except AttributeError:
            raise TypeError("Expected Vulnerability, got %s instead" % type(info))

        # Add vuln to store
        self.__vuln_elements[vuln.identity] = True

        # New category?
        if m_category not in self.__vuln_elements_by_category:
            self.__vuln_elements_by_category[m_category] = []

        # Store info into their category
        self.__vuln_elements_by_category[m_category].append(vuln.identity)


    #----------------------------------------------------------------------
    @property
    def associated_vulnerabilities(self):
        """
        Get a list with vulnerabilities associated to this resource.

        :return: List with vulnerabilities
        :rtype: list
        """
        return self.__vuln_elements.values()


    #----------------------------------------------------------------------
    @property
    def associated_informations(self):
        """
        Get a list with informations associated to this resource.

        :return: List with informations
        :rtype: list
        """
        return self.__info_elements.values()


    #----------------------------------------------------------------------
    def associated_vulnerabilities_by_category(self, cat_name = None):
        """
        Get accociated vulnerabilites by one category

        :param cat_name: category name
        :type cat_name: str

        :return: list with IDs with associated informations. Return empty list if category not exits.
        """
        if cat_name and cat_name in self.__info_elements_by_category:
            return self.__info_elements_by_category.values()
        else:
            return []


    #----------------------------------------------------------------------
    def associated_informations_by_category(self, cat_name = None):
        """
        Get accociated information by one category

        :param cat_name: category name
        :type cat_name: str

        :return: list with IDs with associated vulnerabilities. Return empty list if category not exits.
        """
        if cat_name and cat_name in self.__vuln_elements_by_category:
            return self.__vuln_elements_by_category.values()
        else:
            return []
