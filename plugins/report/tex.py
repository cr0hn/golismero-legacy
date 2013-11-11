#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["LatexReport"]


# Uses the RST plugin to generate the report in memory,
# then converts the RST output to LaTeX with docutils.
from os.path import abspath, split
import sys
cwd = abspath(split(__file__)[0])
sys.path.insert(0, cwd)
try:
    from rst import RSTReport
    rst = sys.modules["rst"]      # Workaround for docutils bug, see:
    del sys.modules["rst"]        # http://sourceforge.net/p/docutils/bugs/228/
finally:
    sys.path.remove(cwd)
del cwd

import warnings
with warnings.catch_warnings(record=True):
    from docutils.core import publish_file

from StringIO import StringIO

from golismero.api.logger import Logger


#------------------------------------------------------------------------------
class LatexReport(RSTReport):
    """
    Creates reports in LaTeX format (.tex).
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        return output_file and output_file.lower().endswith(".tex")


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):
        Logger.log_verbose(
            "Writing LaTeX report to file: %s" % output_file)

        # Generate the report in reStructured Text format.
        source = StringIO()
        self.write_report_to_open_file(source)
        source.seek(0)

        # Convert to LaTeX format.
        with warnings.catch_warnings(record=True):
            with open(output_file, "wb") as destination:
                publish_file(
                    source = source,
                    destination = destination,
                    destination_path = output_file,
                    writer_name = "latex",
                )
