#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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

__all__ = ["get_user_settings_folder"]


import os
import os.path as path

_user_settings_folder = None
def get_user_settings_folder():
    """
    Get the current user's GoLismero settings folder.

    This folder will be used to store the various caches
    and the user-defined plugins.

    :returns: GoLismero settings folder.
    :rtype: str
    """

    # TODO: on Windows, use the roaming data folder instead.

    # Return the cached value if available.
    global _user_settings_folder
    if _user_settings_folder:
        return _user_settings_folder

    # Get the user's home folder.
    home = os.getenv("HOME")              # Unix
    if not home:
        home = os.getenv("USERPROFILE")   # Windows

        # If all else fails, use the current directory.
        if not home:
            home = os.getcwd()

    # Get the user settings folder.
    folder = path.join(home, ".golismero")

    # Make sure it ends with a slash.
    if not folder.endswith(path.sep):
        folder += path.sep

    # Make sure it exists.
    try:
        os.makedirs(folder)
    except Exception:
        pass

    # Cache the folder.
    _user_settings_folder = folder

    # Return the folder.
    return folder