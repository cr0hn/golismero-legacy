#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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

from core.api.results.information.information import Information

#------------------------------------------------------------------------------
class Url(Information):
    """
    This class contain URL information
    """

    #----------------------------------------------------------------------
    def __init__(self, url):
        """
        Construct a Url result, that contain an URL.

        :param url: URL to manage
        :type url: str
        """
        super(Url, self).__init__(Information.INFORMATION_URL)

        self.__url = url

    def get_url_raw(self):
        """
        Get raw info of URL
        """
        return self.__url
    url_raw = property(get_url_raw)
