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
from os import getcwd, walk
from os.path import join, split



#------------------------------------------------------------------------------
class WordListManager(Singleton):
    """This class manager wordlist"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # Store
        self.__store = {} # Pair with: (name, path)

        # Initial load
        self.__load_wordlists(join(getcwd(), "wordlist"))


    #----------------------------------------------------------------------
    def __load_wordlists(self, currentDir):
        """"""


        # The following levels belong to the plugins
        for (dirpath, dirnames, filenames) in walk(currentDir):

            # Look for text files
            for fname in filenames:
                if fname.endswith(".txt") and not fname.startswith("_") and fname.find("readme") ==-1:
                    try:
                        m_file = fname[:-4].lower()

                        # If file name is already in store, looking for new name
                        if m_file in self.__store:
                            m_tmp_path = dirpath
                            while m_file in self.__store:
                                m_tmp_path = split(m_tmp_path)[1]
                                m_file = "%s_%s" % (m_tmp_path, m_file)

                        self.__store[m_file] = join(dirpath,fname)

                    except KeyError:
                        pass


    #----------------------------------------------------------------------
    @property
    def all_wordlists(self):
        """"""
        return self.__store.keys()

    #----------------------------------------------------------------------
    def get_wordlist(self, wordlist_name):
        """"""
        try:
            return WordList(self.__store[wordlist_name.lower()])
        except KeyError:
            return None


#------------------------------------------------------------------------------
def WordList(wordlist_path):
    """iterate a wordlist"""

    try:

        #f = open(wordlist_path, "U", buffering=1)
        #while True:
        for line in open(wordlist_path, "U", buffering=1):
            if not line:
                #f.close()
                break
            yield line.strip()

    except IOError,e:
        Logger.log_error("Error opening wordlist %s: " % e.message)







