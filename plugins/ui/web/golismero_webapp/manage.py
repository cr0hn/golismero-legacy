#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xmlrpclib

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    from django.core.management import execute_from_command_line
    from django.conf import settings

    proxy = xmlrpclib.ServerProxy("http://127.0.0.1:9000")

    settings.RPC = proxy

    execute_from_command_line(sys.argv)
