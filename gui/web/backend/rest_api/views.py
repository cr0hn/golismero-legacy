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


#
#
# This code was borrowed from: http://stackoverflow.com/a/16739450
#
#


from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken, Token
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response

import datetime



class ObtainExpiringAuthToken(ObtainAuthToken):
    """
    This class overrides the default Token Auth and
    """
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            # Remove old token
            try:
                token =  Token.objects.get(user=serializer.object['user'])
                token.delete()
            except ObjectDoesNotExist:
                pass

            # Create new token
            token, created =  Token.objects.get_or_create(user=serializer.object['user'])

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
                token.save()

            return Response({'token': token.key, 'status' : 'ok'})


        #
        # Dirty filter of errors:
        #
        error_descriptions   = []
        error_code           = 0
        if "non_field_errors" in serializer.errors:
            error_code = 0
            error_descriptions.append(serializer.errors["non_field_errors"].pop())
        elif "password" in serializer.errors:
            error_code = 1
            error_descriptions.append("password: %s" % serializer.errors["password"].pop())
        elif "username" in serializer.errors:
            error_code = 1
            error_descriptions.append("username: %s" % serializer.errors["username"].pop())

        # Updating return information
        errors               = {}
        errors["status"]     = "error"
        errors["error_code"] = error_code
        errors["error"]     = error_descriptions

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAuthToken(ObtainAuthToken):
    """
    This class provides the logout mechanism
    """

    #----------------------------------------------------------------------
    def post(self, request):

        raw = get_authorization_header(request)

        if raw:
            _, token_id =  raw.split(" ")

            if token_id:
                # Remove old token
                try:
                    token =  Token.objects.get(key=token_id)
                    token.delete()

                    return Response({'status': 'ok'})
                except ObjectDoesNotExist:
                    return Response({'status' : 'error', 'error' : ["Session does not exits"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status' : 'error', 'error' : ["Not valid session provided"]}, status=status.HTTP_400_BAD_REQUEST)

    #----------------------------------------------------------------------
    def get(self, request):
        return self.post(request)




obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()
logout_token               = LogoutAuthToken.as_view()