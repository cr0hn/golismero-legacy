#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML form.
"""

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

__all__ = ["Form"]

from . import Information
from .. import identity
from ..resource.url import Url
from ...config import Config


#------------------------------------------------------------------------------
class Form(Information):
    """
    HTML form.
    """

    information_type = Information.INFORMATION_FORM


    #----------------------------------------------------------------------
    def __init__(self, url, method = "POST", parameters = ()):
        """
        :param url: URL the form should submit its data to.
        :type url: str

        :param method: HTTP method to submit the data.
        :type method: str

        :param parameters: Form parameters.
        :type parameters: iterable(FormParam)
        """

        if not isinstance(url, str):
            raise TypeError("Expected string, got %r instead" % type(url))
        url = str(url)

        if not isinstance(method, str):
            raise TypeError("Expected string, got %r instead" % type(method))

        if isinstance(parameters, basestring):
            raise TypeError("Expected tuple, got string instead")
        for name in parameters:
            if not isinstance(name, str):
                raise TypeError("Expected string, got %r instead" % type(name))

        # Set the properties.
        self.__url = url
        self.__method = method
        self.__parameters = tuple(sorted(set(parameters)))

        # Call the parent constructor.
        super(Form, self).__init__()


    #----------------------------------------------------------------------
    @identity
    def url(self):
        """
        :return: URL the form should submit its data to.
        :rtype: str
        """
        return self.__url


    #----------------------------------------------------------------------
    @identity
    def method(self):
        """
        :return: HTTP method to submit the data.
        :rtype: str
        """
        return self.__method


    #----------------------------------------------------------------------
    @identity
    def parameters(self):
        """
        :return: Form parameter names.
        :rtype: iterable(str)
        """
        return self.__parameters


    #----------------------------------------------------------------------
    @property
    def discovered(self):
        if self.url in Config.audit_scope:
            return [Url(self.url, method = self.method)]
        return []


#------------------------------------------------------------------------------
class FormParam(Information):
    """
    HTML form parameter.
    """

    information_type = Information.INFORMATION_FORM_PARAM


    # Valid parameter types.
    VALID_TYPES = [
        "checkbox",
        "color",
        "date",
        "datetime",
        "datetime-local",
        "email",
        "file",
        "hidden",
        "month",
        "number",
        "password",
        "radio",
        "range",
        "reset",
        "search",
        "tel",
        "text",
        "time",
        "url",
        "week",
    ]


    #----------------------------------------------------------------------
    def __init__(self, param_type, name, value):
        """
        :param param_type: Parameter type.
            Must be one of the following values:
             - "checkbox"
             - "color"
             - "date"
             - "datetime"
             - "datetime-local"
             - "email"
             - "file"
             - "hidden"
             - "month"
             - "number"
             - "password"
             - "radio"
             - "range"
             - "reset"
             - "search"
             - "tel"
             - "text"
             - "time"
             - "url"
             - "week"
        :type param_type: str

        :param name: Parameter name.
        :type name: str

        :param value: Parameter value. Optional for most types.
            The data type depends on the parameter type - for most types
            it's a string, but for multiple-choice parameters it's a tuple
            of strings.
        :type value: str | tuple(str) | None
        """

        if not isinstance(param_type, str):
            raise TypeError("Expected string, got %r instead" % type(param_type))
        if not isinstance(name, str):
            raise TypeError("Expected string, got %r instead" % type(name))

        if not name:
            raise ValueError("Parameter name is mandatory")
        if param_type not in self.VALID_TYPES:
            raise ValueError("Unknown parameter type: %r" % param_type)

        # Set the properties.
        self.__param_type = param_type
        self.__name       = name
        self.__value      = value

        # Call the parent constructor.
        super(FormParam, self).__init__()
