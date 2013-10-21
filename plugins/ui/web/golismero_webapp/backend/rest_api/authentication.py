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
# This code was based on: http://stackoverflow.com/a/16739450
#
#



import datetime
from django.utils.timezone import utc
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework import serializers


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        utc_now = datetime.datetime.utcnow().replace(tzinfo=utc)

        # Expiration time
        expires = settings.REST_API_TIMEOUT
        if not expires:
            expires = 1800 # By default 30m

        if token.created < utc_now - datetime.timedelta(seconds=expires):
            raise exceptions.AuthenticationFailed('Token has expired')

        return (token.user, token)