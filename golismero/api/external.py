#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
External tools API.
"""

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

__all__ = ["run_external_tool"]

import subprocess

# TODO: Use pexpect to run tools interactively.


#----------------------------------------------------------------------
def run_external_tool(command, args = []):
    """
    Run an external tool and fetch the output.

    Standard and error output are combined.

    .. warning: SECURITY WARNING: Be *extremely* careful when passing
                data coming from the target servers to this function.
                Failure to properly validate the data may result in
                complete compromise of your machine! See:
                https://www.owasp.org/index.php/Command_Injection

    :param command: Command to execute.
    :type command: str

    :param args: Arguments to be passed to the command.
    :type args: list(str)

    :returns: Output from the tool and the exit status code.
    :rtype: tuple(str, int)
    """
    #
    # We put a large and nasty security warning here mostly to scare the noobs,
    # because subprocess is generally safe when you don't run in "shell" mode
    # nor invoke bash directly - i.e. when you know what the hell you're doing.
    #
    # Still, especially on Windows, some external programs are really stupid
    # when it comes to parsing their own command line, so caveat emptor.
    #
    try:
        code   = 0
        output = subprocess.check_output(args, executable = command)
    except subprocess.CalledProcessError, e:
        code   = e.returncode
        output = e.output
    return output, code
