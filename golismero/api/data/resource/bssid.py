#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wi-Fi BSSID.
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

__all__ = ["BSSID"]

from . import Resource
from .. import identity, merge
from .. import Config
from ...text.text_utils import to_utf8

import re


#------------------------------------------------------------------------------
class BSSID(Resource):
    """
    Wi-Fi BSSID.
    """

    resource_type = Resource.RESOURCE_BSSID


    #----------------------------------------------------------------------
    # Regular expression to match BSSIDs.
    __re_mac = re.compile(
        r"[0-9A-Fa-f][0-9A-Fa-f]"
        r"[ \:\-\.]?"
        r"[0-9A-Fa-f][0-9A-Fa-f]"
        r"[ \:\-\.]?"
        r"[0-9A-Fa-f][0-9A-Fa-f]"
        r"[ \:\-\.]?"
        r"[0-9A-Fa-f][0-9A-Fa-f]"
        r"[ \:\-\.]?"
        r"[0-9A-Fa-f][0-9A-Fa-f]"
        r"[ \:\-\.]?"
        r"[0-9A-Fa-f][0-9A-Fa-f]"
    )


    #----------------------------------------------------------------------
    def __init__(self, bssid, essid = None):
        """
        :param bssid: BSSID.
        :type bssid: str

        :param essid: (Optional) ESSID.
        :type essid: str | None
        """

        # Validate and normalize the BSSID.
        address = to_utf8(bssid)
        if not isinstance(bssid, str):
            raise TypeError("Expected str, got %r instead" % type(bssid))
        if not self.__re_mac.match(bssid):
            raise ValueError("Invalid BSSID: %r" % bssid)
        bssid = re.sub(r"[^0-9A-Fa-f]", "", bssid)
        if not len(bssid) == 12:
            raise ValueError("Invalid BSSID: %r" % bssid)
        bssid = ":".join(
            bssid[i:i+2]
            for i in xrange(0, len(bssid) - 2, 2)
        )

        # Save the properties.
        self.__bssid = bssid
        self.essid = essid

        # Parent constructor.
        super(BSSID, self).__init__()

        # Reset the crawling depth.
        self.depth = 0


    #----------------------------------------------------------------------
    def __str__(self):
        return self.bssid


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<BSSID %s>" % self.bssid


    #--------------------------------------------------------------------------
    @property
    def display_name(self):
        return "Wi-Fi 802.11 BSSID"


    #----------------------------------------------------------------------
    @identity
    def bssid(self):
        """
        :return: BSSID.
        :rtype: str
        """
        return self.__bssid


    #----------------------------------------------------------------------
    @merge
    def essid(self):
        """
        :return: ESSID.
        :rtype: str | None
        """
        return self.__essid


    #----------------------------------------------------------------------
    @essid.setter
    def essid(self, essid):
        """
        :param essid: ESSID.
        :type essid: str
        """
        essid = to_utf8(essid)
        if not isinstance(essid, basestring):
            raise TypeError("Expected string, got %r instead" % type(essid))
        self.__essid = essid
