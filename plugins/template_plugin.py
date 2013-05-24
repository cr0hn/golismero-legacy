#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
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

#
# Uncomment the includes you need
#

# CORE
#
# - Access to the plugin configuration:
# from golismero.api.config import Config
#
# - Access to te loggin system
# from golismero.api.logger import Logger

# TYPES:
#
# - Access to the resources types:
# from golismero.api.data.resource.url import Url
# from golismero.api.data.resource.baseurl import BaseUrl
#
# - Access to the vulnerability types:
# from golismero.api.data.vulnerability.information_disclosure.url_suspicious import SuspiciousURL


# GOLISMERO API:
#
# - Access to the network framework:
# from golismero.api.net.protocol import NetworkAPI
#
# - Access to the web utils:
# from golismero.api.net.web_utils import is_method_allowed, fix_url, check_auth, get_auth_obj, detect_auth_method, is_in_scope, generate_error_page_url, DecomposedURL, HTMLElement, HTMLParser
#
# - Text utils:
# from golismero.api.text.text_utils import generate_random_string, split_first
#
# - Text analyzer utils:
# from golismero.api.text.matching_analyzer import get_matching_level
#
# - Wordlists API:
# from golismero.api.text.wordlist_api import WordListAPI


# THIRDPARTY_LIBS
#
# - LRU cache for values returned in functions
# from repoze.lru import lru_cache
#





class TemplatePlugin(TestingPlugin):
    """
    DESCRIPTION FOR THE NEW PLUGIN
    """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        # TODO: this could default to the description found in the metadata.
        return self.__doc__


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        #
        # HERE YOU MUST ADD THE DATA TYPES YOU WANT TO RECEIVE
        #
        # Example:
        #
        # return [Url.RESOURCE_URL, BaseUrl.RESOURCE_BASE_URL]]
        #
        return []


    #----------------------------------------------------------------------
    def recv_info(self, info):
        """"""
        #
        #
        # PUT YOUR CODE HERE
        #
        #
