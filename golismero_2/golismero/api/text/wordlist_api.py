#!/usr/bin/python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Wordlist API
#-----------------------------------------------------------------------

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

__all__ = ["WordListAPI", "WordList"]

from ..logger import Logger
from ...common import Singleton

from os import getcwd, walk
from os.path import join, split, sep, abspath


#------------------------------------------------------------------------------
class WordListAPI(Singleton):
    """
    Wordlist API.
    """


    #----------------------------------------------------------------------
    def __init__(self):

        # Store
        self.__store = {} # Pair with: (name, path)

        # Initial load
        # XXX FIXME this is broken!!! :(
        # It won't work unless you happen to be standing on the GoLismero folder!
        self.__load_wordlists(join(getcwd(), "wordlist"))


    #----------------------------------------------------------------------
    def __load_wordlists(self, currentDir):
        """
        Find and load wordlists from the specified directory.

        :param currentDir: Directory to look for wordlists.
        :type currentDir: str
        """

        # Make sure the directory name is absolute and ends with a slash.
        currentDir = abspath(currentDir)
        if not currentDir.endswith(sep):
            currentDir += sep

        # Iterate the directory recursively.
        for (dirpath, dirnames, filenames) in walk(currentDir):

            # Make sure the directory name is absolute.
            dirpath = abspath(dirpath)

            # Look for text files, skipping README files and disabled lists.
            for fname in filenames:
                if fname.lower().endswith(".txt") and not fname.startswith("_") and fname.lower() != "readme.txt":

                    # Map the relative filename to the absolute filename,
                    # replacing \ for / on Windows.
                    target = join(dirpath, fname)
                    key = target[len(currentDir):]
                    if sep != "/":
                        key = key.replace(sep, "/")
                    self.__store[key] = target


    #----------------------------------------------------------------------
    @property
    def all_wordlists(self):
        """
        Get the names of all the wordlists.

        :returns: list
        """
        return self.__store.keys()


    #----------------------------------------------------------------------
    def get_wordlist(self, wordlist_name):
        """
        Get an iterator with the selected wordlist.

        :returns: iterator with wordlist.
        """
        try:
            return WordList(self.__store[wordlist_name])
        except KeyError:
            raise KeyError("Wordlist file not found: %s" % wordlist_name)


#------------------------------------------------------------------------------
def WordList(wordlist_path):
    """
    Load a wordlist from a file and iterate its words.
    """

    try:
        with open(wordlist_path, "rU") as fd:
            for line in fd:
                line = line.strip()
                if line and not line.startswith("#"):
                    yield line

    except IOError, e:
        Logger.log_error("Error opening wordlist %s: " % e.message)
