#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wordlist API.
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

__all__ = ["WordListAPI", "SimpleWordList", "AdvancedWordlist", "AdvancedDicWordlist"]

from os import getcwd, walk
from os.path import join, sep, abspath

from repoze.lru import lru_cache

from ..logger import Logger
from ...common import Singleton


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

        .. warning: Private method, do not call!

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
                if not fname.startswith("_") and fname.lower() != "readme.txt":

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
        :returns: Names of all the wordlists.
        :rtype: list
        """
        return self.__store.keys()


    #----------------------------------------------------------------------
    def get_wordlist(self, wordlist_name):
        """
        :param wordlist_name: Name of the requested wordlist.
        :type wordlist_name: str

        :returns: Iterator for the selected wordlist.
        :rtype: iter(str)
        """
        try:
            return SimpleWordList(self.__store[wordlist_name])
        except KeyError:
            raise KeyError("Wordlist file not found: %s" % wordlist_name)


    #----------------------------------------------------------------------
    @lru_cache(maxsize=20)
    def get_advanced_wordlist(self, wordlist_name):
        """
        :param wordlist_name: Name of the requested advanced wordlist.
        :type wordlist_name: str

        :returns: Iterator for the selected advanced wordlist.
        :rtype: iter(str)
        """
        try:
            return AdvancedWordlist(self.__store[wordlist_name])
        except KeyError:
            raise KeyError("Wordlist file not found: %s" % wordlist_name)


    #----------------------------------------------------------------------
    @lru_cache(maxsize=20)
    def get_advanced_wordlist_as_dict(self, wordlist_name, separator=";"):
        """
        :param wordlist_name: Name of the requested advanced wordlist.
        :type wordlist_name: str

        :returns: Advanced wordlist object.
        :rtype: AdvancedDicWordlist
        """
        try:
            return AdvancedDicWordlist(self.__store[wordlist_name], separator)
        except KeyError:
            raise KeyError("Wordlist file not found: %s" % wordlist_name)


#------------------------------------------------------------------------------
def SimpleWordList(wordlist_path):
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


#------------------------------------------------------------------------------
class AdvancedWordlist(object):
    """
    Advanced wordlists allow to do some operations with wordlists:
    - Search matches of a word in the wordlist.
    - Binary search in wordlist.
    - Get first coincidence, start at begining or end of list.
    - Search matches of wordlist with mutations.
    """


    #----------------------------------------------------------------------
    def __init__(self, wordlist):

        if not wordlist:
            raise ValueError("Empty wordlist!")

        self.__wordlist = wordlist


    #----------------------------------------------------------------------
    def matches(self, word):
        """
        Search word passed as parameter in wordlist and return a list with
        matches found.

        :param word: Word to search.
        :type word: str.

        :return: Matched words.
        :rtype: list
        """

        if not word:
            return []

        return [x for x in self.__wordlist if word in x]


    #----------------------------------------------------------------------
    def matches_level(self, word):
        """
        Search word passed as parameter in wordlist and return a list with
        matches and level of correspondence.

        :param word: Word to search.
        :type word: str

        :return: Matched words and correpondence levels.
        :rtype: list( (str, int) )
        """

        if not word:
            return []

        return [x for x in self.__wordlist if word in x]


    #----------------------------------------------------------------------
    def binary_search(self, word):
        raise NotImplemented()


    #----------------------------------------------------------------------
    def get_first(self, word, init=0):
        """
        Get first coincidence, starting at begining.
        """
        raise NotImplemented()


    #----------------------------------------------------------------------
    def get_rfirst(self, word, init=0):
        """
        Get first coincidence, starting at begining.
        """
        raise NotImplemented()


    #----------------------------------------------------------------------
    def search_mutations(self, word, rules):
        raise NotImplemented()


#------------------------------------------------------------------------------
class AdvancedDicWordlist(object):
    """
    Advanced wordlist that loads a wordlist with a separator character as a dict, like:

    word list 1; sencond value of wordlist

    These line load as => {'word list 1':'sencond value of wordlist'}

    This wordlist allow to do some operations with wordlists:
    - Search matches of a word in the wordlist.
    - Binary search in wordlist.
    - Get first coincidence, start at begining or end of list.
    - Search matches of wordlist with mutations.
    """

    #----------------------------------------------------------------------
    def __init__(self, wordlist, separator = ";"):
        """Constructor"""
        if not wordlist:
            raise ValueError("Empty wordlist got")
        if not separator:
            raise ValueError("Empty separator got")

        m_tmp_wordlist = None
        try:
            m_tmp_wordlist = open(wordlist, mode='rU').readlines()
        except IOError:
            raise IOError("Error when trying to open wordlist: '%s'" % wordlist)

        #self.__wordlist = { k: dict([v.replace("\n","").replace("\r","").split(separator,1)])  for k, v in enumerate(m_tmp_wordlist)}
        #self.__wordlist = [dict([v.replace("\n","").replace("\r","").split(separator,1)])  for k, v in enumerate(m_tmp_wordlist)]

        self.__wordlist = {}
        for k in m_tmp_wordlist:
            v = k.replace("\n","").replace("\r","").split(separator,1)

            if len(v) < 2:
                #Logger.log_error_more_verbose("Wordlist error: value '%s' can't be splited with separator '%s'." % (v, separator))
                continue

            try:
                self.__wordlist[v[0]].append(v[1])
            except KeyError:
                self.__wordlist[v[0]] = []
                self.__wordlist[v[0]].append(v[1])


        del m_tmp_wordlist

    #----------------------------------------------------------------------
    def matches_by_keys(self, word):
        """
        Search a word passed as parameter in the keys's wordlist and return a list of lists with
        matches found.

        :param word: word to search.
        :type word: str.

        :return: a list with matches.
        :rtype: dict(KEY, VALUE)
        """
        if not word:
            return {}

        word = str(word)

        #
        #
        # TODO: FIX WITH NEW FORMAT!!!!
        #
        #


        return { i:v for i, v in self.__wordlist.iteritems() if word == i}


    #----------------------------------------------------------------------
    def matches_by_key_with_level(self, word):
        """
        Search a word passed as parameter in keys's wordlist and return a list of dicts with
        matches and level of correspondence.

        :param word: word to search.
        :type word: str.

        :return: a list with matches and correpondences.
        :rtype: list(list(KEY, VALUE, LEVEL))
        """
        if not word:
            return []

        word = str(word)

        #
        #
        # TODO: FIX WITH NEW FORMAT!!!!
        #
        #

        return [x for x in self.__wordlist if word == x]

    #----------------------------------------------------------------------
    def matches_by_value(self, word, debug = False):
        """
        Search a word passed as parameter in the keys's wordlist and return a list of lists with
        matches found.

        :param word: word to search.
        :type word: str.

        :return: a list with matches.
        :rtype: dict(KEY, VALUE)
        """
        if not word:
            return {}

        word = str(word)

        m_return = {}

        for k, v in self.__wordlist.iteritems():
            if debug:
                print self.__wordlist
            for l in v:
                if word == l:
                    m_return[k] = l

        return m_return


    #----------------------------------------------------------------------
    def matches_by_value_with_level(self, word):
        """
        Search a word passed as parameter in keys's wordlist and return a list of dicts with
        matches and level of correspondence.

        :param word: word to search.
        :type word: str.

        :return: a list with matches and correpondences.
        :rtype: list(list(KEY, VALUE, LEVEL))
        """
        if not word:
            return []

        word = str(word)

        #
        #
        # TODO: FIX WITH NEW FORMAT!!!!
        #
        #


        return [x for x in self.__wordlist.itervalues() if word == x]


    #----------------------------------------------------------------------
    def binary_search(self, word):
        """"""
        raise NotImplemented()

    #----------------------------------------------------------------------
    def get_first(self, word, init=0):
        """
        Get first coincidence, starting at begining.
        """
        raise NotImplemented()

    #----------------------------------------------------------------------
    def get_rfirst(self, word, init=0):
        """
        Get first coincidence, starting at begining.
        """
        raise NotImplemented()


    #----------------------------------------------------------------------
    def search_mutations(self, word, rules):
        """"""
        raise NotImplemented()
