#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
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

from golismero.api.plugin import ReportPlugin

from golismero.api.config import Config
from golismero.api.data import Data
from golismero.api.data.db import Database
from golismero.api.data.resource import Resource
from os.path import join, dirname


#------------------------------------------------------------------------------
class HTMLReport(ReportPlugin):
    """
    Plugin to generate HTML reports.
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        return output_file and (
            output_file.lower().endswith(".html") or
            output_file.lower().endswith(".htm")
        )


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):

        #
        # configure django
        #

        import django.conf
        django.conf.settings.configure(
            TEMPLATE_DIRS = (join(dirname(__file__), './html_report'),)
        )

        from django.template import Template, loader, Context
        from django.conf import settings

        c = Context()
        t = loader.get_template(template_name="template.html")

        #
        # Fill the context
        #

        # Audit name
        c['audit_name']        = Config.audit_name

        #
        # Write the output
        #
        m_rendered = t.render(c)

        f = open(output_file, "wU")
        f.readlines(m_rendered)
        f.close()
