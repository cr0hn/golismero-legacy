#!/usr/bin/env python
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


from core.api.plugin import ReportPlugin
from core.api.data.result import Result
from core.api.data.information.information import Information
from collections import Counter
from core.api.colorize import *


class ScreenReport(ReportPlugin):
    """
    This plugin to display reports on screen
    """

    #----------------------------------------------------------------------
    @property
    def report_type(self):
        """
        Get an string with the report name that will be generate. For
        example: text, html, grepable...

        :returns: str -- type of report
        """
        return "screen"


    #----------------------------------------------------------------------
    def generate_report(self, config, results):
        """
        Run plugin and generate report.

        :param config: configuration for report
        :type config: GlobalParams

        :param results: iterable with results.
        :type results: iterable.
        """

        # Check for None
        if not config or not results:
            return

        # All results, with not nulls
        m_results = filter(lambda x: x, results)

        m_counter = Counter()

        # Header
        print "\n\n--= %s =--" % colorize("Report", "cyan")

        #
        # 1 - Get urls
        #
        print "\n- %s - \n"% colorize("Spidered URLs", "yellow")

        for u in filter(lambda x: x.data_type == Result.TYPE_INFORMATION and x.information_type == Information.INFORMATION_URL , m_results):
            print "+ %s" % str(u)
            m_counter['url'] += 1


        #
        # End - Write summary
        #
        print "\n- %s -\n" % colorize("Summary", "yellow")

        # Urls
        print "+ Total URLs: %s\n\n" % colorize(str(m_counter['url']), "yellow")


