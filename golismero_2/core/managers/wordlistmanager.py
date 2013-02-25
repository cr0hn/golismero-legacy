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



from core.api.logger import *
from core.main.commonstructures import Singleton
from os import listdir, getcwd
from os.path import join, isdir, abspath


#------------------------------------------------------------------------------
class WordListManager(Singleton):
    """This class manager wordlist"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self.__wordlists_files = self.__get_file_from_path(join(getcwd(), "wordlist"))
        print self.__wordlists_files


    #----------------------------------------------------------------------
    def __get_file_from_path(self, currentDir):
        """"""

        m_files = []

        m_curr_dir = abspath(currentDir)

        # Traverse through all files
        for curFile in filter(lambda a: isdir(a) or a.endswith("txt"), [join(m_curr_dir,x) for x in listdir(m_curr_dir)]):

            # Add files
            m_files.extend(self.__get_file_from_path(curFile) if isdir(curFile) else [curFile])

        return m_files




    #----------------------------------------------------------------------
    def get_all_wordlists(self):
        """"""

    #----------------------------------------------------------------------
    def get_wordlist(self):
        """"""


#------------------------------------------------------------------------------
def WordList(wordlist_path):
    """iterate a wordlist"""

    try:

        for f in open(wordlist_path, "r", buffering=1):
            yield f

    except IOError,e:
        Logger.log_error("Error opening wordlist %s: " % e.message)







