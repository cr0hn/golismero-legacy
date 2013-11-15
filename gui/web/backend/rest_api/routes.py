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



from rest_framework.routers import SimpleRouter, Route, DefaultRouter
from rest_framework.compat import url

class ParameterizedRouter(SimpleRouter):
    """
    Router modification that allows to append a varible into the URL.

    For example:

    http://site.com/search/{TEXT_TO_SEARCH}

    For that, you must can '{text}' into the url regex, like:

    routes = [
        Route(url        = r'^{prefix}/search/{text}$',
              mapping    = {'get' : 'search'},
              name       = '{basename}-search',
              initkwargs = {'suffix': ''}),
        ]

    Now, in your view, you can access to the search text, read the 'text'
    var from the **kwargs:

    class SearchViewSet(ViewSet):
        def search(self, request, *args, **kwargs):
            s = kwargs['text']
    return Response({'search' : s})
    """

    def get_text_regex(self, viewset):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against free text input.
        """
        if self.trailing_slash:
            base_regex = '(?P<{text_field}>[^/]+)'
        else:
            # Don't consume `.json` style suffixes
            base_regex = '(?P<{text_field}>[^/.]+)'
        text_field = getattr(viewset, 'text_field', 'text')
        return base_regex.format(text_field=text_field)


    #----------------------------------------------------------------------
    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        urls = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            text   = self.get_text_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash,
                    text = text
                )

                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                urls.append(url(regex, view, name=name))

        return urls

