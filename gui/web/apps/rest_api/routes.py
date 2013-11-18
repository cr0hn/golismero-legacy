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

__all__ = ["AuditsRouters", "UsersRouters", "PluginsRouters", "ProfilesRouters", "NodesRouters"]

from backend.rest_api.routes import ParameterizedRouter
from rest_framework.routers import Route
from rest_framework.compat import patterns, url


#------------------------------------------------------------------------------
class AuditsRouters(ParameterizedRouter):

    routes = [
        # List
        Route(url       = r'^{prefix}/list/$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {}),
        Route(url       = r'^{prefix}/list$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {}),
        # List
        Route(url       = r'^{prefix}/list/{text}',
              mapping   = {'get' : 'list_parameterized'},
              name      = '{basename}-list-parameterized',
              initkwargs= {}),

        # Create
        Route(url       = r'^{prefix}/create{trailing_slash}$',
              mapping   = {'post' : 'create'},
              name      = '{basename}-create',
              initkwargs= {}),
        Route(url       = r'^{prefix}/create$',
              mapping   = {'post' : 'create'},
              name      = '{basename}-create',
              initkwargs= {}),

        # Delete
        Route(url       = r'^{prefix}/delete/{lookup}$',
              mapping   = {'get' : 'delete'},
              name      = '{basename}-delete',
              initkwargs= {}),
        # Start
        Route(url       = r'^{prefix}/start/{lookup}$',
              mapping   = {'get' : 'start'},
              name      = '{basename}-start',
              initkwargs= {}),

        # Stop
        Route(url       = r'^{prefix}/stop/{lookup}$',
              mapping   = {'get' : 'stop'},
              name      = '{basename}-stop',
              initkwargs= {}),

        # State
        Route(url       = r'^{prefix}/state/{lookup}$',
              mapping   = {'get' : 'state'},
              name      = '{basename}-state',
              initkwargs= {}),

        # Progress
        Route(url       = r'^{prefix}/progress/{lookup}$',
              mapping   = {'get' : 'progress'},
              name      = '{basename}-progress',
              initkwargs= {}),

        # Results as summary
        Route(url       = r'^{prefix}/results/summary/{lookup}$',
              mapping   = {'get' : 'results_summary'},
              name      = '{basename}-results-summary',
              initkwargs= {}),

        # Results as format
        Route(url       = r'^{prefix}/results/{lookup}$',
              mapping   = {'get' : 'results'},
              name      = '{basename}-results',
              initkwargs= {}),
        Route(url       = r'^{prefix}/results/{lookup}/{text}',
              mapping   = {'get' : 'results'},
              name      = '{basename}-results-formated',
              initkwargs= {}),

        # Details
        Route(url       = r'^{prefix}/details/{lookup}$',
              mapping   = {'get' : 'details'},
              name      = '{basename}-details',
              initkwargs= {}),

        # Pause
        Route(url       = r'^{prefix}/pause/{lookup}$',
              mapping   = {'get' : 'pause'},
              name      = '{basename}-pause',
              initkwargs= {}),

        # Resume
        Route(url       = r'^{prefix}/resume/{lookup}$',
              mapping   = {'get' : 'resume'},
              name      = '{basename}-resume',
              initkwargs= {}),

        # Log
        Route(url       = r'^{prefix}/log/{lookup}$',
              mapping   = {'get' : 'log'},
              name      = '{basename}-log',
              initkwargs= {}),

    ]

#------------------------------------------------------------------------------
class UsersRouters(ParameterizedRouter):

    routes = [

        Route(url       = r'^{prefix}{trailing_slash}$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {'suffix': ''}),
    ]


#------------------------------------------------------------------------------
class PluginsRouters(ParameterizedRouter):
    """
    This class defines the plugins routes
    """

    routes = [

        Route(url       = r'^{prefix}{trailing_slash}$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {'suffix': ''}),
        Route(url       = r'^{prefix}/{lookup}{trailing_slash}$',
              mapping   = {'get' : 'detail'},
              name      = '{basename}-details',
              initkwargs= {'suffix': ''}),

        Route(url       = r'^{prefix}/search/{text}$',
              mapping   = {'get' : 'search'},
              name      = '{basename}-search',
              initkwargs= {'suffix': ''}),
    ]



#------------------------------------------------------------------------------
class ProfilesRouters(ParameterizedRouter):

    routes = [

        Route(url       = r'^{prefix}{trailing_slash}$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {'suffix': ''}),
    ]


#------------------------------------------------------------------------------
class NodesRouters(ParameterizedRouter):

    routes = [

        Route(url       = r'^{prefix}{trailing_slash}$',
              mapping   = {'get' : 'list'},
              name      = '{basename}-list',
              initkwargs= {'suffix': ''}),
    ]
