from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import link
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import permission_classes

from backend.rest_api.authentication import ExpiringTokenAuthentication
from backend.rest_api.serializers import *

from backend.managers.golismero_facade import *
from backend.managers import GoLismeroAuditData, CONTENT_TYPES_BY_FORMAT

#
# This file defines the actions for the API-REST
#

__all__ = ["AuditViewSet", "UsersViewSet", "PluginsViewSet", "ProfilesViewSet", "NodesViewSet", "PushingViewSet"]


#------------------------------------------------------------------------------
#
# Pushing actions
#
#------------------------------------------------------------------------------
class PushingViewSet(ViewSet):
    """
    Pushing with plugins
    """
    def push_progress(self, request, *args, **kwargs): # /push/progress/
        """
        This method updates the progress for an audit.

        Params must be received as:

        {
           'audit'      :: str,
           'token'         :: str,
           'params' :
           {
              'current_stage' :: str,
              'steps'         :: int,
              'tests_remain'  :: int,
              'tests_done'    :: int
           }
        }

        :errors:

        code 0 -> parameter missed.
        code 1 -> audit not found
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_progress = GoLismeroAuditProgress(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.set_progress(m_audit, m_progress)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    def push_summary(self, request, *args, **kwargs):
        """
        This method updates the summary for an audit.

        Params must be received as:
        {
           'audit_id'      :: str,
           'token'         :: str,
           'params' :   {
              'vulns_number'            = int
              'discovered_hosts'        = int # Host discovered into de scan process
              'total_hosts'             = int
              'vulns_by_level'          = {
                 'info'     : int,
                 'low'      : int,
                 'medium'   : int,
                 'high'     : int,
                 'critical' : int,
               }
            }
        }
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_summary = GoLismeroAuditSummary(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.summary(m_audit, m_summary)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)




    def push_log(self, request, *args, **kwargs): # /push/log/ ##
        """
        This method updates the audit log.

        Params must be received as:
        {
           'audit_id'      :: str,
           'token'         :: str,
           'params' : {
             plugin_id :: str
             text      :: str
             level     :: int
           }
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_info = GoLismeroAuditInfo(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.log(m_audit, m_info)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)



    def push_perrors(self, request, *args, **kwargs): # /push/perrors/ ##
        """
        This method updates audit plugins errors.

        Params must be received as:
        {
           'audit_id'      :: str,
           'token'         :: str,
           'params' : {
             plugin_id :: str
             text      :: str
             level     :: int
           }
        }
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_info = GoLismeroAuditInfo(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.plugin_errors(m_audit, m_info)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    def push_pwarning(self, request, *args, **kwargs): # /push/pwarning/ ##
        """
        This method updates audit warnings.

        Params must be received as:
        {
           'audit_id'      :: str,
           'token'         :: str,
           'params' : {
             plugin_id :: str
             text      :: str
             level     :: int
           }
        }
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_info = GoLismeroAuditInfo(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.plugin_warning(m_audit, m_info)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    def push_stage(self, request, *args, **kwargs): # /push/stage/ ##
        """
        This method updates audit stage.

        Params must be received as:
        {
           'audit_id'      :: str,
           'token'         :: str,
           'params' : {
             stage :: str
           }
        }
        """

        #
        # Checks for all input params
        #
        # Request has params?
        m_params = request.DATA.get("params", None)
        if not m_params:
            Response({"error" : "params key 'params' missed." % i, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)

        #
        # Checks params
        try:
            m_info = GoLismeroAuditInfo(m_params)
        except ValueError, e:
            Response({"error" : e.message, "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)


        # Additional info
        m_audit = request.DATA.get("audit", None)
        m_token = request.DATA.get("audit", "sample_token")

        # Checks additional params
        if not m_audit and not m_token:
            Response({"error" : "Some para missed.", "error_code" : 0}, status=status.HTTP_400_BAD_REQUEST)



        try:
            # Resquest to core
            GoLismeroFacadeState.stage(m_audit, m_info)

            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)







#------------------------------------------------------------------------------
#
# Audit actions
#
#------------------------------------------------------------------------------
class AuditViewSet(ViewSet):
    """
    Actions with plugins
    """

    AUDIT_STATES = ["running", "stopped", "paused", "canceled", "new", "all"]


    #----------------------------------------------------------------------
    #
    # LIST methods
    #
    #----------------------------------------------------------------------
    def list(self, request, *args, **kwargs): # /api/audits/list/
        """
        Get audit list returning a maximun of 100 audits

        States availables:
        - running
        - stopped
        - paused
        - canceled
        - new
        - all

        :returns: Response format:
        [
           {
              'name'  : 'AUDIT NAME',
              'user'  : 'OWNER OF AUDIT',
              'state' : 'A VALID STATE'
           }
        ]

        """

        m_return = {
            'status'  : 'ok',
            'results' : [x.to_json_brief for x in GoLismeroFacadeAuditPolling.list_audits()]
        }

        return Response(m_return)

    #----------------------------------------------------------------------
    def list_parameterized(self, request, *args, **kwargs): # /api/audits/list/{FILTER}
        """
        Get audit list in the state as parameter "text", returning a maximun of 100 results.

        States availables:
        - running
        - stopped
        - paused
        - canceled
        - new
        - all

        :param text: in kwargs var, parameter with the state
        :type text: str

        :returns: Response format:
        [
           {
              'name'  : 'AUDIT NAME',
              'user'  : 'OWNER OF AUDIT',
              'state' : 'A VALID STATE'
           }
        ]
        """


        m_return = {}
        m_state  = str(kwargs.get("text", "all"))

        if m_state:
            if m_state not in self.AUDIT_STATES:

                #
                # If errors...
                #
                m_return['status']      = "error"
                m_return['error_code']  = 0
                m_return['error']       = ["Unknown state"]

                return Response(m_return, status.HTTP_400_BAD_REQUEST)

        m_return['status']  = "ok"
        m_return['results'] = [x.to_json_brief for x in GoLismeroFacadeAuditPolling.list_audits(m_state)]

        return Response(m_return)




    #----------------------------------------------------------------------
    #
    # CRUD methods
    #
    #----------------------------------------------------------------------
    def create(self, request, *args, **kwargs): # /api/audits/create/
        """
        Create an audit.

        POST data must have this format:

        {
          "audit_name": "asdfasdf",
          "targets": [ "127.0.0.1", "mysite.com"],
          "enable_plugins": [
            {
              "plugin_name": "openvas",
              "params": [
                {
                  "param_name": "profile",
                  "param_value": "Full and fast"
                },
                {
                  "param_name": "user",
                  "param_value": "admin"
                },
                {
                  "param_name": "password",
                  "param_value": "admin"
                }
              ]
            }
          ],
          "disabled_plugins": "spider,nikto"
        }
        """
        m_return = {}
        m_info   = None

        #
        # AUDIT INFO
        #
        audit    = AuditSerializer(data=request.DATA)
        # Audit is valid?
        if not audit.is_valid():
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["%s: %s" %(x, y.pop()) for x, y in audit.errors.iteritems()]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Store into global info
        m_info = { k : str(v) for k, v in audit.data.iteritems()}
        if m_info.get("disable_plugins", None):
            m_info["disable_plugins"] = [x.strip() for x in m_info["disable_plugins"].split(",")]

        #
        # TARGETS
        #
        m_info['targets'] = request.DATA.get("targets", None)
        if not m_info['targets']:
            m_return['status']      = "error"
            m_return['error_code']  = 2
            m_return['error']       = ["Targets are missing."]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        if not isinstance(m_info['targets'], list):
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = ["Targets: parameter error. Targets must be a list of strings."]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        for t in m_info['targets']:
            if not isinstance(t, basestring):
                m_return['status']      = "error"
                m_return['error_code']  = 1
                m_return['error']       = ["Targets: parameter error. Targets must be a list of strings."]
                return Response(m_return, status.HTTP_400_BAD_REQUEST)


        #
        # PLUGINS
        #
        m_plugins_in = request.DATA.get("enable_plugins", [])

        # Clean keys
        if m_plugins_in:
            tmp = []
            for ll in m_plugins_in:
                l_dict = {}
                for dk, dv in ll.iteritems():
                    l_dict[str(dk.strip())] = dv

                tmp.append(l_dict)
            m_plugins_in = tmp

        m_plugins    = [] # Plugins lists

        for p in m_plugins_in:

            l_plugin                = {}
            l_plugin['plugin_name'] = p.get("plugin_name", None)

            if not l_plugin['plugin_name']:
                m_return['status']      = "error"
                m_return['error_code']  = 1
                m_return['error']       = ["A plugin name can be provided."]
                return Response(m_return, status.HTTP_400_BAD_REQUEST)

            pp = p.get('params', None)
            if pp:
                l_plugin_results = []
                for plug_p in pp:

                    l_p                = {}
                    l_p['param_name']  = plug_p.get("param_name", None)
                    l_p['param_value'] = plug_p.get("param_value", None)

                    if not l_p['param_name']:
                        m_return['status']      = "error"
                        m_return['error_code']  = 1
                        m_return['error']       = ["If you specify keywork 'params' in plugin '%s', you must provide a 'param_name' value." % l_plugin['plugin_name']]
                        return Response(m_return, status.HTTP_400_BAD_REQUEST)

                    if not l_p['param_value']:
                        m_return['status']      = "error"
                        m_return['error_code']  = 1
                        m_return['error']       = ["Parameter '%s' must have a 'param_value' value." % l_p['param_name']]
                        return Response(m_return, status.HTTP_400_BAD_REQUEST)

                    l_plugin_results.append(l_p)

                # Add to plugin
                l_plugin['params'] = l_plugin_results

            # Add to plugins store
            m_plugins.append(l_plugin)

        # Add to global info
        m_info['enable_plugins'] = m_plugins

        #
        # Request for new audit
        #
        m_audit_id = None
        try:
            m_audit_id = GoLismeroFacadeAuditPolling.create(m_info)
        except ValueError,e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotAllowedHostException,e:
            m_return['status']      = "error"
            m_return['error_code']  = 3
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotPluginsException,e:
            m_return['status']      = "error"
            m_return['error_code']  = 4
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditUnknownException,e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except Exception,e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        m_return['status']        = "ok"
        m_return['audit_id']      = m_audit_id

        return Response(m_return)


    #----------------------------------------------------------------------
    def audit_import(self, request, *args, **kwargs): # /api/audits/import/
        """
        Create an audit.

        POST data must have this format:

        {
          "audit_name": "AUDIT_NAME",
          "enable_plugins": [
            {
              "plugin_name": "report/text",
              "params": [
                {
                  "param_name": "PARAM_1",
                  "param_value": "VALUE_1
                  "
                }
              ]
            }
          ],
          "imports" : [ "file_1", "file_2"]
        }
        """
        m_return = {}
        m_info   = None

        #
        # AUDIT INFO
        #
        audit    = request.DATA.get("audit_name", None)

        # Audit is valid?
        if not audit:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Field 'audit_name' is required."]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Store into global info
        m_info = { "audit_name" : audit}

        # Get files
        m_imports    = request.DATA.get("imports", None)

        # Audit is valid?
        if not m_imports:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Field 'files' is required."]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        if not isinstance(m_imports, list):
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Field 'imports' must be a list"]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        m_info["imports"] = m_imports


        #
        # PLUGINS
        #
        m_plugins_in = request.DATA.get("enable_plugins", [])

        # Clean keys
        if m_plugins_in:
            tmp = []
            for ll in m_plugins_in:
                l_dict = {}
                for dk, dv in ll.iteritems():
                    l_dict[str(dk.strip())] = dv

                tmp.append(l_dict)
            m_plugins_in = tmp

        m_plugins    = [] # Plugins lists

        for p in m_plugins_in:

            l_plugin                = {}
            l_plugin['plugin_name'] = p.get("plugin_name", None)

            if not l_plugin['plugin_name']:
                m_return['status']      = "error"
                m_return['error_code']  = 1
                m_return['error']       = ["A plugin name can be provided."]
                return Response(m_return, status.HTTP_400_BAD_REQUEST)

            pp = p.get('params', None)
            if pp:
                l_plugin_results = []
                for plug_p in pp:

                    l_p                = {}
                    l_p['param_name']  = plug_p.get("param_name", None)
                    l_p['param_value'] = plug_p.get("param_value", None)

                    if not l_p['param_name']:
                        m_return['status']      = "error"
                        m_return['error_code']  = 1
                        m_return['error']       = ["If you specify keywork 'params' in plugin '%s', you must provide a 'param_name' value." % l_plugin['plugin_name']]
                        return Response(m_return, status.HTTP_400_BAD_REQUEST)

                    if not l_p['param_value']:
                        m_return['status']      = "error"
                        m_return['error_code']  = 1
                        m_return['error']       = ["Parameter '%s' must have a 'param_value' value." % l_p['param_name']]
                        return Response(m_return, status.HTTP_400_BAD_REQUEST)

                    l_plugin_results.append(l_p)

                # Add to plugin
                l_plugin['params'] = l_plugin_results

            # Add to plugins store
            m_plugins.append(l_plugin)

        # Add to global info
        m_info['enable_plugins'] = m_plugins


        #
        # Request for new audit
        #
        m_audit_id = None
        try:
            m_audit_id = GoLismeroFacadeAuditPolling.audit_import(m_info)
        except ValueError,e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotAllowedHostException,e:
            m_return['status']      = "error"
            m_return['error_code']  = 3
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotPluginsException,e:
            m_return['status']      = "error"
            m_return['error_code']  = 4
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditUnknownException,e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except Exception,e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = [str(e)]
            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        m_return['status']        = "ok"
        m_return['audit_id']      = m_audit_id

        return Response(m_return)




    #----------------------------------------------------------------------
    def delete(self, request, *args, **kwargs): # /api/audits/delete/ID
        """
        This method deletes an audit, using their ID

        :param pk: audit ID
        :type pk: str
        """

        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            GoLismeroFacadeAuditPolling.delete(m_audit_id)
            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditRunningException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 2
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def details(self, request, *args, **kwargs): # /api/audits/deatils/ID
        """
        Get Audit defails.
        """
        # Search
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            r                        = GoLismeroFacadeAuditPolling.get_audit(m_audit_id)
            m_return['status']       = "ok"
            m_return.update(r.to_json)

            return Response(m_return)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    #
    # Management
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    def start(self, request, *args, **kwargs): # /api/audits/start/ID
        """
        This method starts an audit, using their ID

        :param pk: audit ID
        :type pk: str
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            GoLismeroFacadeAuditPolling.start(m_audit_id)
            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def stop(self, request, *args, **kwargs): # /api/audits/stop/ID
        """
        This method stops an audit, using their ID

        :param pk: audit ID
        :type pk: str
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            GoLismeroFacadeAuditPolling.stop(m_audit_id)
            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def state(self, request, *args, **kwargs): # /api/audits/state/ID
        """
        Get audit state as format:

        {
           'state' : str
        }

        :returns: dict with state
        :rtype: dict(str)
        """
        # Info
        m_audit_id  = str(kwargs.get("pk", None))
        m_return    = {}

        m_info = None
        try:
            m_info = GoLismeroFacadeAuditPolling.get_state(m_audit_id)

            #
            # Returns info
            #
            m_return['status']      = "ok"
            m_return['state']       = m_info

            return Response(m_return)

        # Audit not exits
        except GoLismeroFacadeAuditNotFoundException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not found"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def progress(self, request, *args, **kwargs): # /api/audits/progress/ID
        """
        Get audit progress as format:

        :returns: return the progress in format:
        {
          'current_stage' : str,
          'steps'         : int,
          'tests_remain'  : int,
          'test_done'     : int
        }
        :rtype: dict(str)
        """
        # Info
        m_audit_id  = str(kwargs.get("pk", None))
        m_return    = {}

        m_info = None
        try:
            m_info = GoLismeroFacadeAuditPolling.get_progress(m_audit_id).to_json

            #
            # Returns info
            #
            m_return['status']      = "ok"
            m_return.update(m_info)

            return Response(m_return)

        # Audit not exits
        except GoLismeroFacadeAuditNotFoundException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not found"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Audit finished
        except GoLismeroFacadeAuditFinishedException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 2
            m_return['error']       = ["Provided audit is finished."]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def pause(self, request, *args, **kwargs): # /api/audits/pause/ID
        """
        This method pauses an audit, using their ID

        :param pk: audit ID
        :type pk: str
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            GoLismeroFacadeAuditPolling.pause(m_audit_id)
            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def resume(self, request, *args, **kwargs): # /api/audits/resume/ID
        """
        This method resumes an audit, using their ID

        :param pk: audit ID
        :type pk: str
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            GoLismeroFacadeAuditPolling.resume(m_audit_id)
            m_return['status']       = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def log(self, request, *args, **kwargs): # /api/audits/log/ID
        """
        This method pauses an audit, using their ID

        :param pk: audit ID
        :type pk: str

        :returns: a string with the log.
        :rtype: str
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_return       = {}

        try:
            m_return['log']       = GoLismeroFacadeAuditPolling.get_log(m_audit_id)
            m_return['status']    = "ok"

            return Response(m_return)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    #
    # Results
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    def results(self, request, *args, **kwargs): # /api/audits/results/ID/FORMAT
        """
        Get results as specified format, or in HTML by default.

        :param pk: audit ID
        :type pk: str

        :param text: text with format.
        :type text: str

        :returns: a format file depending of format requested.
        """
        m_audit_id     = str(kwargs.get("pk", ""))
        m_format       = str(kwargs.get("text", "text"))
        m_return       = {}

        try:
            f = GoLismeroFacadeAuditPolling.get_results(m_audit_id, m_format)

            return Response(f.read(), content_type=CONTENT_TYPES_BY_FORMAT[m_format])

        except GoLismeroFacadeReportNotAvailableException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 2
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeReportUnknownFormatException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditNotFoundException:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not exits"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


    #----------------------------------------------------------------------
    def results_summary(self, request, *args, **kwargs): # /api/audits/results/summary/ID
        """
        This method summary an audit, using their ID. :

        :param pk: audit ID
        :type pk: str

        :returns: return a dic as format:
        {
           'vulns_number'            = int
           'discovered_hosts'        = int # Host discovered into de scan process
           'total_hosts'             = int
           'vulns_by_level'          = {
              'info'     : int,
              'low'      : int,
              'medium'   : int,
              'high'     : int,
              'critical' : int,
        }
        :rtype: dic

        :raise:
        """

        # Info
        m_audit_id  = str(kwargs.get("pk", None))
        m_return    = {}

        m_info = None
        try:
            m_info = GoLismeroFacadeAuditPolling.get_results_summary(m_audit_id)

            #
            # Returns info
            #
            m_return['status']      = "ok"
            m_return.update(m_info)

            return Response(m_return)

        # Audit not exits
        except GoLismeroFacadeAuditNotFoundException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 0
            m_return['error']       = ["Provided audit ID not found"]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        except GoLismeroFacadeAuditStateException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 1
            m_return['error']       = [str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Audit finished
        except GoLismeroFacadeAuditFinishedException, e:
            m_return['status']      = "error"
            m_return['error_code']  = 2
            m_return['error']       = ["Provided audit is finished."]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)

        # Unknown exception
        except Exception, e:
            m_return['status']      = "error"
            m_return['error_code']  = -1
            m_return['error']       = ["Unknown error: %s" % str(e)]

            return Response(m_return, status.HTTP_400_BAD_REQUEST)


#------------------------------------------------------------------------------
#
# Users actions
#
#------------------------------------------------------------------------------
class UsersViewSet(ViewSet):
    """
    Actions with plugins
    """
    pass


#------------------------------------------------------------------------------
#
# Plugins actions
#
#------------------------------------------------------------------------------
class PluginsViewSet(ViewSet):
    """
    Actions with plugins
    """

    #authentication_classes = (BasicAuthentication, SessionAuthentication, TokenAuthentication)
    authentication_classes  = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    #----------------------------------------------------------------------
    def list(self, request, *args, **kwargs):
        """
        List all available plugins and their params in format:

        >>> return = [
           {
              'stage'       : 'recon',
              'plugin_name' : 'spider',
              'params'      : [
                 {
                    'name'    : 'param1',
                    'type'    : 'str',
                    'default' : ''
                 },
                 {
                    'name'    : 'param2',
                    'type'    : 'int',
                    'default' : '0'
                 }
              ]
            }
        ]
        """
        return Response({'as':'aaaa'})


    #----------------------------------------------------------------------
    def search(self, request, *args, **kwargs):
        s = kwargs['text']
        return Response({'search text' : s})


    #----------------------------------------------------------------------
    def detail(self, request, *args, **kwargs):
        """
        Get details from a concrete plugin
        """
        return Response({'details':kwargs['pk']})


#------------------------------------------------------------------------------
#
# Profiles actions
#
#------------------------------------------------------------------------------
class ProfilesViewSet(ViewSet):
    """
    Actions with plugins
    """
    pass


#------------------------------------------------------------------------------
#
# Nodes actions
#
#------------------------------------------------------------------------------
class NodesViewSet(ViewSet):
    """
    Actions with plugins
    """
    pass
