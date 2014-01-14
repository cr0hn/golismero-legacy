#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Autonomous System Number (ASN) for BGP routing.
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

__all__ = ["IP"]

from . import Information
from .. import identity, merge
from ...text.text_utils import to_utf8


#------------------------------------------------------------------------------
class ASN(Information):
    """
    Autonomous System Number (ASN) for BGP routing.
    """

    resource_type = Information.INFORMATION_ASN


    #--------------------------------------------------------------------------
    def __init__(self, asn, isp = None):
        """
        :param asn: Autonomous System Number (ASN).
        :type asn: str

        :param isp: (Optional) ISP name.
        :type isp: str
        """

        asn = to_utf8(asn)
        if not isinstance(asn, str):
            raise TypeError("Expected str, got %r instead" % type(asn))

        if isp:
            isp = to_utf8(isp)
            if not isinstance(isp, str):
                raise TypeError("Expected str, got %r instead" % type(isp))
        else:
            isp = None

        # Save the properties.
        self.__asn = asn
        self.__isp = isp

        # Parent constructor.
        super(ASN, self).__init__()


    #--------------------------------------------------------------------------
    def __str__(self):
        if self.isp:
            return "%s (ASN %s)" % (self.isp, self.asn)
        return self.asn


    #--------------------------------------------------------------------------
    def __repr__(self):
        return "<ASN asn=%r, isp=%r>" % (self.asn, self.isp)


    #--------------------------------------------------------------------------
    @property
    def display_name(self):
        return "Autonomous System Number (ASN)"


    #--------------------------------------------------------------------------
    @identity
    def asn(self):
        """
        :return: Autonomous System Number (ASN).
        :rtype: str
        """
        return self.__asn


    #--------------------------------------------------------------------------
    @merge
    def isp(self):
        """
        :return: ISP name.
        :rtype: str
        """
        return self.__isp


    #--------------------------------------------------------------------------
    @isp.setter
    def isp(self, isp):
        """
        :param isp: ISP name.
        :type isp: str
        """
        if isp:
            isp = to_utf8(isp)
            if not isinstance(isp, str):
                raise TypeError("Expected str, got %r instead" % type(isp))
        else:
            isp = None
        self.__isp = isp
