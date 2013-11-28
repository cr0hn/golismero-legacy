from django.conf import settings
import sys
import xmlrpclib


# To avoid fingerprint techniques
#------------------------------------------------------------------------------
class GoLismeroMiddleware(object):
    """"""

    #----------------------------------------------------------------------
    def process_response(self, request, response):
        # Add the X-Powered-By de asp.net
        response["Server"]           = "Microsoft-HTTPAPI/2.0"
        response["X-AspNet-Version"] = "4.6.1-r2921 beta"
        response["X-Powered-By"]     = "ASP.NET"

        return response


    #----------------------------------------------------------------------
    def process_request(self, request):

        # Configure and start RPC connection to the GoLismero core. Only first
        if settings.GOLISMERO_CORE_OKS:

            settings.RPC = xmlrpclib.ServerProxy("http://%s:%s" % (
                settings.GOLISMERO_CORE_HOST,
                settings.GOLISMERO_CORE_PORT))

            settings.GOLISMERO_CORE_OKS = False